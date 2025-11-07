from http import HTTPStatus
from flask import Response
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from src.app.services.calendar_service import CalendarService

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
