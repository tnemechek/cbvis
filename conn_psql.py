import pandas as pd
from sqlalchemy import create_engine

connstr = 'postgresql+psycopg2://postgres:tnadmin@localhost:5432/'
psql_engines = {
	'mapping': create_engine(connstr + 'mapping'),
	'data': create_engine(connstr + 'data'),
	'cbvis': create_engine(connstr + 'cbvis')
	}

def psql_put(df, db_name, table_name):
	df.to_sql(table_name, psql_engines[db_name], if_exists='replace', index=False)


def psql_pull(db_name, table_name):
	query = f'SELECT * FROM {table_name}'
	return pd.read_sql(query, psql_engines[db_name])
