"""
SRS Compliance Scanner for AgriFarma
Automatically scans the Flask application to detect implemented features
and generates compliance reports against the SRS checklist.
"""
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime


class SRSScanner:
    """
    Scans Flask application structure to detect implemented SRS requirements.
    """
    
    def __init__(self, project_root: str, checklist_path: str = None):
        """
        Initialize scanner with project root and checklist.
        
        Args:
            project_root: Path to AgriFarma project root
            checklist_path: Path to SRS checklist JSON (optional)
        """
        self.project_root = Path(project_root)
        
        # Load SRS checklist
        if checklist_path is None:
            checklist_path = self.project_root / 'srs_checklist.json'
        
        with open(checklist_path, 'r', encoding='utf-8') as f:
            self.checklist = json.load(f)
        
        # Cache for detected items
        self._routes_cache = None
        self._templates_cache = None
        self._models_cache = None
        self._keywords_cache = None
    
    def scan_routes(self) -> Set[str]:
        """
        Scan all Python files in routes/ directory to extract route decorators.
        
        Returns:
            Set of route paths found
        """
        if self._routes_cache is not None:
            return self._routes_cache
        
        routes = set()
        routes_dir = self.project_root / 'agrifarma' / 'routes'
        
        if not routes_dir.exists():
            return routes
        
        # Pattern to match @blueprint.route('...') decorators
        route_pattern = re.compile(r"@\w+\.route\(['\"]([^'\"]+)['\"]")
        
        for py_file in routes_dir.glob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = route_pattern.findall(content)
                    routes.update(matches)
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        self._routes_cache = routes
        return routes
    
    def scan_templates(self) -> Set[str]:
        """
        Scan templates/ directory to find all template files.
        
        Returns:
            Set of template paths (relative to templates/)
        """
        if self._templates_cache is not None:
            return self._templates_cache
        
        templates = set()
        templates_dir = self.project_root / 'templates'
        
        if not templates_dir.exists():
            return templates
        
        for html_file in templates_dir.rglob('*.html'):
            # Get path relative to templates directory
            rel_path = html_file.relative_to(templates_dir)
            templates.add(str(rel_path).replace('\\', '/'))
        
        self._templates_cache = templates
        return templates
    
    def scan_models(self) -> Set[str]:
        """
        Scan models/ directory to extract model class names.
        
        Returns:
            Set of model class names
        """
        if self._models_cache is not None:
            return self._models_cache
        
        models = set()
        models_dir = self.project_root / 'agrifarma' / 'models'
        
        if not models_dir.exists():
            return models
        
        # Pattern to match class definitions
        class_pattern = re.compile(r'^class\s+(\w+)\s*\(', re.MULTILINE)
        
        for py_file in models_dir.glob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = class_pattern.findall(content)
                    models.update(matches)
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        self._models_cache = models
        return models
    
    def scan_keywords(self, keywords: List[str]) -> Dict[str, bool]:
        """
        Search for keywords in Python files across the project.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            Dictionary mapping keyword to found status
        """
        if self._keywords_cache is None:
            self._keywords_cache = {}
        
        results = {}
        
        for keyword in keywords:
            # Check cache first
            if keyword in self._keywords_cache:
                results[keyword] = self._keywords_cache[keyword]
                continue
            
            found = False
            
            # Search in agrifarma directory
            agrifarma_dir = self.project_root / 'agrifarma'
            if agrifarma_dir.exists():
                for py_file in agrifarma_dir.rglob('*.py'):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if keyword in content:
                                found = True
                                break
                    except Exception:
                        continue
                    
                    if found:
                        break
            
            results[keyword] = found
            self._keywords_cache[keyword] = found
        
        return results
    
    def check_requirement(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a single requirement is implemented.
        
        Args:
            requirement: Requirement dictionary from checklist
            
        Returns:
            Dictionary with requirement status and details
        """
        routes = self.scan_routes()
        templates = self.scan_templates()
        models = self.scan_models()
        
        # Check routes
        required_routes = set(requirement.get('routes', []))
        found_routes = set()
        
        for req_route in required_routes:
            # Normalize route (remove <param> for matching)
            normalized_req = re.sub(r'<[^>]+>', r'<\\w+>', req_route)
            pattern = re.compile(f"^{normalized_req}$")
            
            for actual_route in routes:
                if pattern.match(actual_route) or req_route == actual_route:
                    found_routes.add(req_route)
                    break
        
        # Check templates
        required_templates = set(requirement.get('templates', []))
        found_templates = required_templates & templates
        
        # Check models
        required_models = set(requirement.get('models', []))
        found_models = required_models & models
        
        # Check keywords
        required_keywords = requirement.get('keywords', [])
        keyword_results = self.scan_keywords(required_keywords) if required_keywords else {}
        found_keywords = [k for k, v in keyword_results.items() if v]
        
        # Calculate completion percentage
        total_checks = (
            len(required_routes) + 
            len(required_templates) + 
            len(required_models) + 
            len(required_keywords)
        )
        
        if total_checks == 0:
            completion = 100  # If no requirements, consider complete
        else:
            found_checks = (
                len(found_routes) + 
                len(found_templates) + 
                len(found_models) + 
                len(found_keywords)
            )
            completion = int((found_checks / total_checks) * 100)
        
        # Determine status
        if completion == 100:
            status = 'completed'
        elif completion >= 50:
            status = 'partial'
        else:
            status = 'missing'
        
        return {
            'id': requirement['id'],
            'name': requirement['name'],
            'status': status,
            'completion': completion,
            'routes': {
                'required': list(required_routes),
                'found': list(found_routes),
                'missing': list(required_routes - found_routes)
            },
            'templates': {
                'required': list(required_templates),
                'found': list(found_templates),
                'missing': list(required_templates - found_templates)
            },
            'models': {
                'required': list(required_models),
                'found': list(found_models),
                'missing': list(required_models - found_models)
            },
            'keywords': {
                'required': required_keywords,
                'found': found_keywords,
                'missing': [k for k in required_keywords if k not in found_keywords]
            }
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate full compliance report for all modules.
        
        Returns:
            Complete report dictionary with module and requirement details
        """
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'version': self.checklist.get('version', '1.0.0'),
            'summary': {
                'total_modules': 0,
                'completed_modules': 0,
                'partial_modules': 0,
                'missing_modules': 0,
                'total_requirements': 0,
                'completed_requirements': 0,
                'partial_requirements': 0,
                'missing_requirements': 0,
                'overall_completion': 0
            },
            'modules': []
        }
        
        for module in self.checklist.get('modules', []):
            module_result = {
                'id': module['id'],
                'name': module['name'],
                'priority': module.get('priority', 'medium'),
                'requirements': [],
                'completion': 0,
                'status': 'missing'
            }
            
            total_completion = 0
            
            for requirement in module.get('requirements', []):
                req_result = self.check_requirement(requirement)
                module_result['requirements'].append(req_result)
                total_completion += req_result['completion']
                
                # Update summary counts
                report['summary']['total_requirements'] += 1
                if req_result['status'] == 'completed':
                    report['summary']['completed_requirements'] += 1
                elif req_result['status'] == 'partial':
                    report['summary']['partial_requirements'] += 1
                else:
                    report['summary']['missing_requirements'] += 1
            
            # Calculate module completion
            if module_result['requirements']:
                module_result['completion'] = int(
                    total_completion / len(module_result['requirements'])
                )
            else:
                module_result['completion'] = 0
            
            # Determine module status
            if module_result['completion'] == 100:
                module_result['status'] = 'completed'
                report['summary']['completed_modules'] += 1
            elif module_result['completion'] >= 50:
                module_result['status'] = 'partial'
                report['summary']['partial_modules'] += 1
            else:
                module_result['status'] = 'missing'
                report['summary']['missing_modules'] += 1
            
            report['summary']['total_modules'] += 1
            report['modules'].append(module_result)
        
        # Calculate overall completion
        if report['summary']['total_requirements'] > 0:
            report['summary']['overall_completion'] = int(
                (report['summary']['completed_requirements'] / 
                 report['summary']['total_requirements']) * 100
            )
        
        return report
    
    def export_report(self, output_path: str = None, format: str = 'json') -> str:
        """
        Export compliance report to file.
        
        Args:
            output_path: Path to output file (optional)
            format: Output format ('json' or 'html')
            
        Returns:
            Path to exported file
        """
        report = self.generate_report()
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.project_root / f'srs_report_{timestamp}.{format}'
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        elif format == 'html':
            html_content = self._generate_html_report(report)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return str(output_path)
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report from compliance data."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SRS Compliance Report - AgriFarma</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #4680ff; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .summary-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
        .summary-card h3 {{ margin: 0; font-size: 32px; color: #4680ff; }}
        .summary-card p {{ margin: 5px 0 0 0; color: #7f8c8d; }}
        .progress {{ background: #ecf0f1; border-radius: 10px; height: 25px; margin: 10px 0; overflow: hidden; }}
        .progress-bar {{ background: #4680ff; height: 100%; line-height: 25px; color: white; text-align: center; font-weight: bold; }}
        .progress-bar.completed {{ background: #2ecc71; }}
        .progress-bar.partial {{ background: #f39c12; }}
        .progress-bar.missing {{ background: #e74c3c; }}
        .module {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 5px solid #4680ff; }}
        .requirement {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #dee2e6; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        .badge.completed {{ background: #2ecc71; color: white; }}
        .badge.partial {{ background: #f39c12; color: white; }}
        .badge.missing {{ background: #e74c3c; color: white; }}
        .badge.priority-critical {{ background: #e74c3c; color: white; }}
        .badge.priority-high {{ background: #f39c12; color: white; }}
        .badge.priority-medium {{ background: #3498db; color: white; }}
        .details {{ margin: 10px 0; font-size: 14px; }}
        .details ul {{ margin: 5px 0; padding-left: 20px; }}
        .details li {{ margin: 3px 0; }}
        .found {{ color: #2ecc71; }}
        .missing-item {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SRS Compliance Report - AgriFarma</h1>
        <p>Generated: {report['generated_at']}</p>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{report['summary']['overall_completion']}%</h3>
                <p>Overall Completion</p>
            </div>
            <div class="summary-card">
                <h3>{report['summary']['completed_requirements']}/{report['summary']['total_requirements']}</h3>
                <p>Requirements Done</p>
            </div>
            <div class="summary-card">
                <h3>{report['summary']['completed_modules']}/{report['summary']['total_modules']}</h3>
                <p>Modules Complete</p>
            </div>
            <div class="summary-card">
                <h3>{report['summary']['partial_requirements']}</h3>
                <p>Partial Features</p>
            </div>
        </div>
        
        <h2>Modules Overview</h2>
"""
        
        for module in report['modules']:
            status_class = module['status']
            html += f"""
        <div class="module">
            <h3>
                {module['name']}
                <span class="badge {status_class}">{status_class.upper()}</span>
                <span class="badge priority-{module['priority']}">{module['priority'].upper()}</span>
            </h3>
            <div class="progress">
                <div class="progress-bar {status_class}" style="width: {module['completion']}%">
                    {module['completion']}%
                </div>
            </div>
"""
            
            for req in module['requirements']:
                html += f"""
            <div class="requirement">
                <h4>
                    {req['name']}
                    <span class="badge {req['status']}">{req['status'].upper()}</span>
                    <span style="float: right; color: #7f8c8d;">{req['completion']}%</span>
                </h4>
"""
                
                if req['routes']['required']:
                    html += '<div class="details"><strong>Routes:</strong><ul>'
                    for route in req['routes']['found']:
                        html += f'<li class="found">✓ {route}</li>'
                    for route in req['routes']['missing']:
                        html += f'<li class="missing-item">✗ {route}</li>'
                    html += '</ul></div>'
                
                if req['templates']['required']:
                    html += '<div class="details"><strong>Templates:</strong><ul>'
                    for template in req['templates']['found']:
                        html += f'<li class="found">✓ {template}</li>'
                    for template in req['templates']['missing']:
                        html += f'<li class="missing-item">✗ {template}</li>'
                    html += '</ul></div>'
                
                if req['models']['required']:
                    html += '<div class="details"><strong>Models:</strong><ul>'
                    for model in req['models']['found']:
                        html += f'<li class="found">✓ {model}</li>'
                    for model in req['models']['missing']:
                        html += f'<li class="missing-item">✗ {model}</li>'
                    html += '</ul></div>'
                
                html += '</div>'
            
            html += '</div>'
        
        html += """
    </div>
</body>
</html>
"""
        return html


def create_scanner(project_root: str = None) -> SRSScanner:
    """
    Factory function to create scanner instance.
    
    Args:
        project_root: Project root path (defaults to current directory)
        
    Returns:
        Configured SRSScanner instance
    """
    if project_root is None:
        project_root = os.getcwd()
    
    return SRSScanner(project_root)
