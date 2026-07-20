from utils.logger import logger

class LoggingService:
    @staticmethod
    def log_action(action: str):
        logger.info(f"نشاط نظام: {action}")
      
