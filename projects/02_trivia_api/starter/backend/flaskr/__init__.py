import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*":{"origins":"*"}})

  '''
  @Done: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
      return response

  '''
  @Done: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = list(map(Category.format, Category.query.order_by(Category.id).all()))

    if len(categories) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'categories': categories,
        'total_categories': len(Category.query.all())
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 


  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      categories = list(map(Category.format, Category.query.order_by(Category.id).all()))

      if len(current_questions) == 0:
        abort(404)
    
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'categories': categories,
        'current_category': None
      })
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(422)
    finally:
      db.session.close()

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'deleted': question_id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(422)
    finally:
      db.session.close()

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      body = request.get_json()
      new_question = body.get('question', None),
      new_answer = body.get('answer', None),
      new_category = body.get('category', None),
      new_difficulty = body.get('difficulty', None)

      question = Question(
        question = new_question,
        answer = new_answer,
        category = new_category,
        difficulty = new_difficulty
        )
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
      })
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(422)
    finally:
      db.session.close()

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/searchquestions', methods=['POST'])
  def searchquestions():
    body = request.get_json()
    search_term = body.get('search', None)
    try:
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
      questions = paginate_questions(request, selection)
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(404)
    finally:
      db.session.close()
    
    return jsonify({
        'success': True,
        'search': search_term,
        'questions': questions,
        'total_questions_found': len(questions)
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/searchquestions/<string:category_id>', methods=['GET'])
  def getquestions(category_id):
    try:
      selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
      questions = paginate_questions(request, selection)
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(404)
    finally:
      db.session.close()
    
    return jsonify({
        'success': True,
        'questions': questions,
        'total_questions_found': len(questions)
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/playquestions',methods=['POST'])
  def playquestions():
    body = request.get_json()
    category = body.get('category', None)
    previous_questions = body.get('previous_questions', None).strip('][').split(",")
    questions = []
    try:
      selections = Question.query.order_by(Question.id).filter(Question.category == category).all()
  
      for previous_question in previous_questions:
        i = 0
        while selections and i < len(selections):
          if selections[i].id == int(previous_question):
            selections.pop(i)
            break
          i+=1
      if selections:
        questions = [question.format() for question in selections]
      
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(404)
    finally:
      db.session.close()
    
    return jsonify({
        'success': True,
        'questions': questions,
        'total_questions_found': len(questions)
    })

  '''
  @Done: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
    }), 422

  
  return app

    