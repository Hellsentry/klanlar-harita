import requests
from PIL import Image, ImageDraw, ImageFont

DUNYA_ID = "tr101"

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

        klan_tagleri = {t[0]: requests.utils.unquote(t[2]).replace('+', ' ') for t in tribe_raw if len(t) > 2}

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

        klan_koordinatlari = {k_id: [] for k_id in top_klan_ids}

        for v in village_data:
            if len(v) >= 5:
                try:
                    x, y, o_id = int(v[2]), int(v[3]), v[4]
                    k_id = oyuncu_klan.get(o_id, "0")
                    if k_id in renk_map:
                        draw.rectangle([x-1, y-1, x+1, y+1], fill=renk_map[k_id])
                        klan_koordinatlari[k_id].append((x, y))
                    else:
                        draw.point((x, y), fill=(55, 55, 55))
                except: continue

        # --- FONT AYARI ---
        try:
            # GitHub sunucularında genellikle bu font bulunur
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            # Bulamazsa varsayılanı kullan
            font = ImageFont.load_default()

        for k_id in top_klan_ids:
            if klan_koordinatlari[k_id]:
                # Yoğunluk merkezini hesapla
                avg_x = sum(c[0] for c in klan_koordinatlari[k_id]) / len(klan_koordinatlari[k_id])
                avg_y = sum(c[1] for c in klan_koordinatlari[k_id]) / len(klan_koordinatlari[k_id])
                
                tag = klan_tagleri.get(k_id, f"K-{k_id}")
                
                # Yazıyı belirginleştirmek için 4 bir yanına siyah gölge (kontur) yapalım
                for offset in [(-1,-1), (1,-1), (-1,1), (1,1)]:
                    draw.text((avg_x + offset[0], avg_y + offset[1]), tag, fill=(0,0,0), font=font)
                
                # Ana yazıyı kendi renginde yaz
                draw.text((avg_x, avg_y), tag, fill=renk_map[k_id], font=font)

        img.save("guncel_harita.png")
        print("BAŞARILI! Etiketler büyütüldü ve harita güncellendi.")

    except Exception as e:
        print(f"Hata: {str(e)}")

if __name__ == "__main__":
    harita_yap()
