import json
import sys
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication


class SistemaUDG:

  def __init__(self):
    # 1. Cargamos los usuarios guardados desde un archivo JSON
    self.archivo_usuarios = "usuarios.json"
    self.usuarios_bd = self.cargar_usuarios()

    # 2. Memoria temporal para las conversaciones del chat
    self.contador_chats = 1
    self.conversaciones = {
        "Consulta 1": [
            "<b>Bot UDG:</b> ¡Hola! Soy tu asistente del reglamento interno de la UDG. ¿En qué te ayudo?\n"
        ]
    }
    self.chat_actual = "Consulta 1"

    # 3. Cargamos tus dos archivos .ui diseñados en Qt Designer
    self.ventana_login = self.cargar_interfaz("Login.ui")
    self.ventana_chat = self.cargar_interfaz("Chat.ui")

    # 4. Conectamos los botones y cajas de texto con nuestras funciones
    self.conectar_eventos_login()
    self.conectar_eventos_chat()

    # 5. Preparamos el chat y mostramos primero la ventana de Login
    self.inicializar_datos_chat()
    self.ventana_login.show()

  def cargar_interfaz(self, ruta_ui):
    """Abre un archivo .ui y lo convierte en una ventana funcional."""
    archivo = QFile(ruta_ui)
    if not archivo.open(QFile.ReadOnly):
      print(f"Error: No se pudo abrir el archivo {ruta_ui}")
      sys.exit(-1)

    loader = QUiLoader()
    ventana = loader.load(archivo)
    archivo.close()
    return ventana

  # =========================================================================
  # MANEJO DE ARCHIVOS (PERSISTENCIA DE USUARIOS)
  # =========================================================================
  def cargar_usuarios(self):
    """Lee el archivo usuarios.json; si no existe, crea uno con un usuario base."""
    try:
      with open(self.archivo_usuarios, "r", encoding="utf-8") as archivo:
        return json.load(archivo)
    except FileNotFoundError:
      datos_iniciales = {"estudiante": "1234"}
      self.guardar_usuarios(datos_iniciales)
      return datos_iniciales

  def guardar_usuarios(self, datos):
    """Escribe el diccionario de usuarios en el archivo usuarios.json."""
    with open(self.archivo_usuarios, "w", encoding="utf-8") as archivo:
      json.dump(datos, archivo, indent=4)

  # =========================================================================
  # SECCIÓN 1: LÓGICA DE LOGIN Y REGISTRO
  # =========================================================================
  def conectar_eventos_login(self):
    self.ventana_login.btn_login.clicked.connect(self.iniciar_sesion)
    self.ventana_login.btn_registrar.clicked.connect(self.registrar_usuario)
    self.ventana_login.input_contrasena.returnPressed.connect(
        self.iniciar_sesion
    )

  def registrar_usuario(self):
    usuario = self.ventana_login.input_usuario.text().strip()
    contrasena = self.ventana_login.input_contrasena.text().strip()

    if not usuario or not contrasena:
      self.ventana_login.label_mensaje.setStyleSheet("color: red;")
      self.ventana_login.label_mensaje.setText("Completa usuario y contraseña.")
      return

    if usuario in self.usuarios_bd:
      self.ventana_login.label_mensaje.setStyleSheet("color: red;")
      self.ventana_login.label_mensaje.setText("Ese usuario ya está registrado.")
    else:
      self.usuarios_bd[usuario] = contrasena
      self.guardar_usuarios(self.usuarios_bd)  # Guardado permanente en disco
      self.ventana_login.label_mensaje.setStyleSheet("color: green;")
      self.ventana_login.label_mensaje.setText(
          "¡Cuenta registrada! Ya puedes iniciar sesión."
      )
      self.ventana_login.input_usuario.clear()
      self.ventana_login.input_contrasena.clear()

  def iniciar_sesion(self):
    usuario = self.ventana_login.input_usuario.text().strip()
    contrasena = self.ventana_login.input_contrasena.text().strip()

    if not usuario or not contrasena:
      self.ventana_login.label_mensaje.setStyleSheet("color: red;")
      self.ventana_login.label_mensaje.setText(
          "Ingresa tu usuario y contraseña."
      )
      return

    if (
        usuario in self.usuarios_bd
        and self.usuarios_bd[usuario] == contrasena
    ):
      self.ventana_login.label_mensaje.clear()
      self.ventana_login.input_usuario.clear()
      self.ventana_login.input_contrasena.clear()

      # Ocultamos el login y abrimos la ventana del chat
      self.ventana_login.hide()
      self.ventana_chat.show()
    else:
      self.ventana_login.label_mensaje.setStyleSheet("color: red;")
      self.ventana_login.label_mensaje.setText(
          "Usuario o contraseña incorrectos."
      )

  def cerrar_sesion(self):
    """Regresa de la ventana del chat a la ventana de login."""
    self.ventana_chat.hide()
    self.ventana_login.show()

  # =========================================================================
  # SECCIÓN 2: LÓGICA DEL CHAT E HISTORIAL UDG
  # =========================================================================
  def conectar_eventos_chat(self):
    self.ventana_chat.btn_nuevo_chat.clicked.connect(self.crear_nuevo_chat)
    self.ventana_chat.btn_borrar_chat.clicked.connect(self.eliminar_chat_actual)
    self.ventana_chat.btn_logout.clicked.connect(self.cerrar_sesion)
    self.ventana_chat.lista_historial.itemClicked.connect(self.cambiar_chat)

    self.ventana_chat.send_button.clicked.connect(self.enviar_mensaje)
    self.ventana_chat.message_input.returnPressed.connect(self.enviar_mensaje)

  def inicializar_datos_chat(self):
    self.ventana_chat.lista_historial.addItems(self.conversaciones.keys())
    self.ventana_chat.lista_historial.setCurrentRow(0)
    self.cargar_mensajes_en_pantalla()

  def cargar_mensajes_en_pantalla(self):
    self.ventana_chat.chat_history.clear()
    for mensaje in self.conversaciones[self.chat_actual]:
      self.ventana_chat.chat_history.append(mensaje)

  def cambiar_chat(self, item):
    self.chat_actual = item.text()
    self.cargar_mensajes_en_pantalla()

  def crear_nuevo_chat(self):
    self.contador_chats += 1
    nombre = f"Consulta {self.contador_chats}"
    self.conversaciones[nombre] = [
        "<b>Bot UDG:</b> Nueva consulta iniciada sobre el reglamento.\n"
    ]

    self.ventana_chat.lista_historial.addItem(nombre)
    self.ventana_chat.lista_historial.setCurrentRow(
        self.ventana_chat.lista_historial.count() - 1
    )
    self.chat_actual = nombre
    self.cargar_mensajes_en_pantalla()

  def eliminar_chat_actual(self):
    fila = self.ventana_chat.lista_historial.currentRow()
    if fila < 0:
      return

    del self.conversaciones[self.chat_actual]
    self.ventana_chat.lista_historial.takeItem(fila)

    if self.ventana_chat.lista_historial.count() == 0:
      self.crear_nuevo_chat()
    else:
      nuevo_item = self.ventana_chat.lista_historial.currentItem()
      self.chat_actual = nuevo_item.text()
      self.cargar_mensajes_en_pantalla()

  def enviar_mensaje(self):
    texto = self.ventana_chat.message_input.text().strip()
    if not texto:
      return

    msg_usuario = f"<b>Estudiante:</b> {texto}"
    self.conversaciones[self.chat_actual].append(msg_usuario)
    self.ventana_chat.chat_history.append(msg_usuario)
    self.ventana_chat.message_input.clear()

    msg_bot = (
        f"<b>Bot UDG:</b> Analizando el reglamento respecto a: '{texto}'...\n"
    )
    self.conversaciones[self.chat_actual].append(msg_bot)
    self.ventana_chat.chat_history.append(msg_bot)


if __name__ == "__main__":
  app = QApplication(sys.argv)
  sistema = SistemaUDG()
  sys.exit(app.exec())
