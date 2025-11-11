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

    def leia_teos(self, teose_id: int) -> Optional[Dict[str, Any]]:
        """Leia teos ID järgi."""
        df = self._loe_df()
        valik = df[df["id"].astype(str) == str(teose_id)]
        if valik.empty:
            return None
        rida = valik.iloc[0].to_dict()
        if rida.get("hinne"):
            try:
                rida["hinne"] = float(rida["hinne"])
            except ValueError:
                rida["hinne"] = None
        return rida

    def uuenda_teos(self, teose_id: int, muudatused: Dict[str, Any]) -> bool:
        """Uuenda olemasoleva teose andmeid."""
        df = self._loe_df()
        mask = df["id"].astype(str) == str(teose_id)
        if not mask.any():
            return False

        i = df.index[mask][0]
        for võti, väärtus in muudatused.items():
            if võti not in VEERUD:
                continue
            if võti == "meedia_tüüp" and väärtus:
                t = väärtus.strip().lower()
                if t not in LUBATUD_TÜÜBID:
                    raise ValueError(f"Meedia tüüp peab olema üks järgmistest: {LUBATUD_TÜÜBID}")
                df.at[i, võti] = t
                continue
            if võti == "staatus" and väärtus:
                s = väärtus.strip().lower()
                if s not in LUBATUD_STAATUSED:
                    raise ValueError(f"Staatus peab olema üks järgmistest: {LUBATUD_STAATUSED}")
                df.at[i, võti] = s
                continue
            if võti == "hinne":
                df.at[i, võti] = float(väärtus) if väärtus not in ("", None) else ""
                continue
            df.at[i, võti] = str(väärtus) if väärtus is not None else ""
        self._kirjuta_df(df)
        return True

    def kustuta_teos(self, teose_id: int) -> bool:
        """Kustuta teos ID järgi."""
        df = self._loe_df()
        enne = len(df)
        df = df[df["id"].astype(str) != str(teose_id)]
        if len(df) == enne:
            return False
        self._kirjuta_df(df)
        return True

    def otsi_ja_filtreeri(
        self,
        pealkiri: Optional[str] = None,
        meedia_tüübid: Optional[List[str]] = None,
        staatused: Optional[List[str]] = None,
        žanr: Optional[str] = None,
        autor: Optional[str] = None,
        aasta: Optional[int] = None,
    ) -> pd.DataFrame:
        """Otsi ja filtreeri teoseid erinevate kriteeriumite järgi."""
        df = self._loe_df()
        if df.empty:
            return df

        mask = pd.Series([True] * len(df), index=df.index)

        if pealkiri:
            mask &= df["pealkiri"].str.lower().str.contains(pealkiri.lower(), na=False)
        if meedia_tüübid:
            tüüpide_komplekt = {t.strip().lower() for t in meedia_tüübid}
            mask &= df["meedia_tüüp"].str.lower().isin(tüüpide_komplekt)
        if staatused:
            staatused_komplekt = {s.strip().lower() for s in staatused}
            mask &= df["staatus"].str.lower().isin(staatused_komplekt)
        if žanr:
            mask &= df["žanr"].str.lower().str.contains(žanr.lower(), na=False)
        if autor:
            mask &= df["autor_või_režissöör"].str.lower().str.contains(autor.lower(), na=False)
        if aasta:
            def sobib_aasta(v):
                try:
                    return str(aasta) == str(v)[:4]
                except Exception:
                    return False
            mask &= df["kuupäev"].apply(sobib_aasta)

        return df[mask].reset_index(drop=True)


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
    """Arvutab ja kuvab loetud raamatute, vaadatud filmide ja seriaalide statistika."""
    df["hinne"] = pd.to_numeric(df["hinne"], errors="coerce")

    kategooriad = {
        "raamat": "📚 Loetud raamatud",
        "film": "🎬 Vaadatud filmid",
        "seriaal": "📺 Vaadatud seriaalid"
    }

    print("\n⭐ Üldstatistika")

    for tüüp, pealkiri in kategooriad.items():
        valik = df[
            (df["meedia_tüüp"].str.lower() == tüüp)
            & (df["staatus"].str.lower() == "lõpetatud")
        ]

        arv = len(valik)
        keskmine = valik["hinne"].mean()

        print(f"\n{pealkiri}: {arv}")
        if arv > 0:
            print(f"Keskmine hinne: {keskmine:.2f}")
        else:
            print("Keskmine hinne: — (pole lõpetatud)")



# --- PEAPROGRAMM ---


def main():
    haldur = KogumikuHaldur()

    while True:
        print("\n--- Meediariiul ---")
        print("1. Lisa uus teos")
        print("2. Vaata soovinimekirja")
        print("3. Kuva statistika")
        print("4. Näita kõiki teoseid")
        print("5. Otsi ja filtreeri")
        print("6. Uuenda olemasoleva teose andmeid")
        print("7. Kustuta teos")
        print("8. Välju")

        valik = input("Vali tegevus (1-6): ").strip()

        if valik == "1":
            pealkiri = input("Pealkiri: ").strip()
            meedia_tüüp = input("Tüüp (raamat/film/sari): ").strip().lower()
            žanr = input("Žanr (valikuline): ").strip()
            autor = input("Autor või režissöör (valikuline): ").strip()
            staatus = input("Staatus (lõpetatud/soovinimekiri/pooleli/peatatud): ").strip().lower()
            hinne = input("Hinne (valikuline, 0-10): ").strip()
            arvamus = input("Arvamus (valikuline): ").strip()
            kuupäev = input("Kuupäev (nt 2025-11-04, valikuline): ").strip()
            lisainfo = input("Lisainfo (valikuline): ").strip()

            try:
                hinne_float = float(hinne) if hinne else None
                teos = haldur.lisa_teos(
                    pealkiri, meedia_tüüp, žanr, autor, staatus,
                    hinne_float, arvamus, kuupäev, lisainfo
                )
                print(f"\n✅ Teos lisatud (ID: {teos['id']})")
            except Exception as e:
                print(f"❌ Viga: {e}")

        elif valik == "2":
            df = haldur.loe_koik()
            kuva_soovinimekiri(df)

        elif valik == "3":
            df = haldur.loe_koik()
            arvuta_statistika(df)

        elif valik == "4":
            df = haldur.loe_koik()
            if df.empty:
                print("📂 Kogumik on tühi.")
            else:
                print(df.to_string(index=False))

        elif valik == "5":
            sõna = input("Sisesta teose pealkiri (või jäta tühjaks): ").strip()
            df = haldur.otsi_ja_filtreeri(pealkiri=sõna)
            if df.empty:
                print("❌ Midagi ei leitud.")
            else:
                print(df.to_string(index=False))

        elif valik == "6":
            try:
                teose_id = int(input("Sisesta teose ID, mida soovid muuta: ").strip())
                olemasolev = haldur.leia_teos(teose_id)
                if not olemasolev:
                    print("❌ Sellise ID-ga teost ei leitud.")
                    continue
        
                print("\nJäta väli tühjaks, kui ei soovi seda muuta.")
                muudatused = {}
                for väli in ["pealkiri", "meedia_tüüp", "žanr", "autor_või_režissöör",
                             "staatus", "hinne", "arvamus", "kuupäev", "lisainfo"]:
                    uus = input(f"{väli} (praegu: {olemasolev.get(väli, '')}): ").strip()
                    if uus != "":
                        muudatused[väli] = uus
        
                if haldur.uuenda_teos(teose_id, muudatused):
                    print("✅ Teose andmed on uuendatud.")
                else:
                    print("❌ Teost ei leitud.")
            except Exception as e:
                print(f"❌ Viga uuendamisel: {e}")
        
        elif valik == "7":
            try:
                teose_id = int(input("Sisesta teose ID, mida soovid kustutada: ").strip())
                kinnitus = input("Kas oled kindel, et soovid kustutada? (jah/ei): ").strip().lower()
                if kinnitus == "jah":
                    if haldur.kustuta_teos(teose_id):
                        print("🗑️ Teos on kustutatud.")
                    else:
                        print("❌ Sellise ID-ga teost ei leitud.")
                else:
                    print("Kustutamine katkestatud.")
            except Exception as e:
                print(f"❌ Viga kustutamisel: {e}")


        elif valik == "8":
            print("👋 Head aega!")
            break

        else:
            print("❌ Vigane valik. Proovi uuesti.")


if __name__ == "__main__":
    main()
