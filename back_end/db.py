import hashlib
import sqlite3
from datetime import datetime
from typing import Optional


class DatabaseManager:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self._crear_tablas()

    def _conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _crear_tablas(self):
        with self._conectar() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS conversaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    nombre_archivo TEXT NOT NULL,
                    contenido_archivo TEXT NOT NULL,
                    fecha_creacion TEXT NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversacion_id INTEGER NOT NULL,
                    emisor TEXT NOT NULL CHECK(emisor IN ('usuario', 'modelo')),
                    texto TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    FOREIGN KEY (conversacion_id) REFERENCES conversaciones (id) ON DELETE CASCADE
                );
            """)

    # --- Usuarios ---
    @staticmethod
    def _hashear_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def registrar_usuario(self, username: str, password: str) -> bool:
        try:
            with self._conectar() as conn:
                conn.execute(
                    "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                    (username.strip(), self._hashear_password(password))
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def autenticar_usuario(self, username: str, password: str) -> Optional[dict]:
        with self._conectar() as conn:
            row = conn.execute(
                "SELECT id, username FROM usuarios WHERE username = ? AND password_hash = ?",
                (username.strip(), self._hashear_password(password))
            ).fetchone()
            return dict(row) if row else None

    # --- Conversaciones y Mensajes (tus métodos ya corregidos) ---
    def save_conversation(self, usuario_id: int, nombre_archivo: str, contenido_archivo: str) -> int:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conn:
            cursor = conn.execute(
                """
                INSERT INTO conversaciones (usuario_id, nombre_archivo, contenido_archivo, fecha_creacion)
                VALUES (?, ?, ?, ?)
                """,
                (usuario_id, nombre_archivo, contenido_archivo, fecha_actual)
            )
            return cursor.lastrowid

    def save_message(self, conversacion_id: int, emisor: str, texto: str) -> str:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT INTO mensajes (conversacion_id, emisor, texto, fecha_hora)
                VALUES (?, ?, ?, ?)
                """,
                (conversacion_id, emisor, texto, fecha_hora)
            )
        return fecha_hora

    def delete_conversation(self, conversacion_id: int) -> None:
        with self._conectar() as conn:
            conn.execute("DELETE FROM mensajes WHERE conversacion_id = ?", (conversacion_id,))
            conn.execute("DELETE FROM conversaciones WHERE id = ?", (conversacion_id,))

    # --- Consultas para el historial y exportación ---
    def obtener_conversaciones_usuario(self, usuario_id: int) -> list[dict]:
        with self._conectar() as conn:
            rows = conn.execute(
                """
                SELECT id, nombre_archivo, fecha_creacion
                FROM conversaciones WHERE usuario_id = ? ORDER BY id DESC
                """,
                (usuario_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def obtener_detalle_conversacion(self, conversacion_id: int) -> Optional[dict]:
        with self._conectar() as conn:
            conv = conn.execute(
                "SELECT id, nombre_archivo, contenido_archivo, fecha_creacion FROM conversaciones WHERE id = ?",
                (conversacion_id,)
            ).fetchone()
            if not conv:
                return None

            msgs = conn.execute(
                "SELECT emisor, texto, fecha_hora FROM mensajes WHERE conversacion_id = ? ORDER BY id ASC",
                (conversacion_id,)
            ).fetchall()

            resultado = dict(conv)
            resultado["mensajes"] = [dict(m) for m in msgs]
            return resultado