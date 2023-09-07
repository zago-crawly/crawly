from pydantic_settings import BaseSettings


class PSQLConnectionPoolSettings(BaseSettings):
    
    min_connections: int = 2
    max_connections: int = 20
    db_name: str = 'crawly'
    db_host: str = 'psql'
    db_user: str = 'crwl'
    db_port: int = 5432
    db_password: str = 'Crawly97'
    