"""Stock management endpoints."""

from flask.views import MethodView
from flask_smorest import Blueprint

from src.api.schemas.stocks_schemas import (
    StockSchema
)

# Create Flask-Smorest Blueprint
stocks_bp = Blueprint('stocks', __name__, description='Stock management operations')


@stocks_bp.route('/')
class Stocks(MethodView):
    '''
    Stock collection endpoint.
    '''

    @stocks_bp.response(status_code=200, schema=StockSchema(many=True))
    def get(self):
        '''
        List all stocks.
        '''
        # TODO: Implement actual logic
        return [
            {
            "isin": "US0378331005",
            "ticker": "AAPL",
            "name": "Apple Inc."
            },
            {
            "isin": "US5949181045",
            "ticker": "MSFT",
            "name": "Microsoft Corporation"
            }
        ]