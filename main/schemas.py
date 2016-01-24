from marshmallow import Schema, fields


class ServiceSchema(Schema):
    id = fields.Integer()
    title = fields.Str()
    category_id = fields.Integer()


class ServiceCategorySchema(Schema):
    id = fields.Integer()
    title = fields.Str()
