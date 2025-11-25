'''
Watchlist management endpoints exposed via Flask-Smorest.
'''

from http import HTTPStatus
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from src.models.stock_event_model import EventType
import src.app.utils.auth_utils as auth_utils
from src.app.services.watchlists_service import WatchlistService
from src.api.schemas.stocks_schemas import StockSchema
from src.api.schemas.watchlists_schemas import (
    StockFollowResponseSchema,
    WatchlistCreateSchema,
    WatchlistSchema,
    WatchlistUpdateSchema,
)

watchlists_bp = Blueprint('watchlists', __name__, description='Watchlist management operations')

watchlist_service = None


def get_watchlist_service():
    '''
    Get or create the watchlist service singleton.

    Returns:
        WatchlistService instance.
    '''
    global watchlist_service
    if watchlist_service is None:
        watchlist_service = WatchlistService()
    return watchlist_service


def _extract_watchlist_settings(payload, *, include_defaults=True):
    '''
    Extract event settings from request payload.

    Args:
        payload: Request data dict.
        include_defaults: Whether to default missing fields to True.

    Returns:
        Dict mapping EventType to bool.
    '''
    settings = {}
    for event_type in EventType:
        column_name = event_type.db_column
        if column_name in payload:
            settings[event_type] = bool(payload[column_name])
        elif include_defaults:
            settings[event_type] = True
    return settings


@watchlists_bp.route('/')
class WatchlistCollection(MethodView):
    '''
    Collection-level operations for watchlists.
    '''

    @jwt_required()
    @watchlists_bp.doc(
        summary='List watchlists',
        description='Retrieve all watchlists that belong to the authenticated user.',
    )
    @watchlists_bp.response(status_code=HTTPStatus.OK, schema=WatchlistSchema(many=True))
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to list watchlists')
    def get(self):
        '''
        List all watchlists for the authenticated user.

        Returns:
            List of watchlist dicts.
        '''
        user_id = auth_utils.get_current_user_id()
        try:
            return get_watchlist_service().get_all_watchlists_for_user(user_id=user_id)
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f'Failed to list watchlists: {str(exc)}')

    @jwt_required()
    @watchlists_bp.doc(
        summary='Create watchlist',
        description='Create a new watchlist with optional event filters.',
    )
    @watchlists_bp.arguments(schema=WatchlistCreateSchema)
    @watchlists_bp.response(status_code=HTTPStatus.CREATED, schema=WatchlistSchema)
    @watchlists_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid watchlist payload')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to create watchlist')
    def post(self, new_data):
        '''
        Create a new watchlist for the authenticated user.

        Returns:
            Created watchlist dict and 201 status.
        '''
        user_id = auth_utils.get_current_user_id()

        name = new_data['name'].strip()
        if not name:
            abort(HTTPStatus.BAD_REQUEST, message='Watchlist name must not be empty.')

        watchlist_settings = _extract_watchlist_settings(new_data)

        try:
            return get_watchlist_service().create_watchlist(
                user_id=user_id,
                name=name,
                watchlist_settings=watchlist_settings,
            ), HTTPStatus.CREATED
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))


@watchlists_bp.route('/<uuid:watchlist_id>')
class WatchlistDetailResource(MethodView):
    '''
    Item-level operations on a specific watchlist.
    '''

    @jwt_required()
    @watchlists_bp.doc(
        summary='Retrieve watchlist',
        description='Fetch a single watchlist identified by its UUID.',
    )
    @watchlists_bp.response(status_code=HTTPStatus.OK, schema=WatchlistSchema)
    @watchlists_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist not found')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to retrieve watchlist')
    def get(self, watchlist_id):
        '''
        Get a watchlist by ID.

        Returns:
            Watchlist dict.
        '''
        user_id = auth_utils.get_current_user_id()
        try:
            watchlist = get_watchlist_service().get_watchlist_by_id(user_id=user_id, watchlist_id=watchlist_id)
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

        if not watchlist:
            abort(HTTPStatus.NOT_FOUND, message='Watchlist not found.')

        return watchlist

    @jwt_required()
    @watchlists_bp.doc(
        summary='Update watchlist',
        description='Update the name or event filters of a specific watchlist.',
    )
    @watchlists_bp.arguments(schema=WatchlistUpdateSchema)
    @watchlists_bp.response(status_code=HTTPStatus.OK, schema=WatchlistSchema)
    @watchlists_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist not found')
    @watchlists_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid watchlist update payload')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to update watchlist')
    def put(self, update_data, watchlist_id):
        '''
        Update watchlist name and/or settings.

        Returns:
            Updated watchlist dict.
        '''
        user_id = auth_utils.get_current_user_id()

        name = update_data.get('name')
        if name is not None:
            name = name.strip()
            if not name:
                abort(HTTPStatus.BAD_REQUEST, message='Watchlist name must not be empty when provided.')

        watchlist_settings = _extract_watchlist_settings(update_data, include_defaults=False)

        if name is None and not watchlist_settings:
            abort(HTTPStatus.BAD_REQUEST, message='Provide at least one field to update.')

        updated = False

        try:
            updated = get_watchlist_service().update_watchlist(
                user_id=user_id,
                watchlist_id=watchlist_id,
                name=name,
                watchlist_settings=watchlist_settings or None,
            )
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

        if not updated:
            abort(HTTPStatus.NOT_FOUND, message='Watchlist not found.')

        try:
            return get_watchlist_service().get_watchlist_by_id(user_id=user_id, watchlist_id=watchlist_id)
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

    @jwt_required()
    @watchlists_bp.doc(
        summary='Delete watchlist',
        description='Delete the watchlist identified by its UUID.',
    )
    @watchlists_bp.response(status_code=HTTPStatus.NO_CONTENT)
    @watchlists_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist not found')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to delete watchlist')
    def delete(self, watchlist_id):
        '''
        Delete a watchlist.

        Returns:
            None with 204 status.
        '''
        user_id = auth_utils.get_current_user_id()
        try:
            deleted = get_watchlist_service().delete_watchlist(user_id=user_id, watchlist_id=watchlist_id)
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

        if not deleted:
            abort(HTTPStatus.NOT_FOUND, message='Watchlist not found.')

        return None, HTTPStatus.NO_CONTENT


@watchlists_bp.route('/<uuid:watchlist_id>/stocks')
class WatchlistStocksCollection(MethodView):
    '''
    Collection operations for stocks tracked in a watchlist.
    '''

    @jwt_required()
    @watchlists_bp.doc(
        summary='List watchlist stocks',
        description='Return all stocks currently tracked in the specified watchlist.',
    )
    @watchlists_bp.response(status_code=HTTPStatus.OK, schema=StockSchema(many=True))
    @watchlists_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist not found')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to fetch stocks')
    def get(self, watchlist_id):
        '''
        Get all stocks in a watchlist.

        Returns:
            List of stock dicts.
        '''
        user_id = auth_utils.get_current_user_id()
        try:
            return get_watchlist_service().get_watchlist_stocks(user_id=user_id, watchlist_id=watchlist_id)
        except ValueError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f'Failed to fetch stocks: {str(exc)}')


@watchlists_bp.route('/<uuid:watchlist_id>/stocks/<string:stock_ticker>')
class WatchlistStockResource(MethodView):
    '''
    Item operations on a specific stock relationship in a watchlist.
    '''

    @jwt_required()
    @watchlists_bp.doc(
        summary='Follow stock',
        description='Add a stock ticker to the given watchlist.',
    )
    @watchlists_bp.response(status_code=HTTPStatus.OK, schema=StockFollowResponseSchema)
    @watchlists_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist or stock not found')
    @watchlists_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid stock follow payload')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to follow stock')
    def post(self, watchlist_id, stock_ticker):
        '''
        Add a stock to a watchlist.

        Returns:
            Success message dict.
        '''
        user_id = auth_utils.get_current_user_id()

        if not stock_ticker or not stock_ticker.strip():
            abort(HTTPStatus.BAD_REQUEST, message='Stock ticker must not be empty.')
        normalized_ticker = stock_ticker.strip().upper()

        try:
            get_watchlist_service().add_stock_to_watchlist(
                user_id=user_id,
                watchlist_id=watchlist_id,
                stock_ticker=normalized_ticker,
            )
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except LookupError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

        return {
            'message': 'Stock added to watchlist successfully',
            'watchlist_id': watchlist_id,
            'stock_ticker': normalized_ticker,
        }

    @jwt_required()
    @watchlists_bp.doc(
        summary='Unfollow stock',
        description='Remove a stock ticker from the given watchlist.',
    )
    @watchlists_bp.response(status_code=HTTPStatus.OK, schema=StockFollowResponseSchema)
    @watchlists_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Watchlist or stock not found')
    @watchlists_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid stock unfollow payload')
    @watchlists_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to unfollow stock')
    def delete(self, watchlist_id, stock_ticker):
        '''
        Remove a stock from a watchlist.

        Returns:
            Success message dict.
        '''
        user_id = auth_utils.get_current_user_id()

        if not stock_ticker or not stock_ticker.strip():
            abort(HTTPStatus.BAD_REQUEST, message='Stock ticker must not be empty.')
        normalized_ticker = stock_ticker.strip().upper()

        removed = False
        try:
            removed = get_watchlist_service().remove_stock_to_watchlist(
                user_id=user_id,
                watchlist_id=watchlist_id,
                stock_ticker=normalized_ticker,
            )
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except LookupError as exc:
            abort(HTTPStatus.NOT_FOUND, message=str(exc))
        except Exception as exc:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))

        if not removed:
            abort(HTTPStatus.NOT_FOUND, message='Stock not found in watchlist or watchlist not found.')

        return {
            'message': 'Stock removed from watchlist successfully',
            'watchlist_id': watchlist_id,
            'stock_ticker': normalized_ticker,
        }
