"""
SRS Compliance Scanner for AgriFarma
Scans codebase against JSON SRS checklist and generates completion report.
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class SRSComplianceScanner:
    def __init__(self, project_root: str, checklist_path: str):
        self.project_root = Path(project_root)
        self.checklist_path = checklist_path
        self.checklist = None
        self.routes_found = set()
        self.templates_found = set()
        self.models_found = set()
        self.keywords_found = defaultdict(list)
        
    def load_checklist(self):
        """Load SRS checklist from JSON file."""
        with open(self.checklist_path, 'r', encoding='utf-8') as f:
            self.checklist = json.load(f)
        print(f"✓ Loaded SRS checklist version {self.checklist.get('version', 'unknown')}")
        
    def scan_routes(self):
        """Scan all route files for endpoint definitions."""
        routes_dir = self.project_root / 'agrifarma' / 'routes'
        route_pattern = re.compile(r"@\w+_bp\.route\(['\"]([^'\"]+)")
        
        for route_file in routes_dir.glob('*.py'):
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = route_pattern.findall(content)
                self.routes_found.update(matches)
                
        print(f"✓ Found {len(self.routes_found)} route endpoints")
        
    def scan_templates(self):
        """Scan templates directory for HTML files."""
        templates_dir = self.project_root / 'templates'
        agrifarma_templates = self.project_root / 'agrifarma' / 'templates'
        
        for tmpl_dir in [templates_dir, agrifarma_templates]:
            if tmpl_dir.exists():
                for tmpl_file in tmpl_dir.rglob('*.html'):
                    rel_path = tmpl_file.relative_to(tmpl_dir)
                    self.templates_found.add(str(rel_path).replace('\\', '/'))
                    
        print(f"✓ Found {len(self.templates_found)} template files")
        
    def scan_models(self):
        """Scan models directory for model class definitions."""
        models_dir = self.project_root / 'agrifarma' / 'models'
        model_pattern = re.compile(r'class (\w+)\([^)]*\):')
        
        for model_file in models_dir.glob('*.py'):
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = model_pattern.findall(content)
                self.models_found.update(matches)
                
        print(f"✓ Found {len(self.models_found)} model classes")
        
    def scan_keywords(self):
        """Scan entire codebase for specific keywords."""
        search_dirs = [
            self.project_root / 'agrifarma' / 'routes',
            self.project_root / 'agrifarma' / 'models',
            self.project_root / 'agrifarma' / 'forms'
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            for py_file in search_dir.rglob('*.py'):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Store file content for later keyword matching
                    rel_path = py_file.relative_to(self.project_root)
                    self.keywords_found[str(rel_path)] = content
                    
        print(f"✓ Scanned {len(self.keywords_found)} Python files for keywords")
        
    def scan_all(self):
        """Run all scanner functions."""
        print("="*60)
        print("SCANNING AGRIFARMA CODEBASE")
        print("="*60)
        self.load_checklist()
        self.scan_routes()
        self.scan_templates()
        self.scan_models()
        self.scan_keywords()
        print("="*60)
        
    def check_requirement(self, requirement: Dict) -> Tuple[str, Dict]:
        """
        Check a single requirement against scanned codebase.
        Returns: (status, details)
        Status: 'completed', 'partial', 'missing'
        """
        req_id = requirement['id']
        req_name = requirement['name']
        
        # Check routes
        routes = requirement.get('routes', [])
        routes_matched = []
        routes_missing = []
        
        for route in routes:
            # Normalize route patterns (remove blueprint prefix, handle parameters)
            route_base = route.split('/')[-1] if '/' in route else route
            # Check if any found route contains this pattern
            matched = any(
                route in found or route.replace('<slug>', '<').replace('<id>', '<int:') in found
                for found in self.routes_found
            )
            if matched:
                routes_matched.append(route)
            else:
                routes_missing.append(route)
                
        # Check templates
        templates = requirement.get('templates', [])
        templates_matched = []
        templates_missing = []
        
        for template in templates:
            # Check various possible paths
            variants = [
                template,
                template.replace('accounts/', ''),
                template.replace('home/', ''),
                'agrifarma/templates/' + template,
                template.split('/')[-1]  # just filename
            ]
            matched = any(v in self.templates_found for v in variants)
            if matched:
                templates_matched.append(template)
            else:
                templates_missing.append(template)
                
        # Check models
        models = requirement.get('models', [])
        models_matched = []
        models_missing = []
        
        for model in models:
            # Check for exact match or common variations
            variants = [model, f'{model}Category', f'{model}Thread', f'{model}Reply', f'{model}Post']
            matched = any(v in self.models_found for v in variants)
            if matched:
                models_matched.append(model)
            else:
                models_missing.append(model)
                
        # Check keywords
        keywords = requirement.get('keywords', [])
        keywords_matched = []
        keywords_missing = []
        
        for keyword in keywords:
            # Search across all scanned files
            matched = any(keyword in content for content in self.keywords_found.values())
            if matched:
                keywords_matched.append(keyword)
            else:
                keywords_missing.append(keyword)
                
        # Determine status
        total_checks = len(routes) + len(templates) + len(models) + len(keywords)
        if total_checks == 0:
            status = 'completed'  # No specific checks defined
        else:
            matched_checks = len(routes_matched) + len(templates_matched) + len(models_matched) + len(keywords_matched)
            completion_rate = matched_checks / total_checks if total_checks > 0 else 0
            
            if completion_rate >= 0.9:
                status = 'completed'
            elif completion_rate >= 0.5:
                status = 'partial'
            else:
                status = 'missing'
                
        details = {
            'routes': {'matched': routes_matched, 'missing': routes_missing},
            'templates': {'matched': templates_matched, 'missing': templates_missing},
            'models': {'matched': models_matched, 'missing': models_missing},
            'keywords': {'matched': keywords_matched, 'missing': keywords_missing},
            'completion_rate': (matched_checks / total_checks * 100) if total_checks > 0 else 100.0
        }
        
        return status, details
        
    def generate_report(self) -> Dict:
        """Generate comprehensive SRS compliance report."""
        report = {
            'version': self.checklist.get('version'),
            'scan_date': '2025-11-12',
            'modules': [],
            'summary': {
                'total_requirements': 0,
                'completed': 0,
                'partial': 0,
                'missing': 0
            }
        }
        
        for module in self.checklist.get('modules', []):
            module_report = {
                'id': module['id'],
                'name': module['name'],
                'priority': module.get('priority', 'medium'),
                'requirements': []
            }
            
            for requirement in module.get('requirements', []):
                status, details = self.check_requirement(requirement)
                
                req_report = {
                    'id': requirement['id'],
                    'name': requirement['name'],
                    'status': status,
                    'completion_rate': details['completion_rate'],
                    'details': details
                }
                
                module_report['requirements'].append(req_report)
                report['summary']['total_requirements'] += 1
                report['summary'][status] += 1
                
            module_report['module_completion'] = (
                sum(1 for r in module_report['requirements'] if r['status'] == 'completed') / 
                len(module_report['requirements']) * 100
                if module_report['requirements'] else 0
            )
            
            report['modules'].append(module_report)
            
        return report
        
    def print_report(self, report: Dict):
        """Print formatted report to console."""
        print("\n" + "="*80)
        print(" "*25 + "SRS COMPLIANCE REPORT")
        print("="*80)
        print(f"Version: {report['version']} | Scan Date: {report['scan_date']}")
        print("="*80)
        
        # Summary
        summary = report['summary']
        total = summary['total_requirements']
        completed = summary['completed']
        partial = summary['partial']
        missing = summary['missing']
        
        overall_completion = (completed / total * 100) if total > 0 else 0
        
        print(f"\n{'OVERALL SUMMARY':^80}")
        print("-"*80)
        print(f"Total Requirements: {total}")
        print(f"✅ Completed: {completed} ({completed/total*100:.1f}%)")
        print(f"🔧 Partially Done: {partial} ({partial/total*100:.1f}%)")
        print(f"❌ Missing: {missing} ({missing/total*100:.1f}%)")
        print(f"{'Overall Completion: ' + f'{overall_completion:.1f}%':^80}")
        print("-"*80)
        
        # Module details
        for module in report['modules']:
            print(f"\n{'MODULE: ' + module['name'].upper():^80}")
            print(f"{'Priority: ' + module['priority'].upper():^80}")
            module_comp_str = f"Module Completion: {module['module_completion']:.1f}%"
            print(f"{module_comp_str:^80}")
            print("-"*80)
            
            for req in module['requirements']:
                status_icon = {
                    'completed': '✅',
                    'partial': '🔧',
                    'missing': '❌'
                }.get(req['status'], '❓')
                
                print(f"{status_icon} [{req['id']}] {req['name']}")
                print(f"   Completion: {req['completion_rate']:.1f}%")
                
                details = req['details']
                if details['routes']['missing']:
                    print(f"   Missing Routes: {', '.join(details['routes']['missing'][:3])}")
                if details['templates']['missing']:
                    print(f"   Missing Templates: {', '.join(details['templates']['missing'][:3])}")
                if details['models']['missing']:
                    print(f"   Missing Models: {', '.join(details['models']['missing'][:3])}")
                    
        print("\n" + "="*80)
        print(f"{'SCAN COMPLETE':^80}")
        print("="*80 + "\n")
        
    def export_json(self, report: Dict, output_path: str):
        """Export report as JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✓ Report exported to {output_path}")
        
    def export_html(self, report: Dict, output_path: str):
        """Export report as HTML dashboard."""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AgriFarma SRS Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #2c3e50; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 30px 0; }}
        .summary-card {{ padding: 20px; border-radius: 6px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; }}
        .summary-card .value {{ font-size: 32px; font-weight: bold; }}
        .completed {{ background: #d4edda; color: #155724; }}
        .partial {{ background: #fff3cd; color: #856404; }}
        .missing {{ background: #f8d7da; color: #721c24; }}
        .total {{ background: #d1ecf1; color: #0c5460; }}
        .module {{ margin: 30px 0; border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden; }}
        .module-header {{ background: #007bff; color: white; padding: 15px; font-size: 18px; font-weight: bold; }}
        .module-priority {{ float: right; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 4px; font-size: 14px; }}
        .requirement {{ padding: 15px; border-bottom: 1px solid #dee2e6; }}
        .requirement:last-child {{ border-bottom: none; }}
        .requirement-header {{ display: flex; align-items: center; margin-bottom: 8px; }}
        .status-badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }}
        .status-completed {{ background: #28a745; color: white; }}
        .status-partial {{ background: #ffc107; color: #212529; }}
        .status-missing {{ background: #dc3545; color: white; }}
        .req-id {{ font-family: monospace; color: #6c757d; margin-right: 10px; }}
        .completion-bar {{ height: 8px; background: #e9ecef; border-radius: 4px; margin: 8px 0; overflow: hidden; }}
        .completion-bar-fill {{ height: 100%; background: #28a745; transition: width 0.3s; }}
        .details {{ font-size: 13px; color: #6c757d; margin-top: 8px; }}
        .details ul {{ margin: 5px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AgriFarma SRS Compliance Report</h1>
        <p style="text-align: center; color: #6c757d;">Version {report['version']} | Scan Date: {report['scan_date']}</p>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>Total Requirements</h3>
                <div class="value">{report['summary']['total_requirements']}</div>
            </div>
            <div class="summary-card completed">
                <h3>Completed</h3>
                <div class="value">{report['summary']['completed']}</div>
                <p>{report['summary']['completed']/report['summary']['total_requirements']*100:.1f}%</p>
            </div>
            <div class="summary-card partial">
                <h3>Partially Done</h3>
                <div class="value">{report['summary']['partial']}</div>
                <p>{report['summary']['partial']/report['summary']['total_requirements']*100:.1f}%</p>
            </div>
            <div class="summary-card missing">
                <h3>Missing</h3>
                <div class="value">{report['summary']['missing']}</div>
                <p>{report['summary']['missing']/report['summary']['total_requirements']*100:.1f}%</p>
            </div>
        </div>
'''
        
        for module in report['modules']:
            status_map = {'completed': '✅', 'partial': '🔧', 'missing': '❌'}
            html += f'''
        <div class="module">
            <div class="module-header">
                {module['name']}
                <span class="module-priority">{module['priority'].upper()}</span>
                <div style="clear: both;"></div>
                <div style="font-size: 14px; margin-top: 5px;">Module Completion: {module['module_completion']:.1f}%</div>
            </div>
'''
            
            for req in module['requirements']:
                status_class = f"status-{req['status']}"
                status_text = req['status'].upper()
                html += f'''
            <div class="requirement">
                <div class="requirement-header">
                    <span class="status-badge {status_class}">{status_text}</span>
                    <span class="req-id">{req['id']}</span>
                    <strong>{req['name']}</strong>
                </div>
                <div class="completion-bar">
                    <div class="completion-bar-fill" style="width: {req['completion_rate']}%"></div>
                </div>
                <div class="details">Completion: {req['completion_rate']:.1f}%</div>
'''
                
                details = req['details']
                if details['routes']['missing'] or details['templates']['missing'] or details['models']['missing']:
                    html += '<div class="details">'
                    if details['routes']['missing']:
                        html += f"<strong>Missing Routes:</strong> {', '.join(details['routes']['missing'][:5])}<br>"
                    if details['templates']['missing']:
                        html += f"<strong>Missing Templates:</strong> {', '.join(details['templates']['missing'][:5])}<br>"
                    if details['models']['missing']:
                        html += f"<strong>Missing Models:</strong> {', '.join(details['models']['missing'][:5])}<br>"
                    html += '</div>'
                    
                html += '</div>'
                
            html += '</div>'
            
        html += '''
    </div>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ HTML dashboard exported to {output_path}")


def main():
    """Main execution function."""
    import sys
    
    # Get project root (parent of this script)
    script_dir = Path(__file__).parent
    project_root = script_dir
    checklist_path = project_root / 'srs_checklist.json'
    
    if not checklist_path.exists():
        print(f"❌ SRS checklist not found at {checklist_path}")
        sys.exit(1)
        
    # Create scanner
    scanner = SRSComplianceScanner(str(project_root), str(checklist_path))
    
    # Run scan
    scanner.scan_all()
    
    # Generate report
    print("\n" + "="*60)
    print("GENERATING COMPLIANCE REPORT")
    print("="*60)
    report = scanner.generate_report()
    
    # Print to console
    scanner.print_report(report)
    
    # Export reports
    json_output = project_root / 'SRS_COMPLIANCE_REPORT.json'
    html_output = project_root / 'SRS_COMPLIANCE_DASHBOARD.html'
    
    scanner.export_json(report, str(json_output))
    scanner.export_html(report, str(html_output))
    
    print(f"\n✅ Compliance scan complete!")
    print(f"   - Console report printed above")
    print(f"   - JSON report: {json_output}")
    print(f"   - HTML dashboard: {html_output}")
    print(f"\nOpen {html_output} in your browser to view the interactive dashboard.\n")


if __name__ == '__main__':
    main()
