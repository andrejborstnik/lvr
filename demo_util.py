from prevedbe import *
from util import *
from tomazevchaff import tchaff
from os import path
#a = sudoku([["Bla",None,None,None],["Kor",None,None,None],["AS",None,None,None],["MA",None,None,None]])

def resi_sudoku(tabela=[], input_file="", izpisi=False, output_file="", solver = "tchaff", izpis_output_file=""):
    """ v datoteki pričakuje sudoku v formatu (primer 2x2):
    # a,b \n
    # c,d \n
    , kjer so lahko a,b,c in d poljubni neprazni nizi oz. števila, razen 0.
     0, \prazno in None so rezervirani za prazno polje.
     V podani datoteki naj bo samo en sudoku in naj ne bo praznih vrstic."""
    if type(tabela)!= list:
        raise UsageError("Podan \"sudoku\" ni tabela.")
    if solver not in ["DPLL","Chaff","bfSAT", "tchaff"]:
        raise UsageError("Podali ste solver, ki ni implementiran! (ali pa ste se zatipkali)")
    if not tabela:
        if not input_file:
            raise UsageError("Nisete podali sudokuja!")
##        try:
        if not path.isfile(input_file):
            raise UsageError("Podana datoteka z vhodnimi podatki ne obstaja!")
        f = open(input_file,"r",encoding="utf-8")
        file = f.read()
        vrstice = file.split("\n")
        k=1
        for i in vrstice:
            if i:
                k+=1
        vrstice=vrstice[:k]
        n = k-1
        #print(n)
        if "," in file:
            locilo = ","
        elif ";" in file:
            locilo = ";"
        elif n == 1:
            locilo = " " #imamo 1x1 sudoku, ničesar ne rabimo ločiti.
        else:
            raise UsageError("Ločilo med polji je napačno!")
        if not vrstice:
            raise UsageError("Podana datoteka je prazna!.")
        tabela = [None]*n
        for i in range(n):
            k = vrstice[i].split(locilo)
            if len(k)!=n:
                raise UsageError("{0}. vrstica v datoteki ima premalo/preveč elementov.".format(i+1))
            tabela[i] = k
        #print(tabela)
        f.close()

##        except:
##            raise InternalError("Nekaj je šlo narobe pri branju datoteke,"+
##                                "prosim pošljite nam email s podatki o vhodu,"+
##                                "pri katerem je prišlo do te napake.")
    n = len(tabela)
    k = int(n**0.5)
    if k*k !=n:
        raise UsageError("Podana tabela ne predstavlja sudokuja, saj dolžina stranice ni popoln kvadrat!")
    #print(sudoku(tabela))
    for i in range(n):
        if len(tabela[i])!=n:
            raise UsageError("{0}. vrstica v \"sudokuju\" ima premalo/preveč elementov.".format(i+1))
        elif type(tabela[i])!=list:
            raise UsageError("{0}. \"vrstica\" v \"sudokuju\" ni tabela.".format(i+1))
    if izpisi: print("\nNaloga:\n");prikazi(tabela);print("\ndelam...  \n")
    res = eval(solver+"(sudoku(tabela))")
    #za to si rabimo nekje zapomnit imena
    #res = eval(sub(r"([^\(]+?)([0-9]+)([^\)]+?)",r"\1imena[\2-1]\3",str(res))
    if res == "Formula ni izpolnljiva":
        print("Rešitev problema ne obstaja!")
        return None
    resitev = resit(res,n)
    if izpisi:
        print("\nRešeni sudoku:  \n")
        prikazi(resitev)
    if output_file:
        if not path.isfile(output_file):
            raise UsageError("Datoteka, kamor naj bi zapisal rezultat ne obstaja!")
        f = open(output_file,"w",encoding="utf-8")
        file = ""
        for i in resitev:
            s = ""
            for j in i:
                s+= str(j)+","
            s = s[:-1]+"\n"
            file+=s
        f.write(file[:-1])
        f.close()
    if izpis_output_file:
        if not path.isfile(izpis_output_file):
            raise UsageError("Datoteka, kamor naj bi izpisal rezultat ne obstaja!")
        f = open(izpis_output_file,"w",encoding="utf-8")
        f.write(prikazi(resitev,file = True))
        f.close()
    return None

def resit(rezultat,n):
    resitev = [[None]*n for j in range(n)]
    barve = [None]*n
    for i in rezultat.keys():
        j = eval(i)
        if rezultat[i] and j[0][0] != "(":
            barve[j[1]] = j[0]
    for i in rezultat.keys():
        j = eval(i)
        if rezultat[i] and j[0][0] == "(":
            j = eval(j[0]),j[1]
            resitev[j[0][0]][j[0][1]] = barve[j[1]]
    return resitev

def prikazi(resitev,file=False):
    #pravilno deluje samo za sudokuje (dolžina tabele mora biti pravilen kvadrat)
    if type(resitev)!= list:
        raise UsageError("Podan \"sudoku\" ni tabela.")
    n = len(resitev)
    k = int(n**0.5)
    file1=""

    for i in range(n):
        if len(resitev[i])!=n:
            raise UsageError("{0}. vrstica v \"sudokuju\" ima premalo/preveč elementov.".format(i+1))
        elif type(resitev[i])!=list:
            raise UsageError("{0}. \"vrstica\" v \"sudokuju\" ni tabela.".format(i+1))

    naj = ""
    for i in resitev:
        for j in i:
            if len(str(j))>len(naj):
                naj = str(j)
    m = len(naj)
##    if m%2==0:
##        m+=1

    pomo1="#"+(("─"*(2+m)+" ")*(k-1)+"─"*(2+m)+"║")*(k-1)+("─"*(2+m)+" ")*(k-1)+"─"*(2+m)+"#"
    #pomo1="#"+("─"*(2+m)+" ")*(n-1)+"─"*(2+m)+"#"
    pomo2="#"+"="*((2+m)*n+n-1)+"#"
    pomo3="#"*((2+m)*n+n-1+2)
    file1+=pomo3+"\n"
    for i in range(n):
        s = "#"
        for j in range(n):
            l = (2+m-len(str(resitev[i][j])))//2
            if 2*l + len(str(resitev[i][j])) == 2+m:
                d = l
            else:
                d = l + 1
            if j%k == k-1 and j != n-1:
                s+=" "*l+str(resitev[i][j])+" "*d+"║"
            elif j == n-1:
                s+=" "*l+str(resitev[i][j])+" "*d+"#" 
            else:
                s+=" "*l+str(resitev[i][j])+" "*d+"│"
        file1+=s+"\n"
        if i%k==k-1 and i != n-1:
            file1+=pomo2+"\n"
        elif i == n-1:
            file1+=pomo3
        else:
            file1+=pomo1+"\n"
    if not file:
        #print("\nRešeni sudoku:  \n")
        print(file1)
        return None
    return file1


def test(k,velikost = 70):
    t1 = 0
    t2 = 0
    for i in range(k):
        a = primer(n = velikost)
        print(len(a.spremenljivke()))
        b,t1a = DPLL(a,True)
        c,t2a = tchaff(a,True)
        t1+=t1a
        t2+=t2a
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

def izp():
    izpisi = input("Ali naj sudoku lepo izpišem? (da/ne)  ")
    if izpisi and izpisi in "DAdaDaJAjaJaYESYesyes":
        izpisi = True
    elif izpisi and izpisi in "NEneNeNOnoNo":
        izpisi = False
    else:
        print("Zal te nisem razumel, prosim poizkusi ponovno!")
        return izp()
    return izpisi

def sol():
    solver = input("S katerim algoritmom zelite reševati problem?  ")
    if not solver:
        solver = "tchaff"
    elif solver not in ["DPLL","tchaff","bfSAT"]:
        print("Algoritma \"{0}\" zal nismo implementirali. Prosim, vnesite drug algoritem.".format(solver))
        return sol()
    return solver

def de():
    dem = input("Ali želite demonstracijo? (da/ne)  ")
    if dem and dem in "DAdaDaJAjaJaYESYesyesSevedaseveda": dem = True
    elif dem and dem in "NEneNeNOnoNoNikakornikakornikdarNikdarNikolinikoli": dem = False
    else: return de()
    return dem
#Rezultati testiranja:
#tchaff je porabil 0.42 časa DPLL na velikosti 70, pri 100 ponovitvah
#0.59, 100, 10
#0.34, 100, 50
