import requests
from PIL import Image, ImageDraw, ImageFont

DUNYA_ID = "tr101" # Burayı istediğin gibi değiştirebilirsin

def veri_getir(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    return [line.split(',') for line in r.text.strip().split('\n') if line]

def harita_yap():
    try:
        player_data = veri_getir("player")
        village_data = veri_getir("village")
        tribe_raw = veri_getir("tribe")

        # Klan ID -> Tag eşleşmesi (Sunucu tribe.txt'yi düzgün verirse buradan alacak)
        klan_tagleri = {t[0]: requests.utils.unquote(t[2]).replace('+', ' ') for t in tribe_raw if len(t) > 2}

        # Klan Puanlarını Hesapla
        klan_puanlari = {}
        for p in player_data:
            if len(p) >= 5:
                k_id = p[2]
                if k_id != "0":
                    klan_puanlari[k_id] = klan_puanlari.get(k_id, 0) + int(p[4])

        top_klan_ids = sorted(klan_puanlari, key=klan_puanlari.get, reverse=True)[:15]
        
        renkler = [(255,0,0), (0,255,0), (0,150,255), (255,255,0), (255,0,255), (0,255,255), 
                   (255,165,0), (200,200,200), (0,100,0), (255,20,147), (210,105,30), 
                   (127,255,0), (178,34,34), (0,0,128), (128,128,0)]
        renk_map = dict(zip(top_klan_ids, renkler))

        oyuncu_klan = {p[0]: p[2] for p in player_data if len(p) > 2}

        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        draw = ImageDraw.Draw(img)

        # Klan merkezlerini hesaplamak için koordinat listesi
        klan_koordinatları = {k_id: [] for k_id in top_klan_ids}

        # Köyleri Çiz
        for v in village_data:
            if len(v) >= 5:
                try:
                    x, y, o_id = int(v[2]), int(v[3]), v[4]
                    k_id = oyuncu_klan.get(o_id, "0")
                    if k_id in renk_map:
                        draw.rectangle([x-1, y-1, x+1, y+1], fill=renk_map[k_id])
                        klan_koordinatları[k_id].append((x, y))
                    else:
                        draw.point((x, y), fill=(50, 50, 50))
                except: continue

        # Klan İsimlerini Yaz
        for k_id in top_klan_ids:
            if klan_koordinatları[k_id]:
                # Koordinatların ortalamasını al (Yoğunluk merkezi)
                avg_x = sum(c[0] for c in klan_koordinatları[k_id]) / len(klan_koordinatları[k_id])
                avg_y = sum(c[1] for c in klan_koordinatları[k_id]) / len(klan_koordinatları[k_id])
                
                tag = klan_tagleri.get(k_id, f"K-{k_id}")
                # Yazıyı daha belirgin yapmak için siyah gölge ekle
                draw.text((avg_x+1, avg_y+1), tag, fill=(0,0,0))
                draw.text((avg_x, avg_y), tag, fill=renk_map[k_id])

        img.save("guncel_harita.png")
        print(f"BAŞARILI! Etiketli harita kaydedildi.")

    except Exception as e:
        print(f"Hata: {str(e)}")

if __name__ == "__main__":
    harita_yap()
