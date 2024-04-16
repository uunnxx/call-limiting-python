import redis

from functools import wraps


class CallLimitExceededException(Exception):
    pass



def call_limit(max_calls, period=86400):  # 60*60*24
    '''
    Decorator to limit the number of calls to a function within a specified time period.
    Args:
        max_calls (int): Maximum number of function calls allowed within the period.
        period (int): Time period in seconds during which calls are counted (default is 86400 seconds, or 24 hours).
    
    Returns:
        Function: A wrapper that counts calls made to the decorated function.
    '''
    def decorator(func):
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"call_limit:{func.__name__}"
            count = r.get(key)

            if count is None:
                r.set(key, 1, ex=period)
            elif int(count) >= max_calls:
                raise CallLimitExceededException(
                    f"Call limit exceeded for {func.__name__}."
                    f"Max {max_calls} calls in {period} seconds."
                )
            else:
                r.incr(key)

            return func(*args, **kwargs)
        
        return wrapper
    return decorator


@call_limit(10)
def process_data():
    '''Simulate a data processing function that can be called up to 10 times per 24 hours.'''
    return "Data processed successfully."


def example_usage():
    '''
    Example usage of the `process_data` function, demonstrating handling of the call limit.
    '''
    for _ in range(12):
        try:
            print(process_data())
        except CallLimitExceededException as e:
            print(e)


if __name__ == "__main__":
    example_usage()
