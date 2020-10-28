import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# from backend.models import setup_db, Question, Category
QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @DONE: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @Done: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    '''
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route("/api/categories", methods=['GET'])
    def get_available_categories():
        categories = Category.query.all()
        data = Category.get_dict(categories)
        return jsonify({'categories': data})

    '''
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen
    for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        page = int(request.args.get('page', 1))
        category = str(request.args.get('category', 1))
        offset = (page - 1) * 10
        questions = [question.format() for question in
                     Question.query.filter_by(category=category)
                     .offset(offset).limit(QUESTIONS_PER_PAGE)]
        data = {
            'questions': questions,
            'totalQuestions': len(questions),
            'currentCategory': category
        }
        categories = Category.query.all()
        categories_dict = Category.get_dict(categories)
        data.update({'categories': categories_dict})
        return jsonify(data), 200

    '''
    @Done:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/api/questions/<id>', methods=['DELETE'])
    def delete_question(id: int):
        question = Question.query.filter_by(id=id).first()
        if question is not None:
            question.delete()
            return jsonify({'success': True}), 200
        return jsonify({'success': False}), 400

    '''
    @Done:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''

    @app.route("/api/question", methods=['POST'])
    def add_new_question():
        req_data = request.get_json()
        question = Question(**req_data)
        question.insert()
        return jsonify({'success': True}), 200

    '''
    @Done:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    @app.route("/api/questions", methods=['POST'])
    def search_question():
        req_data = request.get_json()
        search_term = req_data.get('searchTerm', '')
        questions = [question.format() for question in
                     Question.query.filter(Question.question
                     .ilike(f'%{search_term}%'))
                     .limit(QUESTIONS_PER_PAGE)]
        data = {
            'questions': questions,
            'totalQuestions': len(questions),
            'currentCategory': None
        }
        return jsonify(data), 200

    '''
    @Done:
    Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/api/categories/<id>/questions', methods=['GET'])
    def get_category_questions(id: int):
        questions = [question.format() for question in Question.query
                     .filter_by(category=id).limit(QUESTIONS_PER_PAGE)]
        data = {
            'questions': questions,
            'totalQuestions': len(questions),
            'currentCategory': id
        }
        return jsonify(data), 200

    '''
    @Done:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/api/quizzes', methods=['POST'])
    def play_quiz():
        from sqlalchemy.sql import func
        req_data = request.get_json()
        previous_questions = req_data.get('previous_questions', [])
        quiz_category = req_data.get('quiz_category', {'id': 0})
        predicate = (~Question.id
                     .in_(list(map(lambda x: x, previous_questions))))
        if quiz_category['id'] != 0:
            predicate &= (Question.category == quiz_category['id'])
        question = Question.query\
            .order_by(func.random()).filter(predicate).first()
        if question is None:
            return jsonify(
                {'question': {},
                 'message': '''No more questions or cannot load
                            questions of the given category'''}), 400
        return jsonify({'question': question.format()}), 200

    '''
    @Done:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return jsonify({'success': False, 'msg': str(e)}), 404

    @app.errorhandler(422)
    def cannot_process(e):
        # note that we set the 404 status explicitly
        return jsonify({'success': False, 'msg': str(e)}), 422

    return app
