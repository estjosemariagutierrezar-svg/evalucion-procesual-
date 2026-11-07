import os
import re
import hashlib
import json
import tkinter as tk
from tkinter import messagebox, ttk

DB_FILE = "legacy_secure_db.json"

# =====================================================================
# CLASE 1: Validador (Validación de datos de entrada y sanitización)
# =====================================================================
class Validador:
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida el formato de un correo electrónico."""
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(patron, email))

    @staticmethod
    def validar_codigo_legado(codigo: str) -> bool:
        """Valida el formato del código legado (Ej. LEG-1234)."""
        patron = r'^LEG-\d{4,6}$'
        return bool(re.match(patron, codigo))

    @staticmethod
    def sanitizar_texto(texto: str) -> str:
        """Limpia caracteres peligrosos para evitar inyecciones."""
        return re.sub(r'[<>&"\']', '', texto).strip()

# =====================================================================
# CLASE 2: Criptografia (Seguridad e Hashing de contraseñas)
# =====================================================================
class Criptografia:
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash SHA-256 para contraseñas."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

# =====================================================================
# CLASE 3: GestorDatos (Manejo de Archivos JSON y Excepciones)
# =====================================================================
class GestorDatos:
    @staticmethod
    def cargar_datos():
        """Carga datos desde JSON con manejo de excepciones."""
        if not os.path.exists(DB_FILE):
            datos_iniciales = {
                "admin": Criptografia.hash_password("Admin123!"),
                "usuarios": []
            }
            GestorDatos.guardar_datos(datos_iniciales)
            return datos_iniciales
        
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            messagebox.showerror("Error de Datos", f"No se pudo cargar la base de datos: {e}")
            return {"admin": "", "usuarios": []}

    @staticmethod
    def guardar_datos(datos):
        """Guarda datos en el archivo JSON con manejo de excepciones."""
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error de Guardado", f"Error al guardar los datos: {e}")

# =====================================================================
# CLASE 4: SistemaMigracion (Lógica de autenticación y migración de datos)
# =====================================================================
class SistemaMigracion:
    def __init__(self):
        self.datos = GestorDatos.cargar_datos()

    def autenticar(self, usuario, password):
        """Autentica a un usuario verificando su contraseña cifrada."""
        pass_hash = Criptografia.hash_password(password)
        if usuario == "admin" and self.datos.get("admin") == pass_hash:
            return True
        return False

    def registrar_usuario(self, codigo, email, nombre):
        """Migra y registra un nuevo registro asegurando sanitización y validación."""
        codigo_sanitizado = Validador.sanitizar_texto(codigo)
        email_sanitizado = Validador.sanitizar_texto(email)
        nombre_sanitizado = Validador.sanitizar_texto(nombre)

        if not Validador.validar_codigo_legado(codigo_sanitizado):
            raise ValueError("El código legado debe tener el formato LEG-XXXX (ej. LEG-1234).")

        if not Validador.validar_email(email_sanitizado):
            raise ValueError("El correo electrónico no tiene un formato válido.")

        nuevo_registro = {
            "codigo": codigo_sanitizado,
            "email": email_sanitizado,
            "nombre": nombre_sanitizado
        }

        self.datos["usuarios"].append(nuevo_registro)
        GestorDatos.guardar_datos(self.datos)
        return True

# =====================================================================
# CLASE 5: InterfazGrafica (GUI con Tkinter y 3 Vistas/Pantallas)
# =====================================================================
class InterfazGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Legado de Migración y Autenticación")
        self.root.geometry("500x480") 
        self.sistema = SistemaMigracion()

        self.container = ttk.Frame(self.root, padding=20)
        self.container.pack(fill="both", expand=True)

        self.mostrar_pantalla_login()

    def limpiar_pantalla(self):
        """Elimina todos los widgets de la pantalla actual."""
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- PANTALLA 1: Autenticación / Login ---
    def mostrar_pantalla_login(self):
        self.limpiar_pantalla()
        
        ttk.Label(self.container, text="Inicio de Sesión Seguro", font=("Helvetica", 14, "bold")).pack(pady=10)

        ttk.Label(self.container, text="Usuario:").pack(anchor="w", pady=2)
        entry_usr = ttk.Entry(self.container)
        entry_usr.pack(fill="x", pady=5)
        entry_usr.insert(0, "admin")

        ttk.Label(self.container, text="Contraseña:").pack(anchor="w", pady=2)
        entry_pass = ttk.Entry(self.container, show="*")
        entry_pass.pack(fill="x", pady=5)

        def intentar_login():
            try:
                usr = entry_usr.get()
                pwd = entry_pass.get()
                if self.sistema.autenticar(usr, pwd):
                    messagebox.showinfo("Éxito", "¡Autenticación correcta!")
                    self.mostrar_pantalla_registro()
                else:
                    messagebox.showerror("Error", "Credenciales incorrectas (Prueba: admin / Admin123!)")
            except Exception as e:
                messagebox.showerror("Error Inesperado", str(e))

        ttk.Button(self.container, text="Ingresar", command=intentar_login).pack(pady=15)

    # --- PANTALLA 2: Registro y Migración de Datos ---
    def mostrar_pantalla_registro(self):
        self.limpiar_pantalla()

        ttk.Label(self.container, text="Migración de Datos Legados", font=("Helvetica", 14, "bold")).pack(pady=10)

        ttk.Label(self.container, text="Código Legado (Ej: LEG-1001):").pack(anchor="w")
        entry_cod = ttk.Entry(self.container)
        entry_cod.pack(fill="x", pady=5)

        ttk.Label(self.container, text="Correo Electrónico:").pack(anchor="w")
        entry_email = ttk.Entry(self.container)
        entry_email.pack(fill="x", pady=5)

        ttk.Label(self.container, text="Nombre del Usuario:").pack(anchor="w")
        entry_nom = ttk.Entry(self.container)
        entry_nom.pack(fill="x", pady=5)

        def procesar_registro():
            try:
                cod = entry_cod.get()
                mail = entry_email.get()
                nom = entry_nom.get()
                
                self.sistema.registrar_usuario(cod, mail, nom)
                messagebox.showinfo("Éxito", "Registro validado y migrado correctamente.")
                entry_cod.delete(0, tk.END)
                entry_email.delete(0, tk.END)
                entry_nom.delete(0, tk.END)
            except ValueError as ve:
                messagebox.showwarning("Validación Fallida", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar: {e}")

        ttk.Button(self.container, text="Validar y Guardar", command=procesar_registro).pack(pady=10)
        ttk.Button(self.container, text="Ver Registros Migrados", command=self.mostrar_pantalla_registros).pack(pady=5)
        ttk.Button(self.container, text="Cerrar Sesión", command=self.mostrar_pantalla_login).pack(pady=5)

    # --- PANTALLA 3: Visualización de Registros Migrados ---
    def mostrar_pantalla_registros(self):
        self.limpiar_pantalla()

        ttk.Label(self.container, text="Base de Datos - Registros Legados", font=("Helvetica", 14, "bold")).pack(pady=10)

        tabla = ttk.Treeview(self.container, columns=("Codigo", "Email", "Nombre"), show="headings", height=8)
        tabla.heading("Codigo", text="Código")
        tabla.heading("Email", text="Correo")
        tabla.heading("Nombre", text="Nombre")
        
        tabla.column("Codigo", width=100)
        tabla.column("Email", width=180)
        tabla.column("Nombre", width=150)
        tabla.pack(fill="both", expand=True, pady=10)

        usuarios = self.sistema.datos.get("usuarios", [])
        for u in usuarios:
            tabla.insert("", tk.END, values=(u.get("codigo"), u.get("email"), u.get("nombre")))

        ttk.Button(self.container, text="Volver al Registro", command=self.mostrar_pantalla_registro).pack(pady=5)

# =====================================================================
# EJECUCIÓN DEL PROGRAMA
# =====================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGrafica(root)
    root.mainloop()
