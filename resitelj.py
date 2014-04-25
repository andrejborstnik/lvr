from util import *
from booli import *
from time import clock
from random import random,shuffle,seed

def resitelj(formula, time = False, restart = False):
    t1 = clock()
    a,b = presitelj(formula,restart,1)
    t = clock()-t1
    if time:
        print("Časi:")
        i="zacetno";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        i="uvod";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        i="ugibanje";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        i="sklepanje";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        i="resiproblem";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        i="konstavek";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        i="periode";print("{0:<12}: {1:.3f} {2:.3f}".format(i,b[i],b[i]/t))
        print("{0:<12}: {1:.3f}".format("skupno",t))
    return a

def presitelj(formula,restart,lub):

    casi = {"zacetno":0,"ugibanje":0,"sklepanje":0,"resiproblem":0,"periode":0,"konstavek":0,"uvod":0}

########################## ZAČETNO ČIŠČENJE ####################################################

    def ime(lit):
        return lit.ime if type(lit)==Spr else lit.izr.ime

    def vred(lit):
        if lit>0:
            return vrednost1[lit]
        if lit<0:
            a = vrednost1[-lit]
            return a if a==None else (not a)

    
        
    vrednost = {i:None for i in formula.spremenljivke()}
    form = formula.poenostavi(chff=True)

    if type(form)==T: return vrednost,casi
    elif type(form)==F: return "Formula ni izpolnljiva",casi
    elif type(form)==Neg: vrednost[form.izr.ime] = False; return vrednost,casi
    elif type(form)==Spr: vrednost[form.ime] = True; return vrednost,casi

    #Najprej določimo vrednost enojcem
    nove = True
    while nove:
        zac = clock()
        nove = {}
        for stavek in form.sez:
            if type(stavek) == Spr:
                nove[stavek.ime]=True
                vrednost[stavek.ime]=True
            elif type(stavek) == Neg:
                nove[stavek.izr.ime]=False
                vrednost[stavek.izr.ime]=False
                
        form = form.vstavi(nove).poenostavi(chff=True)

        casi["zacetno"]+=clock()-zac

        if type(form)==T: return vrednost,casi
        elif type(form)==F: return "Formula ni izpolnljiva",casi
        elif type(form)==Neg: vrednost[form.izr.ime] = False; return vrednost,casi
        elif type(form)==Spr: vrednost[form.ime] = True; return vrednost,casi

    
    
    #Ostali so nam le Ali-ji dolžine 2 in več

    
############################ NEKATERE DEFINICIJE #####################################################################

    zac = clock()
    
    proban = {}                                             #ključi so imena spremenljivk. 1 - v eno smer proban, 2 - obe možnosti že preizkušeni
    literali = {}                                           #ključi so literali. za vsak literal iz formule pove kako pogost je
    stavki = {}                                             #ključi so literali, za vsak literal iz formule pove v katerih stavkih je
    vzrok = {}                                              #ključi so literali. kaj je pripeljalo do sklepa
    sklepi = {}                                             #ključi so literali. za vsako ugibanje kateri sklepi so sledili
    ugibanja = []                                           #vsebuje literale. zaporedje ugibanj
    naslednji = [False]                                     #vsebuje literal. če imamo določeno kaj probamo naslednje (ko pride do konflikta, se vrnemo do zadnje odločitve ne sprobane v obe smeri. S tem določimo da je naslednja na vrsti druga možnost za to ugibanje) 
    stevec1 = 0
    stevec2 = 0

    #literale preimenujemo v številke - dela bistveno hitreje
    stevilka = {}
    inverz = {}
    t = 1
    for im in form.spremenljivke():
        stevilka[im]=t
        inverz[t]=im
        t+=1
    
    #poiščemo vse literale v naši formuli
    for stavek in form.sez:
        n = len(stavek.sez)
        nov = [ (stevilka[ime(lit)] if type(lit)==Spr else -stevilka[ime(lit)]) for lit in stavek.sez ]                
        for lit in stavek.sez:
            num = (stevilka[ime(lit)] if type(lit)==Spr else -stevilka[ime(lit)])            
            literali[num]=literali.get(num,0)+ 10/n
            literali[-num] = literali.get(-num,0)
            stavki[num] = stavki.get(num,[])+[nov]
            stavki[-num] = stavki.get(-num,[])


    vrednost1 = {i:None for i in range(1,t)}
            
    casi["uvod"]+=clock()-zac

    #parametri
    perioda1 = 40
    perioda2 = 5*len(stevilka)
    koef = 0.5
    
            
################################ POMOŽNE FUNKCIJE ######################################################################

    def izhod():
        for i in vrednost1:
            vrednost[inverz[i]]=vrednost1[i]
        return vrednost

    def ugibaj():
        """Izbere literal brez določene vrednosti, ki je najpogostejši."""
        zac=clock()
        temp = [i for i in literali.keys() if literali.get(i)>0]
        if not temp:
            casi["ugibanje"]+=clock()-zac
            return None
        else:
            shuffle(temp)
            y = max(temp,key= lambda x: literali[x])
            vzrok[y] = []
            casi["ugibanje"]+=clock()-zac
            return y
        
    def sklepaj(novi,a):
        """Po ugibanju tranzitivno naredi sklepe, ki iz njega sledijo"""
        temp = []
        zac = clock()
        for lit,zakaj in novi:
            sklepi[a].add(lit)
            vzrok[lit] = zakaj
            literali[lit]=-abs(literali[lit])   #frekvenci spremeni predznak, da vemo da je že izbran - zato ga ne izberemo še enkrat
            literali[-lit]=-abs(literali[-lit])

        #pogledamo za enojce    
        for lit,_ in novi:
            x = abs(lit)
            if lit>0:
                if vrednost1[x] == False:
                    casi["sklepanje"]+=clock()-zac
                    return "konflikt",lit   #prišlo je do konflikta
                elif vrednost1[x] == None:
                    vrednost1[x]=True
                    temp = preglej(-lit,temp)
                    
            elif lit<0:
                if vrednost1[x]:
                    casi["sklepanje"]+=clock()-zac
                    return "konflikt",lit   #prišlo je do konflikta
                elif vrednost1[x] == None:
                    vrednost1[x]=False
                    temp = preglej(-lit,temp)

            else:
                raise InternalError("Formula je v napačnem formatu.")
            
            if temp and temp[0]=="konflikt":
                casi["sklepanje"]+=clock()-zac
                return temp

        casi["sklepanje"]+=clock()-zac
        return temp

    def preglej(l,temp):
        """Literal l je bil nastavljen na False. Pogleda katere implikacije iz tega sledijo. """
        
        for st in stavki[l]:
            
            izpolnjen = False
            nevredni = [] 
            for lit in st:
                
                if vred(lit)==True:
                    #stavek je že izpolnjen, iz njega ne bo novih sklepov
                    izpolnjen = True
                    break
                elif vred(lit)==None:
                    nevredni.append(lit)
            
            if not izpolnjen and len(nevredni)==1:
                temp.append((nevredni[0],[i for i in st if i!=nevredni[0]]))
        return temp
                

    def resiproblem(ugibanja,kons):
        """Če pride do protislovja pri ugibanju sestopa dokler ne odstranimo vsaj enega od sklepov, ki so pripeljali do težav."""
        zac = clock()
        indeksi = sorted([ugibanja.index(-l) for l in kons]) #indeksi konfliktnih ugibanj
        i = indeksi[-1]
        while proban[abs(ugibanja[i])]==2:
            i-=1
            if i<0:
                casi["resiproblem"]+=clock()-zac
                return "konec" #vse možnosti že sprobane
        #odstranimo vse sklepe ki smo jih naredili od tega ugibanja dalje
        for odl in range(i,len(ugibanja)):
            for lit in sklepi[ugibanja[odl]]:
                #ponovno bo lahko izbran za ugibanje
                literali[lit]=abs(literali[lit])
                literali[-lit]=abs(literali[-lit])
                vrednost1[abs(lit)] = None
                del vzrok[lit]
            del sklepi[ugibanja[odl]]
            if odl>i:
                del proban[abs(ugibanja[odl])]
        naslednji[0] = -ugibanja[i]
        ugibanja = ugibanja[:i]
                        
        casi["resiproblem"]+=clock()-zac
        
        return ugibanja

    def konstavek(lit):
        """Vrne nov stavek, ki prepreči ponavljanje ugibanj, za katera smo ugotovili da skupaj vodijo do protislovja. """
        zac=clock()
        nabor = vzrok.get(-lit,[])+vzrok.get(lit,[])
        koreni = set()
        c= True
        while c:
            c = False
            tempo = []
            for x in nabor:
                a=vzrok[-x]
                if a!=[]:
                    c = True
                    tempo+= a
                else:
                    koreni.add(x)
            nabor = tempo
        casi["konstavek"]+=clock()-zac
        return list(koreni)

            
##################################################### TEŽKO DELO ############################################################################       
        
    
    while True:
        if naslednji[0]:
            a = naslednji[0]
            vzrok[a]=[]
            naslednji[0]=False
        else:
            a = ugibaj()
        if not a:
            return izhod(),casi #vsi literali imajo vrednost
        
        ugibanja.append(a)
        proban[abs(a)]=proban.get(abs(a),0)+1
        sklepi[a]=set()
        novi = [(a,[])]
        while novi and novi[0]!="konflikt":
            novi = sklepaj(novi,a)
        
        if novi and novi[0]=="konflikt":     #treba trackat backat
            kons = konstavek(novi[1])
            stevec1+=1
            stevec2+=1
            ugibanja = resiproblem(ugibanja,kons)
            if ugibanja == "konec": return "Formula ni izpolnljiva",casi

            zac=clock()
            if stevec1==perioda1:
                #manjša prioritete
                stevec1=0
                for x in literali:
                    literali[x]*=koef

            #dodamo konfliktni stavek
            n = len(kons)
            for i in kons:
                stavki[i].append(kons)
                if literali[i]>0 or literali[-i]>0: literali[i]+=100/n
                else: literali[i]-=100/n

            if restart and (perioda2*luby(lub))==stevec2:
                print("primitiven restart")
                seed()
                return presitelj(formula,restart,lub)

            casi["periode"]+=clock()-zac
