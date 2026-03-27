import os
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import re
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import tool

# APAGAMOS LA TELEMETRÍA PARA EVITAR TIMEOUTS
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# 1. CONFIGURACIÓN
load_dotenv()
# VOLVEMOS AL 70B: Ahora que no leemos PDFs gigantes, no rozaremos el límite de la API.
mi_llm = "groq/llama-3.3-70b-versatile"

# --- TÚNEL DE LAVADO LATEX ---
def limpiar_latex(codigo_bruto):
    # Convertimos a string por si CrewAI devuelve un objeto complejo
    codigo_limpio = str(codigo_bruto)
    
    # 1. Eliminar las etiquetas de bloque de código de Markdown
    codigo_limpio = codigo_limpio.replace("```latex", "").replace("```", "")
    
    # 2. Arreglar el error de los dobles dólares alrededor de align o align*
    codigo_limpio = codigo_limpio.replace("$$\\begin{align*}", "\\begin{align*}")
    codigo_limpio = codigo_limpio.replace("\\end{align*}$$", "\\end{align*}")
    codigo_limpio = codigo_limpio.replace("$$\n\\begin{align*}", "\\begin{align*}")
    codigo_limpio = codigo_limpio.replace("\\end{align*}\n$$", "\\end{align*}")
    
    # 3. Inyectar el paquete de símbolos de números reales y complejos
    codigo_limpio = codigo_limpio.replace("\\usepackage{amsmath}", "\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{amsfonts}")
    
    # 4. Limpiar espacios en blanco innecesarios al principio y al final
    return codigo_limpio.strip()

# 2. HERRAMIENTAS BLINDADAS
@tool("calculadora")
def calculadora(expresion: str, operacion: str):
    """Calcula operaciones de álgebra (escribe 'simplificar' para matrices), integrales ('integrar') o derivadas ('derivar')."""
    try:
        if operacion == 'simplificar':
            res = eval(expresion, {"Matrix": sp.Matrix, "sp": sp})
            return f"Resultado matricial: {res}"
        
        x = sp.Symbol('x')
        expr = sp.sympify(expresion.replace('ln', 'log'))
        res = sp.integrate(expr, x) if operacion == 'integrar' else sp.diff(expr, x)
        return f"Resultado exacto: {res}"
    except Exception as e:
        return f"Error en la calculadora: {e}"

@tool("graficador")
def graficador(f_original: str, f_aprox: str):
    """Solo úsala si el problema es de funciones continuas f(x). Genera 'grafico.png'."""
    try:
        x = np.linspace(-1, 1, 400)
        
        def limpiar(texto):
            # AQUÍ ESTÁ LA MAGIA: Le enseñamos a leer senos y cosenos
            t = texto.lower().replace('^', '**').replace('e**x', 'np.exp(x)').replace('exp(x)', 'np.exp(x)')
            t = t.replace('sin', 'np.sin').replace('cos', 'np.cos') 
            t = re.sub(r'(\d)([a-z\(])', r'\1*\2', t)
            return t

        y_f = eval(limpiar(f_original), {"np": np, "x": x})
        y_p = eval(limpiar(f_aprox), {"np": np, "x": x})
        
        plt.figure(figsize=(10, 6))
