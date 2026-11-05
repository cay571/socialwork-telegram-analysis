#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
isim_tarama.py - Mesaj metinlerinde kişi adı geçip geçmediğini ÖLÇER. (sürüm 2)

Hiçbir şeyi değiştirmez, hiçbir mesaj metni yazdırmaz. Yalnızca sayar ve
eşleşen ad / ad-soyad çiftlerini sıklıklarıyla raporlar.

SÜRÜM 2'DE DÜZELTİLEN: 1. sürümdeki hitap kalıbı, "hocam" sözcüğünün önündeki
HER kelimeyi ad sayıyordu. Türkçede "hocam" tek başına hitaptır ("Evet hocam"),
bu yüzden sonuç büyük ölçüde yanlış pozitifti. Artık hitaptan önceki kelime
yalnızca ad listesinde varsa sayılır.

Üç ayrı bağlam ölçülür, tanımlayıcılık sırasına göre:

  1. AD + SOYAD   "Derya Yanık"   -> en tanımlayıcı. Çıkan çiftlere bakınca
                                     kamusal kişi mi grup üyesi mi görülür.
  2. AD + HİTAP   "Derya hocam"   -> biri adıyla çağrılıyor. Üye olma ihtimali
                   "Sayın Derya"     en yüksek durum.
  3. YALNIZ AD    "Derya"         -> bağlamsız, tanımlayıcılığı düşük.

Kullanım:
  python isim_tarama.py
  python isim_tarama.py --sutun text_raw
  python isim_tarama.py --kamusal Derya,Vedat,Mehmet,Kemal,Ekrem

  --kamusal ile verdiğin adlar KAMUSAL KİŞİ sayılır ve ayrı raporlanır.
  Önce betiği sade çalıştır, çıkan adlara bak, sonra bakan/siyasetçi
  adlarını bu listeye koyup yeniden çalıştır. Kalan sayı aradığın sayıdır.

Çıktı: loglar/isim_tarama_<sutun>.json ve ekrana özet
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "veri" / "islenmis"
LOG_DIR = BASE / "loglar"

BUYUK = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZQWX"
KUCUK = "abcçdefgğhıijklmnoöprsştuüvyzqwx"
_KUC = str.maketrans(BUYUK, KUCUK)


def tr_kucuk(s):
    return s.translate(_KUC).lower()


ADLAR = set("""
ahmet mehmet mustafa ali hasan hüseyin ibrahim ismail osman yusuf murat ömer
ramazan halil erkan serkan kemal recep bekir cemal şaban yaşar
süleyman abdullah fatih emre burak oğuzhan onur engin ufuk volkan tolga
cem can deniz kaan arda eren efe berke yiğit mert umut barış kerem taha
enes furkan emirhan samet hakan serhat gökhan özkan ercan sinan tuncay
fatma ayşe emine hatice zeynep elif meryem şerife zehra sultan hanife
merve büşra esra özge gamze pınar sevgi aslı burcu ceren damla dilek ebru
feride gül gizem hilal irem kübra melek nur nurcan rabia sema seda selin
şeyma tuğba yasemin aleyna beyza cansu derya duygu eda filiz
gonca hande ilayda kader leyla mine nazlı neslihan nihal nilgün özlem
sevda sibel tuba yağmur zeliha zühal aysel aynur bahar berna betül
cemile çiğdem dilara ela esma fadime ferhat gülsüm handan ilknur
kevser melike meltem müge nalan nergis perihan reyhan rukiye saliha
semra serpil songül şule tülay vildan yeter asuman
adem alper arif aykut aytekin bahadır bilal bülent cengiz
coşkun davut doğan dursun erdal erdem ergün ersin ertuğrul faruk
gökay gürkan hamza harun hayri hikmet ilhan ilker kadir kazım
levent lütfi mahmut mesut metin muhammed muharrem nazım necati nedim
nihat nuri okan oktay orhan özgür rıza sadık sefa selim selçuk sezgin
şükrü tamer tarık tayfun turgay turgut uğur vedat veli yavuz yunus
zafer zeki abdurrahman adnan aziz bedri behçet beytullah
burhan cafer celal cihan cüneyt ekrem erol eyüp fahri feyzullah
galip hamdi haydar hidayet hüsnü kamil kenan kürşat macit mahir
mazhar mithat muzaffer müslüm naci nail nejat nevzat nizam nurettin
raşit refik rüştü sabri sadettin salih savaş şevket şenol tahir
tevfik vahit yakup yalçın yetkin ziya mevlüde mahinur
""".split())

# Ad olarak da kullanılan ama sıradan sözcük olan riskli adlar
RISKLI = {"can", "deniz", "nur", "gül", "umut", "barış", "güneş", "özgür",
          "sevgi", "mert", "ufuk", "bahar", "melek", "kader", "dilek",
          "savaş", "yağmur", "doğan", "ela", "esma", "efe", "sultan"}

# Soyad konumunda görünse bile soyad SAYILMAYACAK sözcükler
BEYAZ = set("""
sosyal hizmet hizmetler hizmeti türkiye ankara istanbul izmir antalya bursa
adana konya hatay kpss ösym yök aile bakanlık bakanlığı bakanlığına
bakanlığının bakanlığında bakan bakanı şubat ocak mart nisan mayıs haziran
temmuz ağustos eylül ekim kasım aralık pazartesi salı çarşamba perşembe
cuma cumartesi pazar üniversite üniversitesi fakülte fakültesi bölüm bölümü
genel müdürlük müdürlüğü sgk shu aös aöf cimer twitter telegram whatsapp
google youtube pdf url kullanici covid korona kızılay afad milli eğitim
sağlık adalet içişleri hacettepe akdeniz anadolu atatürk selçuk ege marmara
gazi dokuz eylül çalışmacı çalışmacılar uzman uzmanı uzmanları uzmanlar
arkadaşlar arkadaşım asdep personel personeli sözleşmeli kadro kadrosu
lisans önlisans yüksek merkez merkezi çocuk çocuğu kadın engelli yaşlı
destek hocam hoca bey hanım abi abla allah inşallah maşallah
sayın bir ben biz siz bu şu evet hayır tamam peki valla aynen
""".split())

HITAPLAR = ("hocam", "hoca", "bey", "bay", "hanım", "abi", "ağabey", "abla",
            "kardeşim", "kardeş", "bacım", "abicim", "ablacım")

BH = r"[A-ZÇĞİIÖŞÜ][a-zçğıiöşü]{2,}"
AD_SOYAD_RE = re.compile(rf"\b({BH})\s+({BH})\b")
AD_HITAP_RE = re.compile(rf"\b({BH})\s+(?:{'|'.join(HITAPLAR)})\b")
SAYIN_RE = re.compile(rf"\bSayın\s+({BH})\b")
TEK_AD_RE = re.compile(rf"\b({BH})\b")


def tara(metinler, kamusal, riskli_haric):
    kamusal = {tr_kucuk(a) for a in kamusal}
    sayac = {k: {"mesaj": 0, "jeton": Counter()} for k in
             ("ad_soyad", "ad_hitap", "ad_tek", "kamusal")}
    n = 0

    def ad_mi(kel):
        k = tr_kucuk(kel)
        if k not in ADLAR:
            return False
        if riskli_haric and k in RISKLI:
            return False
        return True

    for s in metinler:
        if not isinstance(s, str) or not s:
            continue
        n += 1
        bul = {k: set() for k in sayac}
        kapsanan = set()

        for m in AD_SOYAD_RE.finditer(s):
            ad, soyad = m.group(1), m.group(2)
            if ad_mi(ad) and tr_kucuk(soyad) not in BEYAZ:
                if tr_kucuk(ad) in kamusal:
                    bul["kamusal"].add(f"{ad} {soyad}")
                else:
                    bul["ad_soyad"].add(f"{ad} {soyad}")
                kapsanan.add(ad)

        for m in list(AD_HITAP_RE.finditer(s)) + list(SAYIN_RE.finditer(s)):
            ad = m.group(1)
            if ad_mi(ad):
                if tr_kucuk(ad) in kamusal:
                    bul["kamusal"].add(ad)
                else:
                    bul["ad_hitap"].add(ad)
                kapsanan.add(ad)

        for m in TEK_AD_RE.finditer(s):
            ad = m.group(1)
            if ad_mi(ad) and ad not in kapsanan:
                if tr_kucuk(ad) in kamusal:
                    bul["kamusal"].add(ad)
                else:
                    bul["ad_tek"].add(ad)

        for k, kume in bul.items():
            if kume:
                sayac[k]["mesaj"] += 1
                sayac[k]["jeton"].update(kume)
    return n, sayac


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sutun", default="text_light")
    ap.add_argument("--kamusal", default="",
                    help="Kamusal kişi adları, virgülle: Derya,Vedat,Mehmet")
    ap.add_argument("--riskli-dahil", action="store_true",
                    help="Can, Deniz, Nur gibi riskli adları da say")
    args = ap.parse_args()

    kamusal = [a.strip() for a in args.kamusal.split(",") if a.strip()]

    if args.sutun == "text_raw":
        df = pd.read_parquet(OUT_DIR / "mesajlar_ham_metin.parquet")
        metinler = df["text_raw"]
    else:
        df = pd.read_parquet(OUT_DIR / "mesajlar.parquet")
        metinler = df[args.sutun]

    n, sayac = tara(metinler, kamusal, not args.riskli_dahil)

    basliklar = [
        ("ad_soyad", "AD + SOYAD    \"Derya Yanık\"        en tanımlayıcı"),
        ("ad_hitap", "AD + HİTAP    \"Derya hocam\"        biri adıyla çağrılıyor"),
        ("ad_tek",   "YALNIZ AD     \"Derya\"              bağlamsız, düşük"),
        ("kamusal",  "KAMUSAL KİŞİ  (--kamusal listesi)   ayrı tutuldu"),
    ]

    print(f"\nTaranan mesaj : {n:,}")
    print(f"Sütun         : {args.sutun}")
    print(f"Riskli adlar  : {'dahil' if args.riskli_dahil else 'hariç'}")
    print(f"Kamusal liste : {', '.join(kamusal) if kamusal else '(boş)'}\n")

    rapor = {"sutun": args.sutun, "taranan_mesaj": n,
             "kamusal_liste": kamusal,
             "riskli_adlar_haric": not args.riskli_dahil,
             "baglamlar": {}}

    for k, bas in basliklar:
        v = sayac[k]
        if k == "kamusal" and not kamusal:
            continue
        oran = 100 * v["mesaj"] / n if n else 0
        print(bas)
        print(f"   eşleşen mesaj : {v['mesaj']:,}   (%{oran:.2f})")
        print(f"   farklı değer  : {len(v['jeton']):,}")
        print(f"   en sık        : {', '.join(f'{a}({b})' for a, b in v['jeton'].most_common(20))}\n")
        rapor["baglamlar"][k] = {
            "mesaj": v["mesaj"], "yuzde": round(oran, 3),
            "farkli_jeton": len(v["jeton"]),
            "en_sik": [{"jeton": a, "adet": b} for a, b in v["jeton"].most_common(80)],
        }

    ozel = sayac["ad_soyad"]["mesaj"] + sayac["ad_hitap"]["mesaj"]
    print("-" * 62)
    print(f"Kamusal kişiler dışında, ad-soyad veya adla hitap içeren mesaj:")
    print(f"   en fazla {ozel:,} mesaj   (%{100*ozel/n:.2f})")
    print("   (iki bağlam çakışabileceği için bu bir ÜST sınırdır)")
    rapor["ozel_kisi_ust_sinir"] = {"mesaj": ozel, "yuzde": round(100*ozel/n, 3)}

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    yol = LOG_DIR / f"isim_tarama_{args.sutun}.json"
    yol.write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nYazıldı: {yol.relative_to(BASE)}")
    print("Bu dosyada mesaj metni YOKTUR; yalnızca sayım ve eşleşen adlar vardır.")


if __name__ == "__main__":
    main()
