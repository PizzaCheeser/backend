from app.app import app
from ScraperDatabaseConnector import ScraperDatabaseConnector

if __name__ == '__main__':
    app.config.from_object('app.config')
    app.run(host='0.0.0.0')

