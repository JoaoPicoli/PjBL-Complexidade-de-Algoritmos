"""Cross-check stack reports against the exact leaf routine's machine code."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'dados/auditoria_c'


def main():
    report=(DATA/'dedup.su').read_text()
    instrumented=(DATA/'dedup_instrumented.su').read_text()
    frame=int(re.search(r'dedup_heapsort_u16\s+(\d+)\s+static',report)[1])
    assert frame == int(re.search(r'dedup_heapsort_u16\s+(\d+)\s+static',instrumented)[1])
    assembly=(DATA/'dedup_disassembly.txt').read_text()
    other=(DATA/'dedup_instrumented_disassembly.txt').read_text()
    # Ignore file headers; compare the complete function disassembly.
    assert assembly.split('<dedup_heapsort_u16>:')[1] == other.split('<dedup_heapsort_u16>:')[1]
    assert not re.search(r'\b(call|enter)\b',assembly)
    assert not re.search(r'\b(sub|add)\s+rsp\b',assembly)
    pushes=len(re.findall(r'\bpush\s+r\w+',assembly))
    assert frame == 8*pushes+8, (frame,pushes)
    assert not (DATA/'dedup_undefined.txt').read_text().strip()
    sections=(DATA/'dedup_sections.txt').read_text()
    sizes={name:int(re.search(r'\s'+re.escape(name)+r'\s+([0-9a-f]+)',sections)[1],16)
           for name in ('.data','.bss')}
    assert sizes == {'.data':0,'.bss':0}
    # Win64 caller home space is 32 bytes. Add another 16 conservatively for
    # alignment outside the reported callee frame; do not count it twice as measured.
    bound=frame+32+16
    assert bound <= 256
    result={
        'target':'x86_64-w64-mingw32','compiler':'GCC 16.2.0',
        'callee_stack_report_bytes':frame,'callee_push_count':pushes,
        'return_address_bytes':8,'caller_home_space_bytes':32,
        'additional_alignment_allowance_bytes':16,
        'stack_conservative_bound_bytes':bound,
        'algorithm_writable_static_bytes':sum(sizes.values()),
        'algorithm_heap_bytes':0,'total_extra_bound_bytes':bound,
        'budget_bytes':256,'passes_for_this_build':bound<=256,
        'no_calls_or_undefined_symbols':True,
        'instrumented_machine_code_equal':True,
        'dll_sha256':hashlib.sha256((ROOT/'.tools/dedup.dll').read_bytes()).hexdigest(),
        'algorithm_source_sha256':hashlib.sha256((ROOT/'src/embarcada_c/dedup.c').read_bytes()).hexdigest(),
        'method':'GCC static .su, objdump pushes/return, nm, .data/.bss; heap counters checked per run',
        'scope':'Algorithm workspace plus conservative Win64 call overhead. Input/output alias; harness, OS, CRT and interrupts excluded. No claim about an untested sensor ABI.'
    }
    (ROOT/'dados/memoria_c.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
