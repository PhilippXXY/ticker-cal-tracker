import logging
import sys
import atexit
import os
from dotenv import load_dotenv  

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from src.api.routes.auth_rest import auth_bp
from src.api.routes.calendar_rest import calendar_bp
from src.api.routes.stocks_rest import stocks_bp
from src.api.routes.user_rest import user_bp
from src.api.routes.watchlists_rest import watchlists_bp
from src.database.adapter_factory import DatabaseAdapterFactory, parse_environment_from_args
from src.app.background.scheduler import TaskScheduler

# Fix "No module named src" by adding the root folder to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 2. Force load the .env file
load_dotenv()

# Set dummy API keys for development if not present
if not os.getenv('API_KEY_ALPHA_VANTAGE'):
    os.environ['API_KEY_ALPHA_VANTAGE'] = 'dummy_alpha_vantage_key'
if not os.getenv('API_KEY_FINNHUB'):
    os.environ['API_KEY_FINNHUB'] = 'dummy_finnhub_key'


def create_app():
    """
    Create and configure the Flask application.
    Initializes a Flask app instance, registers the application's API blueprints, and configures basic logging.
    Returns:
        Flask: A configured Flask application instance ready to be run.
    """
    # Initialize database adapter based on environment
    db_environment = parse_environment_from_args()
    DatabaseAdapterFactory.initialize(db_environment)
    
    # Verify database connection
    try:
        db_adapter = DatabaseAdapterFactory.get_instance()
        if not db_adapter.health_check():
            logging.error("Database health check failed! Starting without DB.")
            db_adapter = None
        else:
            logging.info(f"Database connection established successfully in {db_environment.value} mode")
            logging.info(f"Database health check is successful: {db_adapter.health_check()}")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        db_adapter = None
        db_adapter = None
    
    # Initialize Flask
    app = Flask(__name__)
    
    # Configuration for Flask-Smorest
    app.config.update({
        'API_TITLE': 'Ticker Calendar Tracker API',
        'API_VERSION': '0.1.7',
        'OPENAPI_VERSION': '3.0.3',
        'OPENAPI_URL_PREFIX': '/',
        'OPENAPI_SWAGGER_UI_PATH': '/docs',
        'OPENAPI_SWAGGER_UI_URL': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/',
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-this'),  
        'API_SPEC_OPTIONS': {
            'security': [{"bearerAuth": []}],
            'components': {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                }
            },
        }
    })

    # Initialize Flask-Smorest API
    api = Api(app)
    
    # Initialize JWT
    JWTManager(app)

    # Register the API blueprints
    api.register_blueprint(auth_bp, url_prefix='/api/auth')
    api.register_blueprint(watchlists_bp, url_prefix='/api/watchlists')
    api.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    api.register_blueprint(user_bp, url_prefix='/api/user')
    api.register_blueprint(calendar_bp, url_prefix='/api/cal')
    
    # Set up logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize and start background task scheduler
    scheduler = TaskScheduler()
    scheduler.start()
    
    # Register cleanup handlers
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        '''
        Clean up database connections on app shutdown.
        
        Args:
            exception: Optional exception that caused the teardown.
        '''
        try:
            db_adapter = DatabaseAdapterFactory.get_instance()
            db_adapter.close()
            logging.info("Database connections closed")
        except Exception as e:
            logging.warning(f"Error during database cleanup: {e}")
    
    # Register cleanup for scheduler on app exit
    atexit.register(lambda: scheduler.shutdown())
        
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
    )
