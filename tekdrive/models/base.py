"""Provide the TekDriveBase model"""
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Optional

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
