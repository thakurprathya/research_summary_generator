from services.db_config import get_db_connection
from datetime import datetime, timezone

db, connection_status = get_db_connection()
faculty_collection = db['faculty'] if db is not None else None

def find_research(email, publication_title):
    if faculty_collection is None:
        raise RuntimeError("Database connection is not established.")
    
    faculty = faculty_collection.find_one({
        'email': email,
        'research': {
            '$elemMatch': {
                'publicationTitle': publication_title
            }
        }
    })
    return faculty

def get_research_by_title(email, publication_title):
    if faculty_collection is None:
        raise RuntimeError("Database connection is not established.")
    
    faculty = find_research(email, publication_title)
    
    if faculty:
        for research in faculty['research']:
            if research['publicationTitle'].lower() == publication_title.lower():
                return research
    return None

def find_faculty(email):
    if faculty_collection is None:
        raise RuntimeError("Database connection is not established.")
    return faculty_collection.find_one({'email': email})

def create_faculty(name, email, address, research, institution):
    if faculty_collection is None:
        raise RuntimeError("Database connection is not established.")

    new_faculty = {
        'name': name,
        'email': email,
        'address': address,
        'institution': institution,
        'research': research,
        'created_at': datetime.now(timezone.utc)
    }

    result = faculty_collection.insert_one(new_faculty)
    return str(result.inserted_id)

def update_faculty(name, email, address, research, institution):
    if faculty_collection is None:
        raise RuntimeError("Database connection is not established.")
    
    existing_faculty = faculty_collection.find_one({'email': email})
    existing_research = existing_faculty.get('research', []) if existing_faculty else []
    updated_research = existing_research + research
    
    # Removing duplicates
    seen_titles = set()
    unique_research = []
    for item in updated_research:
        if item['publicationTitle'] not in seen_titles:
            seen_titles.add(item['publicationTitle'])
            unique_research.append(item)
    
    update_data = {
        'name': name,
        'institution': institution,
        'address': address,
        'research': unique_research,
        'updated_at': datetime.now(timezone.utc)
    }
    
    faculty_collection.update_one(
        {'email': email},
        {'$set': update_data}
    )
    
    faculty = faculty_collection.find_one({'email': email})
    return str(faculty['_id'])

def add_faculty_to_db(name, email, address, research, institution):
    if not name or not research or not institution or not email or not address:
        raise ValueError("Required Information not present...")
    
    validate_research(research)
    
    existing_faculty = find_faculty(email)
    if existing_faculty:
        return update_faculty(name, email, address, research, institution)
    else:
        return create_faculty(name, email, address, research, institution)

def get_allfaculty():
    if db is None:
        raise RuntimeError("Database connection is not established.")
    
    faculty_members = faculty_collection.find()
    faculty_list = []
    for faculty in faculty_members:
        faculty_list.append({
            'id': str(faculty['_id']),
            'name': faculty['name'],
            'email': faculty['email'],
            'address': faculty['address'],
            'institution': faculty['institution'],
            'research': faculty['research'],
            'created_at': faculty['created_at'].isoformat()
        })
    return faculty_list

def validate_research(research):
    required_fields = ['year', 'publicationTitle', 'publicationLink', 'abstract', 'journal']
    for index, item in enumerate(research):
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            raise ValueError(f"Research item {index + 1} is missing required fields: {', '.join(missing_fields)}")