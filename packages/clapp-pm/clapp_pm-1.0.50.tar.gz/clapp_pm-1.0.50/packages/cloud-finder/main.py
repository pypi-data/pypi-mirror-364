import flet as ft
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import mimetypes
import platform
import json
import threading

class FileHistory:
    def __init__(self):
        self.recent_files = []
        self.favorites = []
        self.load_history()
    
    def add_recent(self, path):
        if path not in self.recent_files:
            self.recent_files.insert(0, path)
            self.recent_files = self.recent_files[:10]
            self.save_history()
    
    def add_favorite(self, path):
        if path not in self.favorites:
            self.favorites.append(path)
            self.save_history()
    
    def remove_favorite(self, path):
        if path in self.favorites:
            self.favorites.remove(path)
            self.save_history()
    
    def load_history(self):
        try:
            with open('file_history.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.recent_files = data.get('recent', [])
                self.favorites = data.get('favorites', [])
        except (FileNotFoundError, json.JSONDecodeError):
            # Dosya yoksa veya bozuksa varsayılan değerler kullan
            self.recent_files = []
            self.favorites = []
    
    def save_history(self):
        try:
            with open('file_history.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'recent': self.recent_files,
                    'favorites': self.favorites
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Geçmiş kaydetme hatası: {e}")

class CloudFinder:
    def __init__(self):
        self.current_path = str(Path.home())
        self.selected_items = set()
        self.clipboard = []
        self.clipboard_mode = None  # 'copy' or 'cut'
        self.view_mode = "list"  # "list" or "grid"
        self.show_hidden = False
        self.sort_by = "name"  # "name", "size", "date", "type"
        self.sort_reverse = False
        self.search_term = ""
        self.file_history = FileHistory()
        self.drag_source = None
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.last_selected = None
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Cloud Finder"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.spacing = 0
        page.on_keyboard_event = self._handle_keyboard
        
        # Ana container
        self.main_container = ft.Container(
            expand=True,
            bgcolor="#FFFFFF",
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    self._build_toolbar(),
                    self._build_sidebar_and_content()
                ]
            )
        )
        
        page.add(self.main_container)
        self._load_current_directory()
        
    def _build_toolbar(self):
        """Üst toolbar'ı oluştur"""
        return ft.Container(
            height=50,
            bgcolor="#E3F2FD",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0")),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # Sol taraf - navigasyon butonları
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon="arrow_back",
                                icon_color="#1976D2",
                                tooltip="Geri",
                                on_click=self._go_back
                            ),
                            ft.IconButton(
                                icon="arrow_forward",
                                icon_color="#1976D2",
                                tooltip="İleri",
                                on_click=self._go_forward
                            ),
                            ft.IconButton(
                                icon="arrow_upward",
                                icon_color="#1976D2",
                                tooltip="Üst Klasör",
                                on_click=self._go_up
                            ),
                        ]
                    ),
                    
                    # Orta - yol gösterici ve arama
                    ft.Container(
                        expand=True,
                        margin=ft.margin.only(left=20, right=20),
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    self.current_path,
                                    size=14,
                                    color="#424242",
                                    weight=ft.FontWeight.W_500,
                                    expand=True
                                ),
                                ft.TextField(
                                    hint_text="Dosya ara...",
                                    width=200,
                                    on_change=self._on_search_change,
                                    on_submit=self._perform_search
                                )
                            ]
                        )
                    ),
                    
                    # Sağ taraf - görünüm ve ayarlar
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon="view_list" if self.view_mode == "list" else "grid_view",
                                icon_color="#1976D2",
                                tooltip="Görünüm Değiştir",
                                on_click=self._toggle_view
                            ),
                            ft.IconButton(
                                icon="visibility_off" if self.show_hidden else "visibility",
                                icon_color="#1976D2",
                                tooltip="Gizli Dosyaları Göster/Gizle",
                                on_click=self._toggle_hidden
                            ),
                            ft.PopupMenuButton(
                                icon="sort",
                                tooltip="Sıralama",
                                items=[
                                    ft.PopupMenuItem(text="İsme Göre", on_click=lambda e: self._sort_by("name")),
                                    ft.PopupMenuItem(text="Boyuta Göre", on_click=lambda e: self._sort_by("size")),
                                    ft.PopupMenuItem(text="Tarihe Göre", on_click=lambda e: self._sort_by("date")),
                                    ft.PopupMenuItem(text="Türe Göre", on_click=lambda e: self._sort_by("type")),
                                ]
                            ),
                        ]
                    )
                ]
            )
        )
    
    def _build_sidebar_and_content(self):
        """Sidebar ve ana içerik alanını oluştur"""
        return ft.Row(
            expand=True,
            spacing=0,
            controls=[
                # Sidebar
                ft.Container(
                    width=250,
                    bgcolor="#FAFAFA",
                    border=ft.border.only(right=ft.border.BorderSide(1, "#E0E0E0")),
                    content=ft.Column(
                        expand=True,
                        controls=[
                            # Favoriler
                            ft.Container(
                                padding=ft.padding.all(10),
                                content=ft.Text(
                                    "Favoriler",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color="#757575"
                                )
                            ),
                            ft.Container(
                                padding=ft.padding.only(left=10, right=10, bottom=10),
                                content=ft.Column(
                                    controls=[
                                        self._build_sidebar_item("🏠 Ana Sayfa", str(Path.home()), "home"),
                                        self._build_sidebar_item("📁 Masaüstü", str(Path.home() / "Desktop"), "desktop_windows"),
                                        self._build_sidebar_item("📄 Belgeler", str(Path.home() / "Documents"), "description"),
                                        self._build_sidebar_item("🖼️ Resimler", str(Path.home() / "Pictures"), "image"),
                                        self._build_sidebar_item("🎵 Müzik", str(Path.home() / "Music"), "music_note"),
                                        self._build_sidebar_item("🎬 Videolar", str(Path.home() / "Videos"), "video_library"),
                                        self._build_sidebar_item("📥 İndirilenler", str(Path.home() / "Downloads"), "download"),
                                    ]
                                )
                            ),
                            
                            ft.Divider(height=1, color="#E0E0E0"),
                            
                            # Son Kullanılanlar
                            ft.Container(
                                padding=ft.padding.all(10),
                                content=ft.Text(
                                    "Son Kullanılanlar",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color="#757575"
                                )
                            ),
                            ft.Container(
                                padding=ft.padding.only(left=10, right=10, bottom=10),
                                content=ft.Column(
                                    controls=[self._build_recent_item(path) for path in self.file_history.recent_files[:5]]
                                )
                            ),
                            
                            ft.Divider(height=1, color="#E0E0E0"),
                            
                            # Cihazlar
                            ft.Container(
                                padding=ft.padding.all(10),
                                content=ft.Text(
                                    "Cihazlar",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color="#757575"
                                )
                            ),
                            ft.Container(
                                padding=ft.padding.only(left=10, right=10, bottom=10),
                                content=ft.Column(
                                    controls=[
                                        self._build_sidebar_item("💾 Bu Mac", "/", "computer"),
                                    ]
                                )
                            )
                        ]
                    )
                ),
                
                # Ana içerik alanı
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            # Dosya işlemleri toolbar'ı
                            self._build_file_toolbar(),
                            
                            # Dosya listesi
                            ft.Container(
                                expand=True,
                                content=self._build_file_list()
                            )
                        ]
                    )
                )
            ]
        )
    
    def _build_sidebar_item(self, text, path, icon):
        """Sidebar öğesi oluştur"""
        return ft.Container(
            margin=ft.margin.only(bottom=2),
            content=ft.ListTile(
                leading=ft.Icon(icon, size=16, color="#757575"),
                title=ft.Text(
                    text,
                    size=12,
                    color="#424242"
                ),
                dense=True,
                on_click=lambda e: self._navigate_to_path(path)
            )
        )
    
    def _build_recent_item(self, path):
        """Son kullanılan öğe oluştur"""
        name = os.path.basename(path)
        icon = "folder" if os.path.isdir(path) else self._get_file_icon(name)
        return ft.Container(
            margin=ft.margin.only(bottom=2),
            content=ft.ListTile(
                leading=ft.Icon(icon, size=16, color="#757575"),
                title=ft.Text(
                    name,
                    size=12,
                    color="#424242"
                ),
                subtitle=ft.Text(
                    path,
                    size=10,
                    color="#9E9E9E"
                ),
                dense=True,
                on_click=lambda e: self._navigate_to_path(path)
            )
        )
    
    def _build_file_toolbar(self):
        """Dosya işlemleri toolbar'ı"""
        return ft.Container(
            height=40,
            bgcolor="#FFFFFF",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0")),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # Sol taraf - dosya işlemleri
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon="create_new_folder",
                                icon_color="#1976D2",
                                tooltip="Yeni Klasör",
                                on_click=self._create_new_folder
                            ),
                            ft.IconButton(
                                icon="create",
                                icon_color="#1976D2",
                                tooltip="Yeni Dosya",
                                on_click=self._create_new_file
                            ),
                            ft.IconButton(
                                icon="content_copy",
                                icon_color="#1976D2",
                                tooltip="Kopyala (Ctrl+C)",
                                on_click=self._copy_selected
                            ),
                            ft.IconButton(
                                icon="content_cut",
                                icon_color="#1976D2",
                                tooltip="Kes (Ctrl+X)",
                                on_click=self._cut_selected
                            ),
                            ft.IconButton(
                                icon="content_paste",
                                icon_color="#1976D2",
                                tooltip="Yapıştır (Ctrl+V)",
                                on_click=self._paste_items
                            ),
                            ft.IconButton(
                                icon="delete",
                                icon_color="#D32F2F",
                                tooltip="Sil (Delete)",
                                on_click=self._delete_selected
                            ),
                        ]
                    ),
                    
                    # Sağ taraf - seçim bilgisi
                    ft.Container(
                        padding=ft.padding.only(right=10),
                        content=ft.Text(
                            f"{len(self.selected_items)} öğe seçili" if self.selected_items else "",
                            size=12,
                            color="#757575"
                        )
                    )
                ]
            )
        )
    
    def _build_file_list(self):
        """Dosya listesi oluştur"""
        if self.view_mode == "list":
            self.file_list = ft.ListView(
                expand=True,
                spacing=2,
                padding=ft.padding.all(10)
            )
        else:
            self.file_list = ft.GridView(
                expand=True,
                runs_count=5,
                max_extent=150,
                child_aspect_ratio=1.0,
                spacing=10,
                run_spacing=10,
                padding=ft.padding.all(10)
            )
        return self.file_list
    
    def _load_current_directory(self):
        """Mevcut dizini yükle"""
        try:
            self._show_loading("Yükleniyor...")
            self.file_list.controls.clear()
            
            # Üst dizine git butonu
            if self.current_path != "/":
                self.file_list.controls.append(
                    self._build_file_item("..", "..", True, "folder_open")
                )
            
            # Dizin içeriğini listele
            items = []
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                
                # Gizli dosyaları filtrele
                if not self.show_hidden and item.startswith('.'):
                    continue
                
                try:
                    if os.path.isdir(item_path):
                        items.append((item, item_path, True, "folder"))
                    else:
                        items.append((item, item_path, False, self._get_file_icon(item)))
                except PermissionError:
                    continue
            
            # Arama filtresi uygula
            if self.search_term:
                items = self._filter_items(items)
            
            # Sıralama uygula
            items = self._sort_items(items)
            
            # Görünüm moduna göre oluştur
            for item in items:
                if self.view_mode == "list":
                    self.file_list.controls.append(
                        self._build_file_item(item[0], item[1], item[2], item[3])
                    )
                else:
                    self.file_list.controls.append(
                        self._build_grid_item(item[0], item[1], item[2], item[3])
                    )
            
            self.file_list.update()
            self._hide_loading()
            
        except Exception as e:
            self._show_notification(f"Hata: {e}", "#F44336")
    
    def _build_file_item(self, name, path, is_dir, icon):
        """Dosya öğesi oluştur (liste görünümü)"""
        return ft.Container(
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#FFFFFF"),
            border_radius=ft.border_radius.all(4),
            padding=ft.padding.all(8),
            content=ft.ListTile(
                leading=ft.Icon(icon, color="#1976D2" if is_dir else "#757575"),
                title=ft.Text(
                    name,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color="#212121"
                ),
                subtitle=ft.Text(
                    self._get_file_info(path),
                    size=12,
                    color="#757575"
                ),
                trailing=ft.PopupMenuButton(
                    icon="more_vert",
                    tooltip="Daha fazla",
                    items=[
                        ft.PopupMenuItem(text="Aç", on_click=lambda e: self._open_file(path)),
                        ft.PopupMenuItem(text="Kopyala", on_click=lambda e: self._copy_item(path)),
                        ft.PopupMenuItem(text="Kes", on_click=lambda e: self._cut_item(path)),
                        ft.PopupMenuItem(text="Sil", on_click=lambda e: self._delete_item(path)),
                        ft.PopupMenuItem(text="Favorilere Ekle", on_click=lambda e: self._add_to_favorites(path)),
                    ]
                ),
                on_click=lambda e: self._on_file_click(path, is_dir),
                on_long_press=lambda e: self._on_file_long_press(path),
                selected=path in self.selected_items,
                selected_color="#E3F2FD",
            )
        )
    
    def _build_grid_item(self, name, path, is_dir, icon):
        """Dosya öğesi oluştur (grid görünümü)"""
        return ft.Container(
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E0E0E0"),
            border_radius=ft.border_radius.all(8),
            padding=ft.padding.all(10),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        icon,
                        size=48,
                        color="#1976D2" if is_dir else "#757575"
                    ),
                    ft.Text(
                        name,
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color="#212121",
                        text_align=ft.TextAlign.CENTER,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        self._get_file_info(path),
                        size=10,
                        color="#757575",
                        text_align=ft.TextAlign.CENTER
                    )
                ]
            ),
            on_click=lambda e: self._on_file_click(path, is_dir),
            on_long_press=lambda e: self._on_file_long_press(path),
        )
    
    def _get_file_icon(self, filename):
        """Dosya türüne göre ikon döndür"""
        ext = Path(filename).suffix.lower()
        icon_map = {
            '.txt': 'description',
            '.pdf': 'picture_as_pdf',
            '.doc': 'description',
            '.docx': 'description',
            '.xls': 'table_chart',
            '.xlsx': 'table_chart',
            '.ppt': 'slides',
            '.pptx': 'slides',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.mp3': 'music_note',
            '.mp4': 'video_file',
            '.avi': 'video_file',
            '.zip': 'archive',
            '.rar': 'archive',
            '.py': 'code',
            '.js': 'code',
            '.html': 'code',
            '.css': 'code',
        }
        return icon_map.get(ext, 'insert_drive_file')
    
    def _get_file_info(self, path):
        """Dosya bilgilerini al"""
        try:
            stat = os.stat(path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            if os.path.isdir(path):
                return f"Klasör • {modified.strftime('%d.%m.%Y %H:%M')}"
            else:
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size // 1024} KB"
                else:
                    size_str = f"{size // (1024 * 1024)} MB"
                
                return f"{size_str} • {modified.strftime('%d.%m.%Y %H:%M')}"
        except:
            return "Bilinmeyen"
    
    def _on_file_click(self, path, is_dir):
        """Dosya tıklama olayı"""
        if self.ctrl_pressed:
            # Ctrl + tıklama - çoklu seçim
            if path in self.selected_items:
                self.selected_items.remove(path)
            else:
                self.selected_items.add(path)
            self.last_selected = path
        elif self.shift_pressed and self.last_selected:
            # Shift + tıklama - aralık seçimi
            self._select_range(self.last_selected, path)
        else:
            # Normal tıklama
            if is_dir:
                # Navigasyon geçmişini başlat
                if not hasattr(self, 'navigation_history'):
                    self.navigation_history = []
                    self.current_history_index = -1
                
                # Mevcut yolu geçmişe ekle
                if self.current_path != path:
                    # Geçmişteki mevcut konumdan sonraki tüm geçmişi sil
                    self.navigation_history = self.navigation_history[:self.current_history_index + 1]
                    self.navigation_history.append(self.current_path)
                    self.current_history_index = len(self.navigation_history) - 1
                
                self.current_path = path
                self._load_current_directory()
            else:
                self._open_file(path)
                self.file_history.add_recent(path)
        
        self._load_current_directory()
    
    def _on_file_long_press(self, path):
        """Dosya uzun basma olayı"""
        if path in self.selected_items:
            self.selected_items.remove(path)
        else:
            self.selected_items.add(path)
        self._load_current_directory()
    
    def _select_range(self, start_path, end_path):
        """İki dosya arasındaki tüm dosyaları seç"""
        try:
            # Mevcut dosya listesini al
            current_items = []
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                if not self.show_hidden and item.startswith('.'):
                    continue
                try:
                    if os.path.exists(item_path):
                        current_items.append((item, item_path))
                except PermissionError:
                    continue
            
            # Dosyaları sırala
            current_items.sort(key=lambda x: x[0].lower())
            
            # Başlangıç ve bitiş indekslerini bul
            start_index = -1
            end_index = -1
            
            for i, (name, path) in enumerate(current_items):
                if path == start_path:
                    start_index = i
                if path == end_path:
                    end_index = i
            
            if start_index != -1 and end_index != -1:
                # İndeksleri düzenle (küçük olan başlangıç olsun)
                if start_index > end_index:
                    start_index, end_index = end_index, start_index
                
                # Aralıktaki tüm dosyaları seç
                for i in range(start_index, end_index + 1):
                    _, path = current_items[i]
                    self.selected_items.add(path)
                
                self._show_notification(f"{end_index - start_index + 1} dosya seçildi", "#4CAF50")
            
        except Exception as e:
            self._show_notification(f"Aralık seçimi hatası: {e}", "#F44336")
    
    def _navigate_to_path(self, path):
        """Belirtilen yola git"""
        if os.path.exists(path):
            # Navigasyon geçmişini başlat
            if not hasattr(self, 'navigation_history'):
                self.navigation_history = []
                self.current_history_index = -1
            
            # Mevcut yolu geçmişe ekle
            if self.current_path != path:
                # Geçmişteki mevcut konumdan sonraki tüm geçmişi sil
                self.navigation_history = self.navigation_history[:self.current_history_index + 1]
                self.navigation_history.append(self.current_path)
                self.current_history_index = len(self.navigation_history) - 1
            
            self.current_path = path
            self._load_current_directory()
    
    def _go_back(self, e):
        """Geri git"""
        if not hasattr(self, 'navigation_history'):
            self.navigation_history = []
            self.current_history_index = -1
        
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.current_path = self.navigation_history[self.current_history_index]
            self._load_current_directory()
            self._show_notification("Geri gidildi", "#4CAF50")
        else:
            self._show_notification("Geri gidilecek geçmiş yok", "#FF9800")
    
    def _go_forward(self, e):
        """İleri git"""
        if not hasattr(self, 'navigation_history'):
            self.navigation_history = []
            self.current_history_index = -1
        
        if self.current_history_index < len(self.navigation_history) - 1:
            self.current_history_index += 1
            self.current_path = self.navigation_history[self.current_history_index]
            self._load_current_directory()
            self._show_notification("İleri gidildi", "#4CAF50")
        else:
            self._show_notification("İleri gidilecek geçmiş yok", "#FF9800")
    
    def _go_up(self, e):
        """Üst dizine git"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self._load_current_directory()
    
    def _on_search_change(self, e):
        """Arama terimi değiştiğinde"""
        self.search_term = e.control.value
        self._load_current_directory()
    
    def _perform_search(self, e):
        """Arama yap"""
        self._load_current_directory()
    
    def _toggle_view(self, e):
        """Görünüm değiştir"""
        self.view_mode = "grid" if self.view_mode == "list" else "list"
        self._load_current_directory()
    
    def _toggle_hidden(self, e):
        """Gizli dosyaları göster/gizle"""
        self.show_hidden = not self.show_hidden
        self._load_current_directory()
    
    def _sort_by(self, sort_type):
        """Sıralama türünü değiştir"""
        if self.sort_by == sort_type:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = sort_type
            self.sort_reverse = False
        self._load_current_directory()
    
    def _filter_items(self, items):
        """Arama filtresi uygula"""
        filtered = []
        for item in items:
            if self.search_term.lower() in item[0].lower():
                filtered.append(item)
        return filtered
    
    def _sort_items(self, items):
        """Dosyaları sırala"""
        if self.sort_by == "name":
            items.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "size":
            items.sort(key=lambda x: os.path.getsize(x[1]) if os.path.exists(x[1]) else 0, reverse=self.sort_reverse)
        elif self.sort_by == "date":
            items.sort(key=lambda x: os.path.getmtime(x[1]) if os.path.exists(x[1]) else 0, reverse=self.sort_reverse)
        elif self.sort_by == "type":
            items.sort(key=lambda x: Path(x[0]).suffix.lower(), reverse=self.sort_reverse)
        
        # Klasörleri önce göster
        folders = [item for item in items if item[2]]
        files = [item for item in items if not item[2]]
        return folders + files
    
    def _handle_keyboard(self, e: ft.KeyboardEvent):
        """Klavye olaylarını işle"""
        try:
            # Basit klavye kısayolları
            if e.key == "Delete":
                self._delete_selected()
            elif e.key == "c" and hasattr(e, 'ctrl') and e.ctrl:
                self._copy_selected()
            elif e.key == "v" and hasattr(e, 'ctrl') and e.ctrl:
                self._paste_items()
            elif e.key == "x" and hasattr(e, 'ctrl') and e.ctrl:
                self._cut_selected()
            elif e.key == "a" and hasattr(e, 'ctrl') and e.ctrl:
                self._select_all()
            elif e.key == "Escape":
                self.selected_items.clear()
                self._load_current_directory()
        except Exception as ex:
            print(f"Klavye olayı hatası: {ex}")
    
    def _select_all(self):
        """Tüm dosyaları seç"""
        try:
            self.selected_items.clear()
            
            # Mevcut dizindeki tüm dosyaları al
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                
                # Gizli dosyaları filtrele
                if not self.show_hidden and item.startswith('.'):
                    continue
                
                try:
                    if os.path.exists(item_path):
                        self.selected_items.add(item_path)
                except PermissionError:
                    continue
            
            self._load_current_directory()
            self._show_notification(f"{len(self.selected_items)} dosya seçildi", "#4CAF50")
            
        except Exception as e:
            self._show_notification(f"Tümünü seçme hatası: {e}", "#F44336")
    
    def _create_new_folder(self, e):
        """Yeni klasör oluştur"""
        try:
            folder_name = "Yeni Klasör"
            counter = 1
            while os.path.exists(os.path.join(self.current_path, folder_name)):
                folder_name = f"Yeni Klasör ({counter})"
                counter += 1
            
            os.makedirs(os.path.join(self.current_path, folder_name))
            self._load_current_directory()
            self._show_notification(f"'{folder_name}' klasörü oluşturuldu", "#4CAF50")
        except Exception as e:
            self._show_notification(f"Klasör oluşturma hatası: {e}", "#F44336")
    
    def _create_new_file(self, e):
        """Yeni dosya oluştur"""
        try:
            file_name = "Yeni Dosya.txt"
            counter = 1
            while os.path.exists(os.path.join(self.current_path, file_name)):
                file_name = f"Yeni Dosya ({counter}).txt"
                counter += 1
            
            with open(os.path.join(self.current_path, file_name), 'w') as f:
                f.write("")
            
            self._load_current_directory()
            self._show_notification(f"'{file_name}' dosyası oluşturuldu", "#4CAF50")
        except Exception as e:
            self._show_notification(f"Dosya oluşturma hatası: {e}", "#F44336")
    
    def _copy_selected(self, e=None):
        """Seçili öğeleri kopyala"""
        if self.selected_items:
            self.clipboard = list(self.selected_items)
            self.clipboard_mode = 'copy'
            self._show_notification(f"{len(self.selected_items)} öğe kopyalandı", "#4CAF50")
    
    def _cut_selected(self, e=None):
        """Seçili öğeleri kes"""
        if self.selected_items:
            self.clipboard = list(self.selected_items)
            self.clipboard_mode = 'cut'
            self._show_notification(f"{len(self.selected_items)} öğe kesildi", "#FF9800")
    
    def _copy_item(self, path):
        """Tek dosyayı kopyala"""
        self.selected_items = {path}
        self._copy_selected()
    
    def _cut_item(self, path):
        """Tek dosyayı kes"""
        self.selected_items = {path}
        self._cut_selected()
    
    def _delete_item(self, path):
        """Tek dosyayı sil"""
        self.selected_items = {path}
        self._delete_selected()
    
    def _paste_items(self, e=None):
        """Pano öğelerini yapıştır"""
        if not self.clipboard:
            return
        
        success_count = 0
        for source_path in self.clipboard:
            try:
                source_name = os.path.basename(source_path)
                dest_path = os.path.join(self.current_path, source_name)
                
                # Aynı isimde dosya varsa numara ekle
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(source_name)
                    dest_path = os.path.join(self.current_path, f"{name} ({counter}){ext}")
                    counter += 1
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
                
                # Kesme işlemi ise kaynak dosyayı sil
                if self.clipboard_mode == 'cut':
                    if os.path.isdir(source_path):
                        shutil.rmtree(source_path)
                    else:
                        os.remove(source_path)
                
                success_count += 1
                
            except Exception as e:
                self._show_notification(f"Yapıştırma hatası: {e}", "#F44336")
        
        self.clipboard.clear()
        self.clipboard_mode = None
        self.selected_items.clear()
        self._load_current_directory()
        
        if success_count > 0:
            action = "yapıştırıldı" if self.clipboard_mode == 'copy' else "taşındı"
            self._show_notification(f"{success_count} öğe {action}", "#4CAF50")
    
    def _delete_selected(self, e=None):
        """Seçili öğeleri sil"""
        if not self.selected_items:
            return
        
        success_count = 0
        for path in self.selected_items:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                success_count += 1
            except Exception as e:
                self._show_notification(f"Silme hatası: {e}", "#F44336")
        
        self.selected_items.clear()
        self._load_current_directory()
        
        if success_count > 0:
            self._show_notification(f"{success_count} öğe silindi", "#4CAF50")
    
    def _add_to_favorites(self, path):
        """Favorilere ekle"""
        self.file_history.add_favorite(path)
        self._show_notification("Favorilere eklendi", "#4CAF50")
    
    def _open_file(self, path):
        """Dosyayı varsayılan uygulamada aç"""
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            elif platform.system() == "Windows":
                os.startfile(path)
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            self._show_notification(f"Dosya açma hatası: {e}", "#F44336")
    
    def _show_notification(self, message, color="#4CAF50"):
        """Bildirim göster"""
        # Basit bildirim - geliştirilecek
        print(f"Bildirim: {message}")
    
    def _show_loading(self, message="Yükleniyor..."):
        """Yükleme göstergesi göster"""
        # Basit yükleme göstergesi
        print(f"⏳ {message}")
    
    def _hide_loading(self):
        """Yükleme göstergesini gizle"""
        # Yükleme tamamlandı
        print("✅ Yükleme tamamlandı")

def main():
    app = CloudFinder()
    ft.app(target=app.main)

if __name__ == "__main__":
    main() 