# Database Migration Guide

## Overview
This guide explains the database migration process for the enhanced User Management system.

## Migration Steps

### Step 1: Generate Migration Script

Run the following command to automatically generate the migration script:

```bash
flask db migrate -m "Enhanced User model with comprehensive profile fields"
```

This will:
- Detect changes in `agrifarma/models/user.py`
- Create a new migration file in `migrations/versions/`
- Generate upgrade() and downgrade() functions

### Step 2: Review Migration Script

The migration script will be created in `migrations/versions/` with a filename like:
`xxxx_enhanced_user_model_with_comprehensive_profile_fields.py`

**Expected changes in the migration:**

#### New Columns to be Added:

```python
# Basic Information
op.add_column('users', sa.Column('name', sa.String(length=100), nullable=False))
op.add_column('users', sa.Column('mobile', sa.String(length=20), nullable=True))
op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))

# Location Information
op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
op.add_column('users', sa.Column('state', sa.String(length=100), nullable=True))
op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))
op.add_column('users', sa.Column('address', sa.Text(), nullable=True))

# Professional Information
op.add_column('users', sa.Column('profession', sa.String(length=50), nullable=True))
op.add_column('users', sa.Column('expertise_level', sa.String(length=20), nullable=True))
op.add_column('users', sa.Column('specialization', sa.String(length=255), nullable=True))
op.add_column('users', sa.Column('qualifications', sa.Text(), nullable=True))
op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

# Profile Media
op.add_column('users', sa.Column('profile_picture', sa.String(length=255), nullable=True))

# Status
op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True))
op.add_column('users', sa.Column('join_date', sa.DateTime(), nullable=False))
op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

# Password Reset
op.add_column('users', sa.Column('reset_token', sa.String(length=100), nullable=True))
op.add_column('users', sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))

# Farmer-specific
op.add_column('users', sa.Column('farm_size', sa.Float(), nullable=True))
op.add_column('users', sa.Column('crops_grown', sa.String(length=255), nullable=True))
op.add_column('users', sa.Column('farming_experience', sa.Integer(), nullable=True))

# Consultant-specific
op.add_column('users', sa.Column('consultation_fee', sa.Float(), nullable=True))

# Vendor-specific
op.add_column('users', sa.Column('business_name', sa.String(length=150), nullable=True))
op.add_column('users', sa.Column('business_license', sa.String(length=100), nullable=True))

# Unique constraints
op.create_unique_constraint('uq_reset_token', 'users', ['reset_token'])
```

#### Potential Columns to be Renamed/Removed:

If your original User model had `full_name` instead of `name`, the migration might include:
```python
# This may appear if renaming columns
# Review carefully and adjust if needed
```

### Step 3: Apply Migration

After reviewing the migration script, apply it:

```bash
flask db upgrade
```

This will:
- Execute the `upgrade()` function
- Add all new columns to the database
- Create unique constraints
- Set default values where specified

### Step 4: Verify Migration

Check if migration was successful:

```bash
# Open SQLite database (for development)
sqlite3 agrifarma.db

# List all columns in users table
.schema users

# Exit
.quit
```

You should see all the new columns listed.

## Handling Existing Data

### Default Values for New Fields:

The migration will set default values for existing users:

- `name`: May need manual update (copy from username or set default)
- `state`: Default = 'Sindh'
- `country`: Default = 'Pakistan'
- `profession`: Default = 'farmer'
- `expertise_level`: Default = 'beginner'
- `join_date`: Will be set to current timestamp for existing users
- `is_verified`: Default = False

### Manual Data Update (if needed):

If you have existing users and need to update their `name` field:

```python
# Open Flask shell
flask shell

# Update all users
from agrifarma.extensions import db
from agrifarma.models.user import User

users = User.query.all()
for user in users:
    if not user.name:
        user.name = user.username  # Or set from full_name if it exists
    db.session.add(user)

db.session.commit()
exit()
```

## Rollback (If Needed)

If something goes wrong, you can rollback the migration:

```bash
# Rollback one step
flask db downgrade

# Or rollback to specific revision
flask db downgrade <revision_id>
```

## Common Migration Issues

### Issue 1: "Column 'name' cannot be NULL"

**Cause:** The `name` field is NOT NULL but existing users don't have a value.

**Solution 1:** Modify migration to allow NULL temporarily:
```python
op.add_column('users', sa.Column('name', sa.String(length=100), nullable=True))
```

Then run update script to set names, then make it NOT NULL:
```python
op.alter_column('users', 'name', nullable=False)
```

**Solution 2:** Add default value in migration:
```python
op.add_column('users', sa.Column('name', sa.String(length=100), 
                                  nullable=False, 
                                  server_default='Unknown'))
```

### Issue 2: "Unique constraint failed: users.reset_token"

**Cause:** Trying to add unique constraint on column with duplicate values.

**Solution:** Ensure all existing users have NULL or unique reset_token before migration.

### Issue 3: Migration file not generated

**Possible causes:**
- Flask-Migrate not installed: `pip install Flask-Migrate`
- No changes detected (models match database)
- SQLALCHEMY_DATABASE_URI not set correctly

**Solution:**
```bash
# Reinstall Flask-Migrate
pip install --upgrade Flask-Migrate

# Initialize migration folder (if first time)
flask db init

# Try migration again
flask db migrate
```

### Issue 4: "Can't locate revision identified by 'xxxxx'"

**Cause:** Migration history mismatch.

**Solution:**
```bash
# Check migration status
flask db current

# See migration history
flask db history

# If corrupted, may need to rebuild migration from scratch
# (Backup your database first!)
```

## Testing After Migration

### 1. Test User Creation:

```python
flask shell

from agrifarma.models.user import User
from agrifarma.models.role import Role
from agrifarma.extensions import db

# Create test user
role = Role.query.filter_by(name='farmer').first()
user = User(
    username='testfarmer',
    name='Test Farmer',
    email='test@example.com',
    mobile='03001234567',
    city='Karachi',
    state='Sindh',
    country='Pakistan',
    profession='farmer',
    expertise_level='intermediate',
    role=role
)
user.set_password('Test123')

db.session.add(user)
db.session.commit()

print(f"User created: {user.name} (ID: {user.id})")
exit()
```

### 2. Test New Fields:

```python
flask shell

from agrifarma.models.user import User

user = User.query.filter_by(username='testfarmer').first()

# Check all new fields
print(f"Name: {user.name}")
print(f"Mobile: {user.mobile}")
print(f"City: {user.city}")
print(f"State: {user.state}")
print(f"Profession: {user.profession}")
print(f"Join Date: {user.join_date}")
print(f"Is Verified: {user.is_verified}")

# Test methods
print(f"Is Farmer: {user.is_farmer()}")

# Test password reset token
token = user.get_reset_token()
print(f"Reset Token: {token}")

# Verify token
verified_user = User.verify_reset_token(token)
print(f"Token Verified: {verified_user.username}")

exit()
```

## Production Migration

### Important Notes for Production:

1. **Backup Database First!**
   ```bash
   # For PostgreSQL
   pg_dump -U username -h localhost database_name > backup_before_migration.sql
   
   # For SQLite
   cp agrifarma.db agrifarma.db.backup
   ```

2. **Schedule Downtime:**
   - Notify users of maintenance window
   - Put application in maintenance mode
   - Run migration during low-traffic period

3. **Test on Staging First:**
   - Always test migration on staging environment
   - Verify all functionality works
   - Check data integrity

4. **Migration Checklist:**
   - [ ] Database backed up
   - [ ] Staging migration successful
   - [ ] Users notified of downtime
   - [ ] Application in maintenance mode
   - [ ] Run `flask db upgrade`
   - [ ] Verify migration success
   - [ ] Test critical functionality
   - [ ] Remove maintenance mode
   - [ ] Monitor for errors

5. **Rollback Plan:**
   - Keep database backup accessible
   - Test rollback procedure on staging
   - Have rollback commands ready:
     ```bash
     flask db downgrade
     # Or restore from backup if needed
     ```

## Migration Script Template

If you need to customize the migration, here's the template structure:

```python
"""Enhanced User model with comprehensive profile fields

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-xx-xx

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'xxxxx'
down_revision = 'yyyyy'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('users', sa.Column('name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('mobile', sa.String(length=20), nullable=True))
    # ... add all other columns
    
    # Update existing data if needed
    # conn = op.get_bind()
    # conn.execute("UPDATE users SET name = username WHERE name IS NULL")
    
    # Add constraints
    op.create_unique_constraint('uq_reset_token', 'users', ['reset_token'])
    
    # Make NOT NULL fields non-nullable (after setting defaults)
    # op.alter_column('users', 'name', nullable=False)


def downgrade():
    # Remove constraints
    op.drop_constraint('uq_reset_token', 'users', type_='unique')
    
    # Remove columns
    op.drop_column('users', 'business_license')
    op.drop_column('users', 'business_name')
    # ... remove all added columns in reverse order
```

## Summary

**Migration adds 23 new fields to User model:**

| Category | Fields | Count |
|----------|--------|-------|
| Basic | name, mobile, phone | 3 |
| Location | city, state, country, address | 4 |
| Professional | profession, expertise_level, specialization, qualifications, bio | 5 |
| Media | profile_picture | 1 |
| Status | is_verified, join_date, last_login | 3 |
| Password Reset | reset_token, reset_token_expiry | 2 |
| Farmer | farm_size, crops_grown, farming_experience | 3 |
| Consultant | consultation_fee | 1 |
| Vendor | business_name, business_license | 2 |
| **Total** | | **24** |

**Next Steps:**
1. Run `flask db migrate`
2. Review generated migration script
3. Backup database (production)
4. Run `flask db upgrade`
5. Verify migration success
6. Test application functionality

---

**Migration Status:** Ready for execution  
**Database Impact:** Medium (adds columns, no data loss)  
**Estimated Downtime:** < 1 minute for small databases
