from services.db_config import get_db_connection
from datetime import datetime

db, connection_status = get_db_connection()
faculty_collection = db['faculty'] if db else None

def create_faculty(name, research):
    if db is None:
        raise RuntimeError("Database connection is not established.")
    
    if not name or not research:
        raise ValueError("Name and research are required")

    for item in research:
        required_fields = ['year', 'publicationTitle', 'publicationLink', 'abstract']
        if not all(field in item for field in required_fields):
            raise ValueError("Research item is missing required fields")

    new_faculty = {
        'name': name,
        'research': research,
        'created_at': datetime.utcnow()
    }

    result = faculty_collection.insert_one(new_faculty)
    return str(result.inserted_id)

def get_all_faculty():
    if db is None:
        raise RuntimeError("Database connection is not established.")
    
    faculty_members = faculty_collection.find()
    faculty_list = []
    for faculty in faculty_members:
        faculty_list.append({
            'id': str(faculty['_id']),
            'name': faculty['name'],
            'research': faculty['research'],
            'created_at': faculty['created_at'].isoformat()
        })
    return faculty_list
