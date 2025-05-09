from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.routes import router as main_router
from app.logger import logger  # <-- Import your logger

load_dotenv()
logger.info("Environment variables loaded successfully")

app = FastAPI()
logger.info("FastAPI app instance created")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
logger.info("CORS middleware added")

# Set up folder paths
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "incoming_files")
PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", "output_files")

try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    logger.info(f"Upload and processed directories ensured: {UPLOAD_FOLDER}, {PROCESSED_FOLDER}")
except Exception as e:
    logger.error(f"Failed to create directories: {e}", exc_info=True)
    raise

# Store folder paths and AWS config in application state
app.state.UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)
app.state.PROCESSED_FOLDER = os.path.abspath(PROCESSED_FOLDER)
app.state.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
app.state.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
app.state.AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
app.state.AWS_REGION = os.getenv("AWS_REGION")

logger.info("Application state variables set for upload path, processed path, and AWS credentials")

# Setup Jinja templates (optional if not used directly)
templates = Jinja2Templates(directory="app/templates")
logger.info("Jinja2 templates directory configured")

# Register your routes
app.include_router(main_router)
logger.info("API routes registered with application")
