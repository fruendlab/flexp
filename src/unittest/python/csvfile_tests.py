from unittest import TestCase
from unittest import mock
import logging

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
    @mock.patch('flexp.utils.read_line')
    @mock.patch('flexp.utils.write_line')
    def test_init_doesnt_create_file_if_exists(self,
                                               write_line,
                                               read_line,
                                               exists):
        read_line.return_value = 'ANY_COLUMN,OTHER_COLUMN\n'
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
            with mock.patch('flexp.utils.read_line') as read_line:
                exists.return_value = True
                read_line.return_value = 'ANY_COLUMN,OTHER_COLUMN\n'
                self.csv = csvfile.CsvFile('ANY_FILE_NAME',
                                           ['ANY_COLUMN', 'OTHER_COLUMN'])
        self.write_line = mock.patch('flexp.utils.write_line').start()
        logging.disable(logging.CRITICAL)  # We don't want logging in tests

    def tearDown(self):
        mock.patch.stopall()

    def test_ok_if_same_columns(self):
        self.assertTrue(
            self.csv._validate_columns({'ANY_COLUMN': 'val',
                                        'OTHER_COLUMN': 'val'}))

    def test_ok_if_same_columns_different_order(self):
        self.assertTrue(
            self.csv._validate_columns({'OTHER_COLUMN': 'val',
                                        'ANY_COLUMN': 'val'}))

    def test_fails_if_missing_columns(self):
        self.assertFalse(
            self.csv._validate_columns({'ANY_COLUMN': 'val'}))

    def test_fails_if_additional_columns(self):
        self.assertFalse(
            self.csv._validate_columns({'ANY_COLUMN': 'val',
                                        'OTHER_COLUMN': 'val',
                                        'WRONG': 'val'}))


class TestCsvFileAddRecord(TestCase):

    def setUp(self):
        with mock.patch('os.path.exists') as exists:
            with mock.patch('flexp.utils.read_line') as read_line:
                exists.return_value = True
                read_line.return_value = 'ANY_COLUMN,OTHER_COLUMN\n'
                self.csv = csvfile.CsvFile('ANY_FILE_NAME',
                                           ['ANY_COLUMN', 'OTHER_COLUMN'])
        self.write_line = mock.patch('flexp.utils.write_line').start()
        self.csv._validate_columns = mock.patch.object(
            self.csv,
            '_validate_columns').start()

    def tearDown(self):
        mock.patch.stopall()

    def test_writes_to_file(self):
        self.csv._validate_columns.return_value = True
        self.csv.add_record({'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})
        self.write_line.assert_called_once_with(
            'val,val\n', self.csv.filename, 'a')

    def test_checks_for_invalid_columns(self):
        self.csv._validate_columns.return_value = True
        self.csv.add_record({'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})
        self.csv._validate_columns.assert_called_once_with(
            {'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})

    def test_fails_for_invalid_columns(self):
        self.csv._validate_columns.return_value = False
        with self.assertRaises(ValueError):
            self.csv.add_record({'ANY_COLUMN': 'val', 'OTHER_COLUMN': 'val'})

    def test_converts_everything_to_repr(self):
        self.csv._validate_columns.return_value = True
        self.csv.add_record({'ANY_COLUMN': 1.0, 'OTHER_COLUMN': None})
        self.write_line.assert_called_once_with(
            '1.0,None\n', self.csv.filename, 'a')


class TestCsvFileValidateHeader(TestCase):

    def test_match(self):
        csvfile.CsvFile._validate_header('ANY_COLUMN,OTHER_COLUMN\n',
                                         ['ANY_COLUMN', 'OTHER_COLUMN'])

    def test_too_many(self):
        with self.assertRaises(ValueError):
            csvfile.CsvFile._validate_header(
                'ANY_COLUMN,OTHER_COLUMN\n',
                ['ANY_COLUMN', 'OTHER_COLUMN', 'ADDED'])

    def test_too_few(self):
        with self.assertRaises(ValueError):
            csvfile.CsvFile._validate_header(
                'ANY_COLUMN,OTHER_COLUMN\n',
                ['ANY_COLUMN'])

    def test_different(self):
        with self.assertRaises(ValueError):
            csvfile.CsvFile._validate_header(
                'ANY_COLUMN,OTHER_COLUMN\n',
                ['ANY_COLUMN', 'SHOULDNT_BE_HERE'])
