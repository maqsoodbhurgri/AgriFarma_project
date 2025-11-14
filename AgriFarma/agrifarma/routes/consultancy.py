"""Consultancy module routes.
Implements consultant profiles, available slots, booking workflow, dashboards.
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.consultancy import ConsultantProfile, ConsultationSlot, ConsultationBooking, ConsultancyMessage
from agrifarma.forms.consultancy import ConsultantProfileForm, SlotCreateForm, BookingForm, ContactConsultantForm
from agrifarma.utils.decorators import admin_required
from agrifarma.utils.decorators import consultant_required

consultancy_bp = Blueprint('consultancy', __name__)


@consultancy_bp.route('/')
def index():
    """Consultancy landing page with a subset of consultants."""
    consultants = ConsultantProfile.query.filter_by(is_verified=True).order_by(ConsultantProfile.created_at.desc()).limit(6).all()
    return render_template('consultants.html', title='Consultancy Services', consultants=consultants)


@consultancy_bp.route('/consultants')
def consultants():
    """Full consultant listing with optional specialization filter."""
    specialization = request.args.get('specialization', '').strip()
    query = ConsultantProfile.query.filter_by(is_verified=True)
    if specialization:
        like = f"%{specialization}%"
        query = query.filter(ConsultantProfile.specialization.ilike(like))
    consultants = query.order_by(ConsultantProfile.rating.desc()).all()
    return render_template('consultants.html', title='Find Consultants', consultants=consultants, specialization=specialization)


@consultancy_bp.route('/profile/new', methods=['GET', 'POST'])
@login_required
@consultant_required
def create_profile():
    """Create consultant profile for the logged-in consultant user."""
    existing = ConsultantProfile.query.filter_by(user_id=current_user.id).first()
    if existing:
        flash('You already have a consultant profile. You can edit it instead.', 'warning')
        return redirect(url_for('consultancy.edit_profile'))
    form = ConsultantProfileForm()
    if form.validate_on_submit():
        profile = ConsultantProfile(
            user_id=current_user.id,
            specialization=form.specialization.data,
            bio=form.bio.data,
            hourly_rate=form.hourly_rate.data,
            available_online=form.available_online.data,
            is_verified=False,  # Admin can verify later
        )
        db.session.add(profile)
        db.session.commit()
        flash('Consultant profile created and pending verification.', 'success')
        return redirect(url_for('consultancy.consultant_detail', consultant_id=profile.id))
    return render_template('consultancy/create_profile.html', title='Create Consultant Profile', form=form)


@consultancy_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@consultant_required
def edit_profile():
    """Edit existing consultant profile."""
    profile = ConsultantProfile.query.filter_by(user_id=current_user.id).first_or_404()
    form = ConsultantProfileForm(obj=profile)
    if form.validate_on_submit():
        profile.specialization = form.specialization.data
        profile.bio = form.bio.data
        profile.hourly_rate = form.hourly_rate.data
        profile.available_online = form.available_online.data
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('consultancy.consultant_detail', consultant_id=profile.id))
    return render_template('consultancy/edit_profile.html', title='Edit Profile', form=form, profile=profile)


@consultancy_bp.route('/consultant/<int:consultant_id>')
def consultant_detail(consultant_id):
    """Consultant detail page with upcoming available slots."""
    profile = ConsultantProfile.query.get_or_404(consultant_id)
    # Only show future available slots
    now = datetime.utcnow()
    slots = ConsultationSlot.query.filter(
        ConsultationSlot.consultant_profile_id == profile.id,
        ConsultationSlot.start_time >= now,
        ConsultationSlot.status == 'available'
    ).order_by(ConsultationSlot.start_time.asc()).all()
    contact_form = ContactConsultantForm()
    return render_template('consultant_detail.html', title=f'Consultant {profile.user.name}', profile=profile, slots=slots, contact_form=contact_form)


@consultancy_bp.route('/consultant/<int:consultant_id>/contact', methods=['POST'])
@login_required
def contact_consultant(consultant_id):
    """Submit a message to a consultant profile."""
    profile = ConsultantProfile.query.get_or_404(consultant_id)
    form = ContactConsultantForm()
    if form.validate_on_submit():
        msg = ConsultancyMessage(
            consultant_profile_id=profile.id,
            user_id=current_user.id,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent to consultant.', 'success')
    else:
        flash('Please enter a message.', 'danger')
    return redirect(url_for('consultancy.consultant_detail', consultant_id=profile.id))


@consultancy_bp.route('/slot/create', methods=['GET', 'POST'])
@login_required
@consultant_required
def create_slot():
    """Consultant creates an available slot."""
    profile = ConsultantProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Create your consultant profile first.', 'warning')
        return redirect(url_for('consultancy.create_profile'))
    form = SlotCreateForm()
    if form.validate_on_submit():
        # Combine date and times
        start_dt = datetime.combine(form.date.data, form.start_time.data)
        end_dt = start_dt + timedelta(minutes=form.duration_minutes.data)
        # Overlap check
        overlap = ConsultationSlot.query.filter(
            ConsultationSlot.consultant_profile_id == profile.id,
            ConsultationSlot.start_time < end_dt,
            ConsultationSlot.end_time > start_dt,
            ConsultationSlot.status != 'cancelled'
        ).first()
        if overlap:
            flash('Slot overlaps an existing one.', 'danger')
        else:
            slot = ConsultationSlot(
                consultant_profile_id=profile.id,
                start_time=start_dt,
                end_time=end_dt,
                status='available',
                price=form.price.data or profile.hourly_rate,
            )
            db.session.add(slot)
            db.session.commit()
            flash('Slot created.', 'success')
            return redirect(url_for('consultancy.consultant_detail', consultant_id=profile.id))
    return render_template('consultancy/create_slot.html', title='Create Slot', form=form, profile=profile)


@consultancy_bp.route('/slot/<int:slot_id>/book', methods=['GET', 'POST'])
@login_required
def book_slot(slot_id):
    """Book an available slot (farmer/user action)."""
    slot = ConsultationSlot.query.get_or_404(slot_id)
    profile = slot.profile
    if slot.status != 'available':
        flash('Slot is no longer available.', 'warning')
        return redirect(url_for('consultancy.consultant_detail', consultant_id=profile.id))
    form = BookingForm()
    if form.validate_on_submit():
        booking = ConsultationBooking(
            slot_id=slot.id,
            consultant_profile_id=profile.id,
            user_id=current_user.id,
            status='pending',
            notes=form.notes.data,
        )
        slot.status = 'booked'
        db.session.add(booking)
        db.session.commit()
        flash('Consultation booked successfully! Await confirmation.', 'success')
        return redirect(url_for('consultancy.user_bookings'))
    return render_template('consultancy/book_slot.html', title='Book Consultation', form=form, slot=slot, profile=profile)


@consultancy_bp.route('/bookings')
@login_required
def user_bookings():
    """View bookings made by the current user."""
    bookings = ConsultationBooking.query.filter_by(user_id=current_user.id).order_by(ConsultationBooking.created_at.desc()).all()
    return render_template('consultancy/user_bookings.html', title='My Consultation Bookings', bookings=bookings)


@consultancy_bp.route('/dashboard')
@login_required
@consultant_required
def consultant_dashboard():
    """Consultant dashboard: upcoming slots and bookings."""
    profile = ConsultantProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Create your profile to access the dashboard.', 'warning')
        return redirect(url_for('consultancy.create_profile'))
    upcoming_slots = ConsultationSlot.query.filter(
        ConsultationSlot.consultant_profile_id == profile.id,
        ConsultationSlot.start_time >= datetime.utcnow(),
        ConsultationSlot.status == 'available'
    ).order_by(ConsultationSlot.start_time.asc()).all()
    pending_bookings = ConsultationBooking.query.filter_by(consultant_profile_id=profile.id, status='pending').order_by(ConsultationBooking.created_at.desc()).all()
    recent_messages = ConsultancyMessage.query.filter_by(consultant_profile_id=profile.id).order_by(ConsultancyMessage.created_at.desc()).limit(10).all()
    return render_template('consultancy/dashboard.html', title='Consultant Dashboard', profile=profile, upcoming_slots=upcoming_slots, pending_bookings=pending_bookings, recent_messages=recent_messages)


@consultancy_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking (user or consultant)."""
    booking = ConsultationBooking.query.get_or_404(booking_id)
    # Permission check
    if booking.user_id != current_user.id and (not current_user.is_consultant() or booking.consultant_profile_id != getattr(ConsultantProfile.query.filter_by(user_id=current_user.id).first(), 'id', None)) and not current_user.is_admin():
        abort(403)
    if booking.status in ('cancelled', 'completed'):
        flash('Cannot cancel this booking.', 'warning')
        return redirect(request.referrer or url_for('consultancy.user_bookings'))
    booking.status = 'cancelled'
    booking.cancelled_at = datetime.utcnow()
    # Release slot
    slot = booking.slot
    slot.status = 'available'
    db.session.commit()
    flash('Booking cancelled.', 'info')
    return redirect(request.referrer or url_for('consultancy.user_bookings'))


# --- Admin / consultant actions for booking lifecycle (optional minimal) ---
@consultancy_bp.route('/booking/<int:booking_id>/confirm', methods=['POST'])
@login_required
@consultant_required
def confirm_booking(booking_id):
    booking = ConsultationBooking.query.get_or_404(booking_id)
    profile = ConsultantProfile.query.filter_by(user_id=current_user.id).first()
    if booking.consultant_profile_id != profile.id:
        abort(403)
    if booking.status != 'pending':
        flash('Booking cannot be confirmed.', 'warning')
    else:
        booking.status = 'confirmed'
        db.session.commit()
        flash('Booking confirmed.', 'success')
    return redirect(url_for('consultancy.consultant_dashboard'))


@consultancy_bp.route('/booking/<int:booking_id>/complete', methods=['POST'])
@login_required
@consultant_required
def complete_booking(booking_id):
    booking = ConsultationBooking.query.get_or_404(booking_id)
    profile = ConsultantProfile.query.filter_by(user_id=current_user.id).first()
    if booking.consultant_profile_id != profile.id:
        abort(403)
    if booking.status not in ('confirmed', 'pending'):
        flash('Booking cannot be marked complete.', 'warning')
    else:
        booking.status = 'completed'
        booking.completed_at = datetime.utcnow()
        profile.total_sessions = (profile.total_sessions or 0) + 1
        db.session.commit()
        flash('Booking marked completed.', 'success')
    return redirect(url_for('consultancy.consultant_dashboard'))


# -------- Admin management for consultant verification ---------

@consultancy_bp.route('/admin/consultants')
@login_required
@admin_required
def admin_consultants():
    """List all consultant profiles for verification management."""
    profiles = ConsultantProfile.query.order_by(ConsultantProfile.created_at.desc()).all()
    return render_template('consultancy/admin_consultants.html', title='Consultant Profiles', profiles=profiles)


@consultancy_bp.route('/admin/consultant/<int:profile_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_consultant(profile_id):
    profile = ConsultantProfile.query.get_or_404(profile_id)
    profile.is_verified = True
    db.session.commit()
    flash('Consultant verified.', 'success')
    return redirect(request.referrer or url_for('consultancy.admin_consultants'))


@consultancy_bp.route('/admin/consultant/<int:profile_id>/unverify', methods=['POST'])
@login_required
@admin_required
def unverify_consultant(profile_id):
    profile = ConsultantProfile.query.get_or_404(profile_id)
    profile.is_verified = False
    db.session.commit()
    flash('Consultant unverified.', 'warning')
    return redirect(request.referrer or url_for('consultancy.admin_consultants'))

