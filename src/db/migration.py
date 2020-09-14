from app.database.client import Client


class BaseMigration:
    def migrate(self, es: Client):
        pass

    def roll_back(self, es: Client):
        pass
