from booli import *
from solver import *
from chaff import *
from re import sub
from util import primer

t = [[0,0,4,0],[0,2,0,3],[2,0,0,0],[0,4,0,1]]

def barvanje(g,k):
    """Ali lahko graf podan s slovarjem g pobarvamo s k barvami? """
    def sprem(v,b):
        return Spr("\""+str(v)+"\""+","+str(b))
    
    #vsako vozlišče vsaj ene barve
    f1 = In(*tuple(Ali(*tuple(sprem(v,b) for b in range(k))) for v in g))
    
    #vsako vozlišče z ne več kot eno barvo
    f2 = In(
        *tuple(
            In(
                *tuple(
                    Neg(In(sprem(v,b1),sprem(v,b2)))
                    for b1 in range(k-1)
                    for b2 in range(b1+1,k))
                )
            for v in g))
    
    #povezani vozlišči različnih barv
    f3 = In(
        *tuple(
            In(
                *tuple(
                    Neg(In(sprem(v1,b),sprem(v2,b)))
                    for b in range(k)
                    )
                )
            for v1 in g for v2 in g[v1]))

    formula = In(f1,f2,f3)

    return formula.poenostavi()



def povezanost(g):
    def sprem(u,v,n):
        return Spr("C{0}{1}{2}".format(u,v,n))

    n = len(g)

    #sosedi so povezani
    f1 = In(*tuple(sprem(u,v,1) if v in g[u] else Neg(sprem(u,v,1)) for u in g for v in g.keys()))

    #povezanost
    f3 = In(*tuple(Ali(*tuple(sprem(u,v,i) for i in range(1,n))) for u in g for v in g.keys()-{u}))

    # če u in v povezana in iz v do k v n korakih, potem iz u do k v n+1 korakih
    f2 = In(*tuple(Ali(Neg(sprem(v,k,i)),sprem(u,k,i+1)) for u in g for v in g[u] for k in g.keys()-{u,v} for i in range(1,n)))

    # če iz u do v v n korakih, potem iz nekega soseda od u do v v n-1 korakih
    f4 = In(
        *tuple(
            Ali(
                *tuple(
                    Ali(Neg(sprem(u,v,i)),sprem(k,v,i-1))
                        for k in g[u] for i in range(2,n)
                    )
                )

                for u in g for v in g.keys()-{u}

            )
        )

    print(In(f1,f2,f3,f4))
    return In(f1,f2,f3,f4).poenostavi()

    #???Zakaj ko kličem a = sudoku4(t);b = tchaff(b) se včasih sesuje, včasih ne...tchaff ne dela? In zakaj a.vstavi(b) že skoraj popolnoma poenostavi formulo??
def sudoku1(tabela1):#tale pa kao ni izpolnjiv za t(tudi tale mee errorje). lahko sicer, da sem se kaj zmotil
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("C({0},{1},{2})".format(u,v,n))

    spr = set()
    imena = [None]*n
    obrimena = {}
    st = 0
    tabela = [[j if j not in ["0","None"] else 0 for j in i] for i in tabela1]
    for i in range(n):
        for j in range(n):
            if tabela[i][j] not in [0, "0","None",None] and tabela[i][j] not in spr:
                imena[st] = tabela[i][j]
                obrimena[tabela[i][j]] = st
                st+=1
                spr.add(tabela[i][j])
    st = 0
    imena = [imena[i] if imena[i] else i for i in range(n)]

    #v vsaki vrstici je vsaka številka na vsaj enem polju
    f1 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #v vsakem stolpcu je vsaka številka na vsaj enem polju
    f2 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for i in range(n)))for j in range(n) for l in range(1,n+1)))

    #v vsakem kvadratku je vsaka številka na vsaj enem polju
    f3 = In(*tuple(Ali(*tuple(Sprem(k*(i//k)+j//k,k*(i%k)+j%k,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #če je na polju neko število, potem drugih števil ni
    f4 = In(*tuple(Ali(Neg(Sprem(i,j,imena[l-1])),Neg(Sprem(i,j,imena[z-1]))) for i in range(n) for j in range(n) for l in range(1,n+1) for z in (set(range(1,n+1))-{l})))

    #nastavimo začetne vrednosti
    f5 = In(*tuple(Sprem(i,j,tabela[i][j]) if tabela[i][j] not in [0, "0","None",None] else T() for i in range(n) for j in range(n)))

    return In(f1,f2,f3,f4,f5).poenostavi()


def sudoku4(tabela1):#tale sudoku pa vrne error na t (včasih. ko deletaš probane je bil key error in error, da i nima spremenljivk) in prav tako vrne valuacijo, ki ni true
    #boljša prevedba sudoku na sat
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("C({0},{1},{2})".format(u,v,n))

    spr = set()
    imena = [None]*n
    obrimena = {}
    st = 0
    tabela = [[j if j not in ["0","None"] else 0 for j in i] for i in tabela1]
    for i in range(n):
        for j in range(n):
            if tabela[i][j] not in [0, "0","None",None] and tabela[i][j] not in spr:
                imena[st] = tabela[i][j]
                obrimena[tabela[i][j]] = st
                st+=1
                spr.add(tabela[i][j])

    #v vsaki vrstici je vsaka številka na vsaj enem polju
    f1 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #v vsakem stolpcu je vsaka številka na vsaj enem polju
    f2 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for i in range(n)))for j in range(n) for l in range(1,n+1)))

    #v vsakem kvadratku je vsaka številka na vsaj enem polju
    f3 = In(*tuple(Ali(*tuple(Sprem(i//k+j//k,i%k+j%k,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #če je na polju neko število, potem drugih števil ni
    f4 = In(*tuple(Ali(Neg(Sprem(i,j,imena[l-1])),Neg(Sprem(i,j,imena[z-1]))) for i in range(n) for j in range(n) for l in range(1,n+1) for z in (set(range(1,n+1))-{l})))

    return In(f1,f2,f3,f4).poenostavi()

def sudoku3(tabela1):#naj ostane, da preverimo če tchaff dela
    #boljša prevedba sudoku na sat
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("C({0},{1},{2})".format(u,v,n))

    spr = set()
    imena = [None]*n
    obrimena = {}
    st = 0
    tabela = [[j if j not in ["0","None"] else 0 for j in i] for i in tabela1]
    for i in range(n):
        for j in range(n):
            if tabela[i][j] not in [0, "0","None",None] and tabela[i][j] not in spr:
                imena[st] = tabela[i][j]
                obrimena[tabela[i][j]] = st
                st+=1
                spr.add(tabela[i][j])

    #v vsaki vrstici je vsaka številka na vsaj enem polju
    f1 = In(*tuple(Ali(*tuple(Sprem(imena[i],imena[j],l) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #v vsakem stolpcu je vsaka številka na vsaj enem polju
    f2 = In(*tuple(Ali(*tuple(Sprem(imena[i],imena[j],l) for i in range(n)))for j in range(n) for l in range(1,n+1)))

    #v vsakem kvadratku je vsaka številka na vsaj enem polju
    f3 = In(*tuple(Ali(*tuple(Sprem(imena[i//k+j//k],imena[i%k+j%k],l) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #če je na polju neko število, potem drugih števil ni
    f4 = In(*tuple(Ali(Neg(Sprem(imena[i],imena[j],l)),Neg(Sprem(imena[i],imena[j],z))) for i in range(n) for j in range(n) for l in range(1,n+1) for z in (set(range(1,n+1))-{l})))

    return In(f1,f2,f3,f4).poenostavi()

##a = tchaff(sudoku1(t))
##c = [a if i else "0" for (a,i) in a.items()]
##d= [[None]*4 for i in range(4)]
##for i in range(4):
##    for j in range(4):
##        for k in range(1,5):
##            if "C({0},{1},{2})".format(i,j,k) in c:
##                d[i][j]=k
    

def sudoku2(tabela1):
    #v poenostavljeni obliki je formula majhna, vendar je v cnf ogromna.
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("C,{0},{1},{2}".format(u,v,n))

    spr = set()
    imena = [None]*n
    obrimena = {}
    st = 0
    tabela = [[j if j not in ["0","None"] else 0 for j in i] for i in tabela1]
    for i in range(n):
        for j in range(n):
            if tabela[i][j] not in [0, "0","None",None] and tabela[i][j] not in spr:
                imena[st] = tabela[i][j]
                obrimena[tabela[i][j]] = st
                st+=1
                spr.add(tabela[i][j])

    f = [0]*(3*n)
    for i in range(n):
        #vrstice. nobena dva nimata enake vrednosti
        f[i] = In(*tuple(Ali(*tuple(In(Sprem(i,j,l),*tuple(Neg(Sprem(i,z,l))if z!=j else T() for z in range(n))) for l in range(1,n+1))) for j in range(n)))

        #stoplci
        f[i+n] = In(*tuple(Ali(*tuple(In(Sprem(j,i,l),*tuple(Neg(Sprem(z,i,l))if z!=j else T() for z in range(n))) for l in range(1,n+1))) for j in range(n)))

        #kvadratki
        a = i//k
        b = i%k
        f[i+2*n] = In(*tuple(Ali(*tuple(In(Sprem(a+j//k,b+j%k,l),*tuple(Neg(Sprem(a+z//k,b+z%k,l))if z!=j else T() for z in range(n))) for l in range(1,n+1))) for j in range(n)))
            
    return In(*tuple(i for i in f)).poenostavi()

def sudoku(tabela1):
    """ Prevede sudoku na sat preko barvanja grafa. """
    n = len(tabela1)
    k = int(n**0.5)
    #Preslikamo podane spremenljivke sudokuja v [n].
    spr = set()
    imena = [None]*n
    obrimena = {}
    st = 0
    tabela = [[j if j not in ["0","None", None] else 0 for j in i] for i in tabela1]
    for i in range(n):
        for j in range(n):
            if tabela[i][j] not in [0, "0","None",None] and tabela[i][j] not in spr:
                imena[st] = tabela[i][j]
                obrimena[tabela[i][j]] = st
                st+=1
                spr.add(tabela[i][j])
    
                
    g = {(i,j):set()  for i in range(n) for j in range(n)}
    for i in range(n):
        for j in range(n):
            for x in range(n):
                if x != j: g[(i,j)].add((i,x))
                if x != i: g[(i,j)].add((x,j))
                if (k*(i//k) + x//k, k*(j//k)+x%k)!=(i,j): g[(i,j)].add((k*(i//k) + x//k, k*(j//k)+x%k))

    #barve so 1,...,n

    for i in range(1,n+1):
        g[i]=set()
        for j in range(1,n+1):
            if i!=j: g[i].add(j)

    for i in range(n):
        for j in range(n):
            if tabela[i][j] not in [0, "0","None", None]:
                for x in range(1,n+1):
                    if x != obrimena[tabela[i][j]]+1:
                        g[(i,j)].add(x)
                        g[x].add((i,j))
    
    #for i in g: print(i,g[i])

    #zamenjamo nazaj imena spremenljivk, namesto številk
    g = eval(sub(r"([^\(]+?)([0-9]+)([^\)]+?)",r"\1imena[\2-1]\3",str(g)))
    return barvanje(g,n)

#a = [["Bla",None,None,None],["Kor",None,None,None],["AS",None,None,None],["MA",None,None,None]]

g = {"a":{"b","c","d"},"b":{"a"},"c":{"a"},"d":{"a"}}






