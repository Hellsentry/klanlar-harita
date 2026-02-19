import requests
import pandas as pd
from PIL import Image, ImageDraw
import io

DUNYA_ID = "tr99"

def veri_al(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    # Sütunları ayırmadan ham metin olarak oku
    return pd.read_csv(io.StringIO(r.text), header=None)

def ciz():
    try:
        klan_df = veri_al("tribe")
        oyuncu_df = veri_al("player")
        koy_df = veri_al("village")

        # --- AKILLI ANALİZ ---
        # Klan tablosunda: 0. sütun ID, 2. sütun TAG, 5. sütun PUAN (genellikle)
        # Ama biz işi şansa bırakmıyoruz.
        
        # İlk 15 klanı PUAN sütununa göre bulalım (genelde en büyük sayılar buradadır)
        # Puan sütunu genelde 5. veya 7. sütun olur.
        puan_sutunu = 5 if klan_df.shape[1] > 5 else klan_df.columns[-1]
        
        top15 = klan_df.sort_values(puan_sutunu, ascending=False).head(15)
        
        # ID'leri ve Tag'leri alalım
        klan_renk_map = {}
        renkler = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), 
                   (255,165,0), (128,0,128), (0,128,0), (255,20,147), (210,105,30), 
                   (0,250,154), (0,0,128), (128,128,0), (178,34,34)]
        
        for i, (idx, row) in enumerate(top15.iterrows()):
            k_id = str(row[0])
            klan_renk_map[k_id] = renkler[i]

        # Oyuncu -> Klan Map (0: oyuncu_id, 2: klan_id)
        oyuncu_klan = {str(row[0]): str(row[2]) for _, row in oyuncu_df.iterrows()}

        # 1000x1000 Siyah Tuval
        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        d = ImageDraw.Draw(img)

        # Köyleri İşle
        boyanan_koy = 0
        for _, row in koy_df.iterrows():
            # 2: x, 3: y, 4: oyuncu_id
            try:
                x, y, o_id = int(row[2]), int(row[3]), str(row[4])
                k_id = oyuncu_klan.get(o_id, "0")
                
                if k_id in klan_renk_map:
                    # Köyleri belirgin yapmak için 3x3 kare
                    d.rectangle([x-1, y-1, x+1, y+1], fill=klan_renk_map[k_id])
                    boyanan_koy += 1
                else:
                    # Diğer köyler küçük gri nokta
                    d.point((x, y), fill=(60, 60, 60))
            except:
                continue

        img.save("guncel_harita.png")
        print(f"Başarı: {boyanan_koy} köy ilk 15 klan rengine boyandı.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    ciz()
