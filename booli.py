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

    def vstavi(self,slo):
        return self

    def kopija(self):
        return T()
    
    def poenostavi(self,cnf=False):
        return T()

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

    def vstavi(self,slo):
        return self

    def kopija(self):
        return F()
    
    def poenostavi(self,cnf=False):
        return F()

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

    def vstavi(self,slo):
        #Ni valuacija, ampak samo delno vstavljanje.
        if self.ime in slo.keys():
            if slo[self.ime]:
                return T()
            return F()
        return self

    def kopija(self):
        return Spr(self.ime)
    
    def poenostavi(self,cnf=False):
        return Spr(self.ime)

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

    def vstavi(self,slo):
        return Neg(self.izr.vstavi(slo))

    def kopija(self):
        return Neg(self.izr.kopija())
    
    def poenostavi(self,cnf=False):
        a = self.izr.kopija().poenostavi(cnf)
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

    def vstavi(self,slo):
        return In(*tuple(i.vstavi(slo) for i in self.sez))

    def kopija(self):
        return In(*tuple(i.kopija() for i in self.sez))
    
    def poenostavi(self,cnf=False):
        if len(self.sez)==0: return T()
        elif len(self.sez)==1: return self.kopija().sez.pop().poenostavi(cnf)
        slo = {}
        for i in self.kopija().sez:
            i=i.poenostavi(cnf)
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
            slo[Ali]={(Ali(*tuple(menjave[i])).poenostavi(cnf) if menjave[i]!=0 else None ) if i in menjave else i for i in slo[Ali]} - {None}#Poenostavi od None ne obstaja Tomaž!

            #po absorpciji je treba tipe podizrazov posodobiti
            pomo=[]
            for i in slo[Ali]:
                if type(i)!=Ali:
                    pomo.append(i)
                    if type(i) in slo: slo[type(i)].add(i)
                    else: slo[type(i)]={i}
            for i in pomo: 
                slo[Ali].remove(i)
                
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
        if len(temp.sez)==0: return T()
        elif len(temp.sez)==1: return temp.kopija().sez.pop()
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

    def vstavi(self,slo):
        return Ali(*tuple(i.vstavi(slo) for i in self.sez))
    
    def kopija(self):
        return Ali(*tuple(i.kopija() for i in self.sez))
    
    def poenostavi(self,cnf=False):
        if len(self.sez)==0: return F()
        elif len(self.sez)==1: return self.kopija().sez.pop().poenostavi(cnf)
        slo = {}
        for i in self.kopija().sez:
            i=i.poenostavi(cnf)
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
            slo[In]={(In(*tuple(menjave[i])).poenostavi(cnf) if menjave[i]!=0 else None ) if i in menjave else i for i in slo[In]} - {None}

            #po absorpciji je treba tipe podizrazov posodobiti
            pomo = []
            for i in slo[In]:
                if type(i)!=In:
                    pomo.append(i)
                    if type(i) in slo: slo[type(i)].add(i)
                    else: slo[type(i)]={i}
            for i in pomo: 
                slo[In].remove(i) 
        
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
                return In(*tuple(Ali(x,*tuple(set().union(*tuple(slo.values()))-{a})) for x in a.sez)).poenostavi(True)
                    
       
        

        mn=set()
        for i in slo.values():
            mn|=i
        temp = Ali(*tuple(mn))
        if len(temp.sez)==0: return F()
        elif len(temp.sez)==1: return temp.kopija().sez.pop()
        else: return temp

    def spremenljivke(self):
        a = set()
        for i in self.sez:
            a|=i.spremenljivke()
        return a

def CNF(formula):
    """pretvori dano formulo v konjuktivno normalno obliko"""
    return formula.poenostavi(cnf = True)


###################### TESTNI PRIMERI ZA POENOSTAVLJANJE ##################################################################################

p = Spr("p")
q = Spr("q")
r = Spr("r")

primer1 = Ali(p,In(q,p))

primer2 = In(p,Ali(q,Neg(p)))

primer3 = In(Ali(p,q),Ali(p,r))

primer4 = In(In(p,q),In(q,r),In(r,p))

primer5 = In(Ali(p,q),Ali(q,r),Ali(r,p),Neg(In(p,q)),Neg(In(q,r)),Neg(In(r,p)))





































    

