import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from threading import Thread
from tkinter import ttk

# Variable global para almacenar los enlaces generados
enlaces = []

# Función para mostrar el spinner
def mostrar_spinner():
    spinner_frame = tk.Frame(root, bg="#f5f5f5", padx=20, pady=20)
    spinner_frame.place(relx=0.5, rely=0.5, anchor="center")
    spinner_label = tk.Label(spinner_frame, text="Generando enlaces, por favor espere...", font=("Helvetica", 14), bg="#f5f5f5")
    spinner_label.pack(pady=10)
    spinner = tk.Label(spinner_frame, text="⏳", font=("Helvetica", 40), bg="#f5f5f5")
    spinner.pack()
    root.update_idletasks()
    return spinner_frame

# Función para ocultar el spinner
def ocultar_spinner(spinner_frame):
    spinner_frame.destroy()
    root.update_idletasks()

# Función para seleccionar el archivo CSV
def seleccionar_archivo():
    archivo_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if archivo_path:
        procesar_csv(archivo_path)

# Función para procesar el archivo CSV y generar los enlaces de WhatsApp
def procesar_csv(archivo_path):
    global enlaces
    # Mostrar el spinner y deshabilitar los botones
    spinner_frame = mostrar_spinner()
    btn_seleccionar.config(state=tk.DISABLED)
    btn_limpiar.config(state=tk.DISABLED)
    btn_guardar.config(state=tk.DISABLED)
    
    # Función para ejecutar en un hilo
    def proceso():
        # Leer el archivo CSV
        df = pd.read_csv(archivo_path)
        
        # Verificar que las columnas requeridas existan
        if 'telefono' not in df.columns or 'nombre_completo' not in df.columns:
            messagebox.showerror("Error", "El archivo CSV debe contener las columnas 'telefono' y 'nombre_completo'")
            ocultar_spinner(spinner_frame)
            btn_seleccionar.config(state=tk.NORMAL)
            btn_limpiar.config(state=tk.NORMAL)
            btn_guardar.config(state=tk.NORMAL)
            return
        
        # Obtener el mensaje personalizado
        mensaje_base = mensaje_entry.get("1.0", tk.END).strip()
        
        if not mensaje_base:
            messagebox.showerror("Error", "Por favor ingrese un mensaje antes de cargar el CSV.")
            ocultar_spinner(spinner_frame)
            btn_seleccionar.config(state=tk.NORMAL)
            btn_limpiar.config(state=tk.NORMAL)
            btn_guardar.config(state=tk.NORMAL)
            return
        
        # Función para generar el enlace de WhatsApp
        def generar_enlace_whatsapp(numero, nombre, mensaje_base):
            # Reemplazar el marcador $nombre por el nombre real
            mensaje = mensaje_base.replace("$nombre", nombre)
            mensaje_encoded = mensaje.replace(" ", "%20")
            return f"https://api.whatsapp.com/send?phone={numero}&text={mensaje_encoded}"
        
        # Limpiar el área de texto
        for widget in frame_enlaces.winfo_children():
            widget.destroy()
        
        # Generar los enlaces para cada número en el archivo CSV
        global enlaces
        enlaces = [generar_enlace_whatsapp(row['telefono'], row['nombre_completo'], mensaje_base) for _, row in df.iterrows()]
        
        # Mostrar los enlaces en el área de texto con botones de copiar
        for i, enlace in enumerate(enlaces, start=1):
            frame_enlace = tk.Frame(frame_enlaces, bg="#ffffff", pady=5)
            frame_enlace.pack(fill=tk.X, expand=True)
            
            enlace_texto = tk.Text(frame_enlace, wrap=tk.WORD, height=2, font=("Helvetica", 10), bg="#f0f0f0", bd=0, relief="flat")
            enlace_texto.insert(tk.END, f"{i}. {enlace}")
            enlace_texto.config(state=tk.DISABLED)
            enlace_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            btn_copiar_enlace = tk.Button(frame_enlace, text="Copiar", command=lambda enlace=enlace: copiar_enlace(enlace), bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"), bd=0, relief="flat")
            btn_copiar_enlace.pack(side=tk.RIGHT, padx=5)
        
        ocultar_spinner(spinner_frame)
        btn_seleccionar.config(state=tk.NORMAL)
        btn_limpiar.config(state=tk.NORMAL)
        btn_guardar.config(state=tk.NORMAL)
    
    # Ejecutar el proceso en un hilo separado
    Thread(target=proceso).start()

# Función para copiar un enlace al portapapeles
def copiar_enlace(enlace):
    root.clipboard_clear()
    root.clipboard_append(enlace)
    messagebox.showinfo("Información", "Enlace copiado al portapapeles")

# Función para limpiar el mensaje personalizado y los enlaces generados
def limpiar():
    mensaje_entry.delete("1.0", tk.END)
    for widget in frame_enlaces.winfo_children():
        widget.destroy()

# Función para guardar los enlaces en un archivo de texto
def guardar_enlaces():
    if not enlaces:
        messagebox.showerror("Error", "No hay enlaces para guardar. Por favor, genere los enlaces primero.")
        return
    
    archivo_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if archivo_path:
        with open(archivo_path, "w") as archivo:
            for i, enlace in enumerate(enlaces, start=1):
                archivo.write(f"{i}. {enlace}\n")
        messagebox.showinfo("Información", "Enlaces guardados exitosamente.")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Generador de Enlaces de WhatsApp")
root.geometry("800x600")
root.configure(bg="#f5f5f5")

# Crear y colocar el área de entrada de texto para el mensaje personalizado
mensaje_label = tk.Label(root, text="Ingrese el mensaje personalizado:", font=("Helvetica", 14), bg="#f5f5f5")
mensaje_label.pack(pady=10)

# Indicador de uso del marcador $nombre
indicacion_label = tk.Label(root, text="Utilice $nombre para incluir el nombre completo en el mensaje.", font=("Helvetica", 10), bg="#f5f5f5", fg="#888888")
indicacion_label.pack(pady=5)

mensaje_entry = tk.Text(root, wrap=tk.WORD, height=3, font=("Helvetica", 12), bg="#ffffff", bd=0, relief="flat")
mensaje_entry.pack(fill=tk.BOTH, padx=20, pady=5)

# Crear y colocar el botón de selección de archivo
btn_seleccionar = tk.Button(root, text="Seleccionar archivo CSV", command=seleccionar_archivo, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), bd=0, relief="flat")
btn_seleccionar.pack(pady=15)

# Crear y colocar el botón para limpiar y volver a generar enlaces
btn_limpiar = tk.Button(root, text="Volver a generar enlaces", command=limpiar, bg="#f44336", fg="white", font=("Helvetica", 12, "bold"), bd=0, relief="flat")
btn_limpiar.pack(pady=10)

# Crear y colocar el botón para guardar los enlaces en un archivo de texto
btn_guardar = tk.Button(root, text="Guardar enlaces en archivo de texto", command=guardar_enlaces, bg="#008CBA", fg="white", font=("Helvetica", 12, "bold"), bd=0, relief="flat")
btn_guardar.pack(pady=10)

# Crear el frame con scrollbar para los enlaces
frame_scroll = tk.Frame(root, bg="#f5f5f5")
frame_scroll.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

canvas = tk.Canvas(frame_scroll, bg="#f5f5f5", bd=0, relief="flat")
scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

frame_enlaces = scrollable_frame

root.mainloop()
