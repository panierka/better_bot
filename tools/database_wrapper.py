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


class Badges(Base):
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


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

debug_dict = {
    'test' : TestTabl1,
    'wallet' : Wallet,
    'user' : UserProfile
}


def read_tables(t):
    session = Session()
    items = session.query(debug_dict[t]).all()
    session.close()
    return items


def write_to_table(item: Base):
    session = Session()
    session.add(item)
    session.commit()
    session.close()


def get_user_data(user_id, server_id):
    session = Session()
    results = query_user_data(server_id, session, user_id)

    if len(results) == 0:
        user_profile = UserProfile()
        user_profile.user_id = user_id
        user_profile.server_id = server_id
        session.add(user_profile)
        session.commit()

        badges = Badges()
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
        results = query_user_data(server_id, session, user_id)

    session.close()
    dictionary = {
        'badges' : results[0][0],
        'wallet' : results[0][1]
    }
    return dictionary


def query_user_data(server_id, session, user_id):
    results = session.query(Badges, Wallet). \
        join(Wallet, and_(Badges.user_id == Wallet.user_id, Badges.server_id == Wallet.server_id)). \
        filter(and_(Badges.user_id == user_id, Badges.server_id == server_id)).all()
    return results
