import importlib
import typing

import pydatafront.decorator as decorator
from pydatafront.app import app


def __prep(main_class: typing.Optional[str] = "functions"):
    decorator.enable_wrapper()
    importlib.import_module(main_class)


def run(host: typing.Optional[str] = "localhost", port: typing.Optional[int] = 4010,
        main_class: typing.Optional[str] = "functions"):
    __prep(main_class=main_class)
    app.run(host, port)


def gcf(main_class: typing.Optional[str] = "functions"):
    __prep(main_class=main_class)

    # Ref: https://medium.com/google-cloud/use-multiple-paths-in-cloud-functions-python-and-flask-fc6780e560d3
    # Ref: https://stackoverflow.com/questions/53488766/using-flask-routing-in-gcp-function
    def handler(request):
        internal_ctx = app.test_request_context(path=request.full_path,
                                                method=request.method)
        internal_ctx.request.data = request.data
        internal_ctx.request.headers = request.headers
        internal_ctx.push()
        return_value = app.full_dispatch_request()
        internal_ctx.pop()
        return return_value

    return handler
