import requests
import pandas as pd
from PIL import Image, ImageDraw
import io

# TR99 kesinlikle dolu ve verisi olan bir dünya
DUNYA_ID = "tr99"

def veri_al(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    # Veriyi yüklerken hata veren satırları atla
    return pd.read_csv(io.StringIO(r.text), header=None, on_bad_lines='skip')

def ciz():
    try:
        klan = veri_al("tribe")
        oyuncu = veri_al("player")
        koy = veri_al("village")

        # Klan analizini daha esnek yapalım (Sütunları garantiye alalım)
        # 0: id, 2: tag, 5: puan
        klan_temiz = klan.iloc[:, [0, 2, 5]].copy()
        klan_temiz.columns = ['id', 'tag', 'puan']
        
        # Puan sütununu sayıya çevir ve 0'dan büyükleri al
        klan_temiz['puan'] = pd.to_numeric(klan_temiz['puan'], errors='coerce')
        klan_temiz = klan_temiz.dropna(subset=['puan'])
        
        # İlk 15 klanı belirle
        top15 = klan_temiz.sort_values('puan', ascending=False).head(15)
        
        # Renkler
        renkler = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), 
                   (255,165,0), (128,0,128), (0,128,0), (255,20,147), (210,105,30), 
                   (0,250,154), (0,0,128), (128,128,0), (178,34,34)]
        renk_map = dict(zip(top15['id'], renkler))

        # Oyuncu-Klan Eşleşmesi (0: oyuncu_id, 2: klan_id)
        o_k_map = dict(zip(oyuncu[0], oyuncu[2]))

        # 1000x1000 Harita
        img = Image.new('RGB', (1000, 1000), (25, 25, 25))
        d = ImageDraw.Draw(img)

        # Izgara
        for i in range(100, 1000, 100):
            d.line([(i, 0), (i, 1000)], fill=(45, 45, 45))
            d.line([(0, i), (1000, i)], fill=(45, 45, 45))

        count = 0
        for _, v in koy.iterrows():
            # 2: x, 3: y, 4: oyuncu_id
            x, y, oid = int(v[2]), int(v[3]), v[4]
            kid = o_k_map.get(oid, 0)
            if kid in renk_map:
                # Köyleri belirgin yapmak için 2x2 kare çiziyoruz
                d.rectangle([x-1, y-1, x, y], fill=renk_map[kid])
                count += 1
            else:
                d.point((x,y), (65, 65, 65))

        img.save("guncel_harita.png")
        print(f"Bitti! {count} köy boyandı.")
        
    except Exception as e:
        print(f"Hata detayı: {e}")

if __name__ == "__main__":
    ciz()
