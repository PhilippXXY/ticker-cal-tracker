from flask_jwt_extended import get_jwt_identity


def get_current_user_id() -> int:
    '''
    Get the current authenticated user's ID from JWT token.
    
    Returns:
        int: The user ID of the currently authenticated user.
        
    Raises:
        RuntimeError: If called outside of a JWT-protected route.
    '''
    user_id = get_jwt_identity()
    if user_id is None:
        raise RuntimeError("No authenticated user found. This endpoint requires JWT authentication.")
    return int(user_id)