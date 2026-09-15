# Clase Biblioteca
import json
import os
from clases.libros import Libro
from clases.prestamos import Prestamo
from clases.usuarios import Usuario


class Biblioteca:
    def __init__(self):
        self.archivo_datos = "datos_biblioteca.json"
        self.libros = []
        self.usuarios = []
        self.prestamos = []  # Lista de préstamos en memoria

        # Si no existe el archivo JSON, cargamos los datos iniciales por defecto
        if not os.path.exists(self.archivo_datos):
            self.libros = [
                Libro("1984", "George Orwell"),
                Libro("Cien años de soledad", "Gabriel García Márquez"),
                Libro("Don Quijote de la Mancha", "Miguel de Cervantes"),
                Libro("La casa de los espíritus", "Isabel Allende"),
                Libro("Crimen y castigo", "Fyodor Dostoevsky"),
                Libro("El gran Gatsby", "F. Scott Fitzgerald"),
                Libro("Orgullo y prejuicio", "Jane Austen"),
                Libro("El principito", "Antoine de Saint-Exupéry"),
                Libro("Matar a un ruiseñor", "Harper Lee"),
                Libro("Ulises", "James Joyce"),
            ]
            self.usuarios = [
                Usuario("Juan Pérez", 12345678),
                Usuario("Ana Gómez", 23456789),
            ]
            self.guardar_datos()
        else:
            self.cargar_datos()

    # Métodos de Persistencia (Guardar y Cargar)
    def guardar_datos(self):
        datos = {
            "libros": [
                {
                    "titulo": l.titulo,
                    "autor": l.autor,
                    "disponible": getattr(l, "disponible", True),
                }
                for l in self.libros
            ],
            "usuarios": [{"nombre": u.nombre, "dni": u.dni} for u in self.usuarios],
        }
        with open(self.archivo_datos, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

    def cargar_datos(self):
        try:
            with open(self.archivo_datos, "r", encoding="utf-8") as f:
                datos = json.load(f)
                self.libros = []
                self.usuarios = []
                for l in datos.get("libros", []):
                    libro = Libro(l["titulo"], l["autor"])
                    libro.disponible = l.get("disponible", True)
                    self.libros.append(libro)
                for u in datos.get("usuarios", []):
                    self.usuarios.append(Usuario(u["nombre"], int(u["dni"])))
        except Exception as e:
            print(f"Error al cargar datos persistentes: {e}")

    # Mostrar los libros existentes en la biblioteca
    def mostrar_libros(self):
        print("\nLista de Libros Disponibles:")
        disponibles = [l for l in self.libros if getattr(l, "disponible", True)]
        if not disponibles:
            print("No hay libros disponibles en este momento.")
        for libro in disponibles:
            print(f"- {libro.titulo} de {libro.autor}")

    # Registrar un libro
    def registrar_libro(self, titulo, autor):
        libro = Libro(titulo, autor)
        self.libros.append(libro)
        self.guardar_datos()  # Guarda en JSON
        print(f"El libro '{titulo}' ha sido registrado exitosamente.")

    # Registrar Usuario
    def registrar_usuario(self, nombre, dni):
        dni = int(dni)
        if any(u.dni == dni for u in self.usuarios):
            print(f"El usuario con DNI {dni} ya está registrado.")
        else:
            usuario = Usuario(nombre, dni)
            self.usuarios.append(usuario)
            self.guardar_datos()  # Guarda en JSON
            print(f"El usuario {nombre} con DNI {dni} ha sido registrado.")

    # Eliminar Usuario
    def eliminar_usuario(self, dni):
        dni = int(dni)
        usuario_encontrado = next((u for u in self.usuarios if u.dni == dni), None)
        if usuario_encontrado:
            # Verifica si tiene préstamos activos antes de eliminar
            tiene_prestamos = any(
                p.fecha_devolucion is None for p in getattr(usuario_encontrado, "prestamos", [])
            )
            if tiene_prestamos:
                print(f"No se puede eliminar a {usuario_encontrado.nombre} porque tiene libros pendientes de devolución.")
                return False
            self.usuarios.remove(usuario_encontrado)
            self.guardar_datos()  # Guarda en JSON
            print(f"El usuario {usuario_encontrado.nombre} con DNI {dni} ha sido eliminado correctamente.")
            return True
        else:
            print(f"No se encontró ningún usuario con DNI {dni}.")
            return False

    # Prestar un libro a un usuario
    def prestar_libro(self, dni, titulo):
        dni = int(dni)
        usuario = next((u for u in self.usuarios if u.dni == dni), None)
        libro = next(
            (l for l in self.libros if l.titulo.lower().strip() == titulo.lower().strip() and l.disponible),
            None,
        )
        if usuario and libro:
            libro.disponible = False
            prestamo = Prestamo(usuario, libro)
            usuario.prestamos.append(prestamo)
            self.prestamos.append(prestamo)
            self.guardar_datos()  # Actualiza estado de disponibilidad
            print(
                f"El libro '{titulo}' ha sido prestado a {usuario.nombre}. Fecha de préstamo: {prestamo.fecha_prestamo.strftime('%d/%m/%Y %H:%M:%S')}."
            )
        else:
            print(
                "No se puede realizar el préstamo. Verifica que el libro esté disponible y el usuario esté registrado."
            )

    # Devolver un libro
    def devolver_libro(self, dni, titulo):
        dni = int(dni)
        usuario = next((u for u in self.usuarios if u.dni == dni), None)
        if not usuario:
            print("Usuario no encontrado.")
            return

        prestamo = next(
            (
                p
                for p in usuario.prestamos
                if p.libro.titulo.lower().strip() == titulo.lower().strip() and p.fecha_devolucion is None
            ),
            None,
        )
        if prestamo:
            prestamo.devolver_libro()
            prestamo.libro.disponible = True
            self.guardar_datos()  # Actualiza estado de disponibilidad
            print(
                f"El libro '{titulo}' ha sido devuelto por {usuario.nombre}. Fecha de devolución: {prestamo.fecha_devolucion.strftime('%d/%m/%Y %H:%M:%S')}."
            )
        else:
            print(
                "No se puede devolver el libro. Verifica que el libro esté prestado al usuario."
            )

    # Método para mostrar los usuarios que han solicitado libros
    def mostrar_usuarios_prestados(self):
        for usuario in self.usuarios:
            if getattr(usuario, "prestamos", None):
                libros_prestados = [
                    prestamo.libro.titulo for prestamo in usuario.prestamos if prestamo.fecha_devolucion is None
                ]
                if libros_prestados:
                    print(
                        f"{usuario.nombre} tiene prestados: {', '.join(libros_prestados)}."
                    )
                else:
                    print(f"{usuario.nombre} no tiene libros pendientes.")
            else:
                print(f"{usuario.nombre} no ha solicitado libros.")

    # Método para mostrar los usuarios registrados
    def mostrar_usuarios(self):
        print("\nLista de Usuarios Registrados:")
        for usuario in self.usuarios:
            print(f"- {usuario.nombre}, DNI: {usuario.dni}")