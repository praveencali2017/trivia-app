import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:{}@{}/{}".format('post','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            # drop tables drop all is not working!!!, hence drop each table
            Question.__table__.drop(self.db.get_engine())
            Category.__table__.drop(self.db.get_engine())

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_api_categories_success(self):
        category = Category("Science")
        category.insert()
        to_test = {'categories': {
            f'{category.id}': 'Science'
        }}
        response = self.client().get("/api/categories")
        res_data = response.get_json()
        self.assertEqual(res_data, to_test, msg= 'test_api_categories_success Success!!!!')

    def test_api_categories_failure(self):
        response = self.client().get("/api/category")
        self.assertEqual(response.status_code, 404, msg= 'test_api_categories_failure Success!!!')

    def test_api_questions_success(self):
        category = Category("Test")
        category.insert()
        question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
        question.insert()
        question_1 = Question("How many burgers did Prav sell in his lifetime?", "Ten", category.id, 2)
        question_1.insert()
        req_data = {
            'searchTerm': "many"
        }
        expected_data = {
            'questions': [question.format(), question_1.format()],
            'totalQuestions': 2,
            'currentCategory': None
        }
        response = self.client().post("/api/questions", json = req_data)
        res_data = response.get_json()
        self.assertEqual(expected_data, res_data, msg= "test_api_questions_success, Success!!!!")

    def test_api_questions_not_found(self):
        category = Category("Test")
        category.insert()
        question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
        question.insert()
        question_1 = Question("How many burgers did Prav sell in his lifetime?", "Ten", category.id, 2)
        question_1.insert()
        # when we don't find the match
        req_data = {
            'searchTerm': 3
        }
        expected_data = {
            'questions': [],
            'totalQuestions': 0,
            'currentCategory': None
        }
        response = self.client().post("/api/questions", json = req_data)
        res_data = response.get_json()
        self.assertEqual(expected_data, res_data, msg= "test_api_questions_success, Not found!!!!")

    def test_api_delete_question_success(self):
        category = Category("Test")
        category.insert()
        question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
        question.insert()
        response = self.client().delete(f"/api/questions/{question.id}")
        self.assertEqual(response.status_code, 200, msg= "test_api_delete_question_success")

    def test_api_delete_question_failure(self):
        category = Category("Test")
        category.insert()
        question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
        question.insert()
        response = self.client().delete(f"/api/questions/5")
        self.assertEqual(response.status_code, 400, msg= "test_api_delete_question_failure")

    def test_api_add_question_success(self):
        category = Category("Test")
        category.insert()
        question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
        question.insert()
        req_data = {**question.format()}
        del req_data['id']
        response = self.client().post(f"/api/question", json = req_data)
        res_data = response.get_json()
        self.assertEqual(res_data['success'], True, msg= "test_api_add_question_success")

    def test_api_add_question_failure(self):
        category = Category("Test")
        category.insert()
        question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
        question.insert()
        req_data = {**question.format()}
        # Let's comment it, so that id will go in with the request, which is not supposed to, server should raise 500
        # del req_data['id']
        response = self.client().post(f"/api/question", json = req_data)
        self.assertEqual(response.status_code, 500, msg= "test_api_add_question_failure")


    def test_api_categories_questions_success(self):
        category, question = build_dummy_category_question()
        response = self.client().get(f"/api/categories/{category.id}/questions")
        res_data = response.get_json()
        expected_data = {
            'questions': [question.format()],
            'totalQuestions': 1,
            'currentCategory': '1'
        }
        expected_data.update({'categories': {'1': 'Test'}})
        self.assertEqual(expected_data, res_data, msg= 'test_api_categories_questions_success')


    def test_api_categories_questions_failure(self):
        _, question = build_dummy_category_question()
        # category id 2 is not present, so everything should be empty
        response = self.client().get(f"/api/categories/{2}/questions")
        res_data = response.get_json()
        expected_data = {
            'questions': [],
            'totalQuestions': 0,
            'currentCategory': '2'
        }
        expected_data.update({'categories': {}})
        self.assertEqual(expected_data, res_data, msg= 'test_api_categories_questions_failure')

    def test_api_quizzes_success(self):
        category, question = build_dummy_category_question()
        expected_data = {
            'question': question.format()
        }
        req_data = {
            'previous_questions': [],
            'quiz_category': {'id': 0}
        }
        response = self.client().post('/api/quizzes', json = req_data)
        res_data = response.get_json()
        self.assertEqual(expected_data, res_data, msg= "test_api_quizzes_success")

    def test_api_quizzes_with_prev_success(self):
        category, question = build_dummy_category_question()
        category_1, question_1 = build_dummy_category_question()
        expected_data = {
            'question': question_1.format()
        }
        req_data = {
            'previous_questions': [question.id],
            'quiz_category': {'id': 0}
        }
        response = self.client().post('/api/quizzes', json = req_data)
        res_data = response.get_json()
        self.assertEqual(expected_data, res_data, msg= "test_api_quizzes_with_prev_success")

def build_dummy_category_question():
    category = Category("Test")
    category.insert()
    question = Question("How many paintings did Van Gogh sell in his lifetime?", "One", category.id, 4)
    question.insert()
    return category, question




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()