"""Renderiza páginas e folhas de contato para revisão visual humana."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools' / 'python'))
from PIL import Image, ImageDraw


def main():
    out = ROOT/'tmp/pdfs'
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm','-r','100','-png',
                    str(ROOT/'relatorios_latex/relatorio.pdf'),str(out/'final')],check=True)
    pages = sorted(out.glob('final-*.png'))
    for first in range(0,len(pages),4):
        sheet = Image.new('RGB',(1440,2080),'#cccccc')
        draw = ImageDraw.Draw(sheet)
        for j,path in enumerate(pages[first:first+4]):
            pic = Image.open(path).convert('RGB')
            pic.thumbnail((690,980))
            x = 15+(j%2)*720
            y = 28+(j//2)*1040
            sheet.paste(pic,(x,y))
            draw.text((x,y-20),path.stem,fill='black')
        sheet.save(out/f'contato-{first//4+1}.png')
    print('Páginas renderizadas:',len(pages))


if __name__ == '__main__':
    main()
