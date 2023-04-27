# Define the Annotations module
def skip(func):
    def wrapper(*args, **kwargs):
        print("Skipping function:", func.__name__)
    return wrapper