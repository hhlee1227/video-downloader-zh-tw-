from pathlib import Path
import plistlib
original=plistlib.loads(Path('dist/Video-Downloader-V1.0.unsigned.shortcut').read_bytes())
signed=plistlib.loads(Path('reports/signed-decoded/workflow.bplist').read_bytes())
if original!=signed:
    raise SystemExit('FAIL: signed payload differs. Keep both files and inspect before importing.')
print('PASS: signed workflow payload exactly matches unsigned candidate; iPhone runtime still unverified.')
