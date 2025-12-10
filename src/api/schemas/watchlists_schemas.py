'''
Watchlist schemas for request/response validation and documentation.
'''

from marshmallow import Schema, fields
from marshmallow.validate import Length


class WatchlistSchema(Schema):
    '''
    Schema for watchlist representation.
    '''
    id = fields.UUID(
        required=True,
        metadata={'description': 'Unique watchlist identifier.', 'example': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
    )
    name = fields.Str(
        required=True,
        validate=Length(min=1, max=100),
        metadata={'description': 'User-defined name of the watchlist.', 'example': 'Tech Stocks'},
    )
    created_at = fields.DateTime(
        dump_only=True,
        metadata={'description': 'Timestamp representing when the watchlist was created.', 'example': '2025-10-27T10:30:00Z'},
    )
    include_earnings_announcement = fields.Bool(
        dump_only=True,
        metadata={'description': 'Indicates if earnings announcements are tracked.', 'example': True},
    )
    include_dividend_ex = fields.Bool(
        dump_only=True,
        metadata={'description': 'Indicates if dividend ex-dates are tracked.', 'example': True},
    )
    include_dividend_declaration = fields.Bool(
        dump_only=True,
        metadata={'description': 'Indicates if dividend declarations are tracked.', 'example': True},
    )
    include_dividend_record = fields.Bool(
        dump_only=True,
        metadata={'description': 'Indicates if dividend record dates are tracked.', 'example': True},
    )
    include_dividend_payment = fields.Bool(
        dump_only=True,
        metadata={'description': 'Indicates if dividend payment dates are tracked.', 'example': True},
    )
    include_stock_split = fields.Bool(
        dump_only=True,
        metadata={'description': 'Indicates if stock splits are tracked.', 'example': True},
    )


class WatchlistCreateSchema(Schema):
    '''
    Schema for creating a new watchlist.
    '''
    name = fields.Str(
        required=True,
        validate=Length(min=1, max=100),
        metadata={'description': 'Name for the new watchlist.', 'example': 'Growth Stocks'},
    )
    include_earnings_announcement = fields.Bool(
        load_default=True,
        metadata={'description': 'Track earnings announcement events.', 'example': True},
    )
    include_dividend_ex = fields.Bool(
        load_default=True,
        metadata={'description': 'Track dividend ex-date events.', 'example': True},
    )
    include_dividend_declaration = fields.Bool(
        load_default=True,
        metadata={'description': 'Track dividend declaration events.', 'example': True},
    )
    include_dividend_record = fields.Bool(
        load_default=True,
        metadata={'description': 'Track dividend record date events.', 'example': True},
    )
    include_dividend_payment = fields.Bool(
        load_default=True,
        metadata={'description': 'Track dividend payment date events.', 'example': True},
    )
    include_stock_split = fields.Bool(
        load_default=True,
        metadata={'description': 'Track stock split events.', 'example': True},
    )


class WatchlistUpdateSchema(Schema):
    '''
    Schema for updating a watchlist.
    '''
    name = fields.Str(
        validate=Length(min=1, max=100),
        metadata={'description': 'Updated watchlist name.', 'example': 'Updated Tech Stocks'},
    )
    include_earnings_announcement = fields.Bool(
        metadata={'description': 'Toggle tracking of earnings announcements.', 'example': True},
    )
    include_dividend_ex = fields.Bool(
        metadata={'description': 'Toggle tracking of dividend ex-dates.', 'example': True},
    )
    include_dividend_declaration = fields.Bool(
        metadata={'description': 'Toggle tracking of dividend declarations.', 'example': True},
    )
    include_dividend_record = fields.Bool(
        metadata={'description': 'Toggle tracking of dividend record dates.', 'example': True},
    )
    include_dividend_payment = fields.Bool(
        metadata={'description': 'Toggle tracking of dividend payment dates.', 'example': True},
    )
    include_stock_split = fields.Bool(
        metadata={'description': 'Toggle tracking of stock split events.', 'example': True},
    )


class StockFollowResponseSchema(Schema):
    '''
    Schema for stock follow operation response.
    '''
    message = fields.Str(
        required=True,
        metadata={'description': 'Human readable outcome of the operation.', 'example': 'Stock added to watchlist successfully'},
    )
    watchlist_id = fields.UUID(
        required=True,
        metadata={'description': 'Identifier of the target watchlist.', 'example': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
    )
    stock_ticker = fields.Str(
        required=True,
        metadata={'description': 'Ticker symbol that was followed or unfollowed.', 'example': 'AAPL'},
    )
