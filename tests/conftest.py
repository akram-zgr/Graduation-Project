"""
Test configuration and fixtures for the chatbot test suite.
"""
import pytest
import os
import tempfile
from app import app as flask_app
from extensions import db
from models.user import User
from models.university import University
from models.department import Department
from models.knowledge_base import KnowledgeBase
from models.chat import Chat
from models.message import Message


@pytest.fixture(scope='function')
def app():
    """Create and configure a test Flask application instance."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'MAIL_SUPPRESS_SEND': True,
    })
    
    # Create the database and tables
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for tests."""
    with app.app_context():
        yield db.session


@pytest.fixture(scope='function')
def sample_universities(db_session):
    """Create sample universities for testing."""
    universities = [
        University(
            name='University of Batna 2',
            name_ar='جامعة باتنة 2',
            code='BATNA2',
            city='Batna',
            website='https://univ-batna2.dz',
            email='contact@univ-batna2.dz',
            phone='+213 33 81 51 51',
            is_active=True
        ),
        University(
            name='University of Algiers 1',
            name_ar='جامعة الجزائر 1',
            code='ALGIERS1',
            city='Algiers',
            website='https://univ-alger.dz',
            email='contact@univ-alger.dz',
            phone='+213 21 12 34 56',
            is_active=True
        ),
        University(
            name='University of Constantine 1',
            name_ar='جامعة قسنطينة 1',
            code='CONSTANTINE1',
            city='Constantine',
            website='https://umc.edu.dz',
            email='contact@umc.edu.dz',
            is_active=True
        )
    ]
    
    for univ in universities:
        db_session.add(univ)
    
    db_session.commit()
    return universities


@pytest.fixture(scope='function')
def sample_departments(db_session, sample_universities):
    """Create sample departments for testing."""
    departments = [
        Department(
            name='Computer Science',
            name_ar='علوم الحاسوب',
            code='CS',
            university_id=sample_universities[0].id,
            description='Department of Computer Science',
            building='Building A',
            email='cs@univ-batna2.dz',
            phone='+213 33 81 51 52',
            head_of_department='Dr. Ahmed Ben Ali'
        ),
        Department(
            name='Mathematics',
            name_ar='الرياضيات',
            code='MATH',
            university_id=sample_universities[0].id,
            description='Department of Mathematics',
            building='Building B',
            email='math@univ-batna2.dz'
        ),
        Department(
            name='Physics',
            name_ar='الفيزياء',
            code='PHY',
            university_id=sample_universities[1].id,
            description='Department of Physics',
            building='Building C',
            email='physics@univ-alger.dz'
        )
    ]
    
    for dept in departments:
        db_session.add(dept)
    
    db_session.commit()
    return departments


@pytest.fixture(scope='function')
def sample_users(db_session, sample_universities, sample_departments):
    """Create sample users with different roles for testing."""
    users = []
    
    # Super admin (no university affiliation)
    super_admin = User(
        username='superadmin',
        email='superadmin@test.com',
        full_name='Super Administrator',
        is_admin=True,
        is_verified=True
    )
    super_admin.set_password('SuperAdmin123!')
    users.append(super_admin)
    
    # University admin for Batna 2
    batna_admin = User(
        username='batna_admin',
        email='admin@batna2.test.com',
        full_name='Batna Admin',
        university_id=sample_universities[0].id,
        is_admin=True,
        is_verified=True
    )
    batna_admin.set_password('BatnaAdmin123!')
    users.append(batna_admin)
    
    # University admin for Algiers 1
    algiers_admin = User(
        username='algiers_admin',
        email='admin@algiers1.test.com',
        full_name='Algiers Admin',
        university_id=sample_universities[1].id,
        is_admin=True,
        is_verified=True
    )
    algiers_admin.set_password('AlgiersAdmin123!')
    users.append(algiers_admin)
    
    # Student at Batna 2 - CS Department
    batna_student1 = User(
        username='batna_student1',
        email='student1@batna2.test.com',
        full_name='Ahmed Student',
        university_id=sample_universities[0].id,
        department_id=sample_departments[0].id,
        student_id='CS2021001',
        is_verified=True
    )
    batna_student1.set_password('Student123!')
    users.append(batna_student1)
    
    # Student at Batna 2 - Math Department
    batna_student2 = User(
        username='batna_student2',
        email='student2@batna2.test.com',
        full_name='Fatima Student',
        university_id=sample_universities[0].id,
        department_id=sample_departments[1].id,
        student_id='MATH2021002',
        is_verified=True
    )
    batna_student2.set_password('Student123!')
    users.append(batna_student2)
    
    # Student at Algiers 1
    algiers_student = User(
        username='algiers_student',
        email='student@algiers1.test.com',
        full_name='Omar Student',
        university_id=sample_universities[1].id,
        department_id=sample_departments[2].id,
        student_id='PHY2021003',
        is_verified=True
    )
    algiers_student.set_password('Student123!')
    users.append(algiers_student)
    
    # Unverified user
    unverified_user = User(
        username='unverified',
        email='unverified@test.com',
        full_name='Unverified User',
        university_id=sample_universities[0].id,
        is_verified=False
    )
    unverified_user.set_password('Unverified123!')
    unverified_user.generate_verification_token()
    users.append(unverified_user)
    
    for user in users:
        db_session.add(user)
    
    db_session.commit()
    return users


@pytest.fixture(scope='function')
def sample_knowledge_base(db_session, sample_universities, sample_users):
    """Create sample knowledge base entries for testing."""
    knowledge_entries = [
        # Batna 2 - General
        KnowledgeBase(
            university_id=sample_universities[0].id,
            title='Registration Process',
            content='Students must register online through the university portal before September 15th. Required documents include ID card, baccalaureate certificate, and 2 photos.',
            content_ar='يجب على الطلاب التسجيل عبر الإنترنت قبل 15 سبتمبر.',
            category='registration',
            tags='registration,enrollment,documents',
            priority=10,
            is_active=True,
            created_by=sample_users[1].id
        ),
        KnowledgeBase(
            university_id=sample_universities[0].id,
            title='Tuition Fees',
            content='Tuition is free for Algerian students. Administrative fees are 500 DZD per semester.',
            category='tuition',
            tags='fees,payment,tuition',
            priority=9,
            is_active=True,
            created_by=sample_users[1].id
        ),
        KnowledgeBase(
            university_id=sample_universities[0].id,
            title='Library Hours',
            content='The main library is open Monday-Friday 8:00-18:00, Saturday 9:00-13:00. Closed on Sundays.',
            category='campus',
            tags='library,hours,campus',
            priority=5,
            is_active=True,
            created_by=sample_users[1].id
        ),
        # Algiers 1 - General
        KnowledgeBase(
            university_id=sample_universities[1].id,
            title='Registration Deadline',
            content='Registration for new students closes on September 20th. Late registration may incur additional fees.',
            category='registration',
            tags='registration,deadline',
            priority=10,
            is_active=True,
            created_by=sample_users[2].id
        ),
        KnowledgeBase(
            university_id=sample_universities[1].id,
            title='Campus Facilities',
            content='Campus includes 3 libraries, 2 cafeterias, sports complex, and medical center.',
            category='campus',
            tags='facilities,campus,services',
            priority=6,
            is_active=True,
            created_by=sample_users[2].id
        ),
        # Constantine 1
        KnowledgeBase(
            university_id=sample_universities[2].id,
            title='Academic Calendar',
            content='Fall semester: September-January. Spring semester: February-June.',
            category='academic',
            tags='calendar,semester,schedule',
            priority=8,
            is_active=True,
            created_by=sample_users[0].id
        ),
    ]
    
    for entry in knowledge_entries:
        db_session.add(entry)
    
    db_session.commit()
    return knowledge_entries


@pytest.fixture(scope='function')
def sample_chats(db_session, sample_users):
    """Create sample chat sessions for testing."""
    chats = [
        # Batna student 1 chats
        Chat(
            user_id=sample_users[3].id,  # batna_student1
            title='Registration Questions',
            is_active=True
        ),
        Chat(
            user_id=sample_users[3].id,
            title='Exam Schedule',
            is_active=True
        ),
        # Batna student 2 chats
        Chat(
            user_id=sample_users[4].id,  # batna_student2
            title='Library Access',
            is_active=True
        ),
        # Algiers student chats
        Chat(
            user_id=sample_users[5].id,  # algiers_student
            title='Course Information',
            is_active=True
        ),
        # Deleted chat
        Chat(
            user_id=sample_users[3].id,
            title='Old Conversation',
            is_active=False
        ),
    ]
    
    for chat in chats:
        db_session.add(chat)
    
    db_session.commit()
    return chats


@pytest.fixture(scope='function')
def sample_messages(db_session, sample_chats):
    """Create sample messages for testing."""
    messages = [
        # Chat 1 messages
        Message(
            chat_id=sample_chats[0].id,
            content='How do I register for courses?',
            role='user',
            token_count=10
        ),
        Message(
            chat_id=sample_chats[0].id,
            content='You can register for courses through the online portal...',
            role='assistant',
            token_count=50,
            model='gemini-pro'
        ),
        Message(
            chat_id=sample_chats[0].id,
            content='What documents do I need?',
            role='user',
            token_count=8
        ),
        Message(
            chat_id=sample_chats[0].id,
            content='You need your ID card, baccalaureate certificate...',
            role='assistant',
            token_count=45,
            model='gemini-pro'
        ),
        # Chat 2 messages
        Message(
            chat_id=sample_chats[1].id,
            content='When is the exam?',
            role='user',
            token_count=7
        ),
        Message(
            chat_id=sample_chats[1].id,
            content='Exams are scheduled for January...',
            role='assistant',
            token_count=30,
            model='gemini-pro'
        ),
        # Chat 3 messages
        Message(
            chat_id=sample_chats[2].id,
            content='What are the library hours?',
            role='user',
            token_count=9
        ),
        Message(
            chat_id=sample_chats[2].id,
            content='The library is open Monday-Friday...',
            role='assistant',
            token_count=35,
            model='gemini-pro'
        ),
    ]
    
    for msg in messages:
        db_session.add(msg)
    
    db_session.commit()
    return messages


@pytest.fixture(scope='function')
def authenticated_client(client, sample_users):
    """Create a client authenticated as a regular student."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_users[3].id  # batna_student1
        sess['username'] = sample_users[3].username
    return client


@pytest.fixture(scope='function')
def admin_client(client, sample_users):
    """Create a client authenticated as a university admin."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_users[1].id  # batna_admin
        sess['username'] = sample_users[1].username
    return client


@pytest.fixture(scope='function')
def super_admin_client(client, sample_users):
    """Create a client authenticated as a super admin."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_users[0].id  # superadmin
        sess['username'] = sample_users[0].username
    return client
