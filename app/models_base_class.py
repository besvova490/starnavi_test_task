from app import db, models
from datetime import datetime


class BaseModelsClass:

    @classmethod
    def get_object(cls, obj_id, to_dict=True):
        if to_dict:
            return cls.query.get(obj_id).to_dict()
        return cls.query.get(obj_id)

    @classmethod
    def get_objects_list(cls, to_dict=True, **kwargs):
        if to_dict:
            return [obj.to_dict() for obj in cls.query.filter_by(**kwargs)]
        return cls.query.filter_by(kwargs)

    @classmethod
    def delete(cls, obj_id):
        obj = cls.get_object(obj_id, to_dict=False)
        db.session.delete(obj)
        db.session.commit()

    @classmethod
    def update(cls, obj_id, data):
        cls.query.filter_by(id=obj_id).update(data)
        db.session.commit()

    @classmethod
    def get_analytics(cls, obj_id, date_from, date_to):
        obj = cls.get_object(obj_id, to_dict=False)
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        likes = obj.likes.filter(models.Like.like_date > date_from, models.Like.like_date < date_to)
        return {'likes': [like.to_dict() for like in likes.all()], 'total_likes': likes.count(), 'date_from': date_from, 'date_to': date_to}