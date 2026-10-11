import pygame, sys, math, random, array

pygame.init()
try:
    pygame.mixer.init(22050, -16, 2, 512)
    HAS_SOUND = True
except:
    HAS_SOUND = False

WIDTH, HEIGHT = 960, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Lost Caverns — Enhanced Edition")
clock = pygame.time.Clock()

# === COLORS ===
BLACK=(0,0,0); WHITE=(255,255,255); GRAY=(128,128,128); DGRAY=(50,50,55)
RED=(220,50,50); GREEN=(50,200,50); BLUE=(50,100,220); YELLOW=(240,220,40)
PURPLE=(160,50,220); CYAN=(50,220,220); ORANGE=(240,150,30); BROWN=(139,90,43)
DBROWN=(90,55,25); GOLD=(255,215,0); PINK=(255,150,180); STONE=(100,95,90)
DSTONE=(60,55,50); LSTONE=(140,135,125); CAVEBG=(25,20,35); LAVA=(200,60,20)

# === FONTS ===
ftiny=pygame.font.SysFont("consolas",12); fsmall=pygame.font.SysFont("consolas",16)
fmed=pygame.font.SysFont("consolas",22); flarge=pygame.font.SysFont("consolas",40,True)
ftitle=pygame.font.SysFont("consolas",56,True); fhuge=pygame.font.SysFont("consolas",72,True)

# === SOUND GENERATION ===
def make_snd(f0,f1,dur,vol=0.15,wave='sq'):
    if not HAS_SOUND: return None
    try:
        sr=22050; n=int(sr*dur); buf=array.array('h')
        for i in range(n):
            t=i/sr; p=i/n; f=f0+(f1-f0)*p
            if wave=='sq': v=1 if math.sin(2*math.pi*f*t)>0 else -1
            elif wave=='sn': v=math.sin(2*math.pi*f*t)
            else: v=random.random()*2-1
            env=min(1.0,i/(sr*0.005+1),(n-i)/(sr*0.02+1))
            s=int(32767*vol*v*env); buf.append(s); buf.append(s)
        return pygame.mixer.Sound(buffer=buf)
    except: return None

SND_JUMP=make_snd(300,600,0.1); SND_COIN=make_snd(800,1200,0.08)
SND_HURT=make_snd(200,80,0.2,0.12,'ns'); SND_SECRET=make_snd(400,800,0.3,0.12,'sn')
SND_DASH=make_snd(100,400,0.12,0.08); SND_CKPT=make_snd(500,700,0.15,0.1,'sn')
SND_DEATH=make_snd(400,50,0.5,0.12); SND_STOMP=make_snd(200,500,0.1,0.1)

def snd(s):
    if s: s.play()

def hsv_rgb(h,s,v):
    c=v*s; x=c*(1-abs((h/60)%2-1)); m=v-c
    if h<60:r,g,b=c,x,0
    elif h<120:r,g,b=x,c,0
    elif h<180:r,g,b=0,c,x
    elif h<240:r,g,b=0,x,c
    elif h<300:r,g,b=x,0,c
    else:r,g,b=c,0,x
    return(int((r+m)*255),int((g+m)*255),int((b+m)*255))

def rc(h): return hsv_rgb(h%360,0.8,1.0)
def dtc(s,t,f,c,y): s.blit(f.render(t,True,c),(x,y)) if False else s.blit(f.render(t,True,c),(x,y))
def dtxt(sf,t,f,c,x,y): sf.blit(f.render(t,True,c),(x,y))
def dtctr(sf,t,f,c,y): s=f.render(t,True,c); sf.blit(s,s.get_rect(center=(WIDTH//2,y)))

# === PARTICLES ===
particles=[]
def spawn_p(x,y,c,n=10,sp=3):
    for _ in range(n):
        particles.append({'x':x,'y':y,'vx':random.uniform(-sp,sp),'vy':random.uniform(-sp,0.5),
            'life':random.randint(15,40),'ml':40,'c':c,'sz':random.randint(2,4)})
def update_p():
    for p in particles[:]:
        p['x']+=p['vx'];p['y']+=p['vy'];p['vy']+=0.1;p['life']-=1
        if p['life']<=0: particles.remove(p)
def draw_p(sf):
    for p in particles:
        a=p['life']/p['ml']; sz=max(1,int(p['sz']*a))
        pygame.draw.circle(sf,p['c'],(int(p['x']),int(p['y'])),sz)

# === FLOAT MESSAGES ===
float_msgs=[]
def add_fmsg(t,x,y,c=GOLD):
    float_msgs.append([t,x,y,120,c])

# === EASTER EGG STATE ===
class EE:
    def __init__(self):
        self.kseq=[pygame.K_UP,pygame.K_UP,pygame.K_DOWN,pygame.K_DOWN,pygame.K_LEFT,
                   pygame.K_RIGHT,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_b,pygame.K_a]
        self.kidx=0; self.rainbow=False; self.rhue=0.0; self.matrix=False
        self.mtimer=0; self.mdrops=[]; self.night=False; self.broll=False
        self.bangle=0; self.btimer=0; self.fcrash=False; self.ctimer=0
        self.deaths=0; self.a42=False; self.a42t=0; self.sw_found=False
        self.pacifist=False; self.ptimer=0; self.pstarted=False
        self.king=False; self.ttimer=0; self.on_throne=False
        self.gem_order=[]; self.sdoor=False; self.fwall=False; self.fwtimer=0
        self.bclicks=0; self.huge=False; self.htimer=0; self.mirror=False
        self.ctimer2=0; self.csecret=False; self.cmsgt=0
        self.tbuf=""; self.tbuft=0; self.secrets=0
        self.snake_on=False; self.snake=[[5,5],[4,5],[3,5]]
        self.sdir=[1,0]; self.sfood=[10,10]; self.stimer=0; self.sscore=0
        self.sr_msg=False; self.sr_mt=0; self.start_t=0; self.won=False
        self.won_t=0; self.blocky=False; self.blocky_t=0
        self.dancing=False; self.dance_t=0; self.dance_a=0
        self.coins=0; self.coin42=False; self.title_click=False
        self.title_click_t=0; self.gravity_flip=False; self.gflip_t=0

ee=EE()

def chk_konami(k):
    if k==ee.kseq[ee.kidx]:
        ee.kidx+=1
        if ee.kidx>=len(ee.kseq):
            ee.kidx=0
            if not ee.rainbow:
                ee.rainbow=True; ee.secrets+=1; snd(SND_SECRET)
                add_fmsg("SECRET: Rainbow Mode!",WIDTH//2,HEIGHT//2,GOLD)
    else:
        ee.kidx=1 if k==ee.kseq[0] else 0

def chk_type(k):
    if k==pygame.K_BACKSPACE: ee.tbuf=ee.tbuf[:-1]
    elif k==pygame.K_RETURN: ee.tbuf=""
    elif 32<=k<=126:
        ch=chr(k).lower(); ee.tbuf+=ch
    if len(ee.tbuf)>30: ee.tbuf=ee.tbuf[-30:]
    ee.tbuft=150

def proc_type():
    b=ee.tbuf.lower().strip()
    found=False
    if b=="matrix" and not ee.matrix:
        ee.matrix=True; ee.mtimer=180; found=True
        ee.mdrops=[[random.randint(0,WIDTH//12),random.randint(-HEIGHT,0)]for _ in range(WIDTH//12)]
    elif b=="night":
        ee.night=not ee.night; found=ee.night
        if ee.night: add_fmsg("SECRET: Night Vision!",WIDTH//2,HEIGHT//2,CYAN)
        else: add_fmsg("Night mode off",WIDTH//2,HEIGHT//2,GRAY)
    elif b=="42" and not ee.a42:
        ee.a42=True; ee.a42t=150; found=True
        add_fmsg("The Answer to Life, the Universe, and Everything",WIDTH//2,HEIGHT//2,GOLD)
    elif b=="barrel" and not ee.broll:
        ee.broll=True; ee.btimer=60; found=True
        add_fmsg("SECRET: Do a Barrel Roll!",WIDTH//2,HEIGHT//2,ORANGE)
    elif b=="mirror":
        ee.mirror=not ee.mirror; found=ee.mirror
        if ee.mirror: add_fmsg("SECRET: Mirror World!",WIDTH//2,HEIGHT//2,PINK)
    elif b=="iamgod" and not ee.huge:
        ee.huge=True; ee.htimer=300; found=True
        add_fmsg("SECRET: GOD MODE!",WIDTH//2,HEIGHT//2,GOLD)
    elif b=="notch" and not ee.blocky:
        ee.blocky=True; ee.blocky_t=600; found=True
        add_fmsg("SECRET: Minecraft Mode!",WIDTH//2,HEIGHT//2,BROWN)
    elif b=="dance" and not ee.dancing:
        ee.dancing=True; ee.dance_t=240; ee.dance_a=0; found=True
        add_fmsg("SECRET: Dance Mode!",WIDTH//2,HEIGHT//2,PINK)
    elif b=="flip" and not ee.gravity_flip:
        ee.gravity_flip=True; ee.gflip_t=300; found=True
        add_fmsg("SECRET: Gravity Flip!",WIDTH//2,HEIGHT//2,CYAN)
    if found:
        ee.secrets+=1; snd(SND_SECRET); ee.tbuf=""

# === SCREEN SHAKE ===
shake_amt=0; shake_dur=0
def do_shake(a,d): global shake_amt,shake_dur; shake_amt=a; shake_dur=d

# === GAME OBJECTS ===
class Player:
    def __init__(self,x,y):
        self.x=float(x);self.y=float(y);self.w=24;self.h=36
        self.vx=0.0;self.vy=0.0;self.on_ground=False;self.facing_r=True
        self.alive=True;self.hp=3;self.max_hp=3;self.inv=0
        self.sx=x;self.sy=y;self.blink=0;self.wf=0.0
        self.jumps=2;self.max_j=2;self.coyote=0;self.jbuf=0
        self.dash_cd=0;self.dash_t=0;self.dash_d=0
        self.dmg_flash=0;self.trail=[]

    @property
    def rect(self):
        s=3 if ee.huge else 1
        return pygame.Rect(self.x-self.w*s/2,self.y-self.h*s,self.w*s,self.h*s)
    def draw_rect(self):
        s=3 if ee.huge else 1; w=self.w*s; h=self.h*s
        return pygame.Rect(self.x-w/2,self.y-h,w,h)

    def update(self,platforms,mp_vel=(0,0)):
        if not self.alive: return
        if ee.dancing:
            ee.dance_a+=8; ee.dance_t-=1
            if ee.dance_t<=0: ee.dancing=False
            return
        keys=pygame.key.get_pressed()
        spd=7 if ee.huge else 4.5
        acc=0.8 if self.on_ground else 0.4
        fric=0.78 if self.on_ground else 0.94

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx-=acc; self.facing_r=False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx+=acc; self.facing_r=True
        else: self.vx*=fric
        self.vx=max(-spd,min(spd,self.vx))

        grav=0.55 if not ee.gravity_flip else -0.55
        self.vy+=grav
        self.vy=min(12,max(-12,self.vy))

        if self.dash_t>0:
            self.dash_t-=1
            self.vx=self.dash_d*14
            self.vy=0
            self.trail.append((self.x,self.y-20,8))
        else:
            self.x+=self.vx+mp_vel[0]
        r=self.rect
        for p in platforms:
            if r.colliderect(p):
                if self.vx+mp_vel[0]>0: self.x=p.left-r.width/2
                elif self.vx+mp_vel[0]<0: self.x=p.right+r.width/2
                self.vx=0; r=self.rect

        if self.dash_t<=0:
            self.y+=self.vy+mp_vel[1]
        self.on_ground=False
        r=self.rect
        for p in platforms:
            if r.colliderect(p):
                if ee.gravity_flip:
                    if self.vy<0: self.y=p.bottom+r.height; self.on_ground=True
                    elif self.vy>0: self.y=p.top
                else:
                    if self.vy>0: self.y=p.top; self.on_ground=True
                    elif self.vy<0: self.y=p.bottom+r.height
                self.vy=0; r=self.rect

        self.x=max(0,min(WIDTH,self.x))
        if self.y>HEIGHT+100 or self.y<-100: self.take_damage(99)
        if self.inv>0: self.inv-=1
        if self.dmg_flash>0: self.dmg_flash-=1
        if abs(self.vx)>0.5: self.wf+=0.15
        else: self.wf=0
        self.blink=max(0,self.blink-1)
        if random.random()<0.005: self.blink=8
        if self.on_ground: self.jumps=self.max_j; self.coyote=6
        else: self.coyote=max(0,self.coyote-1)
        if self.jbuf>0: self.jbuf-=1
        if self.dash_cd>0: self.dash_cd-=1
        self.trail=[(x,y,t-1)for x,y,t in self.trail if t>1]

    def jump(self):
        if not self.alive or ee.dancing: return
        self.jbuf=8
        if self.coyote>0 or self.jumps>0:
            jf=-10.5 if not ee.gravity_flip else 10.5
            if self.coyote>0: self.vy=jf; self.coyote=0
            else: self.vy=jf*0.85; self.jumps-=1
            self.on_ground=False
            spawn_p(self.x,self.y,WHITE,5,2); snd(SND_JUMP)

    def dash(self):
        if not self.alive or self.dash_cd>0 or ee.dancing: return
        self.dash_t=8; self.dash_d=1 if self.facing_r else -1
        self.dash_cd=90; self.inv=max(self.inv,10)
        snd(SND_DASH)

    def take_damage(self,amt=1):
        if self.inv>0 or not self.alive: return
        self.hp-=amt; self.inv=60; self.dmg_flash=15
        do_shake(6,10); snd(SND_HURT)
        spawn_p(self.x,self.y-20,RED,8,3)
        if self.hp<=0: self.die()

    def die(self):
        if not self.alive: return
        self.alive=False; ee.deaths+=1
        spawn_p(self.x,self.y-20,RED,25,5); snd(SND_DEATH)
        do_shake(10,15)
        if ee.deaths==5 and not ee.fcrash:
            ee.fcrash=True; ee.ctimer=200

    def respawn(self):
        self.x=float(self.sx);self.y=float(self.sy)
        self.vx=self.vy=0;self.alive=True;self.hp=self.max_hp;self.inv=90

    def draw(self,sf):
        if not self.alive: return
        if self.inv>0 and self.inv%6<3: return
        for tx,ty,tt in self.trail:
            a=tt/8; s=max(1,int(6*a))
            pygame.draw.circle(sf,(100,150,255),(int(tx),int(ty)),s)
        r=self.draw_rect(); s=3 if ee.huge else 1
        bc=rc(ee.rhue) if ee.rainbow else (80,130,200)
        if self.dmg_flash>0 and self.dmg_flash%4<2: bc=WHITE
        if ee.blocky:
            pygame.draw.rect(sf,bc,r)
            pygame.draw.rect(sf,tuple(max(0,c-40)for c in bc),r,2)
            ex=r.centerx; ey=r.y+r.height*0.3; es=max(2,int(5*s))
            pygame.draw.rect(sf,WHITE,(ex-es,ey-es,es*2,es*2))
            pygame.draw.rect(sf,WHITE,(ex+es,ey-es,es*2,es*2))
            ps=max(1,int(2*s))
            pygame.draw.rect(sf,BLACK,(ex-ps,ey-ps,ps*2,ps*2))
            pygame.draw.rect(sf,BLACK,(ex+es*2-ps,ey-ps,ps*2,ps*2))
        elif ee.dancing:
            temp=pygame.Surface((r.width+20,r.height+20),pygame.SRCALPHA)
            tr=pygame.Rect(10,10,r.width,r.height)
            pygame.draw.rect(sf,bc,tr,border_radius=int(4*s))
            rot=pygame.transform.rotate(temp,ee.dance_a)
            sf.blit(rot,rot.get_rect(center=(int(self.x),int(self.y-r.height/2))))
        else:
            pygame.draw.rect(sf,bc,r,border_radius=int(4*s))
            dk=tuple(max(0,c-40)for c in bc)
            pygame.draw.rect(sf,dk,r,width=max(1,int(2*s)),border_radius=int(4*s))
            ey=r.y+r.height*0.3; es=max(2,int(4*s)); sp=r.width*0.2
            if self.facing_r: ex1,ex2=r.centerx+sp-es,r.centerx+sp+es
            else: ex1,ex2=r.centerx-sp-es,r.centerx-sp+es
            if self.blink>0:
                for ex in(ex1,ex2):
                    pygame.draw.line(sf,WHITE,(int(ex),int(ey)),(int(ex)+es*2,int(ey)),max(1,int(2*s)))
            else:
                for ex in(ex1,ex2):
                    pygame.draw.circle(sf,WHITE,(int(ex),int(ey)),es)
                po=int(1.5*s)*(1 if self.facing_r else -1); ps2=max(1,int(2*s))
                for ex in(ex1,ex2):
                    pygame.draw.circle(sf,BLACK,(int(ex)+po,int(ey)),ps2)
            lo=math.sin(self.wf)*4*s; fw=max(2,int(6*s)); fh=max(2,int(4*s))
            pygame.draw.rect(sf,dk,(r.x+r.width*0.2,r.bottom-fh+lo,fw,fh))
            pygame.draw.rect(sf,dk,(r.x+r.width*0.6,r.bottom-fh-lo,fw,fh))
        if ee.king:
            cw=r.width*1.2;ch=r.height*0.3;cx=r.centerx;cy=r.y-ch*0.3
            pts=[(cx-cw/2,cy+ch),(cx-cw/2,cy+ch*0.3),(cx-cw/4,cy+ch*0.7),
                 (cx,cy),(cx+cw/4,cy+ch*0.7),(cx+cw/2,cy+ch*0.3),(cx+cw/2,cy+ch)]
            pygame.draw.polygon(sf,GOLD,[(int(x),int(y))for x,y in pts])
            pygame.draw.polygon(sf,ORANGE,[(int(x),int(y))for x,y in pts],max(1,int(2*s)))
            pygame.draw.circle(sf,RED,(int(cx),int(cy+ch*0.5)),max(2,int(3*s)))

class MovingPlatform:
    def __init__(self,x,y,w,h,dx,dy,dist,spd):
        self.ox=x;self.oy=y;self.x=float(x);self.y=float(y)
        self.w=w;self.h=h;self.dx=dx;self.dy=dy;self.dist=dist;self.spd=spd
        self.t=0;self.px=self.x;self.py=self.y
    def update(self):
        self.px=self.py if False else self.x; self.py2=self.y
        self.px=self.x; self.py=self.y
        self.t+=self.spd
        if self.t>=1: self.t=0;self.dx=-self.dx;self.dy=-self.dy
        self.x=self.ox+self.dx*self.dist*self.t
        self.y=self.oy+self.dy*self.dist*self.t
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.w,self.h)
    @property
    def vx(self): return self.x-self.px
    @property
    def vy(self): return self.y-self.py
    def draw(self,sf):
        r=self.rect; c=rc(ee.rhue+r.x*0.3) if ee.rainbow else (120,110,100)
        pygame.draw.rect(sf,c,r,border_radius=3)
        pygame.draw.rect(sf,tuple(min(255,v+30)for v in c),(r.x,r.y,r.width,4))

class Spike:
    def __init__(self,x,y,cnt=3,dr='up'):
        self.x=x;self.y=y;self.cnt=cnt;self.dr=dr
        self.rect=pygame.Rect(x,y-12 if dr=='up'else y,cnt*16,12)
    def draw(self,sf):
        for i in range(self.cnt):
            bx=self.x+i*16
            if self.dr=='up':
                pts=[(bx,self.y),(bx+8,self.y-12),(bx+16,self.y)]
            else:
                pts=[(bx,self.y),(bx+8,self.y+12),(bx+16,self.y)]
            pygame.draw.polygon(sf,(180,180,190),pts)
            pygame.draw.polygon(sf,LSTONE,pts,1)

class Coin:
    def __init__(self,x,y):
        self.x=x;self.y=y;self.collected=False;self.bob=random.uniform(0,6.28)
    def draw(self,sf,fr):
        if self.collected: return
        y=self.y+math.sin(fr*0.06+self.bob)*3
        w=abs(math.sin(fr*0.08+self.bob))*7+2
        pygame.draw.ellipse(sf,GOLD,(self.x-w,y-6,w*2,12))
        if w>4: pygame.draw.ellipse(sf,YELLOW,(self.x-w+2,y-4,max(1,w*2-4),max(1,8)))
    @property
    def rect(self): return pygame.Rect(self.x-8,self.y-8,16,16)

class Checkpoint:
    def __init__(self,x,y):
        self.x=x;self.y=y;self.on=False;self.rect=pygame.Rect(x-8,y-40,16,40)
    def draw(self,sf,fr):
        c=GREEN if self.on else GRAY
        pygame.draw.line(sf,c,(self.x,self.y),(self.x,self.y-35),3)
        fw=math.sin(fr*0.1)*3
        pts=[(self.x,self.y-35),(self.x+20+fw,self.y-28),(self.x,self.y-20)]
        pygame.draw.polygon(sf,c,pts)

class Gem:
    def __init__(self,x,y,c): self.x=x;self.y=y;self.c=c;self.collected=False;self.bob=random.uniform(0,6.28)
    def draw(self,sf,fr):
        if self.collected: return
        y=self.y+math.sin(fr*0.05+self.bob)*5; sz=10
        pts=[(self.x,y-sz),(self.x+sz*0.7,y),(self.x,y+sz),(self.x-sz*0.7,y)]
        c=rc(ee.rhue+self.c[0])if ee.rainbow else self.c
        if ee.blocky: pygame.draw.rect(sf,c,(self.x-sz,y-sz,sz*2,sz*2))
        else: pygame.draw.polygon(sf,c,pts);pygame.draw.polygon(sf,tuple(min(255,v+80)for v in c),pts,2)
    @property
    def rect(self): return pygame.Rect(self.x-8,self.y-10,16,20)

class Enemy:
    def __init__(self,x,y,c=RED,pat=100,spd=1.5,pac=False,chaser=False):
        self.x=float(x);self.ox=float(x);self.y=float(y);self.c=c
        self.w=28;self.h=24;self.alive=True;self.pat=pat;self.spd=spd
        self.dir=1;self.pac=pac;self.friend=False;self.fr=0;self.chaser=chaser
    @property
    def rect(self): return pygame.Rect(self.x-self.w/2,self.y-self.h,self.w,self.h)
    def update(self,px=None,py=None):
        if not self.alive: return
        self.fr+=1
        if self.friend: self.y+=math.sin(self.fr*0.1)*0.3; return
        if self.chaser and px is not None:
            dx=px-self.x;dy=py-self.y;d=math.hypot(dx,dy)
            if d<250 and d>0:
                self.x+=dx/d*self.spd*0.7;self.dir=1 if dx>0 else -1; return
        self.x+=self.spd*self.dir
        if self.x>self.ox+self.pat: self.dir=-1
        elif self.x<self.ox-self.pat: self.dir=1
    def draw(self,sf):
        if not self.alive: return
        r=self.rect; c=rc(ee.rhue+self.c[0])if ee.rainbow else self.c
        if ee.blocky: pygame.draw.rect(sf,c,r)
        else:
            pygame.draw.ellipse(sf,c,r)
            if self.friend:
                pygame.draw.circle(sf,WHITE,(r.centerx-5,r.centery-3),4)
                pygame.draw.circle(sf,WHITE,(r.centerx+5,r.centery-3),4)
                pygame.draw.circle(sf,BLACK,(r.centerx-5,r.centery-3),2)
                pygame.draw.circle(sf,BLACK,(r.centerx+5,r.centery-3),2)
                pygame.draw.arc(sf,BLACK,(r.centerx-6,r.centery,12,8),3.14,6.28,2)
                pygame.draw.circle(sf,PINK,(r.centerx,r.top-8),4)
            else:
                for i in range(5):
                    sx=r.x+r.width*(i+0.5)/5
                    pygame.draw.polygon(sf,c,[(sx-4,r.y),(sx,r.y-8),(sx+4,r.y)])
                pygame.draw.circle(sf,WHITE,(r.centerx-5,r.centery-2),4)
                pygame.draw.circle(sf,WHITE,(r.centerx+5,r.centery-2),4)
                pygame.draw.circle(sf,BLACK,(r.centerx-5,r.centery-2),2)
                pygame.draw.circle(sf,BLACK,(r.centerx+5,r.centery-2),2)
                if self.chaser:
                    pygame.draw.line(sf,RED,(r.centerx-3,r.centery+5),(r.centerx+3,r.centery+5),2)

class Sign:
    def __init__(self,x,y,t,st=None): self.x=x;self.y=y;self.t=t;self.st=st;self.w=120;self.h=50
    @property
    def rect(self): return pygame.Rect(self.x,self.y,self.w,self.h)
    def draw(self,sf,near):
        pygame.draw.rect(sf,BROWN,(self.x+self.w//2-4,self.y+self.h,8,30))
        pygame.draw.rect(sf,DBROWN,(self.x,self.y,self.w,self.h))
        pygame.draw.rect(sf,BROWN,(self.x,self.y,self.w,self.h),2)
        if near:
            txt=self.st if(self.st and ee.fwall)else self.t
            lines=txt.split('\n'); bh=16+len(lines)*20; by=self.y-bh-10
            bx=max(10,min(self.x,WIDTH-300)); bw=min(280,WIDTH-20)
            pygame.draw.rect(sf,(20,15,30),(bx,by,bw,bh),border_radius=5)
            pygame.draw.rect(sf,GOLD,(bx,by,bw,bh),2,border_radius=5)
            for i,l in enumerate(lines): dtxt(sf,l,fsmall,WHITE,bx+10,by+8+i*20)

class Door:
    def __init__(self,x,y,w,h,dest,dx,dy,lbl="",c=BROWN,req=False):
        self.rect=pygame.Rect(x,y,w,h);self.dest=dest;self.dx=dx;self.dy=dy
        self.lbl=lbl;self.c=c;self.req=req;self.active=not req
    def draw(self,sf,fr):
        if not self.active:
            pygame.draw.rect(sf,DSTONE,self.rect);pygame.draw.rect(sf,STONE,self.rect,1);return
        c=rc(ee.rhue+fr)if ee.rainbow else self.c
        pygame.draw.rect(sf,c,self.rect);pygame.draw.rect(sf,tuple(max(0,v-40)for v in c),self.rect,3)
        pygame.draw.circle(sf,GOLD,(self.rect.x+int(self.rect.width*0.7),self.rect.centery),4)
        if self.lbl: dtctr(sf,self.lbl,ftiny,WHITE,self.rect.y-12)

class Bookshelf:
    def __init__(self,x,y,w,h):
        self.rect=pygame.Rect(x,y,w,h);self.books=[]
        for bx in range(x+5,x+w-10,12):
            bc=random.choice([RED,BLUE,GREEN,BROWN,PURPLE,ORANGE])
            bh=random.randint(h-20,h-5); self.books.append((bx,y+5,10,bh,bc))
    def draw(self,sf):
        pygame.draw.rect(sf,DBROWN,self.rect);pygame.draw.rect(sf,BROWN,self.rect,2)
        mid=self.rect.y+self.rect.height//2
        pygame.draw.line(sf,BROWN,(self.rect.x,mid),(self.rect.right,mid),2)
        for bx,by,bw,bh,bc in self.books:
            c=rc(ee.rhue+bc[0])if ee.rainbow else bc
            pygame.draw.rect(sf,c,(bx,by,bw,bh))

class Throne:
    def __init__(self,x,y): self.rect=pygame.Rect(x,y,50,60);self.x=x;self.y=y
    def draw(self,sf,fr):
        pygame.draw.rect(sf,GOLD,(self.x+5,self.y-30,40,30),border_radius=3)
        pygame.draw.rect(sf,ORANGE,(self.x+5,self.y-30,40,30),2,border_radius=3)
        pygame.draw.rect(sf,(180,50,50),(self.x,self.y,50,15),border_radius=2)
        pygame.draw.rect(sf,GOLD,(self.x+3,self.y+15,8,45))
        pygame.draw.rect(sf,GOLD,(self.x+39,self.y+15,8,45))
        g=int(abs(math.sin(fr*0.05))*50+200)
        pygame.draw.circle(sf,(g,0,0),(self.x+25,self.y-15),5)

class Portal:
    def __init__(self,x,y): self.x=x;self.y=y;self.r=30
    def draw(self,sf,fr):
        for i in range(5):
            r=self.r-i*5; c=rc(ee.rhue+i*60+fr*2)if ee.rainbow else hsv_rgb((fr*2+i*60)%360,0.8,0.9)
            pygame.draw.circle(sf,c,(int(self.x),int(self.y)),max(1,r),3)
        pygame.draw.circle(sf,WHITE,(int(self.x),int(self.y)),8)

def draw_dec(sf,d,fr):
    t=d['type']
    if t=='stalactite':
        pts=[(d['x'],0),(d['x']-15,0),(d['x']-8,d['h'])]
        pygame.draw.polygon(sf,STONE,pts);pygame.draw.polygon(sf,LSTONE,pts,1)
    elif t=='crystal':
        h,c=40,d['c']
        if ee.rainbow: c=rc(ee.rhue+c[0])
        pts=[(d['x'],d['y']-h),(d['x']-10,d['y']),(d['x']+10,d['y'])]
        pygame.draw.polygon(sf,c,pts)
        pygame.draw.polygon(sf,tuple(min(255,v+60)for v in c),
            [(d['x'],d['y']-h),(d['x'],d['y']-h+15),(d['x']-5,d['y']-h+20)])
        gs=pygame.Surface((30,h+10),pygame.SRCALPHA)
        pygame.draw.ellipse(gs,(*c,int(40+20*math.sin(fr*0.08))),(0,0,30,h+10))
        sf.blit(gs,(d['x']-15,d['y']-h-5))
    elif t=='painting':
        x,y,w,h=d['x'],d['y'],d['w'],d['h']
        pygame.draw.rect(sf,DBROWN,(x-5,y-5,w+10,h+10))
        pygame.draw.rect(sf,(30,60,30),(x,y,w,h))
        pygame.draw.rect(sf,(40,80,40),(x,y+h//2,w,h//2))
        pygame.draw.circle(sf,YELLOW,(x+w-20,y+20),10)
        if fr%120<60: dtxt(sf,"...",ftiny,(60,80,60),x+w//2-8,y+h//2-5)
    elif t=='torch':
        x,y=d['x'],d['y']
        pygame.draw.rect(sf,BROWN,(x-3,y-20,6,20))
        fl=random.randint(-2,2)
        for i in range(3):
            fy=y-25-i*5+fl; r=max(1,6-i*2)
            pygame.draw.circle(sf,[ORANGE,YELLOW,WHITE][i],(x+fl//2,fy),r)
        gs=pygame.Surface((60,60),pygame.SRCALPHA)
        pygame.draw.circle(gs,(255,150,50,30),(30,30),30)
        sf.blit(gs,(x-30,y-50))
    elif t=='flower':
        x,y,c=d['x'],d['y'],d['c']
        if ee.rainbow: c=rc(ee.rhue+c[0])
        pygame.draw.line(sf,GREEN,(x,y),(x,y-15),2)
        for a in range(0,360,72):
            px2=x+math.cos(math.radians(a+fr*0.5))*5
            py2=y-15+math.sin(math.radians(a+fr*0.5))*5
            pygame.draw.circle(sf,c,(int(px2),int(py2)),3)
        pygame.draw.circle(sf,YELLOW,(x,y-15),2)

# === ROOMS ===
def make_rooms():
    R=[]
    # Room 0: Entrance
    R.append({'name':'Entrance Cave','bg':CAVEBG,
        'plat':[pygame.Rect(0,580,900,70),pygame.Rect(100,470,150,20),
                pygame.Rect(350,400,120,20),pygame.Rect(580,450,150,20),pygame.Rect(750,370,120,20)],
        'mplat':[],'spikes':[],
        'gems':[Gem(175,440,RED),Gem(410,370,YELLOW),Gem(650,420,GREEN)],
        'enemies':[Enemy(400,580,RED,80,1.2)],
        'signs':[Sign(30,540,"Welcome to\nThe Lost Caverns\nExplore wisely...")],
        'doors':[Door(930,500,30,80,1,50,540,"-> Crystal Chamber")],
        'books':[],'thrones':[],'portals':[],'sw':None,'ckpt':[],
        'coins':[Coin(130,440),Coin(200,440),Coin(400,370),Coin(600,420),Coin(800,340)],
        'dec':[{'type':'stalactite','x':150,'h':40},{'type':'stalactite','x':400,'h':55},
               {'type':'stalactite','x':650,'h':35},{'type':'stalactite','x':820,'h':50}]})
    # Room 1: Crystal Chamber
    R.append({'name':'Crystal Chamber','bg':(20,15,40),
        'plat':[pygame.Rect(0,580,350,70),pygame.Rect(550,580,410,70),
                pygame.Rect(200,460,120,20),pygame.Rect(600,460,120,20),
                pygame.Rect(100,300,120,20),pygame.Rect(700,300,120,20)],
        'mplat':[MovingPlatform(350,420,100,16,1,0,100,0.008)],
        'spikes':[Spike(430,580,4)],
        'gems':[Gem(250,430,RED),Gem(460,350,BLUE),Gem(660,430,GREEN),Gem(160,270,YELLOW),Gem(760,270,PURPLE)],
        'enemies':[Enemy(500,580,PURPLE,50,1.0,pac=True),Enemy(200,580,RED,100,1.5),Enemy(700,300,RED,40,1.8,chaser=True)],
        'signs':[Sign(50,540,"Gems shimmer\nwith strange light...\nOrder matters?")],
        'doors':[Door(0,500,30,80,0,880,540,"<- Entrance"),Door(930,500,30,80,2,50,540,"-> Library"),
                 Door(420,200,60,80,4,450,540,"* Secret",GOLD,True)],
        'books':[],'thrones':[],'portals':[],'sw':None,
        'ckpt':[Checkpoint(50,580)],
        'coins':[Coin(260,430),Coin(380,390),Coin(460,350),Coin(660,430),Coin(760,270),
                 Coin(130,270),Coin(720,270),Coin(500,560)],
        'dec':[{'type':'crystal','x':380,'y':540,'c':CYAN},{'type':'crystal','x':550,'y':540,'c':PURPLE},
               {'type':'crystal','x':500,'y':340,'c':GREEN}]})
    # Room 2: Library
    R.append({'name':'The Library','bg':(25,20,30),
        'plat':[pygame.Rect(0,580,900,70),pygame.Rect(200,460,120,20),
                pygame.Rect(500,400,150,20),pygame.Rect(700,460,120,20)],
        'mplat':[],'spikes':[Spike(350,580,3)],
        'gems':[Gem(260,430,CYAN),Gem(575,370,GOLD)],
        'enemies':[Enemy(500,400,RED,60,1.3)],
        'signs':[Sign(350,540,"ERUTUF EKIL\nUOY ERA","I can see you\nreading this...\nNice try, player."),
                 Sign(50,540,"The books hold\nmany secrets.\nClick them!")],
        'doors':[Door(0,500,30,80,1,890,540,"<- Crystal"),Door(930,500,30,80,5,50,540,"-> Volcanic")],
        'books':[Bookshelf(680,360,120,100),Bookshelf(100,460,80,120),Bookshelf(800,460,80,120)],
        'thrones':[],'portals':[],'sw':pygame.Rect(350,430,20,150),'ckpt':[],
        'coins':[Coin(230,430),Coin(290,430),Coin(530,370),Coin(570,370),Coin(620,370)],
        'dec':[]})
    # Room 3: Throne Room
    R.append({'name':'???','bg':(15,10,25),
        'plat':[pygame.Rect(0,580,900,70),pygame.Rect(350,460,200,20)],
        'mplat':[],'spikes':[],
        'gems':[Gem(450,430,GOLD)],
        'enemies':[],
        'signs':[Sign(100,540,"You found the\nhidden throne room!\nThe throne awaits..."),
                 Sign(650,400,"Click the painting\nfor a surprise...","It's a secret to\neveryone.")],
        'doors':[Door(0,500,30,80,2,890,540,"<- Library")],
        'books':[],'thrones':[Throne(420,500)],'portals':[],'sw':None,'ckpt':[],
        'coins':[Coin(450,430),Coin(500,430),Coin(400,430)],
        'dec':[{'type':'painting','x':700,'y':300,'w':100,'h':80},
               {'type':'torch','x':200,'y':500},{'type':'torch','x':650,'y':500}]})
    # Room 4: Secret Garden
    R.append({'name':'Secret Garden','bg':(10,25,15),
        'plat':[pygame.Rect(0,580,900,70),pygame.Rect(200,470,100,20),
                pygame.Rect(400,400,100,20),pygame.Rect(600,470,100,20)],
        'mplat':[MovingPlatform(100,500,80,16,0,-1,80,0.006),MovingPlatform(750,500,80,16,0,-1,80,0.006)],
        'spikes':[],
        'gems':[Gem(250,440,PINK),Gem(450,370,GOLD),Gem(650,440,WHITE)],
        'enemies':[],
        'signs':[Sign(50,540,"You found the\nSecret Garden!\nThe portal leads\nhome...")],
        'doors':[Door(0,500,30,80,1,890,540,"<- Crystal")],
        'books':[],'thrones':[],'portals':[Portal(450,530)],'sw':None,
        'ckpt':[Checkpoint(50,580)],
        'coins':[Coin(250,440),Coin(450,370),Coin(650,440),Coin(140,470),Coin(790,470)],
        'dec':[{'type':'flower','x':100,'y':560,'c':PINK},{'type':'flower','x':300,'y':560,'c':YELLOW},
               {'type':'flower','x':500,'y':560,'c':PURPLE},{'type':'flower','x':700,'y':560,'c':CYAN},
               {'type':'flower','x':800,'y':560,'c':ORANGE}]})
    # Room 5: Volcanic
    R.append({'name':'Volcanic Depths','bg':(40,15,10),
        'plat':[pygame.Rect(0,580,200,70),pygame.Rect(300,580,100,70),
                pygame.Rect(500,580,100,70),pygame.Rect(750,580,210,70),
                pygame.Rect(150,470,100,20),pygame.Rect(400,420,100,20),
                pygame.Rect(650,470,100,20),pygame.Rect(300,320,120,20),
                pygame.Rect(550,250,120,20)],
        'mplat':[MovingPlatform(200,520,80,16,1,0,80,0.01),MovingPlatform(600,520,80,16,1,0,80,0.01),
                 MovingPlatform(420,340,80,16,0,-1,60,0.007)],
        'spikes':[Spike(200,580,5),Spike(400,580,5),Spike(600,580,5),Spike(750,580,4)],
        'gems':[Gem(200,440,ORANGE),Gem(450,390,RED),Gem(700,440,YELLOW),Gem(360,290,PURPLE),Gem(610,220,ORANGE)],
        'enemies':[Enemy(400,420,ORANGE,40,2.0,chaser=True),Enemy(650,470,RED,30,1.8)],
        'signs':[Sign(50,540,"The floor is\nlava! Well...\nalmost.")],
        'doors':[Door(0,500,30,80,2,890,540,"<- Library"),Door(930,500,30,80,6,50,540,"-> Sky Realm")],
        'books':[],'thrones':[],'portals':[],'sw':None,
        'ckpt':[Checkpoint(50,580)],
        'coins':[Coin(170,440),Coin(220,440),Coin(430,390),Coin(470,390),Coin(670,440),
                 Coin(730,440),Coin(340,290),Coin(380,290),Coin(590,220),Coin(630,220)],
        'dec':[{'type':'torch','x':100,'y':500},{'type':'torch','x':350,'y':380},
               {'type':'torch','x':600,'y':380},{'type':'torch','x':850,'y':500}]})
    # Room 6: Sky Realm
    R.append({'name':'Sky Realm','bg':(15,20,45),
        'plat':[pygame.Rect(0,580,150,70),pygame.Rect(800,580,160,70),
                pygame.Rect(200,480,80,20),pygame.Rect(450,400,80,20),
                pygame.Rect(700,480,80,20),pygame.Rect(300,300,100,20),
                pygame.Rect(550,200,100,20),pygame.Rect(200,120,120,20)],
        'mplat':[MovingPlatform(100,500,80,16,1,0,100,0.007),MovingPlatform(550,480,80,16,1,0,120,0.006),
                 MovingPlatform(400,350,80,16,0,-1,80,0.008),MovingPlatform(650,250,80,16,1,0,80,0.009)],
        'spikes':[],
        'gems':[Gem(240,450,CYAN),Gem(490,370,WHITE),Gem(740,450,PINK),Gem(350,270,GOLD),Gem(600,170,CYAN),Gem(260,90,GOLD)],
        'enemies':[Enemy(450,400,WHITE,30,2.2,chaser=True),Enemy(300,300,CYAN,40,1.5)],
        'signs':[Sign(50,540,"The sky realm...\nSo high, so free.\nFind the portal!")],
        'doors':[Door(0,500,30,80,5,890,540,"<- Volcanic")],
        'books':[],'thrones':[],'portals':[Portal(250,70)],'sw':None,
        'ckpt':[Checkpoint(50,580)],
        'coins':[Coin(230,450),Coin(480,370),Coin(730,450),Coin(330,270),Coin(370,270),
                 Coin(580,170),Coin(620,170),Coin(240,90),Coin(280,90),Coin(260,560)],
        'dec':[]})
    return R

# === MAIN GAME ===
class Game:
    def __init__(self):
        self.state='title';self.rooms=make_rooms();self.cr=0
        self.player=Player(100,540);self.fr=0;self.rt=0;self.tf=0
        self.stars=[(random.randint(0,WIDTH),random.randint(0,HEIGHT//2),random.uniform(0.5,2))for _ in range(60)]
        self.sa=pygame.Rect(380,250,200,200)
        self.trans=None;self.ta=0;self.tt=None;self.help=False
        self.title_rect=ftitle.render("THE LOST CAVERNS",True,GOLD).get_rect(center=(WIDTH//2,180))

    def rm(self): return self.rooms[self.cr]
    def total_coins(self): return sum(1 for r in self.rooms for c in r['coins'] if c.collected)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return False
            if self.state=='title':
                if ev.type==pygame.KEYDOWN:
                    chk_konami(ev.key)
                    if ev.key in(pygame.K_RETURN,pygame.K_SPACE):
                        self.state='playing'; ee.start_t=pygame.time.get_ticks()
                    chk_type(ev.key); proc_type()
                if ev.type==pygame.MOUSEBUTTONDOWN:
                    if self.title_rect.collidepoint(ev.pos) and not ee.title_click:
                        ee.title_click=True;ee.title_click_t=180;ee.secrets+=1
                        snd(SND_SECRET); add_fmsg("SECRET: You clicked the title!",WIDTH//2,250,PINK)
            elif self.state=='playing':
                if ev.type==pygame.KEYDOWN:
                    chk_konami(ev.key)
                    if ev.key in(pygame.K_SPACE,pygame.K_UP,pygame.K_w): self.player.jump()
                    if ev.key==pygame.K_LSHIFT or ev.key==pygame.K_RSHIFT: self.player.dash()
                    if ev.key==pygame.K_h: self.help=not self.help
                    if ev.key==pygame.K_ESCAPE: self.help=False
                    chk_type(ev.key); proc_type()
                if ev.type==pygame.MOUSEBUTTONDOWN:
                    mx,my=ev.pos; rm=self.rm()
                    for bs in rm['books']:
                        if bs.rect.collidepoint(mx,my):
                            ee.bclicks+=1
                            if ee.bclicks>=3 and not ee.fwall:
                                ee.fwall=True;ee.fwtimer=180;ee.secrets+=1;snd(SND_SECRET)
                                add_fmsg("SECRET: Fourth Wall Broken!",WIDTH//2,200,PURPLE)
                            break
                    for d in rm['dec']:
                        if d['type']=='painting':
                            pr=pygame.Rect(d['x'],d['y'],d['w'],d['h'])
                            if pr.collidepoint(mx,my) and not ee.snake_on:
                                ee.snake_on=True;ee.snake=[[5,5],[4,5],[3,5]]
                                ee.sdir=[1,0];ee.sfood=[random.randint(0,9),random.randint(0,9)]
                                ee.sscore=0;ee.stimer=0;ee.secrets+=1;snd(SND_SECRET)
                                add_fmsg("SECRET: Mini Snake Game!",WIDTH//2,200,GREEN)
                                break
            elif self.state=='snake':
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_ESCAPE: ee.snake_on=False
                    elif ev.key==pygame.K_UP and ee.sdir!=[0,1]: ee.sdir=[0,-1]
                    elif ev.key==pygame.K_DOWN and ee.sdir!=[0,-1]: ee.sdir=[0,1]
                    elif ev.key==pygame.K_LEFT and ee.sdir!=[1,0]: ee.sdir=[-1,0]
                    elif ev.key==pygame.K_RIGHT and ee.sdir!=[-1,0]: ee.sdir=[1,0]
            elif self.state=='gameover':
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN:
                    global ee,particles,float_msgs,shake_amt,shake_dur
                    ee=EE();particles=[];float_msgs=[];shake_amt=0;shake_dur=0
                    self.__init__();self.state='title'
        return True

    def change_room(self,dest,dx,dy):
        self.tt=(dest,dx,dy);self.trans='out';self.ta=0

    def update(self):
        global shake_amt,shake_dur
        self.fr+=1; update_p()
        for m in float_msgs[:]:
            m[3]-=1;m[2]-=0.5
            if m[3]<=0: float_msgs.remove(m)
        if ee.tbuft>0:
            ee.tbuft-=1
            if ee.tbuft<=0: ee.tbuf=""
        if shake_dur>0: shake_dur-=1

        if self.state=='title': self.tf+=1; return
        if self.state=='crash':
            ee.ctimer-=1
            if ee.ctimer<=0: ee.fcrash=False;self.state='playing'
            return
        if self.state=='snake': self.update_snake(); return
        if self.state!='playing': return

        # Transitions
        if self.trans=='out':
            self.ta=min(255,self.ta+18)
            if self.ta>=255:
                self.cr=self.tt[0];self.player.x=float(self.tt[1]);self.player.y=float(self.tt[2])
                self.player.vx=self.player.vy=0;self.player.sx=self.tt[1];self.player.sy=self.tt[2]
                self.trans='in'
            return
        if self.trans=='in':
            self.ta=max(0,self.ta-18)
            if self.ta<=0: self.trans=None
            return

        # Timers
        if ee.rainbow: ee.rhue=(ee.rhue+2)%360
        if ee.matrix:
            ee.mtimer-=1
            for d in ee.mdrops:
                d[1]+=3
                if d[1]>HEIGHT: d[1]=random.randint(-100,0);d[0]=random.randint(0,WIDTH//12)
            if ee.mtimer<=0: ee.matrix=False
        if ee.broll:
            ee.btimer-=1;ee.bangle=(ee.bangle+6)%360
            if ee.btimer<=0: ee.bangle=0;ee.broll=False
        if ee.a42: ee.a42t-=1
        if ee.a42t<=0: ee.a42=False
        if ee.huge: ee.htimer-=1
        if ee.htimer<=0: ee.huge=False
        if ee.blocky: ee.blocky_t-=1
        if ee.blocky_t<=0: ee.blocky=False
        if ee.gflip_t>0:
            ee.gflip_t-=1
            if ee.gflip_t<=0: ee.gravity_flip=False
        if ee.fwtimer>0: ee.fwtimer-=1
        if ee.sr_mt>0: ee.sr_mt-=1
        if ee.cmsgt>0: ee.cmsgt-=1
        if ee.won_t>0:
            ee.won_t-=1
            if ee.won_t<=0: self.state='gameover';return
        if ee.title_click_t>0: ee.title_click_t-=1
        if ee.fcrash: self.state='crash';return

        if not self.player.alive:
            self.rt+=1
            if self.rt>60: self.player.respawn();self.rt=0
            return

        rm=self.rm()
        plats=rm['plat'][:]
        if rm['sw'] and not ee.sw_found: plats.append(rm['sw'])

        # Moving platforms
        mp_vx,mp_vy=0,0
        for mp in rm['mplat']:
            mp.update()
            plats.append(mp.rect)
            pr=self.player.rect
            if pr.bottom>=mp.rect.top and pr.bottom<=mp.rect.top+8 and pr.right>mp.rect.left and pr.left<mp.rect.right:
                if self.player.vy>=0:
                    mp_vx=mp.vx;mp_vy=mp.vy
        self.player.update(plats,(mp_vx,mp_vy))

        # Doors
        for door in rm['doors']:
            if door.active and self.player.rect.colliderect(door.rect):
                self.change_room(door.dest,door.dx,door.dy);return

        # Gems
        for gem in rm['gems']:
            if not gem.collected and self.player.rect.colliderect(gem.rect):
                gem.collected=True;spawn_p(gem.x,gem.y,gem.c,12,3);snd(SND_COIN)
                ee.gem_order.append(gem.c)
                if len(ee.gem_order)>=5:
                    if ee.gem_order[-5:]==[RED,BLUE,GREEN,YELLOW,PURPLE]:
                        ee.sdoor=True;ee.secrets+=1;snd(SND_SECRET)
                        add_fmsg("SECRET: Gem Order Unlocked!",WIDTH//2,200,GOLD)
                        for d in self.rooms[1]['doors']:
                            if d.req: d.active=True

        # Coins
        for coin in rm['coins']:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected=True;ee.coins+=1;spawn_p(coin.x,coin.y,GOLD,6,2);snd(SND_COIN)
                if ee.coins==42 and not ee.coin42:
                    ee.coin42=True;ee.secrets+=1;snd(SND_SECRET)
                    add_fmsg("SECRET: 42 Coins! The meaning of wealth!",WIDTH//2,200,GOLD)

        # Enemies
        for en in rm['enemies']:
            if not en.alive: continue
            en.update(self.player.x,self.player.y-20)
            if self.player.rect.colliderect(en.rect):
                if en.pac and not en.friend:
                    if not ee.pstarted: ee.pstarted=True;ee.ptimer=480
                    continue
                if en.friend: continue
                if self.player.dash_t>0:
                    en.alive=False;spawn_p(en.x,en.y-12,en.c,15,4);snd(SND_STOMP);continue
                if self.player.vy>0 and self.player.rect.bottom<en.rect.centery+5:
                    en.alive=False;self.player.vy=-8;spawn_p(en.x,en.y-12,en.c,15,4);snd(SND_STOMP)
                    if en.pac: ee.ptimer=0
                else:
                    self.player.take_damage(1)

        # Spikes
        for sp in rm['spikes']:
            if self.player.rect.colliderect(sp.rect): self.player.take_damage(1)

        # Checkpoints
        for cp in rm['ckpt']:
            if not cp.on and self.player.rect.colliderect(cp.rect):
                cp.on=True;self.player.sx=cp.x;self.player.sy=cp.y-40
                snd(SND_CKPT);add_fmsg("Checkpoint!",WIDTH//2,100,GREEN)

        # Pacifist
        if ee.ptimer>0 and not ee.pacifist:
            ee.ptimer-=1
            if ee.ptimer<=0:
                for en in self.rooms[1]['enemies']:
                    if en.pac and en.alive:
                        en.friend=True;ee.pacifist=True;ee.secrets+=1;snd(SND_SECRET)
                        add_fmsg("SECRET: Pacifist Friendship!",WIDTH//2,200,PURPLE)

        # Secret wall
        if rm['sw'] and not ee.sw_found:
            sw=rm['sw']
            test=pygame.Rect(sw.x-15,sw.y,sw.width+30,sw.height)
            if self.player.rect.colliderect(test):
                ee.sw_found=True;ee.secrets+=1;snd(SND_SECRET)
                add_fmsg("SECRET: Hidden Passage!",WIDTH//2,200,CYAN)
                rm['doors'].append(Door(sw.x-10,sw.y+30,40,60,3,890,540,"-> ???",PURPLE))

        # Throne
        for th in rm['thrones']:
            if self.player.rect.colliderect(th.rect):
                if not ee.on_throne: ee.on_throne=True;ee.ttimer=0
                ee.ttimer+=1
                if ee.ttimer>=180 and not ee.king:
                    ee.king=True;ee.secrets+=1;snd(SND_SECRET)
                    add_fmsg("SECRET: You are the King!",WIDTH//2,200,GOLD)
                    spawn_p(self.player.x,self.player.y-30,GOLD,30,5)
            else: ee.on_throne=False;ee.ttimer=0

        # Portal
        for portal in rm['portals']:
            d=math.hypot(self.player.x-portal.x,self.player.y-20-portal.y)
            if d<portal.r+15 and not ee.won:
                ee.won=True;ee.won_t=180
                el=(pygame.time.get_ticks()-ee.start_t)/1000
                if el<60:
                    ee.sr_msg=True;ee.sr_mt=180;ee.secrets+=1
                    add_fmsg("SECRET: Speedrunner!",WIDTH//2,150,ORANGE)
                spawn_p(portal.x,portal.y,WHITE,40,6)

        # Corner secret (Room 0)
        if self.cr==0:
            if self.player.x<50 and self.player.y<200:
                ee.ctimer2+=1
                if ee.ctimer2>=300 and not ee.csecret:
                    ee.csecret=True;ee.cmsgt=180;ee.secrets+=1;snd(SND_SECRET)
                    add_fmsg("SECRET: The corner knows...",WIDTH//2,200,WHITE)
            else: ee.ctimer2=max(0,ee.ctimer2-2)

    def update_snake(self):
        ee.stimer+=1
        if ee.stimer>=8:
            ee.stimer=0
            h=[ee.snake[0][0]+ee.sdir[0],ee.snake[0][1]+ee.sdir[1]]
            h[0]%=10;h[1]%=10
            if h in ee.snake:
                ee.snake=[[5,5],[4,5],[3,5]];ee.sdir=[1,0]
                ee.sfood=[random.randint(0,9),random.randint(0,9)];ee.sscore=0;return
            ee.snake.insert(0,h)
            if h==ee.sfood:
                ee.sfood=[random.randint(0,9),random.randint(0,9)];ee.sscore+=1
            else: ee.snake.pop()

    def draw(self):
        buf=pygame.Surface((WIDTH,HEIGHT))
        if self.state=='title': self.draw_title(buf)
        elif self.state=='crash': self.draw_crash(buf)
        elif self.state=='snake': self.draw_game(buf);self.draw_snake_ov(buf)
        elif self.state=='gameover': self.draw_go(buf)
        else: self.draw_game(buf)

        for m in float_msgs: dtctr(buf,m[0],fmed,m[4],int(m[2]))

        # Screen shake
        global shake_amt,shake_dur
        if shake_dur>0:
            ox=random.randint(-shake_amt,shake_amt);oy=random.randint(-shake_amt,shake_amt)
            screen.fill(BLACK);screen.blit(buf,(ox,oy))
        else:
            screen.blit(buf,(0,0))

        # Barrel roll
        if ee.broll and ee.bangle!=0:
            tmp=screen.copy();rot=pygame.transform.rotate(tmp,ee.bangle)
            screen.fill(BLACK);screen.blit(rot,rot.get_rect(center=(WIDTH//2,HEIGHT//2)))
        # Mirror
        if ee.mirror:
            tmp=screen.copy();screen.blit(pygame.transform.flip(tmp,True,False),(0,0))
        # Transition
        if self.ta>0:
            fade=pygame.Surface((WIDTH,HEIGHT));fade.fill(BLACK);fade.set_alpha(self.ta)
            screen.blit(fade,(0,0))

    def draw_title(self,sf):
        sf.fill((10,8,20))
        for sx,sy,ss in self.stars:
            b=int(128+127*math.sin(self.tf*0.03+sx))
            pygame.draw.circle(sf,(b,b,b),(int(sx),int(sy)),max(1,int(ss)))
        tc=rc(self.tf*3) if ee.rainbow else GOLD
        dtctr(sf,"THE LOST CAVERNS",ftitle,tc,180)
        dtctr(sf,"Enhanced Edition",fsmall,GRAY,230)
        if self.tf%60<40: dtctr(sf,"Press ENTER to Start",fmed,WHITE,350)
        hints=["Arrow/WASD: Move | Space/Up: Jump (x2!)","Shift: Dash | H: Help | Click things!",
               "Try typing commands...","Some walls aren't what they seem",
               "Not all enemies want to fight","Order matters for gems",
               "Look for the classic code...","Patience is a virtue",
               "42 coins hold a secret..."]
        for i,h in enumerate(hints):
            dtctr(sf,h,ftiny,(40+i*2,40+i*2,50+i*2),410+i*17)
        if ee.tbuf: dtctr(sf,ee.tbuf+"_",fsmall,(100,100,120),590)
        if ee.secrets>0: dtxt(sf,f"Secrets: {ee.secrets}/20",fsmall,GOLD,10,10)
        if ee.title_click_t>0:
            dtctr(sf,"You found the title secret!",fsmall,PINK,280)

    def draw_crash(self,sf):
        sf.fill((0,0,170))
        dtctr(sf,":(  Your PC ran into a problem",fmed,WHITE,150)
        dtctr(sf,"and needs to restart.",fmed,WHITE,185)
        dtctr(sf,"Stop code: CAVES_TOO_SECRET",fsmall,WHITE,300)
        dtctr(sf,"What failed: PlayerCuriosity.sys",fsmall,WHITE,325)
        pct=min(100,int((200-ee.ctimer)/2))
        dtctr(sf,f"Completing: {pct}%",fsmall,WHITE,370)
        pygame.draw.rect(sf,WHITE,(WIDTH//2-100,390,200,10),1)
        pygame.draw.rect(sf,WHITE,(WIDTH//2-98,392,int(196*pct/100),6))
        if ee.ctimer<120: dtctr(sf,"...just kidding :)",flarge,WHITE,460)
        if ee.ctimer<60:
            dtctr(sf,"SECRET: Don't panic!",fmed,GOLD,530)
            dtctr(sf,"(The answer is 42)",fsmall,GRAY,560)

    def draw_go(self,sf):
        sf.fill((10,5,15))
        dtctr(sf,"CONGRATULATIONS!",ftitle,GOLD,100)
        dtctr(sf,"You escaped The Lost Caverns!",fmed,WHITE,170)
        el=ee.start_t and(pygame.time.get_ticks()-ee.start_t)/1000 or 0
        dtctr(sf,f"Time: {el:.1f}s",fmed,CYAN,230)
        dtctr(sf,f"Deaths: {ee.deaths}",fmed,RED,270)
        dtctr(sf,f"Coins: {ee.coins}/42",fmed,GOLD,310)
        dtctr(sf,f"Secrets Found: {ee.secrets}/20",fmed,PURPLE,350)
        if ee.king: dtctr(sf,"* The King of the Caverns *",fmed,GOLD,400)
        if ee.sr_msg: dtctr(sf,">> SPEEDRUNNER <<",flarge,ORANGE,450)
        dtctr(sf,"Press ENTER to play again",fsmall,GRAY,560)
        sl=[]
        if ee.rainbow: sl.append("Rainbow")
        if ee.night: sl.append("Night Vision")
        if ee.sw_found: sl.append("Hidden Passage")
        if ee.pacifist: sl.append("Pacifist")
        if ee.sdoor: sl.append("Gem Order")
        if ee.king: sl.append("King")
        if ee.fcrash: sl.append("Fake Crash")
        if ee.csecret: sl.append("Corner")
        if ee.fwall: sl.append("Fourth Wall")
        if ee.sscore>0 or ee.snake_on: sl.append("Snake")
        if ee.sr_msg: sl.append("Speedrunner")
        if ee.coin42: sl.append("42 Coins")
        if ee.blocky: sl.append("Minecraft")
        if ee.dancing: sl.append("Dance")
        if ee.title_click: sl.append("Title Click")
        if ee.gravity_flip: sl.append("Gravity Flip")
        if ee.matrix: sl.append("Matrix")
        if sl:
            y=490
            for i,s in enumerate(sl):
                dtxt(sf,f"* {s}",ftiny,PURPLE,20+(i%4)*200,y+(i//4)*16)

    def draw_game(self,sf):
        rm=self.rm(); bg=rm['bg']
        if ee.rainbow: bg=hsv_rgb(ee.rhue,0.3,0.15)
        sf.fill(bg)

        # Parallax bg layers
        for i,(sx,sy,ss) in enumerate(self.stars):
            if sy<rm['plat'][0].y-50:
                ox=(self.fr*(i%3+1)*0.2)%WIDTH
                bx=int((sx+ox)%WIDTH)
                b=int(80+40*math.sin(self.fr*0.02+sx))
                pygame.draw.circle(sf,(b,b,min(255,b+20)),(bx,int(sy)),max(1,int(ss*0.7)))

        # Lava glow for volcanic
        if rm['name']=='Volcanic Depths':
            for i in range(5):
                ly=590+math.sin(self.fr*0.05+i)*5
                gx=random.randint(0,WIDTH);gw=random.randint(30,80)
                gs=pygame.Surface((gw,20),pygame.SRCALPHA)
                pygame.draw.ellipse(gs,(255,100,0,40+int(20*math.sin(self.fr*0.1+i))),gs.get_rect())
                sf.blit(gs,(gx,ly))

        for d in rm['dec']: draw_dec(sf,d,self.fr)
        for bs in rm['books']: bs.draw(sf)
        for th in rm['thrones']: th.draw(sf,self.fr)
        for pt in rm['portals']: pt.draw(sf,self.fr)
        for sp in rm['spikes']: sp.draw(sf)
        for cp in rm['ckpt']: cp.draw(sf,self.fr)

        for p in rm['plat']:
            c=rc(ee.rhue+p.x*0.5)if ee.rainbow else STONE
            pygame.draw.rect(sf,c,p);pygame.draw.line(sf,tuple(min(255,v+30)for v in c),p.topleft,p.topright,2)
            pygame.draw.rect(sf,tuple(max(0,v-20)for v in c),p,1)
        for mp in rm['mplat']: mp.draw(sf)

        if rm['sw'] and not ee.sw_found:
            sw=rm['sw'];pygame.draw.rect(sf,STONE,sw);pygame.draw.rect(sf,LSTONE,sw,1)
            if self.fr%120<5:
                pygame.draw.line(sf,DGRAY,(sw.x+5,sw.y+10),(sw.x+15,sw.y+50),1)

        for gem in rm['gems']: gem.draw(sf,self.fr)
        for coin in rm['coins']: coin.draw(sf,self.fr)
        for en in rm['enemies']: en.draw(sf)
        for sign in rm['signs']:
            near=self.player.rect.inflate(60,60).colliderect(sign.rect)
            sign.draw(sf,near)
        for door in rm['doors']: door.draw(sf,self.fr)

        self.player.draw(sf)
        draw_p(sf)

        # Night vision
        if ee.night:
            dark=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA);dark.fill((0,0,0,210))
            px,py=int(self.player.x),int(self.player.y-20)
            for r in range(120,0,-2):
                a=int(210*(1-r/120))
                pygame.draw.circle(dark,(0,0,0,a),(px,py),r)
            sf.blit(dark,(0,0))

        # Matrix
        if ee.matrix:
            for col,row in ee.mdrops:
                ch=chr(random.randint(33,126));b=random.randint(100,255)
                dtxt(sf,ch,fsmall,(0,b,0),col*12,int(row))

        # 42
        if ee.a42:
            sz=int(40+(150-ee.a42t)*0.5);f=pygame.font.SysFont("consolas",min(sz,80),True)
            s=f.render("42",True,GOLD);sf.blit(s,s.get_rect(center=(WIDTH//2,HEIGHT//2)))

        # Corner msg
        if ee.cmsgt>0:
            msgs=["You found the corner secret!","The walls have ears...",
                  "But corners have eyes.","Keep exploring."]
            idx=min(len(msgs)-1,(180-ee.cmsgt)//45)
            dtctr(sf,msgs[idx],fsmall,WHITE,100)

        # Pacifist bar
        if ee.ptimer>0 and not ee.pacifist and ee.pstarted:
            p=1-ee.ptimer/480;bx,by,bw,bh=WIDTH//2-50,75,100,8
            pygame.draw.rect(sf,DGRAY,(bx,by,bw,bh));pygame.draw.rect(sf,PURPLE,(bx,by,int(bw*p),bh))
            dtctr(sf,"Patience...",ftiny,PURPLE,by-10)

        # Throne bar
        if ee.on_throne and not ee.king:
            p=ee.ttimer/180;bx,by,bw,bh=WIDTH//2-50,75,100,8
            pygame.draw.rect(sf,DGRAY,(bx,by,bw,bh));pygame.draw.rect(sf,GOLD,(bx,by,int(bw*p),bh))
            dtctr(sf,"Sitting...",ftiny,GOLD,by-10)

        # Win
        if ee.won and ee.won_t>0:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            a=min(200,(180-ee.won_t)*3);ov.fill((255,255,255,a));sf.blit(ov,(0,0))
            if ee.won_t<120: dtctr(sf,"YOU WIN!",fhuge,GOLD,HEIGHT//2-30)

        if ee.sr_msg and ee.sr_mt>0: dtctr(sf,">> SPEEDRUNNER DETECTED <<",fmed,ORANGE,50)

        # Title click msg
        if ee.title_click_t>0 and self.state=='title':
            pass  # handled in draw_title

        self.draw_hud(sf)

        # Help overlay
        if self.help:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA);ov.fill((0,0,0,180));sf.blit(ov,(0,0))
            lines=["=== CONTROLS ===","Arrow Keys / WASD - Move","Space / Up / W - Jump (Double Jump!)",
                   "Shift - Dash (has cooldown)","H - Toggle this help","ESC - Close help","",
                   "=== TIPS ===","Explore every corner","Try typing commands (type anything!)",
                   "Not all enemies want to fight","Collect gems in order: R B G Y P",
                   "Click on bookshelves and paintings","Sit on the throne patiently",
                   "There are 20 secrets to find!","Die 5 times for a 'surprise'","",
                   "=== PRESS H TO CLOSE ==="]
            for i,l in enumerate(lines):
                c=GOLD if"==="in l else WHITE if l else GRAY
                dtctr(sf,l,fsmall,c,120+i*22)

    def draw_hud(self,sf):
        rm=self.rm()
        # Hearts
        for i in range(self.player.max_hp):
            hx=WIDTH-40-i*30;hy=12
            if i<self.player.hp:
                pts=[(hx,hy+4),(hx-8,hy-4),(hx-4,hy-4),(hx-4,hy-12),(hx+4,hy-12),
                     (hx+4,hy-4),(hx+8,hy-4)]
                pygame.draw.polygon(sf,RED,pts)
                pygame.draw.polygon(sf,(255,100,100),pts,1)
            else:
                pts=[(hx,hy+4),(hx-8,hy-4),(hx-4,hy-4),(hx-4,hy-12),(hx+4,hy-12),
                     (hx+4,hy-4),(hx+8,hy-4)]
                pygame.draw.polygon(sf,DGRAY,pts)

        dtxt(sf,rm['name'],fsmall,WHITE,10,10)
        tg=sum(1 for r in self.rooms for g in r['gems']if g.collected)
        pg=sum(len(r['gems'])for r in self.rooms)
        dtxt(sf,f"Gems: {tg}/{pg}",fsmall,GOLD,10,30)
        dtxt(sf,f"Coins: {ee.coins}/42",fsmall,YELLOW,10,50)
        if ee.secrets>0: dtxt(sf,f"Secrets: {ee.secrets}/20",fsmall,PURPLE,10,70)
        if ee.deaths>0: dtxt(sf,f"Deaths: {ee.deaths}",fsmall,RED,WIDTH-120,35)
        if ee.start_t:
            el=(pygame.time.get_ticks()-ee.start_t)/1000
            dtxt(sf,f"Time: {el:.1f}s",fsmall,CYAN,WIDTH-140,55)

        # Dash cooldown bar
        if self.player.dash_cd>0:
            p=1-self.player.dash_cd/90;bx,by,bw,bh=WIDTH//2-30,HEIGHT-20,60,6
            pygame.draw.rect(sf,DGRAY,(bx,by,bw,bh));pygame.draw.rect(sf,CYAN,(bx,by,int(bw*p),bh))
            dtxt(sf,"Dash",ftiny,GRAY,bx-35,by-2)
        else:
            dtxt(sf,"Dash Ready",ftiny,CYAN,WIDTH//2-30,HEIGHT-22)

        # Double jump indicator
        jleft=self.player.jumps if self.player.on_ground else max(0,self.player.jumps)
        for i in range(self.player.max_j):
            c=CYAN if i<jleft else DGRAY
            pygame.draw.circle(sf,c,(WIDTH//2-10+i*20,HEIGHT-35),5)

        # Active effects
        y=90;fx=[]
        if ee.rainbow: fx.append(("Rainbow",rc(ee.rhue)))
        if ee.night: fx.append(("Night",CYAN))
        if ee.mirror: fx.append(("Mirror",PINK))
        if ee.huge: fx.append(("God Mode",GOLD))
        if ee.king: fx.append(("King",GOLD))
        if ee.blocky: fx.append(("Blocky",BROWN))
        if ee.dancing: fx.append(("Dance!",PINK))
        if ee.gravity_flip: fx.append(("Flip!",CYAN))
        for n,c in fx: dtxt(sf,f"* {n}",ftiny,c,10,y);y+=15

        if ee.tbuf: dtxt(sf,f"> {ee.tbuf}_",fsmall,(120,120,140),WIDTH//2-60,HEIGHT-45)

        # Minimap
        mmx,mmy,ms=WIDTH-130,HEIGHT-90,4
        pygame.draw.rect(sf,(0,0,0,150),(mmx-2,mmy-2,ms*7+4,ms*2+4))
        for i in range(7):
            c=WHITE if i==self.cr else GRAY
            if i<3: pygame.draw.rect(sf,c,(mmx+i*ms,mmy,ms-1,ms-1))
            elif i<5: pygame.draw.rect(sf,c,(mmx+(i-3)*ms,mmy+ms,ms-1,ms-1))
            elif i==5: pygame.draw.rect(sf,c,(mmx+4*ms,mmy+ms,ms-1,ms-1))
            else: pygame.draw.rect(sf,c,(mmx+5*ms,mmy,ms-1,ms-1))

    def draw_snake_ov(self,sf):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA);ov.fill((0,0,0,150));sf.blit(ov,(0,0))
        sa=self.sa;pygame.draw.rect(sf,BLACK,sa);pygame.draw.rect(sf,GREEN,sa,2)
        cw,ch=sa.width//10,sa.height//10
        fx=sa.x+ee.sfood[0]*cw+cw//2;fy=sa.y+ee.sfood[1]*ch+ch//2
        pygame.draw.circle(sf,RED,(fx,fy),cw//3)
        for i,(sx,sy) in enumerate(ee.snake):
            c=GREEN if i==0 else(0,150,0)
            r=pygame.Rect(sa.x+sx*cw+1,sa.y+sy*ch+1,cw-2,ch-2)
            pygame.draw.rect(sf,c,r,border_radius=2)
        dtctr(sf,f"Snake Score: {ee.sscore}",fsmall,WHITE,sa.y-20)
        dtctr(sf,"Arrow keys to move, ESC to exit",ftiny,GRAY,sa.bottom+15)

def main():
    game=Game();running=True
    while running:
        running=game.handle_events()
        game.update();game.draw()
        pygame.display.flip();clock.tick(60)
    pygame.quit();sys.exit()

if __name__=="__main__": main()