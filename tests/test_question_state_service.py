import unittest
from unittest.mock import patch

from services import QuestionStateService, QuestionService


class QuestionStateServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.session_id = 'mysessionid'
        self.project_id = 'myproject_id'
        self.questions = [
            {
                'text': 'question1',
                'context': 'question1',
                'correct_response': 'response1, response2',
                'description': 'Description1'
            },
            {
                'text': 'question2',
                'context': 'question2',
                'correct_response': 'response3, response4',
                'description': 'Description2'
            }
        ]
        self.contexts = [
            {'name': 'mycontext', 'parameters': {}},
            {'name': 'mycontext2', 'parameters': {}}
        ]
        self.text = 'mytext'
        self.service = QuestionStateService(
            self.project_id,
            self.session_id,
            self.contexts,
            self.questions,
            self.text)

    def test_get_next_state_from_context_finish(self):
        expected_state = self.service.STATE_FINISH_GAME
        self.service.text = 'no'

        next_state = self.service.get_next_state_from_context()

        self.assertEqual(next_state, expected_state)

    def test_get_next_state_from_context_send_question(self):
        expected_state = self.service.STATE_SEND_QUESTION
        self.service.text = 'mytext'

        next_state = self.service.get_next_state_from_context()

        self.assertEqual(next_state, expected_state)

    def test_get_next_state_from_context_answer_question(self):
        expected_state = self.service.STATE_ANSWER_QUESTION
        self.service.text = 'mytext'
        self.service.contexts = [
            {'name': self.service.get_context_path('question')}
        ]

        next_state = self.service.get_next_state_from_context()

        self.assertEqual(next_state, expected_state)

    def test_is_question_context_present_return_false(self):
        self.service.contexts = []

        is_present = self.service.is_question_context_present()

        self.assertFalse(is_present)

    def test_is_question_context_present_return_true(self):
        self.service.contexts = [
            {'name': self.service.get_context_path('question')}
        ]

        is_present = self.service.is_question_context_present()

        self.assertTrue(is_present)

    def test_get_next_response_from_request_return_finish_response(self):

        response = self.service.get_next_response_from_request(
            self.service.STATE_FINISH_GAME)

        self.assertEqual(
            response, self.service.question_service.FINISH_GAME_RESPONSE)

    @patch.object(QuestionService, 'get_question')
    def test_get_next_response_from_request_return_send_question_response(
        self, get_question):
        self.service.contexts = []
        get_question.return_value = self.questions[0]

        response = self.service.get_next_response_from_request(
            self.service.STATE_SEND_QUESTION)

        self.assertEqual(response, self.questions[0]['text'])

    def test_get_next_response_from_request_return_answer_question_response_correct(self):
        self.service.text = 'response1'
        self.service.contexts = [
            {'name': self.service.get_context_path('question'),
             'parameters': {'question': self.questions[0]['context']}
             }
        ]
        expected_response = self.service.question_service.CORRECT_QUESTION_FORMAT.format(
            self.questions[0]['correct_response'],
            self.questions[0]['description'])

        response = self.service.get_next_response_from_request(
            self.service.STATE_ANSWER_QUESTION)

        self.assertEqual(response, expected_response)

    def test_get_next_response_from_request_return_answer_question_response_incorrect(self):
        self.service.contexts = [
            {'name': self.service.get_context_path('question'),
             'parameters': {'question': self.questions[0]['context']}
             }
        ]
        expected_response = self.service.question_service.INCORRECT_QUESTION_FORMAT.format(
            self.questions[0]['correct_response'])

        response = self.service.get_next_response_from_request(
            self.service.STATE_ANSWER_QUESTION)

        self.assertEqual(response, expected_response)

    def test_get_question_from_context_notfound(self):
        self.service.contexts = []

        question = self.service.get_question_from_context()

        self.assertFalse(question)

    def test_get_question_from_context_found_question(self):
        self.service.contexts = [
            {'name': self.service.get_context_path('question'),
             'parameters': {'question': self.questions[0]['context']}
             }
        ]

        question = self.service.get_question_from_context()

        self.assertTrue(question)

    def test_get_questions_history_notfound(self):
        self.service.contexts = []

        questions = self.service.get_questions_history()

        self.assertFalse(questions)

    def test_get_questions_history_valid_context(self):
        self.service.contexts = [
            {'name': self.service.get_context_path('question_history'),
             'parameters': {'questions': ['question1']}
             }
        ]

        question = self.service.get_questions_history()

        self.assertTrue(question)


    def test_get_next_context_from_request_finish_state(self):
        next_state = self.service.STATE_FINISH_GAME

        context = self.service.get_next_context_from_request(next_state)

        self.assertFalse(context)

    def test_get_next_context_from_request_send_question_state(self):
        next_state = self.service.STATE_SEND_QUESTION
        expected_contexts_length = 4

        contexts = self.service.get_next_context_from_request(
            next_state, self.questions[0]['text'])

        self.assertEqual(len(contexts), expected_contexts_length)

    def test_get_next_context_from_request_answer_question_state(self):
        next_state = self.service.STATE_ANSWER_QUESTION
        expected_contexts_length = 2

        contexts = self.service.get_next_context_from_request(next_state)

        self.assertEqual(len(contexts), expected_contexts_length)

    def test_get_context_path(self):
        context = 'mycontext'
        expected_result = 'projects/myproject_id/agent/sessions/mysessionid/contexts/{}'.format(context)

        context_path = self.service.get_context_path(context)

        self.assertEqual(context_path, expected_result)
