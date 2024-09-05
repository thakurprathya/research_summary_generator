from services.db_config import get_db_connection
from datetime import datetime

db, connection_status = get_db_connection()
faculty_collection = db['faculty'] if db is not None else None

def create_faculty(name, research):
    if faculty_collection is None:
        raise RuntimeError("Database connection is not established.")
    
    if not name or not research:
        raise ValueError("Name and research are required")

    required_fields = ['year', 'publicationTitle', 'publicationLink', 'abstract']
    for index, item in enumerate(research):
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            raise ValueError(f"Research item {index + 1} is missing required fields: {', '.join(missing_fields)}")

    new_faculty = {
        'name': name,
        'research': research,
        'created_at': datetime.utcnow()
    }

    result = faculty_collection.insert_one(new_faculty)
    return str(result.inserted_id)

def get_all():
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

def validate_research(research):
    required_fields = ['year', 'publicationTitle', 'publicationLink', 'abstract']
    for index, item in enumerate(research):
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            raise ValueError(f"Research item {index + 1} is missing required fields: {', '.join(missing_fields)}")