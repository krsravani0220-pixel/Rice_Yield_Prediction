import os
import sys
import glob

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("PROJECT INSPECTION: SEARCHING FOR EXISTING LSTM & ML ARTIFACTS")
print("=" * 70)

# 1. Search for files mentioning LSTM
print("\n--- Files mentioning LSTM ---")
for root, dirs, files in os.walk('.'):
    # skip .git, venv, node_modules, cache dirs
    if any(p in root for p in ['.git', 'node_modules', '__pycache__', '.venv', '.gemini']):
        continue
    for file in files:
        if file.endswith(('.py', '.ipynb', '.md', '.json', '.yaml')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'lstm' in content.lower():
                        count = content.lower().count('lstm')
                        print(f"  {filepath}: {count} occurrences")
            except Exception as e:
                pass

# 2. Check models directory
print("\n--- Files in models/ directory ---")
if os.path.exists('models'):
    for root, dirs, files in os.walk('models'):
        for file in files:
            path = os.path.join(root, file)
            size_kb = os.path.getsize(path) / 1024
            print(f"  {path} ({size_kb:.1f} KB)")
else:
    print("  models/ directory does not exist")

# 3. Check data files (Excel, CSV)
print("\n--- Datasets in data/ or root ---")
for pattern in ['data/**/*', '*.xlsx', '*.csv', 'data/*.xlsx', 'data/*.csv']:
    for p in glob.glob(pattern, recursive=True):
        if os.path.isfile(p):
            size_kb = os.path.getsize(p) / 1024
            print(f"  {p} ({size_kb:.1f} KB)")

# 4. Check dependencies (torch, tensorflow, keras, etc.)
print("\n--- Checking DL Frameworks ---")
for pkg in ['torch', 'tensorflow', 'keras', 'sklearn']:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, '__version__', 'unknown')
        print(f"  {pkg}: installed (v{ver})")
    except ImportError:
        print(f"  {pkg}: NOT installed")
