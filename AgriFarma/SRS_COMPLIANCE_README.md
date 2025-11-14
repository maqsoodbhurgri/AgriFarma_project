# SRS Compliance Checker for AgriFarma

An automated Flask-based tool that scans the AgriFarma project to detect implemented features and generates compliance reports against the full Software Requirements Specification (SRS) checklist.

## Features

### 🔍 Automated Detection
- **Route Scanning**: Detects all Flask route decorators in the `routes/` directory
- **Template Detection**: Finds all HTML templates in the `templates/` directory
- **Model Discovery**: Identifies SQLAlchemy model classes in the `models/` directory
- **Keyword Analysis**: Searches for specific code patterns and functions

### 📊 Compliance Reporting
- **Module-Level Status**: Shows completion percentage for each major module
  - Authentication & Authorization
  - Community Forum
  - Blog & Knowledge Base
  - Expert Consultancy
  - E-Commerce Marketplace
  - Admin Panel
  - Analytics & Reporting
  - Notifications System
  - Search Functionality

- **Requirement-Level Tracking**: Detailed status for each individual requirement
  - ✅ **Completed**: All components implemented (100%)
  - 🔧 **Partial**: Some components implemented (50-99%)
  - ❌ **Missing**: No components found (<50%)

### 🎯 Dashboard Features
- Real-time progress bars for each module
- Detailed breakdown of routes, templates, models, and keywords
- Manual override capability for admin users
- Export reports as JSON or HTML
- Color-coded status indicators

## Installation & Setup

### 1. Database Migration
Create the SRS compliance tracking tables:

```powershell
.\venv\Scripts\flask.exe migrate-srs-tables
```

### 2. Generate Initial Report
Run the scanner to see current compliance status:

```powershell
.\venv\Scripts\flask.exe generate-srs-report
```

## Usage

### Access the Dashboard
Navigate to the admin SRS compliance dashboard:

```
http://127.0.0.1:5000/admin/srs-status
```

**Requirements**: 
- Must be logged in as an admin user
- Admin role required (`@admin_required` decorator)

### Dashboard Features

#### 1. Overview Cards
- **Overall Completion**: Total percentage across all modules
- **Requirements Done**: Completed vs. total requirements
- **Partial Features**: Number of partially implemented features
- **Missing Features**: Not yet implemented features

#### 2. Module Details
Each module shows:
- Priority level (Critical, High, Medium)
- Completion percentage with progress bar
- List of all requirements with individual status
- Detected routes, templates, and models

#### 3. Manual Overrides
Click the edit button (✏️) on any requirement to:
- Override automatic detection status
- Add notes explaining implementation details
- Mark features as complete even if not auto-detected

#### 4. Export Reports
- **JSON Export**: Machine-readable format for CI/CD integration
- **HTML Export**: Standalone HTML file for sharing

## SRS Checklist Structure

The compliance checker uses `srs_checklist.json` which defines:

```json
{
  "version": "1.0.0",
  "modules": [
    {
      "id": "auth",
      "name": "Authentication & Authorization",
      "priority": "critical",
      "requirements": [
        {
          "id": "auth-001",
          "name": "User Registration",
          "routes": ["/register"],
          "templates": ["accounts/register.html"],
          "models": ["User"],
          "keywords": ["RegisterForm", "db.session.add"]
        }
      ]
    }
  ]
}
```

### Adding New Requirements

1. Edit `srs_checklist.json`
2. Add module or requirement with appropriate criteria
3. Regenerate report to see new items

## API Reference

### Scanner Class

```python
from agrifarma.utils.srs_scanner import create_scanner

# Create scanner instance
scanner = create_scanner('/path/to/project')

# Scan project components
routes = scanner.scan_routes()
templates = scanner.scan_templates()
models = scanner.scan_models()
keywords = scanner.scan_keywords(['login_required', 'db.session'])

# Generate full report
report = scanner.generate_report()

# Export to file
scanner.export_report(output_path='report.json', format='json')
scanner.export_report(output_path='report.html', format='html')
```

### Report Structure

```python
{
  "generated_at": "2025-11-11T12:50:00",
  "version": "1.0.0",
  "summary": {
    "total_modules": 9,
    "completed_modules": 0,
    "partial_modules": 7,
    "missing_modules": 2,
    "total_requirements": 46,
    "completed_requirements": 6,
    "partial_requirements": 31,
    "missing_requirements": 9,
    "overall_completion": 13
  },
  "modules": [
    {
      "id": "auth",
      "name": "Authentication & Authorization",
      "priority": "critical",
      "completion": 96,
      "status": "partial",
      "requirements": [...]
    }
  ]
}
```

## CLI Commands

### Generate Report
```powershell
.\venv\Scripts\flask.exe generate-srs-report
```

Output:
```
============================================================
  📊 SRS COMPLIANCE REPORT
============================================================

Overall Completion: 13%
Completed Requirements: 6/46
Partial Requirements: 31
Missing Requirements: 9

------------------------------------------------------------
⚠ Authentication & Authorization: 96% (PARTIAL)
⚠ Community Forum: 55% (PARTIAL)
⚠ Blog & Knowledge Base: 78% (PARTIAL)
...
```

### Create Migration Tables
```powershell
.\venv\Scripts\flask.exe migrate-srs-tables
```

## Testing

Run the compliance scanner test suite:

```powershell
.\venv\Scripts\python.exe -m pytest tests\test_srs_compliance.py -v
```

### Test Coverage
- Scanner initialization
- Route detection
- Template scanning
- Model discovery
- Keyword analysis
- Requirement checking
- Report generation
- Export functionality
- Caching mechanisms

## Manual Override System

### Database Models

**SRSModule**: Tracks module-level overrides
- `module_id`: Unique module identifier
- `override_status`: Manual status (completed/partial/missing)
- `notes`: Admin notes
- `updated_by_id`: User who made the change

**SRSRequirement**: Tracks requirement-level overrides
- `requirement_id`: Unique requirement identifier
- `module_id`: Parent module
- `override_status`: Manual status
- `notes`: Implementation details

### Using Overrides

1. Navigate to `/admin/srs-status`
2. Click edit button on any module or requirement
3. Select override status or leave blank for auto-detection
4. Add notes explaining the manual override
5. Submit to save

Overrides are displayed with a special icon (✏️) in the dashboard.

## Integration with CI/CD

### Example GitHub Actions Workflow

```yaml
name: SRS Compliance Check

on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Generate compliance report
        run: |
          flask generate-srs-report
      
      - name: Export JSON report
        run: |
          python -c "from agrifarma.utils.srs_scanner import create_scanner; s = create_scanner('.'); s.export_report('compliance.json', 'json')"
      
      - name: Upload report artifact
        uses: actions/upload-artifact@v2
        with:
          name: srs-compliance-report
          path: compliance.json
```

## Priority Levels

- **Critical**: Core functionality required for MVP
  - Authentication
  - E-Commerce checkout
  
- **High**: Important features for user engagement
  - Forum
  - Blog
  - Consultancy
  - Admin panel

- **Medium**: Nice-to-have features
  - Analytics
  - Advanced search

## Current Status (As of Nov 11, 2025)

| Module | Completion | Status |
|--------|-----------|--------|
| Authentication & Authorization | 96% | ⚠ Partial |
| Community Forum | 55% | ⚠ Partial |
| Blog & Knowledge Base | 78% | ⚠ Partial |
| Expert Consultancy | 64% | ⚠ Partial |
| E-Commerce Marketplace | 54% | ⚠ Partial |
| Admin Panel | 59% | ⚠ Partial |
| Analytics & Reporting | 34% | ❌ Missing |
| Notifications System | 0% | ❌ Missing |
| Search Functionality | 77% | ⚠ Partial |

**Overall: 13% Complete** (6/46 requirements fully implemented)

## Roadmap

### Phase 1: Complete Core Features (Priority: Critical)
- [ ] Implement shopping cart persistence
- [ ] Add payment gateway integration
- [ ] Complete checkout workflow

### Phase 2: Enhance Community Features (Priority: High)
- [ ] Forum advanced moderation UI
- [ ] Blog multimedia galleries
- [ ] Consultancy booking system

### Phase 3: Admin & Analytics (Priority: Medium)
- [ ] Sales analytics dashboard
- [ ] User analytics tracking
- [ ] Product performance reports

### Phase 4: Notifications & Search (Priority: Medium)
- [ ] In-app notification system
- [ ] Email notification templates
- [ ] Global search with filters

## Troubleshooting

### Scanner Not Finding Routes
**Issue**: Routes exist but scanner reports 0 routes found

**Solution**: 
- Ensure route files are in `agrifarma/routes/` directory
- Check that routes use proper decorator syntax: `@blueprint.route('/path')`
- Verify Python files are not in `__pycache__` or other excluded directories

### Templates Not Detected
**Issue**: HTML files exist but not detected

**Solution**:
- Templates must be in `templates/` directory
- Use forward slashes in paths (e.g., `accounts/login.html`)
- Check file extensions are `.html`

### Models Missing
**Issue**: SQLAlchemy models not found

**Solution**:
- Models must be in `agrifarma/models/` directory
- Class definitions must use proper syntax: `class ModelName(`
- Import models in `app.py` to ensure they're registered

## Contributing

To add new SRS requirements:

1. Edit `srs_checklist.json`
2. Add module or requirement with criteria
3. Test scanner detects it: `flask generate-srs-report`
4. Add unit tests in `tests/test_srs_compliance.py`
5. Submit pull request

## License

Part of the AgriFarma project. See main project LICENSE file.
