from booli import *

########## Standardni cnf format ###############

def zapisi(formula,file):
    f = open(file, "w")
    formula = formula.poenostavi(chff=True)
    sp = formula.spremenljivke()
    spr={}
    obr = []
    k = 1
    f.write("p cnf {0} {1}\n".format(len(sp),len(formula.sez)))
    for i in sp:
        spr[i]=k
        obr.append(i)
        k+=1
    for i in formula.sez:
        s=""
        if type(i)==Ali:
            for j in i.sez:
                if type(j)==Neg:
                    s+="-{0} ".format(spr[j.izr.ime])
                elif type(j)==Spr:
                    s+="{0} ".format(spr[j.ime])
            s+="0\n"
            f.write(s)
        elif type(i) in [Spr, Neg]:
            if type(i)==Neg:
                s+="-{0} ".format(spr[i.izr.ime])
            else:
                s+="{0} ".format(spr[i.ime])
            s+="0\n"
            f.write(s)
        else:
            print(i)
    f.close()
    return None
    return obr

def preberi(file):
    f = open(file,"r",encoding="utf-8")
    stavki = set()
    fil = str(f.read())
    lines=fil.split("\n")
    i = 1
    x=len(lines)
    nasel = False
    while i < x:
        if lines[i] not in ["","%","0"] and lines[i][0]!="c":
            pomo=[]
            for z in lines[i].split(" "):
                if z:
                    pomo.append(z)
            lines[i]=pomo
            if not nasel:
                prva = lines[i]
                st_spr = int(prva[2])
                st_sta=int(prva[3])
                nasel=True
            else:
                stavki.add(Ali(*tuple(Spr(k) if k[0]!="-" else Neg(Spr(k[1:])) for k in lines[i][:-1])))
        i+=1
        
    f.close()
    return In(*tuple(stavki))

########## Nastavljiva errorja ################

class UsageError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class InternalError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

#########################################

def cista(formula,i):
    #dobi spremenljivko i pove ali v formuli nastopa čisto
    form = repr(formula.poenostavi())
    if ("¬"+i) in form:
        if (" "+i) in form or ("("+i) in form or form[0:len(i)]==i: #Če sta notri hkrati i in negacija i, potem ni čista. Sicer je.
            return False
        return True,False #še false, da vemo, da nastopa i samo z negacijo. To bo vrednost spr i.
    return True,True

########## Kopica #################

class Kopica:
    #Popravi, ker je Pretnarjeva kopica slaba.
    def __init__(self):
        self.sez = []

    def dvigni(self, i):
        j = (i - 1) // 2
        if j >= 0 and self.sez[i] < self.sez[j]:
            self.sez[i], self.sez[j] = self.sez[j], self.sez[i]
            self.dvigni(j)

    def spusti(self, i):
        j = 2 * i + 1
        if len(self.sez) <= j:
            pass
        elif len(self.sez) == j + 1 and self.sez[i] > self.sez[j]:
            self.sez[i], self.sez[j] = self.sez[j], self.sez[i]
        elif len(self.sez) > j + 1 and (self.sez[i] > self.sez[j] or self.sez[i] > self.sez[j + 1]):
            j += 1 if self.sez[j + 1] < self.sez[j] else 0
            self.sez[i], self.sez[j] = self.sez[j], self.sez[i]
            self.spusti(j)

    def dodaj(self, x):
        self.sez.append(x)
        self.dvigni(len(self.sez) - 1)

    def odstrani(self):
        if self.sez:
            najmanjsi = self.sez[0]
            self.sez[0] = self.sez[len(self.sez) - 1]
            del self.sez[len(self.sez) - 1]
            self.spusti(0)
            return najmanjsi
        raise InternalError("Ne moramo odstraniti elementa prazne kopice.")

    def prazna(self):
        return len(self.sez) == 0



########### Sklad #############
    
class Sklad():
    
    def __init__(self,n = 0):
        self.sklad = [0]*n
        self.head = -1

    def dodaj(self,x):
        self.head += 1
        if len(self.sklad) > self.head:
            self.sklad[self.head] = x
        else:
            self.sklad.append(x)

    def odstrani(self):
        if self.prazen():
            raise InternalError("Ne moramo odstraniti elementov iz praznega sklada.")
        self.head -= 1
        return self.sklad[self.head+1]

    def prazen(self):
        if self.head < 0:
            return True
        return False



##################### NAKLJUČNI TESTNI PRIMERI #######################################################################

from random import random
from re import sub
def primer(b = True, n = False):
    #Maximalna velikost primera je 1000.
    moznosti = ["In","Ali","Spr","Spr"]
    moznosti1 = ["In","Ali"]
    i=0
    globina = 1
    cc = int(random()*len(moznosti1))
    c = moznosti1[cc]
    formula = c+"("
    if not n:
        n = int(random()*1000)
    for i in range(n):
        aa = int(random()*len(moznosti))
        a= moznosti[aa]
        if globina > 1 and random()< 1/2:
            #pade vn iz sedanjega in-a/ali-ja oz. not-a, če se da
            if a == "Spr":
                i+=1
                globina-=1
                if formula[-1] == ",":
                    formula = formula[:-1]
                if random()<1/2:
                    formula+="),"+a+"( \'x"+str(i)+"\' ),"
                else:
                    formula+="),"+"Neg("+a+"(\'x"+str(i)+"\')),"
            else:
                if formula[-1] == ",":
                    formula = formula[:-1]
                formula+="),"+a+"("
        else:
            if a!= "Spr":
                globina+=1
                formula+= a+"("
            else:
                i+=1
                if random()<1/2:
                    formula+= a+"(\'x"+str(i)+"\'),"
                else:
                    formula+= "Neg("+a+"(\'x"+str(i)+"\')),"
    if formula[-1] == ",":
        formula=formula[:-1]
    formula+=")"
    while globina>1:
        globina-=1
        formula+=")"
    formula = sub(r"In\(\),*",r"",formula)
    formula = sub(r"Ali\(\),*",r"",formula)
    return eval(formula)
