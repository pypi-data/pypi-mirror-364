from .SQL.query import BaseRepository

class Repository(BaseRepository):
    def __init__(self, tablename: str):
        super().__init__(tablename)

    @classmethod
    def attach_model(cls, model_cls):
        repo = cls(model_cls.__tablename__)
        for name in dir(repo):
            if not name.startswith("_") and callable(getattr(repo, name)):
                setattr(model_cls, name, staticmethod(getattr(repo, name)))
        return model_cls