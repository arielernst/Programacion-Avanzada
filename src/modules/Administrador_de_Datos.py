from datetime import datetime
from mimetypes import guess_type
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from modules.config import db, images


from modules.forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user
from flask import session


from modules.databases import Usuario, Reclamo
from modules.Usuario import UsuarioFinal, JefeDepartamento
from modules.clasificador import Clasificador
from modules.preprocesamiento import ProcesadorArchivo


class AdministradorDeDatos:
    
    
    def __init__(self, db):
        
        self._jefes=[1,2,3]
        self._reclamo = {}
        self._db=db


        self._procesador = ProcesadorArchivo("frases.json")

        self.x,self.y = self._procesador.datosEntrenamiento

        self._Clasificador = Clasificador(self.x,self.y,escalado=True)


    @property
    def jefes(self):
        return self._jefes
        

    @property
    def reclamo(self):
        return self._reclamo
        
    @property
    def procesador(self):
        return self._procesador
        
    @property
    def Clasificador(self):
        return self._Clasificador

    @property
    def db(self):
        return self._db
    

    def guardar_usuario(self, email, nombre_usuario, contraseña, Nombre, Apellido, claustro):
       
        """Verifica que los datos ingresados para el registro sean válidos y, si son válidos,
          los guarda en la base de datos, devuelve el formulario del registro)"""     
      
        info = "Usuario registrado exitosamente, inicie sesión para ingresar"


        if Usuario.query.filter(UsuarioFinal.__table__.c.nombre_usuario == email).first():  #si existe un usuario con ese email es True sino False
            info="El email ingresado corresponde a otro usuario"


        elif Usuario.query.filter(UsuarioFinal.__table__.c.nombre_usuario == nombre_usuario).first():   #lo mismo con el nombre de usuario
            info="El nombre de usuario ingresado ya fue registrado"
            
        else:
            contraseña_encriptada = generate_password_hash(password= contraseña, 
                                                           method= 'pbkdf2:sha256', 
                                                           salt_length=8)                           #Se encripta la contraseña


            usuario = UsuarioFinal(email = email, 
                                   nombre_usuario = nombre_usuario, 
                                   contraseña = contraseña_encriptada, 
                                   Nombre = Nombre, 
                                   Apellido = Apellido, 
                                   claustro = claustro)  #se crea al usuario, obviamente se le guarda la contraseña encriptada


            self._db.session.add(usuario)
            self._db.session.commit()

        return info

    def cargar_usuario(self, nombre_usuario, contraseña):
        
        """Busca el usuario al que corresponden los datos en la base de datos y si este usuario existe,
        crea una instancia usuario correspondiente al mismo""" 

        funcion = "inicio_Usuarios_Finales"


        usuario = UsuarioFinal.query.filter(UsuarioFinal.__table__.c.nombre_usuario == nombre_usuario).first()
     
        if not usuario:
            usuario=JefeDepartamento.query.filter(JefeDepartamento.__table__.c.nombre_usuario == nombre_usuario).first()
            
        if not usuario:        
            funcion="El usuario ingresado no existe"
            
        elif check_password_hash(usuario.contraseña , contraseña):
            return usuario, funcion

        
        usuario=None

        return usuario,funcion
    



    def guardar_datos_reclamo(self, autor, titulo, descripcion, imagen):
        
        """Guarda los datos enviados al formulario en un diccionario"""
        contenido = ["No puedo enviar mi trabajo por correo electrónico porque la red no funciona."]

        contenido.append(titulo)

        dpto = self._Clasificador.clasificar(contenido)
        print(dpto)

        self._reclamo={
                            'autor' : autor,
                            'departamento' : dpto[1],
                            'fecha' : datetime.strftime(datetime.now(),'%Y/%m/%d %H:%M:%S'),
                            'estado' : "pendiente", 
                            'titulo' : str(titulo),
                            'descripcion' : str(descripcion)

        }
        if imagen:
            
            self._reclamo['imagen']=images.save(imagen)
            



    def crear_reclamo(self):
        """Con los datos de self.reclamo, instancia un reclamo y lo guarda en la base de datos."""
        freclamo = Reclamo(autor = self._reclamo.get('autor'),
                            departamento = self._reclamo.get('departamento'),
                            fecha = self._reclamo.get('fecha'),
                            estado = self._reclamo.get('estado'), 
                            titulo=self._reclamo.get('titulo'),
                            descripcion = self._reclamo.get('descripcion'))

        if self._reclamo.get('imagen'):
            freclamo.imagen = self._reclamo.get('imagen')
        
        
        self._db.session.add(freclamo)
        self._db.session.commit()

        self.adherir_usuario(current_user, freclamo.id)
        
        
        
        
        '''if self.reclamo.get('imagen'):
            
        
            reclamo=Reclamo.query.get(int(reclamo.id))
            reclamo.agregar_imagen(self.reclamo.get('imagen'))
            db.session.commit()'''
        


    """def Guardar_Reclamo(self):
        Guarda el reclamo en la base de datos
        
        reclamo = Reclamo(autor=self.reclamoGuardado.Autor, 
                           adheridos = "", 
                           departamento = self.reclamoGuardado.tipo, 
                           fecha = self.reclamoGuardado.Fecha, 
                           estado = self.reclamoGuardado.mostrar_estado,
                           titulo=self.reclamoGuardado.Titulo, 
                           descripcion= self.reclamoGuardado.Descripcion)
        
        db.session.add(reclamo)
        db.session.commit()"""


    def adherir_usuario(self, usuario, reclamo_id):
        """Agrega al usuario a los Adheridos al reclamo dado en la base de datos"""       
        reclamo = Reclamo.query.get(reclamo_id)
        usuario.adherir_a_reclamo(reclamo)
        self._db.session.commit()


    
    def ObtenerReclamos(self, departamento):
        """Filtra los reclamos según el departamento dado"""
        reclamos = Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento).all()
        return reclamos
    


    def buscar_reclamos_similares(self):
        """Busca reclamos similares al reclamo guardado en el self.reclamo"""
        texto=self._reclamo.get('titulo')
        vacias=stopwords.words('spanish')
        text_tokens = word_tokenize(texto)

        palabras_clave = [word for word in text_tokens if not word in vacias and len(word)>3]

        resultados=[]

        for palabra_clave in palabras_clave:
            reclamos = Reclamo.query.filter(Reclamo.__table__.c.titulo.like(f"%{palabra_clave}%")).all()
            for reclamo in reclamos:
                if reclamo not in resultados:
                    resultados.append(reclamo)

        return resultados


    def obtener_reclamos_departamento_sep_estado(self, departamento):
        """Obtiene todos los reclamos del departamento pedido, y devuelve 4 listas, una para cada estado de reclamo"""
        reclamos_enproceso=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "en proceso").all())
        reclamos_pendiente=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "pendiente").all())
        reclamos_resuelto=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "resuelto").all())
        reclamos_invalido=list(Reclamo.query.filter(Reclamo.__table__.c.departamento == departamento , Reclamo.__table__.c.estado == "inválido").all())
        return reclamos_enproceso, reclamos_pendiente, reclamos_resuelto, reclamos_invalido