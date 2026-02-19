import requests
from PIL import Image, ImageDraw

DUNYA_ID = "tr99"

def veri_cek(dosya):
    url = f"https://{DUNYA_ID}.klanlar.org/map/{dosya}.txt"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    return r.text.strip().split('\n')

def harita_yap():
    try:
        # Sunucu klan yerine oyuncu gönderiyorsa, biz de dosyaları çapraz kontrol edelim
        k_verisi = veri_cek("tribe")
        p_verisi = veri_cek("player")
        v_verisi = veri_cek("village")

        # Gerçek klan verisini bulana kadar dene (Satır uzunluğu kontrolü)
        # Gerçek klan satırı kısa, oyuncu satırı uzundur.
        potansiyel_klan = k_verisi if len(k_verisi[0].split(',')) <= 6 else p_verisi
        
        klanlar = []
        for satir in potansiyel_klan:
            s = satir.split(',')
            if len(s) >= 3:
                try:
                    # Tag temizleme ve Puan (Sütun 5 değilse son sütunu dene)
                    tag = requests.utils.unquote(s[2]).replace('+', ' ')
                    puan = int(s[5]) if len(s) > 5 else int(s[-1])
                    if puan > 1000: # Sahte 0 puanlıları ele
                        klanlar.append({'id': s[0], 'tag': tag, 'puan': puan})
                except: continue

        # Puan sırasına göre ilk 15 (İsimsiz olanları ele)
        ilk15 = sorted([k for k in klanlar if k['tag'] != '0'], key=lambda x: x['puan'], reverse=True)[:15]
        
        if not ilk15:
            print("HATA: Gerçek klanlar hala bulunamadı. Sunucu tüm dosyaları maskelemiş olabilir.")
            return

        renkler = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (255,165,0), (128,0,128), (0,128,0), (255,20,147), (210,105,30), (0,250,154), (178,34,34), (0,0,128), (128,128,0)]
        k_renk_map = {k['id']: renkler[i] for i, k in enumerate(ilk15)}

        # Oyuncu-Klan Haritası
        oyuncu_klan = {s.split(',')[0]: s.split(',')[2] for s in p_verisi if len(s.split(',')) > 2}

        # Çizim
        img = Image.new('RGB', (1000, 1000), (20, 20, 20))
        d = ImageDraw.Draw(img)

        sayac = 0
        for satir in v_verisi:
            s = satir.split(',')
            if len(s) >= 5:
                x, y, o_id = int(s[2]), int(s[3]), s[4]
                k_id = oyuncu_klan.get(o_id, "0")
                if k_id in k_renk_map:
                    d.rectangle([x-1, y-1, x+1, y+1], fill=k_renk_map[k_id])
                    sayac += 1
                else:
                    d.point((x, y), fill=(55, 55, 55))

        img.save("guncel_harita.png")
        print(f"BAŞARILI! {sayac} köy boyandı.")
        for i, k in enumerate(ilk15):
            print(f"{i+1}. {k['tag']} ({k['puan']} Puan)")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    harita_yap()
