from functools import wraps
import logging

from storage.storage import StorageError
from utils.constants import SERVER_500_ERROR_MSG

SERVER_500_ERROR_MSG = (
    "Something went wrong while processing your request. Please try again later."
)


def handle_server_errors(storage_error_msg=None, os_error_msg=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except StorageError:
                logging.exception("StorageError in %s", func.__name__)
                self.send_rendered_error_page(
                    error_message=storage_error_msg or SERVER_500_ERROR_MSG,
                    error_code=500,
                )
            except OSError:
                logging.exception("OSError in %s", func.__name__)
                self.send_rendered_error_page(
                    error_message=os_error_msg or SERVER_500_ERROR_MSG,
                    error_code=500,
                )

        return wrapper

    return decorator
