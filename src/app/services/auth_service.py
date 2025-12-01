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
        logging.info(f"Attempting to authenticate user: {username}")
        user = self.db_adapter.get_user_by_username(username)
        
        if not user:
            logging.warning(f"User not found: {username}")
            return None
            
        if not check_password_hash(user.password_hash, password):
            logging.warning(f"Password check failed for user: {username}")
            logging.warning(f"Stored hash: {user.password_hash[:20]}... (len={len(user.password_hash)})")
            return None
            
        logging.info(f"User authenticated successfully: {username}")
        return user

    def create_token(self, user_id):
        """
        Create a JWT access token for the user.
        """
        return create_access_token(identity=str(user_id))

    def change_password(self, user_id, old_password, new_password):
        """
        Change user password.
        """
        # Get user
        user = self.db_adapter.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Verify old password
        if not check_password_hash(user.password_hash, old_password):
            raise ValueError("Incorrect old password")

        # Hash new password
        new_password_hash = generate_password_hash(new_password)

        # Update password
        self.db_adapter.update_user_password(user_id, new_password_hash)
        return True
