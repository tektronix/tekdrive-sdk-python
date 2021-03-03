"""Provides the Permissions dataclass."""
from dataclasses import dataclass


@dataclass
class Permissions:
    """
    Represents permissions to a TekDrive object.

    Attributes:
        creator (bool): Is the object creator?
        edit (bool): Has edit access?
        read (bool): Has read access?
        owner (bool): Is the object owner?
    """

    read: bool
    edit: bool
    owner: bool = None
    creator: bool = None
    public: bool = None  # currently unused
