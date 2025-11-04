import os
import pandas as pd
from typing import Optional, List, Dict, Any

VAIKIMISI_FAIL = "data.csv"
VEERUD = [
    "id", "pealkiri", "meedia_tüüp", "žanr", "autor_või_režissöör",
    "staatus", "hinne", "arvamus", "kuupäev", "lisainfo"
]

LUBATUD_TÜÜBID = {"raamat", "film", "sari"}
LUBATUD_STAATUSED = {"lõpetatud", "soovinimekiri", "pooleli", "peatatud"}


class KogumikuHaldur:
    """Kogumiku haldur võimaldab CSV-failis olevate teoste lisamist, muutmist ja otsimist."""

    def __init__(self, faili_nimi: str = VAIKIMISI_FAIL):
        self.faili_nimi = faili_nimi
        self._tagada_fail()

    def _tagada_fail(self) -> None:
        """Loob tühja faili, kui seda pole olemas."""
        if not os.path.exists(self.faili_nimi):
            pd.DataFrame(columns=VEERUD).to_csv(self.faili_nimi, index=False)

    def _loe_df(self) -> pd.DataFrame:
        """Loeb CSV-faili ja tagab vajalike veergude olemasolu."""
        df = pd.read_csv(self.faili_nimi, dtype=str)
        for v in VEERUD:
            if v not in df.columns:
                df[v] = pd.NA
        return df[VEERUD].fillna("")

    def _kirjuta_df(self, df: pd.DataFrame) -> None:
        """Salvestab DataFrame'i CSV-faili."""
        df.to_csv(self.faili_nimi, index=False)

    def _uus_id(self) -> int:
        """Genereerib uue ID väärtuse."""
        df = self._loe_df()
        if df.empty:
            return 1
        try:
            return int(df["id"].astype(float).max()) + 1
        except Exception:
            return len(df) + 1

    # --- CRUD ---

    def lisa_teos(
        self,
        pealkiri: str,
        meedia_tüüp: str,
        žanr: Optional[str] = None,
        autor_või_režissöör: Optional[str] = None,
        staatus: str = "soovinimekiri",
        hinne: Optional[float] = None,
        arvamus: Optional[str] = None,
        kuupäev: Optional[str] = None,
        lisainfo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lisa uus teos kogumikku."""
        if not pealkiri:
            raise ValueError("Pealkiri on kohustuslik väli.")

        tüüp = meedia_tüüp.strip().lower()
        if tüüp not in LUBATUD_TÜÜBID:
            raise ValueError(f"Meedia tüüp peab olema üks järgmistest: {LUBATUD_TÜÜBID}")

        staatus = staatus.strip().lower()
        if staatus not in LUBATUD_STAATUSED:
            raise ValueError(f"Staatus peab olema üks järgmistest: {LUBATUD_STAATUSED}")

        uus_id = self._uus_id()
        teos = {
            "id": uus_id,
            "pealkiri": pealkiri.strip(),
            "meedia_tüüp": tüüp,
            "žanr": žanr or "",
            "autor_või_režissöör": autor_või_režissöör or "",
            "staatus": staatus,
            "hinne": float(hinne) if hinne is not None else "",
            "arvamus": arvamus or "",
            "kuupäev": kuupäev or "",
            "lisainfo": lisainfo or "",
        }

        df = self._loe_df()
        df = pd.concat([df, pd.DataFrame([teos])], ignore_index=True)
        self._kirjuta_df(df)
        return teos

    def loe_koik(self) -> pd.DataFrame:
        """Tagasta kogu kogumik andmetabelina."""
        return self._loe_df()


# --- LISAFUNKTSIOONID VÄLJASTAMISEKS JA STATISTIKAKS ---

def kuva_soovinimekiri(df: pd.DataFrame) -> None:
    """Kuvab kõik teosed, mille staatus on 'soovinimekiri'."""
    soovid = df[df["staatus"].str.lower() == "soovinimekiri"]
    if soovid.empty:
        print("❌ Soovinimekiri on tühi.")
    else:
        print("\n✅ Soovinimekiri:")
        veerud = [c for c in ["id", "pealkiri", "meedia_tüüp", "žanr"] if c in df.columns]
        print(soovid[veerud].to_string(index=False))


def arvuta_statistika(df: pd.DataFrame) -> None:
    """Arvutab ja kuvab loetud raamatute statistika."""
    df["hinne"] = pd.to_numeric(df["hinne"], errors="coerce")

    loetud = df[
        (df["meedia_tüüp"].str.lower() == "raamat")
        & (df["staatus"].str.lower() == "lõpetatud")
    ]

    loetud_arv = len(loetud)
    keskmine_hinne = loetud["hinne"].mean()

    print("\n📚 Statistika")
    print(f"Loetud raamatuid kokku: {loetud_arv}")
    if loetud_arv > 0:
        print(f"Keskmine hinne: {keskmine_hinne:.2f}")
    else:
        print("Keskmine hinne: — (pole loetud raamatuid)")


# --- PEAPROGRAMM ---

def main():
    haldur = KogumikuHaldur()

    df = haldur.loe_koik()
    print("\n--- Kontroll ---")
    print("Veerunimed:", df.columns.tolist())
    print(df.head(), "\n")

    kuva_soovinimekiri(df)
    arvuta_statistika(df)


if __name__ == "__main__":
    main()
