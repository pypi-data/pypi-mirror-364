import flet as ft
import psutil
import threading
import time
import os
import platform
import json
from datetime import datetime
import requests
from ping3 import ping
import speedtest


class CloudSystem:
    def __init__(self):
        self.tasks = []
        self.system_stats = {}
        self.processes = []
        self.network_stats = {}
        self.update_thread = None
        self.running = True

        
    def main(self, page: ft.Page):
        page.title = "Cloud System - Sistem Yöneticisi"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 1400
        page.window_height = 900
        page.window_resizable = True
        page.padding = 20
        page.spacing = 20
        
        # Ana container
        self.main_container = ft.Container(
            expand=True,
            border_radius=15,
            bgcolor="#1e1e1e",
            padding=20,
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon("cloud", size=40, color="#2196F3"),
                        ft.Text("Cloud System", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("Sistem Yöneticisi", size=16, color="#888888"),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.only(bottom=20)
                ),
                
                                # Navigation tabs
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            text="Süreç Yönetimi",
                            icon="memory",
                            content=self.create_process_manager()
                        ),
                        ft.Tab(
                            text="Sistem İzleme",
                            icon="monitor_heart",
                            content=self.create_system_monitor()
                        ),
                        ft.Tab(
                            text="Görev Yöneticisi",
                            icon="task_alt",
                            content=self.create_task_manager()
                        ),
                        ft.Tab(
                            text="Ağ İzleme",
                            icon="network_check",
                            content=self.create_network_monitor()
                        ),
                        ft.Tab(
                            text="Sistem Bilgileri",
                            icon="info",
                            content=self.create_system_info()
                        ),
                    ],
                    expand=True
                )
            ])
        )
        
        page.add(self.main_container)
        

        
        page.update()
        
        # Sistem istatistiklerini güncelleme thread'ini başlat
        self.start_update_thread()
    
    def create_task_manager(self):
        # Görev yöneticisi bileşenleri
        self.task_input = ft.TextField(
            label="Yeni Görev",
            hint_text="Görev açıklaması girin...",
            expand=True,
            border_radius=10
        )
        
        self.priority_dropdown = ft.Dropdown(
            label="Öncelik",
            options=[
                ft.dropdown.Option("Düşük", "low"),
                ft.dropdown.Option("Orta", "medium"),
                ft.dropdown.Option("Yüksek", "high"),
                ft.dropdown.Option("Kritik", "critical")
            ],
            value="medium",
            border_radius=10
        )
        
        self.task_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Görev Yöneticisi", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row([
                        self.task_input,
                        self.priority_dropdown,
                        ft.ElevatedButton(
                            "Görev Ekle",
                            icon="add",
                            on_click=self.add_task,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10)
                            )
                        )
                    ], spacing=10),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Container(
                    content=self.task_list,
                    expand=True,
                    border=ft.border.all(1, "#444444"),
                    border_radius=10,
                    padding=10
                )
            ]),
            expand=True
        )
    
    def create_system_monitor(self):
        # Sistem izleme bileşenleri
        # İlk değerleri al
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.cpu_usage = ft.ProgressBar(value=cpu_percent/100, color="#2196F3")
        self.ram_usage = ft.ProgressBar(value=memory.percent/100, color="#FF9800")
        self.disk_usage = ft.ProgressBar(value=(disk.used / disk.total), color="#4CAF50")
        
        self.cpu_text = ft.Text(f"CPU: {cpu_percent:.1f}%", color="white")
        self.ram_text = ft.Text(f"RAM: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)", color="white")
        self.disk_text = ft.Text(f"Disk: {(disk.used / disk.total) * 100:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)", color="white")
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Sistem İzleme", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon("memory", color="#2196F3"),
                            ft.Text("CPU Kullanımı", size=16, weight=ft.FontWeight.W_500, color="white"),
                            self.cpu_text
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(self.cpu_usage, height=20, margin=ft.margin.only(bottom=20)),
                        
                        ft.Row([
                            ft.Icon("storage", color="#FF9800"),
                            ft.Text("RAM Kullanımı", size=16, weight=ft.FontWeight.W_500, color="white"),
                            self.ram_text
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(self.ram_usage, height=20, margin=ft.margin.only(bottom=20)),
                        
                        ft.Row([
                            ft.Icon("hard_drive", color="#4CAF50"),
                            ft.Text("Disk Kullanımı", size=16, weight=ft.FontWeight.W_500, color="white"),
                            self.disk_text
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(self.disk_usage, height=20, margin=ft.margin.only(bottom=20)),
                    ]),
                    padding=20,
                    border=ft.border.all(1, "#444444"),
                    border_radius=10
                )
            ]),
            expand=True
        )
    
    def create_process_manager(self):
        # Süreç yönetimi bileşenleri
        self.process_list = ft.ListView(
            expand=True,
            spacing=5,
            padding=10
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Süreç Yönetimi", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.process_list,
                    expand=True,
                    border=ft.border.all(1, "#444444"),
                    border_radius=10,
                    padding=10
                )
            ]),
            expand=True
        )
    

    
    def create_network_monitor(self):
        # Ağ izleme bileşenleri
        try:
            net_io = psutil.net_io_counters()
            sent_mb = net_io.bytes_sent // (1024**2)
            recv_mb = net_io.bytes_recv // (1024**2)
        except:
            sent_mb = 0
            recv_mb = 0
            net_io = type('obj', (object,), {'packets_sent': 0, 'packets_recv': 0})()
        
        # Güncellenebilir text referansları
        self.sent_text = ft.Text(f"{sent_mb:.1f} MB", size=20, weight=ft.FontWeight.BOLD, color="white")
        self.recv_text = ft.Text(f"{recv_mb:.1f} MB", size=20, weight=ft.FontWeight.BOLD, color="white")
        self.total_text = ft.Text(f"{(sent_mb + recv_mb):.1f} MB", size=20, weight=ft.FontWeight.BOLD, color="white")
        self.packets_sent_text = ft.Text(f"Gönderilen: {net_io.packets_sent:,}", size=12, color="white")
        self.packets_recv_text = ft.Text(f"Alınan: {net_io.packets_recv:,}", size=12, color="white")
        
        # Scrollable ListView oluştur
        self.network_content = ft.ListView(
            controls=[
                # Gönderilen Veri
                ft.Container(
                    content=ft.Row([
                        ft.Icon("upload", color="#4CAF50", size=32),
                        ft.Column([
                            ft.Text("Gönderilen", size=14, color="#888888"),
                            self.sent_text
                        ], spacing=2)
                    ], spacing=15),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Alınan Veri
                ft.Container(
                    content=ft.Row([
                        ft.Icon("download", color="#2196F3", size=32),
                        ft.Column([
                            ft.Text("Alınan", size=14, color="#888888"),
                            self.recv_text
                        ], spacing=2)
                    ], spacing=15),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Paket İstatistikleri
                ft.Container(
                    content=ft.Row([
                        ft.Icon("data_usage", color="#FF9800", size=32),
                        ft.Column([
                            ft.Text("Paket İstatistikleri", size=14, color="#888888"),
                            self.packets_sent_text,
                            self.packets_recv_text
                        ], spacing=2)
                    ], spacing=15),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Toplam Trafik
                ft.Container(
                    content=ft.Row([
                        ft.Icon("network_check", color="#9C27B0", size=32),
                        ft.Column([
                            ft.Text("Toplam Trafik", size=14, color="#888888"),
                            self.total_text
                        ], spacing=2)
                    ], spacing=15),
                    padding=ft.padding.only(bottom=20)
                ),
            ],
            expand=True,
            spacing=5
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Ağ İzleme", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.network_content,
                    padding=30,
                    border=ft.border.all(1, "#444444"),
                    border_radius=15,
                    expand=True
                )
            ]),
            expand=True
        )
    
    def create_system_info(self):
        # Sistem bilgileri bileşenleri
        system_info = self.get_system_info()
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Sistem Bilgileri", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.ListView(
                        controls=[
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon("computer", color="#2196F3", size=24),
                                    ft.Text("İşletim Sistemi", size=16, weight=ft.FontWeight.W_500, color="white"),
                                ], spacing=10),
                                padding=ft.padding.only(bottom=5)
                            ),
                            ft.Container(
                                content=ft.Text(f"{platform.system()} {platform.release()}", size=14, color="#CCCCCC"),
                                padding=ft.padding.only(bottom=15, left=34)
                            ),
                            
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon("memory", color="#FF9800", size=24),
                                    ft.Text("Mimari", size=16, weight=ft.FontWeight.W_500, color="white"),
                                ], spacing=10),
                                padding=ft.padding.only(bottom=5)
                            ),
                            ft.Container(
                                content=ft.Text(platform.machine(), size=14, color="#CCCCCC"),
                                padding=ft.padding.only(bottom=15, left=34)
                            ),
                            
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon("speed", color="#4CAF50", size=24),
                                    ft.Text("İşlemci", size=16, weight=ft.FontWeight.W_500, color="white"),
                                ], spacing=10),
                                padding=ft.padding.only(bottom=5)
                            ),
                            ft.Container(
                                content=ft.Text(platform.processor(), size=14, color="#CCCCCC"),
                                padding=ft.padding.only(bottom=15, left=34)
                            ),
                            
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon("code", color="#9C27B0", size=24),
                                    ft.Text("Python Sürümü", size=16, weight=ft.FontWeight.W_500, color="white"),
                                ], spacing=10),
                                padding=ft.padding.only(bottom=5)
                            ),
                            ft.Container(
                                content=ft.Text(platform.python_version(), size=14, color="#CCCCCC"),
                                padding=ft.padding.only(bottom=15, left=34)
                            ),
                            
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon("person", color="#E91E63", size=24),
                                    ft.Text("Kullanıcı", size=16, weight=ft.FontWeight.W_500, color="white"),
                                ], spacing=10),
                                padding=ft.padding.only(bottom=5)
                            ),
                            ft.Container(
                                content=ft.Text(os.getlogin(), size=14, color="#CCCCCC"),
                                padding=ft.padding.only(bottom=15, left=34)
                            ),
                            
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon("folder", color="#607D8B", size=24),
                                    ft.Text("Çalışma Dizini", size=16, weight=ft.FontWeight.W_500, color="white"),
                                ], spacing=10),
                                padding=ft.padding.only(bottom=5)
                            ),
                            ft.Container(
                                content=ft.Text(os.getcwd(), size=14, color="#CCCCCC", selectable=True),
                                padding=ft.padding.only(bottom=15, left=34)
                            ),
                        ],
                        expand=True,
                        spacing=5
                    ),
                    padding=20,
                    border=ft.border.all(1, "#444444"),
                    border_radius=10,
                    expand=True
                )
            ]),
            expand=True
        )
    
    def add_task(self, e):
        if hasattr(self, 'task_input') and self.task_input.value.strip():
            task = {
                "id": len(self.tasks) + 1,
                "description": self.task_input.value,
                "priority": self.priority_dropdown.value,
                "status": "Beklemede",
                "created": datetime.now().strftime("%H:%M:%S"),
                "completed": False
            }
            self.tasks.append(task)
            self.task_input.value = ""
            self.task_input.update()
            self.update_task_list()
    
    def update_task_list(self):
        if hasattr(self, 'task_list') and self.task_list:
            self.task_list.controls.clear()
            
            for task in self.tasks:
                priority_colors = {
                    "low": "#4CAF50",
                    "medium": "#FFC107",
                    "high": "#FF9800",
                    "critical": "#F44336"
                }
                
                task_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(task["description"], size=16, weight=ft.FontWeight.W_500),
                                ft.Container(
                                    content=ft.Text(task["priority"].upper()),
                                    bgcolor=priority_colors[task["priority"]],
                                    padding=5,
                                    border_radius=5
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text(f"Oluşturulma: {task['created']}"),
                                ft.Text(f"Durum: {task['status']}"),
                                ft.Row([
                                    ft.IconButton(
                                        "check_circle" if not task["completed"] else "check_circle_outline",
                                        on_click=lambda t=task: self.toggle_task(t),
                                        icon_color="#4CAF50" if task["completed"] else "#888888"
                                    ),
                                    ft.IconButton(
                                        "delete",
                                        on_click=lambda t=task: self.delete_task(t),
                                        icon_color="#F44336"
                                    )
                                ])
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ]),
                        padding=15
                    )
                )
                self.task_list.controls.append(task_card)
            
            self.task_list.update()
    
    def toggle_task(self, task):
        task["completed"] = not task["completed"]
        task["status"] = "Tamamlandı" if task["completed"] else "Beklemede"
        self.update_task_list()
    
    def delete_task(self, task):
        self.tasks.remove(task)
        self.update_task_list()
    
    def start_update_thread(self):
        def update_loop():
            while self.running:
                try:
                    # Süreç listesi güncelleme
                    if hasattr(self, 'process_list') and self.process_list:
                        self.update_process_list()
                    
                    # Sistem izleme güncelleme
                    self.update_system_monitor()
                    
                    # Ağ izleme güncelleme
                    self.update_network_monitor()
                    

                    time.sleep(3)  # 3 saniyede bir güncelle
                except Exception as e:
                    print(f"Güncelleme hatası: {e}")
                    time.sleep(10)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def update_system_monitor(self):
        try:
            if hasattr(self, 'cpu_usage') and hasattr(self, 'ram_usage') and hasattr(self, 'disk_usage'):
                # CPU kullanımı
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_usage.value = cpu_percent / 100
                self.cpu_text.value = f"CPU: {cpu_percent:.1f}%"
                
                # RAM kullanımı
                memory = psutil.virtual_memory()
                self.ram_usage.value = memory.percent / 100
                self.ram_text.value = f"RAM: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)"
                
                # Disk kullanımı
                disk = psutil.disk_usage('/')
                self.disk_usage.value = disk.used / disk.total
                self.disk_text.value = f"Disk: {(disk.used / disk.total) * 100:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)"
                
                # UI güncelleme
                self.cpu_usage.update()
                self.ram_usage.update()
                self.disk_usage.update()
                self.cpu_text.update()
                self.ram_text.update()
                self.disk_text.update()
        except Exception as e:
            print(f"Sistem izleme güncelleme hatası: {e}")
    
    def update_network_monitor(self):
        try:
            if hasattr(self, 'sent_text') and hasattr(self, 'recv_text') and hasattr(self, 'total_text'):
                net_io = psutil.net_io_counters()
                sent_mb = net_io.bytes_sent // (1024**2)
                recv_mb = net_io.bytes_recv // (1024**2)
                
                # Text güncelleme
                self.sent_text.value = f"{sent_mb:.1f} MB"
                self.recv_text.value = f"{recv_mb:.1f} MB"
                self.total_text.value = f"{(sent_mb + recv_mb):.1f} MB"
                self.packets_sent_text.value = f"Gönderilen: {net_io.packets_sent:,}"
                self.packets_recv_text.value = f"Alınan: {net_io.packets_recv:,}"
                
                # UI güncelleme
                self.sent_text.update()
                self.recv_text.update()
                self.total_text.update()
                self.packets_sent_text.update()
                self.packets_recv_text.update()
                

        except Exception as e:
            print(f"Ağ izleme güncelleme hatası: {e}")
    
    def update_process_list(self):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    # None değerleri 0 ile değiştir
                    if proc_info['cpu_percent'] is None:
                        proc_info['cpu_percent'] = 0.0
                    if proc_info['memory_percent'] is None:
                        proc_info['memory_percent'] = 0.0
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # CPU kullanımına göre sırala
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            if hasattr(self, 'process_list') and self.process_list:
                self.process_list.controls.clear()
                for proc in processes[:20]:  # İlk 20 süreç
                    process_card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"PID: {proc['pid']}", size=12, color="white"),
                                    ft.Text(f"CPU: {proc['cpu_percent']:.1f}%", size=12, color="white"),
                                    ft.Text(f"RAM: {proc['memory_percent']:.1f}%", size=12, color="white"),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(proc['name'], size=14, weight=ft.FontWeight.W_500, color="white", expand=True),
                                    ft.Text(proc['status'], size=12, color="#888888"),
                                    ft.IconButton(
                                        "stop",
                                        icon_size=16,
                                        on_click=lambda p=proc: self.kill_process(p),
                                        icon_color="#F44336"
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            ]),
                            padding=10
                        )
                    )
                    self.process_list.controls.append(process_card)
                self.process_list.update()
        except Exception as e:
            print(f"Süreç listesi güncelleme hatası: {e}")
    
    def kill_process(self, proc):
        try:
            psutil.Process(proc['pid']).terminate()
        except Exception as e:
            print(f"Süreç sonlandırma hatası: {e}")
    

    
    def get_system_info(self):
        try:
            info = f"""
İşletim Sistemi: {platform.system()} {platform.release()}
Mimari: {platform.machine()}
İşlemci: {platform.processor()}
Python Sürümü: {platform.python_version()}
Kullanıcı: {os.getlogin()}
Çalışma Dizini: {os.getcwd()}
            """
            return info
        except Exception as e:
            return f"Sistem bilgileri alınamadı: {e}"
    


if __name__ == "__main__":
    app = CloudSystem()
    ft.app(target=app.main) 