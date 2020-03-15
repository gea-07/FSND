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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    def test_404_get_categories(self):
        '''Test receiving 404 when getting categories'''
        res = self.client().get('/categories/1')
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(res.status_code, 404)

    def test_get_categories(self):
        """Test getting categories. Prefixed with 100 because the 400 version was deleting categories before this test gets called"""
        res = self.client().get('/categories')
        data = json.loads(res.data)
        #print(data['categories'])
        categories = {str(category.id):category.type for category in Category.query.order_by(Category.id).all()}

        self.assertTrue(data['success'])
        self.assertEqual(categories, data['categories'])
        self.assertEqual(res.status_code, 200)


    def test_get_questions(self):
        '''Test getting page 1 questions'''
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        #print(data['questions'])
        questions = Question.query.order_by(Question.id).all()

        self.assertTrue(data['success'])
        self.assertEqual(len(questions), data['total_questions'])
        self.assertEqual(res.status_code, 200)

    def test_404_get_questions_beyond_valid_page(self):
        '''Test getting question beyond a valid page'''
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):
        '''Test deleting a question'''
        #first get a question to delete
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        if data:
            questions1 = data['questions']
            if len(questions1):
                question1 = questions1[0]
                #delete question from db
                res = self.client().delete('questions/'+ str(question1['id']))
                #find out if question indeed got deleted
                data = json.loads(res.data)
                questions2 = data['questions']

                [self.assertTrue(question2['id'] != question1['id']) for question2 in questions2]
                self.assertTrue(data['success'])

                #add the question we deleted back so as not to cause other tests to fail
                res = self.client().post(
                    '/questions',
                    headers={'Content-Type': 'application/json'}, 
                    json =  {
                        'question':question1['question'],
                        'answer': question1['answer'],
                        'category': int(question1['category']),
                        'difficulty':int(question1['difficulty'])
                    })
                data = json.loads(res.data)
                self.assertTrue(data['success'])

        data = json.loads(res.data)
        self.assertTrue(data['success'])
    
    def test_404_delete_question(self):
        '''Test deleting a non-existent question'''
        res = self.client().delete('questions/'+ str(7823832))
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(res.status_code, 404)

    def test_add_question(self):
        '''Test adding a new question'''
        res = self.client().post(
            '/questions',
            headers={'Content-Type': 'application/json'}, 
            json =  {
                'question':'What country did the coronavirus originate from?',
                'answer': 'China',
                'category': 1,
                'difficulty':1
            })

        data = json.loads(res.data)
        self.assertTrue(data['success'])

        question_added = data['created']
        questions = Question.query.order_by(Question.id).all()

        found_added_question = False
        for question in questions:
            if question.id == question_added:
                found_added_question = True
        self.assertTrue(found_added_question)

    def test_400_add_question(self):
        '''Test adding a new question'''
        res = self.client().post(
            '/questions',
            headers={'Content-Type': 'application/json'},
            json = {
                'bangled_question': 'bogus question'
            })

        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)

    def test_search_questions_based_on_search_term(self):
        '''Test questions database for occurrence of the search term'''
        res = self.client().post(
            '/searchForQuestions',
            headers={'Content-Type': 'application/json'},
            json = {
                'searchTerm': 'title'
            })
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)

    def test_422_search_questions_based_on_search_term(self):
        '''Test questions database for occurrence of the search term'''
        res = self.client().post(
            '/searchForQuestions',
            headers={'Content-Type': 'application/json'},
            json = {
                'bangled_searchTerm': 'title'
            })
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)

    def test_get_questions_based_on_category(self):
        '''Test getting questions based on a category'''
        categories = Category.query.all()
        if categories:
            category = categories[0]
            if category:
                res = self.client().get('/categories/' + str(category.id)+'/questions')
                data = json.loads(res.data)
                self.assertTrue(data['success'])
                [self.assertTrue(question['category'] == category.id) for question in data['questions']]
                
    def test_404_get_questions_based_on_category(self):
        '''Test getting questions based on a category but the category is non-existent in the database'''
        categories = Category.query.all()
        if categories:
            category = categories[0]
            if category:
                res = self.client().get('/categories/' + str(9000)+'/questions')
                data = json.loads(res.data)
                self.assertFalse(data['success'])
                self.assertEqual(data['message'], "resource not found")
                self.assertEqual(res.status_code, 404)                
    
    def test_quizzes(self):
        '''Test playing the quiz'''
        res = self.client().post(
            '/quizzes',
            headers={'Content-Type': 'application/json'},
            json = {
                'quiz_category': {'id':0},
                'previous_questions':[11,12,13]
            })
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertIsNotNone(data['question'])
        self.assertEqual(res.status_code, 200)

    def test_400_quizzes(self):
        '''Test getting an error when playing the quiz when category is not submitted with the request'''
        res = self.client().post(
            '/quizzes',
            headers={'Content-Type': 'application/json'},
            json = {
                'previous_questions':[11,12,13]
            })
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)

    def test_404_quizzes(self):
        '''Test getting an error when playing the quiz when quiz category is non-existent'''
        res = self.client().post(
            '/quizzes',
            headers={'Content-Type': 'application/json'},
            json = {
                'quiz_category': {'id':9000},
                'previous_questions':[11,12,13]
            })
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()