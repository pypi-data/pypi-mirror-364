import flet as ft
import requests
import subprocess
import threading
import webbrowser
from typing import Dict

class ClappStore:
    def __init__(self):
        self.packages_url = "https://raw.githubusercontent.com/mburakmmm/clapp-packages/main/index.json"
        self.packages_data = []
        self.installed_packages = []
        self.current_page = None
        self.current_tab = 0  # 0: packages, 1: installed, 2: about
        
    def main(self, page: ft.Page):
        self.current_page = page
        page.title = "Clapp Store"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.padding = 20
        
        self.create_main_layout()
        self.load_packages()
        
    def create_main_layout(self):
        # Header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.STORE, size=40, color=ft.Colors.BLUE_400),
                    ft.Text("Clapp Store", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Python & Lua Uygulama Mağazası", size=16, color=ft.Colors.GREY_400),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.only(bottom=20),
        )
        
        # Arama çubuğu
        self.search_field = ft.TextField(
            hint_text="Uygulama ara...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.filter_packages,
            expand=True,
        )
        
        search_row = ft.Row(
            controls=[
                self.search_field,
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    on_click=self.refresh_packages,
                    tooltip="Paketleri Yenile"
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Tab butonları
        self.tab_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Tüm Uygulamalar",
                    icon=ft.Icons.APPS,
                    on_click=self.switch_to_packages,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_400,
                        color=ft.Colors.WHITE,
                    ),
                ),
                ft.ElevatedButton(
                    "Yüklü Uygulamalar",
                    icon=ft.Icons.DOWNLOAD_DONE,
                    on_click=self.switch_to_installed,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREY_400,
                        color=ft.Colors.WHITE,
                    ),
                ),
                ft.ElevatedButton(
                    "Hakkında",
                    icon=ft.Icons.INFO,
                    on_click=self.switch_to_about,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREY_400,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # İçerik alanı
        self.content_area = ft.Container(
            content=self.create_packages_view(),
            expand=True,
        )
        
        self.current_page.add(header, search_row, self.tab_buttons, self.content_area)
        
    def create_packages_view(self):
        self.packages_list = ft.ListView(expand=1, spacing=10)
        return ft.Container(content=self.packages_list, expand=True)
        
    def create_installed_view(self):
        self.installed_list = ft.Column(expand=1, spacing=10, scroll=ft.ScrollMode.AUTO)
        return ft.Container(content=self.installed_list, expand=True)
        
    def create_about_view(self):
        about_content = ft.Column(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.STORE, color=ft.Colors.BLUE_400),
                                    title=ft.Text("Clapp Store", size=20, weight=ft.FontWeight.BOLD),
                                    subtitle=ft.Text("Python & Lua Uygulama Mağazası"),
                                ),
                                ft.Divider(),
                                ft.Container(
                                    content=ft.Text(
                                        "Clapp Store, clapp paket yöneticisinin grafiksel kullanıcı arayüzüdür. "
                                        "Python ve Lua uygulamalarını kolayca keşfedebilir, yükleyebilir ve yönetebilirsiniz.",
                                        size=16,
                                    ),
                                    padding=20,
                                ),
                            ],
                        ),
                        padding=20,
                    ),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.CODE, color=ft.Colors.GREEN_400),
                                    title=ft.Text("Clapp Paket Yöneticisi", size=18, weight=ft.FontWeight.BOLD),
                                ),
                                ft.Divider(),
                                ft.Container(
                                    content=ft.Text(
                                        "Clapp, Python ve Lua uygulamalarını komut satırından kolayca yükleyip "
                                        "çalıştırmanızı sağlayan hafif bir paket yöneticisidir.",
                                        size=16,
                                    ),
                                    padding=20,
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.ElevatedButton(
                                                "GitHub'da Görüntüle",
                                                icon=ft.Icons.LAUNCH,
                                                on_click=self.open_clapp_github,
                                            ),
                                        ],
                                    ),
                                    padding=ft.padding.only(left=20, right=20, bottom=20),
                                ),
                            ],
                        ),
                        padding=20,
                    ),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.INVENTORY, color=ft.Colors.ORANGE_400),
                                    title=ft.Text("Paket Deposu", size=18, weight=ft.FontWeight.BOLD),
                                ),
                                ft.Divider(),
                                ft.Container(
                                    content=ft.Text(
                                        "Tüm paketler GitHub'daki clapp-packages deposunda saklanır ve "
                                        "otomatik olarak güncellenir.",
                                        size=16,
                                    ),
                                    padding=20,
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.ElevatedButton(
                                                "Paket Deposunu Görüntüle",
                                                icon=ft.Icons.LAUNCH,
                                                on_click=self.open_packages_github,
                                            ),
                                        ],
                                    ),
                                    padding=ft.padding.only(left=20, right=20, bottom=20),
                                ),
                            ],
                        ),
                        padding=20,
                    ),
                ),
            ],
            spacing=20,
        )
        about_list = ft.ListView(
            expand=1,
            spacing=20,
            controls=[about_content]
        )
        return ft.Container(
            content=about_list,
            expand=True,
        )
        
    def open_clapp_github(self, e):
        webbrowser.open("https://github.com/mburakmmm/clapp")
        
    def open_packages_github(self, e):
        webbrowser.open("https://github.com/mburakmmm/clapp-packages")
        
    def load_packages(self):
        try:
            response = requests.get(self.packages_url, timeout=10)
            if response.status_code == 200:
                self.packages_data = response.json()
                self.update_packages_display()
                self.load_installed_packages()
            else:
                self.show_error("Paketler yüklenemedi", f"HTTP {response.status_code}")
        except Exception as e:
            self.show_error("Bağlantı hatası", str(e))
            
    def update_packages_display(self):
        self.packages_list.controls.clear()
        for package in self.packages_data:
            card = self.create_package_card(package)
            self.packages_list.controls.append(card)
        self.current_page.update()
        
    def create_package_card(self, package: Dict) -> ft.Card:
        name = package.get("name", "Bilinmeyen")
        version = package.get("version", "1.0.0")
        description = package.get("description", "Açıklama yok")
        language = package.get("language", "python")
        
        lang_icon = ft.Icons.CODE
        lang_color = ft.Colors.BLUE_400 if language == "python" else ft.Colors.GREEN_400
        
        is_installed = self.is_package_installed(name)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(lang_icon, color=lang_color),
                            title=ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"v{version} • {language}"),
                        ),
                        ft.Container(
                            content=ft.Text(
                                description,
                                size=14,
                                color=ft.Colors.GREY_400,
                                max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            padding=ft.padding.only(left=16, right=16),
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "Yükle" if not is_installed else "Çalıştır",
                                        icon=ft.Icons.DOWNLOAD if not is_installed else ft.Icons.PLAY_ARROW,
                                        on_click=self.create_install_callback(package, is_installed),
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=ft.Colors.BLUE_400 if not is_installed else ft.Colors.GREEN_400,
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE if is_installed else ft.Icons.INFO,
                                        on_click=self.create_action_callback(package, is_installed),
                                        tooltip="Kaldır" if is_installed else "Detaylar",
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=ft.padding.only(left=16, right=16, bottom=16),
                        ),
                    ],
                ),
                padding=10,
            ),
        )
        
    def create_install_callback(self, package, is_installed):
        def callback(e):
            if is_installed:
                self.run_package(package)
            else:
                self.install_package(package)
        return callback
        
    def create_action_callback(self, package, is_installed):
        def callback(e):
            if is_installed:
                package_name = package.get("name")
                self.uninstall_package_by_name(package_name)
            else:
                self.show_package_info(package)
        return callback
        
    def is_package_installed(self, package_name: str) -> bool:
        try:
            result = subprocess.run(["clapp", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    # Başlık satırlarını atla
                    if (line.startswith('📦') or 
                        line.startswith('==') or 
                        line.startswith('Ad') or 
                        line.startswith('---') or 
                        not line):
                        continue
                    
                    # İlk sütunu kontrol et
                    parts = line.split()
                    if parts and parts[0] == package_name:
                        return True
            return False
        except:
            return False
            
    def load_installed_packages(self):
        try:
            result = subprocess.run(["clapp", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                self.installed_packages = []
                
                # Tablo formatını parse et
                for line in lines:
                    line = line.strip()
                    # Başlık satırlarını atla
                    if (line.startswith('📦') or 
                        line.startswith('==') or 
                        line.startswith('Ad') or 
                        line.startswith('---') or 
                        not line):
                        continue
                    
                    # İlk sütunu al (uygulama adı)
                    parts = line.split()
                    if parts:
                        app_name = parts[0]
                        self.installed_packages.append(app_name)
                
                self.update_installed_display()
        except Exception as e:
            print(f"Yüklü paketler yüklenemedi: {e}")
            
    def update_installed_display(self):
        if hasattr(self, 'installed_list'):
            self.installed_list.controls.clear()
            
            if not self.installed_packages:
                self.installed_list.controls.append(
                    ft.Container(
                        content=ft.Text("Henüz yüklü paket yok", size=16, color=ft.Colors.GREY_400),
                        alignment=ft.alignment.center,
                        padding=50,
                    )
                )
            else:
                # Başlık ekle
                self.installed_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"Kurulu Uygulamalar ({len(self.installed_packages)})", 
                                       size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        padding=ft.padding.only(bottom=20),
                    )
                )
                
                for package_name in self.installed_packages:
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.DOWNLOAD_DONE, color=ft.Colors.GREEN_400, size=24),
                                    ft.Container(
                                        content=ft.Text(package_name, weight=ft.FontWeight.BOLD, size=16),
                                        expand=True,
                                        padding=ft.padding.only(left=10),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=self.create_run_callback(package_name),
                                        tooltip="Çalıştır",
                                        icon_color=ft.Colors.GREEN_400,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        on_click=self.create_uninstall_callback(package_name),
                                        tooltip="Kaldır",
                                        icon_color=ft.Colors.RED_400,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            padding=15,
                        ),
                    )
                    self.installed_list.controls.append(card)
                    
            self.current_page.update()
        
    def create_run_callback(self, package_name):
        def callback(e):
            self.run_package_by_name(package_name)
        return callback
        
    def create_uninstall_callback(self, package_name):
        def callback(e):
            self.uninstall_package_by_name(package_name)
        return callback
        
    def install_package(self, package: Dict):
        package_name = package.get("name")
        
        def install_thread():
            try:
                result = subprocess.run(["clapp", "install", package_name], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.current_page.snack_bar = ft.SnackBar(content=ft.Text(f"{package_name} başarıyla yüklendi!"))
                    self.current_page.snack_bar.open = True
                    self.current_page.update()
                    self.load_installed_packages()
                    # Tüm uygulamalar sekmesini yenile
                    if self.current_tab == 0:
                        self.update_packages_display()
                else:
                    self.show_error("Yükleme hatası", result.stderr)
            except Exception as e:
                self.show_error("Yükleme hatası", str(e))
                
        threading.Thread(target=install_thread, daemon=True).start()
        
    def run_package(self, package: Dict):
        package_name = package.get("name")
        self.run_package_by_name(package_name)
        
    def run_package_by_name(self, package_name: str):
        def run_thread():
            try:
                subprocess.run(["clapp", "run", package_name], timeout=60)
            except Exception as e:
                self.show_error("Çalıştırma hatası", str(e))
                
        threading.Thread(target=run_thread, daemon=True).start()
        
    def uninstall_package(self, package: Dict):
        package_name = package.get("name")
        self.uninstall_package_by_name(package_name)
        
    def uninstall_package_by_name(self, package_name: str):
        def uninstall_thread():
            try:
                result = subprocess.run(["clapp", "uninstall", "--yes", package_name], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.current_page.snack_bar = ft.SnackBar(content=ft.Text(f"{package_name} kaldırıldı!"))
                    self.current_page.snack_bar.open = True
                    self.current_page.update()
                    self.load_installed_packages()
                    # Tüm uygulamalar sekmesini yenile
                    if self.current_tab == 0:
                        self.update_packages_display()
                else:
                    self.show_error("Kaldırma hatası", result.stderr)
            except Exception as e:
                self.show_error("Kaldırma hatası", str(e))
                
        threading.Thread(target=uninstall_thread, daemon=True).start()
        
    def show_package_info(self, package: Dict):
        name = package.get("name", "Bilinmeyen")
        version = package.get("version", "1.0.0")
        description = package.get("description", "Açıklama yok")
        language = package.get("language", "python")
        
        dialog = ft.AlertDialog(
            title=ft.Text(name),
            content=ft.Column(
                controls=[
                    ft.Text(f"Versiyon: {version}"),
                    ft.Text(f"Dil: {language}"),
                    ft.Text(f"Açıklama: {description}"),
                ],
                spacing=10,
            ),
            actions=[ft.TextButton("Kapat", on_click=self.close_dialog)],
        )
        
        self.current_page.dialog = dialog
        self.current_page.dialog.open = True
        self.current_page.update()
        
    def close_dialog(self, e):
        self.current_page.dialog.open = False
        self.current_page.update()
        
    def filter_packages(self, e):
        search_term = e.control.value.lower()
        self.packages_list.controls.clear()
        
        for package in self.packages_data:
            name = package.get("name", "").lower()
            description = package.get("description", "").lower()
            
            if search_term in name or search_term in description:
                card = self.create_package_card(package)
                self.packages_list.controls.append(card)
                
        self.current_page.update()
        
    def refresh_packages(self, e):
        self.load_packages()
        self.current_page.snack_bar = ft.SnackBar(content=ft.Text("Paketler yenilendi!"))
        self.current_page.snack_bar.open = True
        self.current_page.update()
        
    def switch_to_packages(self, e):
        self.current_tab = 0
        self.content_area.content = self.create_packages_view()
        self.update_tab_buttons()
        self.load_packages()  # Otomatik yenileme
        self.current_page.update()
        
    def switch_to_installed(self, e):
        self.current_tab = 1
        self.content_area.content = self.create_installed_view()
        self.update_tab_buttons()
        self.load_installed_packages()  # Otomatik yenileme
        self.current_page.update()
        
    def switch_to_about(self, e):
        self.current_tab = 2
        self.content_area.content = self.create_about_view()
        self.update_tab_buttons()
        self.current_page.update()
        
    def update_tab_buttons(self):
        # Tüm butonları gri yap
        for button in self.tab_buttons.controls:
            button.style.bgcolor = ft.Colors.GREY_400
            
        # Aktif butonu mavi yap
        self.tab_buttons.controls[self.current_tab].style.bgcolor = ft.Colors.BLUE_400
            
    def show_error(self, title: str, message: str):
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("Tamam", on_click=self.close_dialog)],
        )
        
        self.current_page.dialog = dialog
        self.current_page.dialog.open = True
        self.current_page.update()

def main(page: ft.Page):
    app = ClappStore()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main) 