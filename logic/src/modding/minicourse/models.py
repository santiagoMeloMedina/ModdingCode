from modding.common import model


class Category(model.Model):
    id: str
    name: str


class Minicourse(model.Model):
    id: str
    category_id: str
    name: str
    thumb_ext: str
