import functools
import logging
import inspect

def methodAutoLogging(logger_name: str=None):
    def methodDecorator(func):
        
        @functools.wraps(func)
        def methodWrapper(*args, **kwargs):
            mod_name = logger_name or inspect.getmodule(func).__name__
            logger = logging.getLogger(mod_name)

            logger.debug(f"→ {func.__qualname__}() CALLED | args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"← {func.__qualname__}() RETURNED | result={result}")
            return result
        return methodWrapper
    
    return methodDecorator
