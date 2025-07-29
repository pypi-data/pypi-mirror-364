#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Example - Cloud Notepad Test Dosyası
Bu dosya Cloud Notepad uygulamasını test etmek için oluşturulmuştur.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional


class CloudNotepadTest:
    """Cloud Notepad test sınıfı"""
    
    def __init__(self, name: str = "Test"):
        self.name = name
        self.created_at = datetime.now()
        self.features = []
        
    def add_feature(self, feature: str) -> None:
        """Özellik ekle"""
        self.features.append(feature)
        print(f"Özellik eklendi: {feature}")
        
    def get_features(self) -> List[str]:
        """Özellikleri getir"""
        return self.features.copy()
        
    def test_syntax_highlighting(self) -> bool:
        """Syntax highlighting test et"""
        # String test
        test_string = "Bu bir test string'idir"
        
        # Sayı test
        test_number = 42
        test_float = 3.14
        
        # Liste test
        test_list = [1, 2, 3, "test", True]
        
        # Dict test
        test_dict = {
            "key1": "value1",
            "key2": 123,
            "key3": [1, 2, 3]
        }
        
        # Boolean test
        test_bool = True
        test_false = False
        
        # None test
        test_none = None
        
        return True


def main():
    """Ana fonksiyon"""
    print("Cloud Notepad Test Başlatılıyor...")
    
    # Test nesnesi oluştur
    test = CloudNotepadTest("Cloud Notepad")
    
    # Özellikler ekle
    features = [
        "Çoklu sekme desteği",
        "Syntax highlighting",
        "Tema desteği",
        "Cloud senkronizasyon",
        "Bul ve değiştir",
        "Otomatik kaydetme"
    ]
    
    for feature in features:
        test.add_feature(feature)
    
    # Test çalıştır
    if test.test_syntax_highlighting():
        print("Syntax highlighting test başarılı!")
    else:
        print("Syntax highlighting test başarısız!")
    
    print("Test tamamlandı!")


if __name__ == "__main__":
    main() 