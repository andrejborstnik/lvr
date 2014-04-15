lvr
===
**Avtorja:** _Tomaž Stepišnik Perdih_ in _Andrej Borštnik_
***

Na tem repozituriju se nahajajo SAT solverji (z spremljajočo mehanizacijo), za SAT solver in nekatere prevedbe problemov na SAT.

***
**Kazalo:**

datoteka | vsebina 
:---: | :--- 
_booli.py_ | Objekti T() = logična resnica, F() neresnica, ..., za predstavitev in poenastavitev logične formule.
_prevedbe.py_ | Prevedbe nekaterih znanih problemov na SAT (grafi so podani s slovarjem, sudokuji pa s tabelami).
_util.py_ | Nekatere pomožne funkcije in objekti (sklad, kopica, ...).
_chaff.py_ | Aproksimacija __*Chaff*__[1] SAT solverja, ne dela povsem.
*bf_dpll.py* | Naivni SAT solver, ter neka različica *DPLL*[2].
*resitelj.py* | Vsebuje SAT solver, navdahnjen z __*Chaff*__[1] in __*GRASP*__[3] SAT solverjema.
*demo_util.py* | Pomožne funkcije za demonstracijo uporabe preostale kode.
*demo.py* | Vmesnik (preko IDLE-a) za demonstracijo.
_*.sud_ | Primeri sudokujev.

***
**Viri:**

1. [Chaff SAT solver](https://www.princeton.edu/~chaff/publication/DAC2001v56.pdf "Chaff")
2. [DPLL SAT solver](http://en.wikipedia.org/wiki/DPLL_algorithm "DPLL")
3. [GRASP SAT solver](http://embedded.eecs.berkeley.edu/Alumni/wjiang/ee219b/grasp.pdf "GRASP")

***
**Uporaba:**

Najprej sestavimo logično formulo in si jo shranimo. To lahko naredimo na več načinov:

1. Logično formulo napišite na roko (npr. `In(Spr("a"),Neg(Spr("b")),T())` = `a /\ ~b /\ True`)
2. Uporabite eno od napisanih prevedb (npr. `sudoku([[0]]))`, `povezanost({"a":{"b"},"b":{"a"}})`).
3. Z uporabo funkcije `primer` zgenerirate neko enostavno (vsaka spremenljivka se pojavi enkrat) naključno formulo (npr. `primer(n = 50)` vrne primer, ki ima cca. 25 spremeljivk in naključno strukturo).
4. Napišete svojo prevedbo.

Nato s nekim solverjem najdemo rešitev (če obstaja) in preberemo podatke, ki nas zanimajo.
Primer uporabe:
```python
tabela = [[0]*4 for i in range(4)]
formula = sudoku(tabela)
resitev = resitelj(formula)
prikazi(resitev) #samo za sudoku
```
Za reševanje sudokuja sva pripravila priročno funkcijo, ki vse delo opravi sama (`resi_sudoku`).
Če želite demonstracijo, poženite _demo.py_, ali pa kličite `demo()`, v IDLE-u.

***
**Lastnosti, prednosti in slabosti:**

1. `chaff` prehitro zavrže valuacije, ki bi lahko bile prave. Če pa vrne valuacijo je ta pravilna.
2. `resitelj` je lahko zelo hiter, če izbira prave spremenljivke. Pomembno je, da so parametri (izbira podobno, kot Chaff) dobro nastavljeni.
3. `poenostavi` ima samo tri možnosti (cnf, dnf in samo krajšanje True/False). Zato ga je zelo zamudno poganjati, tudi na formulah blizu cnf/dnf. `resitelj` in `chaff` zato trenutno predpostavita, da je formula, ki jo dobita že v cnf (lahko ima samo vgnezdene Ali-je oz. In-e).

