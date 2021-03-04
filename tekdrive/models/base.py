"""Provide the TekDriveBase model"""
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

if TYPE_CHECKING:
    from .. import TekDrive


class TekDriveBase:
    @classmethod
    def parse(cls, data: Dict[str, Any], tekdrive: "TekDrive") -> Any:
        """
        Return an instance of ``cls`` from ``data``.

        Args:
            data: The structured data.
            tekdrive: An instance of :class:`.TekDrive`.

        """
        return cls(tekdrive, _data=data)

    def __init__(self, tekdrive: "TekDrive", _data: Optional[Dict[str, Any]]):
        self._tekdrive = tekdrive
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)


class BaseList(TekDriveBase):

    LIST_ATTRIBUTE = None

    def __init__(self, tekdrive: "TekDrive", _data: Dict[str, Any]):
        super().__init__(tekdrive, _data=_data)

        if self.LIST_ATTRIBUTE is None:
            raise NotImplementedError("LIST_ATTRIBUTE is required.")

        child_list = getattr(self, self.LIST_ATTRIBUTE)
        for idx, item in enumerate(child_list):
            child_list[idx] = tekdrive._parser.parse(item)

    def __contains__(self, item: Any) -> bool:
        return item in getattr(self, self.LIST_ATTRIBUTE)

    def __getitem__(self, idx: int) -> Any:
        return getattr(self, self.LIST_ATTRIBUTE)[idx]

    def __iter__(self) -> Iterator[Any]:
        return getattr(self, self.LIST_ATTRIBUTE).__iter__()

    def __len__(self) -> int:
        return len(getattr(self, self.LIST_ATTRIBUTE))

    def __str__(self) -> str:
        return str(getattr(self, self.LIST_ATTRIBUTE))
