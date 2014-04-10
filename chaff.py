from util import *
from booli import *
from time import *
from random import *
from prevedbe import *


def chaff(formula, time = False, debug=False):
    t = clock()
    a = pchaff(formula,debug)
    t1 = clock()
    if time:
        print(t1-t)
    return a

def pchaff(formula,debug):

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
    kontrolni = {}                                          #ključi so stavki. za vsak stavek kateri literali so v njem kontrolni
    kontrolniOd = {}                                        #ključi so literali. za kontrolne literale pove za katere stavke so kontrolni
    literali = {}                                           #ključi so literali. za vsak literal iz formule pove kako pogost je
    vzrok = {}                                              #ključi so literali. kaj je pripeljalo do sklepa
    sklepi = {}                                             #ključi so literali. za vsako ugibanje kateri sklepi so sledili
    ugibanja = []                                           #vsebuje literale. zaporedje ugibanj
    naslednji = [False]                                     #vsebuje literal. če imamo določeno kaj probamo naslednje (ko pride do konflikta, se vrnemo do zadnje odločitve ne sprobane v obe smeri. S tem določimo da je naslednja na vrsti druga možnost za to ugibanje)
    

    #izberemo kontrolne literale
    for stavek in form.sez:
        temp = iter(stavek.sez)
        a = next(temp)
        b = next(temp)
        kontrolni[stavek]=[a,b]
        kontrolniOd[a]=kontrolniOd.get(a,[])+[stavek]
        kontrolniOd[b]=kontrolniOd.get(b,[])+[stavek]
        
    #poiščemo vse literale v naši formuli
    for stavek in form.sez:
        for lit in stavek.sez:
            literali[lit]=literali.get(lit,0)+1
            literali[neg(lit)] = literali.get(neg(lit),0)

    stliteralov = len(literali)
            
    ################################ POMOŽNE FUNKCIJE ######################################################################
    def ugibaj():
        """izbere literal brez določene vrednosti, ki je najpogostejši"""
        y = max(literali,key= lambda x: literali[x])
        if literali[y]<=0:
            return None
        else:
            vzrok[y] = []
            return y
        
    def sklepaj(novi,a):
        """Po ugibanju tranzitivno naredi sklepe, ki iz njega sledijo"""
        temp = []
        for lit in novi:
            sklepi[a].add(lit)
            literali[lit]=-abs(literali[lit])   #frekvenci spremeni predznak, da vemo da je že izbran - zato ga ne izberemo še enkrat
            literali[neg(lit)]=-abs(literali[neg(lit)])
            x = ime(lit)
            if type(lit)==Spr:
                if vrednost[x] == False: return "konflikt",lit   #prišlo je do konflikta
                elif vrednost[x] == None:
                    vrednost[x]=True
                    if neg(lit) in kontrolniOd: temp = menjaj(neg(lit),temp)
                    
            elif type(lit)==Neg:
                if vrednost[x]: return "konflikt",lit   #prišlo je do konflikta
                elif vrednost[x] == None:
                    vrednost[x]=False
                    if neg(lit) in kontrolniOd: temp = menjaj(neg(lit),temp)
                    
            else:
                raise InternalError("Formula je v napačnem formatu.")
            if temp and temp[0]=="konflikt": return temp
            
        return temp

    def menjaj(l,temp):
        """kontrolni literal l je treba zamenjati, ker je l nastavljen na False"""
        for stavek in kontrolniOd[l]:
            najden = False
            kont = kontrolni[stavek]
            i=kont.index(l)
            drugi = kont[1-i]
            #če stavek še ni izpolnjen
            v = vred(drugi)
            if v == None or v == True:
                for literal in stavek.sez:
                    if literal not in kont and vred(literal)!=False:
                        kont[i]=literal
                        kontrolniOd[literal] = kontrolniOd.get(literal,[])+[stavek]
                        najden = True
                        kontrolniOd[l].remove(stavek)
                        break
                if not najden and v==None:
                    temp.append(drugi)
                    vzrok[drugi] = [t for t in stavek.sez if t!=drugi]
            elif v==False:
                vzrok[l] = [t for t in stavek.sez if t!=l]
                return "konflikt",l
        if kontrolniOd[l]==[]: del kontrolniOd[l]
        return temp

    def resiproblem(ugibanja):
        """če pride do protislovja pri ugibanju se vrnemo do najkasnejšega ugibanja, ki še ni imelo preverjeni obe možnosti """
        i = len(ugibanja)-1
        while proban[ime(ugibanja[i])]==2:
            i-=1
            if i<0: return "konec" #vse možnosti že sprobane
        #print(ugibanja)
        #print(sklepi)
        #odstranimo vse sklepe ki smo jih naredili od tega ugibanja dalje
        for odl in range(i,len(ugibanja)):
            #print("")
            #print(ugibanja[odl])
            for lit in sklepi[ugibanja[odl]]:
                #ponovno bo lahko izbran za ugibanje
                if literali[lit]>0: print("neki ga serje")
                literali[lit]=abs(literali[lit])
                literali[neg(lit)]=abs(literali[neg(lit)])
                vrednost[ime(lit)] = None
                del vzrok[lit]
            del sklepi[ugibanja[odl]]
            #print(sklepi)
            if odl>i:
                del proban[ime(ugibanja[odl])]
        naslednji[0] = neg(ugibanja[i])
        ugibanja = ugibanja[:i]
        return ugibanja

    def konstavek(lit):
        """vrne nov stavek, ki prepreči ponavljanje iste napake """
        nabor = vzrok.get(neg(lit),[])+vzrok.get(neg(lit),[])
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


    def analiza():
        """Preveri če je vse kot mora biti """


        doloceni = []
        for x in sklepi.values():
            doloceni = doloceni + list(x)

        opravil = True
        for lit in doloceni:
            if literali[lit]>0: opravil = False
        if not opravil: print("0 - obstaja dolocen literal ki ga lahko izberemo za ugibanje.")
            
        
        opravil = True
        for stavek in form.sez:
            opravil = opravil and (len(kontrolni[stavek])==2)
        if opravil: print("1 - Vsak stavek ima dva kontrolna literala.")
        else: print("0 - Obstaja stavek s premalo kontrolnimi literali!")

        opravil = True
        for stavek in form.sez:
            opravil = opravil and (stavek in kontrolniOd[kontrolni[stavek][0]] and stavek in kontrolniOd[kontrolni[stavek][1]])
        if not opravil: print("0 - Obstaja stavek, čigar kontrolni literali ne vejo, da so njegovi!")
        else: print("1 - Kontrolni literali od stavkov vejo kam spadajo")

        opravil = True
        for lit in kontrolniOd:
            for stavek in kontrolniOd[lit]:
                opravil = opravil and (lit in kontrolni[stavek])
        if not opravil: print("0 - Obstaja literal, ki misli da je kontrolni za nekaj kar ni.")
        else: print("1 - Vsi kontrolni literali imajo svoje stavke.")

        opravil = True
        for lit in literali:
            ime = lit.ime if type(lit)==Spr else lit.izr.ime
            if vrednost[ime]!=None and lit not in doloceni and Neg(lit).poenostavi() not in doloceni:
                opravil = False
        if opravil: print("1 - Vse spremenljivke z vrednostjo so v sklepih.")
        else: print("0 - Obstaja spremenljivka z vrednostjo, ki je ni v sklepih.")

        opravil = True
        for lit in doloceni:
            a = lit.ime if type(lit)==Spr else lit.izr.ime
            if vrednost[a]==None: opravil = False
        if opravil: print("1 - Vsaka sklepana spremenljivka ima vrednost.")
        else: print("0 - Obstaja sklepana spremenljivka brez vrednosti.")

        opravil = True
        for stavek in kontrolni:
            lit1 = kontrolni[stavek][0]
            lit2 = kontrolni[stavek][1]
            ime1 = lit1.ime if type(lit1)==Spr else lit1.izr.ime
            ime2 = lit2.ime if type(lit2)==Spr else lit2.izr.ime
            
            if vrednost[ime1]!=None:
                if type(lit1)==Spr: a = vrednost[ime1]
                else: a = not vrednost[ime1]
            else: a = None
            
            if vrednost[ime2]!=None:
                if type(lit2)==Spr: b = vrednost[ime2]
                else: b = not vrednost[ime2]
            else: b = None
            
            if (a == None and b == False) or (a ==False and b==None):
                print("999 - Obstaja stavek, ki ima en kontrolni False drugega pa ne na True.")
                opravil = False
            elif b==False and a == False:
                print("999 - Obstaja stavek ki ima oba kontrolna False!")
                print(stavek)
                print(kontrolni[stavek])
                print(sklepi)
                opravil = False
        if opravil: print("1 - Vsi kontrolni literali so zadovoljivo vrednoteni.")

        if ugibanja!="korenček":

            opravil = True
            for lit in ugibanja:
                try:
                    a = lit if type(lit)==Spr else lit.izr
                except:
                    print(type(lit))
                    print(ugibanja)
                opravil = opravil and (a in proban)
            if opravil: print("1 - Vsa ugibanja so evidentirana v proban")
            else: print("0 - Obstaja ugibanje, ki ga nismo shranili med probane")

            opravil = True
            for spr in proban:
                opravil = opravil and (spr in ugibanja+naslednji or Neg(spr) in ugibanja+naslednji)
            if opravil: print("1 - Vse kar je zabeležno kot probano je v ugibanja.")
            else: print("0 - Nekaj imamo kot probano, čeprou ni med ugibanji.")
            
            if len(set(doloceni))!=len(doloceni): print("0 - Obstaja sklep ki se pojavi večkrat.")
            else: print("1 - Vsak sklep se pojavi natanko enkrat.")

        opravil = True
        for lit in vzrok:
            opravil = opravil and (lit in doloceni)
        if opravil: print("1 - Vsak literal z vzrokom je določen.")
        else: print("0 - Imamo literal z vzrokom, ki pa ni določen.")

        opravil = True
        for lit in doloceni:
            opravil = opravil and (lit in vzrok)
        if opravil: print("1 - Vsak sklep ima svoj vzrok.")
        else: print("0 - Obstaja sklep brez vzroka.")

        if len(literali)!=stliteralov:
            print("0 - stevilo literalov se spremeni.")
        else:
            print("1 - stevilo literalov je enako kot na začetku.")
            
##################################################### TEŽKO DELO ############################################################################       
        
    
    while True:
        if naslednji[0]:
            a = naslednji[0]
            vzrok[a]=[]
            naslednji[0]=False
        else:
            a = ugibaj()
        #print(a, ugibanja)
        if not a:
            return vrednost #vsi literali imajo vrednost
        ugibanja.append(a)
        proban[ime(a)]=proban.get(ime(a),0)+1
        sklepi[a]=set()
        novi = [a]
        while novi and novi[0]!="konflikt":
            novi = sklepaj(novi,a)
        #print(ugibanja, sklepi[a])
        #print()

        if debug:
            print("Stanje po ugibanju in sklepanju:")
            analiza()
            print()
            

        #print(sklepi)
        if novi and novi[0]=="konflikt":     #treba trackat backat
            #print(konstavek(novi[1]))
            ugibanja = resiproblem(ugibanja)
            if debug:
                print("Stanje po sestopanju:")
                analiza()
                print()
            if ugibanja == "konec": return "Formula ni izpolnljiva"
    
prim = In(Ali(Spr("x"),Spr("z")),Ali(Spr("x"),Spr("u")),Ali(Spr("x"),Spr("v")),Ali(Neg(Spr("x")),Neg(Spr("y"))),Ali(Neg(Spr("x")),Spr("y")))
                
                
        
                
            
                    
                    



















