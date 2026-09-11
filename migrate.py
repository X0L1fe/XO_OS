import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Database setup
DATABASE_URL = os.getenv('XO_OS_DATABASE_URL', 'sqlite:///./data/xo_os.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password):
    return pwd_context.hash(password)

def migrate():
    db = SessionLocal()
    try:
        # Check if the user_id column exists in lessons
        result = db.execute(text("""
            SELECT COUNT(*) FROM pragma_table_info('lessons') 
            WHERE name='user_id'
        """))
        column_exists = result.scalar() > 0

        if not column_exists:
            print('Adding user_id column to lessons table...')
            # Add the column as nullable
            db.execute(text('ALTER TABLE lessons ADD COLUMN user_id INTEGER'))
            db.commit()
            print('Column added.')

        # Now, we need to set the user_id for existing lessons.
        # First, check if there are any users.
        user_count = db.execute(text('SELECT COUNT(*) FROM users')).scalar()
        if user_count == 0:
            print('No users found. Creating a default user...')
            # Create a default user
            default_email = 'default@localhost'
            default_name = 'Default User'
            default_password = get_password_hash('changeme123')  # In production, change this!
            db.execute(text("""
                INSERT INTO users (email, name, password_hash, is_active, onboarding_completed, created_at, updated_at)
                VALUES (:email, :name, :password_hash, 1, 0, datetime('now'), datetime('now'))
            """), {
                'email': default_email,
                'name': default_name,
                'password_hash': default_password
            })
            db.commit()
            # Get the id of the newly created user
            user_id = db.execute(text('SELECT last_insert_rowid()')).scalar()
            print(f'Default user created with id {user_id}.')
        else:
            # If there are users, we'll use the first one (assuming single user scenario)
            # But note: we might have multiple users after authentication is implemented.
            # For simplicity, we'll assign existing lessons to the first user.
            user_id = db.execute(text('SELECT id FROM users ORDER BY id LIMIT 1')).scalar()
            print(f'Using existing user with id {user_id} for existing lessons.')

        # Update existing lessons to set user_id to the selected user
        update_result = db.execute(text(
            'UPDATE lessons SET user_id = :user_id WHERE user_id IS NULL'
        ), {'user_id': user_id})
        db.commit()
        print(f'Updated {update_result.rowcount} lessons with user_id {user_id}.')

        # Optionally, we can now set the column to NOT NULL, but we'll skip for now to avoid migration complexity.
        # We'll leave it nullable and ensure in code that we set it for new lessons.
        print('Migration completed successfully.')

    except Exception as e:
        print(f'Error during migration: {e}')
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    migrate()
