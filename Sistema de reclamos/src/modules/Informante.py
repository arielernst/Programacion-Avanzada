"""import matplotlib
from wordcloud import WordCloud,ImageColorGenerator
from PIL import Image
import numpy as np
"""
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from modules.databases import Reclamo
from wordcloud import WordCloud, ImageColorGenerator
from nltk.corpus import stopwords
from pdfkit import configuration, from_string
from jinja2 import FileSystemLoader, Environment, Template
from fpdf import FPDF
from flask import send_file

import os


import aspose.words as aw

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class Graficador(ABC):

    @abstractmethod    
    def graficar(self, admin, departamento, ruta_base, tipo):
        pass

class GraficadorDeDiagramaCircular(Graficador): 
    def graficar(self, admin, departamento, ruta_base, tipo):
        """"Genera diagrama circular, con los reclamos, 
        para visualizar las proporciones de los reclamos en sus diversos estados"""
        if ruta_base=='default':
            ruta_base = os.path.abspath(os.path.dirname(__file__))
        else:
            ruta_base=ruta_base
        #ruta_pdf = os.path.join(ruta_base, "..", "static", "docs", "Informe_Reclamos.pdf")
        ruta_diagrama = os.path.join(ruta_base, "..", "static", "diagramas", "Diagrama Circular.png")
        #ruta_nube = os.path.join(ruta_base, "..", "static", "diagramas", "Nube de Palabras.png")
        ruta_diagrama_svg = os.path.join(ruta_base, "..", "static", "diagramas", "Diagrama Circular.svg")


        plt.figure(figsize=[10,8])
        estados_reclamos=["pendiente", "en proceso", "resuelto", "inválido"]
        reclamos_enproceso, reclamos_pendiente, reclamos_resuelto, reclamos_invalido = admin.obtener_reclamos_departamento_sep_estado(departamento)

        print(reclamos_resuelto)
        print(reclamos_enproceso)
        print(reclamos_invalido)
        print(reclamos_pendiente)
        cantidades=[len(reclamos_pendiente),len(reclamos_enproceso), len(reclamos_resuelto), len(reclamos_invalido)]
        plt.style.use("ggplot")
        plt.title("Estados de los reclamos")
        plt.pie(x=cantidades, labels=estados_reclamos, autopct="%.2f%%", labeldistance=None)              #, autopct="%.2f%%"
        #plt.axis= ("equal")
        plt.legend(loc="upper left")
        if tipo=='svg':
            plt.savefig(ruta_diagrama_svg)
        elif tipo=='png':
            plt.savefig(ruta_diagrama)
        else:
            raise Exception 

class GraficadorDePalabrasClave(Graficador): 

    def graficar(self,admin,departamento, ruta_base, tipo):
        """Grafica las palabras que más se repiten en los reclamos correspondientes al departamento"""
        if ruta_base=='default':
            ruta_base = os.path.abspath(os.path.dirname(__file__))
        else:
            ruta_base = ruta_base
        #ruta_pdf = os.path.join(ruta_base, "..", "static", "docs", "Informe_Reclamos.pdf")
        #ruta_diagrama = os.path.join(ruta_base, "..", "static", "diagramas", "Diagrama Circular.png")
        ruta_nube = os.path.join(ruta_base, "..", "static", "diagramas", "Nube de Palabras.png")
        ruta_nube_svg=os.path.join(ruta_base, '..', 'static', 'diagramas', 'Nube de Palabras.svg')

        texto = ""

        reclamos=admin.ObtenerReclamos(departamento)
        
        for reclamo in reclamos:
            texto = f"{texto} {reclamo.titulo} {reclamo.descripcion}"

        # Create and generate a word cloud image:
        palabras = stopwords.words('spanish')
        wordcloud = WordCloud(stopwords=palabras, max_words=15, background_color="white").generate(texto)

        wordcloud.to_file(ruta_nube)

        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        if tipo=='png':
            shape = builder.insert_image(ruta_nube)
        elif tipo=='svg':
            shape = builder.insert_image(ruta_nube)
            shape.get_shape_renderer().save(ruta_nube_svg, aw.saving.ImageSaveOptions(aw.SaveFormat.SVG))



class Informante(ABC):
    
    @abstractmethod
    def __init__(self, graficador_torta, graficador_nube):
        self._graficador_torta = graficador_torta
        self._graficador_nube = graficador_nube


    @abstractmethod
    def generar_informe(self, departamento, admin_datos):
        pass




class InformantePDF(Informante):


    def __init__(self, graficador_torta, graficador_nube):
        self._graficador_torta = graficador_torta
        self._graficador_nube = graficador_nube


    def generar_informe(self, departamento, admin_datos):
        
        self._graficador_torta.graficar(admin_datos, departamento, 'default', 'png')
        self._graficador_nube.graficar(admin_datos, departamento, 'default', 'png')
        
        ruta_base = os.path.abspath(os.path.dirname(__file__))
        ruta_pdf = os.path.join(ruta_base, "..", "static", "docs", "Informe_Reclamos.pdf")
        ruta_diagrama = os.path.join(ruta_base, "..", "static", "diagramas", "Diagrama Circular.png")
        ruta_nube = os.path.join(ruta_base, "..", "static", "diagramas", "Nube de Palabras.png")
        

        ruta_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/docs/Informe_Reclamos.pdf"))
        print(f"📄 Nueva ruta corregida: {ruta_pdf}")
        c = canvas.Canvas(ruta_pdf, pagesize=(595.27, 841.89))

        c.setTitle("Informe de reclamos.pdf")

        c.setFont('Helvetica', 16)
        c.drawString(50, 780, "Informe de Reclamos de" + departamento)

        c.setFontSize(12)  

        c.drawImage(ruta_diagrama, 50, 500, width=312.5, height=250)

        c.drawImage(ruta_nube, 50, 240, width= 312.5, height= 250)

        reclamos= admin_datos.ObtenerReclamos(departamento)
        c.drawString(50, 230, "Los reclamos presentados a " + departamento + " son:")


        x=50
        y=210


        for reclamo in reclamos:
            c.drawString(x, y, reclamo.titulo + ' | ' + reclamo.estado)
            y-=20
            if y <= 50:
                c.showPage()
                c.setFont("Helvetica", 12)  
                y = 780
 
        c.showPage()

        c.save()

        print(f"PDF generado en: {ruta_pdf}")

        if not os.path.exists(ruta_pdf):
            print(f"ERROR: El archivo {ruta_pdf} NO fue generado correctamente")
        else:
            print(f"El archivo {ruta_pdf} fue generado correctamente")

        #return send_file(ruta_pdf, as_attachment=True)
        try:
            return send_file(ruta_pdf, as_attachment=True)
        except Exception as e:
            print(f"ERROR en send_file: {e}")
            raise

class InformanteHTML(Informante):

    def __init__(self, graficador_torta, graficador_nube):
        self._graficador_torta = graficador_torta
        self._graficador_nube = graficador_nube


    def generar_informe(self, departamento,admin_datos):
        self._graficador_torta.graficar(admin_datos, departamento, 'default', 'svg')
        self._graficador_nube.graficar(admin_datos, departamento, 'default', 'svg')

        
        ruta_base = os.path.abspath(os.path.dirname(__file__))
        ruta_html = os.path.join(ruta_base, "..", "static", "docs", "Informe_Reclamos.html")
        ruta_diagrama = os.path.join(ruta_base, "..", "static", "diagramas", "Diagrama Circular.svg")
        ruta_nube = os.path.join(ruta_base, "..", "static", "diagramas", "Nube de Palabras.svg")
        
        ruta_html = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/docs/Informe_Reclamos.html"))

        with open(ruta_diagrama,'r', encoding='utf-8') as file:
            torta = file.read()

        
        with open(ruta_nube,'r', encoding='utf-8') as file:
            nube = file.read()


        reclamos= admin_datos.ObtenerReclamos(departamento)

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Galería de Imágenes</title>
</head>
<body>
    {torta}
    <h1></h1>
    {nube}\n
    <h5>Los reclamos presentados a {departamento} son: </h5>\n
"""

        for reclamo in reclamos:
            html_template += f"        <li>{reclamo.titulo} | {reclamo.estado} </li>\n"

        html_template += """    </ul>
</body>
</html>""" 
        
        with open("./src/static/docs/Informe_Reclamos.html", 'w', encoding= 'utf-8') as informe:
            informe.write(html_template)
        
        
        return send_file(ruta_html, as_attachment=True)
            















