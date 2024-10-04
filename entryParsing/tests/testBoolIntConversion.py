import unittest
from entryParsing.common.utils import boolToInt, intToBool

class TestBoolIntConversion(unittest.TestCase):

    def testIntToBool(self):
        self.assertEqual(intToBool(1), True)
        self.assertEqual(intToBool(0), False)

    def testIntToBoolThrowsErrorWhenGivenInvalidNumber(self):
        with self.assertRaises(Exception) as context:
            intToBool(3)
        self.assertEqual(str(context.exception), "There was an error parsing int to bool")

    def testBoolInt(self):
        self.assertEqual(boolToInt(True), 1)
        self.assertEqual(boolToInt(False), 0)
