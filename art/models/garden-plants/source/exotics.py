"""Harvest-ready plants 15–28. Each recipe uses the common indexed mesh builder."""
from math import cos, sin, tau, pi


def offset(p, x=0, y=0, z=0):
    return (p[0]+x, p[1]+y, p[2]+z)


def radial(p, a, r, z):
    return offset(p, r*cos(a), r*sin(a), z)


def body(m, p, levels, colors, sides=10, groove=0, phase=0):
    """Closed ring stack. Alternating sector radii form actual ribs."""
    vs, fs, cs = [], [], []
    for i, (h, rx, ry, dx, dy, turn) in enumerate(levels):
        for j in range(sides):
            a = phase + j*tau/sides + turn
            scale = 1 - groove*(j%2)
            vs.append(offset(p, dx + rx*scale*cos(a), dy + ry*scale*sin(a), h))
            if i:
                k = (i-1)*sides+j
                nxt = (i-1)*sides+(j+1)%sides
                fs.append((k,nxt,nxt+sides,k+sides))
                cs.append(colors(i-1,j) if callable(colors) else colors)
    fs.extend((tuple(reversed(range(sides))), tuple(range(len(vs)-sides,len(vs)))))
    cs.extend((cs[0], cs[-1]))
    m.face_colors(vs,fs,cs)


def profile(m,p,levels,colors,sides=10,groove=0,phase=0):
    body(m,p,[(h,r,r,0,0,0) for h,r in levels],colors,sides,groove,phase)


def blade(m, p, angle, length, rise, width, color, arch=.12, shape=None):
    """Radial folded blade with an angular midrib and optional lobed edges."""
    if shape is None:
        shape = ((.30,.84),(.62,1.0))
    verts = [p]
    faces = []
    prev = None
    for t, w in shape:
        mid = radial(p,angle,length*t,rise*t+arch*sin(pi*t))
        d = w*width
        start = len(verts)
        bank = .57*cos(angle) * min(1,abs(length)/max(.001,abs(rise)))
        verts.extend((radial(mid,angle-pi/2,d,-bank*d),offset(mid,z=.30*d),
                      radial(mid,angle+pi/2,d,bank*d),offset(mid,z=-.13*d)))
        for j in range(4):
            k = (j+1)%4
            if prev is None:
                faces.append((0,start+k,start+j))
            else:
                faces.append((prev+j,prev+k,start+k,start+j))
        prev = start
    tip = len(verts)
    verts.append(radial(p,angle,length,rise))
    for j in range(4):
        faces.append((prev+j,prev+(j+1)%4,tip))
    m.add(verts,[f[::-1] for f in faces],color)


def roots(m, radius=.34, base=(0,0,0)):
    for a in (.05,2.36,4.30):
        m.tube([offset(base,z=.25),radial(base,a,radius*.6,.10),radial(base,a,radius,.035)],
               [.13,.10,.045],'wood',5)


def flower(m,p,size,petal='cream',middle='gold',tilt=.75):
    """Five corolla lobes arranged on a sloping plane toward the viewer."""
    for j in range(5):
        a = j*tau/5+pi/2
        m.blob(offset(p,.59*size*cos(a),.59*size*sin(a)*(1-tilt),
                      .59*size*sin(a)*tilt), (size*.48,size*.29,size*.44),petal,5,2)
    m.blob(offset(p,y=-.20*size,z=.1*size),(size*.34,size*.22,size*.34),middle,6,2)


def blossom(m, p, radius, petal, tilt=.83, rotation=0):
    """Five scalloped petals in one solid corolla with a contrasting centre."""
    outline=[]
    for k in range(5):
        for delta,scale in ((-.40,.52),(-.22,.92),(.20,1)):
            a=(k+delta)*tau/5+rotation
            outline.append((radius*scale*cos(a),radius*scale*sin(a)))
    side=(1-tilt**2)**.5
    def pos(x,y,depth):
        return offset(p,x,side*y-tilt*depth,tilt*y+side*depth)
    vs=[pos(0,0,-radius*.24)]
    vs.extend(pos(x,y,.15*radius) for x,y in outline)
    vs.extend(pos(x*.28,y*.28,.24*radius) for x,y in outline)
    top=len(vs)
    vs.append(pos(0,0,.34*radius))
    faces=[]; shades=[]
    for j in range(15):
        a,b=j+1,(j+1)%15+1
        faces.extend(((0,b,a),(a,b,b+15,a+15),(a+15,b+15,top)))
        shades.extend((petal,petal,'gold'))
    m.face_colors(vs,faces,shades)

def bamboo(m):
    for i,(x,y,h,lean) in enumerate(((0,.08,2.64,0),(-.18,-.01,1.94,-.18),(.20,.07,1.40,.17))):
        n=5 if i==0 else 4
        levels=[]
        for j in range(n):
            for t,r in ((0,.109),(.84,.081),(.90,.115)):
                z=(j+t)*h/n
                levels.append((z,r,r,lean*z/h,0,0))
        body(m,(x,y,.009*i),levels,lambda s,j:'lime' if s%3==2 else ('green' if j%4 else 'leaf'),7)
        for j in range(2 if i==0 else 1,n+1,2):
            base=(x+lean*j/n,y,h*(j-.12)/n)
            a=(j*.76+i*1.68)
            for k in range(4):
                blade(m,base,a+k*1.49,.46+.065*(k%2),-.20+.09*(k%3),.074,
                      ('leaf','lime','green','leaf')[k],.15)
        base=(x+lean,y,h*.96+.009*i)
        for k in range(3):
            blade(m,base,i+.35+k*tau/3,.47,-.09,.078,'leaf',.14)
    roots(m,.40)


def palm(m):
    heights=[0,.20,.46,.75,1.01,1.26,1.46,1.60]
    body(m,(0,0,0),[(z,.22-.048*z,.21-.045*z,.23*z,0,.03*z) for z in heights],
         lambda i,j: ('bark','wood')[i%2],8)
    roots(m,.48)
    top=(.36,0,1.60)
    for j in range(6):
        a=-pi+.31+j*tau/6
        split=((.20,.62),(.39,1),(.48,.48),(.52,.97),(.66,.85),(.73,.40),(.77,.67))
        blade(m,top,a,1.0,-.48+.33*(j%3),.27,('leaf','green','lime')[j%3],.46,split)
    for j in range(3):
        blade(m,top,.61+j*tau/3,.64,.23+.12*(j%2),.18,'leaf',.29)
    for j in range(3):
        c=radial(top,-pi/2+j*tau/3,.20,-.24-(j==0)*.10)
        m.blob(c,(.205,.19,.235),'bark',8,3,phase=j*.4)
    for j in range(2):
        flower(m,offset(top,(j-.5)*.18,-.13,.06*j),.115)


def cactus(m):
    profile(m,(0,0,0),[(0,.30),(.16,.31),(.27,.43),(1.64,.43),(1.80,.33),(1.86,.19)],
            lambda i,j: 'wood' if i==0 else ('green','leaf','green','deep')[j%4],12,.11)
    for x,y,h in ((-1,.035,1.52),(1,-.035,1.23)):
        pts=[(.24*x,y,.80),(.58*x,y,.84),(.73*x,y,1.02),(.74*x,y,h),(.74*x,y,h+.055)]
        m.tube(pts,[.155,.16,.15,.14,.10],'green',8)
        for a,z in ((-1.75,1.02),(-1.28,h-.08)):
            m.blob((.73*x+.135*cos(a),y+.135*sin(a),z),(.04,.032,.045),'cream',5,2)
        if x>0: flower(m,(.74*x,-.075,h+.095),.142,'red')
    for j in range(10):
        a=j*2.4
        m.blob((.403*cos(a),.403*sin(a),.36+.14*j),(.043,.043,.054),'cream',5,2)


def pineapple(m):
    profile(m,(0,0,0),[(0,.16),(.11,.21),(.97,.115),(1.19,.12)],lambda i,j:'wood' if i==0 else 'green',7)
    for j in range(10):
        blade(m,(0,0,.075),.32+j*2.4,.74+(.17 if j%2 else 0),.25+.14*(j%4),.14,
              ('leaf','green','lime')[j%3],.23)
    # Alternating stepped rings form a true triangular diamond lattice.
    verts=[]; faces=[]; colors=[]
    n=9
    for i,(h,r) in enumerate(((.91,.14),(1.02,.235),(1.16,.29),(1.33,.31),(1.49,.28),(1.62,.21),(1.68,.12))):
        for j in range(n):
            a=(j+.5*(i%2))*tau/n
            verts.append((r*cos(a),r*sin(a),h))
    for i in range(6):
        for j in range(n):
            ix=lambda row,col: row*n+col%n
            a,b,c,d=ix(i,j),ix(i,j+1),ix(i+1,j),ix(i+1,j+1)
            faces.extend(((a,b,c),(b,d,c)) if i%2==0 else ((a,b,d),(a,d,c)))
            colors.extend(('gold','orange') if (j+i)%3 else ('straw','gold'))
    faces.extend((tuple(reversed(range(n))),tuple(range(6*n,7*n))))
    colors.extend(('orange','gold'))
    m.face_colors(verts,faces,colors)
    for j in range(9):
        blade(m,(0,0,1.62),j*2.4,.22+.07*(j%2),.21+.14*(j%3),.066,
              ('green','leaf','lime')[j%3],.04)


def fruit_tree(m,cacao):
    roots(m,.38)
    fork=(.045,0,.63 if not cacao else .98)
    m.tube([(0,0,0),(-.03,.005,.35),fork,(.02,.08,1.53),(0,.06,1.89)],
           [.195,.139,.115,.091,.062],'wood',8)
    hubs=[]
    for j,a in enumerate((.14,2.92,4.95)):
        hub=radial((0,.08,1.76),a,.48,-.08*(j%2))
        m.tube([fork,radial(fork,a,.35,.34),hub],[.113,.082,.043],'wood',6)
        hubs.append(hub)
    hubs.append((0,.06,1.95))
    for j,h in enumerate(hubs):
        for k in range(4):
            a=.33+.53*j+k*tau/4
            blade(m,h,a,.54+.09*(k%2),-.43+.065*j,.20 if not cacao else .24,
                  ('green','leaf','deep','lime')[(k+j)%4],.32)
    if not cacao:
        for k in range(6):
            blade(m,hubs[-1],.44+k*tau/6,.62,-.25,.15,('leaf','green','lime')[k%3],.23)
    if cacao:
        for j,p in enumerate(((.07,-.10,.66),(-.10,-.05,1.00),(.11,-.035,1.28),
                              (.49,.08,1.66),(-.46,.14,1.64),(.105,-.345,1.70))):
            a=(-1.28,3.9,-.58,.08,2.92,4.95)[j]
            crown=radial(p,a,.065,-.045)
            m.tube([p,crown],[.034,.028],'wood',5)
            body(m,crown,[(z,r,.88*r,.20*z*cos(a),.20*z*sin(a),0) for z,r in
                          ((-.34,.016),(-.26,.096),(-.13,.133),(-.05,.10),(0,.03))],
                 lambda i,k: ('red','gold','gold','orange','orange','orange')[j] if k%2==0 else ('red','orange','orange','tan','tan','tan')[j],8,.18)
        for p in ((-.11,-.12,.42),(.08,-.10,1.19)):
            flower(m,p,.072)
    else:
        for j,h in enumerate(hubs[:3]):
            a=(.14,2.92,4.95)[j]
            bottom=radial(h,a,.14,-.47-.065*(j%2))
            m.tube([h,radial(h,a,.10,-.15),bottom],[.026,.022,.019],'tan',5)
            body(m,bottom,[(z,r,.8*r,dx,0,0) for z,r,dx in
                           ((-.37,.047,-.065),(-.29,.14,-.035),(-.15,.168,.005),(-.055,.139,.021),(0,.055,0))],
                 lambda i,k:'red' if i==3 and k%8 in (5,6) else ('orange' if i>=2 else 'gold'),8)

def pitaya(m):
    profile(m,(0,0,0),[(0,.275),(.13,.26),(1.1,.32),(1.82,.24),(1.9,.13)],
            lambda i,j: 'wood' if i==0 else ('deep','green','leaf')[j%3],9,.24)
    blossom(m,(0,-.055,1.93),.25,'cream',.72,.32)
    for j,a in enumerate((.06,3.34,4.83)):
        top=(0,0,1.83-.07*j)
        end=radial(top,a,.72,-.56)
        m.tube([top,radial(top,a,.34,-.04),radial(top,a,.56,-.23),end],
               [.16,.156,.135,.093],'green',5)
        fruit=offset(end,z=-.20)
        body(m,fruit,[(z,r,r*.91,0,0,0) for z,r in ((-.275,.035),(-.18,.16),(.01,.21),(.17,.173),(.265,.054))],
             lambda level,k: 'red' if level==0 or (level==1 and k%4==0) else 'berry',9,phase=.18*j)
        for k in range(8):
            b=k*2.40
            p=radial(fruit,b,.173 if k%2 else .157,.03 if k%2 else -.11)
            blade(m,p,b,.063,.15,.054,'lime',.012)
        if j<2: blossom(m,offset(radial(top,a,.43,.016),y=-.045),.15,'cream',.85,.12)


def snowdrop(m):
    profile(m,(0,0,0),[(0,.15),(.08,.16),(.12,.12)],'wood',8)
    for j,(dx,dy,h) in enumerate(((-.49,.10,1.43),(.24,.20,2.0),(.54,-.08,1.35))):
        base=(0,0,.08)
        p=(dx,dy,h-.16)
        m.tube([base,(dx*.28,dy*.5,h*.70),(dx*.5,dy*.8,h*.94),
                (dx*.74,dy,h), (dx*.94,dy,h-.035),p],
               [.043,.040,.038,.037,.035,.033],'green',7)
        m.blob(p,(.088,.088,.105),'leaf',7,3)
        # The bell opens downwards, the three lower points stay separate.
        for k in range(3):
            a=k*tau/3+j*.46
            blade(m,offset(p,z=-.035),a,.135,-.28,.095,'cream',-.01,
                  ((.21,.56),(.61,1),(.81,.80)))
        m.blob(offset(p,z=-.18),(.069,.070,.078),'lime',6,2)
    for a,r,h in ((3.35,.56,.77),(-.26,.52,.87),(1.37,.29,.68)):
        blade(m,(0,0,.07),a,r,h,.13,'leaf',.13)


def snowberry(m):
    profile(m,(0,0,0),[(0,.235),(.14,.16),(.18,.11)],'wood',7)
    for j,(x,y,h) in enumerate(((-.46,.08,1.03),(.04,.14,1.53),(.50,-.02,1.09),(.04,-.25,.78))):
        mid=(x*.57,y*.52,h*.58); p=(x,y,h)
        m.tube([(0,0,.12),mid,p],[.068,.055,.031],'deep',6)
        a=(pi if x<0 else 0)+j*.18
        blade(m,mid,a,.38,.13,.14,'green',.088)
        blade(m,offset(p,z=-.03),a+1.7,.37,.30,.115,'leaf',.065)
        blade(m,p,a-.19,.34,.16,.13,'green',.075)
        for k in range(3):
            fruit=radial(p,-pi/2+k*tau/3,.089,-.068-.045*(k==0))
            m.blob(fruit,(.109,.098,.107),'snow',7,3)
        flower(m,offset(p,y=-.052,z=.044),.089,'violet','gold')


def spiral(m,p,a,r,color):
    pts=[p]
    for i in range(11):
        t=i/10
        theta=-pi/2+t*1.82*pi
        radius=r*(1-.70*t)
        pts.append(radial(p,a,radius*cos(theta),r+radius*sin(theta)))
    # Start at the first circular sample; its bottom coincides with p.
    m.tube(pts[1:],[.030-.018*i/10 for i in range(11)],color,5)


LOBES=((.16,.42),(.30,.94),(.41,.73),(.51,1),(.64,.55),(.74,.61))


def grape_bead(m,p,r,phase):
    # Staggered pentagons make a rounded icosahedron without square sides.
    vs=[offset(p,z=-r)]
    for j in range(2):
        for k in range(5):
            vs.append(radial(p,phase+(k+.5*j)*tau/5,r*.894,r*(j*2-1)*.447))
    vs.append(offset(p,z=r))
    fs=[]
    for k in range(5):
        a,b=1+k,1+(k+1)%5
        fs.extend(((0,b,a),(a,b,a+5),(b,b+5,a+5),(11,a+5,b+5)))
    m.add(vs,fs,'ice')


def grape(m):
    roots(m,.38)
    fork=(.025,.02,1.15)
    m.tube([(0,0,.04),(.17,0,.45),(-.095,.04,.76),fork,(-.04,.04,1.63)],
           [.13,.12,.11,.098,.06],'wood',6)
    shape=((.19,.72),(.31,1.0),(.43,.66),(.56,.90),(.72,.52))
    for j,(x,y) in enumerate(((-.53,.025),(.54,.08))):
        hub=(x,y,1.40+.10*j)
        m.tube([fork,(.55*x,y,1.32),hub],[.10,.073,.043],'wood',5)
        side=pi if x<0 else 0
        blade(m,(.55*x,y,1.32),side+(-.54 if j else .54),.34,.17,.22,'deep',.16,shape)
        blade(m,hub,side+.13,.43,-.41,.235,'leaf',.18,shape)
        blade(m,hub,side+1.47,.43,-.30,.24,'green',.17,shape)
        hanger=(x*.81,y-.14,1.22)
        m.tube([hub,offset(hanger,z=-.102)],[.036,.032],'leaf',5)
        for k in range(4):
            a=k*tau/4+.39*j
            grape_bead(m,radial(hanger,a,.120,-.103),.143,k*.38)
        for k in range(3):
            grape_bead(m,radial(hanger,k*tau/3,.077,-.251),.129,k*.48)
        grape_bead(m,offset(hanger,z=-.391),.099,.12)
        flower_base=offset(hub,x=-.065 if x>0 else .065,y=-.20,z=.10)
        m.tube([hub,flower_base],[.038,.026],'leaf',5)
        blossom(m,flower_base,.135,'cream',.91,.28*j)
    stem=(-.04,.04,1.63)
    tendril=offset(stem,x=.035,z=.14)
    m.tube([stem,tendril],[.037,.028],'leaf',5)
    spiral(m,tendril,.15,.14,'leaf')
    for k,(a,length) in enumerate(((2.81,.49),(.16,.48),(-1.34,.40))):
        blade(m,stem,a,length,-.28+.04*(k%2),.24,'green' if k%2==0 else 'leaf',.21,shape)

def frost_melon(m):
    # Ice segments follow the curvature of the rind around a low broad core.
    c=(0,.03,0)
    levels=((.04,.39),(.12,.64),(.35,.80),(.58,.83),(.79,.73),(.94,.51),(1.01,.19))
    body(m,c,[(z,r,.81*r,0,0,0) for z,r in levels],
         lambda i,j: (('ice','snow','snow','ice')[j%4] if i>1 else 'ice'),24,.12,phase=.045)
    m.tube([(0,.03,.98),(-.01,.03,1.12),(.065,.04,1.24),(.18,.043,1.27),(.24,.05,1.23)],
           [.10,.095,.076,.065,.046],'green',7)
    path=[(-.65,.07,.18),(-.90,-.08,.16),(-.73,-.40,.11),(-.37,-.54,.07),
          (.29,-.53,.075),(.64,-.34,.105),(.91,-.19,.16)]
    m.tube(path,[.054,.062,.071,.067,.062,.055,.033],'green',7)
    spiral(m,path[1],pi,.12,'green')
    for p,a,l in ((path[1],3.55,.45),(path[3],4.87,.37),(path[-1],-.26,.41)):
        blade(m,p,a,l,.045-p[2],.18,'leaf',.105,LOBES)
    # Six close-set icy branches raised on the broad front segment.
    def rind_point(x,z):
        for (z0,r0),(z1,r1) in zip(levels,levels[1:]):
            if z0 <= z <= z1:
                radius = r0+(r1-r0)*(z-z0)/(z1-z0)
                break
        ring=[]
        for j in range(24):
            a=j*tau/24+.045
            r=radius*(1-.12*(j%2))
            ring.append((r*cos(a),.03+.81*r*sin(a)))
        hits=[]
        for (x0,y0),(x1,y1) in zip(ring,ring[1:]+ring[:1]):
            if min(x0,x1) <= x <= max(x0,x1):
                hits.append(y0+(y1-y0)*(x-x0)/(x1-x0))
        return (x,min(hits)-.009,z)
    start=rind_point(.016,.52)
    for k in range(6):
        a=k*tau/6+pi/2
        def mark(t):
            return rind_point(start[0]+t*cos(a),start[2]+t*sin(a))
        mid=mark(.086)
        m.tube([start,mid,mark(.15)],[.014,.013,.009],'blue',5)
        for side in (-1,1):
            tip=rind_point(mid[0]+.052*cos(a+side*.75),mid[2]+.052*sin(a+side*.75))
            m.tube([mid,tip],[.010,.006],'blue',4)

def rose(m):
    base=(0,0,1.39)
    m.tube([(0,0,0),(.017,0,.36),(0,.006,.88),base],[.065,.050,.045,.056],'leaf',7)
    profile(m,(0,0,0),[(0,.11),(.08,.08),(.13,.054)],'wood',7)
    for j in range(5):
        a=j*2.4
        m.tube([(0,0,.24+.18*j),radial((0,0,.24+.18*j),a,.102,.088)],[.038,.008],'lime',4)
    for j,a in enumerate((.03,3.25)):
        blade(m,(0,0,.63+.08*j),a,.60,.27,.177,'green',.055)
    # Rose cups tilt toward the front. Individual wrap-around polygonal
    # petals overlap spirally and have a thick, beveled five-sided rim.
    def tilted(x,y,z):
        return offset(base,x,.83*y-.558*z,.558*y+.83*z)
    for row,(n,r,h,tone) in enumerate(((6,.60,.55,'violet'),(5,.44,.65,'pink'),(4,.286,.71,'violet'),(3,.143,.73,'pink'))):
        for j in range(n):
            a=j*tau/n+row*.81
            z0=.03+row*.115
            rim=[(-.67,.55,.14),(-.60,.88,.76),(-.23,1.04,1.0),(.27,1.03,.94),(.64,.88,.72),(.66,.55,.16)]
            def v(t,s,z, inset=0):
                return tilted((s*r-inset)*cos(a+t),(s*r-inset)*sin(a+t),z0+z*(h-z0))
            verts=[v(t,s,z) for t,s,z in rim]+[v(t,s,z,.055) for t,s,z in rim]
            verts.extend([v(0,1.03,.60),v(0,.80,.56)])
            faces=[]; colors=[]
            for k in range(6):
                b=(k+1)%6
                faces.extend(((12,k,b),(13,b+6,k+6),(k,k+6,b+6,b)))
                colors.extend((tone,tone,'pink' if row%2==0 else 'violet'))
            m.face_colors(verts,faces,colors)
    for j in range(5):
        blade(m,offset(base,z=-.07),j*tau/5,.29,.20,.10,'green',.03)

def moonflower(m):
    stem=[(-.06,0,0),(-.07,.01,.14),(.14,0,.42),(.11,.025,.58),
          (-.14,.05,.81),(-.22,.025,.97),(-.13,.03,1.12),(.015,.02,1.35)]
    m.tube(stem,[.122,.10,.094,.093,.083,.079,.076,.07],'blue',7)
    for j,(p,a) in enumerate(((stem[2],3.25),(stem[4],.08))):
        bud=radial(p,a,.18,.13)
        m.tube([p,bud],[.053,.028],'blue',6)
        blade(m,bud,a,.45,.23,.166,'leaf',.18,((.16,.84),(.35,1),(.56,.88)))
    p=(-.56,.015,1.09)
    m.tube([stem[4],(-.36,.02,.84),(-.49,.02,.92),p],[.051,.04,.035,.029],'blue',6)
    # Tapered horn curls up around the empty centre of the lunar bud.
    curve=[(-.48,.015,1.25),(-.54,0,1.26),(-.61,0,1.21),(-.62,0,1.13),
           (-.55,-.01,1.08),(-.50,-.01,1.10),(-.47,-.01,1.15)]
    m.tube(curve,[.008,.039,.058,.066,.064,.043,.009],'gold',7)
    bottom=stem[-1]
    # A funnel with five alternating high points and a visible folded interior.
    rings=[]
    for r,h,pleat in ((.072,0,0),(.13,.10,.01),(.25,.28,.055),(.48,.51,.16),
                      (.447,.49,.16),(.21,.25,.05),(.059,.14,0)):
        ring=[]
        for k in range(10):
            a=k*tau/10+pi/2
            z=h+pleat*(1 if k%2==0 else -.40)
            rr=r*(1 if k%2==0 else .82)
            x,y=rr*cos(a),rr*sin(a)
            ring.append(offset(bottom,x,y*.91-z*.414,y*.414+z*.91))
        rings.append(ring)
    m.loft(rings,['shadow','cream','cream','snow','cream','straw'])
    for j in range(3):
        low=radial(offset(bottom,y=-.05,z=.12),j*tau/3,.035,0)
        high=offset(low,y=-.06,z=.17+.025*j)
        m.tube([low,high],[.019,.020],'straw',5)
        m.blob(high,(.038,.038,.073),'gold',6,3)


def sakura(m):
    roots(m,.41)
    trunk=[(0,0,.01),(-.10,0,.28),(.16,.03,.57),(-.09,.07,.93),(.11,.08,1.17),(.03,.1,1.65)]
    m.tube(trunk,[.18,.16,.14,.11,.097,.063],'bark',7)
    for j,(x,y,z) in enumerate(((-.69,.08,1.25),(.71,.07,1.39),(-.20,-.24,1.01),(.03,.16,1.79))):
        hub=(x,y,z)
        base=trunk[(3,4,2,5)[j]]
        m.tube([base,((base[0]+x)*.5,y-.015,z-.22),hub],[.080,.063,.036],'bark',6)
        r=(.38,.39,.26,.47)[j]
        # A continuous scalloped cap. A wavy material boundary makes the snow
        # sit over the pink flowers without a second overlapping shell.
        rings=[]
        n=10
        for level,(width,height) in enumerate(((.40,-.24),(.91,-.02),(1,.30),(.72,.63),(.28,.82))):
            ring=[]
            for k in range(n):
                a=(k+.13*j+.15*(level%2))*tau/n
                scallop=1 if k%2 else .85
                wave=sin(k*2.8+j)*(.15 if level==2 else .055)
                ring.append(offset(hub,r*width*scallop*cos(a),r*.84*width*scallop*sin(a),r*(height+wave)))
            rings.append(ring)
        m.loft(rings,['pink','pink','snow','snow'])
        for k,a in enumerate((-1.56,1.20+j*.22)):
            center=offset(hub,.86*r*cos(a),.715*r*sin(a),.13*r)
            # Each separate five-petal flower follows its own side of the puff.
            size=r*(.46 if k==0 else .36)
            verts=[radial(center,a,-.08*size,0),radial(center,a,.19*size,0)]
            for t in range(15):
                b=t*tau/15+.32*j
                length=size*(.52 if t%3==0 else 1.0)
                verts.append(radial(center,a+pi/2,length*cos(b),length*sin(b)))
            faces=[]; shades=[]
            for t in range(15):
                i1,i2=2+t,2+(t+1)%15
                faces.extend(((0,i2,i1),(1,i1,i2)))
                shades.extend(('pink','berry' if k==0 else 'pink'))
            m.face_colors(verts,faces,shades)
            if k==0:
                m.blob(radial(center,a,.18*size,0),(.28*size,.19*size,.28*size),'gold',5,2)
        if j<3:
            for k in range(2):
                anchor=offset(hub,(k-.5)*.066,y=-.08)
                end=offset(anchor,(k-.5)*.09,y=-.07,z=-.16-.035*k)
                m.tube([anchor,end],[.016,.013],'leaf',4)
                m.blob(end,(.063,.059,.062),'red',6,2)
            blade(m,offset(hub,z=-.035),.30 if x>0 else 3.49,.28,-.13,.079,'green',.06)


def build(number,m):
    recipes={15:bamboo,16:palm,17:cactus,18:pineapple,19:lambda m:fruit_tree(m,False),
             20:pitaya,21:lambda m:fruit_tree(m,True),22:snowdrop,23:snowberry,24:grape,
             25:frost_melon,26:rose,27:moonflower,28:sakura}
    recipes[number](m)
