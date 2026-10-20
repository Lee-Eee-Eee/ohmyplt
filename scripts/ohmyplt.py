"""Scientific vector drawing primitives in millimetres. Apache-2.0."""
from __future__ import annotations
import hashlib,json,logging,math,os,warnings
from pathlib import Path
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,_mathtext
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle,FancyArrowPatch,FancyBboxPatch,PathPatch,Rectangle
from matplotlib.path import Path as MPath
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

INK='#273139';EDGE='#758A95';BLUE='#37798A';RUST='#B66A47'
CYAN='#E5F0F2';PURPLE='#EAE5F2';GOLD='#F7EDCE'
WEIGHT=LinearSegmentedColormap.from_list('ohmyplt_weight',['#3D638D','#9AB4CD','#E3E7ED','#D3AD8F','#A76143'])
STYLE={}

def configure(body_font='Arial',math_font='Times New Roman',font_dir=None):
    """Register local fonts and require explicit families, with no silent substitution."""
    directory=font_dir or os.environ.get('OHMYPLT_FONT_DIR')
    if directory:
        for path in sorted(Path(directory).rglob('*')):
            if path.suffix.lower() in ['.ttf','.otf']:font_manager.fontManager.addfont(str(path))
    if os.name=='nt':
        for name in ['arial.ttf','arialbd.ttf','ariali.ttf','arialbi.ttf','times.ttf','timesbd.ttf','timesi.ttf','timesbi.ttf']:
            path=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/name
            if path.is_file():font_manager.fontManager.addfont(str(path))
    paths={}
    for family in [body_font,math_font]:
        try:paths[family]=font_manager.findfont(font_manager.FontProperties(family=family),fallback_to_default=False)
        except ValueError as exc:raise RuntimeError(f'Font unavailable: {family}. Install it, pass --font-dir, or explicitly choose another family.') from exc
    if hasattr(_mathtext,'SHRINK_FACTOR'):_mathtext.SHRINK_FACTOR=.72
    mpl.rcParams.update({'font.family':body_font,'font.size':7,'text.color':INK,
        'mathtext.fontset':'custom','mathtext.rm':math_font,'mathtext.it':f'{math_font}:italic',
        'mathtext.bf':f'{math_font}:bold','mathtext.bfit':f'{math_font}:bold:italic',
        'mathtext.sf':math_font,'mathtext.tt':math_font,'mathtext.cal':f'{math_font}:italic',
        'mathtext.fallback':None,'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white',
        'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':EDGE,'axes.linewidth':.55,
        'xtick.major.width':.55,'ytick.major.width':.55,'xtick.labelsize':6.5,'ytick.labelsize':6.5})
    STYLE.clear();STYLE.update(body_font=body_font,math_font=math_font,font_paths=paths,body_pt=7,math_pt=7.5,script_pt=5.4)
    return STYLE.copy()

def apply_chart_style(ax):
    for label in [*ax.get_xticklabels(),*ax.get_yticklabels()]:
        value=label.get_text().replace('−','-')
        try:float(value);numeric=True
        except ValueError:numeric='$' in value
        label.set_fontfamily(STYLE['math_font'] if numeric else STYLE['body_font'])
    for axis in [ax.xaxis,ax.yaxis]:axis.get_offset_text().set_fontfamily(STYLE['math_font'])
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(length=2,pad=2)
    return ax

class Plate:
    def __init__(self,width_mm,height_mm):
        if not STYLE:configure()
        self.w=float(width_mm);self.h=float(height_mm)
        self.fig=plt.figure(figsize=(self.w/25.4,self.h/25.4))
        self.ax=self.fig.add_axes([0,0,1,1]);self.ax.set(xlim=(0,self.w),ylim=(0,self.h));self.ax.axis('off')
    def text(self,x,y,s,size=None,**kwargs):
        size=(7.5 if '$' in s else 7) if size is None else size
        opts=dict(fontsize=size,color=INK,ha='left',va='center',zorder=6,fontfamily=STYLE['body_font']);opts.update(kwargs)
        return self.ax.text(x,y,s,**opts)
    def panel(self,x,y,letter,title):
        self.text(x,y,letter,8,weight='bold');self.text(x+5,y,title,7,weight='bold')
    def card(self,x,y,w,h,face='white',edge=EDGE,lw=.65,r=1.2,z=1):
        patch=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',
            facecolor=face,edgecolor=edge,lw=lw,zorder=z)
        self.ax.add_patch(patch);return patch
    def port(self,x,y,vertical=True,width=.7,gap=2.5):
        w,h=(width,gap) if vertical else (gap,width)
        patch=Rectangle((x-w/2,y-h/2),w,h,facecolor='white',edgecolor='none',zorder=1.1)
        self.ax.add_patch(patch);return patch
    def wire(self,points,color=INK,lw=.7,r=1.7,arrow=True,ls='-',head=5,z=2):
        points=np.asarray(points,float)
        if points.ndim!=2 or points.shape[1]!=2 or len(points)<2:raise ValueError('A wire needs at least two 2-D points.')
        points=points[np.r_[True,np.linalg.norm(np.diff(points,axis=0),axis=1)>1e-10]]
        if len(points)<2:raise ValueError('A wire must have a nonzero length.')
        vertices=[points[0]];codes=[MPath.MOVETO]
        for i in range(1,len(points)-1):
            prev,here,nxt=points[i-1:i+2];u=here-prev;v=nxt-here
            a,b=np.linalg.norm(u),np.linalg.norm(v);u/=a;v/=b
            rr=min(r,a*.45,b*.45)
            if abs(u[0]*v[1]-u[1]*v[0])<1e-8:vertices.append(here);codes.append(MPath.LINETO)
            else:
                vertices.extend([here-u*rr,here,here+v*rr]);codes.extend([MPath.LINETO,MPath.CURVE3,MPath.CURVE3])
        vertices.append(points[-1]);codes.append(MPath.LINETO)
        patch=FancyArrowPatch(path=MPath(vertices,codes),arrowstyle='-|>' if arrow else '-',
            mutation_scale=head,lw=lw,color=color,linestyle=ls,joinstyle='round',capstyle='round',zorder=z)
        self.ax.add_patch(patch);return patch
    def sigma(self,x,y,radius=2.6,size=9.5):
        self.ax.add_patch(Circle((x,y),radius,facecolor='white',edgecolor=INK,lw=.8,zorder=3))
        glyph=TextPath((0,0),'Σ',size=size,prop=font_manager.FontProperties(family=STYLE['math_font']))
        b=glyph.get_extents();scale=25.4/72
        trans=Affine2D().scale(scale).translate(x-scale*(b.x0+b.x1)/2,y-scale*(b.y0+b.y1)/2)
        self.ax.add_patch(PathPatch(glyph,transform=trans+self.ax.transData,facecolor=INK,edgecolor='none',zorder=6))
        return dict(left=(x-radius,y),right=(x+radius,y),top=(x,y+radius),bottom=(x,y-radius))
    def matrix(self,x,y,w,h,A,maxrows=12,maxcols=16,columns=False,contrast=False,bracket=False):
        A=np.asarray(A,float)
        if A.ndim!=2 or not A.size or not np.isfinite(A).all():raise ValueError('Matrix glyph requires a finite nonempty 2-D array.')
        rows=np.linspace(0,A.shape[0]-1,min(maxrows,A.shape[0]),dtype=int)
        cols=np.linspace(0,A.shape[1]-1,min(maxcols,A.shape[1]),dtype=int);B=A[np.ix_(rows,cols)]
        scale=np.max(abs(B),axis=0,keepdims=True) if columns else np.max(abs(B))
        values=B/np.maximum(scale,1e-30)
        if contrast:values=np.sign(values)*np.sqrt(abs(values))
        nr,nc=values.shape;polys=[];colors=[]
        for i in range(nr):
            for j in range(nc):
                x0,x1=x+w*j/nc,x+w*(j+1)/nc;y1,y0=y+h*(1-i/nr),y+h*(1-(i+1)/nr)
                polys.append([[x0,y0],[x1,y0],[x1,y1],[x0,y1]]);colors.append(WEIGHT((values[i,j]+1)/2))
        self.ax.add_collection(PolyCollection(polys,facecolors=colors,edgecolors='none',linewidths=0,zorder=4))
        if bracket:
            for pts in [[(x-.4,y+h),(x-.8,y+h),(x-.8,y),(x-.4,y)],[(x+w+.4,y+h),(x+w+.8,y+h),(x+w+.8,y),(x+w+.4,y)]]:
                self.wire(pts,lw=.45,r=0,arrow=False,z=5)
        return values
    def history(self,x,y,w,h,t,signals,features,time_unit='h'):
        t=np.asarray(t,float);signals=np.asarray(signals,float);features=np.asarray(features,float)
        if len(t)<2 or not np.all(np.diff(t)>0):raise ValueError('History needs increasing sample times.')
        if signals.ndim!=2 or features.ndim!=2 or signals.shape[0]!=len(t) or features.shape[0]!=len(t):raise ValueError('History rows must match sample times.')
        self.card(x,y,w,h,face='#F8FAFB',z=3)
        self.text(x+w/2,y+h-2.5,'History',ha='center')
        self.text(x+w/2,y+h-6,r'$X\;('+str(len(t))+r'\times'+str(features.shape[1])+r')$',ha='center')
        xx=x+3+(w-6)*(t-t[0])/(t[-1]-t[0]);mid=y+h*.64
        yy=mid+2.3*signals/max(abs(signals).max(),1e-15)
        for k in range(signals.shape[1]):self.ax.plot(xx,yy[:,k],color=BLUE,lw=.45,alpha=.22,zorder=4)
        self.ax.plot(xx,yy[:,0],color=BLUE,lw=.75,zorder=4)
        self.ax.scatter(xx,yy[:,0],s=3,facecolors='white',edgecolors=BLUE,linewidths=.4,zorder=5)
        my=y+8;mh=max(5,h*.25);self.matrix(x+2.5,my,w-5,mh,features.T,maxrows=27,maxcols=len(t))
        for tx in xx:self.wire([(tx,my+mh+.3),(tx,mid-3.2)],color='#A7BAC3',lw=.4,ls=':',arrow=False,z=4)
        ay=y+6.3;self.wire([(x+2.5,ay),(x+w-1.8,ay)],color=BLUE,lw=.5,head=4.2,z=5)
        for tx in xx:self.wire([(tx,ay-.4),(tx,ay+.4)],color=BLUE,lw=.4,arrow=False,z=5)
        for i in [0,len(t)//2,len(t)-1]:self.text(xx[i],y+3.3,f'${t[i]:g}$',ha='center')
        self.text(x+w/2,y-3,r'$t\;(\mathrm{'+time_unit+r'})$',ha='center')
    def gru(self,x,y,w,h,wi,wh):
        wi=np.asarray(wi);wh=np.asarray(wh);hidden=wh.shape[1]
        if wi.shape[0]!=3*hidden or wh.shape!=(3*hidden,hidden):raise ValueError('GRU glyph needs three input and recurrent gate matrices.')
        self.card(x,y,w,h,face=CYAN,edge=INK,z=3);self.text(x+w/2,y+h-2.5,'GRU',ha='center')
        for k in [2,1,0]:
            A=np.c_[wi[k*hidden:(k+1)*hidden],wh[k*hidden:(k+1)*hidden]]
            xx=x+3+.6*k;yy=y+5+.6*k
            self.card(xx-.2,yy-.2,w-5,h-12,face='#F4F7FA',edge='#8B9DAD',lw=.4,r=.1,z=3.2)
            self.matrix(xx,yy,w-5.4,h-12.4,A,maxrows=8,maxcols=12)
        self.wire([(x+w-4,y+h-8),(x+w-2,y+h-8),(x+w-2,y+h-6),(x+3,y+h-6),(x+3,y+h-8)],lw=.55,r=.7,head=4.5,z=5)
        self.text(x+w/2,y+2.2,f'${hidden}$ hidden',ha='center')
    def dense(self,x,y,w,h,W,b):
        W=np.asarray(W);b=np.asarray(b)
        if W.ndim!=2 or b.shape!=(W.shape[0],):raise ValueError('Dense bias must match output width.')
        self.card(x,y,w,h,face=PURPLE,edge=INK,z=3);self.text(x+w/2,y+h-2.5,'Dense',ha='center')
        rows=np.linspace(0,W.shape[0]-1,min(4,W.shape[0]),dtype=int);cols=np.linspace(0,W.shape[1]-1,min(4,W.shape[1]),dtype=int)
        yout=np.linspace(y+10,y+h-7,len(rows));yin=np.linspace(y+10,y+h-7,len(cols));left=x+3;right=x+w-3
        cx=x+w/2;cy=y+7.5;limit=max(abs(W).max(),1e-15)
        for j,yo in zip(rows,yout):
            for i,yi in zip(cols,yin):
                value=W[j,i]/limit;self.ax.plot([left,right],[yi,yo],color=WEIGHT((value+1)/2),lw=.3+.4*abs(value),zorder=4)
            direction=np.array([right-cx,yo-cy]);direction/=np.linalg.norm(direction)
            start=np.array([cx,cy])+direction*1.25;end=np.array([right,yo])-direction*.55
            self.ax.plot([start[0],end[0]],[start[1],end[1]],color=RUST,lw=.45,ls=':',zorder=4)
        for xx,ys in [(left,yin),(right,yout)]:
            for yy in ys:self.ax.add_patch(Circle((xx,yy),.52,facecolor='white',edgecolor='#667689',lw=.55,zorder=5))
        self.ax.add_patch(Circle((cx,cy),1.2,facecolor='white',edgecolor=RUST,lw=.5,zorder=5))
        self.text(cx,cy,'1',6,color=RUST,ha='center',fontfamily=STYLE['math_font'])
        self.text(cx,y+h-5.7,r'$W_1$',ha='center');self.text(cx,y+4.5,r'$b_1$',color=RUST,ha='center')
        self.text(cx,y+1.5,rf'${W.shape[1]}\;\to\;{W.shape[0]}$',ha='center')
    def linear(self,x,y,w,h,W,b):
        W=np.asarray(W);b=np.asarray(b)
        if W.ndim!=2 or b.shape!=(W.shape[0],):raise ValueError('Linear bias must match output width.')
        self.card(x,y,w,h,face=PURPLE,edge=INK,z=3);self.text(x+w/2,y+h-2.5,'Linear',ha='center')
        mw=w-10;mx=x+3;bx=x+w-4
        self.text(mx+mw/2,y+h-7,r'$W_2$',ha='center');self.text(bx+.7,y+h-7,r'$b_2$',color=RUST,ha='center')
        self.matrix(mx,y+8,mw,h-18,W,maxrows=8,maxcols=32,bracket=True)
        self.matrix(bx,y+8,1.4,h-18,b[:,None],maxrows=8,maxcols=1,bracket=True)
        self.text(mx+mw/2,y+5,rf'${W.shape[0]}\times{W.shape[1]}$',ha='center');self.text(bx+.7,y+5,f'${len(b)}$',ha='center')
        self.text(x+w/2,y+1.8,r'$W_2a+b_2$',ha='center')
    def gelu(self,x,y,w,h):
        self.card(x,y,w,h,face=GOLD,edge=INK,z=3);self.text(x+w/2,y+h-2.5,'GELU',ha='center')
        t=np.linspace(-3,3,100);u=.5*t*(1+np.array([math.erf(z/np.sqrt(2)) for z in t]))
        xx=x+2+(t+3)*(w-4)/6;yy=y+5+(u+.35)*(h-12)/3.35
        zero=y+5+.35*(h-12)/3.35
        self.wire([(x+2,zero),(x+w-2,zero)],color='#B9B7AB',lw=.4,arrow=False,z=4)
        self.wire([(x+w/2,y+4.5),(x+w/2,y+h-7)],color='#B9B7AB',lw=.4,arrow=False,z=4)
        self.ax.plot(xx,yy,color='#A67435',lw=1,zorder=4);self.text(x+w/2,y+1.8,r'$a=\mathrm{GELU}(u)$',ha='center')

def check_axes_alignment(fig,axes,mode='row',tolerance_pt=1.5):
    """Check comparable plotting rectangles; call separately for unequal-span groups."""
    if mode not in ['row','column']:raise ValueError('mode must be row or column')
    fig.canvas.draw();w,h=fig.get_size_inches()*72
    boxes=np.array([[a.get_position().x0*w,a.get_position().y0*h,a.get_position().width*w,a.get_position().height*h] for a in axes])
    fields=[1,2,3] if mode=='row' else [0,2,3]
    deviation=float(max((np.ptp(boxes[:,i]) for i in fields),default=0))
    return dict(passed=deviation<=tolerance_pt,max_deviation_pt=deviation,tolerance_pt=tolerance_pt,boxes_pt=boxes.tolist(),mode=mode)

def export(fig,stem,formats=('pdf','svg','png'),dpi=600,source_files=()):
    stem=Path(stem);stem.parent.mkdir(parents=True,exist_ok=True)
    if any(ext not in ['pdf','svg','png'] for ext in formats):raise ValueError('Supported formats: pdf, svg, png')
    messages=[]
    class FontLog(logging.Handler):
        def emit(self,record):messages.append(record.getMessage())
    logger=logging.getLogger('matplotlib');handler=FontLog();logger.addHandler(handler)
    try:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            for ext in formats:fig.savefig(str(stem)+'.'+ext,dpi=dpi,facecolor='white')
        messages.extend(str(w.message) for w in captured)
    finally:logger.removeHandler(handler)
    missing=[s for s in messages if 'glyph' in s.lower() and any(word in s.lower() for word in ['missing','dummy symbol','does not have'])]
    manifest=dict(size_mm=(fig.get_size_inches()*25.4).tolist(),fonts={k:v for k,v in STYLE.items() if k!='font_paths'},
        formats=list(formats),dpi=dpi,warnings=messages,
        inputs=[dict(name=Path(p).name,sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest()) for p in source_files])
    Path(str(stem)+'.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if missing:raise RuntimeError('Missing glyphs in exported figure: '+', '.join(missing))
    return manifest
