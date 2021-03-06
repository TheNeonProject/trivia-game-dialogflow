import unittest
from unittest.mock import patch
import os

from services import SpreadsheetReader

class SpreadsheetReaderTestCase(unittest.TestCase):
    @patch.object(SpreadsheetReader, '__init__')
    def setUp(self, sheet_init):
        key = os.environ.get('KEY')
        credentials_file = os.environ.get('SHEET_CREDENTIALS_FILE')
        sheet_init.return_value = None

        self.service = SpreadsheetReader(key, credentials_file)

    @patch.object(SpreadsheetReader, 'get_values_from_sheet')
    def test_get_values_from_sheet(self, get_values_from_sheet):
        get_values_from_sheet.return_value = [
            [ 'pregunta', 'respuesta']
        ]

        values_sheet = self.service.get_values_from_sheet()

        self.assertEqual(len(values_sheet), 1)

    @patch.object(SpreadsheetReader, 'get_first_sheet')
    def test_get_first_sheet(self, get_first_sheet):
        get_first_sheet.return_value = 'sheet 1'

        result = self.service.get_first_sheet('1')

        self.assertEqual(result, 'sheet 1')

    @patch.object(SpreadsheetReader, 'open_sheet')
    def test_open_sheet(self, open_sheet):
        open_sheet.return_value = 'sheet'

        result = self.service.open_sheet('1')

        self.assertEqual(result, 'sheet')
