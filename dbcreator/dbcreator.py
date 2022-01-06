import os
import configparser
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'info'

    id = sql.Column(sql.Integer, primary_key=True)
    number = sql.Column(sql.Integer)
    name = sql.Column(sql.String)
    surname = sql.Column(sql.String)

    def __repr__(self):
        return "<User(number='%s', name='%s', surname='%s')>" % (self.number, self.name, self.surname)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PostgresConfiguration:
    config = configparser.ConfigParser()
    config.read('./config.ini')
    print(os.getcwd())

    DB_USER = config['POSTGRES']['DB_USER']
    DB_PASSWORD = config['POSTGRES']['DB_PASSWORD']
    DB_HOST = config['POSTGRES']['DB_HOST']
    DB_NAME = config['POSTGRES']['DB_NAME']
    DB_PORT = config['POSTGRES']['DB_PORT']

    @property
    def postgres_db_path(self):
        return f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


def show(table):
    if table:
        print("Data:")
        print("+--------------+")
        for text in table:
            print(text.id, text.number)
        print("+--------------+")
    else:
        print("Error: no data")


pg = PostgresConfiguration()
engine = sql.create_engine(pg.postgres_db_path)
Session = sessionmaker(bind=engine)
session = Session()

show(session.query(User).all())