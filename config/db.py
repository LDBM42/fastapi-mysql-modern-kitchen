from sqlalchemy import create_engine, MetaData
# DATABASE_URL = 'mysql+mysqlconnector://<username>:<password>@<host>/<dbname>'
# DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/serversiderendering"

# engine = create_engine("mysql+pymysql://root@localhost:3306/modernkitchendb")
engine = create_engine("mysql+pymysql://id19445098_ldbm42:tituxboy69971210203AS_@localhost:3306/id19445098_modernkitchendb")
# meta = MetaData()

conn = engine.connect()