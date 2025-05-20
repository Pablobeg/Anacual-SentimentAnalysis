import tkinter as tk
from tkinter import Menu, Scrollbar, Toplevel
from tkinter import ttk
from funcionalidades import Funcionalidades


class Interfaz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Anacual Analisis de sentimientos")
        self.root.geometry("800x600")  # Tamaño inicial de la ventana
        self.funcionalidades = Funcionalidades(self)

        #menú
        self.menu_principal = Menu(self.root)

        # Opción Inicio con subopciones
        self.opcion_inicio = Menu(self.menu_principal, tearoff=0)
        self.opcion_inicio.add_command(label="Crear Proyecto", command=self.funcionalidades.crear_proyecto)
        self.opcion_inicio.add_command(label="Abrir Proyecto", command=self.funcionalidades.abrir_proyecto)
        self.menu_principal.add_cascade(label="Inicio", menu=self.opcion_inicio)

        # Opción Análisis con subopciones
        self.opcion_analisis = Menu(self.menu_principal, tearoff=0)
        self.opcion_analisis.add_command(label="Análisis por Dialogo", command=self.funcionalidades.analizar_entrevista)
        self.opcion_analisis.add_command(label="Análisis por Oraciones", command=self.funcionalidades.analisis_por_puntos)
        self.menu_principal.add_cascade(label="Análisis", menu=self.opcion_analisis)

        # Opción Acerca de
        self.menu_principal.add_command(label="Acerca de")

        # Configurar menú
        self.root.config(menu=self.menu_principal)

        # Dividir la ventana en 3 partes
        self.frame_superior_izquierdo = tk.Frame(self.root, bg="lightblue")
        self.frame_superior_izquierdo.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.frame_inferior_izquierdo = tk.Frame(self.root, bg="lightblue")
        self.frame_inferior_izquierdo.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Frame en el centro
        self.frame_central = tk.Frame(self.root)
        self.frame_central.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=10)

        # Enlazar el evento de clic derecho en el frame_central con la función analizar_sentimiento_desde_seleccion
        #self.frame_central.bind("<Button-3>", self.funcionalidades.analizar_sentimiento_desde_seleccion)
        # Agregar barra de desplazamiento vertical
        scrollbar = Scrollbar(self.frame_central)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Etiqueta para "Documentos" arriba del frame central
        self.label_documentos = tk.Label(self.frame_central, text="Documentos", bg="lightgreen")
        self.label_documentos.pack()

        # Text widget
        self.text_contenido = tk.Text(self.frame_central, wrap="word", yscrollcommand=scrollbar.set)
        self.text_contenido.pack(expand=True, fill=tk.BOTH)

        self.text_contenido.bind("<Button-3>", self.funcionalidades.mostrar_menu_contextual_s)
        # Configurar barra de desplazamiento para que se sincronice con el text widget
        scrollbar.config(command=self.text_contenido.yview)

        # Dos frames divididos
        self.frame_superior_derecho = tk.Frame(self.root, bg="lightcoral")
        self.frame_superior_derecho.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Text widget para mostrar contenido en el frame superior derecho
        self.text_contenido_superior_derecho = tk.Text(self.frame_superior_derecho, wrap="word")
        self.text_contenido_superior_derecho.pack(expand=True, fill=tk.BOTH)

        self.frame_inferior_derecho = tk.Frame(self.root, bg="lightcoral")
        self.frame_inferior_derecho.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        # Configurar pesos de las columnas y filas
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)  # Text widget ocupa 3 veces más espacio que los frames
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Desactivar propagación de tamaño automático
        self.frame_superior_izquierdo.pack_propagate(False)
        self.frame_inferior_izquierdo.pack_propagate(False)
        self.frame_central.pack_propagate(False)
        self.frame_superior_derecho.pack_propagate(False)
        self.frame_inferior_derecho.pack_propagate(False)

        # Creamos el Notebook (pestañas)
        self.notebook = ttk.Notebook(self.frame_superior_izquierdo)
        self.notebook.pack(fill='both', expand='yes')

        # pestañas "Positivo", "Negativo" y "Neutro"
        self.frame_positivos = tk.Frame(self.notebook, bg="lightblue")
        self.frame_negativos = tk.Frame(self.notebook, bg="lightblue")


        #pestañas del Notebook
        self.notebook.add(self.frame_positivos, text="Positivo")
        self.notebook.add(self.frame_negativos, text="Negativo")



        #Etiquetas para las divisiones
        tk.Label(self.frame_inferior_izquierdo, text="Colores de Clasificación", bg="lightblue").pack()
        tk.Label(self.frame_inferior_izquierdo, text="Negativo: Rojo", bg="#ff7c70").pack()
        tk.Label(self.frame_inferior_izquierdo, text="Positivo: Verde", bg="#B2FFB2").pack()
        tk.Label(self.frame_superior_derecho, text="Contenido", bg="lightcoral").pack()
        tk.Label(self.frame_inferior_derecho, text="Información", bg="lightcoral").pack()

    def iniciar(self):
        self.root.mainloop()


if __name__ == "__main__":
    interfaz = Interfaz()
    interfaz.iniciar()
