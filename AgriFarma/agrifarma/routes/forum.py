"""
Forum routes for discussion board functionality.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, desc
from agrifarma.extensions import db
from agrifarma.models.forum import Category, Thread, Reply
from agrifarma.forms.forum import (CategoryForm, ThreadForm, ReplyForm, 
                                   SearchForm, MoveThreadForm, EditThreadForm, EditReplyForm)
from datetime import datetime
import re

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def get_latest_posts(limit=5):
    """Get latest forum posts for sidebar."""
    return Thread.query.filter_by(is_deleted=False).order_by(
        Thread.last_activity.desc()
    ).limit(limit).all()


@forum_bp.route('/')
def index():
    """Forum index page showing all categories and recent threads."""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get all threads (pinned first, then by last activity)
    threads_query = Thread.query.filter_by(is_deleted=False).order_by(
        Thread.is_pinned.desc(), 
        Thread.last_activity.desc()
    )
    
    threads_pagination = threads_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get categories for sidebar
    categories = Category.query.filter_by(
        parent_id=None, 
        is_active=True
    ).order_by(Category.position, Category.name).all()
    
    # Get statistics
    total_threads = Thread.query.filter_by(is_deleted=False).count()
    total_replies = Reply.query.filter_by(is_deleted=False).count()
    latest_posts = get_latest_posts()
    
    return render_template('forum.html',
                         categories=categories,
                         threads=threads_pagination.items,
                         pagination=threads_pagination,
                         total_threads=total_threads,
                         total_replies=total_replies,
                         latest_posts=latest_posts,
                         segment='forum')


@forum_bp.route('/category/<slug>')
def category_detail(slug):
    """View threads in a specific category."""
    category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get threads (pinned first, then by last activity)
    threads_query = Thread.query.filter_by(
        category_id=category.id, 
        is_deleted=False
    ).order_by(Thread.is_pinned.desc(), Thread.last_activity.desc())
    
    threads_pagination = threads_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    latest_posts = get_latest_posts()
    
    return render_template('forum/category_detail.html',
                         category=category,
                         threads=threads_pagination.items,
                         pagination=threads_pagination,
                         latest_posts=latest_posts,
                         segment='forum')


@forum_bp.route('/thread/<int:thread_id>/<slug>')
def thread_detail(thread_id, slug):
    """View a specific thread with its replies."""
    thread = Thread.query.filter_by(id=thread_id, is_deleted=False).first_or_404()
    
    # Increment view count
    thread.increment_views()
    
    # Pagination for replies
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    replies_query = thread.replies.filter_by(is_deleted=False).order_by(Reply.created_at)
    replies_pagination = replies_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Reply form
    form = ReplyForm()
    
    latest_posts = get_latest_posts()
    
    return render_template('forum/thread_detail.html',
                         thread=thread,
                         replies=replies_pagination.items,
                         pagination=replies_pagination,
                         form=form,
                         latest_posts=latest_posts,
                         segment='forum')


@forum_bp.route('/thread/<int:thread_id>/<slug>/reply', methods=['POST'])
@login_required
def post_reply(thread_id, slug):
    """Post a reply to a thread."""
    thread = Thread.query.filter_by(id=thread_id, is_deleted=False).first_or_404()
    
    # Check if thread is locked
    if thread.is_locked:
        flash('This thread is locked. You cannot post replies.', 'warning')
        return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))
    
    form = ReplyForm()
    if form.validate_on_submit():
        reply = Reply(
            content=form.content.data,
            author_id=current_user.id,
            thread_id=thread.id
        )
        
        db.session.add(reply)
        
        # Update thread activity
        thread.update_activity()
        
        db.session.commit()
        
        flash('Your reply has been posted successfully!', 'success')
        
        # Redirect to last page with new reply
        total_replies = thread.get_reply_count()
        per_page = 15
        last_page = (total_replies + per_page - 1) // per_page
        
        return redirect(url_for('forum.thread_detail', 
                              thread_id=thread.id, 
                              slug=thread.slug, 
                              page=last_page) + '#reply-' + str(reply.id))
    
    # If form validation fails, redirect back with errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))


@forum_bp.route('/new-thread', methods=['GET', 'POST'])
@login_required
def new_thread():
    """Create a new discussion thread."""
    form = ThreadForm()
    
    # Populate category choices
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    form.category_id.choices = [(0, 'Select a category...')] + [
        (cat.id, cat.name) for cat in categories
    ]
    
    if form.validate_on_submit():
        # Check if category is locked
        category = Category.query.get(form.category_id.data)
        if category and category.is_locked:
            flash('This category is locked. You cannot create new threads.', 'warning')
            return redirect(url_for('forum.new_thread'))
        
        # Create slug from title
        slug = slugify(form.title.data)
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Thread.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        thread = Thread(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            author_id=current_user.id,
            category_id=form.category_id.data
        )
        
        db.session.add(thread)
        db.session.commit()
        
        flash('Your discussion thread has been created successfully!', 'success')
        return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))
    
    latest_posts = get_latest_posts()
    
    return render_template('forum/new_thread.html',
                         form=form,
                         latest_posts=latest_posts,
                         segment='forum')


@forum_bp.route('/search')
def search():
    """Search forum threads."""
    form = SearchForm(request.args, meta={'csrf': False})
    
    # Populate category choices
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    form.category_id.choices = [(0, 'All Categories')] + [
        (cat.id, cat.name) for cat in categories
    ]
    
    results = []
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = None
    
    if request.args.get('query'):
        query = form.query.data
        category_id = form.category_id.data
        search_in = form.search_in.data
        
        # Build search query
        threads_query = Thread.query.filter_by(is_deleted=False)
        
        # Filter by category
        if category_id and category_id > 0:
            threads_query = threads_query.filter_by(category_id=category_id)
        
        # Search filter
        if search_in == 'title':
            threads_query = threads_query.filter(Thread.title.ilike(f'%{query}%'))
        elif search_in == 'content':
            threads_query = threads_query.filter(Thread.content.ilike(f'%{query}%'))
        else:  # all
            threads_query = threads_query.filter(
                or_(
                    Thread.title.ilike(f'%{query}%'),
                    Thread.content.ilike(f'%{query}%')
                )
            )
        
        # Order by relevance (last activity)
        threads_query = threads_query.order_by(Thread.last_activity.desc())
        
        # Paginate results
        pagination = threads_query.paginate(page=page, per_page=per_page, error_out=False)
        results = pagination.items
    
    latest_posts = get_latest_posts()
    
    return render_template('forum/search.html',
                         form=form,
                         results=results,
                         pagination=pagination,
                         latest_posts=latest_posts,
                         segment='forum')


# ==================== ADMIN/MODERATOR ROUTES ====================

@forum_bp.route('/admin/categories')
@login_required
def manage_categories():
    """Manage forum categories (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    categories = Category.query.order_by(Category.position, Category.name).all()
    
    return render_template('forum/manage_categories.html',
                         categories=categories,
                         segment='forum')


@forum_bp.route('/admin/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create a new category (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    form = CategoryForm()
    
    # Populate parent category choices
    categories = Category.query.order_by(Category.name).all()
    form.parent_id.choices = [(0, 'None (Top Level)')] + [
        (cat.id, cat.name) for cat in categories
    ]
    
    if form.validate_on_submit():
        # Check slug uniqueness
        if Category.query.filter_by(slug=form.slug.data).first():
            flash('A category with this slug already exists.', 'danger')
            return redirect(url_for('forum.create_category'))
        
        category = Category(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data > 0 else None,
            icon=form.icon.data or 'feather icon-folder',
            color=form.color.data,
            position=int(form.position.data) if form.position.data else 0,
            is_active=form.is_active.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{category.name}" has been created successfully!', 'success')
        return redirect(url_for('forum.manage_categories'))
    
    return render_template('forum/category_form.html',
                         form=form,
                         action='Create',
                         segment='forum')


@forum_bp.route('/admin/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit a category (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    # Populate parent category choices (exclude self and descendants)
    categories = Category.query.filter(Category.id != category_id).order_by(Category.name).all()
    form.parent_id.choices = [(0, 'None (Top Level)')] + [
        (cat.id, cat.name) for cat in categories if cat.id != category_id
    ]
    
    if form.validate_on_submit():
        # Check slug uniqueness (exclude current category)
        existing = Category.query.filter_by(slug=form.slug.data).first()
        if existing and existing.id != category_id:
            flash('A category with this slug already exists.', 'danger')
            return redirect(url_for('forum.edit_category', category_id=category_id))
        
        category.name = form.name.data
        category.slug = form.slug.data
        category.description = form.description.data
        category.parent_id = form.parent_id.data if form.parent_id.data > 0 else None
        category.icon = form.icon.data or 'feather icon-folder'
        category.color = form.color.data
        category.position = int(form.position.data) if form.position.data else 0
        category.is_active = form.is_active.data
        
        db.session.commit()
        
        flash(f'Category "{category.name}" has been updated successfully!', 'success')
        return redirect(url_for('forum.manage_categories'))
    
    elif request.method == 'GET':
        # Pre-populate form
        form.parent_id.data = category.parent_id if category.parent_id else 0
        form.position.data = str(category.position)
    
    return render_template('forum/category_form.html',
                         form=form,
                         category=category,
                         action='Edit',
                         segment='forum')


@forum_bp.route('/admin/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete a category (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    category = Category.query.get_or_404(category_id)
    
    # Check if category has threads
    if category.get_thread_count() > 0:
        flash('Cannot delete category with existing threads. Move or delete threads first.', 'danger')
        return redirect(url_for('forum.manage_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Category "{category.name}" has been deleted.', 'success')
    return redirect(url_for('forum.manage_categories'))


@forum_bp.route('/admin/thread/<int:thread_id>/delete', methods=['POST'])
@login_required
def delete_thread(thread_id):
    """Delete (soft delete) a thread (admin/author only)."""
    thread = Thread.query.get_or_404(thread_id)
    
    # Check permissions
    if not (current_user.is_admin() or thread.author_id == current_user.id):
        abort(403)
    
    thread.soft_delete()
    
    flash('Thread has been deleted.', 'success')
    return redirect(url_for('forum.category_detail', slug=thread.category.slug))


@forum_bp.route('/admin/thread/<int:thread_id>/move', methods=['GET', 'POST'])
@login_required
def move_thread(thread_id):
    """Move a thread to a different category (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    thread = Thread.query.get_or_404(thread_id)
    form = MoveThreadForm()
    
    # Populate category choices
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    form.category_id.choices = [(cat.id, cat.name) for cat in categories]
    
    if form.validate_on_submit():
        old_category = thread.category
        thread.category_id = form.category_id.data
        db.session.commit()
        
        flash(f'Thread moved from "{old_category.name}" to "{thread.category.name}".', 'success')
        return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))
    
    elif request.method == 'GET':
        form.category_id.data = thread.category_id
    
    return render_template('forum/move_thread.html',
                         form=form,
                         thread=thread,
                         segment='forum')


@forum_bp.route('/admin/thread/<int:thread_id>/toggle-pin', methods=['POST'])
@login_required
def toggle_pin_thread(thread_id):
    """Pin/unpin a thread (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    thread = Thread.query.get_or_404(thread_id)
    thread.is_pinned = not thread.is_pinned
    db.session.commit()
    
    status = 'pinned' if thread.is_pinned else 'unpinned'
    flash(f'Thread has been {status}.', 'success')
    
    return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))


@forum_bp.route('/admin/thread/<int:thread_id>/toggle-lock', methods=['POST'])
@login_required
def toggle_lock_thread(thread_id):
    """Lock/unlock a thread (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    thread = Thread.query.get_or_404(thread_id)
    thread.is_locked = not thread.is_locked
    db.session.commit()
    
    status = 'locked' if thread.is_locked else 'unlocked'
    flash(f'Thread has been {status}.', 'success')
    
    return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))


@forum_bp.route('/admin/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(reply_id):
    """Delete (soft delete) a reply (admin/author only)."""
    reply = Reply.query.get_or_404(reply_id)
    
    # Check permissions
    if not (current_user.is_admin() or reply.author_id == current_user.id):
        abort(403)
    
    thread = reply.thread
    reply.soft_delete()
    
    flash('Reply has been deleted.', 'success')
    return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug))


@forum_bp.route('/reply/<int:reply_id>/mark-solution', methods=['POST'])
@login_required
def mark_solution(reply_id):
    """Mark a reply as the solution (thread author or admin only)."""
    reply = Reply.query.get_or_404(reply_id)
    thread = reply.thread
    
    # Check permissions (thread author or admin)
    if not (current_user.is_admin() or thread.author_id == current_user.id):
        abort(403)
    
    reply.mark_as_solution()
    
    flash('Reply has been marked as the solution!', 'success')
    return redirect(url_for('forum.thread_detail', thread_id=thread.id, slug=thread.slug) + f'#reply-{reply.id}')
