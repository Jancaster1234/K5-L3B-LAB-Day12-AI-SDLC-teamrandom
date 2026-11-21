"""Replay published slice-1 fixtures without overwriting the original evidence."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
PROOF = ROOT / 'docs/proof/phase-1/gather-lat1'
CASES = [('01-oxy', 5), ('02-choke', 120), ('03-faint', 10), ('04-dive-surface', 200)]


def main():
    failed = False
    print(f'Python: {sys.version.split()[0]}', flush=True)
    with tempfile.TemporaryDirectory(prefix='chonoi-qa-') as directory:
        for name, ticks in CASES:
            outputs = []
            for attempt in (1, 2):
                output = Path(directory) / f'{name}-{attempt}.jsonl'
                inventory = Path(directory) / f'{name}-{attempt}.inventory.json'
                cmd = [sys.executable, '-m', 'chonoi.headless', '--mode', 'gather',
                       '--seed', '1', '--snapshot-every', '1000', '--ticks', str(ticks),
                       '--scenario', str(PROOF / f'{name}.scenario.json'), '--out', str(output)]
                if name == '04-dive-surface':
                    cmd += ['--inputs', str(PROOF / f'{name}.inputs.json')]
                if name == '03-faint':
                    cmd += ['--inventory-out', str(inventory)]
                result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
                if result.returncode:
                    print(f'FAIL {name} run {attempt}: exit={result.returncode}\n{result.stderr}')
                    failed = True
                    break
                outputs.append(output.read_bytes())
                if name == '03-faint':
                    actual = json.loads(inventory.read_text(encoding='utf-8'))
                    archived = json.loads((PROOF / f'{name}.inventory.json').read_text(encoding='utf-8'))
                    if actual != archived or actual != {'items': {}}:
                        print(f'FAIL {name}: inventory differs or is not empty')
                        failed = True
            if len(outputs) != 2:
                continue
            # Read the committed blob: core.autocrlf can change checkout bytes.
            proof_path = (PROOF / f'{name}.out.jsonl').relative_to(ROOT).as_posix()
            original = subprocess.check_output(['git', 'show', f'HEAD:{proof_path}'], cwd=ROOT)
            if outputs[0] != original or outputs[0] != outputs[1]:
                print(f'FAIL {name}: archived output or deterministic replay differs')
                failed = True
            else:
                print(f'PASS {name}: HEAD archive == replay 1 == replay 2; '
                      f'SHA256={hashlib.sha256(outputs[0]).hexdigest()}')
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
