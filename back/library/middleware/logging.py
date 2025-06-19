import logging
import time

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s; %(message)s', )
handler.formatter = formatter
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LoggingProductsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = time.time()
        request_data = {
            'request': request.method,
            'ip_adress': request.META.get('REMOTE_ADDR'),
            'path': request.path,
            'user': request.user if request.user.is_authenticated else 'Anonymous',

        }
        logger.info(request_data)
        method = request.method
        ip_address = request.META.get('REMOTE_ADDR')
        path = request.path

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        duration = time.time() - start_time
        user = request.user if request.user.is_authenticated else 'Anonymous'


        request_data = {
            'request': method,
            'ip_adress': ip_address,
            'path': path,
            'user': user,
        }

        response_dict = {
            'status_code': response.status_code,
            'duration': duration,
        }
        logger.info(request_data)
        logger.info(response_dict)

        return response
