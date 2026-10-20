# -*- coding: utf-8 -*-
"""
06b_islev_kappa.py
Islev ve konu boyutunda kodlayicilar arasi uyum (Cohen kappa).
Girdi : veri/kodlama/islev_konu_insan.xlsx  (sira, tarih, metin, islev, konu)
        veri/kodlama/claude_islev_konu.csv  (sira, islev_claude, konu_claude)
Cikti : loglar/islev_kappa.json
Not   : Kodlayicinin karar veremedigi satirlar ('?') kod kitabindaki
        5. karar kuralina gore hesaptan dislanir.
"""
import json
import os

import pandas as pd

GECERSIZ = {"?", "", "nan", "None", "NaN"}

DORT = {
    "bilgi_talebi": "bilgi_talebi",
    "bilgi_verme": "bilgi_duyuru",
    "duyuru": "bilgi_duyuru",
    "mobilizasyon": "mobilizasyon",
    "degerlendirme": "yorum_sohbet",
    "duygu_destek": "yorum_sohbet",
    "sohbet": "yorum_sohbet",
    "diger": "yorum_sohbet",
}


def kappa(a, b):
    """Iki kodlayici, cok kategori icin Cohen kappa."""
    a = [str(x) for x in a]
    b = [str(x) for x in b]
    n = len(a)
    cats = sorted(set(a) | set(b))
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(k) / n) * (b.count(k) / n) for k in cats)
    return (po - pe) / (1 - pe), po * 100, n


def temizle(df, insan, makine):
    """Iki kolonu metne cevirir, bos ve '?' satirlari atar."""
    s = df[[insan, makine]].copy().dropna()
    for col in (insan, makine):
        s[col] = s[col].astype(str).str.strip()
    return s[~s[insan].isin(GECERSIZ) & ~s[makine].isin(GECERSIZ)]


h = pd.read_excel("veri/kodlama/islev_konu_insan.xlsx")
c = pd.read_csv("veri/kodlama/claude_islev_konu.csv")
m = h.merge(c, on="sira", how="inner")
print(f"Ortak satir: {len(m)}")

sonuc = {"ortak_satir": len(m)}

s = temizle(m, "islev", "islev_claude")
k8, po8, n8 = kappa(s["islev"], s["islev_claude"])
print(f"Islev 8 kategori : kappa={k8:.3f}  uyum %{po8:.1f}  n={n8}  (dislanan {len(m) - n8})")
sonuc["islev_sekiz"] = {"kappa": round(k8, 3), "uyum_yuzde": round(po8, 1), "n": n8}

k4, po4, n4 = kappa(
    s["islev"].map(lambda x: DORT.get(x, x)),
    s["islev_claude"].map(lambda x: DORT.get(x, x)),
)
print(f"Islev 4 kategori : kappa={k4:.3f}  uyum %{po4:.1f}  n={n4}")
sonuc["islev_dort"] = {"kappa": round(k4, 3), "uyum_yuzde": round(po4, 1), "n": n4}

t = temizle(m, "konu", "konu_claude")
kt, pot, nt = kappa(t["konu"], t["konu_claude"])
print(f"Konu             : kappa={kt:.3f}  uyum %{pot:.1f}  n={nt}  (dislanan {len(m) - nt})")
sonuc["konu"] = {"kappa": round(kt, 3), "uyum_yuzde": round(pot, 1), "n": nt}

os.makedirs("loglar", exist_ok=True)
with open("loglar/islev_kappa.json", "w", encoding="utf-8") as f:
    json.dump(sonuc, f, ensure_ascii=False, indent=2)
print("\nYazildi: loglar/islev_kappa.json")