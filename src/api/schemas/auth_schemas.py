from marshmallow import Schema, fields

class UserRegisterSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    email = fields.Email(required=False, allow_none=True)

class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

class TokenSchema(Schema):
    access_token = fields.String(dump_only=True)
