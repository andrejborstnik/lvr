from booli import *
from solver import *
from tomazevchaff import *
from re import sub 

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

def sudoku(tabela1):
    n = len(tabela1)
    k = int(n**0.5)
    #Preslikamo podane spremenljivke sudokuja v [n].
    spr = set()
    imena = [None]*n
    obrimena = {}
    st = 0
    tabela = tabela1.copy()
    for i in range(n):
        for j in range(n):
            if tabela1[i][j] and tabela1[i][j] not in spr:
                imena[st] = tabela1[i][j]
                obrimena[tabela1[i][j]] = st
                st+=1
                spr.add(tabela1[i][j])
                tabela[i][j] = st
                
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
            if tabela[i][j]:
                for x in range(1,n+1):
                    if x != tabela[i][j]:
                        g[(i,j)].add(x)
                        g[x].add((i,j))
    
    #for i in g: print(i,g[i])

    #zamenjamo nazaj imena spremenljivk, namesto številk
    g = eval(sub(r"([^\(]+?)([0-9]+)([^\)]+?)",r"\1imena[\2-1]\3",str(g)))
    return barvanje(g,n),n



###a = sudoku([["Bla",None,None,None],["Kor",None,None,None],["AS",None,None,None],["MA",None,None,None]])
##a = sudoku([["Bla"]])
##n = a[1]
##b = DPLL(a[0])
##rešitev = [[None]*n]*n
##barve = [None]*n
##for i in b.keys():
##    j = eval(i)
##    if b[i] and j[0][0] != "(":
##        barve[j[1]] = j[0]
##for i in b.keys():
##    j = eval(i)
##    if b[i] and j[0][0] == "(":
##        j = eval(j[0]),j[1]
##        rešitev[j[0][0]][j[0][1]] = barve[j[1]]
##
##print(rešitev)



t = [[0,0,4,0],[0,2,0,3],[2,0,0,0],[0,4,0,1]]

g = {"a":{"b","c","d"},"b":{"a"},"c":{"a"},"d":{"a"}}








