from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from src.database.adapter_factory import DatabaseAdapterFactory
from src.models.user_model import User
import logging

class AuthService:
    def __init__(self):
        self.db_adapter = DatabaseAdapterFactory.get_instance()
        self.logger = logging.getLogger(__name__)

    def register_user(self, user_data):
        """
        Register a new user.
        """
        username = user_data.get('username')
        email = user_data.get('email')
        password = user_data.get('password')

        # Check if user already exists
        if self.db_adapter.get_user_by_username(username):
            raise ValueError("Username already exists")
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Create user object 
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        # Save to database
        self.db_adapter.save_user(new_user)
        return new_user

    def authenticate_user(self, username, password):
        """
        Authenticate a user and return the user object if successful.
        """
        user = self.db_adapter.get_user_by_username(username)
        
        if not user or not check_password_hash(user.password_hash, password):
            return None
            
        return user

    def create_token(self, user_id):
        """
        Create a JWT access token for the user.
        """
        return create_access_token(identity=str(user_id))
