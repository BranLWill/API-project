import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def set_access_control(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
        result = {}
        
        for category in categories:
            result[category.id] = category.type
            
        return jsonify({
            'success': True,
            'categories': result
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        # Get the page number from the request query parameters
        page = request.args.get('page', 1, type=int)
        # Set the number of questions per page
        questions_per_page = QUESTIONS_PER_PAGE

        # Calculate the start and end indices for pagination
        start = (page - 1) * questions_per_page
        end = start + questions_per_page

        # Get the questions from the database
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]

        # Paginate the questions
        paginated_questions = formatted_questions[start:end]

        # Get the total number of questions
        total_questions = len(formatted_questions)

        # Get the categories from the database
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        # Get the current category (optional)
        current_category = None

        # Create the response payload
        response = {
            'success': True,
            'questions': paginated_questions,
            'total_questions': total_questions,
            'categories': formatted_categories,
            'current_category': current_category
        }

        return jsonify(response)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # Get the question with the provided question_id
        question = Question.query.get(question_id)

        # Check if the question exists
        if question is None:
            abort(404)

        try:
            # Delete the question from the database
            question.delete()

            # Return a success message
            return jsonify({
                'success': True,
                'message': 'Question successfully deleted'
            })
        except:
            # In case of an error, rollback the session and return an error message
            db.session.rollback()
            abort(500)
        finally:
            # Close the session
            db.session.close()

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    app.route('/questions', methods=['POST'])
    def create_question():
        # Get the request body
        body = request.get_json()

        # Check if all required fields are present
        if 'question' not in body or 'answer' not in body or 'category' not in body or 'difficulty' not in body:
            abort(400)

        # Extract the question data from the request body
        question = body['question']
        answer = body['answer']
        category = body['category']
        difficulty = body['difficulty']

        try:
            # Create a new question object
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)

            # Insert the new question into the database
            new_question.insert()

            # Return a success message
            return jsonify({
                'success': True,
                'message': 'Question successfully created'
            })
        except:
            # In case of an error, rollback the session and return an error message
            db.session.rollback()
            abort(500)
        finally:
            # Close the session
            db.session.close()

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_questions():
        search_term = request.json.get('searchTerm', '')

        filtered_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        questions = []
        for question in filtered_questions:
            questions.append({
                'id': question.id,
                'question': question.question,
                'answer': question.answer,
                'category': question.category,
                'difficulty': question.difficulty
            })

        return jsonify({'questions': questions})



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        # Get the questions for the specified category from the database
        questions = Question.query.filter_by(category=category_id).all()

        # Check if there are no questions for the specified category
        if len(questions) == 0:
            abort(404)

        # Format the questions as a list of dictionaries
        formatted_questions = [question.format() for question in questions]

        # Return the formatted questions
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': category_id
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # Get the request body
        body = request.get_json()

        # Check if all required fields are present
        if 'quiz_category' not in body or 'previous_questions' not in body:
            abort(400)

        # Extract the category and previous questions from the request body
        category = body['quiz_category']
        previous_questions = body['previous_questions']

        try:
            # Get the questions for the specified category from the database
            if category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=category['id']).all()

            # Filter out the previous questions
            available_questions = [question for question in questions if question.id not in previous_questions]

            # Select a random question from the available questions
            if len(available_questions) > 0:
                random_question = random.choice(available_questions).format()
            else:
                random_question = None

            # Return the random question
            return jsonify({
                'success': True,
                'question': random_question
            })
        except:
            # In case of an error, return an error message
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    return app
