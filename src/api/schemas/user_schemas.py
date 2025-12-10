from marshmallow import Schema, fields
from marshmallow.validate import Email

class UserSchema(Schema):
    '''
    Schema for user representation.
    '''
    email = fields.Email(
        required=True,
        metadata={'description': 'User email address.', 'example': 'user@example.com'},
    )
    created_at = fields.DateTime(
        dump_only=True,
        metadata={'description': 'Timestamp when the user account was created.', 'example': '2025-10-27T10:30:00Z'},
    )

class UserUpdateSchema(Schema):
    '''
    Schema for updating user information.
    '''
    email = fields.Email(
        validate=Email(),
        metadata={'description': 'Updated email address.', 'example': 'newemail@example.com'},
    )