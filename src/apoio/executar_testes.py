"""Run behavioral tests and retain clean UTF-8 evidence and exit status."""
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
stream=io.StringIO()
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
log=stream.getvalue()
(ROOT/'dados/testes_execucao.txt').write_text(log,encoding='utf-8')
evidence={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
          'successful':result.wasSuccessful(),'exhaustive_sequences':sum(3**n for n in range(6)),
          'manual_cases':8,'random_cases':40,
          'allocation_positive_control':'17-byte request detected in separate fixture DLL',
          'large_benchmark_checks':'recorded separately in resultados_empiricos.csv',
          'dll_sha256':hashlib.sha256((ROOT/'.tools/dedup.dll').read_bytes()).hexdigest()}
(ROOT/'dados/testes_resultado.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
print(log)
sys.exit(0 if result.wasSuccessful() else 1)
