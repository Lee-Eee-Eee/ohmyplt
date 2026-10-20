"""Run the vendored PDF glyph-size and collision audits, and inspect fonts."""
import argparse,json,subprocess,sys
from pathlib import Path
import pymupdf

def main():
    p=argparse.ArgumentParser();p.add_argument('pdf',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--min-pt',type=float,default=5);p.add_argument('--allow-font',action='append',default=[]);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);base=Path(__file__).resolve().parents[1]/'vendor/nature_figure';checks={}
    for name,script,args in [('text','audit_pdf_text.py',[str(a.pdf),'--min-pt',str(a.min_pt),'--json']),
        ('collision','audit_figure_collisions.py',[str(a.pdf),'--json-out',str(a.out/'collisions.json')])]:
        r=subprocess.run([sys.executable,'-X','utf8',str(base/script),*args],capture_output=True,text=True,encoding='utf8')
        (a.out/f'{name}.log').write_text(r.stdout+r.stderr,encoding='utf8');checks[name]=r.returncode
    with pymupdf.open(a.pdf) as document:
        fonts=sorted({s['font'] for page in document for b in page.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans']})
    normalize=lambda s:''.join(c for c in s.lower() if c.isalnum())
    unexpected=[s for s in fonts if a.allow_font and not any(normalize(f) in normalize(s) for f in a.allow_font)]
    checks['fonts']=1 if unexpected else 0
    report=dict(checks=checks,fonts=fonts,unexpected_fonts=unexpected)
    (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False))
    return 0 if all(code==0 for code in checks.values()) else 1

if __name__=='__main__':raise SystemExit(main())
