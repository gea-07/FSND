import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

from functools import wraps
from urllib.request import urlopen
from jose import jwt
import sys

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.route('/headers')
@requires_auth('get:drinks-detail')
def headers(payload):
    return 'Access Granted'


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@Done implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
        drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    abort_code = None
    drinks_list = []
    try:
        drinks = Drink.query.all()
        print("Database content")
        drinks_list = [drink.short() for drink in drinks]
    except Exception as e:
        db.session.rollback()
        print("Exception: {0}".format(e))
        print(sys.exc_info())
        abort_code = 422
    finally:
        db.session.close()

    if abort_code:
        abort(abort_code)
    else:
        return jsonify({
            "success": True,
            "drinks": drinks_list
        })


'''
@Done implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    abort_code = None
    drinks_list = []
    try:
        drinks = Drink.query.all()
        print("Database content")
        drinks_list = [drink.long() for drink in drinks]
    except Exception as e:
        db.session.rollback()
        print("Exception: {0}".format(e))
        print(sys.exc_info())
        abort_code = 422
    finally:
        db.session.close()

    if abort_code:
        abort(abort_code)
    else:
        return jsonify({
          "success": True,
          "drinks": drinks_list
        })


'''
@Done implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    abort_code = None
    drink_result = {}
    try:
        body = request.get_json()
        title_param = body.get('title', None)
        print("title: ", title_param)
        recipe_param = body.get('recipe', None)
        print("recipe:", json.dumps(recipe_param))
        drink = Drink(title=title_param, recipe=json.dumps(recipe_param))
        drink.insert()
        drink_result = drink.long()
    except Exception as e:
        db.session.rollback()
        print("Exception: {0}".format(e))
        print(sys.exc_info())
        abort_code = 422
    finally:
        db.session.close()

    if abort_code:
        abort(abort_code)
    else:
        return jsonify({
          "success": True,
          "drinks": drink_result
        })


'''
@Done implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    abort_code = None
    drink_result = []
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort_code = 404
        else:
            body = request.get_json()
            title_param = body.get('title', None)
            print("title: ", title_param)
            if title_param is not None:
                drink.title = title_param

            recipe_param = body.get('recipe', None)
            print("recipe: ", recipe_param)

            if recipe_param is not None:
                drink.recipe = json.dumps(recipe_param)

            drink.update()
            drink_result.append(drink.long())
    except Exception as e:
        db.session.rollback()
        print("Exception: {0}".format(e))
        print(sys.exc_info())
        abort_code = 422
    finally:
        db.session.close()

    if abort_code:
        abort(abort_code)
    else:
        return jsonify({
          "success": True,
          "drinks": drink_result
        })


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    abort_code = None
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort_code = 404
        else:
            drink.delete()
    except Exception as e:
        db.session.rollback()
        print("Exception: {0}".format(e))
        print(sys.exc_info())
        abort_code = 422
    finally:
        db.session.close()

    if abort_code:
        abort(abort_code)
    else:
        return jsonify({
            "success": True,
            "delete": id
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@Done implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "data not found"
                    }), 404


'''
@Done implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(e):
    print(e)
    return jsonify({
        "success": False,
        "error": e.error['code'],
        "message": e.error['description']
    }), e.status_code
