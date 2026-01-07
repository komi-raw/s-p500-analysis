from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://sp500_main:sp500_main@127.0.0.1:3306/sp500"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

with engine.connect() as connection:
    print(connection.execute(text("SELECT DATABASE(), CURRENT_USER(), VERSION()")).one())