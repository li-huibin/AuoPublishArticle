import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'async function loadPersonas()' in line:
            print(''.join(lines[i:i+25]))
            break
