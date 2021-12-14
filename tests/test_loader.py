import pytest

import unittest

import json

from src.core.loader import SchemaLoader


class TestSchemeLoader(unittest.TestCase):

    def setUp(self):
        self.loader = SchemaLoader()

    def test_loading(self):
        test_file = json.dumps({
                "header": {
                    "attributes": None,
                    "columns": [
                        {
                            "index": 1,
                            "name": "1foo",
                            "optional": False,
                            "regex": "(?i)^\\d+foo$"
                        },
                        {
                            "index": 2,
                            "name": "2bar",
                            "optional": False,
                            "regex": "(?i)^\\d+bar$"
                        },
                    ]
                },
                "name": "test"
            })
        test_data = self.loader.load(test_file)
        assert test_data
        assert isinstance(test_data, dict)
        
    def test_dumping(self):
        