from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base


class dbTools(object):

    def __init__(self, mode='test'):
        if mode == 'test':
            config_module = 'config'
        else:
            config_module = 'config_pro'

        self.config = __import__(config_module)

    def open(self):
        db_config = self.config.DB_CONFIG
        user = db_config['username']
        pwd = db_config["password"]
        host = db_config['host']
        port = db_config["port"]
        db = db_config['database']

        url = 'mysql+pymysql://%s:%s@%s:%d/%s' % (user, pwd, host, port, db)
        # engine = create_engine(url,  echo=False)
        print(url)
        engine = create_engine(url, max_overflow=200, pool_size=100, echo=False)
        try:
            engine.connect()
        except Exception as e:
            print(f"Connection failed: {e}")
            exit(1)
        self.engine = engine
        self.DbSession = sessionmaker(bind=engine)

    def get_new_session(self):

        session = self.DbSession()
        return session


if __name__ == '__main__':
    db = dbTools("test")
    db.open()
    session = db.get_new_session()

    result = session.execute(text("show tables"))
    for i in result:
        print(i)
    session.close()
