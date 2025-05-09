
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from app.services import process_excel, upload_to_s3
from app.logger import logger
import shutil


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")

    if not file.filename.endswith(".xlsx"):
        logger.warning("Invalid file type uploaded")
        return JSONResponse(status_code=400, content={"message": "Invalid file type"})

    upload_path = os.path.join(request.app.state.UPLOAD_FOLDER, file.filename)

    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved locally at {upload_path}")

        processed_path = process_excel(upload_path, request.app.state.PROCESSED_FOLDER)
        logger.info(f"File processed and saved at {processed_path}")

        original_s3_key = f"uploads/{file.filename}"
        processed_s3_key = f"processed/{os.path.basename(processed_path)}"

        upload_to_s3(upload_path, original_s3_key, request)
        logger.info(f"Original file uploaded to S3: {original_s3_key}")

        upload_to_s3(processed_path, processed_s3_key, request)
        logger.info(f"Processed file uploaded to S3: {processed_s3_key}")

        original_file_url = f"https://{request.app.state.AWS_S3_BUCKET_NAME}.s3.{request.app.state.AWS_REGION}.amazonaws.com/{original_s3_key}"
        processed_file_url = f"https://{request.app.state.AWS_S3_BUCKET_NAME}.s3.{request.app.state.AWS_REGION}.amazonaws.com/{processed_s3_key}"

        return JSONResponse(status_code=200, content={
            "message": "File processed and saved to S3 bucket successfully",
            "original_file_url": original_file_url,
            "processed_file_url": processed_file_url
        })

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"message": str(e)})
