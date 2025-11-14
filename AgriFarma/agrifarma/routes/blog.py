"""
Blog routes for knowledge base functionality.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from agrifarma.extensions import db
from agrifarma.models.blog import BlogPost, BlogCategory, BlogComment, BlogLike, BlogAttachment
from agrifarma.forms.blog import BlogPostForm, BlogCommentForm, BlogCategoryForm, BlogSearchForm
from datetime import datetime
import os
import re

blog_bp = Blueprint('blog', __name__)


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


@blog_bp.route('/')
def index():
    """Blog homepage route."""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get published posts
    posts_query = BlogPost.query.filter_by(
        is_published=True, 
        is_deleted=False
    ).order_by(BlogPost.published_at.desc())
    
    # Filter by category if provided
    category_slug = request.args.get('category')
    if category_slug:
        category = BlogCategory.query.filter_by(slug=category_slug).first_or_404()
        posts_query = posts_query.filter_by(category_id=category.id)
    
    posts_pagination = posts_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get categories for sidebar
    categories = BlogCategory.query.filter_by(is_active=True).order_by(BlogCategory.name).all()
    
    # Get featured posts
    featured_posts = BlogPost.query.filter_by(
        is_published=True,
        is_featured=True,
        is_deleted=False
    ).order_by(BlogPost.published_at.desc()).limit(3).all()
    
    return render_template('blogs.html',
                         posts=posts_pagination,
                         categories=categories,
                         featured_posts=featured_posts,
                         title='Knowledge Base',
                         segment='blog')


@blog_bp.route('/post/<int:post_id>/<slug>')
def post_detail(post_id, slug):
    """View blog post route."""
    post = BlogPost.query.filter_by(id=post_id, is_deleted=False).first_or_404()
    
    # Check if published (unless author or admin)
    if not post.is_published:
        if not current_user.is_authenticated or (current_user.id != post.author_id and not current_user.is_admin()):
            abort(404)
    
    # Increment view count
    post.increment_views()
    
    # Get comments
    comments = post.comments.filter_by(is_deleted=False, is_approved=True).all()
    
    # Comment form
    form = BlogCommentForm()
    
    # Get related posts
    related_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.category_id == post.category_id,
        BlogPost.is_published == True,
        BlogPost.is_deleted == False
    ).order_by(BlogPost.published_at.desc()).limit(3).all()
    
    # Check if user liked this post
    user_liked = False
    if current_user.is_authenticated:
        user_liked = BlogLike.query.filter_by(
            user_id=current_user.id,
            post_id=post.id
        ).first() is not None
    
    return render_template('blog_detail.html',
                         post=post,
                         comments=comments,
                         form=form,
                         comment_form=form,
                         related_posts=related_posts,
                         user_liked=user_liked,
                         user_has_liked=user_liked,
                         title=post.title,
                         segment='blog')


@blog_bp.route('/post/<int:post_id>/<slug>/comment', methods=['POST'])
@login_required
def add_comment(post_id, slug):
    """Add comment to blog post."""
    post = BlogPost.query.get_or_404(post_id)
    form = BlogCommentForm()
    
    if form.validate_on_submit():
        comment = BlogComment(
            content=form.content.data,
            author_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        
        flash('Your comment has been posted!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('blog.post_detail', post_id=post.id, slug=post.slug))


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new blog post route."""
    # All authenticated users can create posts
    # Removed restriction - now open to all users
    
    form = BlogPostForm()
    
    # Populate category choices
    categories = BlogCategory.query.filter_by(is_active=True).order_by(BlogCategory.name).all()
    form.category_id.choices = [(0, 'Select a category...')] + [
        (cat.id, cat.name) for cat in categories
    ]
    
    if form.validate_on_submit():
        # Create slug from title
        slug = slugify(form.title.data)
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        post = BlogPost(
            title=form.title.data,
            slug=slug,
            excerpt=form.excerpt.data,
            content=form.content.data,
            author_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data else None,
            tags=form.tags.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            is_featured=form.is_featured.data
        )
        
        # Ensure upload folder exists
        upload_folder = os.path.join('static', 'uploads', 'blog')
        os.makedirs(upload_folder, exist_ok=True)

        # Handle featured image upload
        if form.featured_image.data and hasattr(form.featured_image.data, 'filename'):
            file = form.featured_image.data
            if file.filename:  # Check if actually a file with filename
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                post.featured_image = f'uploads/blog/{filename}'

        # Handle attachments (multiple)
        files = request.files.getlist('attachments')
        for f in files:
            if not f or f.filename == '':
                continue
            fname = secure_filename(f.filename)
            # Prefix timestamp to reduce collisions
            ts = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            name, ext = os.path.splitext(fname)
            fname_ts = f"{name}_{ts}{ext}"
            fpath = os.path.join(upload_folder, fname_ts)
            try:
                f.save(fpath)
            except Exception:
                continue
            rel_path = f'uploads/blog/{fname_ts}'
            try:
                size = os.path.getsize(fpath)
            except Exception:
                size = None
            attach = BlogAttachment(
                post=post,
                file_path=rel_path,
                mime_type=f.mimetype,
                original_name=f.filename,
                file_size=size
            )
            db.session.add(attach)
        
        # Publish if requested
        if form.is_published.data:
            post.publish()
        
        db.session.add(post)
        db.session.commit()
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('blog.post_detail', post_id=post.id, slug=post.slug))
    
    return render_template('blog/create_post.html',
                         form=form,
                         title='Create Post',
                         segment='blog')


@blog_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit blog post route."""
    post = BlogPost.query.get_or_404(post_id)
    
    # Only author or admin can edit
    if current_user.id != post.author_id and not current_user.is_admin():
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('blog.post_detail', post_id=post.id, slug=post.slug))
    
    form = BlogPostForm(obj=post)
    
    # Populate category choices
    categories = BlogCategory.query.filter_by(is_active=True).order_by(BlogCategory.name).all()
    form.category_id.choices = [(0, 'Select a category...')] + [
        (cat.id, cat.name) for cat in categories
    ]
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.excerpt = form.excerpt.data
        post.content = form.content.data
        post.category_id = form.category_id.data if form.category_id.data else None
        post.tags = form.tags.data
        post.meta_description = form.meta_description.data
        post.meta_keywords = form.meta_keywords.data
        post.is_featured = form.is_featured.data
        
        # Update slug if title changed
        new_slug = slugify(form.title.data)
        if new_slug != post.slug:
            base_slug = new_slug
            counter = 1
            while BlogPost.query.filter(BlogPost.slug==new_slug, BlogPost.id!=post.id).first():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = new_slug
        
        # Handle featured image upload
        if form.featured_image.data and hasattr(form.featured_image.data, 'filename'):
            upload_folder = os.path.join('static', 'uploads', 'blog')
            os.makedirs(upload_folder, exist_ok=True)
            file = form.featured_image.data
            if file.filename:  # Check if actually a file with filename
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                post.featured_image = f'uploads/blog/{filename}'
        
        # Publish if requested
        if form.is_published.data and not post.is_published:
            post.publish()
        elif not form.is_published.data and post.is_published:
            post.unpublish()
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('blog.post_detail', post_id=post.id, slug=post.slug))
    
    # Pre-populate form
    form.category_id.data = post.category_id
    form.is_published.data = post.is_published
    
    return render_template('blog/edit_post.html',
                         form=form,
                         post=post,
                         title='Edit Post',
                         segment='blog')


@blog_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete blog post route."""
    post = BlogPost.query.get_or_404(post_id)
    
    # Only author or admin can delete
    if current_user.id != post.author_id and not current_user.is_admin():
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('blog.post_detail', post_id=post.id, slug=post.slug))
    
    post.soft_delete()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('blog.index'))


@blog_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like/unlike a blog post."""
    post = BlogPost.query.get_or_404(post_id)
    
    # Check if already liked
    existing_like = BlogLike.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        post.like_count -= 1
        message = 'Post unliked.'
    else:
        # Like
        like = BlogLike(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        post.like_count += 1
        message = 'Post liked!'
    
    db.session.commit()
    flash(message, 'success')
    
    return redirect(url_for('blog.post_detail', post_id=post.id, slug=post.slug))


@blog_bp.route('/search')
def search():
    """Search blog posts."""
    form = BlogSearchForm(request.args, meta={'csrf': False})
    
    # Populate category choices
    categories = BlogCategory.query.filter_by(is_active=True).order_by(BlogCategory.name).all()
    form.category_id.choices = [(0, 'All Categories')] + [
        (cat.id, cat.name) for cat in categories
    ]
    
    results = []
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = None
    
    if request.args.get('query'):
        query = form.query.data
        category_id = form.category_id.data
        
        # Build search query
        posts_query = BlogPost.query.filter_by(is_published=True, is_deleted=False)
        
        # Filter by category
        if category_id and category_id > 0:
            posts_query = posts_query.filter_by(category_id=category_id)
        
        # Search in title, excerpt, and content
        posts_query = posts_query.filter(
            db.or_(
                BlogPost.title.ilike(f'%{query}%'),
                BlogPost.excerpt.ilike(f'%{query}%'),
                BlogPost.content.ilike(f'%{query}%'),
                BlogPost.tags.ilike(f'%{query}%')
            )
        )
        
        # Order by relevance (published date)
        posts_query = posts_query.order_by(BlogPost.published_at.desc())
        
        # Paginate results
        pagination = posts_query.paginate(page=page, per_page=per_page, error_out=False)
        results = pagination.items
    
    return render_template('blog/search.html',
                         form=form,
                         results=results,
                         pagination=pagination,
                         title='Search Blog',
                         segment='blog')


# ==================== ADMIN ROUTES ====================

@blog_bp.route('/admin/categories')
@login_required
def manage_categories():
    """Manage blog categories (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    categories = BlogCategory.query.order_by(BlogCategory.position, BlogCategory.name).all()
    
    return render_template('blog/manage_categories.html',
                         categories=categories,
                         title='Manage Categories',
                         segment='blog')


@blog_bp.route('/admin/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new blog category (admin only)."""
    if not current_user.is_admin():
        abort(403)
    
    form = BlogCategoryForm()
    
    if form.validate_on_submit():
        category = BlogCategory(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            icon=form.icon.data,
            color=form.color.data,
            position=int(form.position.data) if form.position.data else 0,
            is_active=form.is_active.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('blog.manage_categories'))
    
    return render_template('blog/category_form.html',
                         form=form,
                         title='Create Category',
                         segment='blog')


# ==================== MODERATION ROUTES ====================

@blog_bp.route('/admin/posts')
@login_required
def manage_posts():
    """List and manage blog posts (admin only)."""
    if not current_user.is_admin():
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = 20

    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('blog/manage_posts.html',
                           posts=posts,
                           title='Manage Posts',
                           segment='blog')


@blog_bp.route('/admin/post/<int:post_id>/publish', methods=['POST'])
@login_required
def admin_publish_post(post_id):
    if not current_user.is_admin():
        abort(403)
    post = BlogPost.query.get_or_404(post_id)
    post.publish()
    flash('Post published.', 'success')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/post/<int:post_id>/unpublish', methods=['POST'])
@login_required
def admin_unpublish_post(post_id):
    if not current_user.is_admin():
        abort(403)
    post = BlogPost.query.get_or_404(post_id)
    post.unpublish()
    flash('Post unpublished.', 'warning')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    if not current_user.is_admin():
        abort(403)
    post = BlogPost.query.get_or_404(post_id)
    post.soft_delete()
    flash('Post moved to trash.', 'warning')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/post/<int:post_id>/restore', methods=['POST'])
@login_required
def admin_restore_post(post_id):
    if not current_user.is_admin():
        abort(403)
    post = BlogPost.query.get_or_404(post_id)
    post.restore()
    flash('Post restored.', 'success')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def admin_approve_comment(comment_id):
    if not current_user.is_admin():
        abort(403)
    comment = BlogComment.query.get_or_404(comment_id)
    comment.approve()
    flash('Comment approved.', 'success')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/comment/<int:comment_id>/unapprove', methods=['POST'])
@login_required
def admin_unapprove_comment(comment_id):
    if not current_user.is_admin():
        abort(403)
    comment = BlogComment.query.get_or_404(comment_id)
    comment.unapprove()
    flash('Comment unapproved.', 'warning')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def admin_delete_comment(comment_id):
    if not current_user.is_admin():
        abort(403)
    comment = BlogComment.query.get_or_404(comment_id)
    comment.soft_delete()
    flash('Comment deleted.', 'warning')
    return redirect(request.referrer or url_for('blog.manage_posts'))


@blog_bp.route('/admin/comment/<int:comment_id>/restore', methods=['POST'])
@login_required
def admin_restore_comment(comment_id):
    if not current_user.is_admin():
        abort(403)
    comment = BlogComment.query.get_or_404(comment_id)
    comment.restore()
    flash('Comment restored.', 'success')
    return redirect(request.referrer or url_for('blog.manage_posts'))
