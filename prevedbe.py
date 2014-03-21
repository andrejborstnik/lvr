from booli import *
from solver import *

def barvanje(g,k):
    """Ali lahko graf podan s slovarjem g pobarvamo s k barvami? """
    def sprem(v,b):
        return Spr(str(v)+","+str(b))
    
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

g = {"a":{"d"},"b":{"d"},"c":{"d"},"d":{"a","b","c"}}


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

def sudoku(tabela):
    n = len(tabela)
    k = int(n**0.5)
    g = {(i,j):set()  for i in range(n) for j in range(n)}
    for i in range(n):
        for j in range(n):
            for x in range(n):
                if x != j: g[(i,j)].add((i,x))
                if x != i: g[(i,j)].add((x,j))
                if (k*(i//k) + x//k, k*(j//k)+x%k)!=(i,j): g[(i,j)].add((k*(i//k) + x//k, k*(j//k)+x%k))

    #barve so 1,2,...,n

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

    for i in g: print(i,g[i])
    
    return barvanje(g,n)














