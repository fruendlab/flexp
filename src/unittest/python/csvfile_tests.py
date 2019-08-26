from unittest import TestCase
from unittest import mock

from flexp import csvfile


class TestCsvFile(TestCase):

    @mock.patch('os.path.exists')
    @mock.patch('flexp.utils.write_line')
    def test_init_creates_file_not_exists(self, write_line, exists):
        exists.return_value = False
        csv = csvfile.CsvFile('ANY_FILE_NAME', ['ANY_COLUMN', 'OTHER_COLUMN'])
        write_line.assert_called_once_with('ANY_COLUMN,OTHER_COLUMN\n',
                                           'ANY_FILE_NAME',
                                           'w')
        exists.assert_called_once_with('ANY_FILE_NAME')

        self.assertEqual(csv.filename, 'ANY_FILE_NAME')
        self.assertListEqual(csv.column_names,  ['ANY_COLUMN', 'OTHER_COLUMN'])

    @mock.patch('os.path.exists')
    @mock.patch('flexp.utils.write_line')
    def test_init_doesnt_create_file_if_exists(self, write_line, exists):
        exists.return_value = True
        csv = csvfile.CsvFile('ANY_FILE_NAME', ['ANY_COLUMN', 'OTHER_COLUMN'])
        write_line.assert_not_called()
        exists.assert_called_once_with('ANY_FILE_NAME')

        self.assertEqual(csv.filename, 'ANY_FILE_NAME')
        self.assertListEqual(csv.column_names,  ['ANY_COLUMN', 'OTHER_COLUMN'])

    @mock.patch('os.path.exists')
    @mock.patch('flexp.utils.write_line')
    def test_overwrite_although_file_exists(self, write_line, exists):
        exists.return_value = True
        csvfile.CsvFile('ANY_FILE_NAME', ['ANY_COLUMN', 'OTHER_COLUMN'],
                        overwrite=True)
        exists.assert_called_once_with('ANY_FILE_NAME')
        write_line.assert_called_once_with('ANY_COLUMN,OTHER_COLUMN\n',
                                           'ANY_FILE_NAME',
                                           'w')


class TestCsvFileValidateColumns(TestCase):

    def setUp(self):
        with mock.patch('os.path.exists') as exists:
            exists.return_value = True
        self.csv = csvfile.CsvFile('ANY_FILE_NAME',
                                   ['ANY_COLUMN', 'OTHER_COLUMN'])
        self.write_line = mock.patch('flexp.utils.write_line').start()

    def tearDown(self):
        mock.patch.stopall()

    def test_ok_if_same_columns(self):
        self.assertTrue(
            self.csv.validate_columns({'ANY_COLUMN': 'val',
                                       'OTHER_COLUMN': 'val'}))

    def test_ok_if_same_columns_different_order(self):
        self.assertTrue(
            self.csv.validate_columns({'OTHER_COLUMN': 'val',
                                       'ANY_COLUMN': 'val'}))

    def test_fails_if_missing_columns(self):
        self.assertFalse(
            self.csv.validate_columns({'ANY_COLUMN': 'val'}))

    def test_fails_if_additional_columns(self):
        self.assertFalse(
            self.csv.validate_columns({'ANY_COLUMN': 'val',
                                       'OTHER_COLUMN': 'val',
                                       'WRONG': 'val'}))


class TestCsvFileAddRecord(TestCase):

    def setUp(self):
        with mock.patch('os.path.exists') as exists:
            exists.return_value = True
        self.csv = csvfile.CsvFile('ANY_FILE_NAME',
                                   ['ANY_COLUMN', 'OTHER_COLUMN'])
        self.write_line = mock.patch('flexp.utils.write_line').start()
        self.csv.validate_columns = mock.patch.object(
            self.csv,
            'validate_columns').start()

    def tearDown(self):
        mock.patch.stopall()

    def test_writes_to_file(self):
        self.csv.validate_columns.return_value = True
        self.csv.add_record({'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})
        self.write_line.assert_called_once_with(
            'val,val\n', self.csv.filename, 'a')

    def test_checks_for_invalid_columns(self):
        self.csv.validate_columns.return_value = True
        self.csv.add_record({'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})
        self.csv.validate_columns.assert_called_once_with(
            {'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})

    def test_fails_for_invalid_columns(self):
        self.csv.validate_columns.return_value = False
        with self.assertRaises(ValueError):
            self.csv.add_record({'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})

    def test_converts_everything_to_repr(self):
        self.csv.validate_columns.return_value = True
        self.csv.add_record({'ANY_COLUMN': 1.0, 'OTHER_COLUMN': None})
        self.write_line.assert_called_once_with(
            '1.0,None\n', self.csv.filename, 'a')
