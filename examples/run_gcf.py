import functions_framework

import pydatafront

handler = pydatafront.gcf("examples")


@functions_framework.http
def main(request):
    handler(request)
