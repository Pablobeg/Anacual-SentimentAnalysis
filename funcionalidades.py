import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Button, Tk, Label, messagebox,Menu, scrolledtext
import os
from docx import Document  # Para archivos Word
import PyPDF2  # Para archivos PDF
import shutil
import re
from datetime import datetime
from analisisSentimientos import completa
from difflib import SequenceMatcher
class Funcionalidades:
    resultado = None
    def __init__(self, interfaz):
        self.interfaz = interfaz
        self.ruta_documento = ""  # Atributo para almacenar la ruta del documento
        self.ruta_documento1 = ""
        self.actualizar_tabs_periodicamente()
        self.resultado = ""

    def resaltar_similitud(self):
        # Definir colores para cada carpeta
        colores = {"positivos": "#B2FFB2", "negativos": "#ff7c70"}
        ruta = self.ruta_documento
        if not ruta:
            return

        # Limpiar resaltados anteriores
        self.interfaz.text_contenido.tag_remove("resaltado_positivos", "1.0", tk.END)
        self.interfaz.text_contenido.tag_remove("resaltado_negativos", "1.0", tk.END)

        # Recorrer las carpetas
        carpetas = ["positivos", "negativos"]

        for carpeta in carpetas:
            # Obtener la lista de archivos en la carpeta
            archivos = os.listdir(os.path.join(ruta, carpeta))
            for archivo in archivos:
                # Leer el contenido del archivo
                ruta_archivo = os.path.join(ruta, carpeta, archivo)
                with open(ruta_archivo, "r") as file:
                    contenido_archivo = file.read()

                # Eliminar caracteres especiales (como saltos de línea) del contenido
                contenido_archivo = contenido_archivo.replace("\n", " ").replace("\r", "")

                # Expresión regular para encontrar el texto entre "Texto analizado:" y "Clasificación:"
                patron = re.compile(r"Texto analizado:(.*?)Clasificación:", re.DOTALL)
                coincidencias = patron.findall(contenido_archivo)

                # Para cada coincidencia, resaltarla en el widget text_contenido
                for coincidencia in coincidencias:
                    coincidencia = coincidencia.strip()  # Eliminar espacios en blanco al principio y al final

                    # Aplicar el color correspondiente según la carpeta
                    color = colores.get(carpeta, "white")

                    # Buscar la coincidencia en el widget text_contenido y resaltarla
                    indice = "1.0"
                    while True:
                        # Usa el índice absoluto para buscar coincidencias completas
                        indice = self.interfaz.text_contenido.search(coincidencia, indice, stopindex=tk.END,
                                                                     nocase=True)
                        if not indice:
                            break

                        # Calcular el índice final basándonos en la longitud de la coincidencia encontrada
                        fin_indice = f"{indice}+{len(coincidencia)}c"

                        # Resaltar el texto en el widget de texto
                        self.interfaz.text_contenido.tag_add(f"resaltado_{carpeta}", indice, fin_indice)
                        self.interfaz.text_contenido.tag_config(f"resaltado_{carpeta}", background=color)

                        # Mover el índice al final de la coincidencia para continuar buscando
                        indice = fin_indice
# Actualiza el menu de la izquierda cada cierto tiempo
    def actualizar_tabs_periodicamente(self):
        self.actualizar_tabs()
        self.resaltar_similitud()  # Llamar a la función para resaltar similitudes
     #   self.interfaz.root.after(15000, self.actualizar_tabs_periodicamente)  # Actualizar cada 5 segundos

    def actualizar_tabs(self):
        # Obtener la ruta del proyecto
        ruta_proyecto = self.ruta_documento
        if not ruta_proyecto:
            return

        # Buscar en las carpetas positivos, negativos
        carpetas = ["positivos", "negativos"]
        for carpeta in carpetas:
            # Limpiar la pestaña antes de actualizarla
            frame = getattr(self.interfaz, f"frame_{carpeta.lower()}")
            for widget in frame.winfo_children():
                widget.destroy()

            # Mostrar los nombres de los archivos en la pestaña con una barra de desplazamiento
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Crear un widget Listbox para mostrar los archivos
            listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
            listbox.pack(expand=True, fill=tk.BOTH)

            # Configurar la barra de desplazamiento para que funcione con el widget Listbox
            scrollbar.config(command=listbox.yview)

            # Obtener la lista de archivos en la carpeta correspondiente
            ruta_carpeta = os.path.join(ruta_proyecto, carpeta)
            archivos = [archivo for archivo in os.listdir(ruta_carpeta) if
                        os.path.isfile(os.path.join(ruta_carpeta, archivo))]

            # Agregar cada archivo al widget Listbox
            for archivo in archivos:
                listbox.insert(tk.END, archivo)

            # Agregar evento de clic derecho para mostrar menú contextual
            listbox.bind("<Button-3>",
                         lambda event, folder=carpeta, listbox=listbox: self.mostrar_menu_contextual(event, folder,
                                                                                                     listbox))
#Muestra el contenido del archivo en el frame derecho
    def mostrar_contenido_archivo(self, carpeta, nombre_archivo):
        # Obtener la ruta completa del archivo
        ruta_archivo = os.path.join(self.ruta_documento, carpeta, nombre_archivo)

        try:
            with open(ruta_archivo, "r", encoding="latin1") as file:  # Cambiar la codificación a latin1
                contenido = file.read()

            # Mostrar el contenido en el frame_superior_derecho
            self.interfaz.text_contenido_superior_derecho.delete("1.0", tk.END)  # Limpiar el contenido actual
            self.interfaz.text_contenido_superior_derecho.insert(tk.END, contenido)  # Insertar el nuevo contenido

            # Verificar si el contenido es "negativo" o "positivo" y cambiar el color de fondo en consecuencia
            if "negativo" in contenido.lower():
                self.interfaz.text_contenido_superior_derecho.config(bg="#ff7c70")
            elif "positivo" in contenido.lower():
                self.interfaz.text_contenido_superior_derecho.config(bg="#B2FFB2")
            else:
                # Restablecer el color de fondo a su valor predeterminado si no coincide con "negativo" ni "positivo"
                self.interfaz.text_contenido_superior_derecho.config(bg="white")
        except Exception as e:
            messagebox.showwarning("Error", f"No se pudo abrir el archivo: {str(e)}")

#Al hacer click izquierdo da opciones para los codigos que se han guardado
    def mostrar_menu_contextual(self, event, carpeta, listbox):
        # Crear menú contextual
        menu = tk.Menu(self.interfaz.root, tearoff=0)
        menu.add_command(label="Borrar", command=lambda: self.borrar_archivo(carpeta, listbox))
        menu.add_command(label="Renombrar", command=lambda: self.renombrar_archivo(carpeta, listbox))
        menu.add_command(label="Mostrar contenido",
                         command=lambda: self.mostrar_contenido_seleccionado(carpeta, listbox))
        menu.add_command(label="Editar", command=lambda: self.editar_contenido(carpeta, listbox))
        menu.add_command(label="Ir al texto", command=lambda: self.ir_al_texto(carpeta, listbox))

        # Mostrar menú en la posición del clic derecho
        menu.post(event.x_root, event.y_root)

    def mostrar_contenido_seleccionado(self, carpeta, listbox):
        # Obtener el índice del elemento seleccionado en el Listbox
        seleccionado = listbox.curselection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar archivo", "Por favor, selecciona un archivo para mostrar su contenido.")
            return

        # Obtener el nombre del archivo seleccionado
        nombre_archivo = listbox.get(seleccionado[0])

        # Mostrar el contenido del archivo seleccionado
        self.mostrar_contenido_archivo(carpeta, nombre_archivo)

    def borrar_archivo(self, carpeta, listbox):
        # Obtener el nombre del archivo seleccionado
        seleccionado = listbox.curselection()
        if not seleccionado:
            return

        nombre_archivo = listbox.get(seleccionado[0])

        # Confirmar la eliminación
        confirmacion = messagebox.askyesno("Confirmar borrado",
                                           f"¿Estás seguro de que deseas borrar '{nombre_archivo}'?")
        if not confirmacion:
            return

        # Eliminar el archivo
        ruta_archivo = os.path.join(self.ruta_documento, carpeta, nombre_archivo)
        os.remove(ruta_archivo)

        # Actualizar la lista de archivos
        self.actualizar_tabs_periodicamente()

    def renombrar_archivo(self, carpeta, listbox):
        # Obtener el nombre del archivo seleccionado
        seleccionado = listbox.curselection()
        if not seleccionado:
            return

        nombre_archivo = listbox.get(seleccionado[0])

        # Pedir al usuario el nuevo nombre del archivo
        nuevo_nombre = simpledialog.askstring("Renombrar archivo", f"Ingrese el nuevo nombre para '{nombre_archivo}':")
        if not nuevo_nombre:
            return

            # Agregar la extensión .txt si no la tiene
        if not nuevo_nombre.endswith(".txt"):
            nuevo_nombre += ".txt"

        # Renombrar el archivo
        ruta_archivo_antiguo = os.path.join(self.ruta_documento, carpeta, nombre_archivo)
        ruta_archivo_nuevo = os.path.join(self.ruta_documento, carpeta, nuevo_nombre)
        os.rename(ruta_archivo_antiguo, ruta_archivo_nuevo)

        # Actualizar la lista de archivos
        self.actualizar_tabs_periodicamente()



#Funcion para crear el proyecto
    def crear_proyecto(self):
        # Preguntar al usuario donde guardar el proyecto
        raiz = filedialog.askdirectory(title="Seleccionar ubicación del proyecto")
        if not raiz:
            return  # Si el usuario cancela, no hacemos nada

        # Preguntar al usuario el nombre para la carpeta principal
        nombre_carpeta_principal = simpledialog.askstring("Nombre de la carpeta",
                                                          "Ingrese el nombre para la carpeta principal:")
        if not nombre_carpeta_principal:
            return  # Si el usuario cancela, no hacemos nada

        # Crear la carpeta principal con el nombre proporcionado
        ruta_carpeta_principal = os.path.join(raiz, nombre_carpeta_principal)
        os.makedirs(ruta_carpeta_principal, exist_ok=True)

        # Establecer la ruta del documento después de que se haya creado la carpeta principal
        self.ruta_documento = self.abrir_documento()
        print("ruta del documento",self.ruta_documento)
        if not self.ruta_documento:
            return  # Si el usuario cancela, no hacemos nada

        # Crear una subcarpeta 'documento1' dentro de la carpeta principal
        ruta_documento1 = os.path.join(ruta_carpeta_principal, "documento1")
        print("ruta del documento despues de crear",ruta_documento1)
        os.makedirs(ruta_documento1, exist_ok=True)

        # Hacer una copia del documento en la carpeta 'documento1'
        shutil.copy(self.ruta_documento, ruta_documento1)

        # Crear un archivo llamado "marcados" en la carpeta 'documento1'
        ruta_marcados = os.path.join(ruta_documento1, "marcados.txt")
        with open(ruta_marcados, "w") as marcados_file:
            marcados_file.write("")

        # Crear una carpeta llamada 'positivos' dentro de 'documento1'
        ruta_positivos = os.path.join(ruta_documento1, "positivos")
        os.makedirs(ruta_positivos, exist_ok=True)

        # Crear una carpeta llamada 'negativos' dentro de 'documento1'
        ruta_negativos = os.path.join(ruta_documento1, "negativos")
        os.makedirs(ruta_negativos, exist_ok=True)

        self.ruta_documento=ruta_documento1
        self.actualizar_tabs_periodicamente()


#Abre el archivo que se quiere estudiar
    def abrir_documento(self):
        # Abrir cuadro de diálogo para seleccionar archivo
        ruta_documento = filedialog.askopenfilename(
            title="Seleccionar documento",
            filetypes=(
                ("Archivos Word", "*.docx"),
                ("Archivos PDF", "*.pdf"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            )
        )
        if not ruta_documento:
            return  # Si el usuario cancela, no hacemos nada


        self.abrir_dialogo(ruta_documento)

        return ruta_documento

    def abrir_dialogo(self, ruta_documento):
        # Determinar el tipo de archivo y abrirlo adecuadamente
        nombre, extension = os.path.splitext(ruta_documento)
        extension = extension.lower()
        if extension == ".docx":
            contenido = self.abrir_documento_word(ruta_documento)
        elif extension == ".pdf":
            contenido = self.abrir_documento_pdf(ruta_documento)
        elif extension == ".txt":
            contenido = self.abrir_documento_txt(ruta_documento)

        # Mostrar el contenido en el frame_central
        self.interfaz.text_contenido.delete("1.0", tk.END)  # Limpiar el contenido actual
        self.interfaz.text_contenido.insert(tk.END, contenido)  # Insertar el nuevo contenido

    def abrir_documento_word(self, ruta_documento):
        document = Document(ruta_documento)
        contenido = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return contenido.encode('utf-8').decode('utf-8')

    def abrir_documento_pdf(self, ruta_documento):
        with open(ruta_documento, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            contenido = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                contenido += page.extract_text()
        return contenido.encode('utf-8').decode('utf-8')

    def abrir_documento_txt(self, ruta_documento):
        with open(ruta_documento, "r", encoding="utf-8") as file:
            contenido = file.read()
        return contenido

# Funcion analisis entrevista el primer aviso(mensaje en pantalla) despues llama al metodo que hace la logica
    def analizar_entrevista(self):
        # Abrir ventana de diálogo con los pasos a seguir
        messagebox.showinfo("Análisis Entrevista",
                            "Estás usando la función Análisis Entrevista.\n"
                            "Ingresa el nombre del entrevistado (con  los dos puntos).\n"
                            "Cuando estés seguro, haz clic en el botón 'Aceptar'.")

        # Pedir al usuario que ingrese el nombre del entrevistado
        nombre_entrevistado = simpledialog.askstring("Nombre del Entrevistado",
                                                     "Ingresa el nombre del entrevistado:")

        if nombre_entrevistado:
            # Limpiar el nombre ingresado quitando posibles espacios en blanco alrededor
            nombre_entrevistado = nombre_entrevistado.strip()
            # Llamar a la función para análisis de entrevista
            self.analisis_entrevista(nombre_entrevistado)
#Funcion de logica de analisis de entrevista
    def analisis_entrevista(self, nombre_entrevistado):
        ruta_documento = self.ruta_documento
        print(ruta_documento)
        archivo_a_analizar = self.encontrar_archivo_a_analizar(ruta_documento)

        if archivo_a_analizar is not None:
            contenido = self.leer_contenido(archivo_a_analizar)

            # Crear ambas versiones del nombre, con y sin los dos puntos
            nombre_con_puntos = nombre_entrevistado.rstrip(':') + ':'
            nombre_sin_puntos = nombre_entrevistado.rstrip(':')

            # Buscar tanto el nombre con como sin los dos puntos en el archivo
            coincidencias_con_puntos = self.buscar_coincidencias(nombre_con_puntos, contenido)
            coincidencias_sin_puntos = self.buscar_coincidencias(nombre_sin_puntos, contenido)

            # Unir las coincidencias encontradas
            coincidencias = coincidencias_con_puntos + coincidencias_sin_puntos

            if coincidencias:
                self.procesar_coincidencias(coincidencias)
            else:
                messagebox.showinfo("Resultado", "No se encontraron coincidencias para el nombre ingresado.")
        else:
            messagebox.showwarning("Error", "No se encontró ningún archivo para analizar.")
#Toma el archivo para buscar el analisis
    def encontrar_archivo_a_analizar(self, ruta_documento1):
        archivo_a_analizar = None
        for nombre_archivo in os.listdir(ruta_documento1):
            if nombre_archivo == "marcados.txt":
                continue
            elif nombre_archivo.endswith((".txt", ".docx", ".pdf")):
                archivo_a_analizar = os.path.join(ruta_documento1, nombre_archivo)
                break
        return archivo_a_analizar
#Abre el archivo para el analisis
    def leer_contenido(self, archivo_a_analizar):
        contenido = ""
        nombre, extension = os.path.splitext(archivo_a_analizar)
        extension = extension.lower()
        if extension == ".txt":
            with open(archivo_a_analizar, "r") as file:
                contenido = file.read()
        elif extension == ".docx":
            contenido = self.abrir_documento_word(archivo_a_analizar)
        elif extension == ".pdf":
            contenido = self.abrir_documento_pdf(archivo_a_analizar)
        return contenido
#Busca las coincidencias del nombre del entrevistado en el archivo
    def buscar_coincidencias(self, nombre_entrevistado, contenido):
        patron = re.compile(rf"{nombre_entrevistado}:(.*?)\n", re.DOTALL)
        coincidencias = patron.findall(contenido)
        return coincidencias

    def procesar_coincidencias(self, coincidencias):
        detener_analisis = [False]  # Usamos una lista para que el valor pueda modificarse dentro de la función interna

        for idx, entrevista in enumerate(coincidencias, start=1):
            if detener_analisis[0]:  # Verifica si el usuario decidió detener el análisis
                break

            resultado = completa(entrevista)
            res = tk.StringVar()
            res.set(resultado)  # Establecemos el resultado inicial
            comentario = tk.StringVar()
            comentario.set("")

            # Función para detener el análisis completo
            def cancelar_analisis(ventana):
                detener_analisis[0] = True  # Cambia a True para detener el ciclo for
                ventana.destroy()

            def abrir_ventana_analisis(resultado_actual):
                ventana_analisis = tk.Tk()
                ventana_analisis.title("Análisis de texto")

                # Tamaño de la ventana de análisis
                ancho_ventana = 500
                alto_ventana = 400

                # Calcular la posición para centrar la ventana
                x_ventana = ventana_analisis.winfo_screenwidth() // 2 - ancho_ventana // 2
                y_ventana = ventana_analisis.winfo_screenheight() // 2 - alto_ventana // 2

                # Configurar el tamaño y la posición de la ventana
                ventana_analisis.geometry(f"{ancho_ventana}x{alto_ventana}+{x_ventana}+{y_ventana}")

                # Caja de texto con scrollbar para mostrar el texto analizado
                tk.Label(ventana_analisis, text="Texto analizado:").pack()
                texto_box = scrolledtext.ScrolledText(ventana_analisis, wrap=tk.WORD, width=40, height=10)
                texto_box.insert(tk.END, entrevista)
                texto_box.configure(state="disabled")  # Hacer que el texto sea solo de lectura
                texto_box.pack()

                tk.Label(ventana_analisis, text=f"Resultado del análisis: {resultado_actual}").pack()

                # Función para guardar el análisis y cerrar la ventana
                def continuar_analisis(resultado_final):
                    ventana_analisis.destroy()
                    if res.get() == "":
                        come = comentario.get()
                        self.guardar_archivo(resultado_final, entrevista, idx, come)
                    else:
                        nuevoR = res.get()
                        come = comentario.get()
                        self.guardar_archivo(nuevoR, entrevista, idx, come)

                # Marco para los botones en línea horizontal
                botones_frame = tk.Frame(ventana_analisis)
                botones_frame.pack(pady=10)

                if resultado_actual == "Neutro":
                    # Botones para el caso "Neutro" en una sola línea
                    tk.Button(botones_frame, text="Parar el análisis",
                              command=lambda: cancelar_analisis(ventana_analisis)).pack(side=tk.LEFT, padx=5)
                    tk.Button(botones_frame, text="Cambiar Clasificación",
                              command=lambda: cambiar_clasificacion(ventana_analisis)).pack(side=tk.LEFT, padx=5)
                    tk.Button(botones_frame, text="No Guardar", command=ventana_analisis.destroy).pack(side=tk.LEFT,
                                                                                                       padx=5)
                else:
                    # Botones para el caso "Positivo" o "Negativo" en una sola línea
                    tk.Button(botones_frame, text="Cambiar Clasificación",
                              command=lambda: cambiar_clasificacion(ventana_analisis)).pack(side=tk.LEFT, padx=5)
                    tk.Button(botones_frame, text="Añadir Comentario",
                              command=lambda: comentario.set(self.anadir_comentario())).pack(side=tk.LEFT, padx=5)
                    tk.Button(botones_frame, text="Guardar",
                              command=lambda r=resultado_actual: continuar_analisis(r)).pack(side=tk.LEFT, padx=5)
                    tk.Button(botones_frame, text="No Guardar", command=ventana_analisis.destroy).pack(side=tk.LEFT,
                                                                                                       padx=5)
                    tk.Button(botones_frame, text="Parar el análisis",
                              command=lambda: cancelar_analisis(ventana_analisis)).pack(side=tk.LEFT, padx=5)

                ventana_analisis.wait_window(ventana_analisis)

            def cambiar_clasificacion(ventana_anterior):
                # Cierra la ventana anterior antes de abrir la de clasificación
                ventana_anterior.destroy()

                # Crear una ventana de diálogo para seleccionar la clasificación
                ventana_clasificacion = tk.Toplevel()
                ventana_clasificacion.title("Cambiar Clasificación")

                # Tamaño de la ventana de clasificación
                ancho_ventana_clasificacion = 300
                alto_ventana_clasificacion = 200

                # Calcular la posición para centrar la ventana de clasificación
                x_ventana_clasificacion = ventana_clasificacion.winfo_screenwidth() // 2 - ancho_ventana_clasificacion // 2
                y_ventana_clasificacion = ventana_clasificacion.winfo_screenheight() // 2 - alto_ventana_clasificacion // 2

                # Configurar el tamaño y la posición de la ventana de clasificación
                ventana_clasificacion.geometry(
                    f"{ancho_ventana_clasificacion}x{alto_ventana_clasificacion}+{x_ventana_clasificacion}+{y_ventana_clasificacion}")

                # Variable para almacenar la clasificación seleccionada
                resultado_nuevo = tk.StringVar()

                # Funciones para asignar la clasificación y cerrar la ventana
                def set_positivo():
                    resultado_nuevo.set("Positivo")
                    ventana_clasificacion.destroy()

                def set_negativo():
                    resultado_nuevo.set("Negativo")
                    ventana_clasificacion.destroy()

                # Etiqueta y botones para seleccionar la clasificación
                tk.Label(ventana_clasificacion, text="Seleccione la nueva clasificación:").pack(pady=10)
                botones_frame_clasificacion = tk.Frame(ventana_clasificacion)
                botones_frame_clasificacion.pack(pady=10)
                tk.Button(botones_frame_clasificacion, text="Positivo", command=set_positivo).pack(side=tk.LEFT,
                                                                                                   padx=10)
                tk.Button(botones_frame_clasificacion, text="Negativo", command=set_negativo).pack(side=tk.RIGHT,
                                                                                                   padx=10)

                # Esperar a que la ventana se cierre antes de continuar
                ventana_clasificacion.wait_window()

                # Validar la clasificación seleccionada
                if resultado_nuevo.get() in ("Positivo", "Negativo"):
                    print(f"Clasificación seleccionada: {resultado_nuevo.get()}")
                    # Actualizar la variable `res` y abrir la ventana con la nueva clasificación
                    res.set(resultado_nuevo.get())
                    abrir_ventana_analisis(res.get())
                else:
                    messagebox.showwarning("Clasificación Inválida", "No se seleccionó una clasificación válida.")
                    abrir_ventana_analisis(
                        resultado)  # Reabrir la ventana de análisis original si no se seleccionó nada

            abrir_ventana_analisis(resultado)

            if detener_analisis[0]:  # Verifica nuevamente después de cerrar la ventana
                break

            self.actualizar_tabs_periodicamente()

# Función para añadir comentario
    def anadir_comentario(self):
        # Abrir cuadro de diálogo para que el usuario ingrese su comentario
        comentario = simpledialog.askstring("Añadir Comentario", "Ingrese su comentario:")

        # Verificar que se haya ingresado un comentario
        if comentario:
            self.comentario = comentario  # Guardar el comentario ingresado
        else:
            messagebox.showwarning("Comentario Vacío", "Por favor, ingrese un comentario.")
        return comentario
#Funcion que se usa para guardar cada archivo
    def guardar_archivo(self, resultado, entrevista, idx, comentario):
        try:
            # Guardar el archivo
            carpeta_destino = resultado.lower() + "s"
            ruta_carpeta_destino = os.path.join(self.ruta_documento, carpeta_destino)
            os.makedirs(ruta_carpeta_destino, exist_ok=True)

            # Generar un sufijo único para el nombre del archivo
            sufijo = datetime.now().strftime("_%Y%m%d%H%M%S")

            nombre_archivo_destino = f"parrafo{idx}_{resultado}{sufijo}.txt"
            ruta_archivo_destino = os.path.join(ruta_carpeta_destino, nombre_archivo_destino)
            #Escribe en un archivo txt el texto guardado con sus datos
            with open(ruta_archivo_destino, "w") as archivo_destino:
                archivo_destino.write(f"Texto analizado: {entrevista}\n")
                archivo_destino.write(f"Clasificación: {resultado}\n")
                archivo_destino.write(f"Comentario: {comentario}\n")

            return ruta_archivo_destino  # Devolver la ruta del archivo guardado
        except Exception as e:
            # Manejar cualquier excepción que ocurra durante el proceso de guardado
            raise Exception(f"No se pudo guardar el archivo: {str(e)}")
        self.actualizar_tabs_periodicamente()
#Funcion para editar cada archivo
    def editar_contenido(self, carpeta, listbox):
        # Obtener el índice del elemento seleccionado en el Listbox
        seleccionado = listbox.curselection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar archivo", "Por favor, selecciona un archivo para editarlo.")
            return

        # Obtener el nombre del archivo seleccionado
        nombre_archivo = listbox.get(seleccionado[0])

        # Obtener la ruta completa del archivo
        ruta_archivo = os.path.join(self.ruta_documento, carpeta, nombre_archivo)

        try:
            # Leer el contenido del archivo y mostrarlo en el frame_inferior_izquierdo
            with open(ruta_archivo, "r") as file:
                contenido = file.read()

            # Limpiar el contenido actual en el frame_inferior_izquierdo
            for widget in self.interfaz.frame_inferior_derecho.winfo_children():
                widget.destroy()

            # Mostrar el contenido en un Text widget en el frame_inferior_izquierdo
            text_widget = tk.Text(self.interfaz.frame_inferior_derecho, wrap="word", height=10, width=50)
            text_widget.insert(tk.END, contenido)
            text_widget.pack(expand=True, fill=tk.BOTH)

            # Agregar botón "Guardar" para guardar los cambios
            btn_guardar = tk.Button(self.interfaz.frame_inferior_derecho, text="Guardar",
                                    command=lambda: self.guardar_cambios(ruta_archivo, text_widget))
            btn_guardar.pack()

        except Exception as e:
            messagebox.showwarning("Error", f"No se pudo abrir el archivo: {str(e)}")
#Funcion para guardar cambios
    def guardar_cambios(self, ruta_archivo, text_widget):
        try:
            # Obtener el contenido del Text widget
            nuevo_contenido = text_widget.get("1.0", tk.END)

            # Escribir el nuevo contenido en el archivo
            with open(ruta_archivo, "w") as file:
                file.write(nuevo_contenido)

            messagebox.showinfo("Guardado", "Los cambios se guardaron correctamente.")

            # Llamar a la función para analizar la clasificación después del guardado
            self.analizar_clasificacion(ruta_archivo)

        except Exception as e:
            messagebox.showwarning("Error", f"No se pudo guardar los cambios: {str(e)}")

        self.actualizar_tabs_periodicamente()
#Funcion para checar que clasificacion tiene y si tiene una diferente lo mueve de carpeta
    def analizar_clasificacion(self, ruta_archivo):
        try:
            with open(ruta_archivo, "r") as file:
                contenido = file.read()

            # Buscar la línea que contiene la clasificación
            for linea in contenido.splitlines():
                if "Clasificación:" in linea:
                    clasificacion = linea.split(":")[1].strip().lower()
                    if clasificacion in ("positivo", "negativo", "neutro"):
                        # Obtener la carpeta correspondiente a la clasificación
                        carpeta_destino = os.path.join(self.ruta_documento, clasificacion + "s")
                        # Comprobar si el archivo ya está en la carpeta de destino
                        if os.path.dirname(ruta_archivo) != carpeta_destino:
                            # Mover el archivo a la carpeta de destino solo si no está ya en esa carpeta
                            shutil.move(ruta_archivo, carpeta_destino)
                            messagebox.showinfo("Clasificación", f"Archivo clasificado como {clasificacion}.")
                        else:
                            messagebox.showinfo("Guardado sin mover", "Los cambios se guardaron correctamente.")
                        return

            messagebox.showwarning("Clasificación no encontrada",
                                   "No se encontró una clasificación válida en el archivo.")
        except Exception as e:
            messagebox.showwarning("Error", f"No se pudo analizar el archivo: {str(e)}")
#Funcion que hace el analisis por puntos
    def analisis_por_puntos(self):
        ruta_documento = self.ruta_documento
        archivo_a_analizar = self.encontrar_archivo_a_analizar(ruta_documento)
        if archivo_a_analizar is not None:
            contenido = self.leer_contenido(archivo_a_analizar)
            textos = self.separar_por_puntos(contenido)
            self.procesar_coincidencias(textos)
        else:
            messagebox.showwarning("Error", "No se encontró ningún archivo para analizar.")
#Funcion que ayuda a separar por puntos
    def separar_por_puntos(self, contenido):
        # Utilizar expresión regular para dividir el contenido por puntos
        textos = re.split(r'\.\s+', contenido)
        return textos
#Funcion para abrir proyecto ya creado
    def abrir_proyecto(self):
        # Abrir cuadro de diálogo para seleccionar un proyecto
        ruta_proyecto = filedialog.askdirectory(title="Seleccionar proyecto")
        if not ruta_proyecto:
            return  # Si el usuario cancela, no hacemos nada

        # Verificar si el proyecto cumple con el formato requerido
        if not self.validar_formato_proyecto(ruta_proyecto):
            messagebox.showwarning("Formato incorrecto",
                                   "El proyecto no contiene el formato adecuado. "
                                   "Por favor, selecciona un proyecto con el formato correcto "
                                   "o crea un proyecto nuevo.")
            # Volver a abrir la ventana para seleccionar un proyecto
            self.abrir_proyecto()
            return

        # Si el proyecto cumple con el formato, guardar la ruta del proyecto
        self.ruta_documento = os.path.join(ruta_proyecto + "/documento1")

        doc=self.encontrar_archivo_a_analizar(self.ruta_documento)
        # Llamar a la función para abrir el diálogo con la ruta del proyecto seleccionado
        self.abrir_dialogo(doc)

        # Llamar a la función para actualizar las tabs periódicamente
        self.actualizar_tabs_periodicamente()
#Valida si el formato del proyecto es el correcto
    def validar_formato_proyecto(self, ruta_proyecto):
        # Verificar que exista la carpeta 'documento1' y las carpetas 'positivos', 'negativos', 'neutros' dentro de ella
        if not os.path.exists(os.path.join(ruta_proyecto, "documento1")):
            return False
        if not os.path.exists(os.path.join(ruta_proyecto, "documento1", "positivos")):
            return False
        if not os.path.exists(os.path.join(ruta_proyecto, "documento1", "negativos")):
            return False


        # Verificar que existan los archivos 'marcados.txt' y un archivo con extensión .pdf, .docx, o .txt dentro de 'documento1'
        archivos_validos = ["marcados.txt", ".pdf", ".docx", ".txt"]
        archivos_en_documento1 = os.listdir(os.path.join(ruta_proyecto, "documento1"))
        archivos_validos_presentes = [archivo for archivo in archivos_en_documento1 if
                                      any(archivo.endswith(ext) for ext in archivos_validos)]

        if len(archivos_validos_presentes) != 2:  # Deben haber exactamente dos archivos válidos presentes
            return False

        return True


    
#Funcion para que el usuario pueda elegir el menu contextual de analizar sentimiento el texto a analizar
    def mostrar_menu_contextual_s(self, event):

        # Crear menú contextual
        self.menu_contextual_s1 = tk.Menu(self.interfaz.root, tearoff=0)
        self.menu_contextual_s1.add_command(label="Analizar sentimiento",
                                            command=self.analizar_sentimiento_desde_seleccion)

        # Mostrar el menú contextual en la posición del clic derecho
        self.menu_contextual_s1.post(event.x_root, event.y_root)
#Funcio que usa para analizar el sentimiento de solo uno
    def analizar_sentimiento_desde_seleccion(self):
        try:
            # Obtener el texto seleccionado dentro del widget de texto
            seleccionado = self.interfaz.text_contenido.get(tk.SEL_FIRST, tk.SEL_LAST)

            if seleccionado:
                # Llamar a la función para analizar sentimiento
                self.procesar_coincidencias([seleccionado])
            else:
                tk.messagebox.showwarning("Selección vacía",
                                          "Por favor, selecciona un texto para analizar el sentimiento.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Ocurrió un error al analizar el sentimiento: {str(e)}")

    def buscar_similitud(self, texto_completo, texto_referencia, umbral=0.7):
        """Busca la mejor coincidencia parcial en el texto completo con al menos un umbral de similitud"""
        lineas = texto_completo.split("\n")
        mejor_coincidencia = None
        mejor_puntaje = 0
        for linea in lineas:
            puntaje = SequenceMatcher(None, texto_referencia, linea).ratio()
            if puntaje > mejor_puntaje and puntaje >= umbral:
                mejor_coincidencia = linea
                mejor_puntaje = puntaje
        return mejor_coincidencia

    def ir_al_texto(self, carpeta, listbox):
        # Obtener el nombre del archivo seleccionado en la lista
        archivo_seleccionado = listbox.get(listbox.curselection())
        ruta_archivo = os.path.join(self.ruta_documento, carpeta, archivo_seleccionado)

        # Leer el contenido del archivo seleccionado
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as file:
                contenido_archivo = file.read()
        except UnicodeDecodeError:
            with open(ruta_archivo, "r", encoding="latin-1") as file:
                contenido_archivo = file.read()

        # Extraer el texto entre "Texto analizado:" y "Clasificación:"
        patron = re.compile(r"Texto analizado:(.*?)Clasificación:", re.DOTALL)
        coincidencia = patron.search(contenido_archivo)
        if not coincidencia:
            tk.messagebox.showerror("Error", "No se encontró el texto de referencia en el archivo.")
            return

        texto_referencia = coincidencia.group(1).strip()

        # Obtener todo el texto mostrado en el panel
        texto_panel = self.interfaz.text_contenido.get("1.0", tk.END)

        # Buscar coincidencia exacta
        indice = self.interfaz.text_contenido.search(texto_referencia, "1.0", tk.END, nocase=True)
        if not indice:
            # Si no se encuentra exacto, buscar coincidencia difusa
            mejor_coincidencia = self.buscar_similitud(texto_panel, texto_referencia, umbral=0.7)
            if mejor_coincidencia:
                texto_referencia = mejor_coincidencia
                indice = self.interfaz.text_contenido.search(texto_referencia, "1.0", tk.END, nocase=True)
            else:
                tk.messagebox.showerror("Error", "El texto de referencia no se encuentra en el contenido mostrado.")
                return

        # Mover el scrollbar para mostrar el texto de referencia
        linea, _ = map(int, indice.split('.'))
        self.interfaz.text_contenido.see(f"{linea}.0")  # Ajusta el scroll para mostrar la línea del texto encontrado

        # Resaltar temporalmente el texto de referencia
        fin_indice = f"{indice}+{len(texto_referencia)}c"
        self.interfaz.text_contenido.tag_add("highlight_temp", indice, fin_indice)
        self.interfaz.text_contenido.tag_config("highlight_temp", background="yellow")

        # Restablecer el color original después de unos segundos (ejemplo: 2000 ms = 2 segundos)
        self.interfaz.text_contenido.after(2000,
                                           lambda: self.restablecer_color_clasificacion(indice, fin_indice, carpeta))

    def restablecer_color_clasificacion(self, inicio, fin, carpeta):
        # Define el color de clasificación original según la carpeta
        colores = {"positivos": "#B2FFB2", "negativos": "#ff7c70"}
        color_original = colores.get(carpeta, "white")

        # Eliminar el resaltado temporal y aplicar el color de clasificación original
        self.interfaz.text_contenido.tag_remove("highlight_temp", inicio, fin)
        self.interfaz.text_contenido.tag_add(f"resaltado_{carpeta}", inicio, fin)
        self.interfaz.text_contenido.tag_config(f"resaltado_{carpeta}", background=color_original)