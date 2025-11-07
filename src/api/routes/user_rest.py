'''
User management endpoints.
'''

from http import HTTPStatus
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from src.app.utils import auth_utils
from src.app.services.user_service import UserService
from src.api.schemas.user_schemas import (
    UserSchema,
    UserUpdateSchema,
)

# Create Flask-Smorest Blueprint
user_bp = Blueprint('user', __name__, description='User management operations')

user_service = None


def get_user_service():
    '''
    Get or create the watchlist service singleton.

    Returns:
        UserService instance.
    '''
    global user_service
    if user_service is None:
        user_service = UserService()
    return user_service



@user_bp.route('/profile')
class UserProfile(MethodView):
    '''
    User profile endpoint.
    '''

    @user_bp.doc(
        summary='Get user profile',
        description='Retrieve the profile information for the authenticated user.',
    )
    @user_bp.response(status_code=HTTPStatus.OK, schema=UserSchema)
    @user_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='User not found')
    @user_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to retrieve user profile')
    def get(self):
        '''
        Get current user profile.

        Returns:
            User dict.
        '''
        user_id = auth_utils.get_current_user_id()

        try:
            user = get_user_service().get_user(user_id=user_id)
        except ValueError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f'Failed to retrieve user profile: {str(exc)}')

        return user

    @user_bp.doc(
        summary='Update user profile',
        description='Update the email address for the authenticated user.',
    )
    @user_bp.arguments(schema=UserUpdateSchema)
    @user_bp.response(status_code=HTTPStatus.OK, schema=UserSchema)
    @user_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid user update payload')
    @user_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='User not found')
    @user_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to update user profile')
    def put(self, update_data):
        '''
        Update user profile.

        Returns:
            Updated user dict.
        '''
        user_id = auth_utils.get_current_user_id()

        email = update_data.get('email')
        if email is not None:
            email = email.strip()
            if not email:
                abort(HTTPStatus.BAD_REQUEST, message='Email must not be empty when provided.')

        if not email:
            abort(HTTPStatus.BAD_REQUEST, message='Provide at least one field to update.')

        updated = False

        try:
            updated = get_user_service().update_user(
                user_id=user_id,
                email=email,
            )
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

        if not updated:
            abort(HTTPStatus.NOT_FOUND, message='User not found.')

        try:
            return get_user_service().get_user(user_id=user_id)
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))