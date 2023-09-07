from apscheduler.jobstores.mongodb import MongoDBJobStore
from pymongo import MongoClient

client = MongoClient('mongodb://crwl:Crawly97@mongodb/')

jobstores = {
    'default': MongoDBJobStore(client=client),
}
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}