from datetime import datetime

import pytz
from django.test import TestCase

from crm.management.commands.import_soil_hardness import extract_device, extract_setdatetime, extract_numeric_value


class TestImportSoilHardness(TestCase):
    def test_extract_device_valid(self):
        line = ['DIK-5531', 'Digital Cone Penetrometer']
        device = extract_device(line[0])
        self.assertEqual('DIK-5531', device)

    def test_extract_device_invalid(self):
        line = ['ABC-1234', 'Invalid Device']
        with self.assertRaises(ValueError):
            extract_device(line[0])

    def test_extract_memory_valid(self):
        line = ['some data', '100']
        memory = extract_numeric_value(line[1], 'memory')
        self.assertEqual(100, memory)

    def test_extract_memory_invalid(self):
        line = ['some data', 'invalid']
        with self.assertRaises(ValueError):
            extract_numeric_value(line[1], 'memory')

    def test_extract_setdepth_valid(self):
        line = ['some data', '50']
        setdepth = extract_numeric_value(line[1], 'setdepth')
        self.assertEqual(50, setdepth)

    def test_extract_setdepth_invalid(self):
        line = ['some data', 'invalid']
        with self.assertRaises(ValueError):
            extract_numeric_value(line[1], 'setdepth')

    def test_extract_setdatetime_valid(self):
        line = ['some data', ' 23.07.01 12:34:56']
        setdatetime = extract_setdatetime(line[1])
        expected_datetime = pytz.timezone('Asia/Tokyo').localize(datetime(2023, 7, 1, 12, 34, 56))
        self.assertEqual(expected_datetime, setdatetime)

    def test_extract_setdatetime_invalid(self):
        line = ['some data', 'invalid']
        with self.assertRaises(ValueError):
            extract_setdatetime(line[1])

    def test_extract_setspring_valid(self):
        line = ['some data', '5']
        setspring = extract_numeric_value(line[1], 'setspring')
        self.assertEqual(5, setspring)

    def test_extract_setspring_invalid(self):
        line = ['some data', 'invalid']
        with self.assertRaises(ValueError):
            extract_numeric_value(line[1], 'setspring')

    def test_extract_setcone_valid(self):
        line = ['some data', '10']
        setcone = extract_numeric_value(line[1], 'setcone')
        self.assertEqual(10, setcone)

    def test_extract_setcone_invalid(self):
        line = ['some data', 'invalid']
        with self.assertRaises(ValueError):
            extract_numeric_value(line[1], 'setcone')
