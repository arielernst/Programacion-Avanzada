import unittest
import pytest
import os
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

ruta_actual = os.getcwd()+"\src"

sys.path.append(ruta_actual)
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


        #@login_manager.user_loader
        #def load_user(user_id):
            #return JefeDepartamento.get(user_id)



        @self.app.route("/generar_informe/pdf")
        def generar_informe():
            admin_datos=AdministradorDeDatos(db)
            informante=InformantePDF(
                graficador_torta=GraficadorDeDiagramaCircular(),
                graficador_nube=GraficadorDePalabrasClave()
            )
            print("🚀 Entrando a la función de generación de PDF...")
            sys.path.append(r'C:\Users\-\Desktop\Programacion Avanzada - copia\Programaci-n-Avanzada\Sistema de Reclamos\src')
            respuesta = informante.generar_informe(departamento=current_user.departamento, admin_datos=admin_datos)
            print(f"Respuesta de la función: {respuesta}")
            return respuesta
        

        @self.app.route("/generar_informe/html")
        def generar_informe_html():
            admin_datos=AdministradorDeDatos(db)
            informante=InformanteHTML(
                graficador_torta=GraficadorDeDiagramaCircular(),
                graficador_nube=GraficadorDePalabrasClave()
            )
            print("Entrando a la función de generación de HTML...")
            sys.path.append(ruta_actual)
            respuesta = informante.generar_informe(departamento=current_user.departamento, admin_datos=admin_datos)
            print(f"Respuesta de la función: {respuesta}")
            return respuesta


    def tearDown(self):
        """ Limpieza después de cada test """
        
        db.session.remove()
        db.drop_all()  # Elimina la base de datos
        self.app_context.pop()



    @patch("app.user_loader")
    @patch("modules.Informante.send_file")
    def test_descargar_pdf_mockeado(self, mock_send_file, mock_user_loader):
        mock_send_file.return_value = "mocked_response"


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


        

        print("Rutas registradas en la aplicación de prueba:")
        for rule in self.client.application.url_map.iter_rules():
            print(rule)


        with self.client:
            with self.client.application.app_context():
                @self.client.application.route("/test_login")
                def test_login():
                    login_user(secretario_tecnico)
                    return "Logged in"
                
                self.client.get('/test_login')
                
                response = self.client.get("/generar_informe/html")



        print(f"Mock send_file call count: {mock_send_file.call_count}")
        print(f"Mock send_file call args: {mock_send_file.call_args}")
        print(f"Mock send_file call args list: {mock_send_file.call_args_list}")

        


        ruta_real = mock_send_file.call_args[0][0]
        ruta_real_normalizada = os.path.abspath(ruta_real)
        
        print(f"Ruta real normalizada: {ruta_real_normalizada}")



        mock_send_file.assert_called_once_with(ruta_real_normalizada, as_attachment=True)



    @patch("app.user_loader")
    @patch("modules.Informante.send_file")
    def test_descargar_html_mockeado(self, mock_send_file, mock_user_loader):
        
        
        mock_send_file.return_value = "mocked_response"

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

        
        #depuración
        print("Rutas registradas en la aplicación de prueba:")
        for rule in self.client.application.url_map.iter_rules():
            print(rule)


        #login forzado
        with self.client:
            with self.client.application.app_context():
                @self.client.application.route("/test_login")
                def test_login():
                    login_user(secretario_tecnico)
                    return "Logged in"
                
                self.client.get('/test_login')
                
                response = self.client.get("/generar_informe/html")



        print(f"Mock send_file call count: {mock_send_file.call_count}")
        print(f"Mock send_file call args: {mock_send_file.call_args}")
        print(f"Mock send_file call args list: {mock_send_file.call_args_list}")


        #definición de la ruta esperada(ruta_esperada=ruta_real_normalizada)
        ruta_real = mock_send_file.call_args[0][0]
        ruta_real_normalizada = os.path.abspath(ruta_real)
        
        print(f"Ruta real normalizada: {ruta_real_normalizada}")
    



        #se verifica la llamada del send_file una vez a la ruta esperada
        mock_send_file.assert_called_once_with(ruta_real_normalizada, as_attachment=True)


if __name__ == '__main__':
    unittest.main()


