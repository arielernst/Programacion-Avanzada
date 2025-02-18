#from abc import ABC,abstractclassmethod
from modules.config import db
from modules.databases import Usuario, Column, String, asociacion_usuarios_reclamos
#from modules.Administrador_de_Datos import AdministradorDeDatos
        

class UsuarioFinal (Usuario):

    _claustro=Column('claustro', String(100))

    _reclamos_seguidos = db.relationship('Reclamo', secondary=asociacion_usuarios_reclamos, backref='usuarios_adheridos')

    def __init__(self,Nombre,Apellido,email,nombre_usuario, contraseña, claustro): 
        super().__init__(Nombre,Apellido,email,nombre_usuario, contraseña)
        self._claustro = claustro
        

    @property
    def reclamos_seguidos(self):
        return self._reclamos_seguidos


    @property
    def claustro(self):
        return self._claustro
    
    def adherir_a_reclamo(self, reclamo):
        self._reclamos_seguidos.append(reclamo)

class JefeDepartamento(Usuario):
    
    _departamento = Column('departamento', String(100))

    def __init__(self,Nombre,Apellido,email,nombre_usuario, contraseña, Departamento): 
        super().__init__(Nombre,Apellido,email,nombre_usuario, contraseña)
        self._departamento = Departamento


    @property
    def departamento(self):
        return self._departamento
