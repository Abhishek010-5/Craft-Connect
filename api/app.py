from flask import Flask
import logging
from flask_cors import CORS
from config import SECRET_KEY

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY
    
    CORS(app)

    # Configure logging
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('app_errors.log'), 
            logging.StreamHandler()  
        ]
    )

    # Register blueprints
    try:
        from blueprints import auth as auth_blueprint, admin as admin_blueprint, points as point_blueprint, user as user_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(admin_blueprint, url_prefix='/admin')
        app.register_blueprint(point_blueprint, url_prefix='/points')
        app.register_blueprint(user_blueprint, url_prefix='/user')
    except ImportError as e:
        app.logger.error(f'Failed to import blueprints: {str(e)}')
        raise

    return app



from login_api.routes import*
from points_api.routes import*
from admin_api.routes import*
from user_api.routes import*

app = create_app()
 
@app.route('/')
def home():
    return jsonify({"message":"API is working"})

def create_error_response(status_code, error, message):
    """Helper function to create a consistent error response."""
    response = {
        "status": status_code,
        "error": error,
        "message": message
    }
    return jsonify(response), status_code

@app.errorhandler(404)
def not_found(error):
    return create_error_response(404, "Not Found", "The requested resource was not found on the server.")

@app.errorhandler(500)
def internal_server_error(error):
    return create_error_response(500, "Internal Server Error", "Something went wrong on our end. Please try again later.")

@app.errorhandler(405)
def method_not_allowed_error(error):
    return create_error_response(405, "Method not allowed", "Invalid request. Please check the request type")