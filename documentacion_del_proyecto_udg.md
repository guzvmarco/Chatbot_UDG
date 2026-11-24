# 🎓 Asistente Universitario UDG — Interfaz Gráfica (Frontend PySide6)

Aplicación de escritorio desarrollada en **Python** con **PySide6** y **Qt Designer**, diseñada como la interfaz de usuario (Frontend) para un sistema de consulta sobre el reglamento interno de la Universidad de Guadalajara (UDG).

Esta versión funciona de manera **100% local e independiente del modelo LLM** (Backend), permitiendo el registro de estudiantes, inicio de sesión con persistencia local y gestión visual de múltiples conversaciones simuladas, dejándola lista para que el equipo de Backend conecte el motor de inteligencia artificial (RAG / LLM).

---

## 📋 Características Implementadas

* **Control de Acceso (Login y Registro):**
  * Registro de nuevos usuarios o códigos estudiantiles con validación de campos vacíos (`.strip()`) y detección de cuentas duplicadas.
  * Persistencia local de credenciales mediante almacenamiento estructurado en archivo JSON (`usuarios.json`), conservando los registros incluso tras cerrar la aplicación.
  * Transición fluida entre la ventana de acceso (`Login.ui`) y la ventana principal del asistente (`Chat.ui`), incluyendo botón de cierre de sesión (`Cerrar Sesión`) para regresar de forma segura al portal de inicio.
* **Interfaz de Chatbot Multi-sesión:**
  * Panel lateral de historial (`QListWidget`) para navegar entre distintas consultas activas con un clic.
  * Creación dinámica de nuevas consultas (`Nuevo chat`) y eliminación de conversaciones (`Eliminar chat`) con protección ante listas vacías.
  * Visor de conversación con soporte HTML (`QTextEdit` en modo `readOnly`) y envío de mensajes tanto mediante botón (`Enviar`) como presionando la tecla `Enter` (`returnPressed`).
  * Respuestas simuladas del asistente listas para ser reemplazadas por la integración con el modelo LLM/RAG.

---

## 📁 Estructura del Proyecto

Todos los archivos del código fuente y diseños visuales deben ubicarse en la raíz del proyecto (siempre **fuera** de la carpeta del entorno virtual `.venv`):

```text
Prueba de Interfaz/
├── .venv/               # Entorno virtual aislado de Python
├── Login.ui             # Diseño visual de la ventana de acceso y registro (Qt Designer)
├── Chat.ui              # Diseño visual de la ventana del chatbot e historial (Qt Designer)
├── main.py              # Controlador principal y lógica de interfaz en Python
├── usuarios.json        # Base de datos local generada automáticamente
└── documentacion_del_proyecto_udg.md            # Documentación completa del proyecto
```

---

## 🛠️ Bitácora de Desarrollo (Paso a Paso desde Cero)

Durante la construcción de este proyecto se recorrieron las siguientes etapas técnicas de aprendizaje y desarrollo:

1. **Fundamentos de PySide6 en Código Puro:**
   * Creación de ventanas principales (`QMainWindow`), contenedores base (`QWidget`) y gestores de distribución responsivos (`QVBoxLayout`, `QHBoxLayout`).
   * Comprensión del ciclo de vida de una aplicación gráfica mediante `QApplication(sys.argv)` y el bucle de eventos `sys.exit(app.exec())`.
2. **Prototipado de Interfaz de Chat con Historial en Memoria:**
   * Construcción inicial de una interfaz dividida mediante `QSplitter` con lista lateral (`QListWidget`), visor de conversación (`QTextEdit`) y barra de entrada (`QLineEdit` + `QPushButton`).
   * Implementación de diccionarios en Python (`self.conversaciones`) para almacenar múltiples hilos de conversación simultáneos.
3. **Diseño Visual Profesional con Qt Designer (`.ui`):**
   * Migración del diseño manual a dos archivos independientes (`Login.ui` y `Chat.ui`) arrastrando y configurando widgets visualmente.
   * Carga dinámica de los archivos XML `.ui` en tiempo de ejecución mediante `QFile` y `QUiLoader` sin necesidad de compilar archivos intermedios.
4. **Señales y Slots (Interactividad):**
   * Conexión de eventos de usuario (`clicked` en botones y `returnPressed` en cajas de texto) con los métodos de la clase controladora `SistemaUDG`.
5. **Persistencia de Datos con el Módulo `json`:**
   * Implementación de lectura y escritura segura en disco utilizando gestores de contexto (`with open(...)`), `json.load()` y `json.dump(..., indent=4)`, además de manejo de excepciones (`try ... except FileNotFoundError`) para inicializar automáticamente un usuario por defecto.
6. **Depuración y Resolución de Problemas Clave:**
   * **Aislamiento de entorno y plugin gráfico (`cocoa` en macOS):** Reinstalación limpia de `PySide6` dentro de `.venv` y reubicación del código fuente fuera de `.venv` para evitar conflictos de ejecución.
   * **Sincronización estricta de `objectName` y rutas:** Alineación exacta entre los identificadores asignados en el *Editor de propiedades* de Qt Designer y los atributos invocados en `main.py` (incluyendo mayúsculas exactas en `Login.ui` y `Chat.ui`, y la sincronización con `label_mesaje`).
   * **Orden de capas (Z-Order) y visibilidad:** Ajuste de dimensiones y envío al fondo (`Send to Back`) de la etiqueta de mensajes en `Login.ui` para evitar que interceptara clics sobre los botones, además de depuración por consola (`print`) y alertas nativas (`QMessageBox`).
7. **Arquitectura de Escalabilidad (Preparación para Nube y Seguridad):**
   * Se documentó el diseño futuro para migrar de `usuarios.json` a **Supabase (PostgreSQL)** mediante funciones RPC encriptadas (`pgcrypto`), políticas RLS y validación de entradas con expresiones regulares (`re`) para prevenir inyección SQL y *Prompt Injection*.

---

## 🧩 Mapa de Componentes (`objectName`)

Para mantener la compatibilidad entre los archivos `.ui` y `main.py`, los controles en Qt Designer deben conservar exactamente los siguientes identificadores (`objectName`):

### Ventana de Acceso (`Login.ui`)

| Widget | `objectName` | Función en `main.py` |
| :--- | :--- | :--- |
| `QLineEdit` | `input_usuario` | Entrada de código de estudiante o nombre de usuario |
| `QLineEdit` | `input_contrasena` | Entrada de contraseña (con `echoMode` en `Password`) |
| `QPushButton` | `btn_login` | Valida credenciales en `usuarios.json` y abre `Chat.ui` |
| `QPushButton` | `btn_registrar` | Registra un usuario nuevo y lo guarda en `usuarios.json` |
| `QLabel` | `label_mesaje` | Muestra avisos de error o confirmación de registro |

### Ventana del Chatbot (`Chat.ui`)

| Widget | `objectName` | Función en `main.py` |
| :--- | :--- | :--- |
| `QListWidget` | `lista_historial` | Lista lateral de conversaciones guardadas |
| `QPushButton` | `btn_nuevo_chat` | Crea una nueva consulta (`Consulta N`) en el historial |
| `QPushButton` | `btn_borrar_chat` | Elimina la consulta seleccionada actualmente |
| `QPushButton` | `btn_logout` | Oculta el chat, cierra sesión y regresa a `Login.ui` |
| `QTextEdit` | `chat_history` | Área de lectura (`readOnly = True`) con formato HTML |
| `QLineEdit` | `message_input` | Caja de entrada de texto para escribir dudas universitarias |
| `QPushButton` | `send_button` | Envía el mensaje del estudiante al visor del chat |

---

## 🚀 Requisitos, Instalación y Ejecución

1. **Requisitos previos:** Tener instalado **Python 3.10 o superior**.
2. **Abrir la carpeta del proyecto** en VS Code (asegurándose de estar en la raíz donde se encuentran `main.py`, `Login.ui` y `Chat.ui`).
3. **Crear y activar el entorno virtual:**
   * **En macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   * **En Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
4. **Instalar la dependencia gráfica:**
   ```bash
   pip install PySide6
   ```
5. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

> **Credenciales por defecto:** Si el archivo `usuarios.json` no existe al arrancar por primera vez, el sistema lo crea automáticamente con el usuario **`estudiante`** y contraseña **`1234`**.

---

## 🔌 Punto de Integración para el Equipo de Backend (LLM / RAG)

Actualmente la interfaz funciona de forma autónoma con respuestas simuladas para validar el flujo visual completo. Para conectar el modelo de lenguaje encargado de responder sobre el reglamento interno de la UDG, el equipo de Backend únicamente debe modificar el método `enviar_mensaje(self)` dentro de `main.py`:

```python
  def enviar_mensaje(self):
    texto = self.ventana_chat.message_input.text().strip()
    if not texto:
      return

    # 1. Muestra y guarda la pregunta del estudiante en la interfaz
    msg_usuario = f"<b>Estudiante:</b> {texto}"
    self.conversaciones[self.chat_actual].append(msg_usuario)
    self.ventana_chat.chat_history.append(msg_usuario)
    self.ventana_chat.message_input.clear()

    # 2. AQUÍ SE CONECTA EL MODELO LLM / RAG:
    # Reemplazar la siguiente línea por la llamada a la función o API del LLM
    respuesta_llm = f"Respuesta simulada sobre: '{texto}'"

    msg_bot = f"<b>Bot UDG:</b> {respuesta_llm}\n"
    self.conversaciones[self.chat_actual].append(msg_bot)
    self.ventana_chat.chat_history.append(msg_bot)
```

