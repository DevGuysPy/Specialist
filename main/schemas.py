from marshmallow import Schema, fields


class ServiceSchema(Schema):
    id = fields.Integer()
    title = fields.Str()
    category_id = fields.Integer()


class ServiceCategorySchema(Schema):
    id = fields.Integer()
    title = fields.Str()


class SpecialistDistanceSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    lat = fields.Function(lambda obj: obj.user.location.latitude)
    lng = fields.Function(lambda obj: obj.user.location.longitude)
