"""Turnaround-based meshes for radish through watermelon. Z is up, front is -Y."""
from math import sin, cos, pi, sqrt

TAU = 2 * pi


def plus(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, k):
    return tuple(x * k for x in a)


def unit(a):
    return scale(a, 1 / sqrt(sum(x * x for x in a)))


def cross(a, b):
    x, y, z = a
    u, v, w = b
    return y*w-z*v, z*u-x*w, x*v-y*u


def polar(radius, angle, z):
    return radius*cos(angle), radius*sin(angle), z


def stem(m, pts, radii, color="leaf", sides=6):
    m.tube(pts, radii, color, sides=sides)


def profile(m, center, levels, color, sides=12, lobes=0, depth=0, phase=0):
    rings = []
    for z, radius in levels:
        ring = []
        for j in range(sides):
            a = TAU*j/sides + phase
            r = radius*(1+depth*cos(lobes*a))
            ring.append(plus(center, polar(r, a, z)))
        rings.append(ring)
    cols = [color]*(len(rings)-1) if isinstance(color, str) else color
    m.loft(rings, cols)


def blade(m, base, tip, width, color, style="simple", arch=.08, normal=(0,-.87,.5)):
    """Folded, solid lamina. Profile widths carry the species-specific leaf margin."""
    profiles = {
        "simple": [(0,.045),(.28,.75),(.53,1),(.76,.69),(1,.02)],
        "lobed": [(0,.045),(.18,.42),(.24,.36),(.38,.84),(.46,.61),(.60,1),(.69,.78),(.83,.75),(1,.18)],
        "serrate": [(0,.04),(.29,.77),(.39,.70),(.56,1),(.70,.71),(1,.025)],
        "strap": [(0,.31),(.24,.78),(.55,1),(.79,.65),(1,.025)],
        "petal": [(0,.22),(.33,.76),(.61,1),(.85,.81),(1,.34)],
    }
    direction = tuple(b-a for a,b in zip(base,tip))
    across = unit(cross(direction,normal))
    face = unit(cross(across,direction))
    rings = []
    for t,w in profiles[style]:
        w=max(w,.095) if width<.08 else w
        mid = plus(plus(base,scale(direction,t)), (0,0,arch*sin(pi*t)))
        rings.append([plus(mid,scale(across,-width*w)),
                      plus(mid,scale(face,.26*width*w)),
                      plus(mid,scale(across,width*w)),
                      plus(mid,scale(face,-.17*width*w))])
    m.loft(rings,[color]*(len(rings)-1))


def flower(m, p, r=.16, petals=5, colors=("cream","gold"), normal=(0,-.92,.39)):
    n = unit(normal)
    u = unit(cross((0,0,1),n))
    v = cross(n,u)
    for j in range(petals):
        a = TAU*j/petals+pi/2
        d = plus(scale(u,cos(a)),scale(v,sin(a)))
        lateral=unit(cross(d,n))
        center=plus(p,scale(d,r*.61))
        cap=plus(p,scale(d,r*.98))
        verts=[p,plus(center,scale(lateral,-r*.31)),plus(cap,scale(lateral,-r*.14)),
               plus(cap,scale(lateral,r*.14)),plus(center,scale(lateral,r*.31)),
               plus(center,scale(n,r*.19)),plus(center,scale(n,-r*.085))]
        m.add(verts,[(k,(k+1)%5,5) for k in range(5)]+[((k+1)%5,k,6) for k in range(5)],colors[0])
    m.blob(plus(p,scale(n,.026)),(r*.32,r*.27,r*.32),colors[1],sides=7,rings=3)


def sprig(m, start, end, width, color):
    direction = tuple(b-a for a,b in zip(start,end))
    joint = plus(start,scale(direction,.38))
    stem(m,[start,joint],[.045,.035],color)
    blade(m,plus(start,scale(direction,.365)),end,width,color,"lobed")


def radish(m):
    profile(m,(0,0,0),[(0,.015),(.30,.06),(.47,.105),(.53,.18),(.66,.32),(.86,.385),(1.02,.315),(1.09,.16)],
            ["cream","cream","cream","red","red","red","red"])
    for end,w,c in [((-.95,.23,2.18),.265,"green"),((.88,-.26,2.12),.28,"green"),((.04,.58,2.53),.30,"lime"),((-.52,-.48,1.53),.18,"leaf"),((.63,.43,1.57),.18,"leaf")]:
        sprig(m,(0,0,1.01),end,w,c)
    for x,z in [(-.26,1.67),(.04,1.97),(.31,1.64)]:
        p=(x,-.17,z)
        stem(m,[(0,0,1.03),p],[.035,.023])
        flower(m,p,.132)


def carrot(m):
    profile(m,(0,0,0),[(0,.035),(.40,.105),(.9,.18),(1.26,.25),(1.40,.25),(1.47,.18)],"orange",11)
    for x,y,z in [(-.70,.28,2.47),(.70,-.26,2.39),(0,.24,2.85),(-.64,-.46,1.85),(.63,.48,1.91)]:
        start=(0,0,1.4)
        d=(x,y,z-1.4)
        stem(m,[start,plus(start,scale(d,.49)),plus(start,scale(d,.98))],[.043,.038,.019])
        for t in [.45,.68]:
            mid=plus(start,scale(d,t))
            for sign in [-1,1]:
                end=plus(mid,(x*.14+sign*.14,y*.13+sign*.016,(z-1.4)*.21))
                blade(m,mid,end,.060,"leaf" if sign==-1 else "lime","simple",.015)
        blade(m,plus(start,scale(d,.83)),plus(start,scale(d,1.08)),.073,"lime","simple",.01)
    # Short ochre growth marks sit on three sides of the tapered root.
    for i,(z,r) in enumerate([(.58,.131),(.99,.193),(1.18,.226)]):
        a=-pi/2+(-.43 if i%2 else .52)
        vs=[polar(r+.004,a-.36,z+.015),polar(r+.007,a+.3,z+.012),polar(r+.003,a-.16,z-.018)]
        vs.append(polar(r-.025,a,z))
        m.add(vs,[(0,1,2),(0,3,1),(1,3,2),(2,3,0)],"tan")


def onion(m):
    profile(m,(0,0,0),[(.13,.11),(.20,.28),(.38,.43),(.58,.45),(.70,.39),(.88,.23),(.99,.13),(1.08,.13)],
            ["gold","gold","gold","gold","gold","gold","lime"],12)
    for j in range(9):
        a=TAU*j/9
        stem(m,[polar(.055,a,.16),polar(.136,a+.1,.085),polar(.19,a+.24,.012)],[.035,.026,.009],"tan",5)
    for j,(x,y,z) in enumerate([(-.7,-.12,1.92),(.69,.16,1.96),(.26,.60,2.24),(-.27,.38,2.22),(.02,-.21,2.58),(.14,-.63,1.85)]):
        blade(m,(x*.08,y*.1,1.02),(x,y,z),.115,["lime","leaf","green"][j%3],"strap",.09)


def potato(m):
    # Each ring is an end-on slice. The unequal shoulders create the two
    # distinct humps in front view without a join between separate ellipsoids.
    # Axial cross-sections from the front silhouette: x, half-depth,
    # bottom and top. Tiny rounded end caps retain the outline in side view.
    outline=[(-1.045,.042,.53,.66),(-1.027,.16,.40,.78),(-.975,.29,.29,.91),
             (-.86,.44,.17,1.07),(-.69,.54,.084,1.23),(-.48,.605,.035,1.315),
             (-.27,.623,.013,1.32),(-.06,.632,.008,1.238),(.14,.619,.012,1.115),
             (.35,.611,.039,1.063),(.55,.574,.078,1.072),(.73,.516,.111,1.036),
             (.885,.435,.170,.948),(.99,.318,.269,.82),(1.043,.171,.39,.704),
             (1.056,.044,.516,.60)]
    sections=[(x,r,(bottom+top)/2,(top-bottom)/2) for x,r,bottom,top in outline]
    sides=18
    verts=[]
    for i,(x,ry,mid,rz) in enumerate(sections):
        for j in range(sides):
            a=TAU*j/sides + .038*sin(i*.8+j*.87)
            k=1+.017*sin(2*a+i*.6)+.014*cos(5*a-i*.55)
            warp = .054*sin(a*2.0 + i*.63)*min(1,i/2,(len(sections)-1-i)/2)
            verts.append((x+warp,ry*cos(a)*k,mid+rz*sin(a)*k))
    faces=[]; colors=[]
    def face(ids,col):
        faces.append(ids); colors.append(col)
    face(tuple(reversed(range(sides))),"straw")
    face(tuple(range(len(verts)-sides,len(verts))),"straw")
    eyes={(5,9),(5,6),(10,8),(10,17),(5,2),(1,13),(13,3)}
    for i in range(len(sections)-1):
        for j in range(sides):
            ids=[i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j]
            if (i,j) not in eyes:
                face(ids,"straw")
                continue
            # Inset eye ring and recessed floor are part of the same watertight shell.
            a,b,c,d=[verts[k] for k in ids]
            def sample(t,s):
                return plus(scale(plus(scale(a,1-t),scale(d,t)),1-s),scale(plus(scale(b,1-t),scale(c,t)),s))
            ring=[]
            for t,s in [(.21,.43),(.055,.46),(.22,.67),(.49,.76),
                        (.78,.67),(.945,.46),(.78,.43),(.49,.48)]:
                ring.append(len(verts));verts.append(sample(t,s))
            for k in range(4):
                v0,v1,v2=ring[(2*k)%8],ring[(2*k+1)%8],ring[(2*k+2)%8]
                face([ids[k],ids[(k+1)%4],v1],"straw")
                face([ids[k],v1,v0],"straw")
                face([ids[(k+1)%4],v2,v1],"straw")
            bottom=sample(.49,.61)
            mid=sections[i][2]
            verts.append((bottom[0],bottom[1]*.93,mid+(bottom[2]-mid)*.93))
            for k in range(8):
                face([ring[k],ring[(k+1)%8],len(verts)-1],"tan")
    m.face_colors(verts,faces,colors)


def stump(m, height, width):
    profile(m,(0,0,0),[(0,width*1.35),(height*.3,width),(height,width*.76)],"wood",8)


def tomato(m):
    stump(m,.30,.145)
    stem(m,[(0,0,.22),(-.035,0,.95),(.025,.03,1.73),(.02,0,2.15)],[.12,.09,.055,.029])
    for j,(z,sgn) in enumerate([(.42,-1),(.51,1),(1.04,-1),(1.14,1),(1.62,-1),(1.52,1)]):
        angle=(.43,-.35,-.88,.94,.71,-.54)[j]
        axis=(sgn*cos(angle),sin(angle),0)
        side=(-axis[1],axis[0],0)
        joint=plus(scale(axis,.43),(0,0,z+.27))
        stem(m,[(0,.01,z),joint],[.069,.039])
        for k in range(3):
            fan=plus(scale(axis,.29+.21*(k==1)),scale(side,(k-1)*.24))
            end=plus(plus(joint,fan),(0,0,.14-.22*(k!=1)))
            fruit_leaf(m,joint,end,.161,"leaf" if j%3 else "green",.10)
    for x,z in [(-.29,1.54),(.13,1.34),(-.27,.94),(.17,.80)]:
        top=(x,-.29,z+.13)
        stem(m,[(0,0,z+.21),(x*.66,-.14,z+.24),top],[.039,.033,.026])
        profile(m,(x,-.29,z),[(-.15,.07),(-.12,.14),(.01,.186),(.11,.151),(.142,.066)],"red",8)
        for k in range(4):
            a=TAU*k/4
            fruit_leaf(m,top,plus(top,polar(.123,a,-.046)),.03,"green",.018)
    for x,z in [(0,2.14),(-.22,1.97),(.23,2.05)]:
        if x: stem(m,[(0,0,1.79),(x,0,z)],[.038,.023])
        flower(m,(x,-.01,z),.115,colors=("gold","orange"))

def fruit_leaf(m, base, tip, width, color, arch=.06):
    """Economical folded leaf with an asymmetric tip and closed underside."""
    vec=tuple(b-a for a,b in zip(base,tip))
    lateral=unit(cross(vec,(0,-.83,.56)))
    n=unit(cross(lateral,vec))
    mid=plus(plus(base,scale(vec,.49)),(0,0,arch))
    verts=[base,plus(mid,scale(lateral,-width)),tip,plus(mid,scale(lateral,width)),
           plus(mid,scale(n,width*.32)),plus(mid,scale(n,-width*.19))]
    faces=[(i,(i+1)%4,4) for i in range(4)]+[((i+1)%4,i,5) for i in range(4)]
    m.add(verts,faces,color)


def strawberry(m):
    stump(m,.21,.16)
    for j,(x,y,z) in enumerate([(-.35,-.25,.58),(.31,.33,.55),(0,.26,1.26)]):
        p=(x,y,z)
        stem(m,[(0,0,.14),(x*.48,y*.45,z*.76),p],[.06,.043,.037])
        for k in range(3):
            dx=(k-1)*(.44 if j==2 else .32)+x*.7
            dy=((-0.28,.14,.27),(.32,.20,-.25),(.17,.35,-.04))[j][k]
            end=plus(p,(dx,dy,.49 if j==2 and k==1 else (.20 if j==2 else -.13)))
            blade(m,p,end,.18 if j==2 else .165,"green","serrate",.07)
    for x in [-.46,.46]:
        top=(x,-.24,.82)
        stem(m,[(0,-.015,.16),(x*.43,-.11,.81),(x*.83,-.20,.89),top],[.049,.037,.032,.027])
        profile(m,top,[(-.34,.035),(-.27,.10),(-.16,.17),(-.07,.18),(-.02,.135),(0,.075)],"red",8)
        for k in range(4):
            a=TAU*k/4
            fruit_leaf(m,top,plus(top,polar(.16,a,-.083)),.05,"leaf",.025)
        for j,(z,r) in enumerate([(-.12,.171),(-.23,.13)]):
            for k in range(5):
                a=TAU*k/5+.25*j
                m.blob(plus(top,polar(r*.93,a,z)),(.022,.022,.032),"gold",sides=5,rings=2)
    p=(0,-.135,1.28)
    stem(m,[(0,0,.16),(-.035,-.09,.81),p],[.042,.031,.025])
    flower(m,p,.224)


def blueberry(m):
    stump(m,.25,.16)
    for i,(x,y,z) in enumerate([(-.54,-.26,.57),(.55,.24,.56),(-.31,.43,1.07),(.37,-.41,1.10),(0,.15,1.40)]):
        joint=(x*.66,y*.64,z-.24)
        end=(x,y,z)
        stem(m,[(0,0,.17),joint,end],[.066,.047,.029],"wood",5)
        for k,(dx,dy,dz) in enumerate([(-.34,-.02,.19),(.30,.08,.20),(.045,.21,.32)]):
            spread=(-.23,.25,.34)[k]*(-1 if i in (0,3) else 1)
            fruit_leaf(m,end,plus(end,(dx+x*.24,dy+spread,dz)),.258,"green" if k%2 else "leaf")
        for side in [-1,1]:
            fruit_leaf(m,joint,plus(joint,(side*.36,.035,.17)),.232,"leaf" if side<0 else "green")
        if i in (1,3):
            inner=plus(scale(joint,.80),(0,0,.17*.20))
            fruit_leaf(m,inner,plus(inner,(-x*.96,-y*.65,.33)),.295,"leaf")
        for k,(dx,dz) in enumerate([(-.088,-.041),(.086,-.034),(.006,-.17)]):
            center=(x+dx,y-.078,z+dz)
            m.blob(center,(.109,.106,.113),"blue",sides=7,rings=3)
            # Blossom scar on the berry, set into its outward-facing end.
            m.blob(plus(center,(0,-.090,.048)),(.041,.021,.026),"violet",sides=5,rings=2)
        if i in [1,2,4]:
            flower(m,plus(end,(.006,-.081,.109)),.109)


def tulip(m):
    stump(m,.105,.19)
    stem(m,[(0,0,.068),(-.037,.02,.67),(-.046,.03,1.22),(0,0,1.66)],[.11,.095,.078,.075])
    for tip,w,c in [((-.68,-.055,1.07),.178,"green"),((.71,.015,1.04),.192,"leaf"),((.16,.32,.89),.137,"lime")]:
        blade(m,(0,0,.054),tip,w,c,"strap",.105)
    # Interleaved crown with a hollow interior and a pointed scalloped rim.
    n=18
    rings=[[],[],[],[],[],[]]
    for j in range(n):
        a=TAU*j/n
        tooth=j%3==1
        z=2.25+.17*tooth
        for ring,(r,h) in zip(rings,[(.105,1.54),(.335,1.71),(.375,1.96),(.29 if tooth else .337,z),(.25 if tooth else .293,z-.021),(.14,1.71)]):
            ring.append(polar(r,a,h))
    m.loft(rings,["orange"]*5)
    for j in range(3):
        a=TAU*j/3-pi/2
        # Outer pointed petals cover a third of the cup and fold at their ridge.
        base=polar(.18,a,1.58)
        mid=polar(.384,a,1.91)
        verts=[base,polar(.374,a-.61,1.9),polar(.351,a-.44,2.12),polar(.306,a,2.31),
               polar(.351,a+.44,2.12),polar(.374,a+.61,1.90),plus(mid,polar(.029,a,0)),polar(.283,a,1.91)]
        m.add(verts,[(i,(i+1)%6,6) for i in range(6)]+[((i+1)%6,i,7) for i in range(6)],"orange")


def daffodil(m):
    stump(m,.10,.18)
    for tip,w in [((-.88,.06,.75),.12),((.84,.12,.79),.14),((.56,.09,1.39),.128),((-.36,.10,1.26),.11)]:
        blade(m,(0,0,.053),tip,w,"leaf","strap",.31)
    p=(.07,-.06,1.78)
    stem(m,[(0,0,.06),(-.07,.04,1.14),(-.025,.075,1.68),p],[.075,.065,.045,.044])
    n=unit((0,-1,.21))
    u=(1,0,0); v=cross(n,u)
    for j in range(6):
        a=TAU*j/6+pi/2
        d=plus(scale(u,cos(a)),scale(v,sin(a)))
        blade(m,plus(plus(p,scale(d,.037)),scale(n,.004*j)),plus(p,scale(d,.48)),.156,"cream","petal",.019,n)
    rings=[]
    for depth,r in [(0,.12),(.16,.14),(.32,.197),(.31,.153),(.09,.092)]:
        ring=[]
        for j in range(12):
            a=TAU*j/12
            k=1+.075*cos(a*6)
            ring.append(plus(plus(p,scale(n,depth)),plus(scale(u,r*k*cos(a)),scale(v,r*k*sin(a)))))
        rings.append(ring)
    m.loft(rings,["gold","gold","gold","orange"])
    for x,z in [(-.41,1.17),(.37,.99)]:
        stem(m,[(0,0,.11),(x*.7,0,z*.84),(x,-.02,z)],[.053,.039,.032])
        m.blob((x,-.02,z),(.074,.064,.108),"gold",sides=7,rings=3)


def corn(m):
    stump(m,.145,.195)
    stem(m,[(0,0,.093),(0,.01,.88),(.025,.015,1.6),(0,.035,2.29)],[.111,.10,.077,.052])
    for j,(z,x,lift) in enumerate([(.28,-.54,.18),(.56,.86,.27),(.70,-.91,.23),(1.05,.51,.36),(1.17,-.50,.34),(1.76,.58,.13),(1.86,-.57,.10)]):
        angle=(-.58,.72,-.26,.98,-.81,-.62,.92)[j]
        blade(m,(0,0,z),(x*cos(angle),abs(x)*sin(angle),z+lift),.103 if j>4 else .153,"green" if j%3==1 else "leaf","strap",.22)
    p=(0,-.13,1.32)
    profile(m,p,[(-.37,.072),(-.28,.196),(.02,.241),(.26,.195),(.38,.109),(.43,.045)],"gold",10)
    # Intersecting kernels are broad faceted blocks, with a shallow gap between rows.
    for row,(height,r) in enumerate([(-.24,.18),(-.125,.214),(-.01,.224),(.105,.21),(.217,.187),(.32,.135)]):
        for k in range(8):
            a=TAU*k/8+.06*(row%2)
            m.blob(plus(p,polar(r*.86,a,height)),(.085,.085,.074),"gold",sides=5,rings=2)
    for x in [-.30,.32]:
        blade(m,(0,-.11,.97),(x,-.22,1.53),.108,"leaf","strap",.035)
    for x,y,z in [(0,.035,2.64),(-.25,.02,2.49),(.25,.06,2.50),(-.30,.10,2.34),(.31,0,2.36)]:
        stem(m,[(0,.035,2.16),(x*.50,y,2.16+(z-2.16)*.62),(x,y,z)],[.050,.047,.027],"tan",6)


def raspberry(m):
    stump(m,.25,.145)
    cane=[(0,0,.16),(-.24,.04,.78),(-.31,.08,1.39),(-.19,.08,1.83),(.10,.06,2.04),(.47,.035,2.04),(.69,0,1.92)]
    stem(m,cane,[.105,.087,.074,.066,.058,.047,.026],"wood")
    for i,(base,joint,tip) in enumerate([((-.13,.04,.55),(-.37,-.17,.7),(-.74,-.40,.34)),((-.2,.04,.77),(.12,.22,.98),(.63,.48,.82)),
            ((-.28,.08,1.26),(-.46,.28,1.40),(-.72,.63,1.35)),((-.24,.08,1.65),(-.16,-.13,1.96),(.31,-.39,2.28)),
            ((-.16,.05,.64),(.02,-.26,.68),(.34,-.61,.42))]):
        stem(m,[base,joint],[.056,.035])
        blade(m,joint,tip,.214,"leaf" if i%2 else "green","serrate",.08)
        if i<4:
            fruit_leaf(m,joint,plus(joint,((tip[0]-joint[0])*.64,.19,(tip[2]-joint[2])*.55+.10)),.132,"green")
    for i,(x,z,source) in enumerate([(.14,1.58,(.09,.06,2.035)),(.47,1.73,(.47,.035,2.04)),(.78,1.75,(.66,0,1.94))]):
        top=(x,-.125,z+.11)
        stem(m,[source,(x,-.09,z+.20),top],[.035,.027,.025],"wood",5)
        m.blob(top,(.128,.107,.052),"gold",sides=7,rings=3)
        for dz,r,n in [(0,.091,5),(-.09,.065,4),(-.157,.008,1)]:
            for j in range(n):
                a=TAU*j/n+i*.08+(-dz)*4
                m.blob((x+r*cos(a),-.125+r*sin(a),z+dz),(.078,.077,.081),"red",sides=6,rings=2)
    for x,z in [(-.24,2.05),(-.46,1.83)]:
        stem(m,[(-.29,.065,1.5),(x,0,z)],[.034,.024])
        flower(m,(x,0,z),.14)

def apple_tree(m):
    stump(m,.95,.147)
    for dx,y,z in [(-.55,.005,1.55),(.58,.08,1.55),(.08,.18,1.87)]:
        stem(m,[(0,0,.55),(dx*.52,y*.6,1.04),(dx,y,z)],[.12,.106,.07],"wood")
    for x,y,z,rx,rz,col in [(-.48,.01,1.49,.47,.34,"green"),(.44,.08,1.48,.48,.35,"green"),
           (.03,.24,1.70,.58,.42,"leaf"),(-.21,-.063,1.76,.50,.39,"leaf"),(.32,-.08,1.73,.42,.35,"green"),(.02,.10,2.015,.37,.23,"lime")]:
        m.blob((x,y,z),(rx,rx*.79,rz),col,sides=8,rings=3,phase=x)
    for i,(x,y,z) in enumerate([(-.77,-.09,1.01),(-.37,-.24,.83),(.36,-.25,.87),(.72,-.13,1.04)]):
        stem(m,[(x*.92,y,1.45),(x,y,z+.105)],[.023,.018],"wood",5)
        profile(m,(x,y,z),[(-.124,.056),(-.099,.112),(.024,.145),(.095,.118),(.114,.053)],"red",8)
    for x,y,z in [(-.52,-.23,1.58),(.10,-.29,1.79),(.54,-.19,1.55),(.42,.23,1.72),(-.18,.36,1.79)]:
        fruit_leaf(m,(x,y,z),plus((x,y,z),(.22 if x>.2 else -.22,-.13,-.17)),.104,"lime")
    for p in [(-.54,-.28,1.66),(.12,-.31,1.96),(.64,-.19,1.60)]:
        flower(m,p,.112)


def spiral(m, start, radius, color="leaf"):
    # The spiral starts at the base of the coil and contracts towards its tip.
    pts=[]
    for j in range(14):
        t=j/13
        a=-pi/2+TAU*1.22*t
        r=radius*(1-.79*t)
        pts.append(plus(start,(r*cos(a),.038*t,radius+r*sin(a))))
    stem(m,pts,[.046*(1-.55*j/13) for j in range(14)],color,5)


def vine_leaf(m,base,tip,width,color):
    # A single five-lobed blade with five radiating ridges.
    vec=tuple(b-a for a,b in zip(base,tip))
    side=unit(cross(vec,(0,-.68,.73)))
    normal=unit(cross(side,vec))
    outline=[(0,.0),(.10,-.47),(.28,-.93),(.42,-.61),(.62,-1),(.71,-.45),
             (1,0),(.68,.40),(.60,.93),(.40,.59),(.26,.84),(.10,.42)]
    mid=plus(plus(base,scale(vec,.42)),scale(normal,.07))
    verts=[plus(plus(base,scale(vec,t)),scale(side,width*w)) for t,w in outline]+[mid,plus(mid,scale(normal,-.12))]
    n=len(outline)
    m.add(verts,[(i,(i+1)%n,n) for i in range(n)]+[((i+1)%n,i,n+1) for i in range(n)],color)


def pumpkin(m):
    profile(m,(0,0,0),[(.095,.135),(.14,.36),(.26,.53),(.51,.62),(.68,.60),(.86,.51),(.94,.32),(.91,.115)],"orange",24,8,.10)
    stem(m,[(0,0,.88),(.03,.01,1.10),(.16,.02,1.21),(.34,0,1.16)],[.109,.099,.094,.065],"wood",7)
    for s in [-1,1]:
        stem(m,[(s*.16,0,.18),(s*.50,-.04,.09),(s*.76,-.03,.18)],[.055,.048,.032])
        for i,(dx,dy) in enumerate([(.40,-.24),(.29,.24),(.13,-.39)]):
            base=(s*(.46+i*.06),-.025,.145)
            vine_leaf(m,base,(base[0]+s*dx,dy,.045+i*.013),.18,["green","leaf","leaf"][i])
    start=(-.48,.02,.79)
    stem(m,[(-.43,0,.29),(-.63,.03,.44),start],[.051,.04,.038])
    spiral(m,start,.137)
    for s,z in [(-1,.61),(1,.58)]:
        p=(s*.78,.01,z)
        stem(m,[(s*.56,-.035,.13),(s*.66,0,z*.70),p],[.032,.025,.020])
        if s<0: flower(m,p,.145,colors=("gold","orange"))
        else: m.blob(p,(.068,.068,.107),"gold",sides=7,rings=3)


def watermelon(m):
    # Longitudinal stripes pinch to a rosette at each end of the horizontal fruit.
    levels=[(-1.28,.10),(-1.25,.24),(-1.16,.40),(-1.00,.485),(-.78,.50),(-.57,.50),
            (-.36,.488),(-.18,.398),(-.082,.245),(-.066,.092)]
    n=32; verts=[]; faces=[]; cols=[]
    for i,(x,r) in enumerate(levels):
        for k in range(n):
            a=TAU*k/n
            a+=.039*sin(i*2.0+k*.39)+.024*cos(k*1.18-i*.74)
            verts.append((x,r*cos(a),.508+r*sin(a)))
    for i in range(len(levels)-1):
        for j in range(n):
            faces.append([i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j])
            cols.append("lime" if j%4==0 else "deep")
    faces.extend([tuple(reversed(range(n))),tuple(range(len(verts)-n,len(verts)))])
    cols.extend(["deep","deep"])
    m.face_colors(verts,faces,cols)
    stem(m,[(-.10,0,.51),(.056,.012,.50),(.18,.03,.33),(.37,.056,.22),(.59,.10,.35),(.79,.07,.36),
            (1.04,.09,.25),(1.23,.16,.275),(1.40,.11,.25)],[.082,.074,.058,.046,.043,.042,.037,.035,.03],"leaf",7)
    for anchor,base,end,w in [((.28,.05,.26),(.31,-.14,.23),(.37,-.52,.048),.26),
                               ((.735,.070,.36),(.75,-.042,.24),(.90,-.29,.105),.174),
                               ((1.36,.12,.25),(1.44,.06,.24),(1.73,-.24,.067),.255),
                               ((1.34,.13,.25),(1.45,.20,.22),(1.72,.34,.11),.180)]:
        stem(m,[anchor,base],[.042,.033])
        vine_leaf(m,base,end,w,"leaf" if w<.2 else "lime")
    start=(1.0,.11,.29)
    spiral(m,start,.14)


CROPS=(radish,carrot,onion,potato,tomato,strawberry,blueberry,tulip,daffodil,corn,raspberry,apple_tree,pumpkin,watermelon)


def build(number,m):
    CROPS[number-1](m)
