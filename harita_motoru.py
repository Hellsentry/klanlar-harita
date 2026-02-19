import requests
from PIL import Image, ImageDraw

DUNYA_ID = "tr99"

def veri_cek(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    r = requests.get(url, headers=headers)
    return r.text.strip().split('\n')

def harita_yap():
    try:
        # Verileri çekiyoruz
        klan_verisi = veri_cek("tribe")
        oyuncu_verisi = veri_cek("player")
        koy_verisi = veri_cek("village")

        # 1. En Yüksek Puanlı 15 Klanın ID'sini Buluyoruz
        klan_listesi = []
        for satir in klan_verisi:
            parca = satir.split(',')
            if len(parca) >= 6:
                try:
                    # parca[0]=ID, parca[5]=Puan
                    klan_id = str(parca[0])
                    puan = int(parca[5])
                    klan_listesi.append({'id': klan_id, 'puan': puan})
                except: continue
        
        # Puan sırasına diz ve ilk 15 ID'yi al
        ilk15_klanlar = sorted(klan_listesi, key=lambda x: x['puan'], reverse=True)[:15]
        ilk15_ids = [k['id'] for k in ilk15_klanlar]
        
        # Renk paleti (Görünürlüğü yüksek renkler)
        renkler = [(255,0,0), (0,255,0), (0,150,255), (255,255,0), (255,0,255), (0,255,255), 
                   (255,165,0), (128,0,128), (0,128,0), (255,20,147), (210,105,30), 
                   (0,250,154), (178,34,34), (0,0,128), (128,128,0)]
        klan_renk_map = dict(zip(ilk15_ids, renkler))

        # 2. Oyuncu-Klan Eşleşmesi (ID tabanlı)
        oyuncu_klan = {}
        for satir in oyuncu_verisi:
            parca = satir.split(',')
            if len(parca) >= 3:
                # parca[0]=OyuncuID, parca[2]=KlanID
                oyuncu_klan[str(parca[0])] = str(parca[2])

        # 3. Çizim (1000x1000)
        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        draw = ImageDraw.Draw(img)

        boyanan = 0
        for satir in koy_verisi:
            parca = satir.split(',')
            if len(parca) >= 5:
                try:
                    # parca[2]=x, parca[3]=y, parca[4]=oyuncu_id
                    x, y, oid = int(parca[2]), int(parca[3]), str(parca[4])
                    kid = oyuncu_klan.get(oid, "0")
                    
                    if kid in klan_renk_map:
                        # Köyleri belirgin yapmak için 3x3 kare çiziyoruz
                        draw.rectangle([x-1, y-1, x+1, y+1], fill=klan_renk_map[kid])
                        boyanan = boyanan + 1
                    else:
                        # Boş köyler gri nokta
                        draw.point((x, y), fill=(55, 55, 55))
                except: continue

        img.save("guncel_harita.png")
        print(f"BAŞARILI! {boyanan} adet köy boyandı.")
        print("Boyanan Klan ID'leri:", ilk15_ids)

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    harita_yap()
