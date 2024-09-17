import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
mongodb_db = os.getenv('MONGODB_DB')

def get_db_connection():
    try:
        client = MongoClient(mongodb_uri, serverselectiontimeoutms=5000, maxpoolsize=5000)
        client.admin.command('ping')
        client.server_info()
        db = client[mongodb_db] if mongodb_db is not None else None
        
        if db is not None:
            faculty_collection = db['faculty']
            faculty_collection.create_index('name', unique=True)
            return db, "Connection successful"
        else:
            raise Exception("Database not found")
        
    except errors.ServerSelectionTimeoutError as e:
        error_message = str(e)
        return None, "Connection failed: Server selection timeout"
    except errors.InvalidURI as e:
        error_message = str(e)
        return None, "Connection failed: Invalid URI"
    except errors.OperationFailure as e:
        error_message = str(e)
        return None, "Connection failed: Authentication error"
    except Exception as e:
        error_message = str(e)
        return None, f"Connection failed: {str(e)}"