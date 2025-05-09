
import pandas as pd
import os
from app.logger import logger
import boto3

def process_excel(file_path, processed_folder):
    logger.info(f"Starting processing of file: {file_path}")
    try:
        df = pd.read_excel(file_path)
        logger.info(f"File {file_path} read into DataFrame successfully")

        df['Date of Capitalization'] = df['Date of Purchase']
        df['95%'] = df['Total Cost'] * 0.95
        df['Life used upto 31st March, 2024'] = ((df['As at Year end'] - df['Date of Capitalization']) / pd.Timedelta(days=30)).round().astype(int)
        df['Remaining useful life'] = ((df['As at Year end'] - df['Date of Purchase']) / pd.Timedelta(days=30)).round().astype(int)
        df["Monthly Depreciation"] = df['95%'] / df['Useful Life (months)']
        df['Dep for the year 2024-25'] = df["Monthly Depreciation"] * 12
        df['Closing Depreciation'] = df['opening Depreciation'] + df['Dep for the year 2024-25']

        processed_filename = f"updated_{os.path.splitext(os.path.basename(file_path))[0]}.xlsx"
        processed_path = os.path.join(processed_folder, processed_filename)
        df.to_excel(processed_path, index=False)

        logger.info(f"File processed and saved to: {processed_path}")
        return processed_path

    except Exception as e:
        logger.error(f"Error while processing Excel file: {e}", exc_info=True)
        raise

def upload_to_s3(file_path, s3_key, request):
    logger.info(f"Uploading file to S3: {file_path} -> {s3_key}")
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=request.app.state.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=request.app.state.AWS_SECRET_ACCESS_KEY,
            region_name=request.app.state.AWS_REGION,
        )
        bucket = request.app.state.AWS_S3_BUCKET_NAME
        s3.upload_file(file_path, bucket, s3_key)
        logger.info(f"Uploaded {file_path} to s3://{bucket}/{s3_key}")

    except Exception as e:
        logger.error(f"Failed to upload {file_path} to S3: {e}", exc_info=True)
        raise
