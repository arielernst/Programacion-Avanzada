import pytest
import unittest
from unittest import TestCase
#from unittest.mock import patch
import sys
from sqlalchemy.orm import Session
from flask import Flask
#from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user
from datetime import timedelta
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash
sys.path.append(r"C:\Users\-\Desktop\Programacion Avanzada - copia\Programaci-n-Avanzada\Sistema de Reclamos\src")
from modules.databases import Reclamo
from modules.Usuario import UsuarioFinal,JefeDepartamento
from modules.Administrador_de_Datos import AdministradorDeDatos  
from modules.config import db, TestingConfig, DevelopmentConfig
from modules.preprocesamiento import ProcesadorArchivo
from modules.clasificador import Clasificador




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



class TestAdministradorDeDatos(TestCase):
    """Clase de pruebas para la clase AdministradorDeDatos."""

    def setUp(self):
        """ Configuración antes de cada test """
        self.app = create_app('testing')  # Inicializa la app en modo testing
        self.client = self.app.test_client()  # Guarda el test_client en self
        self.app_context=self.app.app_context()
        self.app_context.push()
        
        db.create_all()

    def tearDown(self):
        """ Limpieza después de cada test """
        
        db.session.remove()
        db.drop_all()  # Elimina la base de datos
        self.app_context.pop()

    
    def test_init_admin(self):
        admin=AdministradorDeDatos(db)
        

        self.assertEqual(admin.jefes, [1,2,3])
        self.assertIsInstance(admin.procesador, ProcesadorArchivo)
        self.assertIsInstance(admin.Clasificador, Clasificador)
        self.assertEqual(admin.db, db)
        self.assertEqual(admin.reclamo, {})

    
    def test_registrar_usuario(self):
            admin=AdministradorDeDatos(db)
            info=admin.guardar_usuario(email='jorge@gmail.com',
                                              nombre_usuario = 'Jorgito',
                                              contraseña='hashedpassword',
                                              Nombre = 'Jorge',
                                              Apellido = 'García',
                                              claustro = 'PAyS')
            usuario_registrado=UsuarioFinal.query.filter(UsuarioFinal.__table__.c.nombre_usuario == "Jorgito").first()
            assert usuario_registrado is not None  # Se insertó correctamente
            assert usuario_registrado.nombre_usuario == 'Jorgito'
            assert usuario_registrado.nombre == 'Jorge'
            assert usuario_registrado.apellido == 'García'
            assert usuario_registrado.claustro == 'PAyS'

    def test_login_usuario(self):
        admin=AdministradorDeDatos(db)
        info=admin.guardar_usuario(email='jorge@gmail.com',
                                              nombre_usuario = 'Jorgito',
                                              contraseña='hashedpassword',
                                              Nombre = 'Jorge',
                                              Apellido = 'García',
                                              claustro = 'PAyS')
        usuario_logueado, funcion=admin.cargar_usuario(nombre_usuario='Jorgito',
                                                      contraseña= 'hashedpassword')

        assert usuario_logueado is not None  # Se inició sesión correctamente
        assert usuario_logueado.nombre_usuario == 'Jorgito'
        assert usuario_logueado.nombre == 'Jorge'
        assert usuario_logueado.apellido == 'García'
        assert usuario_logueado.claustro == 'PAyS'


    def test_guardar_atributo_reclamo(self):
        admin=AdministradorDeDatos(db)
        info=admin.guardar_usuario(email='jorge@gmail.com',
                                              nombre_usuario = 'Jorgito',
                                              contraseña='hashedpassword',
                                              Nombre = 'Jorge',
                                              Apellido = 'García',
                                              claustro = 'PAyS')
        usuario_logueado, funcion=admin.cargar_usuario(nombre_usuario='Jorgito',
                                                      contraseña= 'hashedpassword')
        
        
        admin.guardar_datos_reclamo(autor = usuario_logueado.nombre_usuario, 
                                    titulo = 'Se terminó el agua del dispenser de las secretarías.', 
                                    descripcion='Tenemos sed', 
                                    imagen=False)
        assert admin.reclamo.get('autor')==usuario_logueado.nombre_usuario
        #assert admin.reclamo.get('departamento') == 'maestranza'
        assert admin.reclamo.get('estado') == 'pendiente'
        assert admin.reclamo.get('titulo') =='Se terminó el agua del dispenser de las secretarías.'
        assert admin.reclamo.get('descripcion') == 'Tenemos sed'


    def test_crear_reclamo(self):
            
        admin=AdministradorDeDatos(db)
        info=admin.guardar_usuario(email='jorge@gmail.com',
                                              nombre_usuario = 'Jorgito',
                                              contraseña='hashedpassword',
                                              Nombre = 'Jorge',
                                              Apellido = 'García',
                                              claustro = 'PAyS')
        usuario_logueado, funcion=admin.cargar_usuario(nombre_usuario='Jorgito',
                                                      contraseña= 'hashedpassword')
        


        with self.app.test_request_context():
                    login_user(usuario_logueado)

        #login_user(usuario_logueado)
                    admin.guardar_datos_reclamo(autor = usuario_logueado.nombre_usuario, 
                                    titulo = 'Se terminó el agua del dispenser de las secretarías.', 
                                    descripcion='Tenemos sed', 
                                    imagen=False)
                    admin.crear_reclamo()
        
        
        
        reclamo_creado = Reclamo.query.filter(Reclamo.__table__.c.autor == 'Jorgito').first()
        
        assert reclamo_creado.autor == usuario_logueado.nombre_usuario
        #assert reclamo_creado.departamento == 'maestranza'
        assert reclamo_creado.estado == 'pendiente'
        assert reclamo_creado.titulo =='Se terminó el agua del dispenser de las secretarías.'
        assert reclamo_creado.descripcion == 'Tenemos sed'


    def test_adherir_a_reclamo(self):
        
        admin=AdministradorDeDatos(db)
        info=admin.guardar_usuario(email='jorge@gmail.com',
                                              nombre_usuario = 'Jorgito',
                                              contraseña='hashedpassword',
                                              Nombre = 'Jorge',
                                              Apellido = 'García',
                                              claustro = 'PAyS')
        autor, funcion=admin.cargar_usuario(nombre_usuario='Jorgito',
                                                      contraseña= 'hashedpassword')
        
        info=admin.guardar_usuario(email='juan@example.com', 
                                     nombre_usuario='Juancito', 
                                     contraseña='hashedpassword', 
                                     Nombre='Juan', 
                                     Apellido='Pérez', 
                                     claustro ='estudiante')
        
        adherido, funcion = admin.cargar_usuario(nombre_usuario='Juancito',
                                                 contraseña='hashedpassword')

        with self.app.test_request_context():
                    login_user(autor)

                    admin.guardar_datos_reclamo(autor = autor.nombre_usuario, 
                                    titulo = 'Se terminó el agua del dispenser de las secretarías.', 
                                    descripcion='Tenemos sed', 
                                    imagen=False)
                    admin.crear_reclamo()
        
        
        reclamo_creado = Reclamo.query.filter(Reclamo.__table__.c.titulo == 'Se terminó el agua del dispenser de las secretarías.').first()

        admin.adherir_usuario(usuario = adherido,
                             reclamo_id = reclamo_creado.id)
        
        assert reclamo_creado in adherido.reclamos_seguidos


    def test_output_register_method(self):
         pass
    
    def test_output_login_method(self):
         pass


    def test_obtener_reclamo(self):
        admin=AdministradorDeDatos(db)
        reclamo1 = Reclamo(autor='Juan', departamento='secretaría técnica', fecha='2025/12/02 16:01:26', estado='pendiente', titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', descripcion='eqw')
        reclamo2 = Reclamo(autor='José', departamento='soporte informático', fecha='2023/23/04 09:38:47', estado='pendiente', titulo='No anda la red wifi de alumnos.', descripcion='eqw')
        reclamo3 = Reclamo(autor='Carlos', departamento='maestranza', fecha='2024/16/08 14:47:08', estado='pendiente', titulo='No hay jabón en el baño de varones del ala 3.', descripcion='eqw')


        db.session.add(reclamo1)
        db.session.add(reclamo2)
        db.session.add(reclamo3)
        db.session.commit()


        reclamos=admin.ObtenerReclamos(departamento='secretaría técnica')
        
        
        self.assertIsNotNone(reclamos)
        self.assertEqual(len(reclamos),1)
        self.assertEqual(reclamos[0].autor,'Juan')
        self.assertEqual(reclamos[0].departamento,'secretaría técnica')
        self.assertEqual(reclamos[0].titulo,'Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.')
        self.assertEqual(reclamos[0].estado,'pendiente')




    def test_buscar_reclamos_similares(self):
        reclamo1 = Reclamo(autor='Juan', departamento='secretaría técnica', fecha='2025/12/02 16:01:26', estado='pendiente', titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', descripcion='eqw')
        reclamo2 = Reclamo(autor='José', departamento='soporte informático', fecha='2023/23/04 09:38:47', estado='pendiente', titulo='No anda la red wifi de alumnos.', descripcion='eqw')

        db.session.add(reclamo1)
        db.session.add(reclamo2)
        db.session.commit()


        admin=AdministradorDeDatos(db)
        admin.guardar_datos_reclamo(
                                    autor = 'José', 
                                    titulo = 'El aula 3 está algo oscura. Le falta luminosidad.', 
                                    descripcion='Tenemos sed', 
                                    imagen=False
                                    )
        reclamos=admin.buscar_reclamos_similares()
        self.assertEqual(len(reclamos),1)
        self.assertEqual(reclamos[0].autor,'Juan')
        self.assertEqual(reclamos[0].departamento,'secretaría técnica')
        self.assertEqual(reclamos[0].titulo,'Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.')
        self.assertEqual(reclamos[0].estado,'pendiente')


        def test_obtener_reclamos_departamento_sep_estado(self):
            reclamo1=Reclamo(autor='Juan', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='pendiente', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )
            reclamo2 = Reclamo(autor='Jorge', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='en proceso', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )
            reclamo3 = Reclamo(autor='José', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='resuelto', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )
            reclamo4=Reclamo(autor='Pablo', 
                             departamento='secretaría técnica', 
                             fecha='2025/12/02 16:01:26', 
                             estado='inválido', 
                             titulo='Los pasillos del ala 2 están algo oscuros. Les falta luminosidad.', 
                             descripcion='eqw'
            )

            db.session.add(reclamo1)
            db.session.add(reclamo2)
            db.session.add(reclamo3)
            db.session.add(reclamo4)
            db.session.commit()

            admin = AdministradorDeDatos(db)

            reclamos_enproceso, reclamos_pendiente, reclamos_resuelto, reclamos_invalido = admin.obtener_reclamos_departamento_sep_estado(departamento='secretaría técnica')



            self.assertEqual(reclamos_enproceso[0].autor, 'Jorge')
            self.assertEqual(reclamos_pendiente[0].autor, 'Juan')
            self.assertEqual(reclamos_resuelto[0].autor, 'José')
            self.assertEqual(reclamos_invalido[0].autor, 'Pablo')




if __name__ == '__main__':
    unittest.main()