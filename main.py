import os
import json
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox, Listbox, Entry, Label, Frame, Button, Scrollbar

# RUTAS IMPORTANTES
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Modificar estas líneas en tu código
#BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

PERFILES_DIR = os.path.join(BASE_DIR, 'PerfilesCreados')
PERFILES_JSON = os.path.join(BASE_DIR, 'perfiles.json')

# Ruta del navegador Brave.exe (puedes cambiarlo a Chrome si quieres)
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# Crear carpeta PerfilesCreados si no existe
os.makedirs(PERFILES_DIR, exist_ok=True)

# Cargar o crear archivo perfiles.json
if not os.path.exists(PERFILES_JSON):
    with open(PERFILES_JSON, 'w') as f:
        json.dump({}, f)

def cargar_perfiles():
    with open(PERFILES_JSON, 'r') as f:
        perfiles = json.load(f)
    
    # Convertir perfiles del formato antiguo al nuevo si es necesario
    perfiles_actualizados = {}
    for nombre, valor in perfiles.items():
        if isinstance(valor, str):  # Formato antiguo (solo ruta)
            perfiles_actualizados[nombre] = {
                "ruta": valor,
                "revisar": False
            }
        else:  # Formato nuevo (diccionario con ruta y revisar)
            perfiles_actualizados[nombre] = valor
    
    # Si hubo cambios, guardar la versión actualizada
    if perfiles_actualizados != perfiles:
        with open(PERFILES_JSON, 'w') as f:
            json.dump(perfiles_actualizados, f, indent=4)
    
    return perfiles_actualizados

def guardar_perfiles(perfiles):
    with open(PERFILES_JSON, 'w') as f:
        json.dump(perfiles, f, indent=4)

def crear_perfil():
    nombre = simpledialog.askstring("Crear Perfil", "Nombre del nuevo perfil:")
    if nombre:
        ruta_perfil = os.path.join(PERFILES_DIR, nombre)
        if os.path.exists(ruta_perfil):
            messagebox.showerror("Error", "Ese perfil ya existe.")
            return
        os.makedirs(ruta_perfil)
        perfiles = cargar_perfiles()
        perfiles[nombre] = {
            "ruta": ruta_perfil,
            "revisar": False  # Inicialmente no marcado para revisar
        }
        guardar_perfiles(perfiles)
        actualizar_lista()
        messagebox.showinfo("Éxito", f"Perfil '{nombre}' creado.")

def abrir_perfil():
    seleccion = lista_perfiles.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona un perfil primero.")
        return
    nombre = lista_perfiles.get(seleccion[0])
    # Eliminar el prefijo "🔍 " si existe
    nombre = nombre[2:] if nombre.startswith("🔍 ") else nombre
    
    perfiles = cargar_perfiles()
    ruta = perfiles[nombre]["ruta"]
    
    # Obtenemos la URL (si existe)
    url = entrada_url.get().strip()
    if url:
        subprocess.Popen([BRAVE_PATH, f"--user-data-dir={ruta}", url])
    else:
        subprocess.Popen([BRAVE_PATH, f"--user-data-dir={ruta}"])

def abrir_varios_perfiles():
    seleccion = lista_perfiles.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona al menos un perfil primero.")
        return
    
    # Obtenemos la URL (si existe)
    url = entrada_url.get().strip()
    
    perfiles = cargar_perfiles()
    for index in seleccion:
        nombre_display = lista_perfiles.get(index)
        # Eliminar el prefijo "🔍 " si existe
        nombre = nombre_display[2:] if nombre_display.startswith("🔍 ") else nombre_display
        
        ruta = perfiles[nombre]["ruta"]
        if url:
            subprocess.Popen([BRAVE_PATH, f"--user-data-dir={ruta}", url])
        else:
            subprocess.Popen([BRAVE_PATH, f"--user-data-dir={ruta}"])

def editar_perfil():
    seleccion = lista_perfiles.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona un perfil para editar.")
        return
    
    nombre_display = lista_perfiles.get(seleccion[0])
    # Eliminar el prefijo "🔍 " si existe
    nombre_actual = nombre_display[2:] if nombre_display.startswith("🔍 ") else nombre_display
    
    nuevo_nombre = simpledialog.askstring("Editar Perfil", "Nuevo nombre del perfil:", initialvalue=nombre_actual)
    
    if nuevo_nombre and nuevo_nombre != nombre_actual:
        perfiles = cargar_perfiles()
        if nuevo_nombre in perfiles:
            messagebox.showerror("Error", "Ya existe un perfil con ese nombre.")
            return
        
        # Renombrar el directorio del perfil
        ruta_antigua = perfiles[nombre_actual]["ruta"]
        ruta_nueva = os.path.join(PERFILES_DIR, nuevo_nombre)
        
        try:
            os.rename(ruta_antigua, ruta_nueva)
            # Actualizar en el diccionario
            revisar_estado = perfiles[nombre_actual]["revisar"]
            perfiles.pop(nombre_actual)
            perfiles[nuevo_nombre] = {
                "ruta": ruta_nueva,
                "revisar": revisar_estado
            }
            guardar_perfiles(perfiles)
            actualizar_lista()
            messagebox.showinfo("Éxito", f"Perfil renombrado a '{nuevo_nombre}'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo renombrar el perfil: {e}")

def eliminar_perfil():
    seleccion = lista_perfiles.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona un perfil para eliminar.")
        return
    
    nombre_display = lista_perfiles.get(seleccion[0])
    # Eliminar el prefijo "🔍 " si existe
    nombre = nombre_display[2:] if nombre_display.startswith("🔍 ") else nombre_display
    
    confirmacion = messagebox.askyesno("Confirmar Eliminación", 
                                      f"¿Estás seguro de que quieres eliminar el perfil '{nombre}'?\n"
                                      "Se eliminarán todos los datos asociados a este perfil.")
    
    if confirmacion:
        perfiles = cargar_perfiles()
        ruta = perfiles[nombre]["ruta"]
        
        try:
            # Eliminar el directorio del perfil de forma recursiva
            import shutil
            shutil.rmtree(ruta, ignore_errors=True)
            # Eliminar del diccionario
            perfiles.pop(nombre)
            guardar_perfiles(perfiles)
            actualizar_lista()
            messagebox.showinfo("Éxito", f"Perfil '{nombre}' eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el perfil: {e}")

def actualizar_lista():
    lista_perfiles.delete(0, tk.END)
    perfiles = cargar_perfiles()
    
    # Ordenar perfiles: primero los marcados para revisar
    perfiles_ordenados = sorted(perfiles.items(), key=lambda x: (not x[1]["revisar"], x[0]))
    
    for nombre, info in perfiles_ordenados:
        if info["revisar"]:
            lista_perfiles.insert(tk.END, f"🔍 {nombre}")
        else:
            lista_perfiles.insert(tk.END, nombre)

def toggle_revisar_perfil():
    seleccion = lista_perfiles.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona un perfil primero.")
        return
    
    nombre_display = lista_perfiles.get(seleccion[0])
    # Eliminar el prefijo "🔍 " si existe
    nombre = nombre_display[2:] if nombre_display.startswith("🔍 ") else nombre_display
    
    perfiles = cargar_perfiles()
    perfiles[nombre]["revisar"] = not perfiles[nombre]["revisar"]
    guardar_perfiles(perfiles)
    actualizar_lista()
    
    estado = "marcado para revisar" if perfiles[nombre]["revisar"] else "desmarcado"
    messagebox.showinfo("Estado Actualizado", f"Perfil '{nombre}' {estado}.")

def abrir_perfiles_revisar():
    perfiles = cargar_perfiles()
    perfiles_revisar = [nombre for nombre, info in perfiles.items() if info["revisar"]]
    
    if not perfiles_revisar:
        messagebox.showinfo("Información", "No hay perfiles marcados para revisar.")
        return
    
    url = entrada_url.get().strip()
    
    for nombre in perfiles_revisar:
        ruta = perfiles[nombre]["ruta"]
        if url:
            subprocess.Popen([BRAVE_PATH, f"--user-data-dir={ruta}", url])
        else:
            subprocess.Popen([BRAVE_PATH, f"--user-data-dir={ruta}"])

# GUI
ventana = tk.Tk()
ventana.title("Administrador de Perfiles de Navegador")
ventana.geometry("600x500")

# Frame para URL
frame_url = Frame(ventana)
frame_url.pack(pady=5, fill=tk.X, padx=10)

label_url = Label(frame_url, text="URL a abrir:")
label_url.pack(side=tk.LEFT, padx=(0, 5))

entrada_url = Entry(frame_url, width=50)
entrada_url.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Frame para botones principales
frame_botones = Frame(ventana)
frame_botones.pack(pady=5, fill=tk.X)

boton_crear = Button(frame_botones, text="Crear Perfil", command=crear_perfil)
boton_crear.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

boton_editar = Button(frame_botones, text="Editar Perfil", command=editar_perfil)
boton_editar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

boton_eliminar = Button(frame_botones, text="Eliminar Perfil", command=eliminar_perfil)
boton_eliminar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

# Frame para botones de apertura
frame_abrir = Frame(ventana)
frame_abrir.pack(pady=5, fill=tk.X)

boton_abrir = Button(frame_abrir, text="Abrir Perfil", command=abrir_perfil)
boton_abrir.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

boton_abrir_varios = Button(frame_abrir, text="Abrir Varios", command=abrir_varios_perfiles)
boton_abrir_varios.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

boton_abrir_revisar = Button(frame_abrir, text="Abrir Marcados para Revisar", command=abrir_perfiles_revisar)
boton_abrir_revisar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

# Frame para lista y botón de revisar
frame_lista = Frame(ventana)
frame_lista.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)

# Etiqueta instructiva
label_instrucciones = Label(frame_lista, text="Perfiles (🔍 = Marcado para revisar)")
label_instrucciones.pack(anchor=tk.W)

# Lista de perfiles
lista_perfiles = Listbox(frame_lista, selectmode=tk.MULTIPLE)
lista_perfiles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar para la lista
scrollbar = tk.Scrollbar(frame_lista, orient="vertical")
scrollbar.config(command=lista_perfiles.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
lista_perfiles.config(yscrollcommand=scrollbar.set)

# Botón para marcar/desmarcar para revisar
boton_revisar = Button(ventana, text="Marcar/Desmarcar para Revisar", command=toggle_revisar_perfil)
boton_revisar.pack(pady=5, padx=10, fill=tk.X)

# Actualizar la lista al inicio
actualizar_lista()

ventana.mainloop()