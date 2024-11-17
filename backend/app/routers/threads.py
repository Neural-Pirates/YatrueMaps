from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from jose import JWTError
import io
import uvicorn
from app.schemas.thread import CreateThread, CreateComment
from app.utils.image_verfier import verify_image
from app.utils.distance import (
    haversine_distance,
    calculate_distance,
    calculate_all_midpoints,
    fetch_nearby_comments_,
)
from bson import ObjectId
from app.models.user import User
from datetime import datetime
from gridfs import GridFS
import base64


threads = APIRouter(prefix="/threads", tags=["Threads"])

oauth_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# Response Models
class AddThreadResponse(BaseModel):
    id: str
    status_code: int


class AddCommentResponse(BaseModel):
    id: str
    parent_id: str
    status_code: int


class SingleThreadResponse(BaseModel):
    id: str
    comment: str
    user: str
    parent_id: str
    lat: float
    long: float
    created_at: datetime


class VoteRequest(BaseModel):
    user_id: str
    comment_id: str
    vote_type: bool


def validate_token(token: str = Depends(oauth_scheme)) -> dict:
    """
    Validate JWT token and return token data.
    Raises 401 for invalid token.
    """
    try:
        payload = User.validate_jwt_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# @threads.post("/thread", response_model=AddThreadResponse)
# async def createThread(
#     data: CreateThread,
#     # file: UploadFile | None = None,
#     valid: dict = Depends(validate_token),
#     db: AsyncIOMotorDatabase = Depends(get_database),
# ):

#     try:
#         thread_data = data.model_dump()
#         print(thread_data)
#         # if thread_data["parent_id"] is not None:
#         #     raise HTTPException(
#         #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         #         detail="Parent id should not exist",
#         #     )
#         thread_data["parent_id"] = None
#         thread = await db["threads"].insert_one(thread_data)
#         created_thread = await db["threads"].find_one({"_id": thread.inserted_id})

#         if not created_thread:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to create thread",
#             )

#         return AddThreadResponse(
#             id=str(created_thread["_id"]),
#             status_code=status.HTTP_201_CREATED,
#         )

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Error creating user: {str(e)}",
#         )


# @threads.post("/comment", response_model=AddCommentResponse)
# async def createComment(
#     comment: str = Form(...),
#     user: str = Form(...),
#     parent_id: str = Form(...),
#     lat: float = Form(...),
#     long: float = Form(...),
#     created_at: datetime = Form(...),
#     file: UploadFile | None = None,
#     db: AsyncIOMotorDatabase = Depends(get_database),
#     # valid: dict = Depends(validate_token),
# ):
#     try:
#         file_id = None
#         if file:
#             try:
#                 file_content = await file.read()
#                 fs = AsyncIOMotorGridFSBucket(
#                     db, collection="fs"
#                 )  # Specify the GridFS collection

#                 tag = verify_image(
#                     file_content=file_content, content_type=file.content_type
#                 )
#                 verifier_status = bool(tag)

#                 # Upload the file to GridFS with metadata
#                 metadata = {
#                     "content_type": file.content_type,
#                     "tag": tag,
#                     "verifier_status": verifier_status,
#                 }

#                 file_id = await fs.upload_from_stream(
#                     file.filename,  # Store the file with its original name
#                     file_content,  # File content
#                     metadata=metadata,  # Attach metadata
#                 )
#             except Exception as e:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Failed to upload image: {str(e)}",
#                 )

#         thread_data = {
#             "comment": comment,
#             "user": user,
#             "parent_id": ObjectId(parent_id),
#             "lat": lat,
#             "long": long,
#             "created_at": created_at,
#             "vote": 0,
#         }

#         if file_id:
#             thread_data["image_id"] = ObjectId(file_id)

#         thread = await db["threads"].insert_one(thread_data)
#         created_thread = await db["threads"].find_one({"_id": thread.inserted_id})

#         if not created_thread:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to create thread",
#             )

#         return AddCommentResponse(
#             id=str(created_thread["_id"]),
#             parent_id=str(created_thread["parent_id"]),
#             status_code=status.HTTP_201_CREATED,
#         )

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Error creating comment: {str(e)}",
#         )


# @threads.get("/show_image/{file_id}")
async def show_image(file_id, db):
    try:
        fs = AsyncIOMotorGridFSBucket(
            db
        )  # Use the same collection name as used for uploads
        print("fkdsajfls", file_id)
        # Retrieve the file from GridFS
        stream = await fs.open_download_stream(ObjectId(file_id))

        # Read and encode the image as a base64 string
        file_content = await stream.read()
        image_data = base64.b64encode(file_content).decode("utf-8")

        # Retrieve metadata from the file document
        file_doc = await db["fs.files"].find_one({"_id": ObjectId(file_id)})
        metadata = file_doc.get("metadata", {})

        return {
            # "file_id": file_id,
            # "filename": stream.filename,
            "verifier_status": metadata.get("verifier_status"),
            "tag": metadata.get("tag"),
            "image_base64": image_data,
        }

    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found") from e


@threads.post("/thread", response_model=AddCommentResponse)
async def createThread(
    comment: str = Form(...),
    user: str = Form(...),
    parent_id: str | None = Form(None),
    lat: float = Form(...),
    long: float = Form(...),
    created_at: datetime = Form(...),
    file: UploadFile | None = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    valid: dict = Depends(validate_token),
):
    try:
        file_id = None
        if file:
            try:
                file_content = await file.read()
                fs = AsyncIOMotorGridFSBucket(db, collection="fs")

                tag = verify_image(
                    file_content=file_content, content_type=file.content_type
                )
                verifier_status = bool(tag)

                metadata = {
                    "content_type": file.content_type,
                    "tag": tag,
                    "verifier_status": verifier_status,
                }

                file_id = await fs.upload_from_stream(
                    file.filename,  # Store the file with its original name
                    file_content,  # File content
                    metadata=metadata,  # Attach metadata
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {str(e)}",
                )

        if not (-90 <= lat <= 90 and -180 <= long <= 180):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid latitude ({lat}) or longitude ({long}) values.",
            )

        thread_data = {
            "comment": comment,
            "user": user,
            "parent_id": ObjectId(parent_id) if parent_id else None,
            # "lat": lat,
            # "long": long,
            "location": {
                "type": "Point",
                "coordinates": [long, lat],
            },  # long and then lat
            "vote": 0,
            "children": 0,
            "upvoted_by": [],
            "downvoted_by": [],
            "created_at": created_at,
        }

        thread_data["image_id"] = ObjectId(file_id) if file_id else None

        thread = await db["threads"].insert_one(thread_data)
        created_thread = await db["threads"].find_one({"_id": thread.inserted_id})

        if not created_thread:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create thread",
            )

        if ObjectId(parent_id):
            # parent = db["threads"].find_one{"parent_id": ObjectId(parent_id)}
            # parent_id = parent["_id"]
            updateChildrenCount = db["threads"].update_one(
                {"_id": ObjectId(parent_id)}, {"$inc": {"children": 1}}
            )

        return AddCommentResponse(
            id=str(created_thread["_id"]),
            parent_id=str(created_thread["parent_id"]),
            status_code=status.HTTP_201_CREATED,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Error creating comment: {str(e)}",
        )


@threads.get("/fetchChild/{parent_id}")
async def fetchChild(
    parent_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    valid: dict = Depends(validate_token),
):
    try:
        all_docs = (
            await db["threads"]
            .find({"parent_id": ObjectId(parent_id)})
            .sort("vote", -1)
            .to_list(length=None)
        )

        nearby_docs = []
        for doc in all_docs:
            doc["_id"] = str(doc["_id"])
            doc["parent_id"] = str(doc["parent_id"])
            if doc["image_id"]:
                doc["image_id"] = str(doc["image_id"])
                image_dict = await show_image(file_id=doc["image_id"], db=db)
                doc["image_data"] = image_dict
            else:
                doc["image_data"] = None
            nearby_docs.append(doc)

        return {"threads": nearby_docs}
    except:
        pass


# @threads.post("/comment", response_model=AddCommentResponse)
# async def createComment(
#     data: CreateComment,
#     # file: UploadFile | None = None,
#     db: AsyncIOMotorDatabase = Depends(get_database),
#     # valid: dict = Depends(validate_token),
# ):
#     try:
#         #     file_id = None
#         #     if file:
#         #         try:
#         #             file_content = await file.read()
#         #             fs = GridFS(db, collection="fs")  # Ensure correct collection is used
#         #             tag = verify_image(
#         #                 file_content=file_content, content_type=file.content_type
#         #             )
#         #             verifier_status = bool(tag)

#         #             # Store file content in GridFS with metadata
#         #             file_id = await fs.put(
#         #                 file_content,
#         #                 content_type=file.content_type,
#         #                 tag=tag,
#         #                 verifier_status=verifier_status,
#         #             )
#         #         except Exception as e:
#         #             raise HTTPException(
#         #                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         #                 detail=f"Failed to upload image: {str(e)}",
#         #             )

#         thread_data = data.model_dump()

#         # Validate parent_id
#         if not thread_data.get("parent_id"):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Parent ID is required to create a thread",
#             )

#         thread_data["parent_id"] = ObjectId(thread_data["parent_id"])

#         # Add image_id only if a file was uploaded
#         # if file_id:
#         #     thread_data["image_id"] = ObjectId(file_id)

#         # Insert thread data into the database
#         thread = await db["threads"].insert_one(thread_data)
#         created_thread = await db["threads"].find_one({"_id": thread.inserted_id})

#         if not created_thread:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to create thread",
#             )

#         return AddCommentResponse(
#             id=str(created_thread["_id"]),
#             parent_id=str(created_thread["parent_id"]),
#             status_code=status.HTTP_201_CREATED,
#         )

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Error creating comment: {str(e)}",
#         )

# yesko kaam aaile chaina pachi modify garda huncha hernu
# @threads.get("thread/{comment_id}", response_model=SingleThreadResponse)
# async def getThread(
#     comment_id: str,
#     db: AsyncIOMotorDatabase = Depends(get_database),
#     valid: dict = Depends(validate_token),
# ) -> SingleThreadResponse:
#     try:
#         if comment_id is None:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Teri ma comment_id patha",
#             )

#         thread = await db["threads"].find_one({"_id": ObjectId(comment_id)})
#         return SingleThreadResponse(
#             id=str(thread["_id"]),
#             comment=thread["comment"],
#             user=thread["user"],
#             parent_id=str(thread["parent_id"]),
#             lat=thread["lat"],
#             long=thread["long"],
#             created_at=thread["created_at"],
#         )

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Error creating user: {str(e)}",
#         )


@threads.get(
    "thread/childs/{comment_id}",
    response_model=List[SingleThreadResponse],
)
async def getThreadChildren(
    comment_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    valid: dict = Depends(validate_token),
):
    try:
        if not comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment ID is required.",
            )

        # Ensure ObjectId is valid
        try:
            parent_id = ObjectId(comment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Comment ID format.",
            )

        # Retrieve child threads
        cursor = db["threads"].find({"parent_id": parent_id})
        threads = await cursor.to_list(length=None)

        # Return an empty list if no child threads are found
        return [
            SingleThreadResponse(
                id=str(thread["_id"]),
                comment=thread["comment"],
                user=thread["user"],
                parent_id=str(thread["parent_id"]),
                lat=thread["lat"],
                long=thread["long"],
                created_at=thread["created_at"],
            )
            for thread in threads
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving child threads: {str(e)}",
        )


@threads.post("/threads/vote/{comment_id}")
async def voteThread(
    data: VoteRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    valid: dict = Depends(validate_token),
):
    try:
        try:
            comment_obj_id = ObjectId(data.comment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Comment ID format.",
            )
        thread = await db["threads"].find_one({"_id": ObjectId(data.comment_id)})
        upvoted_user_list = thread["upvoted_by"]
        downvoted_user_list = thread["downvoted_by"]
        if data.vote_type:

            if data.user_id in upvoted_user_list:
                result = await db["threads"].update_one(
                    {"_id": ObjectId(data.comment_id)},
                    {"$inc": {"vote": -1}, "$pull": {"upvoted_by": data.user_id}},
                )

            elif data.user_id in downvoted_user_list:

                result = await db["threads"].update_one(
                    {"_id": ObjectId(data.comment_id)},
                    {
                        "$inc": {"vote": +2},
                        "$push": {"upvoted_by": data.user_id},
                        "$pull": {"downvoted_by": data.user_id},
                    },
                )
            else:

                result = await db["threads"].update_one(
                    {"_id": ObjectId(data.comment_id)},
                    {"$inc": {"vote": 1}, "$push": {"upvoted_by": data.user_id}},
                )

        else:
            if data.user_id in upvoted_user_list:
                result = await db["threads"].update_one(
                    {"_id": ObjectId(data.comment_id)},
                    {
                        "$inc": {"vote": -2},
                        "$pull": {"upvoted_by": data.user_id},
                        "$push": {"downvoted_by": data.user_id},
                    },
                )

            elif data.user_id in downvoted_user_list:

                result = await db["threads"].update_one(
                    {"_id": ObjectId(data.comment_id)},
                    {"$inc": {"vote": +1}, "$pull": {"downvoted_by": data.user_id}},
                )
            else:

                result = await db["threads"].update_one(
                    {"_id": ObjectId(data.comment_id)},
                    {"$inc": {"vote": -1}, "$push": {"downvoted_by": data.user_id}},
                )

            # result = await db["threads"].update_one(
            #     {"_id": ObjectId(data.comment_id)}, {"$inc": {"vote": -1}, "$push": {"downvoted_by": data.user_id}}
            # )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found.",
            )

        comment = await db["threads"].find_one({"_id": ObjectId(data.comment_id)})
        vote_count = comment["vote"]

        return {
            "message": "Vote count updated successfully",
            "comment_id": data.comment_id,
            "updated_vote_count": vote_count,
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating vote count: {str(e)}",
        )
    
@threads.get("/hasVoted/{comment_id}/{user_id}")
async def hasVoted(
    comment_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    valid: dict = Depends(validate_token),
):
    try:
        try:
            comment_obj_id = ObjectId(comment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Comment ID format.",
            )
        thread = await db["threads"].find_one({"_id": ObjectId(comment_id)})
        upvoted_user_list = thread["upvoted_by"]
        downvoted_user_list = thread["downvoted_by"]
        if user_id in upvoted_user_list:
            return {"hasVoted": "upvoted"}
        elif user_id in downvoted_user_list:
            return {"hasVoted": "downvoted"}
        else:
            return {"hasVoted": "noVote"}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking vote status: {str(e)}",
        )


# @threads.get("/threadsFeed/{page}/{limit}/{lat}/{long}/{radius}")
# async def threadsFeed(
#     page: int,
#     limit: int,
#     lat: float,
#     long: float,
#     radius: int,
#     db: AsyncIOMotorDatabase = Depends(get_database),
#     valid: dict = Depends(validate_token),
# ):
#     try:
#         if page < 1 or limit < 1:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Page and limit must be positive integers.",
#             )

#         skip = (page - 1) * limit

#         # Radius of Earth in kilometers
#         EARTH_RADIUS_KM = 6371
#         # Convert radius in km to radians
#         radius_in_radians = 5 / EARTH_RADIUS_KM

#         pipeline = [
#             {
#                 "$match": {
#                     "location": {
#                         "$geoWithin": {
#                             "$centerSphere": [[long, lat], radius_in_radians]
#                         }
#                     }
#                 }
#             },
#             {"$sort": {"vote": -1}},
#             {"$skip": skip},
#             {"$limit": limit},
#             {
#                 "$project": {
#                     "_id": {"$toString": "$_id"},
#                     "comment": 1,
#                     "user": 1,
#                     "vote_count": 1,
#                     "parent_id": {"$toString": "$parent_id"},
#                     "lat": {"$arrayElemAt": ["$location.coordinates", 1]},
#                     "long": {"$arrayElemAt": ["$location.coordinates", 0]},
#                     "created_at": 1,
#                 }
#             },
#         ]

#         threads = await db["threads"].aggregate(pipeline).to_list(length=None)

#         return {
#             "page": page,
#             "limit": limit,
#             "total_threads": len(threads),
#             "threads": threads,
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching threads feed: {str(e)}",
#         )


# code to recover
# @threads.get("/threadsFeed/{lat}/{long}/{radius}")
# async def fetch_nearby_comments(
#     long: str,
#     lat: str,
#     radius: str,
#     db: AsyncIOMotorDatabase = Depends(get_database),
# ):

#     all_docs = (
#         await db["threads"]
#         .find({"parent_id": None})
#         .sort("vote", -1)
#         .to_list(length=None)
#     )

#     nearby_docs = []
#     for doc in all_docs:
#         if "coordinates" in doc["location"]:
#             doc_longitude = doc["location"]["coordinates"][0]
#             doc_latitude = doc["location"]["coordinates"][1]
#             distance = calculate_distance(
#                 float(long), float(lat), float(doc_longitude), float(doc_latitude)
#             )
#             print("Debugging")
#             print(doc_longitude, doc_latitude, distance)
#             if distance <= float(radius):
#                 doc["_id"] = str(doc["_id"])
#                 doc["parent_id"] = str(doc["parent_id"])
#                 if doc["image_id"]:
#                     doc["image_id"] = str(doc["image_id"])
#                     image_dict = await show_image(file_id=doc["image_id"], db=db)
#                     doc["image_data"] = image_dict
#                 else:
#                     doc["image_data"] = None
#                 nearby_docs.append(doc)

#     return {"threads": nearby_docs}


# @threads.get("/threadsFeed/{lat}/{long}/{radius}")
# async def fetch_nearby_comments(
#     long: str,
#     lat: str,
#     radius: str,
#     db: AsyncIOMotorDatabase = Depends(get_database),
# ) -> Dict[str, List[Dict]]:
#     pipeline = [
#         {
#             "$geoNear": {
#                 "near": {"type": "Point", "coordinates": [float(long), float(lat)]},
#                 "distanceField": "distance",
#                 "maxDistance": float(radius),
#                 "spherical": True,
#             }
#         },
#         {
#             "$project": {
#                 "_id": {"$toString": "$_id"},
#                 "parent_id": {"$toString": "$parent_id"},
#                 "image_id": {"$toString": "$image_id"},
#                 "location": 1,
#                 "distance": 1,
#             }
#         },
#     ]

#     nearby_docs = await db["threads"].aggregate(pipeline).to_list(length=None)
#     return {"threads": nearby_docs}


# @threads.post("/createIndex")
# async def createIndex(db: AsyncIOMotorDatabase = Depends(get_database)):
#     await db["threads"].create_index([("location", "2dsphere")])
#     return {"message": "vayo muji"}


# @threads.get("/testindex")
# async def testIndex(db: AsyncIOMotorDatabase = Depends(get_database)):
#     indexes = await db["threads"].index_information()
#     print(indexes)


@threads.get("/threadsFeed/{long1}/{lat1}/{long2}/{lat2}")
async def fetch_nearby_comments(
    long1: float,
    lat1: float,
    long2: float,
    lat2: float,
    # radius: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    valid: dict = Depends(validate_token),
):

    radius = calculate_distance(float(long1), float(lat1), float(long2), float(lat2))
    print(radius)

    all_docs = (
        await db["threads"]
        .find({"parent_id": None})
        .sort("vote", -1)
        .to_list(length=None)
    )

    nearby_docs = []
    for doc in all_docs:
        if "coordinates" in doc["location"]:
            doc_longitude = doc["location"]["coordinates"][0]
            doc_latitude = doc["location"]["coordinates"][1]
            distance = calculate_distance(
                float(long1), float(lat1), float(doc_longitude), float(doc_latitude)
            )
            print("Debugging")
            print(doc_longitude, doc_latitude, distance)
            if distance <= float(radius):
                doc["_id"] = str(doc["_id"])
                doc["parent_id"] = str(doc["parent_id"])
                if doc["image_id"]:
                    doc["image_id"] = str(doc["image_id"])
                    image_dict = await show_image(file_id=doc["image_id"], db=db)
                    doc["image_data"] = image_dict
                else:
                    doc["image_data"] = None
                nearby_docs.append(doc)

    return {"threads": nearby_docs}


@threads.get("/who_is_your_daddy")
def daddy():
    return {"message": "Kasmik Daddy oh ywahhhhh"}


@threads.get("/routeThreads/{long1}/{lat1}/{long2}/{lat2}")
async def routeThreads(
    long1: float,
    lat1: float,
    long2: float,
    lat2: float,
    # radius: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    midpoints = calculate_all_midpoints(lat1, long1, lat2, long2)
    first_data = await fetch_nearby_comments_(
        midpoints[1][1], midpoints[1][0], midpoints[0][1], midpoints[0][0], db=db
    )
    second_data = await fetch_nearby_comments_(
        midpoints[2][1], midpoints[2][0], midpoints[0][1], midpoints[0][0], db=db
    )

    merged_data = {"threads": first_data["threads"] + second_data["threads"]}

    return merged_data
