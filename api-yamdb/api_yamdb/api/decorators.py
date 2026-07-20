def doc(docstring):
    """Декоратор для задания docstring динамически."""
    def decorator(func):
        func.__doc__ = docstring
        return func
    return decorator
