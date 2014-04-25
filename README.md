lvr
===
**Avtorja:** _Tomaž Stepišnik Perdih_ in _Andrej Borštnik_

**Ekipa**   :rocket:
***

Na tem repozituriju se nahajajo SAT solverji (s spremljajočo mehanizacijo) in nekatere prevedbe problemov na SAT.

***
**Kazalo:**

datoteka | vsebina 
:---: | :--- 
_booli.py_ | Objekti T() = logična resnica, F() neresnica, ..., za predstavitev in poenostavljanje logične formule.
_prevedbe.py_ | Prevedbe nekaterih znanih problemov na SAT (grafi so podani s slovarjem, sudokuji pa s tabelami).
_util.py_ | Nekatere pomožne funkcije in objekti (sklad, kopica, ...).
_chaff.py_ | Aproksimacija __*Chaff*__[1] SAT solverja, ne dela povsem.
*bf_dpll.py* | Naivni SAT solver, ter neka različica __*DPLL*__[2].
*resitelj.py* | Vsebuje SAT solver, navdahnjen z __*Chaff*__[1] in __*GRASP*__[3] SAT solverjema.
*demo_util.py* | Pomožne funkcije za demonstracijo uporabe preostale kode.
*demo.py* | Vmesnik (priporočena uporaba preko IDLE-a) za demonstracijo.
*test.py* | Priročni funkciji za testiranje SAT solverja.
*primeri_r"([0-9]+)"/* | Enakomerno naključni 3-SAT primeri s r"\1" spremenljivkami [4].
_*.sud_ | Primeri sudokujev.

***
**Viri:**

1. [Chaff SAT solver](https://www.princeton.edu/~chaff/publication/DAC2001v56.pdf "Chaff")
2. [DPLL SAT solver](http://en.wikipedia.org/wiki/DPLL_algorithm "DPLL")
3. [GRASP SAT solver](http://embedded.eecs.berkeley.edu/Alumni/wjiang/ee219b/grasp.pdf "GRASP")
4. [SATLIB benchmark problemi](http://www.cs.ubc.ca/~hoos/SATLIB/benchm.html "SATLIB")
5. [Hevristike za ugibanje](http://www.cs.wm.edu/~idillig/cs780-02/matthew-pirocchi.pdf "ugibanje")
6. [O restartih](http://cs.brown.edu/people/pvh/CPL/Papers/v4/Paper1(pp3-13).pdf "restarti")
7. [Primer delovanja GRASP](http://www.cs.cmu.edu/~mtschant/15414-f07/lectures/grasp-ex.pdf "Primer")

***
**Uporaba:**

Algoritem testiramo tako, da poženemo test.py. V kodi se lahko odkomentira testiranje algoritma na primerih [4]. Lahko pa ga uporabnik testira na poljubni cnf formuli. Najprej sestavimo logično formulo in si jo shranimo. To lahko naredimo na več načinov:

1. Logično formulo napišite na roko (npr. `In(Spr("a"),Neg(Spr("b")),T())` = `a /\ ~b /\ True`)
2. Uporabite eno od napisanih prevedb (npr. `sudoku([[0]]))`, `povezanost({"a":{"b"},"b":{"a"}})`).
3. Z uporabo funkcije `primer` zgenerirate neko enostavno (vsaka spremenljivka se pojavi enkrat) naključno formulo (npr. `primer(n = 50)` vrne primer, ki ima cca. 25 spremeljivk in naključno strukturo).
4. Napišete svojo prevedbo.

Nato z nekim solverjem najdemo rešitev (če obstaja) in preberemo podatke, ki nas zanimajo.
Primer uporabe:
```python
tabela = [[0]*4 for i in range(4)]
formula = sudoku(tabela)
resitev = resitelj(formula)
prikazi(resit(resitev,len(tabela))) #samo za sudoku
```
Za reševanje sudokuja sva pripravila priročno funkcijo, ki vse delo opravi sama (`resi_sudoku`).
Če želite demonstracijo, poženite _demo.py_, ali pa kličite `demo()`, v IDLE-u.

***
**Testiranje:**

V *test.py* se nahajata funkciji:
* `test` ... Primeri naj bodo shranjeni v standardnem DIMACS formatu z imeni datotek ime-0 **ŠT** .cnf. Funkciji podate `n`, primere, ki bi jih radi pognali (n je niz oblike npr. "2-5,8,4-10"), `file`, pot do datoteke (`ime` v prejšnjem stringu). `Printaj` pove ali naj sproti izpisuje čas vsakega izračuna, `sat` pa ali so formule izpolnjive (preverja, ali je prav rešeno). Testiranje vseh 1000 primerov s 100 spremenljivkami traja cca. 400 sekund. 100 primerov s 150 spremenljivkami traja cca. 750 sekund (primeri iz[4]). 1000 primerov s 50 spremenljivkami traja cca. 40 sekund.
* `test1` ... Podamo mu `k`, tj. število primerov in `velikost`, od katere je linearno odvisna pričakovana velikost formule. Test1 uporablja naključne primere iz funkcije `primer`.

***
**Lastnosti, prednosti in slabosti:**

1. Algoritem `chaff` prehitro zavrže valuacije, ki bi lahko bile prave. Če pa vrne valuacijo je ta pravilna. Odpravljanje napak je bilo zaradi časovne stiske opuščeno.
2. V algoritmu `resitelj` sva se znebila kontrolnih literalov (ter s tem precej sivih las) in dodala uporabo konfliktnih stavkov. Čas, ki ga potrebuje za rešitev istega problema lahko močno niha. Rešitev za to naj bi bili restarti - algoritem poženemo od začetka, če se zdi, da smo zašli v slabe veje ugibanja. Ker so se poskusi implementacije tega končali neuspešno, oziroma niso prinesli vidnih izboljšav, sva delo na tem opustila. Pri izbiri literalov za ugibanje uporabljava svojo hevristiko, upoštevava pa v koliko stavkih se literal pojavi in kako dolgi so ti stavki. Večina energije je šla v zasnovo algoritma, sama implementacija pa ni močno optimizirana. Moč algoritma se zato bolje opazi na res velikih primerih.
3. Funkcija `poenostavi` ima samo tri možnosti (cnf, krajšanje in samo krajšanje True/False). Zato ga je zelo zamudno poganjati, tudi na formulah blizu cnf/pokrajšane. `resitelj` in `chaff` zato trenutno predpostavita, da je formula, ki jo dobita že v cnf (lahko ima samo vgnezdene Ali-je oz. In-e).

