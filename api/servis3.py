import os
import pandas as pd
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
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


def show(table):
    if table:
        print("Data:")
        print("+--------------+")
        for text in table:
            print(text.id, text.name, text.dttm, text.workplace)
        print("+--------------+")
    else:
        print("Error: no data")


app = FastAPI()
templates = Jinja2Templates(directory="templates")

pg = PostgresConfiguration()
engine = sql.create_engine(pg.postgres_db_path)
Session = sessionmaker(bind=engine)
session = Session()


from starlette.exceptions import HTTPException as StarletteHTTPException
@app.exception_handler(StarletteHTTPException)
def custom_http_exception_handler(request, exc):
    return JSONResponse({"Error:404": "Wrong request address"})


@app.get('/')
async def get_all_items(request: Request):
    table = session.query(User).all()
    for text in table:
        print(text)

    df = pd.read_sql('SELECT * FROM info', engine)

    return templates.TemplateResponse(
        'df_representation.html',
        {'request': request, 'data': df.to_html()}
    )

@app.get('/health')
def heath():
    return 200