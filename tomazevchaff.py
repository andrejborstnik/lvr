from util import *
from booli import *
from time import *
from random import *


def chaff(formula):

  
    
    form = formula.poenostavi(cnf=True)

    vrednost = {i:None for i in form.spremenljivke()}

    if type(form)==T: return vrednost
    elif type(form)==F: return "Formula ni izpolnljiva"

    #Najprej določimo vrednost enojcem
    nove = True
    while nove:
        nove = {}
        for stavek in form:
            if type(i) == Spr:
                nove[i.ime]=True
                vrednost[i.ime]=True
            elif type(i) == Neg:
                nove[i.ime]=False
                vrednost[i.ime]=False
                
        form = form.vstavi(nove).poenostavi(cnf=True)

        if type(form)==T: return vrednost
        elif type(form)==F: return "Formula ni izpolnljiva"

    
    #Ostali so nam le Ali-ji dolžine 2 in več
    #definiramo nekaj stvari:
    določena = {i:0 for i in form.spremenljivke()}
    kontrolne = {}
    kontrolniOd = {}
    stavkiOd = {}
    izpolnjen = {}
    odločitve = []

    #izberemo kontrolne literale
    for stavek in form:
        temp = iter(stavek.sez)
        a = next(temp)
        b = next(temp)
        kontrolne[stavek]=[a,b]
        kontrolniOd[a]=stavek
        kontrolniOd[b]=stavek

    #pogledamo v katerih stavkih se pojavijo kontrolni literali
    kontr = [i for j in kontrolne.values() for i in j]
    ostaliOd = {lit:[] for lit in kontr}
    for stavek in form:
        izpolnjen[stavek]=False
        for lit in stavek.sez:
            if lit in kontrolne:
                ostaliOd[lit].append(stavek)
    
            


    #sestopanje
    while True:
        a = izberi()
        if not a:
            return "Formula ni izpolnljiva"
        elif type(a)==Spr:
            spr = a.ime
            vrednost[spr]=True
        else:
            spr = a.izr.ime
            vrednost[spr]=False

        določena[spr]=1
        odločitve.append(spr)
        sklepi={}
        nove = [spr]
        while True:
            
            
    def sklepaj():
        """Po ugibanju tranzitivno naredi sklepe, ki iz njega sledijo"""
        temp = []
        for spr in nove:
            x = 0
            if Spr(spr) in kontr:
                x = Spr(spr)
            elif Neg(Spr(spr)) in kontr:
                x = Neg(Spr(spr))
            if x:
                

























        
        
    
