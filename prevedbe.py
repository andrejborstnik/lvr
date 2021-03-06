from booli import *
from re import sub
from util import primer


def prazna(n):
    """Naredi prazno tabelo nxn."""
    return [[0]*n for i in range(n)]

def barvanje(g,k):
    """Prevede problem barvanja grafa g s k barvami na SAT."""
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

    return formula.poenostavi(cnf=True)



def povezanost(g):
    """Prevede problem povezanosti grafa na SAT."""
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

def latinski1(tabela1):
    """Prevede izpolnjevanje latinskega kvadrata na SAT."""
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("{0},{1},{2}".format(u,v,n))

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
    imena = [imena[i-1] if imena[i-1] else i for i in range(1,n+1)]

    #v vsakem polju vsaj ena številka
    f1 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for l in range(1,n+1)))for i in range(n) for j in range(n)))

    #če je v vrstici na nekem polju št., je na drugih ni
    f2 = In(*tuple(Ali(Neg(Sprem(i,z,imena[l-1])),Neg(Sprem(i,j,imena[l-1]))) for l in range(1,n+1) for i in range(n)for z in range(n) for j in range(z+1,n)))

    #če je v stoplcu na nekem polju št., je na drugih ni
    f3 = In(*tuple(Ali(Neg(Sprem(z,i,imena[l-1])),Neg(Sprem(j,i,imena[l-1]))) for l in range(1,n+1) for i in range(n)for z in range(n) for j in range(z+1,n)))

    #nastavimo začetne vrednosti
    f4 = In(*tuple(Sprem(i,j,tabela[i][j]) if tabela[i][j] not in [0, "0","None",None] else T() for i in range(n) for j in range(n)))

    return In(*tuple(i for i in f1.sez | f2.sez | f3.sez | f4.sez)).poenostavi(chff=True)

def latinski(tabela1):
    """Prevede izpolnjevanje latinskega kvadrata na SAT."""
    n = len(tabela1)
    def Sprem(u,v,n):
        return Spr("({0},{1},{2})".format(u,v,n))

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
    imena = [imena[i-1] if imena[i-1] else i for i in range(1,n+1)]

    #v vsakem polju vsaj ena številka
    f1 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for l in range(1,n+1)))for i in range(n) for j in range(n)))

    #v vsaki vrstici je vsaka številka na vsaj enem polju
    f2 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #v vsakem stolpcu je vsaka številka na vsaj enem polju
    f3 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for i in range(n)))for j in range(n) for l in range(1,n+1)))

    #če je na polju neko število, potem drugih števil ni
    f4 = In(*tuple(Ali(Neg(Sprem(i,j,imena[l-1])),Neg(Sprem(i,j,imena[z-1]))) for i in range(n) for j in range(n) for l in range(1,n+1) for z in (set(range(1,n+1))-{l})))

    #nastavimo začetne vrednosti
    f5 = In(*tuple(Sprem(i,j,tabela[i][j]) if tabela[i][j] not in [0, "0","None",None] else T() for i in range(n) for j in range(n)))

    return In(*tuple(i for i in f1.sez | f2.sez | f3.sez | f4.sez | f5.sez))

def sudoku(tabela1):
    """Prevede reševanje sudokuja na SAT."""
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("{0},{1},{2}".format(u,v,n))

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
    imena = [imena[i-1] if imena[i-1] else i for i in range(1,n+1)]

    #v vsakem polju vsaj ena številka
    f1 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for l in range(1,n+1)))for i in range(n) for j in range(n)))

    #če je v vrstici na nekem polju št., je na drugih ni
    f2 = In(*tuple(Ali(Neg(Sprem(i,z,imena[l-1])),Neg(Sprem(i,j,imena[l-1]))) for l in range(1,n+1) for i in range(n)for z in range(n) for j in range(z+1,n)))

    #če je v stoplcu na nekem polju št., je na drugih ni
    f3 = In(*tuple(Ali(Neg(Sprem(z,i,imena[l-1])),Neg(Sprem(j,i,imena[l-1]))) for l in range(1,n+1) for i in range(n)for z in range(n) for j in range(z+1,n)))

    #če je v kvadratku na nekem polju št., je na drugih ni
    f4 = In(*tuple(Ali(Neg(Sprem(k*(i//k)+z//k,k*(i%k)+z%k,imena[l-1])),Neg(Sprem(k*(i//k)+j//k,k*(i%k)+j%k,imena[l-1]))) for l in range(1,n+1) for i in range(n)for z in range(n) for j in range(z+1,n)))

    #nastavimo začetne vrednosti
    f5 = In(*tuple(Sprem(i,j,tabela[i][j]) if tabela[i][j] not in [0, "0","None",None] else T() for i in range(n) for j in range(n)))

    return In(*tuple(i for i in f1.sez | f2.sez | f3.sez | f4.sez | f5.sez)).poenostavi(chff=True)

def sudoku1(tabela1):
    """Prevede reševanje sudokuja na SAT."""
    n = len(tabela1)
    k = int(n**0.5)
    def Sprem(u,v,n):
        return Spr("{0},{1},{2}".format(u,v,n))

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
    imena = [imena[i-1] if imena[i-1] else i for i in range(1,n+1)]

    #v vsakem polju vsaj ena številka
    f1 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for l in range(1,n+1)))for i in range(n) for j in range(n)))

    #v vsaki vrstici je vsaka številka na vsaj enem polju
    f2 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #v vsakem stolpcu je vsaka številka na vsaj enem polju
    f3 = In(*tuple(Ali(*tuple(Sprem(i,j,imena[l-1]) for i in range(n)))for j in range(n) for l in range(1,n+1)))

    #v vsakem kvadratku je vsaka številka na vsaj enem polju
    f4 = In(*tuple(Ali(*tuple(Sprem(k*(i//k)+j//k,k*(i%k)+j%k,imena[l-1]) for j in range(n)))for i in range(n) for l in range(1,n+1)))

    #če je na polju neko število, potem drugih števil ni
    f5 = In(*tuple(Ali(Neg(Sprem(i,j,imena[l-1])),Neg(Sprem(i,j,imena[z-1]))) for i in range(n) for j in range(n) for l in range(1,n+1) for z in (set(range(1,n+1))-{l})))

    #nastavimo začetne vrednosti
    f6 = In(*tuple(Sprem(i,j,tabela[i][j]) if tabela[i][j] not in [0, "0","None",None] else T() for i in range(n) for j in range(n)))

    return In(*tuple(i for i in f1.sez | f2.sez | f3.sez | f4.sez | f5.sez | f6.sez)).poenostavi(chff=True)

def sudoku2(tabela1):
    """ Prevede sudoku na SAT preko barvanja grafa. Prevedba je lahko počasna."""
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

g = {"a":{"b","c","d"},"b":{"a","c"},"c":{"a","b"},"d":{"a"}}

prim1 = In(Ali(Spr("x"),Spr("z")),Ali(Spr("x"),Spr("u")),Ali(Spr("x"),Spr("v")),Ali(Neg(Spr("x")),Neg(Spr("y"))),Ali(Neg(Spr("x")),Spr("y")))

t1 = [[0,0,4,0],[0,2,0,3],[2,0,0,0],[0,4,0,1]]
t2 = [[0,0,0,0],[0,2,0,3],[2,0,0,0],[0,0,0,1]]

lahek = [[0,0,6,0,7,4,0,8,2],
         [0,0,9,0,0,5,0,0,3],
         [0,2,0,3,6,0,9,0,5],
         [0,6,0,5,3,2,0,0,0],
         [0,0,0,1,0,9,0,0,0],
         [0,0,0,7,8,6,0,2,0],
         [7,0,5,0,9,3,0,6,0],
         [6,0,0,8,0,0,3,0,0],
         [1,9,0,6,2,0,8,0,0]]

sreden = [[0,1,0,5,0,0,0,6,0],
           [0,6,0,0,7,1,0,0,2],
           [5,0,7,8,0,0,0,0,9],
           [0,0,0,0,0,0,0,9,4],
           [3,0,1,0,0,0,2,0,6],
           [7,9,0,0,0,0,0,0,0],
           [6,0,0,0,0,5,4,0,3],
           [2,0,0,7,6,0,0,5,0],
           [0,3,0,0,0,4,0,7,0]]

zloben = [[7,0,0,0,3,0,0,8,0],
          [0,4,3,0,2,0,0,0,0],
          [0,0,0,0,6,4,0,9,0],
          [0,0,1,0,0,7,0,0,0],
          [8,6,0,0,0,0,0,2,4],
          [0,0,0,2,0,0,9,0,0],
          [0,9,0,5,1,0,0,0,0],
          [0,0,0,0,8,0,2,3,0],
          [0,5,0,0,7,0,0,0,9]]





