import logging
from logging.handlers import TimedRotatingFileHandler
import os

def methodInitLogging():
    # .env 파일에 설정값 로딩
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "console").upper()
    log_file_path = os.getenv("LOG_FILE_PATH", "logs/oasis.log")
    log_rotate = os.getenv("LOG_ROTATE", "0").upper() == "1"
    log_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s, %(name)s]-%(message)s",
        datefmt="%Y.%m.%d %H:%M:%S"
    )
    
    handlers = []
    
    if log_format == "CONSOLE" or log_format == "BOTH":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        handlers.append(console_handler)
        
    if log_format == "FILE" or log_format == "BOTH":
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        if log_rotate:
            file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", backupCount=7, encoding="utf-8")
        else:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")

        file_handler.setFormatter(log_formatter)
        handlers.append(file_handler)
        
    
    # logging.basicConfig(
    #     level=log_level,
    #     format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    #     datefmt="%Y.%m.%d %H:%M:%S"
    # )
    logging.basicConfig(level=log_level, handlers=handlers)
    logging.getLogger().setLevel(log_level)
    print(f"✅ LOG_LEVEL: {log_level}")

def methodGetLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)
    
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.debug("DEBUG 테스트 로그")
    logger.info("INFO 테스트 로그")
    logger.warning("WARNING 테스트 로그")
    logger.error("ERROR 테스트 로그")
    logger.critical("CRITICAL 테스트 로그")
