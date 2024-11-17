from fastapi import FastAPI, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
import asyncio
from typing import List
from pymongo import ASCENDING
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostCleaner:
    def __init__(self, mongodb_url: str, database_name: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client[database_name]
        self.posts_collection = self.db.posts

    async def setup_indexes(self):
        """Create an index on created_time field for better query performance"""
        await self.posts_collection.create_index([("created_time", ASCENDING)])

    async def delete_old_posts(self) -> List[str]:
        """Delete posts older than 10 days and return their IDs"""
        try:
            cutoff_date = datetime.now(timezone) - timedelta(days=10)

            # Find posts older than 10 days
            cursor = self.posts_collection.find({"created_time": {"$lt": cutoff_date}})
            old_posts = await cursor.to_list(length=None)

            if not old_posts:
                logger.info("No old posts found to delete")
                return []

            # Delete the old posts
            delete_result = await self.posts_collection.delete_many(
                {"created_time": {"$lt": cutoff_date}}
            )

            deleted_ids = [str(post["_id"]) for post in old_posts]
            logger.info(f"Deleted {delete_result.deleted_count} posts")

            return deleted_ids

        except Exception as e:
            logger.error(f"Error during post deletion: {str(e)}")
            raise

    async def cleanup_scheduler(self):
        """Run the cleanup task periodically"""
        while True:
            try:
                await self.delete_old_posts()
                # Wait for 24 hours before next cleanup
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"Error in cleanup scheduler: {str(e)}")
                # Wait for 1 hour before retry in case of error
                await asyncio.sleep(60 * 60)


# FastAPI application setup
app = FastAPI()
post_cleaner = None


@app.on_event("startup")
async def startup_event():
    global post_cleaner
    mongodb_url = "your_mongodb_url"  # Replace with your MongoDB URL
    database_name = "your_database"  # Replace with your database name

    post_cleaner = PostCleaner(mongodb_url, database_name)
    await post_cleaner.setup_indexes()

    # Start the cleanup scheduler in the background
    asyncio.create_task(post_cleaner.cleanup_scheduler())


# Optional: Endpoint to manually trigger cleanup
@app.post("/trigger-cleanup")
async def trigger_cleanup(background_tasks: BackgroundTasks):
    if post_cleaner:
        deleted_ids = await post_cleaner.delete_old_posts()
        return {
            "message": f"Cleanup completed. Deleted {len(deleted_ids)} posts",
            "deleted_ids": deleted_ids,
        }
    return {"message": "Post cleaner not initialized"}
