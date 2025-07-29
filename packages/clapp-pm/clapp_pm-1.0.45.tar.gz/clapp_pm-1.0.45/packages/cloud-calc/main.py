import flet as ft
import math
from datetime import datetime

class CloudCalculator:
    def __init__(self):
        self.current_expression = ""
        self.history = []
        self.is_dark_theme = False
        
    def main(self, page: ft.Page):
        page.title = "Cloud Calculator"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 200
        page.window_height = 700
        page.window_resizable = True
        page.padding = 0
        page.spacing = 0
        page.bgcolor = "#667eea"
        
        # Ana container - Tam genişlik, tam yükseklik
        self.main_container = ft.Container(
            expand=True,
            border_radius=0,
            padding=15,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#667eea", "#764ba2"]
            )
        )
        
        # Ekran alanı
        self.display = ft.TextField(
            value="0",
            text_align=ft.TextAlign.RIGHT,
            border=ft.InputBorder.NONE,
            text_size=32,
            color="white",
            bgcolor="transparent",
            read_only=True,
            height=80
        )
        
        # Geçmiş alanı
        self.history_display = ft.Text(
            "",
            size=14,
            color="white",
            text_align=ft.TextAlign.RIGHT,
            opacity=0.7
        )
        
        # Tema değiştirme butonu
        self.theme_button = ft.IconButton(
            icon="dark_mode",
            icon_color="white",
            on_click=self.toggle_theme
        )
        
        # Geçmiş temizleme butonu
        self.clear_history_button = ft.IconButton(
            icon="clear_all",
            icon_color="white",
            on_click=self.clear_history
        )
        
        # Üst bar
        top_bar = ft.Row(
            controls=[
                self.theme_button,
                ft.Text("Cloud Calculator", size=18, color="white", weight=ft.FontWeight.BOLD),
                self.clear_history_button
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Buton stilleri
        button_style = {
            "width": 60,
            "height": 60
        }
        
        # Sayı butonları - Doğru standart düzen
        number_buttons = [
            ft.ElevatedButton("7", **button_style, on_click=lambda e: self.add_to_expression("7")),
            ft.ElevatedButton("8", **button_style, on_click=lambda e: self.add_to_expression("8")),
            ft.ElevatedButton("9", **button_style, on_click=lambda e: self.add_to_expression("9")),
            ft.ElevatedButton("÷", **button_style, on_click=lambda e: self.add_to_expression("/"), bgcolor="#ff9500"),
            
            ft.ElevatedButton("4", **button_style, on_click=lambda e: self.add_to_expression("4")),
            ft.ElevatedButton("5", **button_style, on_click=lambda e: self.add_to_expression("5")),
            ft.ElevatedButton("6", **button_style, on_click=lambda e: self.add_to_expression("6")),
            ft.ElevatedButton("×", **button_style, on_click=lambda e: self.add_to_expression("*"), bgcolor="#ff9500"),
            
            ft.ElevatedButton("1", **button_style, on_click=lambda e: self.add_to_expression("1")),
            ft.ElevatedButton("2", **button_style, on_click=lambda e: self.add_to_expression("2")),
            ft.ElevatedButton("3", **button_style, on_click=lambda e: self.add_to_expression("3")),
            ft.ElevatedButton("-", **button_style, on_click=lambda e: self.add_to_expression("-"), bgcolor="#ff9500"),
            
            ft.ElevatedButton("0", **button_style, on_click=lambda e: self.add_to_expression("0")),
            ft.ElevatedButton(".", **button_style, on_click=lambda e: self.add_to_expression(".")),
            ft.ElevatedButton("+", **button_style, on_click=lambda e: self.add_to_expression("+"), bgcolor="#ff9500"),
            ft.ElevatedButton("=", **button_style, on_click=self.calculate, bgcolor="#ff9500"),
        ]
        
        # Bilimsel hesap makinesi butonları artık manuel satırlarda tanımlanıyor
        
        # Manuel satır düzeni - Doğru sıralama
        row1 = ft.Row(
            controls=[
                ft.ElevatedButton("7", **button_style, on_click=lambda e: self.add_to_expression("7")),
                ft.ElevatedButton("8", **button_style, on_click=lambda e: self.add_to_expression("8")),
                ft.ElevatedButton("9", **button_style, on_click=lambda e: self.add_to_expression("9")),
                ft.ElevatedButton("÷", **button_style, on_click=lambda e: self.add_to_expression("/"), bgcolor="#ff9500"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        row2 = ft.Row(
            controls=[
                ft.ElevatedButton("4", **button_style, on_click=lambda e: self.add_to_expression("4")),
                ft.ElevatedButton("5", **button_style, on_click=lambda e: self.add_to_expression("5")),
                ft.ElevatedButton("6", **button_style, on_click=lambda e: self.add_to_expression("6")),
                ft.ElevatedButton("×", **button_style, on_click=lambda e: self.add_to_expression("*"), bgcolor="#ff9500"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        row3 = ft.Row(
            controls=[
                ft.ElevatedButton("1", **button_style, on_click=lambda e: self.add_to_expression("1")),
                ft.ElevatedButton("2", **button_style, on_click=lambda e: self.add_to_expression("2")),
                ft.ElevatedButton("3", **button_style, on_click=lambda e: self.add_to_expression("3")),
                ft.ElevatedButton("-", **button_style, on_click=lambda e: self.add_to_expression("-"), bgcolor="#ff9500"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        row4 = ft.Row(
            controls=[
                ft.ElevatedButton("0", **button_style, on_click=lambda e: self.add_to_expression("0")),
                ft.ElevatedButton(".", **button_style, on_click=lambda e: self.add_to_expression(".")),
                ft.ElevatedButton("+", **button_style, on_click=lambda e: self.add_to_expression("+"), bgcolor="#ff9500"),
                ft.ElevatedButton("=", **button_style, on_click=self.calculate, bgcolor="#ff9500"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        # Bilimsel butonlar - Manuel satır düzeni
        scientific_row1 = ft.Row(
            controls=[
                ft.ElevatedButton("C", width=60, height=40, on_click=self.clear, bgcolor="#ff3b30"),
                ft.ElevatedButton("⌫", width=60, height=40, on_click=self.backspace, bgcolor="#ff9500"),
                ft.ElevatedButton("√", width=60, height=40, on_click=self.sqrt, bgcolor="#007aff"),
                ft.ElevatedButton("x²", width=60, height=40, on_click=self.square, bgcolor="#007aff"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        scientific_row2 = ft.Row(
            controls=[
                ft.ElevatedButton("sin", width=60, height=40, on_click=self.sin, bgcolor="#007aff"),
                ft.ElevatedButton("cos", width=60, height=40, on_click=self.cos, bgcolor="#007aff"),
                ft.ElevatedButton("tan", width=60, height=40, on_click=self.tan, bgcolor="#007aff"),
                ft.ElevatedButton("log", width=60, height=40, on_click=self.log, bgcolor="#007aff"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        # Ana layout - Manuel satır düzeni
        self.main_container.content = ft.Column(
            controls=[
                top_bar,
                self.history_display,
                self.display,
                ft.Divider(color="white", opacity=0.3),
                scientific_row1,
                scientific_row2,
                row1,
                row2,
                row3,
                row4
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        page.add(self.main_container)
        page.update()
    
    def add_to_expression(self, value):
        if self.display.value == "0" and value not in ["+", "-", "*", "/", "."]:
            self.current_expression = value
        else:
            self.current_expression += value
        
        self.display.value = self.current_expression
        self.display.update()
    
    def calculate(self, e=None):
        try:
            if self.current_expression:
                result = eval(self.current_expression)
                if isinstance(result, (int, float)):
                    if result == int(result):
                        result = int(result)
                    
                    # Geçmişe ekle
                    history_entry = f"{self.current_expression} = {result}"
                    self.history.append({
                        "expression": self.current_expression,
                        "result": result,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Geçmişi güncelle
                    self.update_history_display()
                    
                    self.display.value = str(result)
                    self.current_expression = str(result)
                else:
                    self.display.value = "Error"
            self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def clear(self, e=None):
        self.current_expression = ""
        self.display.value = "0"
        self.display.update()
    
    def backspace(self, e=None):
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            if not self.current_expression:
                self.display.value = "0"
            else:
                self.display.value = self.current_expression
            self.display.update()
    
    def sqrt(self, e=None):
        try:
            if self.current_expression:
                result = math.sqrt(float(self.current_expression))
                self.add_to_history(f"√({self.current_expression})", result)
                self.display.value = str(result)
                self.current_expression = str(result)
                self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def square(self, e=None):
        try:
            if self.current_expression:
                result = float(self.current_expression) ** 2
                self.add_to_history(f"({self.current_expression})²", result)
                self.display.value = str(result)
                self.current_expression = str(result)
                self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def sin(self, e=None):
        try:
            if self.current_expression:
                result = math.sin(math.radians(float(self.current_expression)))
                self.add_to_history(f"sin({self.current_expression}°)", result)
                self.display.value = str(result)
                self.current_expression = str(result)
                self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def cos(self, e=None):
        try:
            if self.current_expression:
                result = math.cos(math.radians(float(self.current_expression)))
                self.add_to_history(f"cos({self.current_expression}°)", result)
                self.display.value = str(result)
                self.current_expression = str(result)
                self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def tan(self, e=None):
        try:
            if self.current_expression:
                result = math.tan(math.radians(float(self.current_expression)))
                self.add_to_history(f"tan({self.current_expression}°)", result)
                self.display.value = str(result)
                self.current_expression = str(result)
                self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def log(self, e=None):
        try:
            if self.current_expression:
                result = math.log10(float(self.current_expression))
                self.add_to_history(f"log({self.current_expression})", result)
                self.display.value = str(result)
                self.current_expression = str(result)
                self.display.update()
        except:
            self.display.value = "Error"
            self.display.update()
    
    def add_to_history(self, expression, result):
        self.history.append({
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        self.update_history_display()
    
    def update_history_display(self):
        if self.history:
            # Son 3 işlemi göster
            recent_history = self.history[-3:]
            history_text = "\n".join([f"{entry['expression']} = {entry['result']}" for entry in recent_history])
            self.history_display.value = history_text
            self.history_display.update()
    
    def clear_history(self, e=None):
        self.history = []
        self.history_display.value = ""
        self.history_display.update()
    
    def toggle_theme(self, e):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.main_container.gradient = ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#2c3e50", "#34495e"]
            )
            self.theme_button.icon = "light_mode"
        else:
            self.main_container.gradient = ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#667eea", "#764ba2"]
            )
            self.theme_button.icon = "dark_mode"
        
        self.main_container.update()
        self.theme_button.update()

if __name__ == "__main__":
    calculator = CloudCalculator()
    ft.app(target=calculator.main) 