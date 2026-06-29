#!/usr/bin/env python3
import re, subprocess, sys

with open('/home/claude/beebo/index.html', 'r') as f:
    c = f.read()

ok = True

# 1. script 標籤完整性
scripts = list(re.finditer(r'<script[^>]*>', c))
script_ends = list(re.finditer(r'</script>', c))
if len(scripts) != len(script_ends):
    print(f"✗ script 標籤不對稱: {len(scripts)} 開 / {len(script_ends)} 關")
    ok = False
else:
    print(f"✓ script 標籤: {len(scripts)} 對")

# 2. main script 語法
main_start = c.find('\n<script>\n') + len('\n<script>\n')
main_end = c.rfind('</script>')
main_js = c[main_start:main_end]
with open('/tmp/check_main.js','w') as f: f.write(main_js)
r = subprocess.run(['node','--check','/tmp/check_main.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"✗ Main JS 語法錯誤: {r.stderr[:100]}")
    ok = False
else:
    print(f"✓ Main JS 語法正確 ({len(main_js)} chars)")

# 3. 關鍵函數存在
key_fns = ['openDecide','buildNavs','renderList','renderChal','renderMemory',
           'addListItem','addChal','openMo','closeMo','goPage','fillLocationSelect',
           'addNotif','renderNotifPage','confirmAction','openChalCatMo']
missing = [f for f in key_fns if f'function {f}(' not in main_js]
if missing:
    print(f"✗ 缺少函數: {missing}")
    ok = False
else:
    print(f"✓ 所有關鍵函數存在")

# 4. module 語法
mod_start = c.find('<script type="module">') + len('<script type="module">')
mod_end = c.find('</script>', mod_start)
mod_js = re.sub(r'^\s*import .*$', '', c[mod_start:mod_end], flags=re.MULTILINE)
with open('/tmp/check_mod.js','w') as f: f.write(mod_js)
r2 = subprocess.run(['node','--check','/tmp/check_mod.js'], capture_output=True, text=True)
if r2.returncode != 0:
    print(f"✗ Module JS 語法錯誤: {r2.stderr[:100]}")
    ok = False
else:
    print(f"✓ Module JS 語法正確")

print(f"\n{'✅ 全部通過' if ok else '❌ 有問題'}")
sys.exit(0 if ok else 1)
