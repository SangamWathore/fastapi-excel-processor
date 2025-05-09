import logging

logger = logging.getLogger("excel_processor")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():  # Prevent adding handlers multiple times
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
