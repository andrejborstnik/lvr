from booli import *
from util import *
from chaff import chaff
from prevedbe import *
from bf_dpll import DPLL, bfSAT
from resitelj import resitelj
from time import clock

def test(n, file, printaj=False, sat = True):
    #test na sat problemih v datotekah file-0ŠT.cnf,
    #kjer gre št. po vseh številih vzorva n.
    #Primer: 1-3,6 so števila 1,2,3,6
    #Primer: 2-10,4-12 so števila 2,3,4,5,6,7,8,9,10,11,12
    t=0
    n = n.split(",")
    st=set()
    for i in n:
        if "-" in i:
            j = i.split("-")
            j1=int(j[0])
            j2=int(j[1])
            for k in range(j1,j2+1):
                st.add(k)
        elif i != "":
            st.add(int(i))
    for i in st:
        a = preberi("{0}-0{1}.cnf".format(file,i)).poenostavi(chff=True)
        t1=clock()

        #reševanje -> tu lahko spremeniš algoritem
        b = resitelj(a)
        
        t2=clock()
        if sat:
            if a.vstavi(b).poenostavi()!=T():
                print("NE DELAM PRAV!")
        else:
            if a!="Problem ni izpolnjiv":
                print("NE DELAM PRAV!")
        t+=t2-t1
        if printaj: print("Porabljen čas za {0}. problem:  {1}".format(i,t2-t1))
    return t

#rez = test("1-1000","./primeri_50/uf50")
rez = test("1-1000","./primeri_100/uf100")
#rez = test("1-100","./primeri_150/uf150",True)
#rez = test("2,4,12,19,21,24,25","./primeri_250/uf250",True)
print("\nSkupni čas:  {0}".format(rez))
    
def test1(k,velikost = 70):
    t1=0
    t2=0
    for i in range(k):
        a = primer(n = velikost).poenostavi(True)
        print("Velikost:  {0}".format(len(a.spremenljivke())))

        #primerja algoritme. Poljubo preuredi. Ne preverja pravilnosti.
        t1a = clock()
        b = DPLL(a,True)
        t1b=clock()
        c = resitelj(a,True)
        t2b=clock()
        t1+=t1b-t1a
        t2+=t2b-t1b
        
    print("Časa: {0}, {1}".format(t1,t2))
    return None
