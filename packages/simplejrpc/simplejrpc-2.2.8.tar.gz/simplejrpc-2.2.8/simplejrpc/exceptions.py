# -*- encoding: utf-8 -*-
import http
import json
from typing import Optional

from simplejrpc._json import _jsonify  # type: ignore


class RPCException(Exception):
    """基础RPC异常"""

    def __init__(
        self,
        message=http.HTTPStatus.BAD_REQUEST.description,
        code=http.HTTPStatus.BAD_REQUEST.value,
        data: Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.message = message
        self.code = code
        self.data = data

    def __str__(self):
        """ """
        from simplejrpc._text import TextMessageDecoder  # type: ignore

        data = _jsonify(code=self.code, data=self.data, msg=self.message)
        return json.dumps(data, cls=TextMessageDecoder)


class UnauthorizedError(RPCException):
    """未授权异常"""


class ValidationError(RPCException):
    """验证异常"""


class RuntimeError(RPCException):
    """ """


class FileNotFoundError(RPCException):
    """ """


class ValueError(RPCException):
    """ """


class RuntimeError(RPCException):  # type: ignore
    """ """


class AttributeError(RPCException):
    """ """


class TypeError(RPCException):
    """ """
