"""Inventário de comandos e configuração; não instala ou modifica toolchains."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools' / 'python'))


def run(args):
    try:
        proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=40)
        return {'command': args, 'returncode': proc.returncode,
                'stdout': proc.stdout.strip(), 'stderr': proc.stderr.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {'command': args, 'returncode': None, 'error': str(exc)}


def main():
    commands = {name: shutil.which(name) for name in [
        'python','python3','py','gcc','clang','cl','pdflatex','xelatex','lualatex',
        'latexmk','tectonic','pdftoppm','pdfinfo','lean','lake','elan','node','rg']}
    versions = [run([name, '--version']) for name in
                ['python','gcc','clang','lean','lake','elan']]
    versions += [run(['cl']), run(['pdftoppm','-v']),run(['pdfinfo','-v'])]
    for relative in ['.tools/tectonic.exe', '.tools/pandoc-3.13/pandoc.exe',
                     '.tools/w64devkit/bin/gcc.exe']:
        if (ROOT / relative).exists():
            versions.append(run([str(ROOT / relative), '--version']))
    packages = {}
    for name in ['sympy','mpmath','numpy','matplotlib','pypdf']:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    files = ['lean4-codex.env', 'lean-toolchain', 'lakefile.lean', 'lakefile.toml',
             'lake-manifest.json','vendor/lean4-plugin/commands/diagnose.md',
             'vendor/lean4-plugin/skills/lean4/SKILL.md',
             'vendor/lean4-plugin/commands/checkpoint.md',
             'container_tools/mark_artifact_operation_started.mjs']
    artifacts = {}
    for name in ['tectonic.zip','pandoc.zip','tectonic.exe','pandoc-3.13/pandoc.exe',
                 'w64devkit-x64-2.11.0.7z.exe','w64devkit/bin/gcc.exe','dedup.dll']:
        path = ROOT / '.tools' / name
        if path.exists():
            artifacts[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    output = {
        'date_user_timezone': '2026-11-11 America/Sao_Paulo',
        'platform': platform.platform(), 'python_executable': sys.executable,
        'cpu': run(['powershell','-NoProfile','-Command',
                    '(Get-CimInstance Win32_Processor).Name']),
        'os': run(['powershell','-NoProfile','-Command',
                   'Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture | ConvertTo-Json']),
        'path_discovery': commands, 'version_attempts': versions,
        'python_packages': packages,
        'project_configuration_exists': {name:(ROOT/name).exists() for name in files},
        'lean_policy': 'No Lean declarations created; build and kernel axiom audit unavailable. Mathlib not configured.',
        'initial_git_status': 'Unborn main; no tracked files; ?? learning_references/; ?? statement/',
        'downloaded_tools_sha256': artifacts,
        'tool_sources': {
            'tectonic':'https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0',
            'pandoc':'https://github.com/jgm/pandoc/releases/tag/3.13',
            'sympy':'PyPI sympy==1.14.0 mpmath==1.3.0 installed with --target .tools/python',
            'gcc':'https://github.com/skeeto/w64devkit/releases/tag/v2.11.0'},
        'tectonic_cache': str(ROOT / '.tools' / 'tectonic-cache'),
        'c_flags': '-std=c11 -O2 -Wall -Wextra -Wconversion -Werror -fno-builtin -fno-stack-protector -fstack-usage -fcallgraph-info=su',
        'local_c_compiler': str(ROOT/'.tools/w64devkit/bin/gcc.exe'),
        'reference_machine': 'Not identified as course reference. Measurements are local only.',
    }
    (ROOT/'docs'/'ambiente.json').write_text(
        json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Inventário e tentativas de versão registrados em docs/ambiente.json')


if __name__ == '__main__':
    main()
