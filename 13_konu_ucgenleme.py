# -*- coding: utf-8 -*-
"""
13_konu_ucgenleme.py
Konu modeli bulgularini dogrular ve uretir:
  1. Dokuz tematik grubun yillik paylari (siniflanmis taban)
  2. Her yilin en buyuk grubu  -> "istihdam her yil ilk sirada" iddiasi
  3. Istihdam + sinav serisi    -> Ozet'teki 39.8 -> 64.6
  4. Mobilizasyon serisinin iki yontemle karsilastirmasi -> Pearson r
Girdi : loglar/konu_etiketleri.csv, loglar/konu_yillik.csv, loglar/islev_dagilim.csv
Cikti : loglar/ucgenleme.json
"""
import json

import pandas as pd

YILLAR = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
ISTIHDAM_GRUPLARI = ["alım ve istihdam", "sınav, puan ve tercih"]


def oku(yol):
    for kod in ("utf-8", "utf-8-sig", "cp1254"):
        try:
            return pd.read_csv(yol, encoding=kod)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Kodlama cozulemedi: {yol}")


et = oku("loglar/konu_etiketleri.csv")
ky = oku("loglar/konu_yillik.csv")
clf = oku("loglar/islev_dagilim.csv")

et["Topic"] = et["Topic"].astype(int)
et["aile"] = et["aile"].astype(str).str.strip()
ky["konu"] = ky["konu"].astype(int)
clf["yil"] = clf["yil"].astype(str)


def taban(y):
    """O yilin siniflanmis mesaj payi (yuzde)."""
    return 100.0 - float(ky.loc[ky["konu"] == -1, y].iloc[0])


def pay(konular, y):
    """Verilen konularin o yildaki payi, siniflanmis taban uzerinden."""
    toplam = float(ky.loc[ky["konu"].isin(konular), y].sum())
    return round(100.0 * toplam / taban(y), 1)


# 1. Dokuz grubun yillik paylari
gruplar = sorted(set(et.loc[et["Topic"] != -1, "aile"]))
gt = pd.DataFrame(
    {g: {y: pay(et.loc[et["aile"] == g, "Topic"].tolist(), y) for y in YILLAR} for g in gruplar}
).T[YILLAR]

print("Grup paylari (siniflanmis taban, %):")
print(gt.to_string())

# 2. Her yilin en buyuk grubu
enbuyuk = gt.idxmax().to_dict()
print("\nHer yilin en buyuk grubu:")
for y in YILLAR:
    print(f"  {y}: {enbuyuk[y]}  (%{gt.loc[enbuyuk[y], y]})")

# 3. Istihdam + sinav serisi
ist_konulari = et.loc[et["aile"].isin(ISTIHDAM_GRUPLARI), "Topic"].tolist()
ist_seri = {y: pay(ist_konulari, y) for y in YILLAR}
print("\nIstihdam + sinav (siniflanmis taban):")
for y in YILLAR:
    print(f"  {y}: %{ist_seri[y]}")

# 4. Mobilizasyon, iki yontem
mob_konulari = et.loc[et["aile"] == "mobilizasyon", "Topic"].tolist()
print(f"\nMobilizasyon konulari: {sorted(mob_konulari)}")

a = clf.set_index("yil")["mobilizasyon"].reindex(YILLAR).astype(float)
b = pd.Series({y: pay(mob_konulari, y) for y in YILLAR}).reindex(YILLAR)
karsilastirma = pd.DataFrame({"siniflandirici": a, "konu_modeli": b})
r = float(karsilastirma["siniflandirici"].corr(karsilastirma["konu_modeli"]))

print("\nMobilizasyon serisi:")
print(karsilastirma.to_string())
print(f"\nPearson r = {r:.3f}")
print("Not: iki serinin tabanlari farkli (siniflandirici tum mesajlar,")
print("     konu modeli siniflanmis mesajlar). Karsilastirma seviye degil, yon uzerine.")

with open("loglar/ucgenleme.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "grup_paylari": {g: gt.loc[g].to_dict() for g in gt.index},
            "en_buyuk_grup": enbuyuk,
            "istihdam_sinav_serisi": ist_seri,
            "mobilizasyon_konulari": sorted(mob_konulari),
            "mobilizasyon_siniflandirici": a.to_dict(),
            "mobilizasyon_konu_modeli": b.to_dict(),
            "pearson_r": round(r, 3),
        },
        f,
        ensure_ascii=False,
        indent=2,
    )
print("\nYazildi: loglar/ucgenleme.json")