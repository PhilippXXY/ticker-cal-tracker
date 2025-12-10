'''
Stock schemas for request/response validation and documentation.
'''

from marshmallow import Schema, fields
from marshmallow.validate import Length

class StockSchema(Schema):
    '''
    Schema for a stock.
    '''
    ticker = fields.Str(required=True, validate=Length(min=1, max=10), metadata={"description": "Market ticker symbol", "example": "AAPL"})
    name = fields.Str(required=True, validate=Length(min=1, max=200), metadata={"description": "Company full name", "example": "Apple Inc."})
    current_price = fields.Float(dump_only=True, metadata={"description": "Current stock price", "example": 150.25})
    change_percent = fields.Float(dump_only=True, metadata={"description": "Daily percentage change", "example": 1.5})
