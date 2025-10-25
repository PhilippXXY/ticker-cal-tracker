import logging

from flask import Flask
from flask_smorest import Api

from src.api.routes.auth_rest import auth_bp
from src.api.routes.calendar_rest import calendar_bp
from src.api.routes.stocks_rest import stocks_bp
from src.api.routes.user_rest import user_bp
from src.api.routes.watchlists_rest import watchlists_bp

def create_app():
    """
    Create and configure the Flask application.
    Initializes a Flask app instance, registers the application's API blueprints, and configures basic logging.
    Returns:
        Flask: A configured Flask application instance ready to be run.
    """
    # Initialize Flask
    app = Flask(__name__)
    
    # Configuration for Flask-Smorest
    app.config.update({
        'API_TITLE': 'Ticker Calendar Tracker API',
        'API_VERSION': '0.0.0',
        'OPENAPI_VERSION': '3.0.3',
        'OPENAPI_URL_PREFIX': '/',
        'OPENAPI_SWAGGER_UI_PATH': '/docs',
        'OPENAPI_SWAGGER_UI_URL': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/',
    })

    # Initialize Flask-Smorest API
    api = Api(app)

    # Register the API blueprints
    api.register_blueprint(auth_bp, url_prefix='/api/auth')
    api.register_blueprint(watchlists_bp, url_prefix='/api/watchlists')
    api.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    api.register_blueprint(user_bp, url_prefix='/api/user')
    api.register_blueprint(calendar_bp, url_prefix='/api/cal')
    
    # Set up logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
    