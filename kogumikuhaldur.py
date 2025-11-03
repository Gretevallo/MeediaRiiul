import pandas as pd
import os
from typing import Optional, List, Dict, Any

VAIKIMISI_FAIL = "data.csv"
VEERUD = [
    "id",
    "pealkiri",
    "meedia_tüüp",
    "žanr",
    "autor_või_režissöör",
    "staatus",
    "hinne",
    "arvamus",
    "kuupäev",
    "lisainfo"
]

LUBATUD_TÜÜBID = {"raamat", "film", "sari"}
LUBATUD_STAATUSED = {"lõpetatud", "soovinimekiri", "pooleli", "peatatud"}

class KogumikuHaldur:
    def __init__(self, faili_nimi: str = VAIKIMISI_FAIL):
        self.faili_nimi = faili_nimi
        self._kontrolli_fail()
    
    #Loo fail, kui seda pole
    def _kontrolli_fail(self):
        if not os.path.exists(self.faili_nimi):
            df = pd.DataFrame(columns=VEERUD)
            df.to_csv(self.faili_nimi, index=False)
    
    #Andmete lugemine ning salvestamine
    def _loe_df(self) -> pd.DataFrame:
        df = pd.read_csv(self.faili_nimi, dtype=str)
        for v in VEERUD:
            if v not in df.columns:
                df[v] = pd.NA
        if not df.empty:
            try:
                df["id"] = df["id"].astype(int)
            except Exception:
                pass
        return df[VEERUD]

    def _kirjuta_df(self, df: pd.DataFrame):
        df.to_csv(self.faili_nimi, index=False)

    def _uus_id(self) -> int:
        df = self._loe_df()
        if df.empty:
            return 1
        try:
            return int(df["id"].max()) + 1
        except Exception:
            return len(df) + 1
    
    #CRUD - loo, loe, uuenda, kustuta
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
            valik = df[df["id"] == int(teose_id)]
            if valik.empty:
                return None
            rida = valik.iloc[0].to_dict()
            try:
                rida["id"] = int(rida["id"])
            except Exception:
                pass
            try:
                rida["hinne"] = float(rida["hinne"]) if rida["hinne"] != "" else None
            except Exception:
                rida["hinne"] = None
            return rida

        def uuenda_teos(self, teose_id: int, muudatused: Dict[str, Any]) -> bool:
            """Uuenda olemasoleva teose välju."""
            if "id" in muudatused:
                muudatused.pop("id")
            df = self._loe_df()
            mask = df["id"] == int(teose_id)
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
            df = df[df["id"] != int(teose_id)]
            if len(df) == enne:
                return False
            self._kirjuta_df(df)
            return True

    #Otsimine ning filtreerimine
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
