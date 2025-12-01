from flask.views import MethodView
from flask_smorest import Blueprint, abort
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from src.app.services.auth_service import AuthService
from src.api.schemas.auth_schemas import UserRegisterSchema, UserLoginSchema, TokenSchema, ChangePasswordSchema

auth_bp = Blueprint('auth', __name__, description='Authentication operations')

auth_service = None

def get_auth_service():
    global auth_service
    if not auth_service:
        auth_service = AuthService()
    return auth_service

@auth_bp.route('/register')
class Register(MethodView):
    @auth_bp.arguments(UserRegisterSchema)
    @auth_bp.response(HTTPStatus.CREATED, description="User registered successfully")
    def post(self, user_data):
        """Register a new user"""
        try:
            get_auth_service().register_user(user_data)
            return {"message": "User registered successfully"}, HTTPStatus.CREATED
        except ValueError as e:
            abort(HTTPStatus.CONFLICT, message=str(e))
        except Exception as e:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred during registration")

@auth_bp.route('/login')
class Login(MethodView):
    @auth_bp.arguments(UserLoginSchema)
    @auth_bp.response(HTTPStatus.OK, TokenSchema)
    def post(self, user_data):
        """Login and get access token"""
        user = get_auth_service().authenticate_user(user_data['username'], user_data['password'])
        if not user:
            abort(HTTPStatus.UNAUTHORIZED, message="Invalid username or password")
        
        access_token = get_auth_service().create_token(user.id)
        return {"access_token": access_token}

@auth_bp.route('/change-password')
class ChangePassword(MethodView):
    @jwt_required()
    @auth_bp.arguments(ChangePasswordSchema)
    @auth_bp.response(HTTPStatus.OK, description="Password changed successfully")
    def post(self, password_data):
        """Change user password"""
        from src.app.utils.auth_utils import get_current_user_id
        user_id = get_current_user_id()
        
        try:
            get_auth_service().change_password(
                user_id=user_id,
                old_password=password_data['old_password'],
                new_password=password_data['new_password']
            )
            return {"message": "Password changed successfully"}
        except ValueError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
        except Exception as e:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred while changing password")