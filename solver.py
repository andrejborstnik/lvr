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

def Chaff(formula,cas = False):
    t1 = clock()
    res = pChaff(formula)
    if cas:
        print("Čas:  {0}".format(clock()-t1))
    print("Rešitev:   \n{0}".format(res))
    return res

def pChaff(formula):
    
    def slovar(vrednosti,kazalci):
        pomo = {}
        for i in range(n):
            if vrednosti[i]:
                pomo[kazalci[i]] = vrednosti[i][0]
            else:
                pass#Tu lahko nastavimo na True/False če želimo
        return pomo
    def izberi(literali):
        a = -1
        j = -1
        print(vrednosti)
        for i in range(len(literali)):
            if not vrednosti[i] and  literali[i] > a:
                a = literali[i]
                j = i
        if j==-1 and not vrednosti[0]:
            j = 0
        elif j == -1:
            raise UsageError("Vse spremenljivke imajo vrednosti, zato ni česa za izbrati.")
        return j
    def izpolnjen():
        #gleda samo opazovane spr.
        #print(vrednosti)
        #print(opazovaneSta)
        print(len(opazovaneSta),sum([(vrednosti[i[0]] in [(True,1),(True,2)] or vrednosti[i[1]] in [(True,1),(True,2)])  for i in opazovaneSta]))
        return len(opazovaneSta) == sum([(vrednosti[i[0]] in [(True,1),(True,2)] or vrednosti[i[1]] in [(True,1),(True,2)])  for i in opazovaneSta])
    formula = formula.poenostavi(True)
    spr = formula.spremenljivke()
    n = len(spr)
    kazalci = [0] * n#preslikava fi : [n] -> Imena spremelnjivk
    obratnikazalci = {}#Inverz fi.
    opazovaneSpr={}#Slovar, ki za spr. pove v katerih stavkih je opazovana.
    sprStavki = {}#Slovar, ki za spr. pove v katerih stavkih je vsebovana.
    k=0
    for i in spr:
        kazalci[k] = i
        obratnikazalci[i] = k
        opazovaneSpr[k] = set()
        opazovaneSpr[k+n] = set()
        k += 1
    vrednosti = [None] * (2*n)
    literali = [0] * (2*n)
    koraki = Sklad()

    if type(formula)==T:
        return slovar(vrednosti,kazalci)
    elif type(formula)==F:
        return False
    elif type(formula) == Spr:
        vrednosti[obratnikazalci[formula.ime]] = (True,2)
        return slovar(vrednosti,kazalci)
    elif type(formula) == Neg:
        vrednosti[obratnikazalci[formula.izr.ime]] = (False,2)
        return slovar(vrednosti,kazalci)
    
    #dokler imamo enojce jih krajšamo.
    novevrednosti = {0:1}
    while novevrednosti:
        novevrednosti = {}
        odstrani = set()
        for i in formula.sez:
            #In(Ali(Spr("x"))) je že poenostavljen v In(Spr("x")), In(Ali()) pa v False, tako da smo pokrili vse primere.
            if type(i) == Spr:
                novevrednosti[i.ime] = True
                vrednosti[obratnikazalci[i.ime]] = (True,2)
                odstrani.add(i)
            elif type(i) == Neg:#Negacija ima notri samo eno spr, saj smo že poenostavili.
                odstrani.add(i)
                novevrednosti[i.izr.ime] = False
                vrednosti[obratnikazalci[i.izr.ime]] = (False,2)
        for i in odstrani:
            formula.sez.remove(i)
        formula = formula.vstavi(novevrednosti).poenostavi(True)
        if type(formula)==T:
            return slovar(vrednosti,kazalci)
        elif type(formula)==F:
            return False
        elif type(formula) == Spr:
            vrednosti[obratnikazalci[formula.ime]] = (True,2)
            return slovar(vrednosti,kazalci)
        elif type(formula) == Neg:
            vrednosti[obratnikazalci[formula.izr.ime]] = (False,2)
            return slovar(vrednosti,kazalci)
    
    izraz = []#Formulo spremenimo v seznam seznamov, ker bo tako lažje izvajati algoritem.
    opazovaneSta = [] #Seznam, ki za stavke pove kateri spremenljivki(literala) sta v njem opazovani. Vedno vsebuje dve, tudi ko je (največ) ena od njiju false(literal). Ta se namreč pri backtrackingu spremeni v true oz. nedoločeno.
    for i in formula.sez:
        podizraz = []
        if len(i.sez)>1:
            for j in i.sez:
                if type(j) == Spr:
                    podizraz.append(obratnikazalci[j.ime])
                    if obratnikazalci[j.ime] in sprStavki.keys():
                        sprStavki[obratnikazalci[j.ime]].add(len(izraz)-1)
                    else:
                        sprStavki[obratnikazalci[j.ime]]={len(izraz)-1}
                elif type(j) == Neg:
                    podizraz.append(obratnikazalci[j.izr.ime] + n)
                    if (obratnikazalci[j.izr.ime]+n) in sprStavki.keys():
                        sprStavki[obratnikazalci[j.izr.ime]+n].add(len(izraz)-1)
                    else:
                        sprStavki[obratnikazalci[j.izr.ime]+n]={len(izraz)-1}
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

    def backtrack():
        if koraki.prazen():
            print("ni več korakov")
            return False
        pomo = koraki.odstrani()
        while pomo[0] == "i":
            vrednosti[pomo[1]] = None
            vrednosti[pomo[1]+n*(-1)**(pomo[1]>=n)] = None
            pomo = koraki.odstrani()
        if vrednosti[pomo[1]][1] == 2:
            if not backtrack():
                return False
        else:
            vrednosti[pomo[1]] = (not vrednosti[pomo[1]][0],2)
            vrednosti[pomo[1]+n*(-1)**(pomo[1]>=n)] = (vrednosti[pomo[1]][0],2)
            return pomoChaff(pomo[1])
        return True

    def pomoChaff(b):
        if vrednosti[b] and not vrednosti[b][0]:#izberemo tiste stavke, kjer je literal false (in opazovan)
            b = b + n*(-1)**(b>=n)
        for i in opazovaneSpr.get(b,[]):
            #najde nov literal, ki ga opazujemo v i, če primeren obstaja.
            opazovaneSta[i].remove(b)
            pommo = True
            for j in izraz[i]:
                literali[j]+=1
                if j != b and (not vrednosti[j] or vrednosti[j][0]):
                    opazovaneSta[i].append(j)
                    if j in opazovaneSpr.keys():
                        opazovaneSpr[j].add(i)
                    else:
                        opazovaneSpr[j] = {i}
                    pommo = False
                    break
            if pommo:#Nismo našli nove spr, torej mora biti spr, ki je ostala true. Shranimo si tudi spr., ki je false, saj se bo pri backtrackingu spremenila na true oz. nedefinirano
                #vemo, da mora biti zadnji literal true
                if vrednosti[opazovaneSta[i][0]]  and vrednosti[opazovaneSta[i][0]][0] == False:
                    if not backtrack():
                        return False
                else:
                    vrednosti[opazovaneSta[i][0]] = (True,2)
                    vrednosti[opazovaneSta[i][0]+n*(-1)**(opazovaneSta[i][0]>=n)] = (False,2)
                    koraki.dodaj(("i",opazovaneSta[i][0]))#"i" pomeni, da je spremenljivka implicirana, tj. sledi iz prejšnjih odločitev.
                    pomoChaff(opazovaneSta[i][0])
                opazovaneSta[i].append(b)
                print("tutu")
        return True
    
    pommmo = True
    stevec = 0
    while ((not koraki.prazen()) or pommmo) and not izpolnjen():# and type(formula.vstavi(slovar(vrednosti,kazalci)).poenostavi())!=T:#pommmo je zato, da se prvič zanka izvede, potem pa se ne preverja dokler ne pridemo do zadnje iteracije zanke.
        #Če imajo vse spr. vrednost, ko začnemo novo iteracijo je formula izpolnjiva z izračunano valuacijo.
        stevec += 1
        pommmo = False
        if stevec % (10 * n) == 0: #vsake toliko časa delimo s konstanto
            literali = [i/2 for i in literali]#??? Daj v kopico?
        b = izberi(literali)#izbere literal, ki ima največjo vrednost po cca. chaff metodi
        vrednosti[b] = (True,1)
        vrednosti[b+n*(-1)**(b>=n)] = (False,2)
        koraki.dodaj(("d",b))
        print(opazovaneSta)
        if not pomoChaff(b):
            return False
                    
    if koraki.prazen() and type(formula.vstavi(slovar(vrednosti,kazalci)).poenostavi())!=T:
        return False
    
    return slovar(vrednosti,kazalci)
        
        



#a = primer(n = 70)
#DPLL(a,True)
#Chaff(a,True)
















