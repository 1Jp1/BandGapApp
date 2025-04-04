import numpy as np
import matplotlib.pyplot as plt

import io
import base64
import pandas as pd
import re
import csv
from flask import Flask, request, jsonify, render_template


stored_data = {}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

def get_clean_headers(file_content):
    """
    Función auxiliar para procesar encabezados
    """
    try:
        # Convertir contenido a objeto file-like
        file_obj = io.StringIO(file_content)
        
        # Leer solo los encabezados
        df = pd.read_csv(file_obj, encoding='utf-8-sig', nrows=0)
        
        # Filtrar columnas Unnamed
        clean_headers = [
            col.strip() for col in df.columns 
            if col.strip() and not re.match(r'^Unnamed:\s*\d+$', str(col))
        ]
        
        return clean_headers
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

@app.route("/read", methods=["POST"])
def read_data():
    global stored_data  # Necesario para modificar la variable global
    
    if 'archivo' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400

    file = request.files['archivo']
    
    try:
        # Leer contenido del archivo
        file_content = file.read().decode('utf-8-sig')
        file_obj = io.StringIO(file_content)
        
        # Leer el DataFrame completo
        df = pd.read_csv(file_obj, encoding='utf-8-sig')
        
        # Obtener encabezados limpios
        headers = [
            col.strip() for col in df.columns 
            if col.strip() and not re.match(r'^Unnamed:\s*\d+$', str(col))
        ]
        
        if not headers:
            return jsonify({"error": "No se encontraron encabezados válidos"}), 500
        
        # Almacenar los datos
        stored_data = {
            'df': df.to_dict('list'),
            'headers': headers,
            
        }
        
        print("Datos almacenados:", stored_data.keys())
        return jsonify({
            "status": "success",
            "headers": headers,
            "count": len(headers)
        })
    
    except UnicodeDecodeError:
        return jsonify({"error": "Error de codificación del archivo"}), 400
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    

@app.route("/graph", methods=["POST"])
def graph():

    file =  request.files['archive']
    value = int(request.form.get('value'))
    option = request.form.get('option')


    file_content = file.read().decode('utf-8-sig')
    file_obj = io.StringIO(file_content)
        
    # Leer el DataFrame completo
    df = pd.read_csv(file_obj, encoding='utf-8-sig' , header=1)

    x1 = pd.to_numeric(df.iloc[:, (value )], errors='coerce')  # Columna 1 (índice 0)
    y1 = pd.to_numeric(df.iloc[:, (value + 1)], errors='coerce')  # Columna 2 (índice 1)

    if option == "1":
        plt.figure(figsize=(20, 5))

        plt.subplot(1, 2, 1)
        plt.plot(x1, y1, 'b-', linewidth=1.5)
        plt.title(f"{df.columns[ value ]} vs {df.columns[ value + 1]}", fontsize=12)
        plt.xlabel(df.columns[value ], fontsize=10)
        plt.ylabel(df.columns[ value + 1], fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        plt.close()

        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

    elif option == "2":

        wavelenght = x1
        reflectance = y1
        n = 2
        h = 1237.9
        p_energy = h/wavelenght
        y_tauc = (p_energy * reflectance) ** ( 1 / n )
        
        plt.figure(figsize=(20, 10))
        plt.plot(p_energy, y_tauc, label='Grafica Normalizada')
        # plt.plot(x_region, a + b * x_region, 'r--', label=f'Ajuste lineal: $E_g$ = {E_g:.2f} eV')
        plt.xlabel(r'$h\nu$ (eV)' ,fontsize = 10)
        plt.ylabel(r'$(h \nu F(R))^{1/n}$' , fontsize = 10)
        plt.title("Grafica Normalizada", fontsize = 12)
        plt.legend()
        
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        plt.close()

        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
    
    elif option == "3":

        lower_value = float(request.form.get('lowerBandGap'))
        upper_value = float(request.form.get('upperBandGap'))

        wavelenght = x1
        reflectance = y1
        n = 2
        h = 1237.9
        p_energy = h/wavelenght
        y_tauc = (p_energy * reflectance) ** ( 1 / n )

        region = (p_energy >= lower_value) & (p_energy <= upper_value)  # Selección más razonable
        x_region = p_energy[region]
        y_region = y_tauc[region]

        # Ajustar línea recta a la región seleccionada
        b, a = np.polyfit(x_region, y_region, 1)

        # Calcular Band Gap (intersección con el eje x)
        E_g = -a / b
        # Gráfica del Band Gap
        plt.figure(figsize=(20, 10))
        plt.plot(p_energy, y_tauc, label='Grafica Normalizada')
        plt.plot(x_region, a + b * x_region, 'r--', label=f'Ajuste lineal: $E_g$ = {E_g:.2f} eV')
        plt.xlabel(r'$h\nu$ (eV)' ,fontsize = 10)
        plt.ylabel(r'$(h \nu F(R))^{1/n}$' , fontsize = 10)
        plt.title(f'Band Gap estimado: {E_g:.2f} eV', fontsize = 20)
        plt.legend()
        
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        plt.close()

        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()    


    return jsonify({"image": image_base64})
    
        



# @app.route("/generar-grafica", methods=["POST"])
# def generar_grafica():
#     datos = request.json
#     data = datos["data"]  # Array de pares x, y
#     option = datos["option"]  # Opción seleccionada

#     df = pd.DataFrame(data, columns=["x", "y"])
#     wavelength = df['x'].to_numpy()
#     reflectance = df['y'].to_numpy()

#     # Parámetros para la conversión
#     n = 2  # Dependiendo del material (usualmente 2 para semiconductores)
#     h = 1237.9  # Constante para calcular energía en eV
#     p_energy = h / wavelength
#     y_tauc = (p_energy * reflectance) ** (1 / n)

#     # Corregir el intervalo de selección
#     region = (p_energy >= 1.5) & (p_energy <= 4)  # Selección más razonable
#     x_region = p_energy[region]
#     y_region = y_tauc[region]

#     # Ajustar línea recta a la región seleccionada
#     b, a = np.polyfit(x_region, y_region, 1)

#     # Calcular Band Gap (intersección con el eje x)
#     E_g = -a / b

#     if option == "1":
#         # Gráfica normalizada
#         plt.figure()
#         plt.plot(p_energy, y_tauc, label="Gráfica original")
#         plt.title("Gráfica normalizada")
#         plt.xlabel("hv (eV)")
#         plt.ylabel(r"$(h\nu F(R))^{1/2}$")
#         plt.legend()
#         plt.grid(True)

#     elif option == "2":
#         # Gráfica del Band Gap
#         plt.figure()
#         plt.plot(p_energy, y_tauc, label='Datos de Tauc')
#         plt.plot(x_region, a + b * x_region, 'r--', label=f'Ajuste lineal: $E_g$ = {E_g:.2f} eV')
#         plt.xlabel(r'$h\nu$ (eV)')
#         plt.ylabel(r'$(h \nu F(R))^{1/n}$')
#         plt.legend()
#         plt.title(f'Band Gap estimado: {E_g:.2f} eV')
#         plt.grid(True)

#     elif option == "3":



#     else:
#         return jsonify({"error": "Opción no válida"}), 400

#     # Guardar la gráfica y enviarla como base64
#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     buf.seek(0)
#     plt.close()

#     image_base64 = base64.b64encode(buf.read()).decode("utf-8")
#     buf.close()

#     return jsonify({"image": image_base64})

if __name__ == "__main__":
    app.run(debug=True)
