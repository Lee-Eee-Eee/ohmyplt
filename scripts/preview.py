"""Render a final-size PDF preview or a crop in bottom-left millimetres."""
import argparse
from pathlib import Path
import pymupdf

def main():
    p=argparse.ArgumentParser();p.add_argument('pdf',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--page',type=int,default=1);p.add_argument('--dpi',type=float,default=144)
    p.add_argument('--clip-mm',type=float,nargs=4,metavar=('LEFT','BOTTOM','WIDTH','HEIGHT'));a=p.parse_args()
    if a.dpi<=0:p.error('dpi must be positive')
    with pymupdf.open(a.pdf) as document:
        if not 1<=a.page<=len(document):p.error('page is outside the PDF')
        page=document[a.page-1];clip=None
        if a.clip_mm:
            x,y,w,h=a.clip_mm;scale=72/25.4
            if w<=0 or h<=0:p.error('crop width/height must be positive')
            clip=pymupdf.Rect(x*scale,page.rect.height-(y+h)*scale,(x+w)*scale,page.rect.height-y*scale)
            if not page.rect.contains(clip):p.error('crop extends outside the PDF page')
        a.out.parent.mkdir(parents=True,exist_ok=True)
        page.get_pixmap(matrix=pymupdf.Matrix(a.dpi/72,a.dpi/72),clip=clip,alpha=False).save(a.out)
    print(a.out)

if __name__=='__main__':main()
