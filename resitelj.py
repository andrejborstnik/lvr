from util import *
from booli import *
from time import *
from random import *
from prevedbe import *

def resitelj(formula, time = False):
    t = clock()
    a = presitelj(formula)
    t1 = clock()
    if time:
        print("Porabljen čas:",t1-t)
    return a

def presitelj(formula):

########################## ZAČETNO ČIŠČENJE ####################################################

    def ime(lit):
        return lit.ime if type(lit)==Spr else lit.izr.ime

    def neg(lit):
        return Neg(lit) if type(lit)==Spr else lit.izr

    def vred(lit):
        if type(lit) == Spr:
            return vrednost[lit.ime]
        else:
            a = vrednost[lit.izr.ime]
            return a if a==None else (not a)
    
        
    vrednost = {i:None for i in formula.spremenljivke()}
    form = formula.poenostavi(chff=True)

    if type(form)==T: return vrednost
    elif type(form)==F: return "Formula ni izpolnljiva"
    elif type(form)==Neg: vrednost[form.izr.ime] = False; return vrednost
    elif type(form)==Spr: vrednost[form.ime] = True; return vrednost

    #Najprej določimo vrednost enojcem
    nove = True
    while nove:
        nove = {}
        for stavek in form.sez:
            if type(stavek) == Spr:
                nove[stavek.ime]=True
                vrednost[stavek.ime]=True
            elif type(stavek) == Neg:
                nove[stavek.izr.ime]=False
                vrednost[stavek.izr.ime]=False
                
        form = form.vstavi(nove).poenostavi(chff=True)

        if type(form)==T: return vrednost
        elif type(form)==F: return "Formula ni izpolnljiva"
        elif type(form)==Neg: vrednost[form.izr.ime] = False; return vrednost
        elif type(form)==Spr: vrednost[form.ime] = True; return vrednost

    
    #Ostali so nam le Ali-ji dolžine 2 in več

    
############################ NEKATERE DEFINICIJE #####################################################################
    
    proban = {}                                             #ključi so imena spremenljivk. 1 - v eno smer proban, 2 - obe možnosti že preizkušeni
    literali = {}                                           #ključi so literali. za vsak literal iz formule pove kako pogost je
    stavki = {}                                             #ključi so literali, za vsak literal iz formule pove v katerih stavkih je
    vzrok = {}                                              #ključi so literali. kaj je pripeljalo do sklepa
    sklepi = {}                                             #ključi so literali. za vsako ugibanje kateri sklepi so sledili
    ugibanja = []                                           #vsebuje literale. zaporedje ugibanj
    naslednji = [False]                                     #vsebuje literal. če imamo določeno kaj probamo naslednje (ko pride do konflikta, se vrnemo do zadnje odločitve ne sprobane v obe smeri. S tem določimo da je naslednja na vrsti druga možnost za to ugibanje)
    
        
    #poiščemo vse literale v naši formuli
    for stavek in form.sez:
        n = len(stavek.sez)
        for lit in stavek.sez:
            literali[lit]=literali.get(lit,0)+10/n
            literali[neg(lit)] = literali.get(neg(lit),0)
            stavki[lit] = stavki.get(lit,[])+[stavek]
            stavki[neg(lit)] = stavki.get(neg(lit),[])

    stliteralov = len(literali)
    perioda = 100
    koef = 2
    stevec = 0
    cas = 0
            
################################ POMOŽNE FUNKCIJE ######################################################################
    def ugibaj():
        """Izbere literal brez določene vrednosti, ki je najpogostejši."""
        y = max(literali,key= lambda x: literali[x]+(random() if literali[x]>0 else -random()))
        
        if literali[y]<=0.0:
            return None
        else:
            vzrok[y] = []
            return y
        
    def sklepaj(novi,a):
        """Po ugibanju tranzitivno naredi sklepe, ki iz njega sledijo"""
        temp = []
        for lit,stavek in novi:
            sklepi[a].add(lit)
            vzrok[lit] = stavek
            literali[lit]=-abs(literali[lit])   #frekvenci spremeni predznak, da vemo da je že izbran - zato ga ne izberemo še enkrat
            literali[neg(lit)]=-abs(literali[neg(lit)])
            
        for lit,_ in novi:
            x = ime(lit)
            if type(lit)==Spr:
                if vrednost[x] == False:
                    return "konflikt",lit   #prišlo je do konflikta
                elif vrednost[x] == None:
                    vrednost[x]=True
                    temp = preglej(neg(lit),temp)
                    
            elif type(lit)==Neg:
                if vrednost[x]:
                    return "konflikt",lit   #prišlo je do konflikta
                elif vrednost[x] == None:
                    vrednost[x]=False
                    temp = preglej(neg(lit),temp)

            else:
                raise InternalError("Formula je v napačnem formatu.")
            
            if temp and temp[0]=="konflikt": return temp
        
        return temp

    def preglej(l,temp):
        """Literal l je bil nastavljen na False. Pogleda katere implikacije iz tega sledijo. """
        #print("trenutne vrednosti",vrednost)
        #print("negirali smo:",l,vred(l))
        for st in stavki[l]:
            #print("stavek:",st)
            izpolnjen = False
            nevredni = [] 
            for lit in st.sez:
                if vred(lit)==True:
                    #print(lit)
                    #stavek je že izpolnjen, iz njega ne bo novih sklepov
                    izpolnjen = True
                    break
                elif vred(lit)==None:
                    nevredni.append(lit)
            if not izpolnjen and len(nevredni)==1:
                temp.append((nevredni[0],[i for i in st.sez if i!=nevredni[0]]))
            #print("izpolnjen:",izpolnjen)
            #print("nevredni so:",nevredni)
        return temp
                

    def resiproblem(ugibanja,kons):
        """Če pride do protislovja pri ugibanju sestopa dokler ne odstranimo vsaj enega od sklepov, ki so pripeljali do težav."""
        indeksi = sorted([ugibanja.index(neg(l)) for l in kons.sez]) #indeksi
        i = indeksi[-1]
        while proban[ime(ugibanja[i])]==2:
            i-=1
            if i<0: return "konec" #vse možnosti že sprobane
        #odstranimo vse sklepe ki smo jih naredili od tega ugibanja dalje
        for odl in range(i,len(ugibanja)):
            for lit in sklepi[ugibanja[odl]]:
                #ponovno bo lahko izbran za ugibanje
                literali[lit]=abs(literali[lit])
                literali[neg(lit)]=abs(literali[neg(lit)])
                vrednost[ime(lit)] = None
                del vzrok[lit]
            del sklepi[ugibanja[odl]]
            if odl>i:
                del proban[ime(ugibanja[odl])]
        naslednji[0] = neg(ugibanja[i])
        ugibanja = ugibanja[:i]
        return ugibanja

    def konstavek(lit):
        """Vrne nov stavek, ki prepreči ponavljanje ugibanj, za katera smo ugotovili da skupaj vodijo do protislovja. """
        nabor = vzrok.get(neg(lit),[])+vzrok.get(lit,[])
        c= True
        while c:
            c = False
            tempo = []
            for x in nabor:
                a=vzrok[neg(x)]
                if a!=[]:
                    c = True
                    tempo+= a
                else:
                    tempo.append(x)
            nabor = tempo
        return Ali(*tuple(nabor))

            
##################################################### TEŽKO DELO ############################################################################       
        
    
    while True:
        if naslednji[0]:
            a = naslednji[0]
            vzrok[a]=[]
            naslednji[0]=False
        else:
            a = ugibaj()
        if not a:
            return vrednost #vsi literali imajo vrednost
        
        ugibanja.append(a)
        #print("ugibanja:",ugibanja)
        proban[ime(a)]=proban.get(ime(a),0)+1
        sklepi[a]=set()
        novi = [(a,[])]
        while novi and novi[0]!="konflikt":
            novi = sklepaj(novi,a)

        #print("sklepi:",sklepi)
        #print(vzrok)
        #print()
        
        if novi and novi[0]=="konflikt":     #treba trackat backat
            kons = konstavek(novi[1])
            stevec+=1
            #print(ugibanja,"kons=",kons)
            ugibanja = resiproblem(ugibanja,kons)
            if ugibanja == "konec": return "Formula ni izpolnljiva"
            for i in kons.sez:
                stavki[i].append(kons)
                if stevec==perioda:
                    stevec=0
                    for x in literali:
                        literali[x]/=koef
                if literali[i]>0 or literali[neg(i)]>0: literali[i]+=10/len(kons.sez)
                else: literali[i]-=10/len(kons.sez)

    
prim1 = In(Ali(Spr("x"),Spr("z")),Ali(Spr("x"),Spr("u")),Ali(Spr("x"),Spr("v")),Ali(Neg(Spr("x")),Neg(Spr("y"))),Ali(Neg(Spr("x")),Spr("y")))
                

##x = latinski(prazna(6));
##print("n=",6,x.vrednost(resitelj(x,True)))
##print()
##
##x = latinski(prazna(7));
##y = resitelj(x,True)
##print("n=",7,x.vrednost(y))

##                
##l= sudoku(lahek)
##print("Lahek: ", l.vrednost(resitelj(l,True)))
##print()

##s= sudoku(sreden)
##print("Sreden: ", s.vrednost(resitelj(s,True)))
##print()
##
##z= sudoku(zloben)
##print("Zloben: ", z.vrednost(resitelj(z,True)))

                    





















