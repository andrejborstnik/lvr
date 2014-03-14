class T():
    def __init__(self):
        pass

    def __repr__(self):
        return "⊤"

    def __eq__(self,other):
        return type(other)==T

    def __hash__(self):
        return hash(repr(self))

    def vrednost(self,slo):
        return True

    def poenostavi(self):
        return self

    def spremenljivke(self):
        return set()

###################################################
class F():
    def __init__(self):
        pass

    def __repr__(self):
        return "⊥"
    
    def __eq__(self,other):
        return type(other)==F

    def __hash__(self):
        return hash(repr(self))

    def vrednost(self,slo):
        return False

    def poenostavi(self):
        return self

    def spremenljivke(self):
        return set()

###################################################
class Spr():
    def __init__(self,ime):
        self.ime=ime

    def __repr__(self):
        return str(self.ime)

    def __eq__(self,other):
        if type(other)==Spr:
            return self.ime==other.ime
        else:
            return False

    def __hash__(self):
        return hash(repr(self))

    def vrednost(self,slo):
        return slo[self.ime]

    def poenostavi(self):
        return self

    def spremenljivke(self):
        return {self.ime}
    
######################################################
class Neg():
    def __init__(self,izr):
        self.izr = izr

    def __repr__(self):
        if type(self.izr)!=Ali and type(self.izr)!=In:
            return "¬"+repr(self.izr)
        else:
            return "¬("+repr(self.izr)+")"

    def __eq__(self,other):
        if type(other) == Neg:
            return self.izr==other.izr
        else:
            return False
    
    def __hash__(self):
        return hash(repr(self))

    def vrednost(self,slo):
        return not self.izr.vrednost(slo)

    def poenostavi(self,cnf=False):
        a = self.izr.poenostavi(cnf)
        tip = type(a)
        if tip == T:
            return F()
        elif tip == F:
            return T()
        elif tip == Spr:
            return Neg(a)
        elif tip == Neg:
            return a.izr
        elif tip == In:
            return Ali(*tuple(Neg(i) for i in a.sez)).poenostavi(cnf)
        elif tip == Ali:
            return In(*tuple(Neg(i) for i in a.sez)).poenostavi(cnf)

    def spremenljivke(self):
        return self.izr.spremenljivke()

#####################################################
class In():
    def __init__(self,*args):
        self.sez=set(args)

    def __repr__(self):
        niz=""
        for i in self.sez:
            if type(i)!=In and type(i)!=Ali:
                niz+=" ∧ "+repr(i)
            else:
                niz+=" ∧ ("+repr(i)+")"

        return niz[3:]

    def __eq__(self,other):
        if type(other)==In:
            return self.sez==other.sez
        else:
            return False
    
    def __hash__(self):
        return hash(repr(self))

    def vrednost(self,slo):
        a=True
        for i in self.sez:
            a= a and i.vrednost(slo)
            if a==False:
                return a
        return a

    def poenostavi(self,cnf=False):
        if len(self.sez)==0: return T()
        elif len(self.sez)==1: return self.sez.pop().poenostavi(cnf)
        slo = {}
        for i in self.sez:
            i=i.poenostavi()
            if type(i)==F: return F()
            elif type(i)==T: pass
            elif type(i) in slo:
                slo[type(i)].add(i)
            else:
                slo[type(i)]={i}

        #če imaš In znotraj In, ju lahko združiš
        if In in slo.keys():
            for j in slo[In]:
                for i in j.sez:
                    if type(i) in slo: slo[type(i)].add(i)
                    else: slo[type(i)]={i}
      
            del slo[In]

        #complementary law
        if Neg in slo.keys():
            for i in slo[Neg]:
                for j in slo.values():
                    if i.izr in j:
                        return F()

        #absorpcija in common identities
        if Ali in slo.keys():
            menjave={}
            for i in slo[Ali]:
                for j in slo.values():
                    for k in j:
                        if k in i.sez:
                            menjave[i]=0
                        elif Neg(k) in i.sez:
                            menjave[i]=i.sez-{Neg(k)}
            slo[Ali]={(Ali(*tuple(menjave[i])) if menjave[i]!=0 else None ).poenostavi(cnf) if i in menjave else i for i in slo[Ali]} - {None}

        #distributivnost
            if len(slo[Ali])>1 and not cnf:
                presek = 42
                for i in slo[Ali]:
                    if presek==42:
                        presek={j for j in i.sez}
                    else:
                        presek&=i.sez
                if presek:
                    slo[Ali]={Ali(
                        In(*tuple(set().union(*tuple(i.sez-presek for i in slo[Ali])))),
                        *tuple(presek)
                        )}
                

        #sestavi poenostavljen izraz
        mn=set()
        for i in slo.values():
            mn|=i
        temp = In(*tuple(mn))
        if len(temp.sez)==1: return temp.sez.pop()
        else: return temp
    
    def spremenljivke(self):
        a = set()
        for i in self.sez:
            a|=i.spremenljivke()
        return a

    
########################################################
    
class Ali():
    def __init__(self,*args):
        self.sez=set(args)

    def __repr__(self):
        niz=""
        for i in self.sez:
            if type(i)!=Ali and type(i)!=In:
                niz+=" ∨ "+repr(i)
            else:
                niz+=" ∨ ("+repr(i)+")"

        return niz[3:]

    def __eq__(self,other):
        if type(other)==Ali:
            return self.sez==other.sez
        else:
            return None

    def __hash__(self):
        return hash(repr(self))

    def vrednost(self,slo):
        a=False
        for i in self.sez:
            a= a or i.vrednost(slo)
            if a==True:
                return a
        return a

    def poenostavi(self,cnf=False):
        if len(self.sez)==0: return F()
        elif len(self.sez)==1: return self.sez.pop().poenostavi(cnf)
        slo = {}
        for i in self.sez:
            i=i.poenostavi()
            if type(i)==T: return T()
            elif type(i)==F: pass
            elif type(i) in slo:
                slo[type(i)].add(i)
            else:
                slo[type(i)]={i}

        #če imaš Ali znotraj Ali, ju lahko združiš
        if Ali in slo.keys():
            for j in slo[Ali]:
                for i in j.sez:
                    if type(i) in slo: slo[type(i)].add(i)
                    else: slo[type(i)]={i}
      
            del slo[Ali]
        
        #complementary law
        if Neg in slo.keys():
            for i in slo[Neg]:
                for j in slo.values():
                    if i.izr in j:
                        return T()

        #absorpcija in common identities in distributivnost
        if In in slo.keys():
            menjave={}
            for i in slo[In]:
                for j in slo.values():
                    for k in j:
                        if k in i.sez: #absorpcija
                            menjave[i]=0
                        elif Neg(k) in i.sez: #common id
                            menjave[i]=i.sez-{Neg(k)}
            slo[In]={(In(*tuple(menjave[i])) if menjave[i]!=0 else None ).poenostavi(cnf) if i in menjave else i for i in slo[In]} - {None}
        
            #distributivnost
            if len(slo[In])>1:
                presek = 42
                for i in slo[In]:
                    if presek==42:
                        presek={j for j in i.sez}
                    else:
                        presek&=i.sez
                if presek:
                    slo[In]={In(
                        Ali(*tuple(set().union(*tuple(i.sez-presek for i in slo[In])))),
                        *tuple(presek)
                        )}

            if cnf:
                a = min(slo[In],key=lambda x:len(x.sez))
                print(set().union(*tuple(slo.values()))-{a})
                return In(*tuple(Ali(x,*tuple(set().union(*tuple(slo.values()))-{a})) for x in a.sez)).poenostavi(True)
                    
       
        

        mn=set()
        for i in slo.values():
            mn|=i
        temp = Ali(*tuple(mn))
        if len(temp.sez)==1: return temp.sez.pop()
        else: return temp

    def spremenljivke(self):
        a = set()
        for i in self.sez:
            a|=i.spremenljivke()
        return a


def CNF(formula):
    """pretvori dano formulo v konjuktivno normalno obliko"""
    f = formula.poenostavi(cnf = True)
    
    
    
    
    

###################### TESTNI PRIMERI ZA POENOSTAVLJANJE ##################################################################################

p = Spr("p")
q = Spr("q")
r = Spr("r")

primer1 = Ali(p,In(q,p))

primer2 = In(p,Ali(q,Neg(p)))

primer3 = In(Ali(p,q),Ali(p,r))

primer4 = In(In(p,q),In(q,r),In(r,p))

primer5 = In(Ali(p,q),Ali(q,r),Ali(r,p),Neg(In(p,q)),Neg(In(q,r)),Neg(In(r,p)))

            




###################### VAJE ŠTEVILKA 2 ########################################################################


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
    

    return In(f1,f2,f3,f4).poenostavi()

            

##################### REŠEVANJE SAT #######################################################################

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
            

    
            




from random import random
from re import sub
def primer(b = True, n = False):
    #Maximalna velikost primera je 1000.
    moznosti = ["In","Ali","Spr","Spr","Spr","Spr"]
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
                    formula+="),"+a+"("+str(i)+"),"
                else:
                    formula+="),"+"Neg("+a+"("+str(i)+")),"
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
                    formula+= a+"("+str(i)+"),"
                else:
                    formula+= "Neg("+a+"("+str(i)+")),"
    if formula[-1] == ",":
        formula=formula[:-1]
    formula+=")"
    while globina>1:
        globina-=1
        formula+=")"
    #formula = sub(r"Neg\(\),*",r"",formula)
    return eval(formula)


print(primer(n = 300))



































    

