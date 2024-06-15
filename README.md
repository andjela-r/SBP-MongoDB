# League of Legends Ranked Matches - optimizacija upita nad NoSQL bazom podataka
Projekat iz predmeta Sistemi baza podataka.  
- Skup podataka predstavlja podatke o ranked mečevima igrice **League of Legends** preuzet sa [kaggle.com](https://www.kaggle.com/datasets/paololol/league-of-legends-ranked-matches/data).  
- Svi .csv fajlovi skupa zauzimaju **695MB**. Nakon što se preuzmu svi fajlovi sa sajta i pošto postoje nedostajući podaci i veliki broj nekorišćenih obeležja, neophodno je pokrenuti skriptu **preprocesing.ipynb** sa .csv fajlovima u istom direktorijumu.  
- Novi skup podataka zauzima **292MB** i spreman je za dalju upotrebu.  
- Nakon što je napravljena nova baza podataka i kolekcije, import se može raditi putem skripte **import-data.py** ili ručno.  

## Sekcije
1. **Upiti [pre](https://github.com/andjela-r/SBP-MongoDB/blob/main/v1-part1.md) i [posle](https://github.com/andjela-r/SBP-MongoDB/blob/main/v2-part1.md) optimizacije**
2. **Korišćenje [design shema](https://github.com/andjela-r/SBP-MongoDB/blob/main/design-shema.ipynb)**
3. **[Indeksi](https://github.com/andjela-r/SBP-MongoDB/blob/main/indexes.md)**
4. **Poređenje rezultata pre i posle optimizacije**
