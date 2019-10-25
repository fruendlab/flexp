from unittest import TestCase
from unittest import mock

from flexp.experiment import BaseExperiment


class TestInitialization(TestCase):

    def setUp(self):
        self.patches = {
            'window': mock.patch('flexp.experiment.visual.Window'),
            'dpp': mock.patch('flexp.experiment.dppWindow'),
            'circle': mock.patch('flexp.experiment.visual.Circle'),
            'textstim': mock.patch('flexp.experiment.visual.TextStim'),
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

    def test_creates_fixation_point_of_size_1pix(self):
        expr = BaseExperiment()
        self.mocks['circle'].assert_called_once_with(
            expr.win, size=1, units='pix')
        self.assertEqual(expr.fixation, self.mocks['circle'].return_value)

    def test_creates_text_element(self):
        expr = BaseExperiment()
        self.mocks['textstim'].assert_called_once_with(expr.win)
        self.assertEqual(expr.txt, self.mocks['textstim'].return_value)

    def test_creates_sound(self):
        expr = BaseExperiment()
        self.mocks['sound'].assert_called_once_with(200, secs=0.2)
        self.assertEqual(expr.beep, self.mocks['sound'].return_value)


class TestMethods(TestCase):

    def setUp(self):
        with mock.patch.multiple('flexp.experiment',
                                 dppWindow=mock.MagicMock(),
                                 Sound=mock.MagicMock()):
            with mock.patch.multiple('flexp.experiment.visual',
                                     Window=mock.MagicMock(),
                                     Circle=mock.MagicMock(),
                                     TextStim=mock.MagicMock()):
                self.expr = BaseExperiment()

    def test_do_a_trial_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.expr.do_a_trial()

    def test_feedback_beeps_for_incorrect(self):
        self.expr.feedback(False)
        self.expr.beep.play.assert_called_once_with()

    def test_feedback_doesnt_beep_for_correct(self):
        self.expr.feedback(True)
        self.expr.beep.play.assert_not_called()

    def test_draw_and_flip_draws_every_object_before_flipping(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()

        def check_called():
            obj1.draw.assert_called_once_with()
            obj2.draw.assert_called_once_with()

        self.expr.win.flip.side_effect = check_called

        self.expr.draw_and_flip(obj1, obj2)

        self.expr.win.flip.assert_called_once_with()

    @mock.patch('flexp.experiment.event.waitKeys')
    def test_message_shows_message_and_waits_for_keys(self, waitKeys):
        self.expr.draw_and_flip = mock.MagicMock()

        def check_called():
            self.assertEqual(self.expr.txt.text, 'ANY_MESSAGE')
            self.expr.draw_and_flip.assert_called_once_with(self.expr.txt)

        waitKeys.side_effect = check_called

        self.expr.message('ANY_MESSAGE')

        waitKeys.assert_called_once_with()
