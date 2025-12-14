from typing import Optional
from src.models.user_model import User
from src.database.adapter_factory import DatabaseAdapterFactory

from werkzeug.security import generate_password_hash

class UserService:
    '''
    Service for managing user information and preferences.
    
    Handles user data retrieval and updates.
    '''
    
    def __init__(self):
        '''
        Initialise the UserService with database connection.
        '''
        self.db = DatabaseAdapterFactory.get_instance()
        
        
    def get_user(self, *, user_id: int) -> User:
        '''
        Retrieve user information by user ID.
        
        Args:
            user_id: The integer ID of the user to retrieve.
            
        Returns:
            User object containing user details.
            
        Raises:
            ValueError: If user with the given ID is not found.
            Exception: If database query fails.
        '''
        query = """
            SELECT
                u.email,
                u.created_at
            FROM users u
            WHERE u.id = :user_id
        """
        
        try:
            results = self.db.execute_query(
                query=query,
                params={'user_id': user_id}
            )
            
            # Convert results to a list to check if empty
            results_list = list(results)
            
            if not results_list:
                raise ValueError(f"User with id {user_id} not found")
            
            user_data = results_list[0]
            
            # Create and return a User object from the query results
            # Note: We provide dummy values for username and password_hash as they are not returned by this query
            # but are required by the User model. In a real app, we might want to fetch them or make them optional.
            return User(
                id=user_id,
                email=user_data['email'],
                username=user_data['email'].split('@')[0], # Derived username
                password_hash='<hidden>', # Placeholder
                created_at=user_data['created_at'],
            )
        except Exception as e:
            # Log the error and re-raise or handle appropriately
            raise Exception(f"Error fetching user {user_id}: {str(e)}")
    
    def update_user(
        self,
        *,
        user_id: int,
        email: Optional[str] = None,
        password: Optional[str] = None,) -> bool:
        '''
        Update user information.
        
        Args:
            user_id: The integer ID of the user to update.
            email: Optional new email address for the user.
            password: Optional new password for the user.
            
        Returns:
            True if user was updated, False if no changes were made.
            
        Raises:
            TypeError: If user_id is not an integer.
            Exception: If database update fails.
        '''
        if not isinstance(user_id, int):
            raise TypeError("user_id must be an integer")
        
        if email is None and password is None:
            return False
        
        try:
            updated = False
            
            if email is not None:              
                update_query = """
                    UPDATE users
                    SET email = :email
                    WHERE id = :user_id
                """
                rows = self.db.execute_update(
                    query=update_query,
                    params={
                        'email': email,
                        'user_id': user_id
                    }
                )
                updated = updated or rows > 0
            
            if password is not None:
                password_hash = generate_password_hash(password)
                
                update_query = """
                    UPDATE users
                    SET password_hash = :password_hash
                    WHERE id = :user_id
                """
                rows = self.db.execute_update(
                    query=update_query,
                    params={
                        'password_hash': password_hash,
                        'user_id': user_id
                    }
                )
                updated = updated or rows > 0
            
            return updated
        except Exception as e:
            raise Exception(f"Error updating user {user_id}: {str(e)}")
