from flask import Flask
import logging
from config import SECRET_KEY

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY

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


if __name__ == '__main__':
    from login_api.routes import*
    from points_api.routes import*
    from admin_api.routes import*
    from user_api.routes import*
    
    app = create_app()
    app.run()  