"""Provides the Artifact class."""
from typing import TYPE_CHECKING, Optional, Dict, Any, Union

from .base import DriveBase
from ..base import BaseList

if TYPE_CHECKING:
    from .. import TekDrive


class Artifact(DriveBase):
    """
    Represents a file artifact.

    Attributes:
        bytes (str): Artifact size in bytes.
        created_at (datetime): When the artifact was created.
        context_type (str): Context to identify the type of artifact such as ``"SETTING"`` or ``"CHANNEL"``.
        file_id (str): ID of the file that the artifact is associated with.
        file_type (str): Artifact file type such as ``"TSS"`` or ``"SET"``.
        id (str): Unique artifact ID.
        name (str): Artifact name.
        parent_artifact_id: ID of the parent artifact.
        updated_at (datetime, optional): When the artifact was last updated.
    """

    STR_FIELD = "id"

    @classmethod
    def from_data(cls, tekdrive, data):
        return cls(tekdrive, data)

    def __init__(
        self,
        tekdrive: "TekDrive",
        _data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(tekdrive, _data=_data)

    def __setattr__(
        self,
        attribute: str,
        value: Union[str, int, Dict[str, Any]],
    ):
        super().__setattr__(attribute, value)


class ArtifactsList(BaseList):
    """List of artifacts"""

    _parent = None

    LIST_ATTRIBUTE = "artifacts"
