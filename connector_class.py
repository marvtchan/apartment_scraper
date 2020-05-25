# connector_class.py

# from apartment import eb_apts

from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
# establish connection

import pandas as pd
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 300)
pd.set_option('display.width', 1000)

database = 'apartments'

class SQLiteConnector:
	def __init__(self, database):
		self.database = database
		
	def create_database(self):
		engine = create_engine('sqlite:///' + self.database + '.db', echo=False)
		connection = engine.raw_connection()
		return connection, engine

	def inspector(engine):
		""" This function is used to get all table names of the database. Set engine to 
		SQLiteConnector.create_database(database) and print(inspector.get_table_names()) """
		inspector = inspect(engine)
		return inspector

	def insert_df(df, database, connection):
		""" This function is used to append df to database, if no database will create """
		df.to_sql(database, connection, index=False, if_exists='append')

	def query(connection, query):
		""" This function is used to query the database table"""
		query_results = pd.read_sql_query(query, connection)
		return query_results


connection, engine = SQLiteConnector(database).create_database()

Base = declarative_base()

class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listing'

    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    sqft = Column(String)
    bedrooms = Column(Float)
    availability = Column(String)
    cl_id = Column(Integer, unique=True)
    city = Column(String)
    mapped = Column(String)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

inspector = SQLiteConnector.inspector(engine)

# SQLiteConnector.insert_df(eb_apts, database, connection)

print(inspector.get_table_names())

query = "SELECT * from listing"

if __name__ == '__main__':
	print(SQLiteConnector.query(connection,query))

