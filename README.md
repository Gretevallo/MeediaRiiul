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
- HTML
- CSS
- JavaScript
- Flask
- Flask-Login
- Flask-Bcrypt
- pandas (andmete töötlemiseks)
- CSV
- Pip
- GitHub

## Failid

app.py – rakenduse põhiprogramm (routing, andmetöötlus, kasutajate haldus)

meediariiul.py – KogumikuHaldur klass: lugemine, lisamine, muutmine, kustutamine

users.csv – kasutajate info (ID, kasutajanimi, parooliräsi)

data_<userid>.csv – iga kasutaja isiklik meediakogumik

meediariiul.css – kujundus

README.md – projekti kirjeldus, kasutusjuhend

# Alfaversioon

Alfaversiooni võimaldab kasutajal hallata oma isiklikku meediakogumikku (nt raamatuid, filme ja sarju): lisada uusi teoseid, vaadata soovinimekirja,näha loetud raamatute  statistikat (nt keskmine hinnang), salvestada kõik andmed automaatselt faili data.csv.

Uue teose lisamisel saab kasutaja sisestada: pealkirja, meedia tüübi (raamat / film / sari), žanri, autori või režissööri, staatuse (lõpetatud / soovinimekiri / pooleli / peatatud), hinnangu, arvamuse, kuupäeva ja lisainfo
Programm valideerib, et tüüp ja staatus oleksid lubatud väärtused.
Kõik andmed salvestatakse püsivalt faili data.csv.

# Beetaversioon

Beetaversioon võimaldab kasutajal turvaliselt hallata oma isiklikku meediakogumikku. Kasutaja saab luua konto, sisse logida ning vaadata ja muuta oma profiili.

Kogumikus saab lisada, vaadata, muuta ja kustutada teoseid, sh pealkiri, meedia liik, žanr, autor või režissöör, staatus, arvamus, hinne ja kuupäev. Tabelivaates kuvatakse korraga kuni 10 teost. Otsing ja filtreerimine toimivad žanri, autor/režissööri, pealkirja, meedia liigi ja staatuse järgi.

Soovinimekiri võimaldab hallata tuleviku meediat, lisada ja kustutada teoseid ning filtreerida kuvades ka koguarvu.

Statistika kuvab meedia liikide jaotuse, lõpetatud/pooleli/soovinimekirjas teoste hulga, keskmise hinne ja parima teose avalehel koos sellel kui ka eelmisel kuul lõpetatud teoste hulgaga.

Avalehel kuvatakse lühike ülevaade kogumikust ja kiirlingid peamistele funktsioonidele. 

# Käivitamine lokaalselt
1. Paigalda Python (kui puudub):
   - Laadi alla https://www.python.org/downloads/windows/
   - Installimisel märgi "Add Python to PATH"

2. Klooni repo:
   git clone https://github.com/Gretevallo/MeediaRiiul.git

3. Liigu kausta:
   cd MeediaRiiul

4. Paigalda sõltuvused:
   python -m pip install -r requirements.txt

   Kui mõni teek puudub, paigalda käsitsi:
   python -m pip install flask 
   python -m pip install flask-login 
   python -m pip install flask-bcrypt 
   python -m pip install pandas

5. Käivita:
   python app.py

6. Ava brauseris:
   http://127.0.0.1:5000
www.python.org
