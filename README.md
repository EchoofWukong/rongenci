# 🕵️ Instagram Takipçi Analiz ve Cinsiyet Ayrıştırma Aracı

Python ve Tkinter kullanılarak geliştirilmiş, Instagram hesaplarının takipçi/takip edilen verilerini tarayıcı otomasyonu ile çekerek bu kişileri cinsiyetlerine (kadın/erkek) göre analiz eden ve gruplandıran masaüstü uygulamasıdır.

## 🌟 Özellikler

- **Veri Çekme (Scraping):** Tarayıcı otomasyonu kullanılarak belirlenen hesabın takipçi listelerinin otomatik olarak çekilmesi.
- **Cinsiyet Tahmin Algoritması:** Çekilen kullanıcı verilerini (isim, kullanıcı adı vb.) analiz ederek kadın/erkek ayrımını yapan özel tespit (heuristic) sistemi.
- **Yerel Depolama:** Çekilen ve işlenen tüm verilerin hızlı erişim ve analiz için yerel olarak `JSON` formatında saklanması.
- **Masaüstü Arayüz (GUI):** Tkinter ile hazırlanmış, kolay kullanımlı ve verilerin anlık takip edilebildiği pencere tasarımı.

## 🛠️ Kullanılan Teknolojiler

- **Ana Dil:** Python 3
- **Arayüz (GUI):** Tkinter
- **Veri Yönetimi:** JSON
- **Otomasyon:** Tarayıcı otomasyon araçları (Selenium vb.)

## ⚙️ Kurulum ve Çalıştırma (Yerel Ortam)

Projeyi bilgisayarınızda çalıştırmak için aşağıdaki komutları sırayla terminalinizde çalıştırın:

```bash
git clone [https://github.com/EchoofWukong/instagram-takipci-analiz.git](https://github.com/EchoofWukong/instagram-takipci-analiz.git)
cd instagram-takipci-analiz
pip install -r requirements.txt
python main.py
