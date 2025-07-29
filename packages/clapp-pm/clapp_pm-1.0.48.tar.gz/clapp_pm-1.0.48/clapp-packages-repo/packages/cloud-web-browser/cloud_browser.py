import flet as ft
from flet_webview import WebView
import webbrowser
import threading
import time

class CloudWebBrowser:
    def __init__(self):
        self.current_url = "https://www.google.com"
        self.history = []
        self.history_index = -1
        self.bookmarks = []
        self.tabs = []  # Sekmeler listesi
        self.current_tab_index = 0  # Aktif sekme indeksi
        self.downloads = []  # İndirilenler listesi
        
    def main(self, page: ft.Page):
        self.page = page  # Page nesnesini sınıf içinde sakla
        self.is_dark_mode = False  # Tema durumu
        page.title = "Cloud Web Browser"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1400
        page.window_height = 900
        page.window_resizable = True
        page.padding = 0
        
        # URL giriş alanı
        self.url_field = ft.TextField(
            value=self.current_url,
            expand=True,
            border_radius=20,
            bgcolor="white",
            color="black",
            text_size=14,
            on_submit=self.navigate_to_url,
            prefix_icon="language",
            hint_text="URL girin veya arama yapın..."
        )
        
        # Navigasyon butonları
        back_btn = ft.IconButton(
            icon="arrow_back",
            icon_color="blue600",
            on_click=self.go_back,
            tooltip="Geri"
        )
        
        forward_btn = ft.IconButton(
            icon="arrow_forward",
            icon_color="blue600",
            on_click=self.go_forward,
            tooltip="İleri"
        )
        
        refresh_btn = ft.IconButton(
            icon="refresh",
            icon_color="blue600",
            on_click=self.refresh_page,
            tooltip="Yenile"
        )
        
        home_btn = ft.IconButton(
            icon="home",
            icon_color="blue600",
            on_click=self.go_home,
            tooltip="Ana Sayfa"
        )
        
        bookmark_btn = ft.IconButton(
            icon="bookmark_border",
            icon_color="blue600",
            on_click=self.toggle_bookmark,
            tooltip="Yer İmi Ekle/Çıkar"
        )
        
        # external_btn kaldırıldı - hamburger menüye taşındı
        
        # theme_btn kaldırıldı - hamburger menüye taşındı
        
        # Sekme listesi butonu
        tabs_btn = ft.IconButton(
            icon="tab",
            icon_color="blue600",
            on_click=self.toggle_tabs_list,
            tooltip="Sekme Listesi"
        )
        
        # Sekme listesi (başlangıçta gizli) - GridView ile
        self.tabs_list = ft.Container(
            content=ft.GridView(
                controls=[],
                runs_count=3,  # 3 sütun
                max_extent=200,  # Maksimum genişlik
                spacing=5,
                run_spacing=5
            ),
            bgcolor="white",
            border=ft.border.all(1, "grey300"),
            border_radius=10,
            padding=ft.padding.all(10),
            visible=False
        )
        
        # Hamburger menü butonu
        hamburger_btn = ft.IconButton(
            icon="menu",
            icon_color="blue600",
            on_click=self.toggle_quick_access,
            tooltip="Hızlı Erişim Menüsü"
        )
        
        # Navigasyon toolbar'ı
        navigation_bar = ft.Container(
            content=ft.Row(
                controls=[
                    hamburger_btn,
                    ft.VerticalDivider(width=1, color="grey300"),
                    back_btn,
                    forward_btn,
                    refresh_btn,
                    home_btn,
                    bookmark_btn,
                    tabs_btn,
                    ft.VerticalDivider(width=1, color="grey300"),
                    self.url_field,
                    ft.IconButton(
                        icon="search",
                        icon_color="blue600",
                        on_click=self.navigate_to_url,
                        tooltip="Git"
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=5
            ),
            padding=ft.padding.all(10),
            bgcolor="grey50",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "grey300"))
        )
        
        # Hızlı erişim menüsü (NavigationDrawer) - Genişleyen bölümlerle
        self.quick_access_drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # Hızlı Erişim (Genişleyen)
                            ft.ExpansionTile(
                                title=ft.Text("Hızlı Erişim", size=16, weight=ft.FontWeight.BOLD, color="blue600"),
                                leading=ft.Icon("star", color="blue600"),
                                controls=[
                                    ft.ListTile(
                                        leading=ft.Icon("search", color="blue600"),
                                        title=ft.Text("Google"),
                                        on_click=lambda _: self.navigate_to("https://www.google.com")
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("play_arrow", color="red600"),
                                        title=ft.Text("YouTube"),
                                        on_click=lambda _: self.navigate_to("https://www.youtube.com")
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("code", color="grey600"),
                                        title=ft.Text("GitHub"),
                                        on_click=lambda _: self.navigate_to("https://github.com")
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("article", color="black"),
                                        title=ft.Text("Wikipedia"),
                                        on_click=lambda _: self.navigate_to("https://www.wikipedia.org")
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("question_answer", color="orange600"),
                                        title=ft.Text("Stack Overflow"),
                                        on_click=lambda _: self.navigate_to("https://stackoverflow.com")
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("twitter", color="blue600"),
                                        title=ft.Text("Twitter"),
                                        on_click=lambda _: self.navigate_to("https://twitter.com")
                                    )
                                ]
                            ),
                            
                            ft.Divider(color="grey300"),
                            
                            # Yer İmleri
                            ft.ListTile(
                                leading=ft.Icon("bookmark", color="green600"),
                                title=ft.Text("Yer İmleri"),
                                on_click=self.show_bookmarks
                            ),
                            
                            # Geçmiş
                            ft.ListTile(
                                leading=ft.Icon("history", color="purple600"),
                                title=ft.Text("Geçmiş"),
                                on_click=self.show_history
                            ),
                            
                            # İndirilenler
                            ft.ListTile(
                                leading=ft.Icon("download", color="orange600"),
                                title=ft.Text("İndirilenler"),
                                on_click=self.show_downloads
                            ),
                            
                            ft.Divider(color="grey300"),
                            
                            # Varsayılan Tarayıcıda Aç
                            ft.ListTile(
                                leading=ft.Icon("open_in_new", color="blue600"),
                                title=ft.Text("Varsayılan Tarayıcıda Aç"),
                                on_click=self.open_external
                            ),
                            
                            # Tema Değiştir
                            ft.ListTile(
                                leading=ft.Icon("light_mode", color="orange600"),
                                title=ft.Text("Tema Değiştir"),
                                on_click=self.toggle_theme
                            ),
                            
                            ft.Divider(color="grey300"),
                            
                            # Ayarlar
                            ft.ListTile(
                                leading=ft.Icon("settings", color="grey600"),
                                title=ft.Text("Ayarlar"),
                                on_click=self.show_settings
                            )
                        ],
                        spacing=5
                    ),
                    padding=ft.padding.all(20)
                )
            ],
            bgcolor="white",
            selected_index=None,
            on_change=self.on_drawer_change
        )
        
        # WebView alanı
        self.webview = WebView(
            url=self.current_url,
            expand=True,
            on_page_started=self.on_page_started,
            on_page_ended=self.on_page_ended,
            on_web_resource_error=self.on_web_resource_error
        )
        
        # Sekme çubuğu kaldırıldı - sadece sekme listesi kullanılacak
        
        # Ana layout
        page.add(
            navigation_bar,
            self.tabs_list,
            self.webview
        )
        
        # Drawer'ı sayfaya ekle
        page.drawer = self.quick_access_drawer
        
        # İlk sekmeyi başlat
        self.tabs.append({
            'url': 'https://www.google.com',
            'title': 'Google'
        })
        self.update_tabs_display()
        
        # Test için birkaç yer imi ekle
        self.bookmarks = [
            {'url': 'https://www.google.com', 'title': 'Google'},
            {'url': 'https://www.youtube.com', 'title': 'YouTube'},
            {'url': 'https://github.com', 'title': 'GitHub'}
        ]
        
        # Test için geçmiş ekle
        self.history = [
            'https://www.google.com',
            'https://www.youtube.com',
            'https://github.com',
            'https://www.wikipedia.org',
            'https://stackoverflow.com'
        ]
        self.history_index = len(self.history) - 1
    
    def navigate_to_url(self, e):
        """URL'ye git"""
        url = self.url_field.value.strip()
        if not url:
            return
            
        # URL'yi düzelt
        if not url.startswith(('http://', 'https://')):
            if '.' in url:
                url = 'https://' + url
            else:
                url = f'https://www.google.com/search?q={url}'
        
        self.navigate_to(url)
    
    def navigate_to(self, url):
        """Belirtilen URL'ye git"""
        self.add_to_history(url)
        self.current_url = url
        self.url_field.value = url
        self.webview.url = url
        self.webview.update()
        
        # Aktif sekmeyi güncelle
        if self.tabs and self.current_tab_index < len(self.tabs):
            self.tabs[self.current_tab_index]['url'] = url
            # Başlığı güncelle (basit bir yaklaşım)
            if 'google.com' in url:
                self.tabs[self.current_tab_index]['title'] = 'Google'
            elif 'youtube.com' in url:
                self.tabs[self.current_tab_index]['title'] = 'YouTube'
            elif 'github.com' in url:
                self.tabs[self.current_tab_index]['title'] = 'GitHub'
            elif 'wikipedia.org' in url:
                self.tabs[self.current_tab_index]['title'] = 'Wikipedia'
            elif 'stackoverflow.com' in url:
                self.tabs[self.current_tab_index]['title'] = 'Stack Overflow'
            elif 'twitter.com' in url:
                self.tabs[self.current_tab_index]['title'] = 'Twitter'
            else:
                self.tabs[self.current_tab_index]['title'] = 'Web Sayfası'
            self.update_tabs_display()
    
    def add_to_history(self, url):
        """URL'yi geçmişe ekle"""
        # Mevcut indeksten sonraki geçmişi temizle
        self.history = self.history[:self.history_index + 1]
        self.history.append(url)
        self.history_index = len(self.history) - 1
    
    def go_back(self, e):
        """Geri git"""
        if self.history_index > 0:
            self.history_index -= 1
            url = self.history[self.history_index]
            self.current_url = url
            self.url_field.value = url
            self.webview.url = url
            self.webview.update()
    
    def go_forward(self, e):
        """İleri git"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            url = self.history[self.history_index]
            self.current_url = url
            self.url_field.value = url
            self.webview.url = url
            self.webview.update()
    
    def refresh_page(self, e):
        """Sayfayı yenile"""
        self.webview.url = self.current_url
        self.webview.update()
    
    def go_home(self, e):
        """Ana sayfaya git"""
        self.navigate_to("https://www.google.com")
    
    def toggle_bookmark(self, e):
        """Yer imi ekle/çıkar"""
        if self.current_url in self.bookmarks:
            self.bookmarks.remove(self.current_url)
            e.control.icon = "bookmark_border"
            self.show_snackbar("Yer imi kaldırıldı", "orange600")
        else:
            self.bookmarks.append(self.current_url)
            e.control.icon = "bookmark"
            self.show_snackbar("Yer imi eklendi", "green600")
        e.control.update()
    
    def open_external(self, e):
        """Varsayılan tarayıcıda aç"""
        try:
            webbrowser.open(self.current_url)
            self.show_snackbar("Varsayılan tarayıcıda açıldı", "blue600")
        except Exception as e:
            self.show_snackbar(f"Varsayılan tarayıcı açılamadı: {str(e)}", "red600")
    
    def toggle_quick_access(self, e):
        """Hızlı erişim menüsünü aç/kapat"""
        self.page.drawer.open = True
        self.page.update()
    
    def on_drawer_change(self, e):
        """Drawer değişiklik olayı"""
        pass
    
    def show_settings(self, e):
        """Ayarlar menüsünü göster"""
        print("Ayarlar butonuna tıklandı!")  # Debug bilgisi
        
        # Basit bir mesaj göster
        self.show_snackbar("Ayarlar menüsü açılıyor...", "blue600")
        
        # Ayarlar bottom sheet oluştur
        settings_bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # Başlık
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text("Ayarlar", size=20, weight=ft.FontWeight.BOLD),
                                    ft.IconButton(
                                        icon="close",
                                        on_click=self.close_settings
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            padding=ft.padding.all(20)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # Tema ayarları
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Tema", size=16, weight=ft.FontWeight.BOLD, color="blue600"),
                                    ft.Row(
                                        controls=[
                                            ft.ElevatedButton(
                                                "Açık Tema",
                                                icon="light_mode",
                                                on_click=lambda _: self.set_theme(ft.ThemeMode.LIGHT)
                                            ),
                                            ft.ElevatedButton(
                                                "Koyu Tema",
                                                icon="dark_mode",
                                                on_click=lambda _: self.set_theme(ft.ThemeMode.DARK)
                                            )
                                        ],
                                        spacing=10
                                    )
                                ],
                                spacing=10
                            ),
                            padding=ft.padding.all(10)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # Tarayıcı ayarları
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Tarayıcı Ayarları", size=16, weight=ft.FontWeight.BOLD, color="blue600"),
                                    ft.ListTile(
                                        leading=ft.Icon("home", color="blue600"),
                                        title=ft.Text("Ana Sayfa"),
                                        subtitle=ft.Text("https://www.google.com"),
                                        trailing=ft.IconButton(
                                            icon="edit",
                                            on_click=self.edit_homepage
                                        )
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("search", color="blue600"),
                                        title=ft.Text("Arama Motoru"),
                                        subtitle=ft.Text("Google"),
                                        trailing=ft.IconButton(
                                            icon="edit",
                                            on_click=self.edit_search_engine
                                        )
                                    )
                                ],
                                spacing=5
                            ),
                            padding=ft.padding.all(10)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # Gelişmiş ayarlar
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Gelişmiş", size=16, weight=ft.FontWeight.BOLD, color="blue600"),
                                    ft.ListTile(
                                        leading=ft.Icon("history", color="blue600"),
                                        title=ft.Text("Geçmişi Temizle"),
                                        on_click=self.clear_history
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("bookmark", color="blue600"),
                                        title=ft.Text("Yer İmlerini Yönet"),
                                        on_click=self.manage_bookmarks
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon("info", color="blue600"),
                                        title=ft.Text("Hakkında"),
                                        on_click=self.show_about
                                    )
                                ],
                                spacing=5
                            ),
                            padding=ft.padding.all(10)
                        )
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.all(20),
                height=500
            ),
            open=True
        )
        
        # Bottom sheet'i sayfaya ekle ve aç
        self.page.overlay.append(settings_bottom_sheet)
        self.page.drawer.open = False
        self.page.update()
        print("Bottom sheet açıldı!")  # Debug bilgisi
    
    def toggle_theme(self, e):
        """Tema değiştir"""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()
        self.page.drawer.open = False
        self.page.update()
    
    def toggle_tabs_list(self, e):
        """Sekme listesini aç/kapat"""
        self.tabs_list.visible = not self.tabs_list.visible
        if self.tabs_list.visible:
            self.update_tabs_list()
        self.tabs_list.update()
    
    def update_tabs_list(self):
        """Sekme listesini güncelle - GridView ile"""
        self.tabs_list.content.controls.clear()
        
        # Yeni sekme butonu (en üstte)
        new_tab_btn = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon("add", color="blue600", size=24),
                    ft.Text("Yeni Sekme", color="blue600", size=12, text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=ft.padding.all(12),
            bgcolor="blue50",
            border_radius=8,
            on_click=self.new_tab
        )
        self.tabs_list.content.controls.append(new_tab_btn)
        
        # Mevcut sekmeler
        for i, tab in enumerate(self.tabs):
            is_active = i == self.current_tab_index
            
            # Sekme içeriği
            tab_content = [
                ft.Icon("tab", color="blue600" if is_active else "grey600", size=20),
                ft.Text(tab['title'], color="blue600" if is_active else "black", size=11, text_align=ft.TextAlign.CENTER)
            ]
            
            # Kapatma butonu ekle (sadece birden fazla sekme varsa)
            if len(self.tabs) > 1:
                tab_content.append(
                    ft.IconButton(
                        icon="close",
                        icon_size=14,
                        icon_color="red600",
                        on_click=lambda e, idx=i: self.close_tab_from_list(idx)
                    )
                )
            
            tab_item = ft.Container(
                content=ft.Column(
                    controls=tab_content,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3
                ),
                padding=ft.padding.all(10),
                bgcolor="blue100" if is_active else "grey50",
                border_radius=8,
                border=ft.border.all(1, "blue300" if is_active else "grey300"),
                on_click=lambda e, idx=i: self.switch_tab_from_list(idx)
            )
            self.tabs_list.content.controls.append(tab_item)
    
    def new_tab(self, e):
        """Yeni sekme aç"""
        new_tab_index = len(self.tabs)
        self.tabs.append({
            'url': 'https://www.google.com',
            'title': 'Yeni Sekme'
        })
        self.current_tab_index = new_tab_index
        self.update_tabs_display()
        self.navigate_to('https://www.google.com')
        # Sekme listesini güncelle ve gizle
        if self.tabs_list.visible:
            self.update_tabs_list()
            self.tabs_list.visible = False
            self.tabs_list.update()
    
    def switch_tab_from_list(self, tab_index):
        """Sekme listesinden sekme değiştir"""
        self.switch_tab(tab_index)
        # Sekme listesini gizle
        self.tabs_list.visible = False
        self.tabs_list.update()
    
    def close_tab_from_list(self, tab_index):
        """Sekme listesinden sekme kapat"""
        self.close_tab(tab_index)
        # Sekme listesini güncelle
        if self.tabs_list.visible:
            self.update_tabs_list()
            self.tabs_list.update()
    
    def switch_tab(self, tab_index):
        """Sekme değiştir"""
        if 0 <= tab_index < len(self.tabs):
            self.current_tab_index = tab_index
            tab = self.tabs[tab_index]
            self.current_url = tab['url']
            self.url_field.value = tab['url']
            self.webview.url = tab['url']
            self.update_tabs_display()
            self.webview.update()
            self.url_field.update()
    
    def update_tabs_display(self):
        """Sekme çubuğunu güncelle - artık kullanılmıyor"""
        # Sekme çubuğu kaldırıldı, bu metod artık gerekli değil
        pass
    
    def close_tab(self, tab_index):
        """Sekme kapat"""
        if len(self.tabs) > 1:
            self.tabs.pop(tab_index)
            if self.current_tab_index >= len(self.tabs):
                self.current_tab_index = len(self.tabs) - 1
            if self.tabs:
                self.switch_tab(self.current_tab_index)
            self.update_tabs_display()
    
    def show_snackbar(self, message, color):
        """Snackbar mesajı göster"""
        # Basit bir mesaj gösterme (gerçek uygulamada daha gelişmiş olabilir)
        print(f"Mesaj: {message}")
    
    def on_page_started(self, e):
        """Sayfa yüklenmeye başladığında"""
        print(f"Sayfa yükleniyor: {e.data}")
    
    def on_page_ended(self, e):
        """Sayfa yüklendiğinde"""
        print(f"Sayfa yüklendi: {e.data}")
        # URL'yi güncelle
        if e.data and e.data != self.current_url:
            self.current_url = e.data
            self.url_field.value = e.data
            self.url_field.update()
    
    def on_web_resource_error(self, e):
        """Web kaynağı hatası"""
        print(f"Web kaynağı hatası: {e.data}")
    
    def set_theme(self, theme_mode):
        """Tema ayarla"""
        self.page.theme_mode = theme_mode
        self.is_dark_mode = (theme_mode == ft.ThemeMode.DARK)
        self.page.update()
        self.show_snackbar(f"Tema değiştirildi: {'Koyu' if self.is_dark_mode else 'Açık'}", "green600")
    
    def edit_homepage(self, e):
        """Ana sayfa düzenle"""
        self.show_snackbar("Ana sayfa düzenleme yakında eklenecek", "blue600")
    
    def edit_search_engine(self, e):
        """Arama motoru düzenle"""
        self.show_snackbar("Arama motoru düzenleme yakında eklenecek", "blue600")
    
    def clear_history(self, e):
        """Geçmişi temizle"""
        self.history = []
        self.history_index = -1
        self.show_snackbar("Geçmiş temizlendi", "green600")
    
    def manage_bookmarks(self, e):
        """Yer imlerini yönet"""
        self.show_snackbar("Yer imleri yönetimi yakında eklenecek", "blue600")
    
    def show_about(self, e):
        """Hakkında bilgisi göster"""
        about_dialog = ft.AlertDialog(
            title=ft.Text("Cloud Web Browser", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Modern ve hızlı web tarayıcı", size=16),
                    ft.Text("Python ve Flet ile geliştirilmiştir", size=14, color="grey600"),
                    ft.Divider(color="grey300"),
                    ft.Text("Özellikler:", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("• WebView desteği", size=12),
                    ft.Text("• Sekme yönetimi", size=12),
                    ft.Text("• Hızlı erişim", size=12),
                    ft.Text("• Tema desteği", size=12),
                    ft.Text("• Yer imleri", size=12),
                    ft.Divider(color="grey300"),
                    ft.Text("Yazan: Melih Burak", size=12, color="grey600"),
                    ft.Text("Sürüm: 1.0", size=12, color="grey600")
                ],
                spacing=10
            ),
            actions=[
                ft.TextButton("Kapat", on_click=self.close_about)
            ]
        )
        
        self.page.dialog = about_dialog
        about_dialog.open = True
        self.page.update()
    
    def close_about(self, e):
        """Hakkında dialog'unu kapat"""
        self.page.dialog.open = False
        self.page.update()
    
    def close_settings(self, e):
        """Ayarlar bottom sheet'ini kapat"""
        # Overlay'den bottom sheet'i kaldır
        if self.page.overlay:
            self.page.overlay.pop()
        self.page.update()
    
    def show_bookmarks(self, e):
        """Yer imlerini göster"""
        print("Yer imleri butonuna tıklandı!")  # Debug bilgisi
        print(f"Yer imleri sayısı: {len(self.bookmarks)}")  # Debug bilgisi
        
        if not self.bookmarks:
            self.show_snackbar("Henüz yer imi eklenmemiş", "orange600")
            return
        
        # Yer imleri bottom sheet oluştur
        bookmarks_bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # Başlık
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text("Yer İmleri", size=20, weight=ft.FontWeight.BOLD),
                                    ft.IconButton(
                                        icon="close",
                                        on_click=self.close_bookmarks
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            padding=ft.padding.all(20)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # Yer imleri listesi
                        *[ft.ListTile(
                            leading=ft.Icon("bookmark", color="green600"),
                            title=ft.Text(bookmark['title']),
                            subtitle=ft.Text(bookmark['url']),
                            trailing=ft.IconButton(
                                icon="delete",
                                icon_color="red600",
                                on_click=lambda e, url=bookmark['url']: self.remove_bookmark(url)
                            ),
                            on_click=lambda e, url=bookmark['url']: self.navigate_to_bookmark(url)
                        ) for bookmark in self.bookmarks]
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.all(20),
                height=400
            ),
            open=True
        )
        
        # Bottom sheet'i sayfaya ekle
        self.page.overlay.append(bookmarks_bottom_sheet)
        self.page.drawer.open = False
        self.page.update()
    
    def close_bookmarks(self, e):
        """Yer imleri bottom sheet'ini kapat"""
        if self.page.overlay:
            self.page.overlay.pop()
        self.page.update()
    
    def navigate_to_bookmark(self, url):
        """Yer imine git"""
        self.navigate_to(url)
        self.close_bookmarks(None)
    
    def remove_bookmark(self, url):
        """Yer imini kaldır"""
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        self.show_snackbar("Yer imi kaldırıldı", "green600")
        # Bottom sheet'i yenile
        self.close_bookmarks(None)
        self.show_bookmarks(None)
    
    def show_history(self, e):
        """Geçmişi göster"""
        print("Geçmiş butonuna tıklandı!")  # Debug bilgisi
        print(f"Geçmiş sayısı: {len(self.history)}")  # Debug bilgisi
        
        if not self.history:
            self.show_snackbar("Geçmiş boş", "orange600")
            return
        
        # Geçmiş bottom sheet oluştur
        history_bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # Başlık
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text("Geçmiş", size=20, weight=ft.FontWeight.BOLD),
                                    ft.IconButton(
                                        icon="close",
                                        on_click=self.close_history
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            padding=ft.padding.all(20)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # Geçmiş listesi (son 20 kayıt)
                        *[ft.ListTile(
                            leading=ft.Icon("history", color="purple600"),
                            title=ft.Text(url[:50] + "..." if len(url) > 50 else url),
                            subtitle=ft.Text(f"Ziyaret: {i+1}"),
                            on_click=lambda e, url=url: self.navigate_to_history(url)
                        ) for i, url in enumerate(self.history[-20:])]
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.all(20),
                height=400
            ),
            open=True
        )
        
        # Bottom sheet'i sayfaya ekle
        self.page.overlay.append(history_bottom_sheet)
        self.page.drawer.open = False
        self.page.update()
    
    def close_history(self, e):
        """Geçmiş bottom sheet'ini kapat"""
        if self.page.overlay:
            self.page.overlay.pop()
        self.page.update()
    
    def navigate_to_history(self, url):
        """Geçmişten URL'ye git"""
        self.navigate_to(url)
        self.close_history(None)
    
    def show_downloads(self, e):
        """İndirilenleri göster"""
        print("İndirilenler butonuna tıklandı!")  # Debug bilgisi
        print(f"İndirilenler sayısı: {len(self.downloads)}")  # Debug bilgisi
        
        # İndirilenler bottom sheet oluştur
        downloads_bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # Başlık
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text("İndirilenler", size=20, weight=ft.FontWeight.BOLD),
                                    ft.IconButton(
                                        icon="close",
                                        on_click=self.close_downloads
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            padding=ft.padding.all(20)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # Test indirme butonu
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Test İndirme Başlat",
                                icon="download",
                                on_click=self.start_test_download
                            ),
                            padding=ft.padding.all(10)
                        ),
                        
                        ft.Divider(color="grey300"),
                        
                        # İndirilenler listesi
                        *([ft.ListTile(
                            leading=ft.Icon("file_download", color="green600"),
                            title=ft.Text(download['filename']),
                            subtitle=ft.Text(f"Boyut: {download['size']} - Durum: {download['status']}"),
                            trailing=ft.IconButton(
                                icon="delete",
                                icon_color="red600",
                                on_click=lambda e, filename=download['filename']: self.remove_download(filename)
                            )
                        ) for download in self.downloads] if self.downloads else [
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon("download", color="orange600", size=48),
                                        ft.Text("Henüz indirme yok", size=16, color="grey600"),
                                        ft.Text("Test indirme butonunu kullanın", size=12, color="grey600")
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10
                                ),
                                padding=ft.padding.all(30)
                            )
                        ])
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.all(20),
                height=400
            ),
            open=True
        )
        
        # Bottom sheet'i sayfaya ekle
        self.page.overlay.append(downloads_bottom_sheet)
        self.page.drawer.open = False
        self.page.update()
    
    def close_downloads(self, e):
        """İndirilenler bottom sheet'ini kapat"""
        if self.page.overlay:
            self.page.overlay.pop()
        self.page.update()
    
    def start_test_download(self, e):
        """Test indirme başlat"""
        import time
        import random
        
        # Test dosya adları
        test_files = [
            "test_document.pdf",
            "sample_image.jpg", 
            "example_video.mp4",
            "data_file.xlsx",
            "archive.zip"
        ]
        
        # Rastgele test dosyası seç
        filename = random.choice(test_files)
        file_size = f"{random.randint(1, 100)}.{random.randint(0, 9)} MB"
        
        # İndirme ekle
        download = {
            'filename': filename,
            'size': file_size,
            'status': 'İndiriliyor...',
            'progress': 0
        }
        
        self.downloads.append(download)
        self.show_snackbar(f"İndirme başlatıldı: {filename}", "green600")
        
        # İndirme simülasyonu (gerçek uygulamada threading kullanılır)
        def simulate_download():
            for i in range(101):
                download['progress'] = i
                if i == 100:
                    download['status'] = 'Tamamlandı'
                else:
                    download['status'] = f'İndiriliyor... {i}%'
                time.sleep(0.1)
        
        # Basit simülasyon
        download['status'] = 'Tamamlandı'
        download['progress'] = 100
        
        # Bottom sheet'i yenile
        self.close_downloads(None)
        self.show_downloads(None)
    
    def remove_download(self, filename):
        """İndirmeyi kaldır"""
        self.downloads = [d for d in self.downloads if d['filename'] != filename]
        self.show_snackbar(f"İndirme kaldırıldı: {filename}", "green600")
        # Bottom sheet'i yenile
        self.close_downloads(None)
        self.show_downloads(None)

def main():
    browser = CloudWebBrowser()
    ft.app(target=browser.main)

if __name__ == "__main__":
    main() 