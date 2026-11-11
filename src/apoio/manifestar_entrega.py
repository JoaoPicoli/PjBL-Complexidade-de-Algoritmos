"""Lista entregáveis novos e preservados sem incluir caches e temporários."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    originals = json.loads((ROOT/'docs/entradas_sha256.json').read_text(encoding='utf-8'))
    old_paths = {item['path'] for item in originals}
    proc = subprocess.run(['git','ls-files','--others','--exclude-standard','-z'],
                          cwd=ROOT, capture_output=True, check=True)
    files = sorted(x for x in proc.stdout.decode('utf-8').split('\0') if x)
    entries = []
    for name in files:
        if name == 'docs/manifesto_entrega.json':
            continue
        path = ROOT/name
        entries.append({'path': name, 'state': 'preservado' if name in old_paths else 'criado',
                        'bytes': path.stat().st_size,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    result = {
        'scope': 'Arquivos não rastreados visíveis ao Git; .tools e tmp ignorados',
        'date_user_timezone': '2026-11-11 America/Sao_Paulo',
        'git_status': subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,
                                     check=True).stdout.decode('utf-8'),
        'files': entries,
        'self': 'docs/manifesto_entrega.json: criado, sem hash de si próprio',
        'created_count_including_self': sum(x['state']=='criado' for x in entries)+1,
        'original_preserved_count': len(old_paths),
    }
    baseline=ROOT/'docs/historico/manifesto_etapa1.json'
    if baseline.exists():
        previous={item['path']:item['sha256'] for item in
                  json.loads(baseline.read_text(encoding='utf-8'))['files']}
        result['changes_since_stage1']=[
            {'path':item['path'],
             'change':'criado' if item['path'] not in previous else 'alterado'}
            for item in entries if previous.get(item['path'])!=item['sha256']]
    (ROOT/'docs/manifesto_entrega.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print('Arquivos criados incluindo manifesto:',result['created_count_including_self'])
    print('Entradas preservadas:',len(old_paths))


if __name__ == '__main__':
    main()
