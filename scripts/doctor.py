"""Inspect actual font availability and glyph coverage."""
import argparse,json
from matplotlib.ft2font import FT2Font
from ohmyplt import configure

def main():
    p=argparse.ArgumentParser();p.add_argument('--body-font',default='Arial');p.add_argument('--math-font',default='Times New Roman')
    p.add_argument('--font-dir');p.add_argument('--glyphs',default='Σθη∂←→×');a=p.parse_args()
    try:style=configure(a.body_font,a.math_font,a.font_dir)
    except RuntimeError as exc:p.exit(1,str(exc)+'\n')
    font=FT2Font(style['font_paths'][a.math_font]);coverage={c:bool(font.get_char_index(ord(c))) for c in a.glyphs}
    print(json.dumps(dict(fonts=style['font_paths'],required_glyphs=coverage,
        optional_glyphs={c:bool(font.get_char_index(ord(c))) for c in '∈∇'}),ensure_ascii=False,indent=2))
    return 0 if all(coverage.values()) else 1

if __name__=='__main__':raise SystemExit(main())
