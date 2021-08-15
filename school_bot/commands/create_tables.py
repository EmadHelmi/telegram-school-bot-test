import os

from models import DB, Base

from . import Command


class CreateTablesCommand(Command):
    @staticmethod
    def run():
        for model in filter(lambda file: not file.split("/")[-1].startswith("__"), os.listdir("models")):
            __import__(f'models.{model.split("/")[-1].split(".")[0]}')
        db = DB()
        db.open_session()
        Base.metadata.create_all(db.engine, checkfirst=True)
