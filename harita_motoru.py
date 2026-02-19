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
        # Tüm dosyaları çek
        tribe_data = veri_getir("tribe")
        player_data = veri_getir("player")
        village_data = veri_getir("village")

        # --- KRİTİK ANALİZ: Gerçek klan verisi hangisi? ---
        # Gerçek klan verisinde genelde 6-8 sütun olur ve 3. sütun (index 2) klan tagidir.
        # Eğer sunucu isimleri gizlediyse, sütun sayısından bulalım.
        
        klan_id_puan = {}
        # Hangi dosya klan dosyası gibi duruyor? (Sütun sayısı < 10 olanı seç)
        hedef_klan_verisi = tribe_data if len(tribe_data[0]) < 10 else player_data
        
        for p in hedef_klan_verisi:
            if len(p) >= 6:
                try:
                    # ID: p[0], Puan: p[5]
                    # Eğer puan çok yüksekse (milyonlarca), o klan verisidir.
                    klan_id_puan[p[0]] = int(p[5])
                except: continue

        # En büyük 15 puanlı ID'yi al
        top_ids = sorted(klan_id_puan, key=klan_id_puan.get, reverse=True)[:15]
        
        renkler = [(255,0,0), (0,255,0), (0,150,255), (255,255,0), (255,0,255), (0,255,255), 
                   (255,165,0), (200,200,200), (0,100,0), (255,20,147), (210,105,30), 
                   (127,255,0), (178,34,34), (0,0,128), (128,128,0)]
        renk_map = dict(zip(top_ids, renkler))

        # Oyuncu -> Klan Eşleşmesi (player.txt içinden)
        # 1. sütun oyuncu_id, 3. sütun klan_id
        oyuncu_klan = {p[0]: p[2] for p in player_data if len(p) > 2}

        # Çizim
        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        draw = ImageDraw.Draw(img)

        boyanan = 0
        for v in village_data:
            if len(v) >= 5:
                try:
                    x, y, o_id = int(v[2]), int(v[3]), v[4]
                    k_id = oyuncu_klan.get(o_id, "0")
                    
                    if k_id in renk_map:
                        draw.rectangle([x-1, y-1, x+1, y+1], fill=renk_map[k_id])
                        boyanan += 1
                    else:
                        draw.point((x, y), fill=(50, 50, 50))
                except: continue

        img.save("guncel_harita.png")
        print(f"SONUÇ: {boyanan} köy renklendirildi.")
        print("Boyanan ID'ler:", top_ids)

    except Exception as e:
        print(f"Hata: {str(e)}")

if __name__ == "__main__":
    harita_yap()
