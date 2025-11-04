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

    # --- Faili kontroll ja haldus ---

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

        # ID veeru puhastus
        if not df.empty:
            with pd.option_context("mode.chained_assignment", None):
                df["id"] = pd.to_numeric(df["id"], errors="ignore")

        return df[VEERUD].fillna("")

    def _kirjuta_df(self, df: pd.DataFrame) -> None:
        """Salvestab DataFrame'i CSV-faili."""
        df.to_csv(self.faili_nimi, index=False)

    def _uus_id(self) -> int:
        """Genereerib uue ID väärtuse."""
        df = self._loe_df()
        if df.empty:
