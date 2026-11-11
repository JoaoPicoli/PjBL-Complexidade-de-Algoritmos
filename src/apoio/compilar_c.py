"""Build and retain GCC stack/object evidence for the exact benchmark binary."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT/'.tools/w64devkit/bin'
BUILD = ROOT/'dados/auditoria_c'
FLAGS = ['-std=c11','-O2','-Wall','-Wextra','-Wconversion','-Werror',
         '-fno-builtin','-fno-stack-protector','-fstack-usage','-fcallgraph-info=su']


def main():
    BUILD.mkdir(parents=True,exist_ok=True)
    env = os.environ.copy()
    temporary=ROOT/'.tools/tmp_compilacao'
    temporary.mkdir(parents=True,exist_ok=True)
    for name in ('TMPDIR','TMP','TEMP'):
        env[name]=str(temporary)
    env['PATH'] = str(BIN)+os.pathsep+env.get('PATH','')
    commands = []

    def run(args, output=None):
        proc = subprocess.run([str(x) for x in args],cwd=ROOT,env=env,
                              capture_output=True,text=True,encoding='utf-8',errors='replace')
        commands.append({'command':[str(x) for x in args], 'returncode':proc.returncode,
                         'stdout':proc.stdout,'stderr':proc.stderr})
        if output:
            (BUILD/output).write_text(proc.stdout+proc.stderr,encoding='utf-8')
        if proc.returncode:
            raise RuntimeError(proc.stderr)
        return proc.stdout

    gcc = BIN/'gcc.exe'
    run([gcc,'--version'],'gcc_version.txt')
    run([gcc,'-dumpmachine'],'target.txt')
    run([gcc,*FLAGS,'-c','src/embarcada_c/dedup.c','-o',BUILD/'dedup.o'])
    run([gcc,*FLAGS,'-include','src/embarcada_c/alloc_hooks.h','-c',
         'src/embarcada_c/dedup.c','-o',BUILD/'dedup_instrumented.o'])
    run([gcc,*FLAGS,'-c','src/embarcada_c/alloc_audit.c','-o',BUILD/'alloc_audit.o'])
    run([gcc,'-shared','-static-libgcc',BUILD/'dedup_instrumented.o',
         BUILD/'alloc_audit.o','-o',ROOT/'.tools/dedup.dll'])
    run([gcc,*FLAGS,'-include','src/embarcada_c/alloc_hooks.h','-c',
         'src/embarcada_c/audit_fixture.c','-o',BUILD/'audit_fixture.o'])
    run([gcc,'-shared','-static-libgcc',BUILD/'audit_fixture.o',
         BUILD/'alloc_audit.o','-o',ROOT/'.tools/allocation_fixture.dll'])
    run([BIN/'objdump.exe','-d','-Mintel',BUILD/'dedup.o'],'dedup_disassembly.txt')
    run([BIN/'objdump.exe','-h',BUILD/'dedup.o'],'dedup_sections.txt')
    run([BIN/'nm.exe','-u',BUILD/'dedup.o'],'dedup_undefined.txt')
    run([BIN/'nm.exe','-S',BUILD/'dedup.o'],'dedup_symbols.txt')
    run([BIN/'objdump.exe','-d','-Mintel',BUILD/'dedup_instrumented.o'],
        'dedup_instrumented_disassembly.txt')
    (BUILD/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
    print('C compiled; evidence in dados/auditoria_c; DLL in .tools/dedup.dll')


if __name__ == '__main__':
    main()
