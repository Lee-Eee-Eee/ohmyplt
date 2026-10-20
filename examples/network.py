"""Render a network component example with seeded illustrative signals and weights."""
import argparse,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ohmyplt import Plate,configure,export,BLUE,RUST

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('output'))
    parser.add_argument('--body-font',default='Arial');parser.add_argument('--math-font',default='Times New Roman');parser.add_argument('--font-dir')
    args=parser.parse_args();configure(args.body_font,args.math_font,args.font_dir)
    rng=np.random.default_rng(7);t=np.arange(10,19);signals=np.sin((t[:,None]-10)/3+np.arange(12)[None,:]/5)+rng.normal(0,.12,(9,12))
    features=np.c_[signals,np.cos(signals),np.linspace(-1,1,9),np.linspace(1,-1,9),np.linspace(0,1,9)]
    wi=rng.normal(size=(96,27));wh=rng.normal(size=(96,32));W1=rng.normal(size=(32,32));b1=rng.normal(size=32)
    W2=rng.normal(size=(8,32));b2=rng.normal(size=8);WR=rng.normal(size=(8,243));bR=rng.normal(size=8)
    args.out.mkdir(parents=True,exist_ok=True);data=args.out/'network-demo.npz'
    np.savez_compressed(data,t=t,signals=signals,features=features,wi=wi,wh=wh,W1=W1,b1=b1,W2=W2,b2=b2,WR=WR,bR=bR)
    p=Plate(183,90);p.panel(3,86,'a','Sparse history and trainable correction')
    p.history(5,22,24,38,t,signals,features)
    p.card(36,23,105,36,face='#FCFCFC',r=1.5,z=.5);p.port(36,40);p.port(141,40)
    p.text(88.5,56.4,'Trainable temporal branch',ha='center')
    p.gru(39,27,20,26,wi,wh);p.dense(64,27,20,26,W1,b1);p.gelu(89,27,20,26);p.linear(114,27,24,26,W2,b2)
    for start,end in [(29,39),(59,64),(84,89),(109,114),(138,147.4)]:p.wire([(start,40),(end,40)])
    p.wire([(33,40),(33,74),(39,74)],r=2)
    p.card(39,68,98,13,face='#F1F3F6',r=1,z=3);p.text(43,76,'Fixed affine map');p.text(43,71,r'$z_{\mathrm{R}}=W_{\mathrm{R}}\mathrm{vec}(X)+b_{\mathrm{R}}$')
    p.matrix(86,70.3,34,8,WR,maxrows=8,maxcols=81);p.matrix(129,70.3,2,8,bR[:,None],maxrows=8,maxcols=1,bracket=True)
    p.text(103,65.7,r'$W_{\mathrm{R}}\;(8\times243)$',ha='center')
    p.wire([(137,74),(150,74),(150,42.6)],r=2)
    p.sigma(150,40);p.wire([(152.6,40),(163,40)])
    p.card(163,31,12,19,face='#FBF7F4',edge='#C5A28F',z=3);p.text(169,47,r'$\hat z$',ha='center')
    for k in range(8):p.card(165+k,33,.6,9,face='#E6BEA9',edge='#B47B5D',lw=.25,r=.05,z=4)
    p.text(88.5,19.3,r'$\hat z=z_{\mathrm{R}}+g_{\theta}(X)$',ha='center')
    p.card(130,3,24,7,edge=RUST,z=3);p.text(142,6.5,'Latent loss',6.5,ha='center')
    p.wire([(169,31),(169,6.5),(154,6.5)],color=RUST,r=2)
    p.wire([(130,6.5),(49,6.5),(49,23)],color=RUST,ls='-.',r=2)
    p.text(89,10,r'AdamW updates $\theta$',color=RUST,ha='center')
    export(p.fig,args.out/'network',source_files=[data])
    (args.out/'network.caption.md').write_text('Component demonstration using seeded illustrative signals and weights. Four representative neurons show a 32×32 affine map; nine columns show the nine time samples. This is a drawing template.\n',encoding='utf8')
    print(args.out/'network.pdf')

if __name__=='__main__':main()
