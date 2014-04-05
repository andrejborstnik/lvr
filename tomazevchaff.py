from util import *
from booli import *
from time import *
from random import *
def tchaff(formula, time = False):
    t = clock()
    a = ptchaff(formula)
    t1 = clock()
    if time:
        print(t1-t)
    return a,t1-t

def ptchaff(formula):

    ########################## ZAČETNO ČIŠČENJE ####################################################
    
    vrednost = {i:None for i in formula.spremenljivke()}
    form = formula.poenostavi(cnf=True)

    if type(form)==T: return vrednost
    elif type(form)==F: return "Formula ni izpolnljiva"
    elif type(form)==Neg: vrednost[i.izr.ime] = False; return vrednost
    elif type(form)==Spr: vrednost[i.ime] = True; return vrednost

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
                
        form = form.vstavi(nove).poenostavi(cnf=True)

        if type(form)==T: return vrednost
        elif type(form)==F: return "Formula ni izpolnljiva"

    
    #Ostali so nam le Ali-ji dolžine 2 in več

    
    ############################ NEKATERE DEFINICIJE #####################################################################
        
    proban = {}                                             #1 - v eno smer proban, 2 - obe možnosti že preizkušeni
    kontrolni = {}                                          #za vsak stavek kateri literali so v njem kontrolni
    kontrolniOd = {}                                        #za kontrolne literale pove za katere stavke so kontrolni
    literali = {}                                           #za vsak literal iz formule pove kako pogost je
    vzrok = {}                                              #kaj je pripeljalo do sklepa
    

    #izberemo kontrolne literale
    for stavek in form.sez:
        temp = iter(stavek.sez)
        a = next(temp)
        b = next(temp)
        kontrolni[stavek]=[a,b]
        if a in kontrolniOd: kontrolniOd[a].append(stavek)
        else: kontrolniOd[a]=[stavek]
        if b in kontrolniOd: kontrolniOd[b].append(stavek)
        else: kontrolniOd[b]=[stavek]
        
    #poiščemo vse literale v naši formuli in vse njihove negacije (tudi če jih v formuli ni)
    for stavek in form.sez:
        for lit in stavek.sez:
            literali[lit]=literali.get(lit,0)+1

    
            
    ################################ POMOŽNE FUNKCIJE ######################################################################
    def ugibaj():
        """izbere literal brez določene vrednosti, ki je najpogostejši"""
        y = max(literali,key= lambda x: literali[x])
        if literali[y]<=0:
            return None
        else:
            vzrok[y] = []
            return y
        
    def sklepaj(novi):
        """Po ugibanju tranzitivno naredi sklepe, ki iz njega sledijo"""
        temp = []
        for lit in novi:
            sklepi[a].append(lit)
            literali[lit]*=-1   #frekvenci spremeni predznak, da vemo da je že izbran - zato ga ne izberemo še enkrat
            u = Neg(lit) if type(lit)==Spr else lit.izr
            if u in literali: literali[u]*=-1
            if type(lit)==Spr:
                x = lit.ime
                if vrednost[x] == False: return False   #prišlo je do konflikta
                elif vrednost[x] == None:
                    vrednost[x]=True
                    if Neg(lit) in kontrolniOd: temp = menjaj(Neg(lit),temp)
            elif type(lit)==Neg:
                x = lit.izr.ime
                if vrednost[x]: return False    #prišlo je do konflikta
                elif vrednost[x] == None:
                    vrednost[x]=False
                    if lit.izr in kontrolniOd: temp = menjaj(lit.izr,temp)
            else:
                raise InternalError("Formula je v napačnem formatu.")

        return temp

    def menjaj(l,temp):
        """kontrolni literal l je treba zamenjati, ker je l nastavljen na False"""
        for stavek in kontrolniOd[l]:
            najden = False
            i=kontrolni[stavek].index(l)
            #če stavek še ni izpolnjen
            if vrednost[kontrolni[stavek][1-i].ime if type(kontrolni[stavek][1-i])==Spr else kontrolni[stavek][1-i].izr.ime]==None:
                for literal in stavek.sez:
                    if literal not in kontrolni[stavek] and vrednost[literal.ime if type(literal)==Spr else literal.izr.ime]!=False:
                        kontrolni[stavek][i]=literal
                        if literal in kontrolniOd: kontrolniOd[literal].append(stavek)
                        else: kontrolniOd[literal]=[stavek]
                        najden = True
                        kontrolniOd[l].remove(stavek)
                        break
                if not najden:
                    x = kontrolni[stavek][1-i]  #edini ostali kontrolni literal v stavku, ki more dati vrednost True+
                    temp.append(x)
                    vzrok[x] = [t for t in stavek.sez if t!=x]
        if kontrolniOd[l]==[]: del kontrolniOd[l]
        return temp

    def resiproblem(ugibanja):
        """če pride do protislovja pri ugibanju se vrnemo do najkasnejšega ugibanja, ki še ni imelo preverjeni obe možnosti """
        i = len(ugibanja)-1
        while proban[ugibanja[i] if type(ugibanja[i]) == Spr else ugibanja[i].izr]==2:
            i-=1
            if i<0: return "korenček" #vse možnosti že sprobane
        #print(ugibanja)
        #print(sklepi)
        for odl in range(i,len(ugibanja)):
            #print("")
            #print(ugibanja[odl])
            for lit in sklepi[ugibanja[odl]]:
                #ponovno bo lahko izbran za ugibanje
                literali[lit]*=-1   
                u = Neg(lit) if type(lit)==Spr else lit.izr
                if u in literali: literali[u]*=-1
                vrednost[lit.ime if type(lit)==Spr else lit.izr.ime] = None
                del vzrok[lit]
            del sklepi[ugibanja[odl]]
            #print(sklepi)
            if odl>i:
                del proban[ugibanja[odl]]
        naslednji[0] = Neg(ugibanja[i]) if type(ugibanja[i]) == Spr else ugibanja[i].izr
        ugibanja = ugibanja[:i]
        return ugibanja

    def konstavek(lit):
        """vrne nov stavek, ki prepreči ponavljanje iste napake """
        nabor = vzrok[lit]+vzrok[Neg(lit) if type(lit)==Spr else lit.izr]
        c= True
        while c:
            print(nabor)
            c = False
            temp = []
            for x in nabor:
                a=vzrok[Neg(x) if type(x)==Spr else x.izr]
                if a:
                    c = True
                    temp+= a
                else:
                    temp.append(x)
            nabor = temp
        return Ali(*tuple(nabor))
        

    ##################################################### TEŽKO DELO ############################################################################
    
    sklepi = {}         #za vsako ugibanje kateri sklepi so sledili
    ugibanja = []       #zaporedje ugibanj
    naslednji = [False]      #če imamo določeno kaj probamo naslednje (ko pride do konflikta, se vrnemo do zadnje odločitve ne sprobane v obe smeri. S tem določimo da je naslednja na vrsti druga možnost za to ugibanje)
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
        b = a if type(a)== Spr else a.izr
        proban[b]=proban.get(b,0)+1
        sklepi[a]=[]
        novi = [a]
        while novi:
            novi = sklepaj(novi)
            
        if novi==False:     #treba trackat backat
            ugibanja = resiproblem(ugibanja)
            if ugibanja == "korenček": return "Formula ni izpolnljiva"

primer = In(Ali(Spr("x"),Spr("z")),Ali(Spr("x"),Spr("u")),Ali(Spr("x"),Spr("v")),Ali(Neg(Spr("x")),Neg(Spr("y"))),Ali(Neg(Spr("x")),Spr("y")))
                
                
        
                
            
                    
                    



















