import requests
import pandas as pd
from PIL import Image, ImageDraw
import io

DUNYA_ID = "tr101"

def veri_al(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    # GitHub üzerinden çekince genellikle engel yemeyiz
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    return pd.read_csv(io.StringIO(r.text), header=None, on_bad_lines='skip')

def ciz():
    try:
        klan = veri_al("tribe")
        oyuncu = veri_al("player")
        koy = veri_al("village")

        # Gerçek klan verisi mi kontrolü (0. sütun ID, 5. sütun Puan)
        # Sütunları standart hale getir
        klan = klan.iloc[:, [0, 2, 5]]
        klan.columns = ['id', 'tag', 'puan']
        
        # Sadece puanı 1000'den büyük olanları al (Sahte veriyi elemek için)
        klan = klan[klan['puan'] > 1000]
        top15 = klan.sort_values('puan', ascending=False).head(15)
        
        # Renkler ve Eşleşmeler
        renkler = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (255,165,0)]
        renk_map = dict(zip(top15['id'], (renkler * 3)[:15]))
        o_k_map = dict(zip(oyuncu[0], oyuncu[2]))

        img = Image.new('RGB', (1000, 1000), (30, 30, 30))
        d = ImageDraw.Draw(img)

        for _, v in koy.iterrows():
            x, y, oid = int(v[2]), int(v[3]), v[4]
            kid = o_k_map.get(oid, 0)
            if kid in renk_map:
                d.rectangle([x-1, y-1, x+1, y+1], fill=renk_map[kid])
            else:
                d.point((x,y), (70, 70, 70))

        img.save("guncel_harita.png")
        print("Harita başarıyla oluşturuldu.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    ciz()
