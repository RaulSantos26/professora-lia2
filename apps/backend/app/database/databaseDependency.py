from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.databaseSessionFactory import DatabaseSessionFactory


def getDatabaseSession() -> Generator[Session, None, None]:
    session = DatabaseSessionFactory()

    try:
        yield session
    finally:
        session.close()
