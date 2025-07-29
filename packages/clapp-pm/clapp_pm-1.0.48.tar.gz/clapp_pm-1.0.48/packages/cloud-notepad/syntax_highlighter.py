#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syntax Highlighter - Kod renklendirme modülü
Farklı programlama dilleri için syntax highlighting desteği
"""

import re
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighting sınıfı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = "text"
        self.setup_formats()
        self.setup_rules()
        
    def setup_formats(self):
        """Renk formatlarını ayarla"""
        self.formats = {
            'keyword': self.create_format(QColor(86, 156, 214), bold=True),
            'string': self.create_format(QColor(214, 157, 133)),
            'comment': self.create_format(QColor(87, 166, 74), italic=True),
            'number': self.create_format(QColor(181, 206, 168)),
            'function': self.create_format(QColor(220, 220, 170)),
            'class': self.create_format(QColor(78, 201, 176), bold=True),
            'operator': self.create_format(QColor(180, 180, 180)),
            'preprocessor': self.create_format(QColor(155, 155, 155), italic=True),
        }
        
    def create_format(self, color, bold=False, italic=False):
        """Format oluştur"""
        format = QTextCharFormat()
        format.setForeground(color)
        if bold:
            format.setFontWeight(QFont.Weight.Bold)
        if italic:
            format.setFontItalic(True)
        return format
        
    def setup_rules(self):
        """Syntax kurallarını ayarla"""
        self.rules = []
        
        # Python kuralları
        python_keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield'
        ]
        
        # JavaScript kuralları
        javascript_keywords = [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
            'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
            'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof',
            'var', 'void', 'while', 'with', 'yield'
        ]
        
        # HTML kuralları
        html_tags = [
            'html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style',
            'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img',
            'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input',
            'button', 'textarea', 'select', 'option'
        ]
        
        # CSS kuralları
        css_properties = [
            'color', 'background', 'margin', 'padding', 'border', 'font',
            'text', 'display', 'position', 'width', 'height', 'top', 'left',
            'right', 'bottom', 'float', 'clear', 'overflow', 'z-index'
        ]
        
        # Python için kurallar
        self.python_rules = [
            # String'ler
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.formats['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.formats['string']),
            (r'"""[^"]*"""', self.formats['string']),
            (r"'''[^']*'''", self.formats['string']),
            
            # Yorumlar
            (r'#.*$', self.formats['comment']),
            (r'"""[^"]*"""', self.formats['comment']),
            (r"'''[^']*'''", self.formats['comment']),
            
            # Sayılar
            (r'\b\d+\b', self.formats['number']),
            (r'\b\d+\.\d+\b', self.formats['number']),
            
            # Anahtar kelimeler
            (r'\b(' + '|'.join(python_keywords) + r')\b', self.formats['keyword']),
            
            # Fonksiyon tanımları
            (r'\bdef\s+(\w+)', self.formats['function']),
            (r'\bclass\s+(\w+)', self.formats['class']),
            
            # Operatörler
            (r'[+\-*/=<>!&|^~%]', self.formats['operator']),
        ]
        
        # JavaScript için kurallar
        self.javascript_rules = [
            # String'ler
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.formats['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.formats['string']),
            (r'`[^`]*`', self.formats['string']),
            
            # Yorumlar
            (r'//.*$', self.formats['comment']),
            (r'/\*.*?\*/', self.formats['comment']),
            
            # Sayılar
            (r'\b\d+\b', self.formats['number']),
            (r'\b\d+\.\d+\b', self.formats['number']),
            
            # Anahtar kelimeler
            (r'\b(' + '|'.join(javascript_keywords) + r')\b', self.formats['keyword']),
            
            # Fonksiyon tanımları
            (r'\bfunction\s+(\w+)', self.formats['function']),
            (r'\bclass\s+(\w+)', self.formats['class']),
            
            # Operatörler
            (r'[+\-*/=<>!&|^~%]', self.formats['operator']),
        ]
        
        # HTML için kurallar
        self.html_rules = [
            # HTML tag'leri
            (r'<[^>]+>', self.formats['keyword']),
            
            # String'ler
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.formats['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.formats['string']),
            
            # Yorumlar
            (r'<!--.*?-->', self.formats['comment']),
        ]
        
        # CSS için kurallar
        self.css_rules = [
            # Property'ler
            (r'\b(' + '|'.join(css_properties) + r')\b', self.formats['keyword']),
            
            # String'ler
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.formats['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.formats['string']),
            
            # Yorumlar
            (r'/\*.*?\*/', self.formats['comment']),
            
            # Sayılar
            (r'\b\d+\b', self.formats['number']),
            (r'\b\d+\.\d+\b', self.formats['number']),
            
            # Operatörler
            (r'[{}:;,]', self.formats['operator']),
        ]
        
    def set_language(self, language):
        """Dil ayarla"""
        self.language = language.lower()
        self.rehighlight()
        
    def highlightBlock(self, text):
        """Metin bloğunu renklendir"""
        if self.language == 'python':
            rules = self.python_rules
        elif self.language == 'javascript':
            rules = self.javascript_rules
        elif self.language == 'html':
            rules = self.html_rules
        elif self.language == 'css':
            rules = self.css_rules
        else:
            return
            
        for pattern, format in rules:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                start = match.start()
                end = match.end()
                self.setFormat(start, end - start, format)
                
    def detect_language(self, file_path):
        """Dosya uzantısından dili tespit et"""
        if not file_path:
            return 'text'
            
        ext = file_path.lower().split('.')[-1]
        
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'html': 'html',
            'htm': 'html',
            'css': 'css',
            'txt': 'text',
            'md': 'markdown',
            'json': 'json',
            'xml': 'xml',
            'sql': 'sql',
            'php': 'php',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'cs': 'csharp',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'swift': 'swift',
            'kt': 'kotlin',
        }
        
        return language_map.get(ext, 'text') 