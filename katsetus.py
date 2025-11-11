import tkinter as tk
from tkinter import ttk, messagebox
from meediariiul import KogumikuHaldur, kuva_soovinimekiri, arvuta_statistika
import pandas as pd
import io
import sys

class MeediariiulApp:
    def __init__(self, master):
        self.master = master
        master.title("🎬 Meediariiul")
        master.geometry("700x500")

        self.haldur = KogumikuHaldur()

        # --- Menüü ---
        menüü = tk.Menu(master)
        master.config(menu=menüü)

        failimenüü = tk.Menu(menüü, tearoff=0)
        failimenüü.add_command(label="Lisa uus teos", command=self.lisa_teos_aken)
        failimenüü.add_command(label="Vaata soovinimekirja", command=self.kuva_soovid)
        failimenüü.add_command(label="Kuva statistika", command=self.kuva_statistika)
        failimenüü.add_separator()
        failimenüü.add_command(label="Välju", command=master.quit)

        menüü.add_cascade(label="Tegevused", menu=failimenüü)

        # --- Kuvamisala ---
        self.väljund = tk.Text(master, wrap="word", font=("Consolas", 10))
        self.väljund.pack(fill="both", expand=True, padx=10, pady=10)

        self.uuenda_väljund("Tere tulemast Meediariiulisse!")

    def uuenda_väljund(self, tekst):
        self.väljund.delete("1.0", tk.END)
        self.väljund.insert(tk.END, tekst)

    def lisa_teos_aken(self):
        aken = tk.Toplevel(self.master)
        aken.title("Lisa uus teos")
        aken.geometry("400x400")

        väljad = {
            "Pealkiri": tk.Entry(aken),
            "Tüüp (raamat/film/sari)": tk.Entry(aken),
            "Žanr": tk.Entry(aken),
            "Autor või režissöör": tk.Entry(aken),
            "Staatus (lõpetatud/soovinimekiri/pooleli/peatatud)": tk.Entry(aken),
            "Hinne": tk.Entry(aken),
        }

        for i, (nimi, väli) in enumerate(väljad.items()):
            tk.Label(aken, text=nimi).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            väli.grid(row=i, column=1, padx=5, pady=3)

        def salvesta():
            try:
                teos = self.haldur.lisa_teos(
                    pealkiri=väljad["Pealkiri"].get(),
                    meedia_tüüp=väljad["Tüüp (raamat/film/sari)"].get(),
                    žanr=väljad["Žanr"].get(),
                    autor_või_režissöör=väljad["Autor või režissöör"].get(),
                    staatus=väljad["Staatus (lõpetatud/soovinimekiri/pooleli/peatatud)"].get(),
                    hinne=float(väljad["Hinne"].get()) if väljad["Hinne"].get() else None,
                )
                messagebox.showinfo("Salvestatud", f"✅ Teos lisatud (ID: {teos['id']})")
                aken.destroy()
                self.kuva_soovid()
            except Exception as e:
                messagebox.showerror("Viga", str(e))

        tk.Button(aken, text="Salvesta", command=salvesta, bg="#4CAF50", fg="white").grid(row=len(väljad)+1, column=0, columnspan=2, pady=10)

    def kuva_soovid(self):
        df = self.haldur.loe_koik()
        soovid = df[df["staatus"].str.lower() == "soovinimekiri"]
        if soovid.empty:
            self.uuenda_väljund("❌ Soovinimekiri on tühi.")
        else:
            self.uuenda_väljund(soovid.to_string(index=False))

    def kuva_statistika(self):
        df = self.haldur.loe_koik()
        # Suuname print() väljundi tekstiväljale
        vana_stdout = sys.stdout
        sys.stdout = io.StringIO()
        arvuta_statistika(df)
        tekst = sys.stdout.getvalue()
        sys.stdout = vana_stdout
        self.uuenda_väljund(tekst)


if __name__ == "__main__":
    root = tk.Tk()
    app = MeediariiulApp(root)
    root.mainloop()
