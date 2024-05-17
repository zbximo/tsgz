import config
import sshtunnel
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base


class dbTools(object):
    session = None
    isClosed = True

    def open(self, db_config=config.DB_CONFIG, use_ssh=False):
        user = db_config['username']
        pwd = db_config["password"]
        host = db_config['host']
        port = db_config["port"]
        db = db_config['database']
        if use_ssh:
            host, port = self.open_ssh()
        url = 'mysql+pymysql://%s:%s@%s:%d/%s' % (user, pwd, host, port, db)
        print(url)
        engine = create_engine(url, echo=False)
        DbSession = sessionmaker(bind=engine)

        self.session = DbSession()
        self.isClosed = False
        return self.session

    def open_ssh(self):
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

    def query(self, type):
        query = self.session.query(type)
        return query

    def execute(self, sql):
        return self.session.execute(sql)

    def add(self, item):
        self.session.add(item)

    def add_all(self, items):
        self.session.add_all(items)

    def delete(self, item):
        self.session.delete(item)

    def commit(self):
        self.session.commit()

    def close(self):
        if self.isClosed:
            pass
        try:
            self.session.close()
            self.tunnel.close()
            self.isClosed = True
        except Exception as e:
            pass


if __name__ == '__main__':
    db = dbTools()
    db.open(use_ssh=True)
    result = db.execute(text("show tables"))
    for i in result:
        print(i)
    db.close()
