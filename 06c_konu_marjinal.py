#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06c_konu_marjinal.py - Iki kodlayicinin konu ve islev marjinal dagilimlari.

Tartismadaki "both coders independently placed employment first" iddiasinin
dayanagini uretir. Ortak satirlar uzerinde, her iki kodlayicinin kategori
siralamasini ayri ayri verir.

Cikti: loglar/konu_marjinal.json ve ekrana tablo
Kullanim: python 06c_konu_marjinal.py
"""

import json
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
CODE_DIR = BASE / "veri" / "kodlama"
LOG_DIR = BASE / "loglar"

GECERSIZ = {"?", "", "nan", "none", "naan", "NaN", "None"}


def oku(yol):
    if yol.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            return pd.read_excel(yol, sheet_name="kodlama")
        except Exception:
            return pd.read_excel(yol)
    return pd.read_csv(yol)


def tablolari_bul():
    """veri/kodlama altinda 'sira' sutunu olan butun tablolari okur."""
    bulunan = []
    for yol in sorted(CODE_DIR.iterdir()):
        if yol.suffix.lower() not in (".csv", ".xlsx", ".xlsm"):
            continue
        try:
            df = oku(yol)
        except Exception:
            continue
        if "sira" not in df.columns:
            continue
        bulunan.append((yol.name, df))
    return bulunan


def sutun_bul(tablolar, ad):
    """Verilen sutun adini tasiyan ilk tabloyu dondurur."""
    for isim, df in tablolar:
        if ad in df.columns:
            return isim, df[["sira", ad]].copy()
    return None, None


def temizle(s):
    return str(s).strip()


def dagilim(seri):
    sayim = Counter(temizle(x) for x in seri)
    for k in list(sayim):
        if k.lower() in GECERSIZ:
            del sayim[k]
    n = sum(sayim.values())
    return n, [
        {"kategori": k, "n": v, "yuzde": round(100 * v / n, 1)}
        for k, v in sorted(sayim.items(), key=lambda x: (-x[1], x[0]))
    ]


def main():
    tablolar = tablolari_bul()
    if not tablolar:
        raise SystemExit("veri/kodlama altinda 'sira' sutunlu tablo bulunamadi.")
    print("Okunan tablolar:", ", ".join(ad for ad, _ in tablolar), "\n")

    sonuc = {}
    for boyut in ("konu", "islev"):
        ad_m, makine = sutun_bul(tablolar, boyut + "_claude")
        ad_i, insan = sutun_bul(tablolar, boyut)
        if makine is None or insan is None:
            print(f"[{boyut}] sutun bulunamadi, atlandi "
                  f"(makine={ad_m}, insan={ad_i})")
            continue

        ortak = makine.merge(insan, on="sira").dropna()
        gecerli = ortak[
            ~ortak[boyut + "_claude"].map(lambda x: temizle(x).lower()).isin(GECERSIZ)
            & ~ortak[boyut].map(lambda x: temizle(x).lower()).isin(GECERSIZ)
        ]

        n1, d1 = dagilim(gecerli[boyut + "_claude"])
        n2, d2 = dagilim(gecerli[boyut])
        sonuc[boyut] = {
            "kaynak_makine": ad_m,
            "kaynak_insan": ad_i,
            "ortak_satir": int(len(ortak)),
            "gecerli_satir": int(len(gecerli)),
            "kodlayici_1_ilk_tur": {"n": n1, "dagilim": d1},
            "kodlayici_2_bagimsiz": {"n": n2, "dagilim": d2},
            "ilk_siradaki_ayni_mi": bool(d1 and d2 and d1[0]["kategori"] == d2[0]["kategori"]),
        }

        print(f"=== {boyut.upper()} (ortak {len(ortak)}, gecerli {len(gecerli)}) ===")
        print(f"{'kategori':28s} {'kod.1':>12s}   {'kod.2':>12s}")
        kats = sorted({x["kategori"] for x in d1} | {x["kategori"] for x in d2})
        h1 = {x["kategori"]: x for x in d1}
        h2 = {x["kategori"]: x for x in d2}
        for k in sorted(kats, key=lambda k: -(h1.get(k, {}).get("n", 0) + h2.get(k, {}).get("n", 0))):
            a = h1.get(k, {"n": 0, "yuzde": 0.0})
            b = h2.get(k, {"n": 0, "yuzde": 0.0})
            print(f"{k:28s} {a['n']:4d} (%{a['yuzde']:5.1f})   {b['n']:4d} (%{b['yuzde']:5.1f})")
        print(f"\n  kodlayici 1 ilk sira : {d1[0]['kategori']} (%{d1[0]['yuzde']})")
        print(f"  kodlayici 2 ilk sira : {d2[0]['kategori']} (%{d2[0]['yuzde']})")
        print(f"  IKISI AYNI MI        : {'EVET' if sonuc[boyut]['ilk_siradaki_ayni_mi'] else 'HAYIR'}\n")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "konu_marjinal.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Yazildi: loglar/konu_marjinal.json")


if __name__ == "__main__":
    main()