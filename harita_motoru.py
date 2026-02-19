import requests
from PIL import Image, ImageDraw

DUNYA_ID = "tr99"

def veri_getir(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    return [line.split(',') for line in r.text.strip().split('\n') if line]

def harita_yap():
    try:
        player_data = veri_getir("player")
        village_data = veri_getir("village")

        # --- KLANLARI OYUNCU LİSTESİNDEN HESAPLA ---
        # Player.txt formatı: id, isim, klan_id, koy_sayisi, puan, rank
        klan_puanlari = {}
        for p in player_data:
            if len(p) >= 5:
                k_id = p[2]
                if k_id != "0": # Bir klana üye olanlar
                    puan = int(p[4])
                    klan_puanlari[k_id] = klan_puanlari.get(k_id, 0) + puan

        # Puanı en yüksek 15 klan ID'sini bul
        top_klan_ids = sorted(klan_puanlari, key=klan_puanlari.get, reverse=True)[:15]
        
        # Renkler
        renkler = [(255,0,0), (0,255,0), (0,150,255), (255,255,0), (255,0,255), (0,255,255), 
                   (255,165,0), (200,200,200), (0,100,0), (255,20,147), (210,105,30), 
                   (127,255,0), (178,34,34), (0,0,128), (128,128,0)]
        renk_map = dict(zip(top_klan_ids, renkler))

        # Oyuncu -> Klan Eşleşmesi
        oyuncu_klan = {p[0]: p[2] for p in player_data if len(p) > 2}

        # Çizim (1000x1000)
        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        draw = ImageDraw.Draw(img)

        boyanan = 0
        for v in village_data:
            if len(v) >= 5:
                try:
                    # x, y, sahip_id
                    x, y, o_id = int(v[2]), int(v[3]), v[4]
                    k_id = oyuncu_klan.get(o_id, "0")
                    
                    if k_id in renk_map:
                        # Görünürlüğü artırmak için 3x3 kare
                        draw.rectangle([x-1, y-1, x+1, y+1], fill=renk_map[k_id])
                        boyanan += 1
                    else:
                        draw.point((x, y), fill=(50, 50, 50))
                except: continue

        img.save("guncel_harita.png")
        print(f"BAŞARILI! {boyanan} köy renklendirildi.")
        print("Boyanan Klan ID'leri:", top_klan_ids)

    except Exception as e:
        print(f"Hata: {str(e)}")

if __name__ == "__main__":
    harita_yap()
