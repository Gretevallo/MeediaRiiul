import pandas as pd

# --- Andmete lugemine ja puhastamine ---
def loe_andmed(failitee: str) -> pd.DataFrame:
    """Loeb CSV-faili ja puhastab veerunimed."""
    df = pd.read_csv(
        failitee,
        sep=",",
        engine="python",
        encoding="utf-8",
        dtype=str,
        on_bad_lines="skip"
    ).fillna("")
    
    # Puhastame veerunimed
    df.columns = (
        df.columns
        .str.replace('\ufeff', '', regex=True)
        .str.strip()
        .str.lower()
    )
    
    return df


# --- Soovide kuvamine ---
def kuva_soovid(df: pd.DataFrame) -> None:
    """Kuvab kõik kirjed, mille staatus on 'soovib'."""
    if "staatus" not in df.columns:
        print("❌ Failis pole veergu nimega 'staatus'.")
        return
    
    df["staatus"] = df["staatus"].astype(str).str.strip().str.lower()
    print("Staatus veeru unikaalsed väärtused:", df["staatus"].unique())
    
    soovid = df[df["staatus"] == "soovib"]
    if soovid.empty:
        print("❌ Soovide nimekiri on tühi.")
    else:
        print("\n✅ Soovide nimekiri:")
        veerud = [col for col in ["id", "pealkiri", "tüüp", "žanr"] if col in soovid.columns]
        print(soovid[veerud].to_string(index=False))


# --- Statistika ---
def arvuta_statistika(df: pd.DataFrame) -> None:
    """Arvutab ja kuvab loetud raamatute statistika."""
    if "hinnang" not in df.columns or "tüüp" not in df.columns or "staatus" not in df.columns:
        print("\n⚠️ Statistikat ei saa arvutada – mõni vajalik veerg puudub.")
        return

    df["hinnang"] = pd.to_numeric(df["hinnang"], errors="coerce")
    
    loetud_raamatud = df[
        (df["tüüp"].str.strip().str.lower() == "raamat") &
        (df["staatus"].str.strip().str.lower() == "lõpetatud")
    ]
    
    loetud_arv = len(loetud_raamatud)
    keskmine_hinnang = loetud_raamatud["hinnang"].mean()
    
    print("\n📚 Statistika")
    print(f"Loetud raamatuid kokku: {loetud_arv}")
    print(f"Keskmine hinnang: {keskmine_hinnang:.2f}" if loetud_arv > 0 else "Keskmine hinnang: — (pole loetud raamatuid)")


# --- Peaprogramm ---
def main():
    df = loe_andmed("data.csv")
    
    print("\n--- Kontroll ---")
    print("Veerunimed:", df.columns.tolist())
    print(df.head(), "\n")
    
    kuva_soovid(df)
    arvuta_statistika(df)


if __name__ == "__main__":
    main()

