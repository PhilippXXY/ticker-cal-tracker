'''
Calendar schemas for request/response validation and documentation.
'''

from marshmallow import Schema, fields


class CalendarTokenResponseSchema(Schema):
    '''
    Schema for calendar token response.
    '''
    calendar_url = fields.Str(
        required=True,
        metadata={
            'description': 'Full URL to subscribe to the watchlist calendar.',
            'example': 'http://localhost:5001/api/cal/abc123xyz.ics'
        },
    )
    token = fields.Str(
        required=True,
        metadata={
            'description': 'The calendar subscription token.',
            'example': 'abc123xyz'
        },
    )
