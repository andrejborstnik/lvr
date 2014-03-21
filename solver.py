from util import *
from booli import *

############ Brute force #########

def bfSAT(formula):
    spr = formula.spremenljivke()
    n=len(spr)

    def poskusi(ze,se,form):
        if se:
            x = se.pop()
            
            ze[x]=False
            a= poskusi(ze,se,form)
            if a: return a
            
            ze[x]=True
            a= poskusi(ze,se,form)
            se|={x}
            return a
            
        else:
            if form.vrednost(ze):
                return ze
            else:
                return False

    if spr:
        return poskusi({},spr,formula)
        
    else:
        if form.vrednost({}):
            return {}
        else:
            return False



############ DPLL ############
        
from time import clock
def DPLL(formula,cas = False):
    #Če želimo imeti vse spremenljivke definirane uporabimo zakomentirano.
    t1 = clock()
##    pomo = DPLLpomo(formula.kopiraj())
##    spr = formula.spremenljivke()
##    if not pomo:
##        return False
##    for i in spr:
##        if i not in pomo.keys():
##            pomo[i] = False/True, kar nam paše
##    return pomo
    a = DPLLpomo(formula.kopija())
    t2 = clock()
    if cas:
        print("Čas za izračun:  {0}".format(t2-t1))
    print("Rešitev: \n{0}".format(a))
    return a

def DPLLpomo(formula,vrednosti = {}):
    #formula mora biti v cnf obliki. Če ni, jo v to spremenimo
    #vrne valucaijo, če ta obstaja in False sicer (pozor!!! valuacija je lahko prazen slovar!)

    formula = CNF(formula)#že poenostavi zraven
    
    if formula == F():
        return False
    elif type(formula) == Spr:
        vrednosti[formula.ime] = True
        return vrednosti
    elif type(formula) == Neg:
        vrednosti[formula.izr.ime] = False
        return vrednosti
    elif formula == T() or (not formula.sez):
        return vrednosti

    #za spremenljivke, ki nastopajo samostojno vemo kaj morajo biti, zato jih kar določimo in pokrajšamo formulo
    novevrednosti = {0:1}
    while novevrednosti:
        novevrednosti = {}
        #odstrani = [] #da deluje hitreje odstranimo tiste enojce, ki smo jih določili. ??? Ali je to res hitreje?
        for i in formula.sez:
            #In(Ali(Spr("x"))) je že poenostavljen v In(Spr("x")), In(Ali()) pa v False, tako da smo pokrili vse primere.
            if type(i) == Spr:
                novevrednosti[i.ime] = True
                vrednosti[i.ime] = True
                ##odstrani.append(i)
            elif type(i) == Neg:#Negacija ima notri samo eno spr, saj smo že poenostavili.
                ##odstrani.append(i)
                novevrednosti[i.izr.ime] = False
                vrednosti[i.izr.ime] = False
##        for i in odstrani:
##            formula.sez.remove(i)
        formula = formula.vstavi(novevrednosti).poenostavi(True)
        if type(formula)==T:
            return vrednosti
        elif type(formula)==F:
            return False
        elif type(formula) == Spr:
            vrednosti[formula.ime] = True
            return vrednosti
        elif type(formula) == Neg:
            vrednosti[formula.izr.ime] = True
            return vrednosti

    #Stavke s čistimi spremenljivkami lahko pobrišemo. Čiste spremenljivke dobijo ustrezno vrednost. glede na to ali nastopajo z negacijo oz. brez.
    spr = formula.spremenljivke()
    for i in spr:
        pomo = cista(formula,i)
        if pomo:
            vrednosti[i] = pomo[1]
            odstrani=[]
            for k in formula.sez:
                if i in repr(k):
                    odstrani.append(k)
            for k in odstrani:
                formula.sez.remove(k)
            formula = formula.poenostavi(True)
            if type(formula)==T:
                return vrednosti
            elif type(formula)==F:
                return False
            elif type(formula)==Spr:
                vrednosti[formula.ime] = True
                return vrednosti
            elif type(formula) == Neg:
                vrednosti[formula.izr.ime] = False
                return vrednosti

    spr = formula.spremenljivke()
    #Izberemo si neko spremenljivko in poizkusimo obe možnosti 
    b = spr.pop()

    formula1 = formula.vstavi({b:True}).poenostavi(True)
    vrednosti[b] = True
    pomo = DPLLpomo(formula1, vrednosti)
    if pomo!=False:
        return pomo
    
    formula1 = formula.vstavi({b:False}).poenostavi(True)
    vrednosti[b] = False
    pomo = DPLLpomo(formula1, vrednosti)
    return pomo



############### Chaff DPLL ############


def Chaff(formula):
    def slovar(vrednosti,kazalci):
        pomo = {}
        for i in range(len(vrednosti)):
            pomo[kazalci[i]] = vrednosti[i][0]
        return pomo
    def izberi(literali):
        a = literali[0]
        j = 0
        for i in range(len(literali)):
            if literali[i] > a:
                a = literali[i]
                j = i
        return j
    formula = formula.poenostavi(True)
    spr = formula.spremenljivke()
    kazalci = [0] * len(spr)
    obratnikazalci = {}
    opazovaneSpr={}#Slovar, ki za spr. pove v katerih stavkih je opazovana.
    sprStavki = {}#Slovar, ki za spr. pove v katerih stavkih je vsebovana.
    k=0
    for i in spr:
        kazalci[k] = i
        obratnikazalci[i] = k
        opazovaneSpr[i] = set()
        k += 1
    vrednosti = [None] * len(spr)
    literali = [0] * (2*len(spr))
    koraki = Sklad()

    #dokler imamo enojce jih krajšamo.
    novevrednosti = {0:1}
    while novevrednosti:
        novevrednosti = {}
        odstrani = []
        for i in formula.sez:
            #In(Ali(Spr("x"))) je že poenostavljen v In(Spr("x")), In(Ali()) pa v False, tako da smo pokrili vse primere.
            if type(i) == Spr:
                novevrednosti[i.ime] = True
                vrednosti[obratnikazalci[i.ime]] = (True,2)
                odstrani.append(i)
            elif type(i) == Neg:#Negacija ima notri samo eno spr, saj smo že poenostavili.
                odstrani.append(i)
                novevrednosti[i.izr.ime] = False
                vrednosti[obratnikazalci[i.izr.ime]] = (False,2)
            for i in odstrani:
                formula.sez.remove(i)
            formula = formula.vstavi(novevrednosti).poenostavi(True)
            if type(formula)==T:
                return slovar(vrednosti)
            elif type(formula)==F:
                return False
            elif type(formula) == Spr:
                vrednosti[obratnikazalci[formula.ime]] = (True,2)
                return slovar(vrednosti)
            elif type(formula) == Neg:
                vrednosti[obratnikazalci[formula.izr.ime]] = (False,2)
                return slovar(vrednosti)
    
    izraz = []#Formulo spremenimo v seznam seznamov, ker bo tako lažje izvajati algoritem.
    opazovaneSta = [] #Seznam, ki za stavke pove kateri spremenljivki sta v njem opazovani (lahko tudi ena ali 0 spr).
    for i in formula.sez:
        podizraz = []
        if len(i.sez)>1:
            for j in i.sez:
                if type(j) == Spr:
                    podizraz.append((obratnikazalci[j],False)) #False pomeni da spremenljivka ni negirana
                    if obratnikazalci[j] in sprStavki.keys():
                        sprStavki[obratnikazalci[j]].add(len(izraz)-1)
                    else:
                        sprStavki[obratnikazalci[j]]={len(izraz)-1}
                elif type(j) == Neg:
                    podizraz.append((obratnikazalci[j.izr],True))
                    if obratnikazalci[j.izr] in sprStavki.keys():
                        sprStavki[obratnikazalci[j.izr]].add(len(izraz)-1)
                    else:
                        sprStavki[obratnikazalci[j.izr]]={len(izraz)-1}
                else:
                    raise UsageError("Ta formula ni bila poenostavljena pravilno.")
            izraz.append(podizraz)
            opazovaneSta.append([podizraz[0],podizraz[1]])
            if podizraz[0] in opazovaneSpr.keys():
                opazovaneSpr[podizraz[0]].add(len(izraz)-1)
            else:
                opazovaneSpr[podizraz[0]] = {len(izraz)-1}
            if podizraz[1] in opazovaneSpr.keys():
                opazovaneSpr[podizraz[1]].add(len(izraz)-1)
            else:
                opazovaneSpr[podizraz[1]] = {len(izraz)-1}
        else:
            raise UsageError("To se ne bi smelo zgoditi, saj smo vse enojce krajšali.")
        
    while ...:
        b = izberi(literali)#izbere literal, ki ima največjo vrednost po cca. chaff metodi
        if b >= len(spr):
            if vrednosti[b-len(spr)] and vrednosti[b-len(spr)][1] == 2:
                return False
            elif vrednosti[b-len(spr)]:
                vrednosti[b-len(spr)] = (False,2)
            else:
                vrednosti[b-len(spr)] = (False,1)
        else:
            if vrednosti[b] and vrednosti[b][1] == 2:
                return False
            elif vrednosti[b]:
                vrednosti[b] = (True,2)
            else:
                vrednosti[b] = (True,1)
        for i in opazovaneSpr.get(b,[]):
            #najde novo spremenljivko, ki jo opazujemo v i, če primerna obstaja.
            opazovaneSta[i].remove(b)
            pommo = True
            for j in izraz[i]:
                if vrednosti[j] and vrednosti[j][1]:
                    opazovaneSta[i].append(b)
                    if b in opazovaneSpr.keys():
                        opazovaneSpr[b].add(i)
                    else:
                        opazovaneSpr[b] = {i}
                    pommo = False
                    break
            if pommo:#Nismo našli nove spr, torej mora biti spr, ki je ostala true. Shranimo si tudi spr., ki je false, saj se bo pri backtrackingu spremenila na true
                #vemo, da mora biti zadnji literal true
                if vrednosti[opazovaneSta[i][0]] and vrednosti[opazovaneSta[i][0]][1] == 2 and vrednosti[opazovaneSta[i][0]][0] == False:
                    return False
                elif vrednosti[opazovaneSta[i][0]] and vrednosti[opazovaneSta[i][0]][0] == False:
                    vrednosti[opazovaneSta[i][0]] = (True,2)
                else:
                    pass#mogoče bom tu dodal kakšen assert.
                opazovaneSta[i].append(b)
                    
                
        
            


    return None


