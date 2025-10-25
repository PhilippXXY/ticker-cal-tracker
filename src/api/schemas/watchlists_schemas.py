'''
Watchlist schemas for request/response validation and documentation.
'''

from marshmallow import Schema, fields
from marshmallow.validate import Length


class WatchlistSchema(Schema):
    '''
    Schema for watchlist representation.
    '''
    id = fields.Int(required=True, metadata={"description": "The watchlist identifier"})
    name = fields.Str(required=True, validate=Length(min=1, max=100), metadata={"description": "The watchlist name"})
    description = fields.Str(validate=Length(max=500), metadata={"description": "The watchlist description"}, allow_none=True)
    created_at = fields.DateTime(dump_only=True, metadata={"description": "Creation timestamp"})
    updated_at = fields.DateTime(dump_only=True, metadata={"description": "Last update timestamp"})


class WatchlistCreateSchema(Schema):
    '''
    Schema for creating a new watchlist.
    '''
    name = fields.Str(required=True, validate=Length(min=1, max=100), metadata={"description": "The watchlist name"})
    description = fields.Str(validate=Length(max=500), metadata={"description": "The watchlist description"}, allow_none=True)


class WatchlistUpdateSchema(Schema):
    '''
    Schema for updating a watchlist.
    '''
    name = fields.Str(validate=Length(min=1, max=100), metadata={"description": "The watchlist name"})
    description = fields.Str(validate=Length(max=500), metadata={"description": "The watchlist description"}, allow_none=True)