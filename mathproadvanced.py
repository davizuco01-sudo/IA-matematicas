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
mi_llm = "groq/llama-3.2-90b-text-preview"

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
        
        # ... el resto de las líneas para dibujar (plt.figure...) se quedan igual
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y_f, 'r-', linewidth=2, label=f"Original")
        plt.plot(x, y_p, 'b--', linewidth=2, label=f"Aproximada")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.title("Visualización Matemática")
        plt.savefig("grafico.png")
        plt.close()
        return "Gráfico generado con éxito como grafico.png."
    except Exception as e:
        return f"Error crítico al graficar: {e}"

# 3. AGENTES
arquitecto = Agent(
    role='Catedrático de Álgebra y Análisis',
    goal='Resolver el problema rigurosamente mostrando todos los pasos.',
    backstory='Dominas tanto las matrices y valores propios como las integrales. Usas la calculadora para evitar errores.',
    tools=[calculadora],
    llm=mi_llm, verbose=True
)

investigador = Agent(
    role='Investigador Científico',
    goal='Contextualizar matemáticamente el problema resuelto.',
    backstory='Posees un vasto conocimiento de física, ingeniería y ciencia de datos. Explicas para qué sirven los conceptos matemáticos en el mundo real usando tu propia memoria.',
    tools=[], 
    llm=mi_llm, verbose=True
)

visualizador = Agent(
    role='Ingeniero Gráfico',
    goal='Decidir si graficar o no, y hacerlo solo cuando proceda.',
    backstory='Tienes criterio propio. Si ves matrices o vectores propios, TIENES ESTRICTAMENTE PROHIBIDO usar la herramienta graficador.',
    tools=[graficador], 
    llm=mi_llm, verbose=True
)

# 4. FLUJO DINÁMICO
def ejecutar_ia_dinamica(problema):
    t1 = Task(
        description=f"Resuelve paso a paso el siguiente problema: {problema}",
        agent=arquitecto,
        expected_output="Solución matemática rigurosa."
    )
    t2 = Task(
        description="Analiza la respuesta del Catedrático y explica en 2 o 3 párrafos las aplicaciones reales de esos conceptos en la ingeniería, física o informática usando tu conocimiento avanzado.",
        agent=investigador,
        expected_output="Sección de aplicaciones prácticas."
    )
    t3 = Task(
        description=(
            "Revisa el problema original y la solución. DECISIÓN CRÍTICA: "
            "¿El problema trata sobre funciones continuas 2D (ej. f(x))? -> SÍ: Usa la herramienta graficador. "
            "¿El problema trata sobre álgebra lineal pura (matrices, valores propios)? -> NO: NO USES LA HERRAMIENTA. Escribe ÚNICAMENTE el texto: 'Gráfico omitido por tratarse de álgebra lineal abstracta'."
        ),
        agent=visualizador,
        expected_output="Confirmación de imagen creada O explicación de omisión."
    )
    t4 = Task(
        description="Genera el código LaTeX definitivo (Clase Article) unificando la solución matemática y las aplicaciones. Si el Visualizador omitió el gráfico, no incluyas el entorno de figura.",
        agent=arquitecto,
        expected_output="Código LaTeX listo para compilar."
    )

    crew = Crew(agents=[arquitecto, investigador, visualizador], tasks=[t1, t2, t3, t4])
    resultado = crew.kickoff()
    
    return str(resultado)

if __name__ == "__main__":
    pass
