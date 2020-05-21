# connector_class.py

from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
# establish connection



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

	def insert_df(self, df, connection):
		""" This function is used to append df to database, if no database will create """
		df.to_sql(df, connection, index=False, if_exists='append')

	def query(self, connection, query):
		""" This function is used to query the database table"""
		query_results = pd.read_sql_query(query, connection)
		return query_results


database = 'apartments'

connection, engine = SQLiteConnector(database).create_database()

inspector = SQLiteConnector.inspector(engine)

print(inspector.get_table_names())


