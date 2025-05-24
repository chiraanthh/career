from app import app
from models import db, CareerCounselor
from datetime import datetime


def initialize_counsellors():
    for c in initial_counsellors:
        existing = CareerCounselor.query.filter_by(email=c['email']).first()
        if existing:
            continue
        counsellor = CareerCounselor(
            first_name=c['first_name'],
            last_name=c['last_name'],
            email=c['email'],
            specialization=c['specialization'],
            qualification=c['qualification'],
            years_of_experience=c['years_of_experience'],
            bio=c['bio'],
            availability_status=c['availability_status'],
            rating=c['rating'],
            date_registered=datetime.utcnow()
        )
        counsellor.set_password(c['password'])
        db.session.add(counsellor)
    db.session.commit()

initial_counsellors = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'password123',
        'specialization': 'Technology & Engineering',
        'qualification': 'MSc Computer Science',
        'years_of_experience': 10,
        'bio': 'Experienced technology counselor.',
        'availability_status': True,
        'rating': 4.5
    },
    {
        'first_name': 'Aisha',
        'last_name': 'Patel',
        'email': 'aisha.patel@example.com',
        'password': 'password123',
        'specialization': 'Technology & Startups',
        'qualification': 'MBA Entrepreneurship',
        'years_of_experience': 6,
        'bio': 'Startup and technology expert.',
        'availability_status': True,
        'rating': 4.7
    },
    {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@example.com',
        'password': 'password123',
        'specialization': 'Healthcare & Medicine',
        'qualification': 'MD Medicine',
        'years_of_experience': 8,
        'bio': 'Healthcare career counselor.',
        'availability_status': True,
        'rating': 4.6
    },
    {
        'first_name': 'Ahmed',
        'last_name': 'Khan',
        'email': 'ahmed.khan@example.com',
        'password': 'password123',
        'specialization': 'Public Health & Research',
        'qualification': 'PhD Public Health',
        'years_of_experience': 11,
        'bio': 'Public health specialist.',
        'availability_status': True,
        'rating': 4.8
    },
    {
        'first_name': 'Michael',
        'last_name': 'Brown',
        'email': 'michael.brown@example.com',
        'password': 'password123',
        'specialization': 'Business & Finance',
        'qualification': 'MBA Finance',
        'years_of_experience': 12,
        'bio': 'Business and finance counselor.',
        'availability_status': True,
        'rating': 4.9
    },
    {
        'first_name': 'Rachel',
        'last_name': 'Lee',
        'email': 'rachel.lee@example.com',
        'password': 'password123',
        'specialization': 'Entrepreneurship & MBA',
        'qualification': 'MBA Business',
        'years_of_experience': 7,
        'bio': 'Entrepreneurship expert.',
        'availability_status': True,
        'rating': 4.4
    }
]
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initialize_counsellors()
        print("Database tables created and counselors initialized!")
