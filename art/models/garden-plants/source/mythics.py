"""Silhouette-led construction for the eight magical garden plants."""
from math import cos, sin, pi, tau


def polar(origin, r, a, z):
    return (origin[0] + r*cos(a), origin[1] + r*sin(a), origin[2] + z)


def strip(m, centers, widths, lateral, normal, depths, colors):
    """Four-sided changing profile. Ridges keep the petal solid on both faces."""
    rings = []
    for p, w, d in zip(centers, widths, depths):
        rings.append([tuple(p[j] + lateral[j]*u + normal[j]*v for j in range(3))
                      for u, v in [(w, 0), (0, d), (-w, 0), (0, -d*.55)]])
    m.loft(rings, colors)


def petal(m, origin, a, profile, colors):
    centers = [polar(origin, r, a, z) for r, z, w, d in profile]
    strip(m, centers, [s[2] for s in profile], (-sin(a), cos(a), 0),
          (0, 0, 1), [s[3] for s in profile], colors)


def rosette(m, origin, spread, rise, width, count, offset=0, colors=('leaf','green')):
    for i in range(count):
        a = tau*i/count + offset
        blade(m, origin, a, spread*(1-.06*(i%2)), rise, width, colors[i%len(colors)],
              .68*(-1 if i%2 else 1))


def blade(m, origin, a, length, rise, width, color, roll):
    # Roll some blades toward the player so their wide faces show from the ground.
    cx,cy,cz=polar(origin,length*.52,a,rise*.54+length*.19)
    dx,dy,dz=-sin(a)*cos(roll),cos(a)*cos(roll),sin(roll)
    verts=[origin]
    for t,sign in [(.3,-1),(.66,-1),(1,0),(.66,1),(.3,1)]:
        x,y,z=polar(origin,length*t,a,rise*t+length*.15*sin(t*pi))
        breadth=width*sign*(.85 if t<.5 else 1)
        verts.append((x+breadth*dx,y+breadth*dy,z+breadth*dz))
    verts.extend([(cx,cy,cz+width*.34),(cx,cy,cz-width*.45)])
    faces=[]
    for i in range(6):
        j=(i+1)%6
        faces.extend([(6,i,j),(7,j,i)])
    m.add(verts,faces,color)


def stem(m, pts, radii, color='wood', sides=7):
    m.tube(pts, radii, color, sides=sides)


def base_roots(m, scale=1):
    for i in range(4):
        a = tau*i/4 + .4
        stem(m, [polar((0,0,0), .05*scale,a,.17*scale),
                 polar((0,0,0), .17*scale,a,.10*scale),
                 polar((0,0,0), .32*scale,a,.045*scale)],
             [.12*scale,.105*scale,.045*scale], sides=5)


def canopy(m, center, width, color='green', count=7):
    x,y,z = center
    m.blob((x,y,z+.075), (width*.95,width*.73,width*.53),color, sides=7,rings=3)
    for i in range(count):
        a=tau*i/count+.22
        base=polar((x,y,z),.08*width,a,.53*width)
        blade(m,base,a,width*.95,-width*(.60+.12*(i%2)),width*.39,
              ('leaf',color,'green')[i%3],.45*(-1 if i%2 else 1))


def blossom(m, center, scale):
    # Broad petals in the vertical plane, attached to a raised central boss.
    x,y,z = center
    for i in range(5):
        a=tau*i/5+.3
        m.blob((x+cos(a)*scale*.58,y,z+sin(a)*scale*.58),
               (scale*.46,scale*.21,scale*.46),'straw',sides=5,rings=2)
    m.blob((x,y-scale*.14,z),(scale*.36,scale*.29,scale*.35),'orange',sides=6,rings=2)


def pomegranate(m):
    stem(m,[(0,0,.02),(-.05,0,.40),(.15,.02,.90),(.02,.05,1.43),(.06,.06,1.90)],
         [.16,.105,.10,.06,.04])
    for x,z in [(-.52,1.48),(.56,1.54)]:
        stem(m,[(0,0,.35),(x*.70,.03,.80),(x,.05,1.17),(x,.03,z+.22)],
             [.096,.086,.065,.043])
        for k in range(3):
            h=.91+.36*k
            rosette(m,(x*(.79+.09*k),.04,h),.51,.20-.09*k,.173,5,.32+.5*k)
        m.blob((x,-.08,z-.15),(.275,.255,.30),'red',sides=9,rings=4)
        stem(m,[(x,0,z+.22),(x,-.06,z+.11)],[.037,.028],'wood',5)
        for k in range(5):
            a=tau*k/5
            stem(m,[polar((x,-.09,z-.41),.045,a,0),polar((x,-.09,z-.41),.093,a,-.08)],
                 [.04,.015],'orange',4)
    # Exposed garnet arils enclosed by the ochre pith of the split fruit.
    m.blob((.56,-.292,1.40),(.182,.073,.21),'straw',sides=8,rings=3)
    for u,v in [(0,0),(-.090,.065),(.021,.122),(.098,.043),(.073,-.085),(-.047,-.105),(-.099,-.028)]:
        m.blob((.56+u,-.354,1.40+v),(.063,.043,.063),'red',sides=5,rings=2)
    for z,spread in [(1.66,.48),(1.87,.40)]:
        rosette(m,(.065,.06,z),spread*1.19,.25,.19,5,.6+z)
    for x,z in [(-.52,1.68),(.55,1.75),(.08,.93)]:
        blossom(m,(x,-.09,z),.116)


def candy_disc(m,x,y,z,r):
    # Face bands follow a rotated middle ring for the peppermint swirl.
    n=10
    verts=[(x,y-r*.32,z),(x,y+r*.32,z)]
    for depth,radius,twist in [(-.28,.55,.47),(-.18,1,0),(.18,1,0),(.28,.55,.47)]:
        verts += [(x+r*radius*cos(tau*i/n+twist),y+r*depth,z+r*radius*sin(tau*i/n+twist)) for i in range(n)]
    faces=[]; colors=[]
    for i in range(n):
        j=(i+1)%n
        panels=[(0,2+i,2+j)]
        for k in range(3):
            s=2+n*k
            panels.append((s+j,s+i,s+n+i,s+n+j))
        panels.append((1,2+3*n+j,2+3*n+i))
        faces.extend(panels); colors.extend([('red','cream')[i%2]]*5)
    m.face_colors(verts,faces,colors)


def candy_tree(m):
    base_roots(m,1.26)
    stem(m,[(0,0,.04),(0,.01,.31),(-.025,0,1.05),(.015,.05,1.70),(.02,.075,2.05)],
         [.235,.174,.136,.114,.075],'tan',8)
    for x,y,z,s in [(-.63,.00,1.49,.58),(.64,-.02,1.54,.55),(.02,.08,2.08,.64)]:
        if abs(x)>.1:
            stem(m,[(0,0,.84),(x*.49,y,1.11),(x,y,z)], [.135,.106,.074],'tan')
        canopy(m,(x,y,z),s,'leaf')
        stem(m,[(x,y,z+.04),(x,y-.09,z-.19),(x,y-.12,z-.31)],[.047,.032,.03],'tan',5)
        candy_disc(m,x,y-.13,z-.45,.187)


def lily(m):
    base_roots(m,.77)
    stem(m,[(0,0,.045),(0,.025,.61),(-.028,.04,1.21),(0,0,1.68)],
         [.081,.065,.061,.076],'green')
    for k in range(3):
        z=.39+k*.35
        rosette(m,(-.012,.02,z),.54-.035*k,.07,.113,3,.1+k*.85)
    o=(0,0,1.69)
    start=len(m.vertices)
    for i in range(6):
        a=tau*i/6+.08
        # Each recurved petal has an orange midrib and a scarlet outer flank.
        profile=[(.02,0,.043,.026),(.19,.16,.108,.053),(.39,.23,.146,.065),
                 (.53,.19,.127,.066),(.63,.09,.085,.048),(.66,-.045,.046,.027),
                 (.63,-.13,.008,.008)]
        rings=[]
        for k,(r,h,w,d) in enumerate(profile):
            b=a+.11*k/6
            cx,cy,cz=polar(o,r,b,h)
            cross=[(-w,0),(-w*.58,d*.67),(0,d),(w*.58,d*.67),(w,0),(0,-d*.63)]
            rings.append([(cx-sin(b)*u,cy+cos(b)*u,cz+v) for u,v in cross])
        faces=[tuple(reversed(range(6)))]; colors=['gold']
        for k in range(len(rings)-1):
            for j in range(6):
                h=(j+1)%6
                faces.append((6*k+j,6*k+h,6*k+h+6,6*k+j+6))
                colors.append('red' if j in (0,3,4,5) or k>=5 else ('gold' if k<=2 else 'orange'))
        faces.append(tuple(range(36,42))); colors.append('red')
        m.face_colors(sum(rings,[]),faces,colors)
    for i in range(6):
        a=i*tau/6+.15
        p=polar(o,.205,a,.42+.08*(i%2))
        stem(m,[polar(o,.041,a,.02),polar(o,.115,a,.26),p],[.023,.02,.017],'bark',5)
        m.blob(p,(.040,.040,.058),'wood',sides=5,rings=2)
    tilt=.91
    for index in range(start,len(m.vertices)):
        x,y,z=m.vertices[index]
        h=z-o[2]
        m.vertices[index]=(x,y*cos(tilt)-h*sin(tilt),o[2]+y*sin(tilt)+h*cos(tilt))


def pad(m, x,y,z, r, h, color, phase):
    # One concave pad with a V-cut all the way through its beveled rim.
    count=18
    outline=[(.075*cos(phase),.075*sin(phase))]
    for i in range(count):
        a=phase+.14+(tau-.28)*i/(count-1)
        outline.append((cos(a),sin(a)))
    n=len(outline)
    verts=[(x+r*p*scale,y+r*q*.94*scale,z+height) for scale,height in
           [( .96,0),(1,h*.6),(.97,h)] for p,q in outline]
    faces=[]; cols=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(n+i,n+j,2*n+j,2*n+i)])
        cols.extend([color,color])
    faces.extend([tuple(reversed(range(n))),tuple(range(2*n,3*n))]);cols.extend([color,color])
    m.face_colors(verts,faces,cols)


def lotus(m):
    pad(m,0,0,.01,1.13,.115,'deep',-pi/2)
    pad(m,-.03,.025,.115,.83,.07,'green',-pi/2+.12)
    stem(m,[(0,0,.17),(0,0,.37)], [.14,.12],'deep',8)
    for i in range(9):
        petal(m,(0,0,.31),i*tau/9+.17,
              [(.07,0,.07,.055),(.37,.035,.18,.085),(.63,.17,.224,.11),
               (.75,.34,.16,.09),(.78,.46,.015,.023)],['cream']*4)
    for i in range(7):
        petal(m,(0,0,.39),i*tau/7+.43,
              [(.04,0,.055,.04),(.25,.035,.14,.07),(.46,.15,.17,.083),
               (.56,.31,.118,.07),(.575,.39,.014,.022)],['violet']*4)
    outline=[((.41 if i%2==0 else .225)*cos(i*pi/5+pi/2),
              (.41 if i%2==0 else .225)*sin(i*pi/5+pi/2)) for i in range(10)]
    m.loft([[(x*s,y*s,z) for x,y in outline] for s,z in [(.85,.52),(1,.62),(.91,.69)]],
           ['orange','gold'])


def bell(m,p,r,color):
    x,y,z=p
    n=5
    rings=[]
    for width,height in [(.21,.12),(.54,.07),(.61,0),(1,-.075)]:
        rings.append([(x+r*width*cos(tau*i/n),y+r*width*sin(tau*i/n),
                       z+height+(.02*(i%2) if height<0 else 0)) for i in range(n)])
    m.loft(rings,[color]*3)


def sky_vine(m):
    stem(m,[(0,0,.03),(0,0,.095),(0,0,.17)],[.218,.215,.132],'earth',8)
    start=.15
    for side,col in [(1,'lime'),(-1,'green')]:
        pts=[]
        for i in range(19):
            t=i/18
            a=3*pi*t
            # The front projection encloses three almond-shaped windows.
            pts.append((side*.306*sin(a),side*.108*cos(a), start+2.01*t))
        stem(m,pts,[.071-.019*i/18 for i in range(19)],col,5)
    for k in range(3):
        z=.82+.67*k
        for s in [-1,1]:
            petal(m,(0,0,z-.04),0 if s>0 else pi,
                  [(.015,0,.064,.035),(.212,.099,.157,.068),
                   (.39,.015,.102,.046),(.43,-.027,.015,.015)],['cream']*3)
            stem(m,[(s*.31,-.01,z+.018),(s*.43,-.018,z-.034),(s*.465,-.035,z-.116)],
                 [.036,.031,.019],'green',5)
            bell(m,(s*.465,-.035,z-.181),.085,'ice')
        stem(m,[(0,-.03,z-.03),(0,-.056,z-.18)],[.028,.023],'green',5)
        m.blob((0,-.06,z-.225),(.082,.072,.087),'gold',sides=6,rings=2)
    pts=[(0,-.02,2.12),(.08,0,2.22)]
    for i in range(10):
        a= -.72+i*.51
        r=.117-.005*i
        pts.append((.02+r*cos(a),0,2.31+r*sin(a)))
    stem(m,pts,[.054-.025*i/(len(pts)-1) for i in range(len(pts))],'lime',5)


def front_petal(m,origin,angle,profile,colors):
    # Profile advances radially in XZ; depth in Y gives the face visible cupping.
    x,y,z=origin
    centers=[(x+cos(angle)*r,y+v,z+sin(angle)*r) for r,v,w,d in profile]
    strip(m,centers,[s[2] for s in profile],(-sin(angle),0,cos(angle)),
          (0,-1,0),[s[3] for s in profile],colors)


def aurora(m):
    stem(m,[(0,0,.02),(-.038,0,.34),(.05,.03,.65),(.19,.045,.98),
            (.205,.05,1.19),(.09,.03,1.49)], [.099,.087,.079,.074,.073,.067],'green')
    for s in [-1,1]:
        blade(m,(0,0,.045),.16 if s>0 else pi-.16,.65,.55,.181,'lime',s*.91)
    o=(.09,.025,1.48)
    for degrees in [-22,37,91,143,202]:
        front_petal(m,o,degrees*pi/180,
                    [(.055,0,.050,.042),(.26,.082,.137,.064),(.42,.035,.202,.079),
                     (.57,-.04,.235,.089),(.729,.006,.212,.067),
                     (.77,.028,.088,.047)],['violet','violet','blue','ice','ice'])
    m.blob((.09,-.04,1.48),(.187,.15,.18),'gold',sides=9,rings=3)


def spring_tree(m):
    base_roots(m,1.55)
    stem(m,[(-.21,.04,.045),(-.39,.065,.30),(-.34,.085,.55),(-.11,.11,.78),
            (.22,.10,1.05),(.32,.095,1.24),(.49,.055,1.40)], [.168,.136,.12,.124,.13,.115,.087],'tan')
    stem(m,[(.20,-.03,.035),(.34,-.05,.29),(.33,-.03,.53),(.15,.005,.78),
            (-.15,.045,1.12),(-.24,.06,1.44),(-.15,.10,1.72)], [.174,.151,.142,.127,.115,.099,.08],'wood')
    stem(m,[(-.16,.055,.73),(-.41,.02,.82),(-.57,-.035,.98)],[.1,.086,.069],'tan',6)
    crowns=[(-.55,-.035,1.005,.53),(.51,.045,1.37,.50),(-.16,.11,1.76,.71)]
    for idx,(x,y,z,w) in enumerate(crowns):
        canopy(m,(x,y,z),w,'green',7)
        for k in range(3):
            a=-pi+.43+k*1.1
            p=polar((x,y,z),w*.58,a,-.057)
            m.blob((p[0],p[1],p[2]-.036),(w*.175,w*.17,w*.19),('orange','gold','red')[k],sides=6,rings=2)
        for k in range(2):
            dx=(-.22 if k==0 else .30)*w
            blossom(m,(x+dx,y-.66*w,z+.27*w),w*.132)
        for k in range(2):
            p=(x+.05*k,y+.05,z+w*.33)
            m.leaf(p,(p[0]+.073*(-1 if k else 1),p[1]+.01,p[2]+w*.15),w*.05,'lime',arch=.014)


def sun_heart(m):
    stem(m,[(0,0,.033),(.035,.015,.31),(-.058,.034,.57),(-.07,.055,.80),
            (.016,.06,1.09),(0,.07,1.48)], [.129,.114,.103,.113,.085,.091],'green',8)
    stem(m,[(0,0,.024),(0,0,.09),(0,0,.16)],[.247,.213,.132],'earth',8)
    for s in [-1,1]:
        blade(m,(-.017,.02,.38+s*.055),.06 if s>0 else pi-.06,.69,.31,.207,'lime',s*1.00)
        front_petal(m,(0,.045,.85),pi/4 if s>0 else 3*pi/4,
                    [(0,0,.035,.046),(.225,-.022,.101,.083),(.415,-.044,.094,.061),
                     (.574,-.066,.014,.019)],['orange']*3)
    o=(0,.055,1.58)
    m.blob(o,(.35,.155,.35),'gold',sides=10,rings=3)
    for i in range(11):
        a=pi/2+i*tau/11
        front_petal(m,o,a,[(.185,0,.058,.041),(.36,.008,.10,.068),(.55,.013,.131,.077),
                            (.635,.027,.109,.058),(.66,.035,.046,.045)],
                    ['orange','gold','gold','gold'])
    # Double-lobed faceted heart, domed amber face, crisp pointed base.
    outline=[(0,.169),(-.109,.254),(-.228,.242),(-.304,.142),(-.285,.014),
             (-.19,-.114),(0,-.303),(.19,-.114),(.285,.014),(.304,.142),
             (.228,.242),(.109,.254)]
    n=len(outline)
    rings=[[(x*s, y, 1.58+z*s) for x,z in outline] for y,s in
           [(-.075,.95),(-.17,1.07),(-.25,.85),(-.289,.52)]]
    verts=sum(rings,[])+[(0,-.314,1.595)]
    faces=[tuple(reversed(range(n)))]; colors=['orange']
    for k in range(3):
        for i in range(n):
            j=(i+1)%n
            faces.append((n*k+i,n*k+j,n*(k+1)+j,n*(k+1)+i))
            colors.append('straw' if k==2 and i in (1,2) else 'orange')
    for i in range(n):
        faces.append((3*n+i,3*n+(i+1)%n,4*n))
        colors.append('orange')
    m.face_colors(verts,faces,colors)


def build(number,m):
    builders={29:pomegranate,30:candy_tree,31:lily,32:lotus,
              33:sky_vine,34:aurora,35:spring_tree,36:sun_heart}
    builders[number](m)
