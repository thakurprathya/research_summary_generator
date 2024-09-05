import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
mongodb_db = os.getenv('MONGODB_DB')

def get_db_connection():
    try:
        client = MongoClient(mongodb_uri)
        client.admin.command('ping')
        db = client[mongodb_db]
        connection_status = 'Connection successful'
        
        faculty_collection = db['faculty']
        faculty_collection.create_index('name', unique=True)
    except errors.ServerSelectionTimeoutError as e:
        db = None
        connection_status = 'Connection failed'
        error_message = str(e)
    except errors.InvalidURI as e:
        db = None
        connection_status = 'Invalid URI'
        error_message = str(e)
    except Exception as e:
        db = None
        connection_status = 'Connection failed'
        error_message = str(e)
    else:
        connection_status = 'Connection successful'
    
    return db, connection_status
