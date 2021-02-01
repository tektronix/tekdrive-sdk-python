import pytest
from tekdrive.utils.casing import to_snake_case

from ..base import UnitTest


class TestCasing(UnitTest):

    @pytest.mark.parametrize("test_input,expected", [
        ("snake_case", "snake_case"),
        ("camelCase", "camel_case"),
        ("PascalCase", "pascal_case"),
        ("HTTPErrorCode", "http_error_code"),
        ("404HTTPCode", "404http_code"),
        ("ownerId", "owner_id"),
        ("parentFolderId", "parent_folder_id"),
    ])
    def test_to_snake_case_simple(self, test_input, expected):
        assert to_snake_case(test_input) == expected

    def test_to_snake_case_dict(self):
        camel_keys = {
            "trashedAt": None,
            "uploadState": "SUCCESS",
            "bytes": "100321",
            "type": "FILE",
            "parentFolderId": "33ac8720-7292-4272-bb3f-90315352a04b",
        }

        expected = {
            "trashed_at": None,
            "upload_state": "SUCCESS",
            "bytes": "100321",
            "type": "FILE",
            "parent_folder_id": "33ac8720-7292-4272-bb3f-90315352a04b",
        }

        assert to_snake_case(camel_keys) == expected

    def test_to_snake_case_nested_dicts(self):
        camel_keys = {
            "ownerId": "ea29f0df-ad46-4601-8110-0e926ce6c6e3",
            "tree": {
                "id": "5f6dcf17-1935-4993-bae0-27e2d6dcd6a0",
                "owner": {
                    "exampleId": "ea29f0df-ad46-4601-8110-0e926ce6c6e3",
                    "exampleUsername": "me@example.com"
                },
                "children": [
                    {
                        "uploadState": "SUCCESS",
                        "allFlags": {
                            "foo": 1,
                            "fooBar": {
                                "barBaz": 2
                            }
                        }
                    },
                    {
                        "uploadState": "PENDING",
                    }
                ]
            }
        }

        expected = {
            "owner_id": "ea29f0df-ad46-4601-8110-0e926ce6c6e3",
            "tree": {
                "id": "5f6dcf17-1935-4993-bae0-27e2d6dcd6a0",
                "owner": {
                    "example_id": "ea29f0df-ad46-4601-8110-0e926ce6c6e3",
                    "example_username": "me@example.com"
                },
                "children": [
                    {
                        "upload_state": "SUCCESS",
                        "all_flags": {
                            "foo": 1,
                            "foo_bar": {
                                "bar_baz": 2
                            }
                        }
                    },
                    {
                        "upload_state": "PENDING",
                    }
                ]
            }
        }

        assert to_snake_case(camel_keys) == expected
