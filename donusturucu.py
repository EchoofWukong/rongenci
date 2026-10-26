import json

def txt_den_listeye(dosya_adi):
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            # Her satırı okur, sağındaki solundaki boşluğu siler ve küçük harfe (lower) çevirir
            return [satir.strip().lower() for satir in f.readlines() if satir.strip()]
    except:
        return []

# .txt dosyalarını oku
kadin_isimleri = txt_den_listeye("kız.txt")
erkek_isimleri = txt_den_listeye("erkek.txt")

# İkisini tek bir yapıda birleştir
veritabani = {
    "kadin": kadin_isimleri,
    "erkek": erkek_isimleri
}

# Hatasız, tırnaklı ve virgüllü JSON dosyasını oluştur
with open("isim_veritabani.json", "w", encoding="utf-8") as f:
    json.dump(veritabani, f, ensure_ascii=False, indent=4)

print(f"[+] İşlem tamam! {len(kadin_isimleri)} kadın, {len(erkek_isimleri)} erkek ismi JSON'a çevrildi.")