"""Paired observations and a time plot, using seeded demonstration data."""
import argparse,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ohmyplt import Plate,configure,apply_chart_style,check_axes_alignment,export,BLUE,RUST

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('output'))
    parser.add_argument('--body-font',default='Arial');parser.add_argument('--math-font',default='Times New Roman');parser.add_argument('--font-dir')
    args=parser.parse_args();configure(args.body_font,args.math_font,args.font_dir)
    rng=np.random.default_rng(19);reference=np.linspace(.07,.15,12)+rng.normal(0,.006,12);model=.8*reference+rng.normal(0,.008,12)
    t=np.linspace(0,30,121);truth=np.sin(t/3)+.15*np.cos(t/1.5);forecast=truth+.1*np.sin(t/2+.3)
    args.out.mkdir(parents=True,exist_ok=True);data=args.out/'data-demo.npz'
    np.savez_compressed(data,reference=reference,model=model,t=t,truth=truth,forecast=forecast)
    p=Plate(183,78);p.panel(3,74,'a','Paired cases');p.panel(96,74,'b','Time forecast')
    a=p.fig.add_axes([15/183,17/78,65/183,49/78]);b=p.fig.add_axes([107/183,17/78,65/183,49/78])
    for r,m in zip(reference,model):a.plot([0,1],[r,m],color='#B6C4CC',lw=.65,zorder=1)
    a.scatter(np.zeros(12),reference,s=13,color=BLUE,zorder=2);a.scatter(np.ones(12),model,s=13,color=RUST,zorder=2)
    a.set(xlim=(-.3,1.3),xticks=[0,1],xticklabels=['Reference','Model'],ylabel=r'Error $(\%)$')
    b.plot(t,truth,color='#9AAAB4',lw=.8,label='Reference');keep=t>=12;b.plot(t[keep],forecast[keep],color=RUST,lw=1,label='Forecast')
    obs=np.arange(0,49,8);b.scatter(t[obs],truth[obs],s=10,facecolors='white',edgecolors=BLUE,linewidths=.7,label='Samples',zorder=3)
    b.axvline(12,color='#AAB7BF',lw=.6,ls='--');b.set(xlim=(0,30),xticks=[0,10,20,30],xlabel=r'$t\;(\mathrm{h})$',ylabel=r'$s(t)$')
    b.legend(loc='lower center',bbox_to_anchor=(.5,1.01),ncol=3,fontsize=6,frameon=False,columnspacing=.9,handlelength=1.2)
    for ax in [a,b]:apply_chart_style(ax)
    alignment=check_axes_alignment(p.fig,[a,b]);(args.out/'data-plot.alignment.json').write_text(json.dumps(alignment,indent=2)+'\n',encoding='utf8')
    if not alignment['passed']:raise RuntimeError('Comparable plotting rectangles differ.')
    export(p.fig,args.out/'data-plot',source_files=[data])
    (args.out/'data-plot.caption.md').write_text('Seeded demonstration data: twelve paired cases and a sampled time signal with a future curve. Pairing lines identify the same case; no statistical inference is attached.\n',encoding='utf8')
    print(args.out/'data-plot.pdf')

if __name__=='__main__':main()
