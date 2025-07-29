from .SQL.query import BaseRepository

class Repository(BaseRepository):
    def __init__(self, tablename: str):
        super().__init__(tablename)
