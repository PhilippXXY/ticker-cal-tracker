from http import HTTPStatus
from flask import Response, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from src.app.services.calendar_service import CalendarService
from src.api.schemas.calendar_schemas import CalendarTokenResponseSchema
import src.app.utils.auth_utils as auth_utils

calendar_bp = Blueprint('calendar', __name__, description='Calendar subscription operations')

calendar_service = None

def get_calendar_service():
    '''
    Get or create the calendar service singleton.

    Returns:
        CalendarService instance.
    '''
    global calendar_service
    if calendar_service is None:
        calendar_service = CalendarService()
    return calendar_service

@calendar_bp.route('/<string:token>.ics')
class CalendarSubscription(MethodView):
    '''
    Calendar subscription endpoint.
    
    This endpoint serves iCalendar (.ics) files that users can subscribe to
    in their personal calendar applications (Google Calendar, Apple Calendar, Outlook, etc.).
    '''
    
    @calendar_bp.doc(
        summary='Get calendar subscription',
        description='Fetch the iCalendar (.ics) file for a watchlist calendar subscription.',
    )
    @calendar_bp.response(status_code=HTTPStatus.OK, description='iCalendar file')
    @calendar_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid calendar token')
    @calendar_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Calendar not found')
    @calendar_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to generate calendar')
    def get(self, token):
        '''
        Get the iCalendar file for a watchlist.
        
        Args:
            token: The unique calendar token (from the URL path)
            
        Returns:
            Response: iCalendar (.ics) file with proper MIME type
        '''
        # Validate token
        if not token or not token.strip():
            abort(HTTPStatus.BAD_REQUEST, message='Calendar token must not be empty.')
        
        normalized_token = token.strip()
        
        try:
            # Get the iCalendar content from the service using just the token
            # The service will look up the watchlist by token, not full URL
            ics_content = get_calendar_service().get_calendar(token=normalized_token)
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except LookupError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f'Failed to generate calendar: {str(exc)}')
        
        # Check if calendar was found (empty result)
        if not ics_content or ics_content.strip() == '':
            abort(HTTPStatus.NOT_FOUND, message='Calendar not found for the provided token.')
        
        # Return the iCalendar file with proper headers
        return Response(
            ics_content,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': f'attachment; filename="{normalized_token}.ics"',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )

@calendar_bp.route('/<uuid:watchlist_id>')
class CalendarWatchlist(MethodView):
    '''
    Calendar token management for a specific watchlist.
    '''
    
    @calendar_bp.doc(
        summary='Rotate calendar token',
        description='Generate a new calendar subscription token for the watchlist, invalidating the old one.',
    )
    @calendar_bp.response(status_code=HTTPStatus.OK, schema=CalendarTokenResponseSchema)
    @calendar_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid request')
    @calendar_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist not found')
    @calendar_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to rotate token')
    def post(self, watchlist_id):
        '''
        Generate a new calendar token for a watchlist.
        
        Args:
            watchlist_id: UUID of the watchlist
            
        Returns:
            Dict with the new calendar URL and token
        '''
        user_id = auth_utils.get_current_user_id()
        
        try:
            new_token = get_calendar_service().rotate_calendar_token(
                user_id=user_id,
                watchlist_id=watchlist_id
            )
            
            # Construct the calendar URL
            # Get the base URL from the request
            base_url = request.host_url.rstrip('/')
            calendar_url = f"{base_url}/api/cal/{new_token}.ics"
            
            return {
                'calendar_url': calendar_url,
                'token': new_token
            }
            
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except LookupError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f'Failed to rotate calendar token: {str(exc)}')
    
    @calendar_bp.doc(
        summary='Get calendar URL',
        description='Retrieve the calendar subscription URL for the watchlist.',
    )
    @calendar_bp.response(status_code=HTTPStatus.OK, schema=CalendarTokenResponseSchema)
    @calendar_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid request')
    @calendar_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist not found')
    @calendar_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to get calendar URL')
    def get(self, watchlist_id):
        '''
        Get the calendar subscription URL for a watchlist.
        
        Args:
            watchlist_id: UUID of the watchlist
            
        Returns:
            Dict with the calendar URL and token
        '''
        user_id = auth_utils.get_current_user_id()
        
        try:
            token = get_calendar_service().get_calendar_token(
                user_id=user_id,
                watchlist_id=watchlist_id
            )
            
            # Construct the calendar URL
            # Get the base URL from the request
            base_url = request.host_url.rstrip('/')
            calendar_url = f"{base_url}/api/cal/{token}.ics"
            
            return {
                'calendar_url': calendar_url,
                'token': token
            }
            
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except LookupError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f'Failed to get calendar URL: {str(exc)}')

        
