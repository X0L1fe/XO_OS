import sys
sys.path.insert(0, '.')

from app.auth.service import get_password_hash
from app.database import db
from app.database.models import User

with db.session() as session:
    # Check if user already exists
    existing = session.query(User).filter(User.email == 'test@example.com').first()
    if existing:
        # Update to verified if not already
        if not existing.email_verified:
            existing.email_verified = True
            existing.mais_group_id = ''
            existing.selected_calendar_id = 'primary'
            session.add(existing)
        user = existing
    else:
        # Create new user
        hashed_password = get_password_hash('testpassword')
        user = User(
            email='test@example.com',
            hashed_password=hashed_password,
            is_active=True,
            email_verified=True,
            maiis_group_id='',
            selected_calendar_id='primary',
        )
        session.add(user)
    session.commit()

    # Now authenticate
    from app.auth.service import authenticate_user, create_session
    auth_user = authenticate_user(session, 'test@example.com', 'testpassword')
    if auth_user:
        session_obj = create_session(session, auth_user.id)
        print(session_obj.token)
    else:
        print('')
EOF