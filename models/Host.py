from sqlalchemy import Column, Integer, String, Boolean
from configs.db import db


class Host(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(50), nullable=False, unique=True)
    addr = Column(String(50), nullable=False)
    port = Column(Integer, default=80)
    manager = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    user_num = Column(Integer, default=0)
    status = Column(Boolean, default=True)

    def __init__(self, host=None, addr=None, port=80, manager=None, password=None, user_num=0, status=True ):
        self.host = host
        self.addr = addr
        self.port = port
        self.manager = manager
        self.password = password
        self.user_num = user_num
        self.status = status

    def to_json(self):
        return {
            'host': self.host,
            'addr': self.addr,
            'port': self.port,
            'manager': self.manager,
            'password': self.password,
            'user_num': self.user_num,
            'status': self.status
        }

    def to_select_field(self):
        field = (self.id, self.host)
        return field
