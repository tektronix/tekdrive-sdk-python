"""Provide the TekDriveBase model"""
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .. import Client


class TekDriveBase:
    @staticmethod
    def _safely_add_arguments(argument_dict, key, **new_arguments):
        """Replace argument_dict[key] with a deepcopy and update.

        This method is often called when new parameters need to be added to a request.
        By calling this method and adding the new or updated parameters we can insure we
        don't modify the dictionary passed in by the caller.
        """
        value = deepcopy(argument_dict[key]) if key in argument_dict else {}
        value.update(new_arguments)
        argument_dict[key] = value

    @classmethod
    def parse(cls, data: Dict[str, Any], client: "Client") -> Any:
        """Return an instance of ``cls`` from ``data``.

        :param data: The structured data.
        :param client: An instance of :class:`.Client`.

        """
        return cls(client, _data=data)

    def __init__(self, client: "Client", _data: Optional[Dict[str, Any]]):
        self._client = client
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)


class BaseList(TekDriveBase):
    """An abstract class to coerce a list into a TekDriveBase."""

    CHILD_ATTRIBUTE = None

    def __init__(self, client: "Client", _data: Dict[str, Any]):
        super().__init__(client, _data=_data)

        if self.CHILD_ATTRIBUTE is None:
            raise NotImplementedError("BaseList must be extended.")

        child_list = getattr(self, self.CHILD_ATTRIBUTE)
        for index, item in enumerate(child_list):
            child_list[index] = client._parser.parse(item)

    def __contains__(self, item: Any) -> bool:
        """Test if item exists in the list."""
        return item in getattr(self, self.CHILD_ATTRIBUTE)

    def __getitem__(self, index: int) -> Any:
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator to the list."""
        return getattr(self, self.CHILD_ATTRIBUTE).__iter__()

    def __len__(self) -> int:
        """Return the number of items in the list."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __str__(self) -> str:
        """Return a string representation of the list."""
        return str(getattr(self, self.CHILD_ATTRIBUTE))
