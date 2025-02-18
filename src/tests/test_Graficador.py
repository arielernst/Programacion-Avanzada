import unittest
import pytest
from unittest.mock import patch
import sys
from sqlalchemy.orm import Session
from flask import Flask, send_file
from unittest import TestCase
from flask_login import LoginManager
from datetime import timedelta
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user, login_manager
import os
import tempfile
from wordcloud import WordCloud
import aspose.words as aw



sys.path.append(r"C:\Users\-\Desktop\Programacion Avanzada - copia\Programaci-n-Avanzada\Sistema de Reclamos\src")
from modules.databases import Reclamo
from modules.Usuario import UsuarioFinal,JefeDepartamento
from modules.Administrador_de_Datos import AdministradorDeDatos  
from modules.config import db, TestingConfig, DevelopmentConfig
from modules.Informante import InformantePDF, InformanteHTML, GraficadorDeDiagramaCircular, GraficadorDePalabrasClave







def create_app(config_name="development"):
    """Crea y configura la instancia de la aplicación Flask."""
    
    app = Flask(__name__)
    Session(app) 
        #bootstrap1=Bootstrap(app)
    login_manager=LoginManager()
    images=UploadSet('images', IMAGES)


        # Configuración de la app según el entorno
    app.config['SECRET_KEY'] = 'loquemasteguste'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        #app.config["WTF_CSRF_ENABLED"] = False
    app.config["UPLOADED_IMAGES_DEST"] = "src/static/uploads/images"
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
        #app.config.from_object(f"app.config.{config_name.capitalize()}Config")


    config_classes = {
    "development": DevelopmentConfig,
    "testing": TestingConfig
    }

        # Aplicar la configuración correcta
    app.config.from_object(config_classes.get(config_name, DevelopmentConfig))

        # Inicializar las extensiones con la app
    db.init_app(app)
        #bootstrap1.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return JefeDepartamento.query.get(int(user_id))


        #session.init_app(app)
    configure_uploads(app, images)
    #sys.path.append(r"C:\Users\-\Desktop\Programacion Avanzada - copia\Programaci-n-Avanzada\Sistema de Reclamos\src")
    #from app import routes
    return app
"""app = create_app('testing')"""  # Carga una configuración especial para pruebas
    #app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base en memoria
    #app.config["TESTING"] = True


"""with app.app_context():
    db.create_all()  # Crea las tablas en la BD ficticia
    yield app.test_client()  # Devuelve el cliente de pruebas
    db.session.remove()
    db.drop_all()  # Limpia la BD después de cada test


if __name__ == "__main__":
    app.run(debug=True)"""



class TestInformantes(TestCase):
    def setUp(self):
        """ Configuración antes de cada test """
        self.app = create_app('testing')  # Inicializa la app en modo testing
        self.client = self.app.test_client()  # Guarda el test_client en self
        self.app_context=self.app.app_context()
        self.app_context.push()
        
        db.create_all()  # Crea la base de datos
        self.temp_dir = tempfile.TemporaryDirectory()

        self.diagramas_dir = os.path.join(self.temp_dir.name, "..", "static", "diagramas")
        os.makedirs(self.diagramas_dir, exist_ok=True)

        #@login_manager.user_loader
        #def load_user(user_id):
            #return JefeDepartamento.get(user_id)



    def tearDown(self):
        """ Limpieza después de cada test """
        
        db.session.remove()
        db.drop_all()  # Elimina la base de datos
        self.app_context.pop()
        self.temp_dir.cleanup()

    def test_generar_diagrama_circular(self):
        graficador=GraficadorDeDiagramaCircular()
        admin_datos=AdministradorDeDatos(db)
        reclamo = Reclamo(
            autor="Juancito",
            departamento="secretaría técnica",
            fecha="2025/02/27 18:30:34",
            estado="pendiente",
            titulo="Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.",
            descripcion="Está todo en penumbras",
        )

        db.session.add(reclamo)
        db.session.commit()

        secretario_tecnico = JefeDepartamento(
            email="secretariotecnico@email.com",
            nombre_usuario="Tecnico",
            contraseña=generate_password_hash("12345678"),
            Nombre="Secretario",
            Apellido="Tecnico",
            Departamento="secretaría técnica"
        )
        db.session.add(secretario_tecnico)
        db.session.commit()

        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='png')
        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='svg')

        ruta_diagrama = os.path.join(self.temp_dir.name, "..", "static", "diagramas", "Diagrama Circular.png")
        ruta_diagrama_svg = os.path.join(self.temp_dir.name, "..", "static", "diagramas", "Diagrama Circular.svg")

        # Verificar que los archivos existen
        self.assertTrue(os.path.exists(ruta_diagrama))
        self.assertTrue(os.path.exists(ruta_diagrama_svg))

        # Verificar que los archivos no están vacíos
        self.assertGreater(os.path.getsize(ruta_diagrama), 0)
        self.assertGreater(os.path.getsize(ruta_diagrama_svg), 0)




    def test_generar_nube_palabras(self):
        admin_datos= AdministradorDeDatos(db)
        graficador=GraficadorDePalabrasClave()
        reclamo = Reclamo(
            autor="Juancito",
            departamento="secretaría técnica",
            fecha="2025/02/27 18:30:34",
            estado="pendiente",
            titulo="Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.",
            descripcion="Está todo en penumbras",
        )

        db.session.add(reclamo)
        db.session.commit()

        secretario_tecnico = JefeDepartamento(
            email="secretariotecnico@email.com",
            nombre_usuario="Tecnico",
            contraseña=generate_password_hash("12345678"),
            Nombre="Secretario",
            Apellido="Tecnico",
            Departamento="secretaría técnica"
        )
        db.session.add(secretario_tecnico)
        db.session.commit()

        graficador.graficar(admin=admin_datos ,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='png')
        graficador.graficar(admin=admin_datos,departamento=secretario_tecnico.departamento, ruta_base=self.temp_dir.name, tipo='svg')

        ruta_nube = os.path.join(self.temp_dir.name, "..", "static", "diagramas", "Nube de Palabras.png")
        ruta_nube_svg = os.path.join(self.temp_dir.name, "..", "static", "diagramas", "Nube de Palabras.svg")

        # Verificar que los archivos existen
        self.assertTrue(os.path.exists(ruta_nube))
        self.assertTrue(os.path.exists(ruta_nube_svg))

        # Verificar que los archivos no están vacíos
        self.assertGreater(os.path.getsize(ruta_nube), 0)
        self.assertGreater(os.path.getsize(ruta_nube_svg), 0)


if __name__ == '__main__':
    unittest.main()
