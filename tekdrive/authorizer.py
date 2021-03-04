"""Provides AccessKeyAuthorizer and other future authorizer classes."""


class BaseAuthorizer(object):
    def __init__(self):
        pass

    def _set_auth_header(self):
        raise NotImplementedError()


class AccessKeyAuthorizer(BaseAuthorizer):
    def __init__(self, access_key):
        """
        Represent a single, personal-use authorization via access key.

        Args:
            access_key: The previously generated access key.
        """
        self._access_key = access_key

    def _get_auth_header(self):
        return {"X-IS-AK": self._access_key}
