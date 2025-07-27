from collect import collect_data
from clean import load_and_clean
from features import process_features
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='data_pipeline.log'
)

logger = logging.getLogger(__name__)

def run_pipeline():
    try:
        logger.info("Starting data pipeline...")
        
        # Step 1: Data collection
        logger.info("Data collection started")
        collect_data()
        logger.info("Data collection completed")
        
        # Step 2: Data cleaning
        logger.info("Data cleaning started")
        load_and_clean()
        logger.info("Data cleaning completed")
        
        # Step 3: Feature engineering
        logger.info("Feature engineering started")
        process_features()
        logger.info("Feature engineering completed")
        
        logger.info("Data pipeline completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_pipeline()
    