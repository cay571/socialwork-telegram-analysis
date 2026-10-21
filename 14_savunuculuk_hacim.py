# -*- coding: utf-8 -*-
"""
14_savunuculuk_hacim.py
Aylik mesaj hacmi ile savunuculuk payi arasindaki iliski.
Girdi : loglar/savunuculuk_aylik.csv, loglar/zaman_rapor.json
Cikti : loglar/savunuculuk_hacim.json
"""
import json

import pandas as pd

d = pd.read_csv("loglar/savunuculuk_aylik.csv")
with open("loglar/zaman_rapor.json", encoding="utf-8") as f:
    z = json.load(f)
olagandisi = [a["ay"] for a in z["olagandisi_aylar"]]

rho = float(d["mesaj"].corr(d["sinyal_dar_oran"], method="spearman"))
icinde = d[d["ay"].isin(olagandisi)]["sinyal_dar_oran"]
disinda = d[~d["ay"].isin(olagandisi)]["sinyal_dar_oran"]

yil = d.assign(yil=d["ay"].str[:4]).groupby("yil")[["mesaj", "sinyal_dar"]].sum()
yil["oran_yuzde"] = (100 * yil["sinyal_dar"] / yil["mesaj"]).round(2)

sonuc = {
    "ay_sayisi": len(d),
    "spearman_rho_hacim_savunuculuk": round(rho, 3),
    "olagandisi_aylar": olagandisi,
    "olagandisi_ay_ortalamasi_yuzde": round(float(icinde.mean()), 2),
    "diger_ay_ortalamasi_yuzde": round(float(disinda.mean()), 2),
    "yillik_oran_yuzde": yil["oran_yuzde"].to_dict(),
}

print(json.dumps(sonuc, ensure_ascii=False, indent=2))
with open("loglar/savunuculuk_hacim.json", "w", encoding="utf-8") as f:
    json.dump(sonuc, f, ensure_ascii=False, indent=2)
print("\nYazildi: loglar/savunuculuk_hacim.json")