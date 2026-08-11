import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl  # QUrl se importa de QtCore
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class NavegadorLigero(QWidget):

  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    self.setWindowTitle("Mi Navegador Ultra Ligero")
    self.setGeometry(100, 100, 1024, 768)

    # Layout principal vertical
    layout_principal = QVBoxLayout()
    layout_principal.setContentsMargins(5, 5, 5, 5)

    # Layout horizontal para la barra de herramientas superior
    layout_barra = QHBoxLayout()

    # Botones de navegación
    self.btn_atras = QPushButton("⬅")
    self.btn_atras.setFixedWidth(40)
    self.btn_atras.clicked.connect(lambda: self.browser.back())

    self.btn_adelante = QPushButton("➡")
    self.btn_adelante.setFixedWidth(40)
    self.btn_adelante.clicked.connect(lambda: self.browser.forward())

    self.btn_recargar = QPushButton("🔄")
    self.btn_recargar.setFixedWidth(40)
    self.btn_recargar.clicked.connect(lambda: self.browser.reload())

    # Barra de direcciones (URL)
    self.url_input = QLineEdit()
    self.url_input.returnPressed.connect(self.ir_a_url)

    # Botón Ir
    self.btn_ir = QPushButton("Ir")
    self.btn_ir.setFixedWidth(50)
    self.btn_ir.clicked.connect(self.ir_a_url)

    # Añadir elementos a la barra superior
    layout_barra.addWidget(self.btn_atras)
    layout_barra.addWidget(self.btn_adelante)
    layout_barra.addWidget(self.btn_recargar)
    layout_barra.addWidget(self.url_input)
    layout_barra.addWidget(self.btn_ir)

    # Componente web real (motor Chromium optimizado y ligero)
    self.browser = QWebEngineView()
    self.browser.setUrl(QUrl("https://duckduckgo.com"))

    # Actualizar la barra de direcciones cuando la página cambie de URL
    self.browser.urlChanged.connect(self.actualizar_barra_url)

    # Agregar la barra y el navegador al layout principal
    layout_principal.addLayout(layout_barra)
    layout_principal.addWidget(self.browser)

    self.setLayout(layout_principal)

  def ir_a_url(self):
    texto = self.url_input.text().strip()
    if not texto.startswith("http://") and not texto.startswith("https://"):
      # Si no es una URL directa, permite buscar o asume https
      if "." in texto and " " not in texto:
        texto = "https://" + texto
      else:
        # Búsqueda rápida en DuckDuckGo si escribes texto plano
        texto = (
            "https://duckduckgo.com/?q="
            + texto.replace(" ", "+")
        )
    self.browser.setUrl(QUrl(texto))

  def actualizar_barra_url(self, q):
    self.url_input.setText(q.toString())


if __name__ == "__main__":
  app = QApplication(sys.argv)
  ventana = NavegadorLigero()
  ventana.show()
  sys.exit(app.exec())
  
