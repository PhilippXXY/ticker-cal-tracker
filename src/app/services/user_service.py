from datetime import timedelta
from typing import Optional, Any, Dict
from uuid import UUID
from src.models.user_model import User
from src.database.adapter_factory import DatabaseAdapterFactory

class UserService:
    
    def __init__(self):
        self.db = DatabaseAdapterFactory.get_instance()
        
        
    def get_user(self, *, user_id: UUID) -> User:
        
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
            return User(
                email=user_data['email'],
                created_at=user_data['created_at'],
            )
        except Exception as e:
            # Log the error and re-raise or handle appropriately
            raise Exception(f"Error fetching user {user_id}: {str(e)}")
    
    def update_user(
        self,
        *,
        user_id: UUID,
        email: Optional[str] = None,
    ) -> bool:
        
        if not isinstance(user_id, UUID):
            raise TypeError("user_id must be a UUID instance")
        
        if email is None:
            return False
        
        try:
            updated = False
            
            if email is not None:
                params: Dict[str, Any] = {'user_id': user_id}                

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
            
            return updated
        except Exception as e:
            raise Exception(f"Error updating user {user_id}: {str(e)}")
