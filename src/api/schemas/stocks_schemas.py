'''
Stock schemas for request/response validation and documentation.
'''

from marshmallow import Schema, fields
from marshmallow.validate import Length

class StockSchema(Schema):
    '''
    Schema for a stock.
    '''
    isin = fields.Str(required=True, validate=Length(equal=12), metadata={"description": "International Securities Identification Number. Canonical unique identifier", "pattern": "^[A-Z]{2}[A-Z0-9]{10}$ (12 chars)", "unique": True, "example": "US0378331005"})
    ticker = fields.Str(required=True, validate=Length(min=1, max=10), metadata={"description": "Market ticker symbol", "example": "AAPL"})
    name = fields.Str(required=True, validate=Length(min=1, max=200), metadata={"description": "Company full name", "example": "Apple Inc."})