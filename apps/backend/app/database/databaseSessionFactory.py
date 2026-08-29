from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from app.config.databaseSettings import databaseSettings


databaseUrl = URL.create(
    drivername="postgresql+psycopg",
    username=databaseSettings.user,
    password=databaseSettings.password,
    host=databaseSettings.host,
    port=databaseSettings.port,
    database=databaseSettings.database,
)

databaseEngine = create_engine(
    databaseUrl,
    pool_pre_ping=True,
    future=True,
)

DatabaseSessionFactory = sessionmaker(
    bind=databaseEngine,
    autoflush=False,
    expire_on_commit=False,
)
