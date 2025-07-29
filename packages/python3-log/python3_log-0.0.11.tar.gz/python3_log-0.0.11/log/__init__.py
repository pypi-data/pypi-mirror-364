from log.log import get_logger
log=get_logger()

def enter_and_leave_log(func):
    def wrapper(*args, **kwargs):
        if args:
            if kwargs:
                log.info(f"Entering {func.__name__},args is {args},kwargs is {kwargs}")
            else:
                log.info(f"Entering {func.__name__},args is {args}")
        else:
            if kwargs:
                log.info(f"Entering {func.__name__},kwargs is {kwargs}")
            else:
                log.info(f"Entering {func.__name__}")
        result = func(*args, **kwargs)
        log_str=f"Leaving {func.__name__},result type is {type(result)}, and result is {result}"
        log.info(log_str[:100]+"...more to view log file")
        return result
    return wrapper