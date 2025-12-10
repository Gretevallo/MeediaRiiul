# Isiklik raamatute ja filmide kogumik

See projekt on programm, mis aitab hallata isiklikku raamatute, filmide ja seriaalide nimekirja.  
Kogumik võimaldab:

- lisada loetud raamatuid ja vaadatud filme/seriaale koos arvamuse ja hinnanguga,
- lisada soovide nimekirja teoseid, mida tahad tulevikus lugeda/vaadata,
- otsida ja filtreerida teoseid,
- näha statistikat ja graafikuid (nt kui palju oled lugenud või vaadanud, keskmised hinnangud),
- saada lihtsaid soovitusi (nt “Sul on soovi nimekirjas 5 filmi, mida võiksid sel kuul ette võtta”).

## Kasutatud tehnoloogiad

- Python
- pandas (andmete töötlemiseks)
- matplotlib (visualiseerimiseks)
- tkinter või PySimpleGUI (kasutajaliides)

## Failid

- `meediariiul.py` – põhiprogramm
- `data.csv` – andmete hoidmine
- `README.md` – projekti kirjeldus

# Alfaversioon

Alfaversiooni võimaldab kasutajal hallata oma isiklikku meediakogumikku (nt raamatuid, filme ja sarju): lisada uusi teoseid, vaadata soovinimekirja,näha loetud raamatute  statistikat (nt keskmine hinnang), salvestada kõik andmed automaatselt faili data.csv.

Uue teose lisamisel saab kasutaja sisestada: pealkirja, meedia tüübi (raamat / film / sari), žanri, autori või režissööri, staatuse (lõpetatud / soovinimekiri / pooleli / peatatud), hinnangu, arvamuse, kuupäeva ja lisainfo
Programm valideerib, et tüüp ja staatus oleksid lubatud väärtused.
Kõik andmed salvestatakse püsivalt faili data.csv.

# Käivitamine lokaalselt
1. Klooni repo:
   git clone https://github.com/Gretevallo/MeediaRiiul.git
2. Liigu kausta:
   cd MeediaRiiul
3. Paigalda sõltuvused:
   pip install -r requirements.txt
4. Käivita:
   python app.py
5. Ava brauseris:
   http://127.0.0.1:5000
