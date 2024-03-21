import os
import sys

sys.path.append(".")

from src.scheduler.app.crawly_sched.crawly_jobstore import CrawlyJobStore

psql_host = os.environ.get('PSQL_DB_HOST', 'psql')
psql_user = os.environ.get('PSQL_DB_USER', 'crwl') 
psql_db = os.environ.get('PSQL_DB_NAME', 'crawly')
psql_port = os.environ.get('PSQL_DB_PORT', 5432)
psql_pass = os.environ.get('PSQL_DB_PASS', 'Crawly97')

jobstores = {
    'default': CrawlyJobStore(url=f"postgresql://{psql_user}:{psql_pass}@{psql_host}:{psql_port}/{psql_db}"),
}
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}