from booli import *
from util import *
from bf_dpll import DPLL
from resitelj import resitelj
from time import clock

def test(n, file, printaj=False, sat = True):
    #test na sat problemih v datotekah file-0ŠT.cnf od 1 do n
    t=0
    for i in range(1,n+1):
        a = preberi("{0}-0{1}.cnf".format(file,i)).poenostavi(chff=True)
        t1=clock()
        b = resitelj(a)
        t2=clock()
        if sat:
            if a.vstavi(b).poenostavi()!=T():
                print("NE DELAM PRAV!")
        else:
            if a!="Problem ni izpolnjiv":
                print("NE DELAM PRAV!")
        t+=t2-t1
        if printaj: print("Porabljen čas:  {0}".format(t2-t1))
    return t

rez = test(1000,"./primeri_50/uf50")
    
def test1(k,velikost = 70):
    t1=0
    t2=0
    for i in range(k):
        a = primer(n = velikost).poenostavi(True)
        print("Velikost:  {0}".format(len(a.spremenljivke())))
        t1a = clock()
        b = DPLL(a,True)
        t1b=clock()
        c = resitelj(a,True)
        t2b=clock()
        t1+=t1b-t1a
        t2+=t2b-t1b
        if b:
            d = a.vstavi(b).poenostavi()
        else:
            d = a.poenostavi()
        if c:
            if type(c)!= str:
                e = a.vstavi(c).poenostavi()
            else:
                e = F()
        else:
            e = a.poenostavi()
        
        if d != e:
            print("NE DELAM PRAV!", d, e)
            print("Časa: {0}, {1}".format(t1,t2))
            print(a)
            break
    print("Časa: {0}, {1}".format(t1,t2))
    return None
