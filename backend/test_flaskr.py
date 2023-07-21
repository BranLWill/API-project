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
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path ="postgres://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_all_categories(self):
        response = self.client.get('http://127.0.0.1:5000/categories')
        
        # Verify the response status code
        self.assertEqual(response.status_code, 200)
        
        # Verify that the returned data is not empty
        data = response.get_json()
        print(data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify that the data is in the expected format
        self.assertIn('categories', data)
        categories = data['categories']
        self.assertIsInstance(categories, dict)

        for id, catagory in categories.items():
            print(f"{id} - {catagory}")
            
    def test_get_questions(self):
        response = self.client.get('/questions')
        
        # Verify the response status code
        self.assertEqual(response.status_code, 200)
        
        # Verify that the returned data is not empty
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify that the data is in the expected format
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        self.assertIn('categories', data)
        self.assertIn('current_category', data)

        questions = data['questions']
        total_questions = data['total_questions']
        categories = data['categories']
        current_category = data['current_category']

        self.assertIsInstance(questions, list)
        self.assertIsInstance(total_questions, int)
        self.assertIsInstance(categories, list)
        self.assertIsNone(current_category)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
