from datetime import datetime, timezone

import psycopg

from app.contracts.serviceStatusContract import ServiceStatusContract


class PostgresHealthRepository:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    async def checkHealth(self) -> ServiceStatusContract:
        try:
            connection = await psycopg.AsyncConnection.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database,
                connect_timeout=3,
            )

            async with connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT current_database(), version()")
                    databaseName, version = await cursor.fetchone()

            return ServiceStatusContract(
                serviceName="postgres",
                status="ONLINE",
                checkedAt=datetime.now(timezone.utc),
                details={
                    "database": databaseName,
                    "server": version.split(" on ")[0],
                },
            )
        except Exception as error:
            return ServiceStatusContract(
                serviceName="postgres",
                status="OFFLINE",
                checkedAt=datetime.now(timezone.utc),
                details={"errorType": type(error).__name__},
            )
