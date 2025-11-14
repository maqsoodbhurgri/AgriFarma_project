"""
Test suite for SRS Compliance Scanner.
Tests route detection, template matching, model scanning, and report generation.
"""
import pytest
import json
import os
from pathlib import Path
from agrifarma.utils.srs_scanner import SRSScanner, create_scanner


@pytest.fixture
def project_root():
    """Get project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def scanner(project_root):
    """Create scanner instance for testing."""
    return create_scanner(project_root)


class TestSRSScanner:
    """Test SRS Scanner functionality."""
    
    def test_scanner_initialization(self, scanner):
        """Test scanner initializes correctly."""
        assert scanner is not None
        assert scanner.project_root is not None
        assert scanner.checklist is not None
        assert 'modules' in scanner.checklist
    
    def test_scan_routes(self, scanner):
        """Test route scanning finds Flask routes."""
        routes = scanner.scan_routes()
        
        assert isinstance(routes, set)
        # Should find at least some core routes
        assert len(routes) > 0
        
        # Check for expected routes
        expected_routes = ['/login', '/register', '/profile']
        found_expected = [r for r in expected_routes if r in routes]
        assert len(found_expected) > 0, f"Should find at least one expected route, found: {list(routes)}"
    
    def test_scan_templates(self, scanner):
        """Test template scanning finds HTML files."""
        templates = scanner.scan_templates()
        
        assert isinstance(templates, set)
        assert len(templates) > 0
        
        # Check for known templates
        expected_templates = [
            'accounts/login.html',
            'accounts/register.html',
            'home/index.html'
        ]
        
        for template in expected_templates:
            assert template in templates, f"Expected template {template} not found"
    
    def test_scan_models(self, scanner):
        """Test model scanning finds SQLAlchemy models."""
        models = scanner.scan_models()
        
        assert isinstance(models, set)
        assert len(models) > 0
        
        # Check for core models
        expected_models = ['User', 'BlogPost', 'Product', 'ForumThread']
        found_models = [m for m in expected_models if m in models]
        assert len(found_models) > 0, f"Should find at least one expected model, found: {list(models)}"
    
    def test_scan_keywords(self, scanner):
        """Test keyword scanning in code."""
        keywords = ['login_required', 'db.session', 'render_template']
        results = scanner.scan_keywords(keywords)
        
        assert isinstance(results, dict)
        assert len(results) == len(keywords)
        
        # These keywords should be found
        assert results.get('login_required') is True
        assert results.get('db.session') is True
        assert results.get('render_template') is True
    
    def test_check_requirement_completed(self, scanner):
        """Test checking a completed requirement."""
        # Create a test requirement with minimal criteria
        requirement = {
            'id': 'test-001',
            'name': 'Test Requirement',
            'routes': ['/login'],
            'templates': ['accounts/login.html'],
            'models': ['User'],
            'keywords': ['login_user']
        }
        
        result = scanner.check_requirement(requirement)
        
        assert result['id'] == 'test-001'
        assert result['status'] in ['completed', 'partial', 'missing']
        assert 'routes' in result
        assert 'templates' in result
        assert 'models' in result
        assert 'keywords' in result
        assert 0 <= result['completion'] <= 100
    
    def test_check_requirement_missing(self, scanner):
        """Test checking a non-existent requirement."""
        requirement = {
            'id': 'test-999',
            'name': 'Non-existent Feature',
            'routes': ['/non-existent-route'],
            'templates': ['non-existent.html'],
            'models': ['NonExistentModel'],
            'keywords': ['non_existent_function']
        }
        
        result = scanner.check_requirement(requirement)
        
        assert result['status'] == 'missing'
        assert result['completion'] < 50
        assert len(result['routes']['found']) == 0
        assert len(result['templates']['found']) == 0
        assert len(result['models']['found']) == 0
    
    def test_generate_report(self, scanner):
        """Test full report generation."""
        report = scanner.generate_report()
        
        assert isinstance(report, dict)
        assert 'generated_at' in report
        assert 'version' in report
        assert 'summary' in report
        assert 'modules' in report
        
        # Check summary structure
        summary = report['summary']
        assert 'total_modules' in summary
        assert 'total_requirements' in summary
        assert 'completed_requirements' in summary
        assert 'partial_requirements' in summary
        assert 'missing_requirements' in summary
        assert 'overall_completion' in summary
        
        # Check modules
        assert len(report['modules']) > 0
        for module in report['modules']:
            assert 'id' in module
            assert 'name' in module
            assert 'priority' in module
            assert 'requirements' in module
            assert 'completion' in module
            assert 'status' in module
    
    def test_report_summary_calculations(self, scanner):
        """Test that report summary calculations are correct."""
        report = scanner.generate_report()
        summary = report['summary']
        
        # Verify totals match
        total_reqs = sum(len(m['requirements']) for m in report['modules'])
        assert summary['total_requirements'] == total_reqs
        
        # Verify completion counts sum correctly
        total_counted = (
            summary['completed_requirements'] +
            summary['partial_requirements'] +
            summary['missing_requirements']
        )
        assert total_counted == summary['total_requirements']
        
        # Verify completion percentage is valid
        assert 0 <= summary['overall_completion'] <= 100
    
    def test_export_report_json(self, scanner, tmp_path):
        """Test exporting report as JSON."""
        output_path = tmp_path / "test_report.json"
        
        result_path = scanner.export_report(str(output_path), format='json')
        
        assert os.path.exists(result_path)
        
        # Verify JSON is valid
        with open(result_path, 'r') as f:
            data = json.load(f)
            assert 'summary' in data
            assert 'modules' in data
    
    def test_export_report_html(self, scanner, tmp_path):
        """Test exporting report as HTML."""
        output_path = tmp_path / "test_report.html"
        
        result_path = scanner.export_report(str(output_path), format='html')
        
        assert os.path.exists(result_path)
        
        # Verify HTML contains expected content
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content
            assert 'SRS Compliance Report' in content
            assert 'Overall Completion' in content
    
    def test_route_pattern_matching(self, scanner):
        """Test that route patterns with parameters are matched correctly."""
        # Add a test route with parameter
        requirement = {
            'id': 'test-pattern',
            'name': 'Pattern Test',
            'routes': ['/blog/post/<id>'],
            'templates': [],
            'models': [],
            'keywords': []
        }
        
        result = scanner.check_requirement(requirement)
        
        # Should match routes like /blog/post/<int:post_id> or /blog/post/<id>
        assert 'routes' in result
    
    def test_module_priority_levels(self, scanner):
        """Test that modules have valid priority levels."""
        report = scanner.generate_report()
        
        valid_priorities = ['critical', 'high', 'medium', 'low']
        
        for module in report['modules']:
            assert module['priority'] in valid_priorities
    
    def test_checklist_structure(self, scanner):
        """Test that checklist JSON has valid structure."""
        checklist = scanner.checklist
        
        assert 'version' in checklist
        assert 'modules' in checklist
        
        for module in checklist['modules']:
            assert 'id' in module
            assert 'name' in module
            assert 'priority' in module
            assert 'requirements' in module
            
            for req in module['requirements']:
                assert 'id' in req
                assert 'name' in req
                assert 'routes' in req
                assert 'templates' in req
                assert 'models' in req
                assert 'keywords' in req


class TestSpecificModules:
    """Test detection of specific SRS modules."""
    
    def test_auth_module_detection(self, scanner):
        """Test authentication module is detected."""
        report = scanner.generate_report()
        
        auth_modules = [m for m in report['modules'] if m['id'] == 'auth']
        assert len(auth_modules) > 0
        
        auth_module = auth_modules[0]
        # Should have decent completion since auth is implemented
        assert auth_module['completion'] > 0
    
    def test_blog_module_detection(self, scanner):
        """Test blog module is detected."""
        report = scanner.generate_report()
        
        blog_modules = [m for m in report['modules'] if m['id'] == 'blog']
        assert len(blog_modules) > 0
        
        blog_module = blog_modules[0]
        assert blog_module['completion'] > 0
    
    def test_forum_module_detection(self, scanner):
        """Test forum module is detected."""
        report = scanner.generate_report()
        
        forum_modules = [m for m in report['modules'] if m['id'] == 'forum']
        assert len(forum_modules) > 0
        
        forum_module = forum_modules[0]
        assert forum_module['completion'] > 0
    
    def test_marketplace_module_detection(self, scanner):
        """Test marketplace module is detected."""
        report = scanner.generate_report()
        
        marketplace_modules = [m for m in report['modules'] if m['id'] == 'marketplace']
        assert len(marketplace_modules) > 0
        
        marketplace_module = marketplace_modules[0]
        assert marketplace_module['completion'] > 0


class TestCaching:
    """Test scanner caching mechanisms."""
    
    def test_route_caching(self, scanner):
        """Test that routes are cached after first scan."""
        # First call
        routes1 = scanner.scan_routes()
        
        # Second call should use cache
        routes2 = scanner.scan_routes()
        
        assert routes1 == routes2
        assert scanner._routes_cache is not None
    
    def test_template_caching(self, scanner):
        """Test that templates are cached."""
        templates1 = scanner.scan_templates()
        templates2 = scanner.scan_templates()
        
        assert templates1 == templates2
        assert scanner._templates_cache is not None
    
    def test_model_caching(self, scanner):
        """Test that models are cached."""
        models1 = scanner.scan_models()
        models2 = scanner.scan_models()
        
        assert models1 == models2
        assert scanner._models_cache is not None
    
    def test_keyword_caching(self, scanner):
        """Test that keywords are cached."""
        keywords = ['login_required', 'db.session']
        
        results1 = scanner.scan_keywords(keywords)
        results2 = scanner.scan_keywords(keywords)
        
        assert results1 == results2


def test_create_scanner_factory(project_root):
    """Test scanner factory function."""
    scanner = create_scanner(project_root)
    
    assert scanner is not None
    assert isinstance(scanner, SRSScanner)
    assert scanner.project_root == Path(project_root)


def test_scanner_handles_missing_directories(tmp_path, project_root):
    """Test scanner handles missing directories gracefully."""
    # Create scanner pointing to empty directory but use real checklist
    checklist_path = os.path.join(project_root, 'srs_checklist.json')
    scanner = SRSScanner(str(tmp_path), checklist_path)
    
    routes = scanner.scan_routes()
    templates = scanner.scan_templates()
    models = scanner.scan_models()
    
    # Should return empty sets, not crash
    assert routes == set()
    assert templates == set()
    assert models == set()
