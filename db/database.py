from concurrent.futures import ThreadPoolExecutor

import sshtunnel
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

    def open(self, use_ssh=False):
        db_config = self.config.DB_CONFIG
        user = db_config['username']
        pwd = db_config["password"]
        host = db_config['host']
        port = db_config["port"]
        db = db_config['database']
        if use_ssh:
            host, port = self.open_ssh()
        url = 'mysql+pymysql://%s:%s@%s:%d/%s' % (user, pwd, host, port, db)
        print(url)
        # engine = create_engine(url,  echo=False)

        engine = create_engine(url, max_overflow=200, pool_size=100, echo=False)
        self.engine = engine
        self.DbSession = sessionmaker(bind=engine)

    def get_new_session(self):

        session = self.DbSession()
        return session

    def open_ssh(self):
        config = self.config
        self.tunnel = sshtunnel.SSHTunnelForwarder(
            ssh_address_or_host=(config.SSH_CONFIG['host'], config.SSH_CONFIG['port']),
            ssh_username=config.SSH_CONFIG['username'],
            ssh_password=config.SSH_CONFIG['password'],
            remote_bind_address=(config.DB_CONFIG['host'], config.DB_CONFIG['port'])
        )
        self.tunnel.start()

        local_bind_address = self.tunnel.local_bind_host
        local_bind_port = self.tunnel.local_bind_port
        return local_bind_address, local_bind_port

    def close_ssh(self):
        try:
            self.tunnel.close()
        except Exception as e:
            pass


if __name__ == '__main__':
    db = dbTools("test")
    db.open(use_ssh=True)
    session = db.get_new_session()

    result = session.execute(text("show tables"))
    for i in result:
        print(i)
    session.close()
