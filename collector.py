#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Los Ojos Trendyol Satis Takip - Veri Toplayici (collector)
-----------------------------------------------------------
Bu program Trendyol'daki Los Ojos markasinin tum urunlerini gezer,
her urun icin Trendyol'un gosterdigi sosyal kanit verilerini toplar:
  - orderCountL3D : "son 3 gunde X+ satti" (Trendyol'un kendi satis rakami)
  - basketCount   : kac kisinin sepetinde
  - favoriteCount : favori sayisi
  - pageViewCount : goruntulenme
  - ratingCount   : yorum / degerlendirme sayisi (satis hizinin en saglam isareti)

Calistiginda data/history.json dosyasina o gunun bir "fotografini" ekler.
Gun gectikce bu fotograflarin farki = satis hizi tahmini.

Hicbir giris / sifre / cerez gerekmez. Sadece internet baglantisi.
"""

import json
import os
import sys
import time
import datetime
import urllib.request

BRAND_ID = 147875
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
REQUEST_PAUSE = 0.8
MAX_PAGES = 40

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SEARCH_API = ("https://apigw.trendyol.com/discovery-web-searchgw-service/"
              "v2/api/infinite-scroll/sr")
SOCIAL_API = ("https://apigw.trendyol.com/discovery-sfint-search-service/"
              "api/social-proof/")


def _get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.trendyol.com/",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse_tr_number(val):
    """ '1,7B'->1700, '385,2B'->385200, '2B+'->2000, '500+'->500, '371'->371 """
    if val is None:
        return None, False
    s = str(val).strip()
    plus = "+" in s
    s = s.replace("+", "").strip()
    mult = 1
    up = s.upper()
    if up.endswith("MN"):
        mult = 1000000; s = s[:-2]
    elif up.endswith("M"):
        mult = 1000000; s = s[:-1]
    elif up.endswith("B"):
        mult = 1000; s = s[:-1]
    elif up.endswith("K"):
        mult = 1000; s = s[:-1]
    s = s.replace(".", "").replace(",", ".").strip()
    try:
        return int(round(float(s) * mult)), plus
    except ValueError:
        return None, plus



def _extract_props_json(html):
    """Marka sayfasi HTML'inden gomulu urun JSON'unu cikarir (yedek yontem)."""
    tag = 'window["__single-search-result__PROPS"]='
    i = html.find(tag)
    if i < 0:
        return None
    j = html.find("{", i)
    depth = 0; in_str = False; esc = False
    k = j
    while k < len(html):
        c = html[k]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return html[j:k+1]
        k += 1
    return None


def _find_products(o, d=0):
    if not o or d > 8:
        return None
    if isinstance(o, list) and o and isinstance(o[0], dict) and o[0].get("id") and o[0].get("price"):
        return o
    if isinstance(o, dict):
        for v in o.values():
            r = _find_products(v, d + 1)
            if r:
                return r
    return None


def fetch_catalog_html(products):
    """API ise yaramazsa marka sayfasi HTML'ini gezerek urunleri toplar."""
    for pi in range(1, MAX_PAGES + 1):
        url = f"https://www.trendyol.com/los-ojos-x-b147875?pi={pi}"
        try:
            html = _get(url)
        except Exception as e:
            print(f"  ! (html) sayfa {pi} alinamadi: {e}")
            break
        ps = _extract_props_json(html)
        if not ps:
            break
        try:
            props = json.loads(ps)
        except Exception:
            break
        page = _find_products(props) or []
        if not page:
            break
        before = len(products)
        for p in page:
            pid = p.get("id")
            if pid is None or pid in products:
                continue
            pr = p.get("price") or {}
            price = None
            if isinstance(pr, dict):
                price = (pr.get("sellingPrice") or pr.get("discountedPrice") or pr.get("originalPrice"))
            rating = p.get("ratingScore") or {}
            avg = rating.get("averageRating") if isinstance(rating, dict) else None
            products[pid] = {
                "id": pid, "name": (p.get("name") or "").strip(), "price": price,
                "ratingCount": rating.get("totalCount") if isinstance(rating, dict) else None,
                "rating": round(avg, 2) if avg else None, "merchantId": p.get("merchantId"),
            }
        print(f"  (html) sayfa {pi}: toplam {len(products)} urun")
        if len(products) == before:
            break
        time.sleep(REQUEST_PAUSE)
    return products


def fetch_catalog():
    products = {}
    for pi in range(1, MAX_PAGES + 1):
        url = (f"{SEARCH_API}?wb={BRAND_ID}&pi={pi}&culture=tr-TR"
               f"&storefrontId=1&countryCode=TR")
        try:
            data = json.loads(_get(url))
        except Exception as e:
            print(f"  ! sayfa {pi} alinamadi: {e}")
            break
        result = data.get("result", data)
        page_products = (result.get("products")
                         or (result.get("searchResult") or {}).get("products") or [])
        if not page_products:
            break
        for p in page_products:
            pid = p.get("id")
            if pid is None or pid in products:
                continue
            pr = p.get("price") or {}
            price = None
            if isinstance(pr, dict):
                price = (pr.get("sellingPrice") or pr.get("discountedPrice")
                         or pr.get("originalPrice"))
            rating = p.get("ratingScore") or {}
            avg = rating.get("averageRating") if isinstance(rating, dict) else None
            imgs = p.get("images") or []
            img = imgs[0] if imgs else None
            if img and not img.startswith("http"):
                img = "https://cdn.dsmcdn.com/mnresize/400/-/" + img.lstrip("/")
            products[pid] = {
                "id": pid,
                "name": (p.get("name") or "").strip(),
                "price": price,
                "ratingCount": rating.get("totalCount") if isinstance(rating, dict) else None,
                "rating": round(avg, 2) if avg else None,
                "merchantId": p.get("merchantId"),
                "image": img,
            }
        print(f"  sayfa {pi}: toplam {len(products)} urun")
        time.sleep(REQUEST_PAUSE)
    if not products:
        print("  API urun vermedi, HTML yedek yontemi deneniyor...")
        products = fetch_catalog_html(products)
    return products


def fetch_social(product_ids):
    out = {}
    batch = 24
    for i in range(0, len(product_ids), batch):
        chunk = product_ids[i:i + batch]
        ids = ",".join(str(x) for x in chunk)
        url = (f"{SOCIAL_API}?contentIds={ids}&channelId=1&storefrontId=1"
               f"&culture=tr-TR&countryCode=TR")
        try:
            data = json.loads(_get(url))
        except Exception as e:
            print(f"  ! sosyal kanit grubu alinamadi: {e}")
            time.sleep(REQUEST_PAUSE)
            continue
        for pid, arr in (data.get("data") or {}).items():
            rec = {}
            for o in arr:
                k = o.get("key"); v = o.get("value")
                if k in ("orderCountL3D", "basketCount", "favoriteCount", "pageViewCount"):
                    num, _ = parse_tr_number(v)
                    rec[k] = num
                    rec[k + "_raw"] = v
            out[int(pid)] = rec
        time.sleep(REQUEST_PAUSE)
    return out


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def main():
    today = datetime.date.today().isoformat()
    print(f"Los Ojos veri toplama basladi - {today}")

    print("1) Urun katalogu cekiliyor...")
    catalog = fetch_catalog()
    if not catalog:
        print("HATA: Hic urun alinamadi. (Trendyol IP'yi engellemis olabilir.)")
        sys.exit(1)
    ids = list(catalog.keys())
    print(f"   {len(ids)} urun bulundu.")

    print("2) Satis / sepet / favori verileri cekiliyor...")
    social = fetch_social(ids)
    print(f"   {len(social)} urun icin sosyal kanit alindi.")

    snapshot = {}
    for pid, info in catalog.items():
        s = social.get(pid, {})
        snapshot[str(pid)] = {
            "name": info["name"], "price": info["price"],
            "ratingCount": info["ratingCount"], "rating": info["rating"],
            "orderL3D": s.get("orderCountL3D"), "orderL3D_raw": s.get("orderCountL3D_raw"),
            "basket": s.get("basketCount"), "favorite": s.get("favoriteCount"),
            "pageView": s.get("pageViewCount"),
            "image": info.get("image"),
        }

    save_json(os.path.join(DATA_DIR, "latest.json"),
              {"collectedAt": today, "brand": "Los Ojos",
               "productCount": len(catalog), "products": snapshot})

    history = load_json(os.path.join(DATA_DIR, "history.json"),
                        {"brand": "Los Ojos", "snapshots": []})
    history["snapshots"] = [s for s in history["snapshots"] if s.get("date") != today]
    compact = {"date": today, "products": {}}
    for pid, pr in snapshot.items():
        compact["products"][pid] = {
            "rc": pr["ratingCount"], "o3": pr["orderL3D"],
            "b": pr["basket"], "f": pr["favorite"], "v": pr["pageView"], "p": pr["price"],
        }
    history["snapshots"].append(compact)
    history["snapshots"].sort(key=lambda s: s["date"])
    history["names"] = {pid: pr["name"] for pid, pr in snapshot.items()}
    save_json(os.path.join(DATA_DIR, "history.json"), history)

    n_order = sum(1 for p in snapshot.values() if p["orderL3D"])
    print(f"TAMAM. {len(catalog)} urun kaydedildi, {n_order} urunde '3 gunluk satis' var.")
    print(f"Arsivde {len(history['snapshots'])} gunluk veri birikti.")


if __name__ == "__main__":
    main()
