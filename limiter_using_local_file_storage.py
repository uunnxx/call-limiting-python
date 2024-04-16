import os
import time
from functools import wraps


class CallLimitExceededException(Exception):
    '''Exception raised when the allowed number of function calls is exceeded.'''
    pass


def call_limit(max_calls, period=86400):
    def decorator(func):
        filepath = f"{func.__name__}_call_limit.txt"

        def read_data():
            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    data = file.read().split()
                    if len(data) == 2:
                        return int(data[0]), float(data[1])
            return 0, time.time()

        def write_data(count, timestamp):
            with open(filepath, 'w') as file:
                file.write(f"{count} {timestamp}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            count, start_time = read_data()
            if time.time() - start_time > period:
                # Reset the count after the period expires
                count = 0
                start_time = time.time()
            if count < max_calls:
                count += 1
                write_data(count, start_time)
                return func(*args, **kwargs)
            else:
                raise CallLimitExceededException(
                    f"Exceeded {max_calls} calls in {period} seconds.")

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
