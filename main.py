# -*- coding: utf-8 -*-
import sys
import glob
import webbrowser
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
                             QTableWidget, QTableWidgetItem, QLabel, QComboBox, 
                             QHeaderView, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QFont, QPixmap

import core
from scraper import VeriCekmeMotoru, ProfilResmiIndirici

class SayisalItem(QTableWidgetItem):
    def __lt__(self, diger): return self.data(Qt.UserRole) < diger.data(Qt.UserRole)

class InstagramAnalizArayuzu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProAnaliz: Gelişmiş Takipçi & Favori Sistemi")
        self.resize(1450, 800)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #11111b; }
            QLabel { color: #cdd6f4; font-family: 'Segoe UI'; }
            QLineEdit, QComboBox { padding: 8px; background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; }
            QPushButton { padding: 8px; background-color: #cba6f7; color: #11111b; font-weight: bold; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #b4befe; }
            QPushButton:disabled { background-color: #45475a; color: #a6adc8; }
            QListWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; padding: 5px; outline: none; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #242436; }
            QListWidget::item:selected { background-color: #cba6f7; color: #11111b; font-weight: bold; border-radius: 4px; }
            QTableWidget { 
                background-color: #181825; color: #cdd6f4; border: 1px solid #313244; 
                border-radius: 6px; alternate-background-color: #1e1e2e; 
                gridline-color: #45475a; 
            }
            QTableWidget::item:selected { background-color: #313244; color: #cba6f7; }
            QHeaderView::section { 
                background-color: #1e1e2e; color: #a6adc8; padding: 8px; 
                font-weight: bold; border: 1px solid #313244; 
            }
            QToolTip { background-color: #313244; color: #cdd6f4; border: 1px solid #cba6f7; border-radius: 4px; padding: 4px; }
        """)
        
        self.ana_widget = QWidget()
        self.setCentralWidget(self.ana_widget)
        self.ana_layout = QHBoxLayout(self.ana_widget)
        
        self.sol_layout = QVBoxLayout()
        self.sol_layout.addWidget(QLabel("⭐ Özel Listeler"))
        self.ozel_liste = QListWidget()
        self.ozel_liste.addItem("⭐ Favoriler")
        self.ozel_liste.addItem("📝 Not Eklenenler")
        self.sol_layout.addWidget(self.ozel_liste)
        
        self.sol_layout.addWidget(QLabel("📂 Kayıtlı Taramalar"))
        self.hesap_listesi = QListWidget()
        self.sol_layout.addWidget(self.hesap_listesi)
        self.json_guncelle()
        
        self.sag_layout = QVBoxLayout()
        self.ust_layout = QHBoxLayout()
        self.hedef_input = QLineEdit()
        self.hedef_input.setPlaceholderText("Hedef Kullanıcı Adı Girin...")
        self.cek_btn = QPushButton("⚡ Tara")
        self.cek_btn.setCursor(Qt.PointingHandCursor)
        self.ust_layout.addWidget(self.hedef_input)
        self.ust_layout.addWidget(self.cek_btn)
        
        self.durum_lbl = QLabel("Durum: Hazır.")
        self.durum_lbl.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        
        self.filtre_layout = QHBoxLayout()
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("🔍 Tabloda Ara...")
        self.cinsiyet_filtresi = QComboBox()
        self.cinsiyet_filtresi.addItems(["Tümü", "Kadın", "Erkek", "Belirsiz"])
        self.filtre_layout.addWidget(self.arama_input)
        self.filtre_layout.addWidget(self.cinsiyet_filtresi)
        
        # 8 Sütunlu Yeni Tablo (İşlemler Sütunu Eklendi)
        self.tablo = QTableWidget(0, 8)
        self.tablo.setHorizontalHeaderLabels(["#", "★", "Kullanıcı Adı", "Tam İsim", "Cinsiyet", "Ortak Takip Ettiği", "Notlar", "İşlemler"])
        
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tablo.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tablo.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.tablo.horizontalHeader().setStretchLastSection(False)
        self.tablo.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.tablo.verticalHeader().setVisible(False) 
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setShowGrid(True)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablo.setMouseTracking(True)
        self.tablo.viewport().installEventFilter(self)
        
        self.sag_layout.addLayout(self.ust_layout)
        self.sag_layout.addWidget(self.durum_lbl)
        self.sag_layout.addLayout(self.filtre_layout)
        self.sag_layout.addWidget(self.tablo)
        
        self.bolucu = QSplitter(Qt.Horizontal)
        sol_w = QWidget(); sol_w.setLayout(self.sol_layout)
        sag_w = QWidget(); sag_w.setLayout(self.sag_layout)
        self.bolucu.addWidget(sol_w); self.bolucu.addWidget(sag_w)
        self.bolucu.setSizes([250, 1200])
        self.ana_layout.addWidget(self.bolucu)
        
        self.hesap_listesi.itemClicked.connect(self.liste_secildi)
        self.ozel_liste.itemClicked.connect(self.ozel_liste_secildi)
        self.cek_btn.clicked.connect(self.tarama_baslat)
        self.arama_input.textChanged.connect(self.tabloyu_filtrele)
        self.cinsiyet_filtresi.currentTextChanged.connect(self.tabloyu_filtrele)
        self.tablo.cellClicked.connect(self.hucre_tiklandi)
        self.tablo.cellDoubleClicked.connect(self.profile_git)
        self.tablo.itemChanged.connect(self.not_degisti)
        
        # Daha Kaliteli ve Büyük Fotoğraf Popup'ı
        self.foto_popup = QLabel(self)
        self.foto_popup.setWindowFlags(Qt.ToolTip)
        self.foto_popup.setFixedSize(256, 256)
        self.foto_popup.setStyleSheet("border: 3px solid #cba6f7; border-radius: 12px; background-color: #1e1e2e; font-weight:bold; color:#cba6f7;")
        self.foto_popup.setAlignment(Qt.AlignCenter)
        self.foto_popup.hide()
        
        self.suanki_hover = ""
        self.resim_motoru = None
        self.cekme_motoru = None
        self.download_motoru = None
        self.aktif_liste_adi = ""
        self.guncelleniyor = False 
        
        self.ortak_hesap_haritasi = core.ortak_hesaplari_cikar()
        self.ozel_veriler = core.ozel_veri_yukle()

    def json_guncelle(self):
        self.hesap_listesi.clear()
        for dosya in glob.glob("*.json"):
            if dosya not in ["isim_veritabani.json", "favoriler.json", "veri.json"]:
                self.hesap_listesi.addItem(dosya.replace(".json", ""))

    def ozel_liste_secildi(self, item):
        self.hesap_listesi.clearSelection()
        self.hedef_input.setText("") 
        self.aktif_liste_adi = "" 
        self.ozel_veriler = core.ozel_veri_yukle()
        
        if item.text() == "⭐ Favoriler":
            favs = [v for v in self.ozel_veriler.values() if v.get("is_fav")]
            self.tabloyu_doldur(favs)
        elif item.text() == "📝 Not Eklenenler":
            notlular = [v for v in self.ozel_veriler.values() if v.get("not", "").strip() != ""]
            self.tabloyu_doldur(notlular)

    def liste_secildi(self, item):
        self.ozel_liste.clearSelection()
        self.hedef_input.setText(item.text())
        self.aktif_liste_adi = item.text()
        try:
            with open(f"{item.text()}.json", "r", encoding="utf-8") as f:
                self.tabloyu_doldur(json.load(f).get("users", []))
        except Exception as e: self.durum_lbl.setText(f"Hata: {str(e)}")

    def tabloyu_doldur(self, veriler):
        self.guncelleniyor = True
        self.tablo.setSortingEnabled(False)
        self.tablo.setRowCount(0)
        for kisi in veriler: self.satir_ekle(kisi)
        self.durum_lbl.setText(f"Durum: {len(veriler)} kişi yüklendi.")
        
        self.tablo.resizeColumnToContents(2)
        self.tablo.resizeColumnToContents(3)
        self.tablo.resizeColumnToContents(5)
        
        self.guncelleniyor = False
        self.tabloyu_filtrele()

    def satir_ekle(self, kisi):
        ilk_durum = self.guncelleniyor
        self.guncelleniyor = True 
        
        satir = self.tablo.rowCount()
        self.tablo.insertRow(satir)
        
        uname = kisi.get("username", "")
        fname = kisi.get("full_name", "")
        cinsiyet, skor = core.cinsiyet_analizi(uname, fname)
        
        sira = SayisalItem("")
        sira.setData(Qt.UserRole, 0); sira.setTextAlignment(Qt.AlignCenter)
        self.tablo.setItem(satir, 0, sira)
        
        is_fav = self.ozel_veriler.get(uname, {}).get("is_fav", False)
        yildiz_metin = "⭐" if is_fav else "☆"
        yildiz = QTableWidgetItem(yildiz_metin)
        yildiz.setTextAlignment(Qt.AlignCenter)
        yildiz.setForeground(QColor("#f9e2af") if is_fav else QColor("#a6adc8"))
        yildiz.setFont(QFont("Segoe UI", 16))
        yildiz.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tablo.setItem(satir, 1, yildiz)
        
        k_item = QTableWidgetItem(uname)
        k_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        k_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tablo.setItem(satir, 2, k_item)
        
        i_item = QTableWidgetItem(fname)
        i_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        i_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tablo.setItem(satir, 3, i_item)
        
        c_item = QTableWidgetItem(cinsiyet)
        c_item.setTextAlignment(Qt.AlignCenter)
        c_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        c_item.setForeground(QColor("#f5c2e7") if cinsiyet == "Kadın" else QColor("#89b4fa") if cinsiyet == "Erkek" else QColor("#a6adc8"))
        self.tablo.setItem(satir, 4, c_item)
        
        tum_ortaklar = self.ortak_hesap_haritasi.get(uname, [])
        filtrelenmis = [h for h in tum_ortaklar if h != self.aktif_liste_adi]
        ortak_metin = ", ".join(filtrelenmis) if filtrelenmis else "Yok"
        
        o_item = QTableWidgetItem(ortak_metin)
        o_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        o_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        o_item.setForeground(QColor("#a6e3a1"))
        o_item.setToolTip(ortak_metin) 
        self.tablo.setItem(satir, 5, o_item)
        
        not_metni = self.ozel_veriler.get(uname, {}).get("not", "")
        not_item = QTableWidgetItem(not_metni)
        not_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        not_item.setBackground(QColor("#313244")) 
        not_item.setToolTip(not_metni) 
        self.tablo.setItem(satir, 6, not_item)
        
        # YENİ: Aksiyon Butonları (Tarama ve İndirme)
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(4, 2, 4, 2)
        btn_layout.setSpacing(5)
        
        btn_tara = QPushButton("🔍")
        btn_tara.setToolTip(f"{uname} Takipçilerini Tara")
        btn_tara.setFixedSize(30, 30); btn_tara.setCursor(Qt.PointingHandCursor)
        btn_tara.setStyleSheet("background-color: #45475a; border-radius: 4px;")
        
        btn_indir = QPushButton("📥")
        btn_indir.setToolTip(f"{uname} Profil Fotoğrafını İndir")
        btn_indir.setFixedSize(30, 30); btn_indir.setCursor(Qt.PointingHandCursor)
        btn_indir.setStyleSheet("background-color: #45475a; border-radius: 4px;")
        
        btn_layout.addWidget(btn_tara)
        btn_layout.addWidget(btn_indir)
        self.tablo.setCellWidget(satir, 7, btn_widget)
        
        # Buton Sinyalleri
        btn_tara.clicked.connect(lambda _, u=uname: self.bu_kisiyi_tara(u))
        btn_indir.clicked.connect(lambda _, u=uname: self.masaustune_indir(u))
        
        self.guncelleniyor = ilk_durum 

    def bu_kisiyi_tara(self, uname):
        self.hedef_input.setText(uname)
        self.tarama_baslat()

    def masaustune_indir(self, uname):
        self.durum_lbl.setText(f"Durum: {uname} HD profil fotoğrafı indiriliyor...")
        self.download_motoru = ProfilResmiIndirici(uname)
        self.download_motoru.resim_hazir.connect(self.indirilen_resmi_kaydet)
        self.download_motoru.start()

    def indirilen_resmi_kaydet(self, uname, data):
        if data:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            path = os.path.join(desktop, f"{uname}_profil.jpg")
            with open(path, "wb") as f:
                f.write(data)
            self.durum_lbl.setText(f"Durum: {uname} fotoğrafı Masaüstüne kaydedildi! ✅")
        else:
            self.durum_lbl.setText(f"Durum: {uname} fotoğrafı alınamadı (Hesap gizli veya engelli). ❌")

    def hucre_tiklandi(self, satir, sutun):
        if sutun == 1:
            uname = self.tablo.item(satir, 2).text()
            yildiz = self.tablo.item(satir, 1)
            
            # Favori mantığı artık tamamen izole
            is_fav = (yildiz.text() == "☆")
            yildiz.setText("⭐" if is_fav else "☆")
            yildiz.setForeground(QColor("#f9e2af") if is_fav else QColor("#a6adc8"))
            
            fname = self.tablo.item(satir, 3).text()
            note = self.tablo.item(satir, 6).text()
            
            core.ozel_veri_kaydet(uname, fname, is_fav, note)
            self.ozel_veriler = core.ozel_veri_yukle()

    def not_degisti(self, item):
        if self.guncelleniyor: return 
        if item.column() == 6:
            satir = item.row()
            uname = self.tablo.item(satir, 2).text()
            fname = self.tablo.item(satir, 3).text()
            not_metni = item.text()
            
            item.setToolTip(not_metni)
            
            # Not yazıldığında favori durumunu ELLEME, sadece notu kaydet.
            is_fav = (self.tablo.item(satir, 1).text() == "⭐")
            
            self.tablo.blockSignals(True)
            core.ozel_veri_kaydet(uname, fname, is_fav, not_metni)
            self.ozel_veriler = core.ozel_veri_yukle()
            self.tablo.blockSignals(False)

    def profile_git(self, satir, sutun):
        if sutun not in [6, 7]: # Not veya butonlara tıklayınca siteye gitmesin
            webbrowser.open(f"https://www.instagram.com/{self.tablo.item(satir, 2).text()}/")

    def eventFilter(self, source, event):
        if source == self.tablo.viewport():
            if event.type() == QEvent.MouseMove:
                index = self.tablo.indexAt(event.pos())
                if index.isValid() and index.column() in [2, 3]:
                    uname = self.tablo.item(index.row(), 2).text()
                    if uname != self.suanki_hover:
                        self.suanki_hover = uname
                        self.foto_popup.setText("HD Resim\nAranıyor ⏳")
                        self.resim_motoru = ProfilResmiIndirici(uname)
                        self.resim_motoru.resim_hazir.connect(self.popup_bas)
                        self.resim_motoru.start()
                    self.foto_popup.move(event.globalPos().x() + 15, event.globalPos().y() + 15)
                    self.foto_popup.show()
                else:
                    self.foto_popup.hide(); self.suanki_hover = ""
            elif event.type() == QEvent.Leave:
                self.foto_popup.hide(); self.suanki_hover = ""
        return super().eventFilter(source, event)

    def popup_bas(self, uname, data):
        if uname == self.suanki_hover:
            if data:
                p = QPixmap(); p.loadFromData(data)
                self.foto_popup.setPixmap(p.scaled(250, 250, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            else:
                self.foto_popup.setText("Gizli Profil\n❌")

    def tarama_baslat(self):
        hedef = self.hedef_input.text()
        if not hedef or hedef in ["Favoriler", "📝 Not Eklenenler"]: return
        self.cek_btn.setEnabled(False)
        self.tablo.setRowCount(0)
        self.cekme_motoru = VeriCekmeMotoru(hedef)
        self.cekme_motoru.bilgi_sinyali.connect(lambda msg: self.durum_lbl.setText(msg))
        self.cekme_motoru.anlik_veri_sinyali.connect(self.satir_ekle)
        self.cekme_motoru.islem_bitti_sinyali.connect(self.tarama_bitti)
        self.cekme_motoru.start()

    def tarama_bitti(self, dosya):
        self.cek_btn.setEnabled(True)
        self.ortak_hesap_haritasi = core.ortak_hesaplari_cikar() 
        self.json_guncelle()
        self.tabloyu_filtrele()

    def tabloyu_filtrele(self):
        self.tablo.setSortingEnabled(False)
        aranan, cinsiyet = self.arama_input.text().lower(), self.cinsiyet_filtresi.currentText()
        if cinsiyet == "Tümü": cinsiyet = ""
        
        for r in range(self.tablo.rowCount()):
            u, i, c = self.tablo.item(r, 2).text().lower(), self.tablo.item(r, 3).text().lower(), self.tablo.item(r, 4).text()
            self.tablo.setRowHidden(r, not ((aranan in u or aranan in i) and (not cinsiyet or c == cinsiyet)))
            
        sira = 1
        for r in range(self.tablo.rowCount()):
            if not self.tablo.isRowHidden(r):
                self.tablo.item(r, 0).setText(str(sira))
                self.tablo.item(r, 0).setData(Qt.UserRole, sira)
                sira += 1
        self.tablo.setSortingEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = InstagramAnalizArayuzu()
    p.show()
    sys.exit(app.exec_())