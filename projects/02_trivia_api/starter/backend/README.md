# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/categories'
GET ...
POST ...
DELETE ...

GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}

```

GET '/questions?page=<page_argument>'
- Fetches a list of questions from the database
- Request Arguments: page_argument - page number, where each page represents the 10 questions for that page
-Returns: An object with the following example key-value pair definition, if successful:
{
    'success': True,
    'questions': <list of questions for that page>,
    'total_questions': <total questions in the database>,
    'categories': <list of categories from the database>,
    'current_category': None
}
Will return 404 if questions for given page is not found or 422 if request is unprocessable

DELETE 'questions/<question_id>
- Deletes a question from the database
- Request arguments: question_id - id of the question to delete
- Returns:  An object with the following example key-value pair definition, if successful:
{
    'success': True,
    'categories': None,
    'current_category': None,
    'questions': <list of all questions in database>,
    'total_questions': <total # question in database>
}
Will return 404 if question to be deleted is not found in the database, 400
if request argument is missing, or 422 if request is unprocessable

POST '/questions?question=<question string>&answer=<answer string>&category=<category num>&difficulty=<difficulty num>'
- Add/Inserts a new question to the database
- Request Arguments:
question - question string
answer - answer string
category - category number as int
question - question number as int
- Returns:  An object with the following example key-value pair definition, if successful:
{
    'success': True,
    'created': <new question.id that got inserted>,
    'questions': <list of all questions in db>,
    'total_questions': <total number of questions in the database>

}
Will return 422 if request is unprocessable

POST '/searchForQuestions?searchTerm=<search string>
- Searches for a term in all the questions in the database
- Request arguments: searchTerm - substring to search for in the question field of the questions database
- Returns:  An object with the following example key-value pair definition, if successful:
{         
    'success': True,
    'current_category': None,
    'questions': <list of questions that has the substring value in searchTerm>,
    'total_questions': len(questions)
}
Will return 404 if question to be deleted is not found in the database, 400
if request argument is missing, or 422 if request is unprocessable

GET '/categories/<category_id>'
- Fetches the questions for a certain category
- Request arguments: category_id - category of a question
- Returns: An object with the following example key-value pair definition, if successful:
{         
    'success': True,
    'questions': <list of questions for given category>,
    'total_questions': <len(questions) for given category>,
    'current_category': category_id
}
Will return 404 if question(s) cannot be found for the given category, or 422 if request is unprocessable

POST '/quizzes'
- Fetches a random question to play the quiz that has not been played before
- Request arguments: 
category - quiz category, if 0 it will fetch all questions from the database; otherwise, all questions from the database the matches the category id 
previous question - list of previously asked questions, maybe empty
- Returns: Return a random question within the given category. Specifically, the following key-value pair
{
    'success': True,
    'question': <random question, never played yet>
}
If unprocessable, returns 422; 400 if category parameter is missing; 404 is no questions can be found

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```