from unittest import TestCase
from unittest import mock

from flexp.experiment import BaseExperiment


class TestInitialization(TestCase):

    def setUp(self):
        self.patches = {
            'window': mock.patch('psychopy.visual.Window'),
            'dpp': mock.patch('flexp.experiment.dppWindow'),
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
        self.mocks['dpp'].assert_not_called()
        self.assertEqual(expr.win, self.mocks['window'].return_value)

    def test_develop_true_can_still_overwrite_wintype(self):
        expr = BaseExperiment(develop=True, winType='pyglet')
        self.mocks['window'].assert_called_once_with(winType='pyglet')
        self.mocks['dpp'].assert_not_called()
        self.assertEqual(expr.win, self.mocks['window'].return_value)

    def test_develop_false_creates_dpp(self):
        expr = BaseExperiment(develop=False)
        self.mocks['window'].assert_not_called()
        self.mocks['dpp'].assert_called_once_with()
        self.assertEqual(expr.win, self.mocks['dpp'].return_value)

    def test_additional_kwds_are_passed_through(self):
        for key, develop in [('window', True), ('dpp', False)]:
            with self.subTest(develop=develop):
                BaseExperiment(develop=develop,
                               winType='ANY_WINTYPE',  # for develop=True
                               any_keyword='ANY_VALUE')
                self.mocks[key].assert_called_once_with(
                    winType='ANY_WINTYPE',
                    any_keyword='ANY_VALUE')
