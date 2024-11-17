# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi.responses import JSONResponse
# from datetime import timedelta
# from pydantic import BaseModel, EmailStr
# from app.db.mongo import get_database
# from motor.motor_asyncio import AsyncIOMotorDatabase
# from jose import JWTError
# import google.generativeai as genai
# import io
# import uvicorn


# API_KEY = "AIzaSyCstK_9OTIeaaEcBRLCCY2LBFEjNDYXrpw"  # Placing it here js for now.. Dont send too many requests in testing..
# genai.configure(api_key=API_KEY)

# # Router Configuration
# p_router = APIRouter(prefix="/posts", tags=["Posts"])


# # Response Models
# class PostResponse(BaseModel):
#     result: bool


# @p_router.post("/verify_image", response_model=PostResponse)
# async def verify_image(file: UploadFile, tag: str) -> PostResponse:
#     try:
#         file_content = await file.read()
#         file_stream = io.BytesIO(file_content)
#         myfile = genai.upload_file(file_stream, mime_type=file.content_type)

#         model = genai.GenerativeModel("gemini-1.5-pro")

#         question = f"Does this picture contain {tag}? Return 1 if it does and 0 if it does not. Dont write anything else."

#         result = model.generate_content([myfile, "\n\n", question])

#         return {"result": False if result.text == "0" else True}
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return {"error": str(e)}
