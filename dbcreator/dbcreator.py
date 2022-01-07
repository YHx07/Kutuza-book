import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'info'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String)
    dttm = sql.Column(sql.String)
    workplace = sql.Column(sql.String)

    def __repr__(self):
        return "<User(id='%s', name='%s', dttm='%s', workplace='%s')>" %\
               (self.id, self.name, self.dttm, self.workplace)

    def as_dict(self):
        return {c.id: getattr(self, c.id) for c in self.__table__.columns}


class PostgresConfiguration:

    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_HOST = "db"
    DB_PORT = "5432"
    DB_NAME = "postgres"

    @property
    def postgres_db_path(self):
        return f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


pg = PostgresConfiguration()
engine = sql.create_engine(pg.postgres_db_path)
Session = sessionmaker(bind=engine)
session = Session()

data = pd.read_csv(
    "data/data.csv",
    header=None,
    names=['id', 'name', 'dttm', 'workplace']
)
data.to_sql('info', engine, index=False, if_exists='append')

print("Recorded csv to table in postgre........")

table = session.query(User).all()

if table:
    print("================ DATA =================")
    for text in table:
        print(text)
    print("============ Data is exist ============")
else:
    print("Error: data not loaded")