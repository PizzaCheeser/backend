from app.database.base import ES_config

database = ES_config()
database.delete_whole_database()
database.create_structure()