import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from ..enums import ErrorCode, ObjectType
from ..exceptions import TekDriveAPIException, ERROR_CODE_TO_API_EXCEPTION_MAPPING
from ..utils.casing import to_snake_case

if TYPE_CHECKING:
    from .. import TekDrive

log = logging.getLogger(__name__)


class Parser:
    @classmethod
    def parse_error(
        cls, data: Union[List[Any], Dict[str, Dict[str, str]]], *, headers
    ) -> Optional[TekDriveAPIException]:
        """Convert JSON response into an API error"""
        data = to_snake_case(data)
        error_code = data.get("error_code")
        if error_code is None:
            # doesnt match expected error format from API
            return None

        try:
            error_code = ErrorCode(error_code)
        except ValueError:
            return TekDriveAPIException(data, headers=headers)

        if error_code in ERROR_CODE_TO_API_EXCEPTION_MAPPING:
            return ERROR_CODE_TO_API_EXCEPTION_MAPPING[error_code](
                to_snake_case(data), headers=headers
            )

        return TekDriveAPIException(data, headers=headers)

    def __init__(self, tekdrive: "TekDrive", models: Optional[Dict[str, Any]] = None):
        self._tekdrive = tekdrive
        self.models = {} if models is None else models

    def _is_file(self, data: dict) -> bool:
        return data.get("type") == ObjectType.FILE.value

    def _is_file_with_upload_url(self, data: dict) -> bool:
        return {"file", "upload_url"}.issubset(data)

    def _is_folder(self, data: dict) -> bool:
        return data.get("type") == ObjectType.FOLDER.value

    def _is_members_list(self, data: dict) -> bool:
        return "members" in data

    def _is_member(self, data: dict) -> bool:
        return {"id", "username", "permissions"}.issubset(data)

    def _is_paginated_list(self, data: dict) -> bool:
        return "meta" in data

    def _is_trash(self, data: dict) -> bool:
        return "trasher" in data

    def _is_drive_user(self, data: dict) -> bool:
        return {"account_id", "owner_type", "plan"}.issubset(data)

    def _is_tree(self, data: dict) -> bool:
        return "tree" in data

    def _parse_dict(self, data: dict):
        """Create model from dict."""
        data = to_snake_case(data)
        if self._is_file(data):
            model = self.models["File"]
        elif self._is_folder(data):
            model = self.models["Folder"]
        elif self._is_members_list(data):
            model = self.models["MembersList"]
        elif self._is_member(data):
            model = self.models["Member"]
        elif self._is_file_with_upload_url(data):
            model = self.models["File"]
            file = data["file"]
            file["_upload_url"] = data["upload_url"]
            data = file
        elif self._is_paginated_list(data):
            if "trash" in data:
                model = self.models["TrashPaginatedList"]
            else:
                # generic paginated list
                model = self.models["PaginatedList"]
        elif self._is_trash(data):
            data["id"] = f"trash{data['item']['id']}"
            model = self.models["Trash"]
        elif self._is_drive_user(data):
            model = self.models["DriveUser"]
        elif self._is_tree(data):
            tree_folder = data["tree"]
            data = tree_folder
            model = self.models["Folder"]
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
            return self._parse_dict(data)

        return data
