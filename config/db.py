from sqlalchemy import create_engine, MetaData
# DATABASE_URL = 'mysql+mysqlconnector://<username>:<password>@<host>/<dbname>'
# DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/serversiderendering"

# engine = create_engine("mysql+pymysql://root@localhost:3306/modernkitchendb")
CLEARDB_DATABASE_URL = "mysql+pymysql://bd213d79e5d0f0:e9dda132@us-cdbr-east-06.cleardb.net/heroku_cc73e3a97a02270?reconnect=true"
engine = create_engine(CLEARDB_DATABASE_URL)
# meta = MetaData()

conn = engine.connect()