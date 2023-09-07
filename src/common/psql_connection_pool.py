import psycopg2
import psycopg2.pool
import sys

sys.path.append(".")
from src.common.psql_connection_pool_settings import PSQLConnectionPoolSettings


class PSQLConnectionPool():
    
    def __init__(self, settings = PSQLConnectionPoolSettings()) -> None:
        self._conf = settings
        self.minconn = self._conf.min_connections
        self.maxconn = self._conf.max_connections
        self.dbname = self._conf.db_name
        self.user = self._conf.db_user
        self.password = self._conf.db_password
        self.host = self._conf.db_host
        self.port = self._conf.db_port
        self.connection_pool = None
                                  
                                
    def create_pool(self):
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=self.minconn,
                maxconn=self.maxconn,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            # self._logger.debug("Connection pool created successfully!")
        except (Exception, psycopg2.DatabaseError) as error:
            return
            # self._logger.error("Error while creating PostgreSQL connection pool:", error)
            
    def get_psql_connection(self):
        if self.connection_pool:
            return self.connection_pool.getconn()
        else:
            return
            # self._logger.error("Connection pool is not initialized. Call create_pool() first.")
            
    def release_psql_connection(self, connection):
        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)
        else:
            return
            # self._logger.error("Connection pool is not initialized. Call create_pool() first.")
    
    def close_pool(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            # self._logger.debug("Connection pool closed successfully!")
        else:
            return 
            # self._logger.error("Connection pool is not initialized.")