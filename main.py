import pandas as pd
import matplotlib.pyplot as plt

# Loeme faili, lubame lisakomad ja eemaldame tühjad veerud
df = pd.read_csv(
    "data.csv",
    sep=",",
    engine="python",
    encoding="utf-8",
    dtype=str,
    on_bad_lines="skip"  # ignoreerib liialt pikki ridu
).fillna("")

# Puhastame veerunimed
df.columns = df.columns.str.replace('\ufeff', '', regex=True)
df.columns = df.columns.str.strip().str.lower()

print("\n--- Kontroll ---")
print("Veerunimed:", df.columns.tolist())
print(df.head(), "\n")

# Kontrollime, et 'staatus' veerg on olemas
if "staatus" not in df.columns:
    print("❌ Failis pole veergu nimega 'staatus'.")
else:
    # Puhastame väärtused
    df["staatus"] = df["staatus"].astype(str).str.strip().str.lower()
    print("Staatus veeru unikaalsed väärtused:", df["staatus"].unique())

    # Filtreerime soovitud kirjed
    soovid = df[df["staatus"] == "soovib"]

    if soovid.empty:
        print("❌ Soovide nimekiri on tühi.")
    else:
        print("\n✅ Soovide nimekiri:")
        print(soovid[["id", "pealkiri", "tüüp", "žanr"]].to_string(index=False))


def arvuta_statistika(df):
    # Puhastame hinnangu veeru arvudeks
    df["hinnang"] = pd.to_numeric(df["hinnang"], errors="coerce")
    
    # Filtreerime ainult lõpetatud raamatud
    loetud_raamatud = df[
        (df["tüüp"].str.strip().str.lower() == "raamat") &
        (df["staatus"].str.strip().str.lower() == "lõpetatud")
    ]
    
    loetud_arv = len(loetud_raamatud)
    keskmine_hinnang = loetud_raamatud["hinnang"].mean()
    
    print("\n📚 Statistika")
    print(f"Loetud raamatuid kokku: {loetud_arv}")
    if loetud_arv > 0:
        print(f"Keskmine hinnang: {keskmine_hinnang:.2f}")
    else:
        print("Keskmine hinnang: — (pole loetud raamatuid)")

arvuta_statistika(df)
