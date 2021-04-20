import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from ..exceptions import TekDriveAPIException
from ..utils.casing import to_snake_case

if TYPE_CHECKING:
    from .. import TekDrive

log = logging.getLogger(__name__)


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

    def __init__(self, tekdrive: "TekDrive", models: Optional[Dict[str, Any]] = None):
        self._tekdrive = tekdrive
        self.models = {} if models is None else models

    def _parse_dict(self, data: dict):
        """Create model from dict."""
        data = to_snake_case(data)
        if data.get("type") == "FILE":
            model = self.models["File"]
        elif data.get("type") == "FOLDER":
            model = self.models["Folder"]
        elif data.get("members"):
            model = self.models["MembersList"]
        elif {"id", "username", "permissions"}.issubset(data):
            model = self.models["Member"]
        elif {"file", "upload_url"}.issubset(data):
            model = self.models["File"]
            file = data["file"]
            file["_upload_url"] = data["upload_url"]
            data = file
        elif {"meta", "results"}.issubset(data):
            model = self.models["PaginatedList"]
        elif {"meta", "trash"}.issubset(data):
            model = self.models["TrashPaginatedList"]
        elif data.get("trasher"):
            data["id"] = f"trash{data['item']['id']}"
            model = self.models["Trash"]
        elif {"account_id", "owner_type", "plan"}.issubset(data):
            model = self.models["DriveUser"]
        elif {"tree"}.issubset(data):
            # TODO: Rachel handle tree results
            pass
        else:
            log.debug(f"Parsing found unknown model for: {data}")
            return data
        log.debug(f"Parsing using model: {model}")
        return model.parse(data, self._tekdrive)

    def parse(
        self, data: Optional[Union[Dict[str, Any], List[Any]]]
    ) -> Optional[Union[Dict[str, Any], List[Any]]]:
        log.debug(f"Parse data: {data}")
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
