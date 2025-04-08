from rest_framework.exceptions import APIException as DrfAPIException


class APIException(DrfAPIException):
    """
    包装一下原 APIException
    在 init 中加入 status_code
    不加的话只能 500
    """

    def __init__(self, detail: str | None = None, status_code: int = 500, code: str | None = None):
        super().__init__(detail, code)
        self.status_code = status_code
