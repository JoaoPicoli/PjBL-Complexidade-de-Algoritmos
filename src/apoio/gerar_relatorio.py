"""Gera LaTeX a partir da análise canônica; opcionalmente compila com Tectonic."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compilar', action='store_true')
    args = parser.parse_args()
    pandoc = ROOT / '.tools' / 'pandoc-3.13' / 'pandoc.exe'
    if not pandoc.exists():
        discovered = shutil.which('pandoc')
        if not discovered:
            raise SystemExit('Pandoc ausente: ver README para preparar as ferramentas locais.')
        pandoc = Path(discovered)
    cmd = [str(pandoc), 'docs/analise_teorica.md', '--from=markdown', '--to=latex',
           '--standalone','--number-sections','--toc','--toc-depth=1',
           '--lua-filter=src/apoio/quebras_codigo.lua',
           '--pdf-engine=xelatex','--variable=documentclass:article',
           '--variable=fontsize:11pt', '--variable=papersize:a4',
           '--variable=geometry:margin=23mm', '--variable=mainfont:Cambria',
           '--variable=sansfont:Calibri', '--variable=monofont:Consolas',
           '--variable=colorlinks:true','--variable=linkcolor:projectblue',
           '--include-in-header=relatorios_latex/preambulo.tex',
           '--output=relatorios_latex/relatorio.tex']
    subprocess.run(cmd, cwd=ROOT, check=True)
    texpath = ROOT/'relatorios_latex/relatorio.tex'
    tex = texpath.read_text(encoding='utf-8')
    tex = tex.replace('\\tableofcontents', '\\tableofcontents\n\\clearpage', 1)
    texpath.write_text(tex, encoding='utf-8')
    print('LaTeX gerado a partir de docs/analise_teorica.md')
    if args.compilar:
        tectonic = ROOT / '.tools' / 'tectonic.exe'
        if not tectonic.exists():
            raise SystemExit('Tectonic local ausente. O LaTeX foi preservado.')
        env = os.environ.copy()
        env['TECTONIC_CACHE_DIR'] = str(ROOT / '.tools' / 'tectonic-cache')
        env['XDG_CACHE_HOME'] = str(ROOT / '.tools' / 'cache')
        fontconfig = ROOT/'.tools/fonts.conf'
        fontconfig.write_text(
            '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">'
            '<fontconfig><dir>C:/Windows/Fonts</dir><cachedir>'
            + escape(str(ROOT/'.tools/fontconfig-cache').replace('\\','/'))
            + '</cachedir></fontconfig>', encoding='utf-8')
        env['FONTCONFIG_FILE'] = str(fontconfig)
        proc = subprocess.run([str(tectonic),'--keep-logs','--keep-intermediates',
                               'relatorios_latex/relatorio.tex'],
                              cwd=ROOT, env=env, capture_output=True, text=True,
                              encoding='utf-8', errors='replace')
        output = proc.stdout + '\n' + proc.stderr
        (ROOT/'docs'/'compilacao_pdf.txt').write_text(output, encoding='utf-8')
        print(output)
        if proc.returncode:
            raise SystemExit(proc.returncode)


if __name__ == '__main__':
    main()
