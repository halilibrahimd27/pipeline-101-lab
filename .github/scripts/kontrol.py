#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Security 101 — LAB karnesi.

Bu betik gorevlerinin durumunu kontrol eder ve
Actions > Summary ekraninda bir tablo olarak gosterir.

Bu dosyayi degistirmen gerekmiyor.
"""
import glob
import os
import re
import sys

KOK = os.getcwd()
CI_YOLU = os.path.join(KOK, ".github", "workflows", "ci.yml")
ANAHTAR_DESENI = "sk_" + "live_"          # kendini yakalamasin diye bolundu


def oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


ci = oku(CI_YOLU)
gitignore = oku(os.path.join(KOK, ".gitignore"))

sonuclar = []      # (tamam, baslik, ipucu)


# ---------------------------------------------------------- 1
env_duruyor = os.path.exists(os.path.join(KOK, ".env"))
gitignore_tamam = re.search(r"^\s*\.env\s*$", gitignore, re.M) is not None
gomulu_dosyalar = [
    os.path.relpath(p, KOK)
    for p in glob.glob(os.path.join(KOK, "src", "**", "*.js"), recursive=True)
    if ANAHTAR_DESENI in oku(p)
]

eksikler = []
if env_duruyor:
    eksikler.append(".env dosyasi hala repoda")
if not gitignore_tamam:
    eksikler.append(".gitignore icinde .env satiri yok")
if gomulu_dosyalar:
    eksikler.append("koda gomulu anahtar duruyor: " + ", ".join(gomulu_dosyalar))

sonuclar.append((
    not eksikler,
    "Gorev 1 — Secret temizligi",
    "; ".join(eksikler) or "`.env` silindi, `.gitignore` guncellendi, koda gomulu anahtar kaldirildi",
))


# ---------------------------------------------------------- 2
bas_bolum = ci.split("\njobs:")[0]
izin_var = re.search(r"^permissions:", bas_bolum, re.M) is not None
okuma_var = re.search(r"contents:\s*read|read-all", bas_bolum) is not None
sonuclar.append((
    izin_var and okuma_var,
    "Gorev 2 — Izni kis",
    "ci.yml'in en ustune `permissions:` / `contents: read` ekle"
    if not (izin_var and okuma_var) else "varsayilan izin okumaya cekilmis",
))


# ---------------------------------------------------------- 3
ci_var = re.search(r"run:\s*npm ci\b", ci) is not None
install_var = re.search(r"run:\s*npm install\b", ci) is not None
sonuclar.append((
    ci_var and not install_var,
    "Gorev 3 — Kurulumu duzelt",
    "`npm install` yerine `npm ci` kullan"
    if not (ci_var and not install_var) else "lockfile'a birebir uyuluyor",
))


# ---------------------------------------------------------- 4
kullanilanlar = re.findall(r"uses:\s*([^\s#]+)", ci)
sabitlenmemis = [u for u in kullanilanlar if not re.search(r"@[0-9a-fA-F]{40}$", u)]
sonuclar.append((
    bool(kullanilanlar) and not sabitlenmemis,
    "Gorev 4 — Action'lari sabitle",
    "etiketle cagirilan action'lar: " + ", ".join(sabitlenmemis)
    if sabitlenmemis else "tum action'lar 40 karakterlik commit numarasina sabit",
))


# ---------------------------------------------------------- 5
riskli_satirlar = []
for no, satir in enumerate(ci.splitlines(), start=1):
    if "github.event" not in satir:
        continue
    if re.match(r"\s*#", satir):
        continue
    if re.match(r"\s*-?\s*run:", satir):
        riskli_satirlar.append(no)
    elif re.match(r"\s*[\w.\-]+:\s*\$\{\{", satir):
        continue                       # env: ALTINDA — dogru kullanim
    else:
        riskli_satirlar.append(no)     # muhtemelen bir run blogunun icinde

env_blogu = re.search(r"^\s*env:", ci, re.M) is not None
hala_logluyor = "github.event" in ci

if riskli_satirlar:
    ipucu5 = "su satirlarda girdi dogrudan komuta gomulu: " + \
             ", ".join(str(n) for n in riskli_satirlar)
elif not hala_logluyor:
    ipucu5 = "adimi silmek cozum degil — env ile tekrar ekle"
elif not env_blogu:
    ipucu5 = "degeri once `env:` altinda bir degiskene al"
else:
    ipucu5 = "girdi env uzerinden aliniyor, komut icine gomulmuyor"

sonuclar.append((
    (not riskli_satirlar) and env_blogu and hala_logluyor,
    "Gorev 5 — Girdiyi ayir",
    ipucu5,
))


# ---------------------------------------------------------- bonus
bonus_araclar = [a for a in ("gitleaks", "osv-scanner", "semgrep") if a in ci]
bonus = bool(bonus_araclar)


# ---------------------------------------------------------- karne
puan = sum(1 for tamam, _, _ in sonuclar if tamam)
toplam = len(sonuclar)

satirlar = []
satirlar.append("# Pipeline Security 101 — Karne\n")
dolu = "█" * puan + "░" * (toplam - puan)
satirlar.append(f"## `{dolu}`  {puan} / {toplam}\n")

if puan == toplam:
    satirlar.append("**Hepsi tamam. Pipeline'i sertlestirdin.**\n")
else:
    satirlar.append("Eksik gorevler asagida. Duzeltip tekrar commit at, "
                    "bu karne kendiliginden yenilenir.\n")

satirlar.append("| | Gorev | Durum |")
satirlar.append("|---|---|---|")
for tamam, baslik, ipucu in sonuclar:
    isaret = "✅" if tamam else "❌"
    satirlar.append(f"| {isaret} | **{baslik}** | {ipucu} |")

isaret_b = "⭐" if bonus else "—"
bonus_metin = ("eklenen arac: " + ", ".join(bonus_araclar)) if bonus \
    else "ci.yml'e bir tarama adimi ekle (gitleaks / osv-scanner)"
satirlar.append(f"| {isaret_b} | *Bonus — Tarama ekle* | {bonus_metin} |")

satirlar.append("")
satirlar.append("> Takildigin yerde `README.md` dosyasindaki ilgili goreve bak.")

karne = "\n".join(satirlar)
print(karne)

ozet = os.environ.get("GITHUB_STEP_SUMMARY")
if ozet:
    with open(ozet, "a", encoding="utf-8") as f:
        f.write(karne + "\n")

sys.exit(0 if puan == toplam else 1)
