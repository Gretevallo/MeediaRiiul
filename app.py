"""
===========================================
MeediaRiiul – meediakogumiku veebirakendus
Autor: Grete Vällo ja Helena Sinilaid
Aasta: 2025

Käivitusjuhis:

Paigalda Python (kui puudub):

Laadi alla https://www.python.org/downloads/windows/
Installimisel märgi "Add Python to PATH"
Klooni repo: git clone https://github.com/Gretevallo/MeediaRiiul.git

Liigu kausta: cd MeediaRiiul

Paigalda sõltuvused: python -m pip install -r requirements.txt

Kui mõni teek puudub, paigalda käsitsi: python -m pip install flask python -m pip install flask-login python -m pip install flask-bcrypt python -m pip install pandas

Käivita: python app.py

Ava brauseris: http://127.0.0.1:5000 www.python.org
===========================================
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pandas as pd
import os
from meediariiul import KogumikuHaldur

app = Flask(__name__)
app.secret_key = "väga_salajane_võti_12345"  # vajalik flash-sõnumite jaoks
bcrypt = Bcrypt(app)

def get_user_haldur():
    return KogumikuHaldur(user_id=current_user.id)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # kui proovib minna kaitstud lehele → suunatakse loginile

from werkzeug.utils import secure_filename
UPLOAD_FOLDER = "static/profiilipildid"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}

USERS_FILE = "users.csv"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["id", "kasutajanimi", "parool"]).to_csv(USERS_FILE, index=False)

class User(UserMixin):
    def __init__(self, id, kasutajanimi, parool):
        self.id = id
        self.kasutajanimi = kasutajanimi
        self.parool = parool


haldur = KogumikuHaldur()  # kasutab data.csv

ŽANRID = [
    "Fantaasia", "Ulme", "Krimi", "Romaan", "Ajalugu", "Põnevik", "Draama",
    "Horror", "Seiklus", "Teadus", "Biograafia", "Animatsioon", "Dokumentaal",
    "Komöödia", "Müsteerium", "Muu"
]

@app.route("/")
@login_required
def avaleht():
    df = get_user_haldur().loe_koik()

    # --- Viimati lisatud ---
    latest = []
    if not df.empty:
        df2 = df.copy()
        df2["kuupäev"] = pd.to_datetime(df2["kuupäev"], errors="coerce")
        df2 = df2.sort_values("kuupäev", ascending=False)
        latest = df2.head(3).to_dict(orient="records")

    # --- Top 3 hinnatud ---
    top3 = []
    if not df.empty:
        df3 = df.copy()
        df3["hinne"] = pd.to_numeric(df3["hinne"], errors="coerce")
        df3 = df3.dropna(subset=["hinne"])
        df3 = df3.sort_values("hinne", ascending=False)
        top3 = df3.head(3).to_dict(orient="records")

    # --- Progress ---
    total = len(df)
    done = (df["staatus"].str.lower() == "lopetatud").sum() if not df.empty else 0
    progress = round((done / total) * 100) if total > 0 else 0

    # --- Põhiarvud ---
    kokku = len(df)
    lopetatud = (df["staatus"].str.lower() == "lopetatud").sum()
    pooleli = (df["staatus"].str.lower() == "pooleli").sum()
    soovid = (df["staatus"].str.lower() == "soovinimekiri").sum()

    # --- Parim teos ---
    best = None
    if not df.empty:
        df["hinne"] = pd.to_numeric(df["hinne"], errors="coerce")
        lop_df = df[df["staatus"].str.lower() == "lõpetatud"]
        if not lop_df.empty:
            parim = lop_df.sort_values("hinne", ascending=False).iloc[0]
            best = {
                "pealkiri": parim["pealkiri"],
                "hinne": parim["hinne"],
                "tüüp": parim["meedia_tüüp"]
            }

    # --- Kuu võrdlus ---
    this_month = 0
    last_month = 0
    trend = "—"
    if not df.empty and "kuupäev" in df.columns:
        df2 = df.copy()
        df2["kuupäev"] = pd.to_datetime(df2["kuupäev"], errors="coerce")
        df2 = df2.dropna(subset=["kuupäev"])
        if not df2.empty:
            today = pd.Timestamp.today()
            this_month = len(df2[(df2["kuupäev"].dt.year == today.year) &
                                 (df2["kuupäev"].dt.month == today.month)])
            last_month = len(df2[(df2["kuupäev"].dt.year == (today.year if today.month > 1 else today.year - 1)) &
                                 (df2["kuupäev"].dt.month == (today.month - 1 if today.month > 1 else 12))])

            trend = (
                "⬆ Rohkem kui eelmisel kuul" if this_month > last_month else
                "⬇ Vähem kui eelmisel kuul" if this_month < last_month else
                "Sama palju kui eelmisel kuul"
            )

    # --- RETURN ÕIGES KOHAIS ---
    return render_template(
        "avaleht.html",
        kokku=kokku,
        lopetatud=lopetatud,
        pooleli=pooleli,
        soovid=soovid,
        top3=top3,
        latest=latest,
        this_month=this_month,
        last_month=last_month,
        trend=trend,
        done=done,
        total=total,
        progress=progress
    )







@app.route("/teos/<int:id>")
@login_required
def teos(id):
    teos = get_user_haldur().leia_teos(id)
    if not teos:
        flash("Teost ei leitud!", "error")
        return redirect(url_for("kogu"))
    return render_template("teos.html", teos=teos)



@app.route("/lisa", methods=["GET", "POST"])
@login_required
def lisa():
    if request.method == "POST":
        zanr = request.form.get("žanr")
        if zanr == "Muu":
            zanr = request.form.get("zanr_custom")

        # --- KUUPÄEVA KONTROLL ---
        kuup_str = request.form.get("kuupäev", "").strip()

        if kuup_str:
            try:
                d = datetime.strptime(kuup_str, "%Y-%m-%d")
                if d.year < 1900 or d.year > 2100:
                    flash("Kuupäev peab olema vahemikus 1900–2100.", "error")
                    return redirect(url_for("lisa"))
            except ValueError:
                flash("Kuupäev on vigane. Kasuta kuupäeva valikut.", "error")
                return redirect(url_for("lisa"))

        # --- LISAMINE ---
        get_user_haldur().lisa_teos(
            request.form["pealkiri"],
            request.form["meedia_tüüp"],
            zanr,
            request.form.get("autor_või_režissöör"),
            request.form["staatus"],
            request.form.get("hinne"),
            request.form.get("arvamus"),
            request.form.get("kuupäev"),
            request.form.get("lisainfo"),
        )

        flash("Teos on lisatud!", "success")
        return redirect(url_for("lisa"))

    return render_template("lisateos.html", zanrid=ŽANRID)



@app.route("/kogu")
@login_required
def kogu():
    df = get_user_haldur().loe_koik()

    # --- OTSING ---
    otsi = request.args.get("otsi", "").strip().lower()

    if otsi:
        df = df[
            df["pealkiri"].str.lower().str.contains(otsi, na=False) |
            df["autor_või_režissöör"].str.lower().str.contains(otsi, na=False) |
            df["žanr"].str.lower().str.contains(otsi, na=False)
        ]

    # --- FILTRID ---
    tüüp_filter = request.args.get("tüüp", "kõik")
    staatus_filter = request.args.get("staatus", "kõik")
    hinne_filter = request.args.get("hinne", "kõik")
    zanr_filter = request.args.get("zanr", "kõik")

    if tüüp_filter != "kõik":
        df = df[df["meedia_tüüp"] == tüüp_filter]

    if staatus_filter != "kõik":
        df = df[df["staatus"] == staatus_filter]

    if hinne_filter != "kõik":
        try:
            df["hinne"] = pd.to_numeric(df["hinne"], errors="coerce")
            df = df[df["hinne"] >= float(hinne_filter)]
        except:
            pass

    if zanr_filter != "kõik":
        df = df[df["žanr"].str.lower() == zanr_filter.lower()]

    # --- SORT ---
    sort_col = request.args.get("sort")
    sort_dir = request.args.get("dir", "asc")

    if sort_col:
        if sort_col == "hinne":
            df["hinne"] = pd.to_numeric(df["hinne"], errors="coerce")
            df = df.sort_values("hinne", ascending=(sort_dir == "asc"))

        elif sort_col == "staatus":
            order = {"lõpetatud": 1, "pooleli": 2, "soovinimekiri": 3, "peatatud": 4}
            df["sort_staatus"] = df["staatus"].map(order)
            df = df.sort_values("sort_staatus", ascending=(sort_dir == "asc"))
            df = df.drop(columns=["sort_staatus"])

        else:
            df = df.sort_values(sort_col, ascending=(sort_dir == "asc"))

    # --- PAGINATION ---
    per_page = 10
    page = request.args.get("page", 1, type=int)
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    page_df = df.iloc[start:end]
    total_pages = (total + per_page - 1) // per_page if total else 1

    records = page_df.to_dict(orient="records")

    # Kuvavormistused
    tüüp_map = {"raamat": "Raamat", "film": "Film", "sari": "Sari"}
    staatus_map = {
        "lõpetatud": "Lõpetatud", "lopetatud": "Lõpetatud",
        "pooleli": "Pooleli", "soovinimekiri": "Soovinimekirjas", "peatatud": "Peatatud"
    }
    for r in records:
        r["meedia_tüüp"] = tüüp_map.get(r["meedia_tüüp"], r["meedia_tüüp"])
        r["staatus"] = staatus_map.get(r["staatus"], r["staatus"])

    zanrid = sorted({z for z in haldur.loe_koik()["žanr"] if z})

    return render_template(
        "kogumik.html",
        tabel=records,
        page=page,
        total_pages=total_pages,
        tüüp_filter=tüüp_filter,
        staatus_filter=staatus_filter,
        hinne_filter=hinne_filter,
        zanr_filter=zanr_filter,
        zanrid=zanrid,
        sort_col=sort_col,
        sort_dir=sort_dir
    )






@app.route("/soovid")
@login_required
def soovid():
    df = get_user_haldur().loe_koik()
    df = df[df["staatus"] == "soovinimekiri"]

    otsi = request.args.get("otsi", "").strip().lower()

    if otsi:
        df = df[
            df["pealkiri"].str.lower().str.contains(otsi, na=False) |
            df["autor_või_režissöör"].str.lower().str.contains(otsi, na=False) |
            df["žanr"].str.lower().str.contains(otsi, na=False)
        ]
    # tüübifilter
    tüüp_filter = request.args.get("filter", "kõik")
    if tüüp_filter != "kõik":
        df = df[df["meedia_tüüp"] == tüüp_filter]

    # --- PAGINATION ---
    per_page = 10
    page = request.args.get("page", 1, type=int)

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    page_df = df.iloc[start:end]

    total_pages = (total + per_page - 1) // per_page if total else 1

    records = page_df.to_dict(orient="records")

    # ilusad kuvaväärtused
    tüüp_map = {"raamat": "Raamat", "film": "Film", "sari": "Sari"}
    staatus_map = {
        "lõpetatud": "Lõpetatud",
        "lopetatud": "Lõpetatud",
        "pooleli": "Pooleli",
        "soovinimekiri": "Soovinimekirjas",
        "peatatud": "Peatatud"
    }

    for r in records:
        r["meedia_tüüp"] = tüüp_map.get(r["meedia_tüüp"], r["meedia_tüüp"])
        r["staatus"] = staatus_map.get(r["staatus"], r["staatus"])

    return render_template(
        "soovid.html",
        tabel=records,
        filter=tüüp_filter,   # alati string
        page=page,
        total_pages=total_pages
    )





@app.route("/statistika")
@login_required
def statistika():
    df = get_user_haldur().loe_koik().copy()

    # --- NORMALISEERI STAATUS ---
    df["staatus"] = (
        df["staatus"]
        .str.strip()
        .str.lower()
        .str.replace("lopetatud", "lõpetatud")
    )

    kokku = len(df)
    lopetatud = (df["staatus"] == "lõpetatud").sum()
    pooleli = (df["staatus"] == "pooleli").sum()
    soovid = (df["staatus"] == "soovinimekiri").sum()

    df["hinne"] = pd.to_numeric(df["hinne"], errors="coerce")
    keskmine_hinne = round(df["hinne"].mean(), 2) if df["hinne"].notna().any() else 0

    return render_template(
        "statistika.html",
        kokku=kokku,
        lopetatud=lopetatud,
        pooleli=pooleli,
        soovid=soovid,
        keskmine_hinne=keskmine_hinne,
        statistika={
            "raamat": {"pealkiri": "📚 Raamatud", "arv": (df["meedia_tüüp"]=="raamat").sum(),
                       "keskmine": round(df[df["meedia_tüüp"]=="raamat"]["hinne"].mean(), 2) if (df["meedia_tüüp"]=="raamat").any() else "—"},
            "film":   {"pealkiri": "🎬 Filmid", "arv": (df["meedia_tüüp"]=="film").sum(),
                       "keskmine": round(df[df["meedia_tüüp"]=="film"]["hinne"].mean(), 2) if (df["meedia_tüüp"]=="film").any() else "—"},
            "sari":   {"pealkiri": "📺 Sarjad", "arv": (df["meedia_tüüp"]=="sari").sum(),
                       "keskmine": round(df[df["meedia_tüüp"]=="sari"]["hinne"].mean(), 2) if (df["meedia_tüüp"]=="sari").any() else "—"},
        }
    )



@app.route("/muuda/<int:id>", methods=["GET", "POST"])
@login_required
def muuda(id):
    teos = get_user_haldur().leia_teos(id)
    if not teos:
        flash("Teost ei leitud!", "error")
        return redirect(url_for("kogu"))

    if request.method == "POST":

        # --- KUU PÄEVA KONTROLL ---
        kuup_str = request.form.get("kuupäev", "").strip()

        if kuup_str:
            try:
                d = datetime.strptime(kuup_str, "%Y-%m-%d")
                if d.year < 1900 or d.year > 2100:
                    flash("Kuupäev peab olema vahemikus 1900–2100.", "error")
                    return redirect(url_for("muuda", id=id))
            except ValueError:
                flash("Kuupäev on vigane. Kasuta kuupäeva valikut.", "error")
                return redirect(url_for("muuda", id=id))

        # --- MUUDATUSED ---
        muudatused = {k: request.form.get(k) for k in [
            "pealkiri", "meedia_tüüp", "žanr", "autor_või_režissöör",
            "staatus", "hinne", "arvamus", "kuupäev", "lisainfo"
        ]}

        haldur.uuenda_teos(id, muudatused)
        flash("Muudatused salvestatud!", "success")
        return redirect(url_for("kogu"))

    return render_template("muuda.html", teos=teos, zanrid=ŽANRID)


@app.route("/kustuta/<int:id>")
@login_required
def kustuta(id):
    if get_user_haldur().kustuta_teos(id):
        flash("Teos kustutati!", "success")
    else:
        flash("Sellist teost ei leitud!", "error")
    return redirect(url_for("kogu"))

@login_manager.user_loader
def load_user(user_id):
    df = pd.read_csv(USERS_FILE, dtype=str)
    kasutaja = df[df["id"] == str(user_id)]
    if kasutaja.empty:
        return None
    row = kasutaja.iloc[0]
    return User(row["id"], row["kasutajanimi"], row["parool"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        kasutajanimi = request.form["kasutajanimi"]
        parool = request.form["parool"]

        df = pd.read_csv(USERS_FILE, dtype=str)
        if kasutajanimi in df["kasutajanimi"].values:
            flash("Selline kasutajanimi on juba olemas!", "error")
            return redirect(url_for("register"))

        hash_pw = bcrypt.generate_password_hash(parool).decode("utf-8")

        new_id = 1 if df.empty else int(df["id"].astype(int).max()) + 1
        df.loc[len(df)] = [new_id, kasutajanimi, hash_pw]
        df.to_csv(USERS_FILE, index=False)

        flash("Konto loodud! Logi sisse.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        kasutajanimi = request.form["kasutajanimi"]
        parool = request.form["parool"]

        df = pd.read_csv(USERS_FILE, dtype=str)
        r = df[df["kasutajanimi"] == kasutajanimi]

        if r.empty or not bcrypt.check_password_hash(r.iloc[0]["parool"], parool):
            flash("Vale kasutajanimi või parool", "error")
            return redirect(url_for("login"))

        kasutaja = User(r.iloc[0]["id"], kasutajanimi, r.iloc[0]["parool"])
        login_user(kasutaja)
        return redirect(url_for("avaleht"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Oled välja logitud.", "success")
    return redirect(url_for("login"))

@app.route("/profiil", methods=["GET", "POST"])
@login_required
def profiil():
    df = pd.read_csv(USERS_FILE, dtype=str)
    row = df[df["id"] == str(current_user.id)].iloc[0]
    kasutajanimi = row["kasutajanimi"]

    if request.method == "POST":
        muudeti_midagi = False

        # kasutajanimi
        uus_nimi = request.form.get("kasutajanimi", "").strip()
        if uus_nimi and uus_nimi != kasutajanimi:
            if uus_nimi in df["kasutajanimi"].values:
                flash("Selline kasutajanimi on juba olemas.", "error")
                return redirect(url_for("profiil"))
            df.loc[df["id"] == str(current_user.id), "kasutajanimi"] = uus_nimi
            login_user(User(current_user.id, uus_nimi, row["parool"]))
            muudeti_midagi = True

        # parool
        vana = request.form.get("vana_parool", "")
        uus = request.form.get("uus_parool", "")
        kordus = request.form.get("uus_parool_kaks", "")

        if vana or uus or kordus:
            if not bcrypt.check_password_hash(row["parool"], vana):
                flash("Vale praegune parool.", "error")
                return redirect(url_for("profiil"))
            if uus != kordus:
                flash("Uued paroolid ei ühti.", "error")
                return redirect(url_for("profiil"))

            hash_pw = bcrypt.generate_password_hash(uus).decode("utf-8")
            df.loc[df["id"] == str(current_user.id), "parool"] = hash_pw
            muudeti_midagi = True

        if muudeti_midagi:
            df.to_csv(USERS_FILE, index=False)
            flash("Profiil uuendatud!", "success")

        return redirect(url_for("profiil"))

    return render_template("profiil.html", kasutajanimi=kasutajanimi)




if __name__ == "__main__":
    app.run(debug=True)






