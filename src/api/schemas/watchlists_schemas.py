'''
Watchlist schemas for request/response validation and documentation.
'''

from datetime import datetime
from marshmallow import Schema, fields
from marshmallow.validate import Length


class WatchlistSchema(Schema):
    '''
    Schema for watchlist representation.
    '''
    id = fields.Int(required=True, metadata={"description": "The watchlist identifier", "example": 1})
    name = fields.Str(required=True, validate=Length(min=1, max=100), metadata={"description": "The watchlist name", "example": "Tech Stocks"})
    description = fields.Str(validate=Length(max=500), metadata={"description": "The watchlist description", "example": "My favorite technology stocks"}, allow_none=True)
    created_at = fields.DateTime(dump_only=True, metadata={"description": "Creation timestamp", "example": datetime(2025, 10, 27, 10, 30, 0)})
    updated_at = fields.DateTime(dump_only=True, metadata={"description": "Last update timestamp", "example": datetime(2025, 10, 27, 14, 20, 0)})


class WatchlistCreateSchema(Schema):
    '''
    Schema for creating a new watchlist.
    '''
    name = fields.Str(required=True, validate=Length(min=1, max=100), metadata={"description": "The watchlist name", "example": "Growth Stocks"})
    description = fields.Str(validate=Length(max=500), metadata={"description": "The watchlist description", "example": "High growth potential stocks"}, allow_none=True)


class WatchlistUpdateSchema(Schema):
    '''
    Schema for updating a watchlist.
    '''
    name = fields.Str(validate=Length(min=1, max=100), metadata={"description": "The watchlist name", "example": "Updated Tech Stocks"})
    description = fields.Str(validate=Length(max=500), metadata={"description": "The watchlist description", "example": "Updated list of technology stocks"}, allow_none=True)