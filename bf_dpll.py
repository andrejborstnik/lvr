from util import *
from booli import *
from re import findall

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
    #print("Rešitev: \n{0}".format(a))
    return a

def DPLLpomo(formula,vrednosti = {}):
    #formula mora biti v cnf obliki. Če ni, jo v to spremenimo
    #vrne valucaijo, če ta obstaja in False sicer (pozor!!! valuacija je lahko prazen slovar!)

    formula = formula.poenostavi(chff=True)

    def aSmoKonc(formula,vrednosti):
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
        return None
    kon = aSmoKonc(formula,vrednosti)
    if kon!=None: return kon

   
    def pucaj1(formula,vrednosti):
        #za spremenljivke, ki nastopajo samostojno vemo kaj morajo biti, zato jih kar določimo in pokrajšamo formulo
        novevrednosti = {0:1}
        k = -1
        while novevrednosti:
            k+=1
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
            formula = formula.vstavi(novevrednosti).poenostavi(chff=True)
            kon = aSmoKonc(formula,vrednosti)
            if kon!=None: return kon,"",""
        return k,formula,vrednosti

    def pucaj2(formula,vrednosti):
        #Stavke s čistimi spremenljivkami lahko pobrišemo. Čiste spremenljivke dobijo ustrezno vrednost. glede na to ali nastopajo z negacijo oz. brez.
        spr = formula.spremenljivke()
        cis = set()
        for i in spr:
            pomo = cista(formula,i)
            if pomo:
                cis.add(i)
                vrednosti[i] = pomo[1]
                odstrani=[]
                for k in formula.sez:
                    if i in repr(k):
                        odstrani.append(k)
                for k in odstrani:
                    formula.sez.remove(k)
                formula = formula.poenostavi(chff=True)
                kon = aSmoKonc(formula,vrednosti)
                if kon!=None: return kon,"",""
        return len(cis),formula,vrednosti

    pu1 = 1
    pu2 = 1
    while pu1 or pu2:
        pu1,formula,vrednosti=pucaj1(formula,vrednosti)
        if type(pu1) == dict or type(pu1)==bool: return pu1
        pu2,formula,vrednosti=pucaj2(formula,vrednosti)
        if type(pu2) == dict or type(pu2)==bool: return pu2

    spr = formula.spremenljivke()
    #Izberemo si neko spremenljivko in poizkusimo obe možnosti
    s = str(formula)
    b = max(spr,key = lambda x: len(findall(x,s)))

    formula1 = formula.vstavi({b:True}).poenostavi(chff=True)
    vrednosti[b] = True
    pomo = DPLLpomo(formula1, vrednosti)
    if pomo!=False:
        return pomo
    
    formula1 = formula.vstavi({b:False}).poenostavi(chff=True)
    vrednosti[b] = False
    pomo = DPLLpomo(formula1, vrednosti)
    return pomo



