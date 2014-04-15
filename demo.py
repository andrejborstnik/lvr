"""Tu bo potekala demonstracija primerov."""
from demo_util import *
import sys
from time import sleep

def demo():
    cas1 = 3
    cas2 = 0.5
    try:
        print("Avtorja: Tomaž Stepišnik Perdih in Andrej Borštnik\n")
        print("DEMONSTRACIJA UPORABE: reševanje sudokuja\n")

        print("Navodila za uporabo:")
        print("Sudoku podamo kot tabelo tabel, ali pa kot ustrezen format v datoteki (glej primer.sud)."+
              " V zadnjem primeru pustimo tabelo prazno."+
              " Elementi so lahko katerikoli znaki (ki ne motijo programa samega), razen 0 in None."+
              " Ti dve oznaki sta rezervirani za prazno polje. "+
              "Lahko si izberemo (možnosti se ne izključujejo), da se sudoku lepo izpiše,"+
              " se v ustreznem formatu zapiše v datoteko, ali pa se lepo izpiše v datoteko."+
              " Opomba: podana datoteka mora obstajati, sicer se algoritem ne bo izvedel."
              " Prav tako si lahko izberemo, s katerim algoritmom bomo reševali problem. Trenutno so na voljo"+
              " naslednji algoritmi: DPLL, resitelj in bfSAT. ")

        print("\n")
        
    except (KeyboardInterrupt, EOFError):
        print("\nJa tole res lahko dela počasi.\n")

    try:
        dem = de()
        if dem:
            print("\nDemonstracija:")
            print("Vnesi tabelo:  ",end ="")
            for i in str([[None]]): sleep(cas2);print(i,end="")
            sleep(cas2)
            print("")
            print("Vnesi vhodno datoteko:  ",end="");sleep(cas1); print("")
            print("Ali naj sudoku lepo izpišem?  ", end="")
            for i in "Da":sleep(cas2);print(i,end="")
            sleep(cas2)
            print("")
            print("Vnesi izhodno datoteko:  ",end="");sleep(cas1);print("")
            print("S katerim algoritmom želite reševati problem?  ",end="");
            for i in "DPLL":sleep(cas2);print(i,end="")
            sleep(cas2)
            print("")
            print("Vnesi datoteko, kamor naj lepo izpišem sudoku:  ",end="");sleep(cas1);print("")
            #resi_sudoku(tabela,input_file,izpisi,output_file,solver,izpis_output_file)
            print("")

            #print("Naloga:  \n")
            #print("\nRešeni sudoku:  \n")
            resi_sudoku(tabela = [[None]], izpisi = True, solver = "DPLL")

            print("\nPoizkusite še sami!\n")
        else:
            print("\nPreskočili ste demonstracijo!\n")
    except (KeyboardInterrupt, EOFError):
        print("\n\nJoj, si neučakan!\n")

    while True:
        try:
            tabela = input("Vnesi tabelo:  ")
            if not tabela: tabela = []
            else: tabela = eval(tabela)
            input_file = input("Vnesi vhodno datoteko:  ")
            izpisi = izp()
            output_file = input("Vnesi izhodno datoteko:  ")
            solver = sol()
            izpis_output_file = input("Vnesi datoteko, kamor naj lepo izpišem sudoku:  ")
            resi_sudoku(tabela,input_file,izpisi,output_file,solver,izpis_output_file)
            print("")
        except UsageError as e:
            print("\nPrišlo je do naslednje napake: {0}\n".format(e.value))
            continue
        except (KeyboardInterrupt,EOFError):
            print("\nADIJO!\n")
            break
        except:
            print("\nUnexpected error:", sys.exc_info()[0])
            print("Prosiva, da poročate o okoliščinah, pri katerih je prišlo do te napake.\nHvala!\n")
            continue
    return None
demo()
    

