# Joshua Aguilar Nieto  Baldemar Emilio López Abreu  Carlos Jeshua Vázquez Dzib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# 1. FUNCIÓN DE CÁLCULO (CPM / BACKEND)
def calcular_cpm(actividades):
    """Calcula ES, EF, LS, LF, Holgura y determina la Ruta Crítica para una red de actividades."""
    # Paso 1: Ida (Forward Pass) - Calcular ES y EF
    for nombre, datos in actividades.items():
        if not datos["preds"]:
            datos["ES"] = 0
        else:
            datos["ES"] = max(actividades[p]["EF"] for p in datos["preds"])
        datos["EF"] = datos["ES"] + datos["duracion"]

    duracion_total = max(datos["EF"] for datos in actividades.values())

    # Paso 2: Vuelta (Backward Pass) - Calcular LF y LS
    for nombre in reversed(list(actividades.keys())):
        datos = actividades[nombre]
        sucesores = [
            n for n, d in actividades.items() if nombre in d["preds"]
        ]

        if not sucesores:
            datos["LF"] = duracion_total
        else:
            datos["LF"] = min(actividades[s]["LS"] for s in sucesores)

        datos["LS"] = datos["LF"] - datos["duracion"]
        datos["holgura"] = datos["LS"] - datos["ES"]
        datos["es_critica"] = datos["holgura"] == 0

    return actividades, duracion_total


# 2. INTERFAZ GRÁFICA (FRONTEND)
class AppCPM:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "Método de la Ruta Crítica (CPM) - Ingeniería Civil (UAC)"
        )
        self.root.geometry("720x650")

        # Variables para almacenar resultados calculados
        self.resultados_actuales = None
        self.duracion_total_actual = None
        self.ruta_critica_actual = []

        # Encabezado
        lbl_titulo = tk.Label(
            root,
            text="Planificación de Obras - Método CPM",
            font=("Arial", 14, "bold"),
        )
        lbl_titulo.pack(pady=10)

        # Entrada de datos
        frame_input = tk.LabelFrame(
            root,
            text="Actividades del Proyecto (Nombre, Duración en días, Predecesoras separadas por coma)",
            padx=10,
            pady=10,
        )
        frame_input.pack(fill="x", padx=15, pady=5)

        lbl_format = tk.Label(
            frame_input,
            text="Formato por línea:  Actividad, Duración, Predecesoras\nEjemplo: A, 3, -\n         B, 4, A",
            font=("Courier", 9),
            justify="left",
            fg="gray",
        )
        lbl_format.pack(anchor="w", pady=2)

        self.txt_datos = tk.Text(frame_input, height=6)
        self.txt_datos.pack(fill="x")

        # Ejemplo precargado
        ejemplo_obra = (
            "A, 3, -\nB, 2, A\nC, 4, A\nD, 3, B\nE, 2, C\nF, 4, D, E"
        )
        self.txt_datos.insert("1.0", ejemplo_obra)

        # Botones de Acción
        frame_botones = tk.Frame(root)
        frame_botones.pack(pady=10)

        btn_calcular = tk.Button(
            frame_botones,
            text="Calcular Ruta Crítica",
            bg="#0056b3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            command=self.procesar_cpm,
        )
        btn_calcular.pack(side="left", padx=5)

        self.btn_guardar = tk.Button(
            frame_botones,
            text="💾 Guardar Reporte (TXT)",
            bg="#28a745",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            state="disabled",
            command=self.guardar_reporte_txt,
        )
        self.btn_guardar.pack(side="left", padx=5)

        # Resumen general
        self.lbl_duracion = tk.Label(
            root,
            text="Duración total del proyecto: -- días",
            font=("Arial", 11, "bold"),
            fg="blue",
        )
        self.lbl_duracion.pack(pady=2)

        self.lbl_ruta = tk.Label(
            root, text="Ruta Crítica: --", font=("Arial", 11, "bold"), fg="red"
        )
        self.lbl_ruta.pack(pady=2)

        # Tabla de resultados
        frame_tabla = tk.Frame(root)
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=10)

        columnas = (
            "Act",
            "Duración",
            "ES",
            "EF",
            "LS",
            "LF",
            "Holgura",
            "Crítica?",
        )
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings"
        )

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=75, anchor="center")

        self.tabla.pack(fill="both", expand=True)

    def procesar_cpm(self):
        contenido = self.txt_datos.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning(
                "Advertencia", "Ingresa al menos una actividad."
            )
            return

        actividades = {}
        try:
            for linea in contenido.split("\n"):
                if not linea.strip():
                    continue
                partes = [p.strip() for p in linea.split(",")]
                nombre = partes[0]
                duracion = int(partes[1])
                preds = (
                    []
                    if partes[2] == "-" or not partes[2]
                    else [p.strip() for p in partes[2:]]
                )

                actividades[nombre] = {"duracion": duracion, "preds": preds}

            resultados, duracion_total = calcular_cpm(actividades)

            # Guardar en memoria para exportación
            self.resultados_actuales = resultados
            self.duracion_total_actual = duracion_total

            # Limpiar tabla previa
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            self.ruta_critica_actual = []
            for nombre, d in resultados.items():
                critica_str = "SÍ" if d["es_critica"] else "NO"
                if d["es_critica"]:
                    self.ruta_critica_actual.append(nombre)

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        nombre,
                        d["duracion"],
                        d["ES"],
                        d["EF"],
                        d["LS"],
                        d["LF"],
                        d["holgura"],
                        critica_str,
                    ),
                )

            self.lbl_duracion.config(
                text=f"Duración total del proyecto: {duracion_total} días"
            )
            self.lbl_ruta.config(
                text=f"Ruta Crítica: {' -> '.join(self.ruta_critica_actual)}"
            )

            # Habilitar el botón de guardar
            self.btn_guardar.config(state="normal")

        except Exception:
            messagebox.showerror(
                "Error de formato",
                "Asegúrate de ingresar las actividades con el formato correcto.\nEjemplo: A, 3, -",
            )

    def guardar_reporte_txt(self):
        if not self.resultados_actuales:
            return

        # Ventana emergente para seleccionar ubicación del archivo
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar Reporte CPM",
            initialfile="reporte_ruta_critica.txt",
        )

        if archivo:
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write("===============================================\n")
                    f.write("     REPORTE DE PLANIFICACIÓN DE OBRA (CPM)    \n")
                    f.write("     Universidad Autónoma de Campeche (UAC)    \n")
                    f.write("===============================================\n\n")

                    f.write(
                        f"Duración Total del Proyecto: {self.duracion_total_actual} días\n"
                    )
                    f.write(
                        f"Ruta Crítica: {' -> '.join(self.ruta_critica_actual)}\n\n"
                    )

                    f.write(
                        "----------------------------------------------------------------------\n"
                    )
                    f.write(
                        f"{'Act':<6}{'Duración':<10}{'ES':<8}{'EF':<8}{'LS':<8}{'LF':<8}{'Holgura':<10}{'Crítica?':<8}\n"
                    )
                    f.write(
                        "----------------------------------------------------------------------\n"
                    )

                    for nombre, d in self.resultados_actuales.items():
                        critica_str = "SÍ" if d["es_critica"] else "NO"
                        f.write(
                            f"{nombre:<6}{d['duracion']:<10}{d['ES']:<8}{d['EF']:<8}"
                            f"{d['LS']:<8}{d['LF']:<8}{d['holgura']:<10}{critica_str:<8}\n"
                        )

                    f.write(
                        "----------------------------------------------------------------------\n"
                    )

                messagebox.showinfo(
                    "Éxito", f"Reporte guardado exitosamente en:\n{archivo}"
                )

            except Exception as err:
                messagebox.showerror(
                    "Error", f"No se pudo guardar el archivo: {err}"
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = AppCPM(root)
    root.mainloop()