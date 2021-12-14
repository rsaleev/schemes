import pytest

import unittest

from src.core.schemes.workbook import *

class TestWorkbookSchemes(unittest.TestCase):
    
    def setUp(self) -> None:
        self.workbook_schemes = WorkbookSchemes()
