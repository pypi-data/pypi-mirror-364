#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Replace Dialog - Bul ve değiştir dialog'u
Metin arama ve değiştirme işlevselliği
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QTextDocument


class FindReplaceDialog(QDialog):
    """Bul ve değiştir dialog'u"""
    
    def __init__(self, parent=None, find_only=True):
        super().__init__(parent)
        self.parent = parent
        self.find_only = find_only
        self.current_match = None
        
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("Bul ve Değiştir")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Bul grubu
        find_group = QGroupBox("Bul")
        find_layout = QGridLayout(find_group)
        
        find_layout.addWidget(QLabel("Aranacak:"), 0, 0)
        self.find_edit = QLineEdit()
        self.find_edit.textChanged.connect(self.find_text_changed)
        find_layout.addWidget(self.find_edit, 0, 1)
        
        # Seçenekler
        self.case_sensitive = QCheckBox("Büyük/küçük harf duyarlı")
        find_layout.addWidget(self.case_sensitive, 1, 0, 1, 2)
        
        self.whole_words = QCheckBox("Tam kelime")
        find_layout.addWidget(self.whole_words, 2, 0, 1, 2)
        
        self.regex = QCheckBox("Düzenli ifade")
        find_layout.addWidget(self.regex, 3, 0, 1, 2)
        
        layout.addWidget(find_group)
        
        # Değiştir grubu (sadece replace modunda)
        if not self.find_only:
            replace_group = QGroupBox("Değiştir")
            replace_layout = QGridLayout(replace_group)
            
            replace_layout.addWidget(QLabel("Değiştirilecek:"), 0, 0)
            self.replace_edit = QLineEdit()
            replace_layout.addWidget(self.replace_edit, 0, 1)
            
            layout.addWidget(replace_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        if self.find_only:
            self.find_button = QPushButton("Bul")
            self.find_button.clicked.connect(self.find_next)
            button_layout.addWidget(self.find_button)
            
            self.find_prev_button = QPushButton("Önceki")
            self.find_prev_button.clicked.connect(self.find_previous)
            button_layout.addWidget(self.find_prev_button)
        else:
            self.find_button = QPushButton("Bul")
            self.find_button.clicked.connect(self.find_next)
            button_layout.addWidget(self.find_button)
            
            self.replace_button = QPushButton("Değiştir")
            self.replace_button.clicked.connect(self.replace_current)
            button_layout.addWidget(self.replace_button)
            
            self.replace_all_button = QPushButton("Tümünü Değiştir")
            self.replace_all_button.clicked.connect(self.replace_all)
            button_layout.addWidget(self.replace_all_button)
        
        self.close_button = QPushButton("Kapat")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # İlk odak
        self.find_edit.setFocus()
        
    def find_text_changed(self):
        """Arama metni değiştiğinde"""
        self.current_match = None
        
    def get_current_editor(self):
        """Mevcut editörü al"""
        if self.parent and hasattr(self.parent, 'tab_widget'):
            return self.parent.tab_widget.currentWidget()
        return None
        
    def find_next(self):
        """Sonraki eşleşmeyi bul"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        search_text = self.find_edit.text()
        if not search_text:
            return
            
        # Arama seçenekleri
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        # Arama yap
        cursor = editor.textCursor()
        if self.current_match is None:
            # İlk arama
            found = editor.find(search_text, flags)
        else:
            # Sonraki arama
            cursor.setPosition(self.current_match + 1)
            editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
            
        if found:
            self.current_match = editor.textCursor().position() - len(search_text)
            self.parent.statusBar().showMessage(f"Eşleşme bulundu: {search_text}")
        else:
            self.current_match = None
            self.parent.statusBar().showMessage("Eşleşme bulunamadı")
            
    def find_previous(self):
        """Önceki eşleşmeyi bul"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        search_text = self.find_edit.text()
        if not search_text:
            return
            
        # Arama seçenekleri
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        # Geriye doğru arama
        flags |= QTextDocument.FindFlag.FindBackward
        
        # Arama yap
        cursor = editor.textCursor()
        if self.current_match is None:
            # İlk arama
            found = editor.find(search_text, flags)
        else:
            # Önceki arama
            cursor.setPosition(self.current_match - 1)
            editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
            
        if found:
            self.current_match = editor.textCursor().position()
            self.parent.statusBar().showMessage(f"Eşleşme bulundu: {search_text}")
        else:
            self.current_match = None
            self.parent.statusBar().showMessage("Eşleşme bulunamadı")
            
    def replace_current(self):
        """Mevcut eşleşmeyi değiştir"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        if self.current_match is None:
            self.find_next()
            return
            
        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
            self.current_match = None
            self.parent.statusBar().showMessage("Değiştirildi")
            
    def replace_all(self):
        """Tüm eşleşmeleri değiştir"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        search_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not search_text:
            return
            
        # Onay al
        reply = QMessageBox.question(
            self, "Tümünü Değiştir",
            f"'{search_text}' metninin tüm eşleşmelerini '{replace_text}' ile değiştirmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Tüm metni al
            full_text = editor.toPlainText()
            
            # Arama seçenekleri
            if self.case_sensitive.isChecked():
                # Büyük/küçük harf duyarlı
                new_text = full_text.replace(search_text, replace_text)
            else:
                # Büyük/küçük harf duyarsız
                import re
                flags = re.IGNORECASE if not self.case_sensitive.isChecked() else 0
                new_text = re.sub(re.escape(search_text), replace_text, full_text, flags=flags)
                
            # Metni güncelle
            editor.setPlainText(new_text)
            
            # İstatistik
            count = full_text.count(search_text) if self.case_sensitive.isChecked() else len(re.findall(re.escape(search_text), full_text, re.IGNORECASE))
            self.parent.statusBar().showMessage(f"{count} eşleşme değiştirildi")
            
    def keyPressEvent(self, event):
        """Tuş basma olayı"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.find_only:
                self.find_next()
            else:
                self.replace_current()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event) 