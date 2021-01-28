from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from ..exceptions import TekDriveAPIException
from ..utils.casing import to_snake_case

if TYPE_CHECKING:  # pragma: no cover
    from .. import Client


class Parser:
    @classmethod
    def parse_error(
        cls, data: Union[List[Any], Dict[str, Dict[str, str]]]
    ) -> Optional[TekDriveAPIException]:
        """Convert JSON response into an error object"""
        error_code = data.get("errorCode")
        if error_code is None:
            return None
        return TekDriveAPIException(to_snake_case(data))

    @classmethod
    def check_error(cls, data: Union[List[Any], Dict[str, Dict[str, str]]]):
        """Raise an error if the argument resolves to an error object."""
        error = cls.parse_error(data)
        if error:
            raise error

    def __init__(self, client: "Client", models: Optional[Dict[str, Any]] = None):
        self._client = client
        self.models = {} if models is None else models

    def _parse_dict(self, data: dict):
        """Create model from dict."""
        data = to_snake_case(data)
        if data.get("type") == "FILE":
            print("Detected File")
            model = self.models["File"]
        elif data.get("members"):
            print("Detected Members list")
            model = self.models["MembersList"]
        elif {"id", "username", "permissions"}.issubset(data):
            print("Detected Member")
            model = self.models["Member"]
        elif {"file", "upload_url"}.issubset(data):
            model = self.models["File"]
            file = data["file"]
            file["_upload_url"] = data["upload_url"]
            data = file
        else:
            print(f"UNKNOWN MODEL: {data}")
            return data
        return model.parse(data, self._client)

    def parse(
        self, data: Optional[Union[Dict[str, Any], List[Any]]]
    ) -> Optional[Union[Dict[str, Any], List[Any]]]:
        print(f"parse data {data}")
        if data is None:
            # HTTP 204 No Content
            return None

        if isinstance(data, list):
            return [self.parse(item) for item in data]

        if isinstance(data, dict):
            if "errorCode" in data:
                raise TekDriveAPIException(to_snake_case(data))
            return self._parse_dict(data)

        return data
