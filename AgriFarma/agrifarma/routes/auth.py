"""
Authentication routes for login, registration, and logout.
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from agrifarma.extensions import db, login_manager
from agrifarma.models.user import User
from agrifarma.models.role import Role
from agrifarma.forms.auth import (LoginForm, RegisterForm, ForgotPasswordForm, 
                                  ResetPasswordForm, ChangePasswordForm)
from agrifarma.forms.profile import EditProfileForm

auth_bp = Blueprint('auth', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_profile_picture(file):
    """Save uploaded profile picture and return filename."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to make filename unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check if input is email or username
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username/email or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Update last login
        user.update_last_login()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page or role-specific dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')  # Changed from main.index to dashboard
        
        flash(f'Welcome back, {user.name or user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form, segment='login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Get or create the role
        role = Role.query.filter_by(name=form.role.data).first()
        if not role:
            role = Role(name=form.role.data)
            db.session.add(role)
            db.session.flush()
        
        # Create new user
        user = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data,
            mobile=form.mobile.data,
            city=form.city.data,
            state=form.state.data or 'Sindh',
            country=form.country.data or 'Pakistan',
            address=form.address.data,
            profession=form.profession.data,
            expertise_level=form.expertise_level.data,
            specialization=form.specialization.data,
            bio=form.bio.data,
            role_id=role.id,
            is_active=True,
            is_verified=False,
            join_date=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        # Set role-specific fields
        if form.role.data == 'farmer':
            try:
                user.farm_size = float(form.farm_size.data) if form.farm_size.data else None
            except ValueError:
                user.farm_size = None
            user.crops_grown = form.crops_grown.data
            try:
                user.farming_experience = int(form.farming_experience.data) if form.farming_experience.data else None
            except ValueError:
                user.farming_experience = None
        elif form.role.data == 'consultant':
            user.qualifications = form.qualifications.data
            try:
                user.consultation_fee = float(form.consultation_fee.data) if form.consultation_fee.data else None
            except ValueError:
                user.consultation_fee = None
        elif form.role.data == 'vendor':
            user.business_name = form.business_name.data
            user.business_license = form.business_license.data
        
        # Save optional profile picture (guard for older form versions)
        pp_field = getattr(form, 'profile_picture', None)
        if pp_field and pp_field.data:
            filename = save_profile_picture(pp_field.data)
            if filename:
                user.profile_picture = filename
                user.profile_image = filename
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in to continue.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form, segment='register')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile view route with aggregated user stats and latest posts."""
    from agrifarma.models.blog import BlogPost, BlogLike
    from agrifarma.models.forum import Thread, Reply

    # Aggregated metrics
    post_count = BlogPost.query.filter_by(author_id=current_user.id, is_deleted=False).count()
    like_count = BlogLike.query.filter_by(user_id=current_user.id).count()
    forum_threads = Thread.query.filter_by(author_id=current_user.id, is_deleted=False).count()
    forum_replies = Reply.query.filter_by(author_id=current_user.id, is_deleted=False).count()

    # Latest authored content
    latest_blog_posts = BlogPost.query.filter_by(author_id=current_user.id, is_deleted=False) \
        .order_by(BlogPost.published_at.desc().nullslast(), BlogPost.created_at.desc()).limit(5).all()
    latest_threads = Thread.query.filter_by(author_id=current_user.id, is_deleted=False) \
        .order_by(Thread.last_activity.desc()).limit(5).all()

    return render_template(
        'home/profile.html',
        user=current_user,
        segment='profile',
        post_count=post_count,
        like_count=like_count,
        forum_threads=forum_threads,
        forum_replies=forum_replies,
        latest_blog_posts=latest_blog_posts,
        latest_threads=latest_threads,
    )


@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile route."""
    form = EditProfileForm()
    
    if form.validate_on_submit():
        # Update basic information
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.mobile = form.mobile.data
        current_user.phone = form.phone.data
        
        # Update location
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.country = form.country.data
        current_user.address = form.address.data
        
        # Update professional info
        current_user.profession = form.profession.data
        current_user.expertise_level = form.expertise_level.data
        current_user.specialization = form.specialization.data
        current_user.bio = form.bio.data
        current_user.qualifications = form.qualifications.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            filename = save_profile_picture(form.profile_picture.data)
            if filename:
                current_user.profile_picture = filename
                current_user.profile_image = filename  # Keep both for compatibility
        
        # Update role-specific fields
        if current_user.is_farmer():
            try:
                current_user.farm_size = float(form.farm_size.data) if form.farm_size.data else None
            except ValueError:
                current_user.farm_size = None
            current_user.crops_grown = form.crops_grown.data
            try:
                current_user.farming_experience = int(form.farming_experience.data) if form.farming_experience.data else None
            except ValueError:
                current_user.farming_experience = None
        elif current_user.is_consultant():
            try:
                current_user.consultation_fee = float(form.consultation_fee.data) if form.consultation_fee.data else None
            except ValueError:
                current_user.consultation_fee = None
        elif current_user.is_vendor():
            current_user.business_name = form.business_name.data
            current_user.business_license = form.business_license.data
        
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        # Pre-populate form with current user data
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.mobile.data = current_user.mobile
        form.phone.data = current_user.phone
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.country.data = current_user.country
        form.address.data = current_user.address
        form.profession.data = current_user.profession
        form.expertise_level.data = current_user.expertise_level
        form.specialization.data = current_user.specialization
        form.bio.data = current_user.bio
        form.qualifications.data = current_user.qualifications
        
        # Role-specific fields
        if current_user.is_farmer():
            form.farm_size.data = str(current_user.farm_size) if current_user.farm_size else ''
            form.crops_grown.data = current_user.crops_grown
            form.farming_experience.data = str(current_user.farming_experience) if current_user.farming_experience else ''
        elif current_user.is_consultant():
            form.consultation_fee.data = str(current_user.consultation_fee) if current_user.consultation_fee else ''
        elif current_user.is_vendor():
            form.business_name.data = current_user.business_name
            form.business_license.data = current_user.business_license
    
    return render_template('home/edit_profile.html', form=form, segment='edit_profile')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('home/change_password.html', form=form, segment='change_password')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_token()
            # TODO: Send email with reset link
            # For now, just show success message
            flash(f'Password reset instructions have been sent to {form.email.data}. '
                  f'Reset token: {token}', 'info')
        else:
            # Don't reveal if email exists or not
            flash(f'If an account exists with {form.email.data}, '
                  'password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('accounts/forgot_password.html', form=form, segment='forgot_password')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        
        flash('Your password has been reset successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('accounts/reset_password.html', form=form, segment='reset_password')
