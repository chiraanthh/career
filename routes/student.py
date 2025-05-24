from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import Student, db, Notification, CareerGoal, GoalMilestone, Task, StudentDocument, Grievance, Event, EventRegistration, Message, Appointment, CounsellorSchedule, CareerCounselor
from datetime import datetime, timedelta, time
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename
import os
import uuid

student_bp = Blueprint('student', __name__)

def assign_counselor(student_interests):
    """
    Assigns a counselor to a student based on matching specializations with student interests.
    Args:
        student_interests: Comma-separated string of student interests
    Returns:
        The counselor_id of the best matching counselor, or None if no match found
    """
    # Get all active counselors
    available_counselors = CareerCounselor.query.filter_by(availability_status=True).all()
    
    if not available_counselors:
        return None
        
    # Convert student interests to a list and clean them
    interests = [interest.strip().lower() for interest in student_interests.split(',')]
    
    # Find best matching counselor based on specialization
    best_match_score = 0
    selected_counselor = None
    
    # Define specialization categories and related keywords
    specialization_keywords = {
        'Technology': ['technology', 'computer', 'it', 'software', 'programming', 'tech'],
        'Healthcare': ['healthcare', 'medical', 'medicine', 'health', 'nursing'],
        'Business': ['business', 'finance', 'management', 'entrepreneurship', 'marketing'],
        'Engineering': ['engineering', 'mechanical', 'civil', 'electrical', 'electronics'],
        'Arts': ['arts', 'creative', 'design', 'music', 'fine arts', 'media'],
        'Science': ['science', 'physics', 'chemistry', 'biology', 'research'],
        'Education': ['education', 'teaching', 'training', 'academic'],
        'Law': ['law', 'legal', 'justice', 'advocacy']
    }
    
    for counselor in available_counselors:
        match_score = 0
        counselor_specialization = counselor.specialization.lower()
        
        # Check each student interest against counselor's specialization and related keywords
        for interest in interests:
            # Direct match with specialization
            if interest in counselor_specialization:
                match_score += 2  # Give higher weight to direct matches
                continue
            
            # Check against specialization keywords
            for spec, keywords in specialization_keywords.items():
                if spec.lower() == counselor_specialization:
                    if any(keyword in interest for keyword in keywords):
                        match_score += 1
                        break
        
        # Update best match if this counselor has a better score
        if match_score > best_match_score:
            best_match_score = match_score
            selected_counselor = counselor
    
    # If no matches found, assign the counselor with highest rating
    if not selected_counselor and available_counselors:
        selected_counselor = max(available_counselors, key=lambda c: c.rating)
    
    return selected_counselor.id if selected_counselor else None

@student_bp.route('/student/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data with debug prints
            print("Starting registration process...")
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            dob_str = request.form.get('dob')
            address = request.form.get('address')
            education_level = request.form.get('education_level')
            interests = request.form.getlist('interests')
            password = request.form.get('password')

            print(f"Received data: {first_name=}, {last_name=}, {email=}, {interests=}")

            # Validate required fields
            if not all([first_name, last_name, email, password, dob_str]):
                flash('Please fill in all required fields', 'danger')
                return render_template('student/register.html')

            # Parse date of birth
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError as e:
                print(f"DOB parsing error: {e}")
                flash('Invalid date format for date of birth', 'danger')
                return render_template('student/register.html')

            # Check if email already exists
            existing_student = Student.query.filter_by(email=email).first()
            if existing_student:
                flash('Email already registered', 'danger')
                return render_template('student/register.html')

            # Convert interests list to comma-separated string
            interests_str = ','.join(interests) if interests else ''
            print(f"Interests string: {interests_str}")
            
            # Assign a counselor based on interests
            counselor_id = assign_counselor(interests_str)
            print(f"Assigned counselor ID: {counselor_id}")

            # Create new student
            student = Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                dob=dob,
                address=address,
                education_level=education_level,
                interests=interests_str,
                counselor_id=counselor_id,
                is_active=True
            )
            
            # Set password
            student.set_password(password)
            print("Student object created, attempting database save...")

            # Add to database
            db.session.add(student)
            db.session.commit()
            print(f"Student saved to database with ID: {student.id}")

            # Create notification for assigned counselor
            if counselor_id:
                try:
                    notification = Notification(
                        user_id=counselor_id,  # Changed from f"counselor-{counselor_id}"
                        message=f"New student {first_name} {last_name} has been assigned to you based on matching interests.",
                        notification_type='assignment',
                        related_entity_id=student.id
                    )
                    db.session.add(notification)
                    db.session.commit()
                    print("Counselor notification created")
                except Exception as notif_error:
                    print(f"Notification creation error: {notif_error}")
                    # Continue even if notification fails
                    pass

                flash('Registration successful! A counselor matching your interests has been assigned to you.', 'success')
            else:
                flash('Registration successful! A counselor will be assigned to you soon.', 'success')

            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('student/register.html')

    # GET request - show registration form
    return render_template('student/register.html')

@student_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def manage_goals():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')
        target_date_str = request.form.get('target_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date() if target_date_str else None
            
            goal = CareerGoal(
                student_id=current_user.id,
                title=title,
                description=description,
                start_date=start_date,
                target_date=target_date,
                status='not_started'
            )
            db.session.add(goal)
            db.session.commit()
            flash('Career goal added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding career goal', 'danger')
        
        return redirect(url_for('student.manage_goals'))
    
    goals = CareerGoal.query.filter_by(student_id=current_user.id).all()
    return render_template('student/goals.html', goals=goals)

@student_bp.route('/goals/<int:goal_id>/milestones', methods=['GET', 'POST'])
@login_required
def manage_milestones(goal_id):
    goal = CareerGoal.query.filter_by(goal_id=goal_id, student_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        milestone_title = request.form.get('milestone_title')
        due_date_str = request.form.get('due_date')
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            milestone = GoalMilestone(
                goal_id=goal_id,
                milestone_title=milestone_title,
                due_date=due_date,
                status='pending'
            )
            db.session.add(milestone)
            db.session.commit()
            flash('Milestone added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding milestone', 'danger')
        
        return redirect(url_for('student.manage_milestones', goal_id=goal_id))
    
    milestones = GoalMilestone.query.filter_by(goal_id=goal_id).order_by(GoalMilestone.due_date.asc()).all()
    return render_template('student/milestones.html', goal=goal, milestones=milestones)

@student_bp.route('/goals/<int:goal_id>', methods=['PUT', 'DELETE'])
@login_required
def handle_goal(goal_id):
    goal = CareerGoal.query.filter_by(goal_id=goal_id, student_id=current_user.id).first_or_404()
    
    if request.method == 'PUT':
        data = request.get_json()
        goal.status = data.get('status', goal.status)
        goal.title = data.get('title', goal.title)
        goal.description = data.get('description', goal.description)
        if 'target_date' in data:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        
        try:
            db.session.commit()
            return jsonify({
                'id': goal.goal_id,
                'title': goal.title,
                'description': goal.description,
                'status': goal.status,
                'target_date': goal.target_date.isoformat() if goal.target_date else None
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update goal'}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(goal)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete goal'}), 500

@student_bp.route('/milestones/<int:milestone_id>', methods=['PUT', 'DELETE'])
@login_required
def handle_milestone(milestone_id):
    milestone = GoalMilestone.query.join(CareerGoal).filter(
        GoalMilestone.milestone_id == milestone_id,
        CareerGoal.student_id == current_user.id
    ).first_or_404()
    
    if request.method == 'PUT':
        data = request.get_json()
        milestone.status = data.get('status', milestone.status)
        milestone.milestone_title = data.get('title', milestone.milestone_title)
        if 'due_date' in data:
            milestone.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        try:
            db.session.commit()
            return jsonify({
                'id': milestone.milestone_id,
                'title': milestone.milestone_title,
                'status': milestone.status,
                'due_date': milestone.due_date.isoformat() if milestone.due_date else None
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update milestone'}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(milestone)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete milestone'}), 500

@student_bp.route('/student/tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        priority = request.form.get('priority')
        category = request.form.get('category')
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            
            task = Task(
                student_id=current_user.id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                category=category,
                status='Pending'
            )
            db.session.add(task)
            db.session.commit()
            return jsonify({'message': 'Task added successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to add task'}), 500
    
    # GET request - return tasks with filters
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    sort_by = request.args.get('sort_by', 'due_date')

    query = Task.query.filter_by(student_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)
    
    if sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc())
    elif sort_by == 'priority':
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        query = query.order_by(Task.priority.asc())
    elif sort_by == 'created_at':
        query = query.order_by(desc(Task.created_at))
    
    tasks = query.all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    pending_tasks = sum(1 for task in tasks if task.status == 'Pending')
    completed_tasks = sum(1 for task in tasks if task.status == 'Completed')
    due_soon = sum(1 for task in tasks 
                  if task.status == 'Pending' 
                  and task.due_date 
                  and task.due_date <= datetime.now().date() + timedelta(days=3))

    stats = {
        'total': total_tasks,
        'pending': pending_tasks,
        'completed': completed_tasks,
        'due_soon': due_soon
    }

    return jsonify({
        'tasks': [task.to_dict() for task in tasks],
        'stats': stats
    })

@student_bp.route('/student/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def handle_task(task_id):
    task = Task.query.filter_by(task_id=task_id, student_id=current_user.id).first_or_404()
    
    if request.method == 'PUT':
        data = request.get_json()
        task.status = data.get('status', task.status)
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.priority = data.get('priority', task.priority)
        task.category = data.get('category', task.category)
        if 'due_date' in data:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        try:
            db.session.commit()
            return jsonify(task.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update task'}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(task)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete task'}), 500

@student_bp.route('/student/documents', methods=['GET', 'POST'])
@login_required
def manage_documents():
    if request.method == 'POST':
        title = request.form.get('title')
        document_type = request.form.get('document_type')
        file = request.files.get('file')
        
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        try:
            # Save file to appropriate location
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            document = StudentDocument(
                student_id=current_user.id,
                title=title,
                document_type=document_type,
                file_path=file_path
            )
            db.session.add(document)
            db.session.commit()
            
            return jsonify({'message': 'Document uploaded successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to upload document'}), 500
    
    # GET request - return student's documents
    documents = StudentDocument.query.filter_by(student_id=current_user.id).all()
    return jsonify({
        'documents': [{
            'title': doc.title,
            'document_type': doc.document_type,
            'upload_date': doc.upload_date.isoformat(),
            'file_path': doc.file_path
        } for doc in documents]
    })

@student_bp.route('/student/grievances', methods=['GET', 'POST'])
@login_required
def manage_grievances():
    if request.method == 'POST':
        data = request.get_json()
        subject = data.get('subject')
        description = data.get('description')
        
        try:
            grievance = Grievance(
                student_id=current_user.id,
                subject=subject,
                description=description,
                status='Pending'
            )
            db.session.add(grievance)
            db.session.commit()
            
            return jsonify({'message': 'Grievance submitted successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to submit grievance'}), 500
    
    # GET request - return student's grievances
    grievances = Grievance.query.filter_by(student_id=current_user.id).order_by(Grievance.created_at.desc()).all()
    return jsonify({
        'grievances': [{
            'id': g.id,
            'subject': g.subject,
            'description': g.description,
            'status': g.status,
            'response': g.response,
            'created_at': g.created_at.isoformat()
        } for g in grievances]
    })

@student_bp.route('/student/events', methods=['GET'])
@login_required
def view_events():
    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.now().date()
    ).order_by(Event.event_date.asc()).all()
    
    # Get student's registrations
    registrations = {r.event_id: r for r in EventRegistration.query.filter_by(student_id=current_user.id).all()}
    
    return jsonify({
        'events': [{
            'event_id': event.event_id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'event_date': event.event_date.isoformat(),
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'location': event.location,
            'is_online': event.is_online,
            'capacity': event.capacity,
            'registration': bool(registrations.get(event.event_id))
        } for event in upcoming_events]
    })

@student_bp.route('/student/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    existing_registration = EventRegistration.query.filter_by(
        event_id=event_id,
        student_id=current_user.id
    ).first()
    
    if existing_registration:
        return jsonify({'error': 'Already registered for this event'}), 400
    
    # Check event capacity
    current_registrations = EventRegistration.query.filter_by(event_id=event_id).count()
    if current_registrations >= event.capacity:
        return jsonify({'error': 'Event is at full capacity'}), 400
    
    try:
        registration = EventRegistration(
            event_id=event_id,
            student_id=current_user.id
        )
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({'message': 'Successfully registered for event'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to register for event'}), 500

@student_bp.route('/student/messages', methods=['GET', 'POST'])
@login_required
def messages():
    if request.method == 'POST':
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        message_text = data.get('message_text')
        
        try:
            message = Message(
                sender_id=current_user.id,
                recipient_id=recipient_id,
                message_text=message_text
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({'message': 'Message sent successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to send message'}), 500
    
    # GET request - return student's messages
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(recipient_id=current_user.id).all()
    
    return jsonify({
        'messages': [{
            'id': msg.message_id,
            'sender_id': msg.sender_id,
            'recipient_id': msg.recipient_id,
            'message_text': msg.message_text,
            'sent_at': msg.sent_at.isoformat(),
            'is_read': msg.is_read
        } for msg in sorted(sent_messages + received_messages, key=lambda x: x.sent_at, reverse=True)]
    })

@student_bp.route('/student/submit_grievance', methods=['POST'])
@login_required
def submit_grievance():
    subject = request.form.get('subject')
    description = request.form.get('description')
    
    if not subject or not description:
        flash('Please fill in all required fields', 'danger')
        return redirect(url_for('student.dashboard'))
    
    try:
        # Create new grievance
        grievance = Grievance(
            student_id=current_user.id,
            subject=subject,
            description=description,
            status='Pending'
        )
        db.session.add(grievance)
        db.session.commit()
        
        # Create notification for the student
        notification = Notification(
            user_id=current_user.id,
            message=f'Your grievance "{subject}" has been submitted successfully.',
            notification_type='grievance',
            related_entity_id=grievance.id
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Grievance submitted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to submit grievance. Please try again.', 'danger')
    
    return redirect(url_for('student.dashboard'))

@student_bp.route('/student/request_appointment', methods=['POST'])
@login_required
def request_appointment():
    # Get student ID from current_user
    student_id = int(current_user.get_id().split('-')[1])
    counselor_id = current_user.counselor_id
    
    if not counselor_id:
        flash('You need to be assigned a counselor first.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    appointment_type = request.form.get('appointment_type')
    appointment_date = request.form.get('appointment_date')
    start_time = request.form.get('start_time')
    mode = request.form.get('mode')
    notes = request.form.get('notes')
    
    # Validate required fields
    if not all([appointment_type, appointment_date, start_time, mode]):
        flash('Please fill in all required fields', 'danger')
        return redirect(url_for('student.dashboard'))
    
    try:
        # Convert string inputs to proper datetime objects
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time, '%H:%M').time()
        
        # Validate appointment date is not in the past
        if appointment_date < datetime.now().date():
            flash('Cannot schedule appointments in the past', 'danger')
            return redirect(url_for('student.dashboard'))
        
        # Calculate end time (1 hour duration)
        end_time = (datetime.combine(datetime.min, start_time) + timedelta(hours=1)).time()
        
        # Check if counselor is available at this time
        day_of_week = appointment_date.strftime('%A')
        counselor_schedule = CounsellorSchedule.query.filter_by(
            counsellor_id=counselor_id,
            day_of_week=day_of_week
        ).first()
        
        if not counselor_schedule:
            flash('Counselor is not available on this day.', 'danger')
            return redirect(url_for('student.dashboard'))
        
        if (start_time < counselor_schedule.start_time or 
            end_time > counselor_schedule.end_time):
            flash('Selected time is outside counselor\'s working hours.', 'danger')
            return redirect(url_for('student.dashboard'))
        
        # Check for existing appointments at the same time
        existing_appointment = Appointment.query.filter_by(
            counselor_id=counselor_id,
            appointment_date=appointment_date,
            start_time=start_time
        ).first()
        
        if existing_appointment:
            flash('This time slot is already booked. Please choose another time.', 'danger')
            return redirect(url_for('student.dashboard'))
        
        # Create new appointment
        appointment = Appointment(
            student_id=student_id,
            counselor_id=counselor_id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            status='scheduled',
            mode=mode,
            is_free=True  # You can modify this based on your business logic
        )
        
        if mode == 'online':
            # Generate a unique meeting link
            appointment.meeting_link = f"meet.counseling.com/{uuid.uuid4().hex}"
        
        db.session.add(appointment)
        
        # Create notification for both student and counselor
        student_notification = Notification(
            user_id=student_id,
            message=f'Your {appointment_type} appointment has been scheduled for {appointment_date.strftime("%B %d, %Y")} at {start_time.strftime("%I:%M %p")}',
            notification_type='appointment',
            related_entity_id=appointment.id
        )
        db.session.add(student_notification)
        
        # Create notification for counselor
        counselor_notification = Notification(
            user_id=counselor_id,
            message=f'New {appointment_type} appointment scheduled with {current_user.first_name} {current_user.last_name} for {appointment_date.strftime("%B %d, %Y")} at {start_time.strftime("%I:%M %p")}',
            notification_type='appointment',
            related_entity_id=appointment.id
        )
        db.session.add(counselor_notification)
        
        db.session.commit()
        flash('Appointment scheduled successfully!', 'success')
        
    except ValueError as e:
        flash('Invalid date or time format.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash('Failed to schedule appointment. Please try again.', 'danger')
    
    return redirect(url_for('student.dashboard'))

@student_bp.route('/student/dashboard')
@login_required
def dashboard():
    if not current_user.get_id().startswith('student-'):
        flash('Access denied. This dashboard is for students only.', 'danger')
        return redirect(url_for('index'))
    
    # Get unread notifications count
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        read_status=False
    ).count()
    
    # Get career goals and their milestones
    career_goals = CareerGoal.query.filter_by(
        student_id=current_user.id
    ).all()
    
    # Get upcoming milestones
    upcoming_milestones = GoalMilestone.query.join(CareerGoal).filter(
        CareerGoal.student_id == current_user.id,
        GoalMilestone.status == 'pending'
    ).order_by(GoalMilestone.due_date.asc()).limit(5).all()
    
    # Get recent grievances
    recent_grievances = Grievance.query.filter_by(
        student_id=current_user.id
    ).order_by(Grievance.created_at.desc()).limit(5).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.student_id == current_user.id,
        Appointment.appointment_date >= datetime.now().date(),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date.asc(), Appointment.start_time.asc()).all()
    
    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.now().date()
    ).order_by(Event.event_date.asc()).limit(5).all()
    
    # Get event registrations
    event_registrations = {}
    if upcoming_events:
        event_ids = [event.event_id for event in upcoming_events]
        registrations = EventRegistration.query.filter(
            EventRegistration.student_id == current_user.id,
            EventRegistration.event_id.in_(event_ids)
        ).all()
        event_registrations = {r.event_id: r for r in registrations}
    
    return render_template('student/dashboard.html',
                         student=current_user,
                         unread_notifications=unread_notifications,
                         career_goals=career_goals,
                         upcoming_milestones=upcoming_milestones,
                         recent_grievances=recent_grievances,
                         upcoming_appointments=upcoming_appointments,
                         upcoming_events=upcoming_events,
                         event_registrations=event_registrations,
                         today=datetime.now())

@student_bp.route('/student/notifications')
@login_required
def get_notifications():
    # Get recent notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify({
        'notifications': [notification.to_dict() for notification in notifications]
    })

@student_bp.route('/student/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(
        notification_id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    notification.read_status = True
    db.session.commit()
    
    return jsonify({'success': True})

@student_bp.route('/student/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(
        user_id=current_user.id,
        read_status=False
    ).update({'read_status': True})
    
    db.session.commit()
    
    return jsonify({'success': True})

@student_bp.route('/student/notifications/all')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    notification_icons = {
        'appointment': 'fa-calendar-check',
        'resource': 'fa-book',
        'grievance': 'fa-exclamation-circle',
        'payment': 'fa-credit-card',
        'general': 'fa-bell'
    }
    
    return render_template('student/notifications.html',
                         notifications=notifications,
                         notification_icons=notification_icons)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return 'pdf'
    elif ext in ['doc', 'docx']:
        return 'doc'
    elif ext in ['jpg', 'jpeg', 'png']:
        return 'image'
    return 'other'

@student_bp.route('/student/documents/upload', methods=['POST'])
@login_required
def upload_document():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'File type not allowed'}), 400
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create upload folder if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Create document record
        document = StudentDocument(
            student_id=current_user.id,
            title=request.form.get('title'),
            document_type=request.form.get('document_type'),
            file_path=unique_filename,
            file_type=get_file_type(file.filename)
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': {
                'id': document.document_id,
                'title': document.title,
                'document_type': document.document_type,
                'file_type': document.file_type,
                'upload_date': document.upload_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@student_bp.route('/student/documents/<int:doc_id>/download')
@login_required
def download_document(doc_id):
    document = StudentDocument.query.filter_by(
        document_id=doc_id,
        student_id=current_user.id
    ).first_or_404()
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        document.file_path,
        as_attachment=True,
        download_name=f"{document.title}.{document.file_path.rsplit('.', 1)[1]}"
    )

@student_bp.route('/student/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    document = StudentDocument.query.filter_by(
        document_id=doc_id,
        student_id=current_user.id
    ).first_or_404()
    
    try:
        # Delete file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete record
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
