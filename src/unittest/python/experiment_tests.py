from unittest import TestCase
from unittest import mock

from flexp.experiment import BaseExperiment


class TestInitialization(TestCase):

    def setUp(self):
        self.patches = {
            'window': mock.patch('psychopy.visual.Window'),
            'dpp': mock.patch('flexp.display.dppWindow'),
            'circle': mock.patch('psychopy.visual.Circle'),
            'textstim': mock.patch('psychopy.visual.TextStim'),
            'sound': mock.patch('flexp.experiment.Sound'),
        }

        self.mocks = {
            key: patch.start() for key, patch in self.patches.items()
        }

    def tearDown(self):
        mock.patch.stopall()

    def test_develop_true_creates_standard_window(self):
        expr = BaseExperiment(develop=True)
        self.mocks['window'].assert_called_once_with(winType='pygame')
        self.assertEqual(expr.win, self.mocks['window'].return_value)
