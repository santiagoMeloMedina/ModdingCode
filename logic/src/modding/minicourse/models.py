from modding.common import model


class Category(model.Model):
    name: str


class Minicourse(model.Model):
    category_id: str
    name: str
    thumb_ext: str
