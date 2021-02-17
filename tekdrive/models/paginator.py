from copy import deepcopy
from .base import TekDriveBase
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive
    from ..routing import Route


class PaginatedList(TekDriveBase):
    CHILD_ATTRIBUTE = "results"
    META_ATTRIBUTE = "meta"

    def __len__(self) -> int:
        """Return the number of items in the full list."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __getitem__(self, index: int) -> Any:
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __setattr__(self, attribute: str, value: Any):
        """Objectify the CHILD_ATTRIBUTE attribute."""
        if attribute == self.CHILD_ATTRIBUTE:
            value = self._tekdrive._parser.parse(value)
        super().__setattr__(attribute, value)

    @property
    def page(self) -> int:
        return getattr(self, self.META_ATTRIBUTE)["page"]

    @property
    def limit_per_page(self) -> int:
        return getattr(self, self.META_ATTRIBUTE)["limit"]


class PaginatedListGenerator(TekDriveBase, Iterator):

    def __init__(
        self,
        tekdrive: "TekDrive",
        route: "Route",
        limit: int = 100,
        limit_per_page: int = 100,
        params: Optional[Dict[str, Union[str, int]]] = None,
    ):
        """Initialize a PaginatedListGenerator instance.

        :param tekdrive: An instance of :class:`.TekDrive`.
        :param route: A Route for an API endpoint returning a paginated list.
        :param limit: Number of total results to fetch.
        :param params: A dictionary containing additional query string parameters to
            send with the request.
        """
        super().__init__(tekdrive, _data=None)
        self._exhausted = False
        self._list = None
        self._list_index = None
        self.limit = limit  # total results limit
        self.params = deepcopy(params) if params else {}
        self.params["limit"] = min(limit, limit_per_page)  # limit for a single page
        self.route = route
        self.yielded = 0

    def __iter__(self) -> Iterator[Any]:
        """Permit ListingGenerator to operate as an iterator."""
        return self

    def __next__(self) -> Any:
        """Permit ListingGenerator to operate as a generator."""
        if self.limit is not None and self.yielded >= self.limit:
            raise StopIteration()

        if self._list is None or self._list_index >= len(self._list):
            self._next_batch()

        self._list_index += 1
        self.yielded += 1
        return self._list[self._list_index - 1]

    def _next_batch(self):
        if self._exhausted:
            raise StopIteration()

        self._list = self._tekdrive.request(self.route, params=self.params)
        self._list_index = 0

        if not self._list:
            raise StopIteration()

        if len(self._list) == self._list.limit_per_page:
            # go to next page
            self.params["page"] = self._list.page + 1
        else:
            self._exhausted = True
