# -*- coding: utf-8 -*-
class SigfoxBaseException(BaseException):
    pass


class SigfoxConnectionError(SigfoxBaseException):
    pass


class SigfoxBadStatusError(SigfoxBaseException):
    pass


class SigfoxResponseError(SigfoxBaseException):
    pass


class SigfoxTooManyRequestsError(SigfoxBaseException):
    pass
