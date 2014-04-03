from util import *
from booli import *
from time import *
from random import *


def tchaff(formula):

    ########################## ZAČETNO ČIŠČENJE ####################################################
    
    vrednost = {i:None for i in formula.spremenljivke()}
    form = formula.poenostavi(cnf=True)

    if type(form)==T: return vrednost
    elif type(form)==F: return "Formula ni izpolnljiva"

    

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

    print(kontrolni)
    print()
    print(kontrolniOd)
    print()
            
    ################################ POMOŽNE FUNKCIJE ######################################################################
    def ugibaj():
        """izbere literal brez določene vrednosti, ki je najpogostejši"""
        y = max(literali,key= lambda x: literali[x])
        if literali[y]<=0:
            return None
        else:
            return y
        
    def sklepaj():
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
                vrednost[x]=True
                if Neg(lit) in kontrolniOd: menjaj(Neg(lit))
            else:
                x = lit.izr.ime
                if vrednost[x]: return False    #prišlo je do konflikta
                vrednost[x]=False
                if lit in kontrolniOd: menjaj(lit)

    def menjaj(l):
        """kontrolni literal l je treba zamenjati, ker je l nastavljen na False"""
        for stavek in kontrolniOd[l]:
            najden = False
            i=kontrolni[stavek].index(l)
            for literal in stavek.sez:
                if literal not in kontrolni[stavek] and vrednost[literal.ime if type(literal)==Spr else literal.izr.ime]!=False:
                    kontrolni[stavek][i]=literal
                    if literal in kontrolniOd: kontrolniOd[literal].append(stavek)
                    else: kontrolniOd[literal]=[stavek]
                    najden = True
                    break
            if not najden:
                x = kontrolni[stavek][1-i]  #edini ostali kontrolni literal v stavku, ki more dati vrednost True
                novi.append(x)
        del kontrolniOd[l]

    def resiproblem():
        """če pride do protislovja pri ugibanju se vrnemo do najkasnejšega ugibanja, ki še ni imelo preverjeni obe možnosti """
        print("konflikt!")
        i = len(ugibanja)-1
        while proban[ugibanja[i]]==2:
            i-=1
            if i<0: return True #vse možnosti že sprobane

        for odl in range(i,len(ugibanja)):
            for lit in sklepi[ugibanja[odl]]:
                #ponovno bo lahko izbran za ugibanje
                literali[lit]*=-1   
                u = Neg(lit) if type(lit)==Spr else lit.izr
                if u in literali: literali[u]*=-1
                vrednost[lit.ime if type(lit)==Spr else lit.izr.ime] = None
            del sklepi[ugibanja[odl]]
            if odl>i:
                del proban[ugibanja[odl]]
        ugibanja = ugibanja[:i]
        return False

    ##################################################### TEŽKO DELO ############################################################################
    
    print("primer ni lahek")
    sklepi = {}         #za vsako ugibanje kateri sklepi so sledili
    ugibanja = []       #zaporedje ugibanj
    while True:
        print(literali)
        a = ugibaj()
        if not a:
            return vrednost #vsi literali imajo vrednost
        ugibanja.append(a)
        proban[a]=proban.get(a,0)+1
        sklepi[a]=[]
        novi = [a]
        while novi:
            novi = sklepaj()
        if novi==False:     #treba trackat backat
            if resiproblem(): return "Formula ni izpolnljiva"


                
                
        
                
            
                    
                    



















