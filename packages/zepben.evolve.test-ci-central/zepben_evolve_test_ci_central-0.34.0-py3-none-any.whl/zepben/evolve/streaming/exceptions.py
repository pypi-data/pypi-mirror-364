# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

__all__ = ["AuthException", "StreamingException", "UnsupportedOperationException"]


class AuthException(Exception):
    pass


class StreamingException(Exception):
    pass


class UnsupportedOperationException(Exception):
    pass
