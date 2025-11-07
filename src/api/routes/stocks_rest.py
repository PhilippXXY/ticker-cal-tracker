"""Stock management endpoints."""

from http import HTTPStatus
from flask.views import MethodView
from flask_smorest import Blueprint, abort

import src.app.utils.auth_utils as auth_utils
from src.app.services.stocks_service import StocksService
from src.api.schemas.stocks_schemas import (
    StockSchema
)

# Create Flask-Smorest Blueprint
stocks_bp = Blueprint('stocks', __name__, description='Stock management operations')

stocks_service = None


def get_stocks_service():
    '''
    Get or create the stocks service singleton.

    Returns:
        StocksService instance.
    '''
    global stocks_service
    if stocks_service is None:
        stocks_service = StocksService()
    return stocks_service

@stocks_bp.route('/<string:ticker_symbol>')
class StockResource(MethodView):
    '''
    Item-level operations on a specific stock.
    '''

    @stocks_bp.doc(
        summary='Retrieve stock',
        description='Fetch stock information by ticker symbol.',
    )
    @stocks_bp.response(status_code=HTTPStatus.OK, schema=StockSchema)
    @stocks_bp.alt_response(status_code=HTTPStatus.UNAUTHORIZED, description='Authentication required')
    @stocks_bp.alt_response(status_code=HTTPStatus.BAD_REQUEST, description='Invalid ticker symbol')
    @stocks_bp.alt_response(status_code=HTTPStatus.NOT_FOUND, description='Stock not found')
    @stocks_bp.alt_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, description='Failed to retrieve stock')
    def get(self, ticker_symbol):
        '''
        Get stock information by ticker symbol.

        Returns:
            Stock dict with ticker, name, and last_updated timestamp.
        '''
        # Verify user is authenticated
        user_id = auth_utils.get_current_user_id()
        if not user_id:
            abort(HTTPStatus.UNAUTHORIZED, message='Authentication required.')
        
        # Validate ticker symbol
        if not ticker_symbol or not ticker_symbol.strip():
            abort(HTTPStatus.BAD_REQUEST, message='Stock ticker must not be empty.')
        
        try:
            stock = get_stocks_service().get_stock_from_ticker(ticker=ticker_symbol)
            # Convert Stock object to dict matching schema format
            return {
                'ticker': stock.symbol,
                'name': stock.name
            }
        except ValueError as exc:
            abort(HTTPStatus.BAD_REQUEST, message=str(exc))
        except Exception as exc:
            # Check if it's a "not found" type error
            if 'not found' in str(exc).lower() or 'Failed to fetch stock' in str(exc):
                abort(HTTPStatus.NOT_FOUND, message=f'Stock {ticker_symbol.upper()} not found.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(exc))