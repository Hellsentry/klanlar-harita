import requests
from PIL import Image, ImageDraw
import io

DUNYA_ID = "tr99"

def veri_cek(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    return r.text.strip().split('\n')

def harita_yap():
    try:
        klan_verisi = veri_cek("tribe")
        oyuncu_verisi = veri_cek("player")
        koy_verisi = veri_cek("village")

        # 1. Klanları Ayıkla (ID, Tag, Puan)
        klanlar = []
        for satir in klan_verisi:
            parca = satir.split(',')
            if len(parca) >= 6:
                try:
                    # s[0]=ID, s[2]=Tag, s[5]=Puan
                    klanlar.append({'id': parca[0], 'tag': requests.utils.unquote(parca[2]).replace('+', ' '), 'puan': int(parca[5])})
                except: continue
        
        # Puanı en yüksek 15 klanı al
        ilk15 = sorted(klanlar, key=lambda x: x['puan'], reverse=True)[:15]
        renkler = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (255,165,0), (128,0,128), (0,128,0), (255,20,147), (210,105,30), (0,250,154), (178,34,34), (0,0,128), (128,128,0)]
        klan_renk_map = {k['id']: renkler[i] for i, k in enumerate(ilk15)}

        # 2. Oyuncu-Klan Eşleşmesi
        oyuncu_klan = {}
        for satir in oyuncu_verisi:
            parca = satir.split(',')
            if len(parca) >= 3:
                oyuncu_klan[parca[0]] = parca[2]

        # 3. Çizim (1000x1000)
        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        draw = ImageDraw.Draw(img)

        boyanan = 0
        for satir in koy_verisi:
            parca = satir.split(',')
            if len(parca) >= 5:
                # x=parca[2], y=parca[3], oyuncu_id=parca[4]
                x, y, oid = int(parca[2]), int(parca[3]), parca[4]
                kid = oyuncu_klan.get(oid, "0")
                if kid in klan_renk_map:
                    # Köyleri belirgin yapmak için 3x3 kare
                    draw.rectangle([x-1, y-1, x+1, y+1], fill=klan_renk_map[kid])
                    boyanan += 1
                else:
                    draw.point((x, y), fill=(60, 60, 60))

        img.save("guncel_harita.png")
        print(f"Final Sonuç: {boyanan} köy renklendirilerek harita kaydedildi.")
        for i, k in enumerate(ilk15):
            print(f"{i+1}. {k['tag']} ({k['puan']} Puan)")

    except Exception as e:
        print(f"Hata Oluştu: {e}")

if __name__ == "__main__":
    harita_yap()
