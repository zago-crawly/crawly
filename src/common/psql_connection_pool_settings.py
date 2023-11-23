from pydantic_settings import BaseSettings
import os


class PSQLConnectionPoolSettings(BaseSettings):
    
    min_connections: int = os.environ.get('PSQL_POOL_MIN_CONN', 2)
    max_connections: int = os.environ.get('PSQL_POOL_MAX_CONN', 20)
    db_name: str = os.environ.get('PSQL_DB_NAME', 'crawly')
    db_host: str = os.environ.get('PSQL_DB_HOST', 'psql')
    db_user: str = os.environ.get('PSQL_DB_USER', 'crwl')
    db_port: int = os.environ.get('PSQL_DB_PORT', 5432)
    db_password: str = os.environ.get('PSQL_DB_PASS', 'Crawly97')
    