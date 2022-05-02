import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, and_, BigInteger
from sqlalchemy.schema import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
login = os.getenv('SQL_LOGIN')
password = os.getenv('SQL_PASSW')
host = os.getenv('SQL_HOST')
db_name = os.getenv('SQL_DBNAME')

uri = f'mysql://{login}:{password}@{host}/{db_name}'
engine = create_engine(uri)
Base = declarative_base()


class TestTabl1(Base):
    __tablename__ = 'test'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(256))

    def __str__(self):
        return f'{self.id}: {self.name}'


class UserProfile(Base):
    __tablename__ = 'user_profile'
    user_id = Column('user_id', String(32))
    server_id = Column('server_id', String(32))

    __table_args__ = (
        PrimaryKeyConstraint(user_id, server_id),
    )


class Wallet(Base):
    __tablename__ = 'wallet'
    id = Column('id', Integer, primary_key=True)
    money = Column('money', Integer)
    user_id = Column('user_id', String(32))
    server_id = Column('server_id', String(32))

    __table_args__ = (
        ForeignKeyConstraint(
            ('user_id', 'server_id'), ['user_profile.user_id', 'user_profile.server_id']),
    )


class Badge(Base):
    __tablename__ = 'badges'
    id = Column('id', Integer, primary_key=True)
    badge = Column('name', String(64))
    description = Column('description', String(256))
    user_id = Column('user_id', String(32))
    server_id = Column('server_id', String(32))

    __table_args__ = (
        ForeignKeyConstraint(
            ('user_id', 'server_id'), ['user_profile.user_id', 'user_profile.server_id']),
    )


class RegisteredChannel(Base):
    __tablename__ = 'channels'
    id = Column('id', String(32), primary_key=True)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

table_names = {
    'test' : TestTabl1,
    'wallet' : Wallet,
    'user' : UserProfile,
    'badge': Badge,
    'channel': RegisteredChannel
}


def read_all_rows_from_table(t: type):
    session = Session()
    rows = session.query(t).all()
    session.close()
    return rows


def write_to_table(item: Base):
    session = Session()

    if session.query(type(item)).one_or_none() is None:
        session.add(item)
        session.commit()
    session.close()


def read_userdata_from_table(table_key, user_id, server_id):
    session = Session()
    result = get_item(session, table_key, server_id, user_id)

    session.close()
    return result


def get_item(session, table_key, server_id, user_id):
    t = table_names[table_key]
    result = session.query(t). \
        filter(and_(t.user_id == user_id, t.server_id == server_id)).one_or_none()
    if result is None:
        create_record(server_id=server_id, session=session, user_id=user_id)
        result = session.query(t). \
            filter(and_(t.user_id == user_id, t.server_id == server_id)).one_or_none()
    return result


def update_table(table_key, user_id, server_id, key, value):
    session = Session()
    result = get_item(session, table_key, server_id, user_id)
    setattr(result, key, value)
    session.commit()
    session.close()


def get_user_data(user_id, server_id):
    session = Session()
    result = query_user_data(server_id, session, user_id)

    if result is None:
        create_record(server_id, session, user_id)
        result = query_user_data(server_id, session, user_id)

    session.close()
    dictionary = {
        'badges' : result[0],
        'wallet' : result[1]
    }
    return dictionary


def create_record(server_id, session, user_id):
    user_profile = UserProfile()
    user_profile.user_id = user_id
    user_profile.server_id = server_id
    session.add(user_profile)
    session.commit()
    badges = Badge()
    badges.user_id = user_id
    badges.server_id = server_id
    session.add(badges)
    session.commit()
    wallet = Wallet()
    wallet.user_id = user_id
    wallet.server_id = server_id
    wallet.money = 0
    session.add(wallet)
    session.commit()


def query_user_data(server_id, session, user_id):
    result = session.query(Badge, Wallet). \
        join(Wallet, and_(Badge.user_id == Wallet.user_id, Badge.server_id == Wallet.server_id)). \
        filter(and_(Badge.user_id == user_id, Badge.server_id == server_id)).one_or_none()
    return result

def find_active_users(server_id, session):
    result = session.query(Wallet). \
        filter(and_(Wallet.server_id == server_id, Wallet.money > 0)).all()
    return result
