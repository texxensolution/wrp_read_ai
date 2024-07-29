import os 
import logging

logger = logging.getLogger()
def initialize_dependencies():
    # create storage for supported assessments.
    assessments = ['script_reading', 'quote_translation', 'photo_interpretation']
    for assessment in assessments:
        storage_dir = os.path.join('storage', assessment)
        if not os.path.exists(storage_dir):
            logger.info(f'creating storage directory for {assessment}...')
            os.makedirs(storage_dir)
    
    


