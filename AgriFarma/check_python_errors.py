"""Check for Python syntax errors in all Python files"""
import os
import py_compile
import sys

def check_python_files(directory):
    """Check all Python files for syntax errors"""
    errors = []
    checked = []
    
    for root, dirs, files in os.walk(directory):
        # Skip venv and other unnecessary directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'migrations']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                
                try:
                    py_compile.compile(filepath, doraise=True)
                    checked.append(rel_path)
                    print(f"✓ {rel_path}")
                except py_compile.PyCompileError as e:
                    errors.append((rel_path, str(e)))
                    print(f"✗ {rel_path}: {e}")
    
    return checked, errors

def main():
    print("=" * 60)
    print("CHECKING PYTHON FILES FOR SYNTAX ERRORS")
    print("=" * 60)
    print()
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    checked, errors = check_python_files(project_dir)
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files checked: {len(checked)}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print("\nFILES WITH ERRORS:")
        for filepath, error in errors:
            print(f"  ✗ {filepath}")
            print(f"    {error}")
    else:
        print("\n✓✓✓ NO SYNTAX ERRORS FOUND ✓✓✓")
    
    return len(errors) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
