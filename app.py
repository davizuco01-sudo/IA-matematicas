import streamlit as st
import os
import subprocess
from mathproadvanced import ejecutar_ia_dinamica
def limpiar_latex(codigo_bruto):
    # 1. Eliminar las etiquetas de bloque de código de Markdown
    codigo_limpio = codigo_bruto.replace("```latex", "").replace("```", "")
    
    # 2. Arreglar el error de los dobles dólares alrededor de align o align*
    codigo_limpio = codigo_limpio.replace("$$\\begin{align*}", "\\begin{align*}")
    codigo_limpio = codigo_limpio.replace("\\end{align*}$$", "\\end{align*}")
    codigo_limpio = codigo_limpio.replace("$$\n\\begin{align*}", "\\begin{align*}")
    codigo_limpio = codigo_limpio.replace("\\end{align*}\n$$", "\\end{align*}")
    
    # 3. Limpiar espacios en blanco innecesarios al principio y al final
    return codigo_limpio.strip()

st.set_page_config(page_title="IA Matemática Suprema", page_icon="🧮", layout="centered")

st.title("🧮 IA Matemática Suprema")
st.markdown("Escribe un problema de cálculo, álgebra o física. El equipo de agentes lo resolverá, investigará aplicaciones y generará el PDF.")

problema_usuario = st.text_area("Enunciado del problema:", height=150, placeholder="Ej: Halla los valores propios de la matriz A = [[2, 1], [1, 2]]...")

if st.button("🚀 Resolver Problema", type="primary"):
    if problema_usuario.strip() == "":
        st.warning("Por favor, escribe un problema primero.")
    else:
        with st.spinner("Los agentes están analizando y redactando..."):
            try:
                # 1. Ejecutamos la IA
                resultado_latex = ejecutar_ia_dinamica(problema_usuario)
                st.success("¡Problema resuelto por los agentes!")
                
                # Mostramos si hay gráfico
                if os.path.exists("grafico.png"):
                    st.image("grafico.png", caption="Visualización del problema")
                
                # 2. Guardamos el LaTeX temporalmente
                nombre_tex = "informe_generado.tex"
                nombre_pdf = "informe_generado.pdf"
                
                with open(nombre_tex, "w", encoding="utf-8") as f:
                    f.write(str(resultado_latex))
                
                # 3. Magia: Compilamos a PDF usando el sistema
                with st.spinner("Compilando el documento a PDF..."):
                    try:
                        # Llama al compilador de LaTeX de tu ordenador
                        subprocess.run(["pdflatex", "-interaction=nonstopmode", nombre_tex], check=True, capture_output=True)
                        
                        # Si funciona, preparamos el botón de descarga del PDF
                        if os.path.exists(nombre_pdf):
                            with open(nombre_pdf, "rb") as pdf_file:
                                PDFbyte = pdf_file.read()
                            
                            st.download_button(
                                label="📄 Descargar Informe en PDF",
                                data=PDFbyte,
                                file_name="Resolucion_IA.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                    except FileNotFoundError:
                        st.error("⚠️ No se encontró el compilador. Para generar PDFs, necesitas instalar MiKTeX en tu Windows.")
                    except subprocess.CalledProcessError:
                        st.warning("⚠️ Hubo un error menor al compilar el PDF (a veces pasa con símbolos raros en LaTeX). Te dejo el código puro abajo.")

                # Siempre damos la opción de copiar el código o bajar el .tex por si acaso
                with st.expander("Ver Código LaTeX Original"):
                    st.code(resultado_latex, language="latex")
                    st.download_button(
                        label="📥 Descargar archivo .tex",
                        data=str(resultado_latex),
                        file_name="informe_generado.tex",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"Ocurrió un error en la IA: {e}")
