from flask import render_template, request, redirect, url_for, flash, abort,Flask, session, send_file
from flask_login import login_user, login_required, current_user, logout_user
from modules.config import app, db, login_manager
from modules.Administrador_de_Datos import AdministradorDeDatos
from modules.databases import Reclamo
from modules.forms import RegisterForm, LoginForm, FormularioCrearReclamo, FormularioEditarReclamo, ParaSecretarioTecnico
from modules.Usuario import JefeDepartamento, UsuarioFinal
from werkzeug.security import generate_password_hash
from functools import wraps


from modules.Informante import GraficadorDeDiagramaCircular, GraficadorDePalabrasClave, InformantePDF, InformanteHTML

admin_datos = AdministradorDeDatos(db)


Jefes=['1','2','3']

with app.app_context():
    db.create_all()

@login_manager.user_loader
def user_loader(user_id):
    if user_id in Jefes:
        global graficador_diagrama
        global graficador_nube
        
        graficador_diagrama=GraficadorDeDiagramaCircular()
        graficador_nube=GraficadorDePalabrasClave()
        return db.session.get(JefeDepartamento, user_id)
    else:
        return db.session.get(UsuarioFinal, user_id)


#Decoradores para restringir accesos

def solo_jefes(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not isinstance(current_user,JefeDepartamento):
            return abort(403)
        return f(*args,**kwargs)
    return decorated_function


def solo_usuarios_finales(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not isinstance(current_user,UsuarioFinal):
            return abort(403)
        return f(*args,**kwargs)
    return decorated_function



#Rutas

@app.route("/")
def home(): 
    """Acá se inicia el programa"""
    if isinstance(current_user,UsuarioFinal):
        return render_template("InicioUsuarioFinal.html", usuario=current_user.nombre_usuario)
    elif isinstance(current_user,JefeDepartamento):
        return render_template ('InicioJefes.html')
    else:
        return render_template("PaginaInicial.html")





@app.route("/register", methods = ['GET','POST'])
def register():

    register_form=RegisterForm()
    
    if register_form.validate_on_submit():
        
        info = admin_datos.guardar_usuario(email = register_form.email.data, 
                                             nombre_usuario = register_form.nombre_usuario.data, 
                                             contraseña = register_form.contraseña.data, 
                                             Nombre = register_form.nombre.data, 
                                             Apellido = register_form.apellido.data, 
                                             claustro = register_form.claustro.data)

        
        if info=="Usuario registrado exitosamente, inicie sesión para ingresar":
            flash(info)
            return redirect(url_for("login"))
        else:
            flash(info)
            return render_template("register.html",form=register_form)
            #return render_template("register.html",form=register_form)
    else:
        return render_template("register.html",form=register_form)





@app.route("/login", methods=['GET', 'POST'])
def login():
   
    login_form=LoginForm()
    
    
    if login_form.validate_on_submit():
            
            usuario,funcion=admin_datos.cargar_usuario(nombre_usuario = login_form.nombre_usuario.data,
                                                       contraseña = login_form.contraseña.data)
            

            if funcion in ['inicio_Usuarios_Finales','inicio_jefes']:
                login_user(usuario)
                session['username']=usuario.nombre_usuario
                return redirect(url_for('home'))

            else:
                flash(funcion)
                return render_template("login.html", form=login_form)
            
    else:
        return render_template("login.html", form=login_form)
    
    


      
@app.route("/logout", methods=['GET','POST'])
def cerrar_sesion():
    logout_user()
    return redirect(url_for('home'))



#Solo UsuariosFinales


@app.route("/InicioUsuarioFinal", methods=['GET','POST'])
@solo_usuarios_finales
def inicio_Usuarios_Finales():
    return render_template("InicioUsuarioFinal.html", usuario=current_user.nombre_usuario)


@app.route("/crear_reclamo", methods=['GET','POST'])
@solo_usuarios_finales
def formulario_reclamo():
    
    #Cargar imagen si se ingresara
    form_reclamo = FormularioCrearReclamo()
    
    if form_reclamo.validate_on_submit():
            admin_datos.guardar_datos_reclamo(autor=current_user.nombre_usuario, 
                                              titulo=form_reclamo.titulo.data, 
                                              descripcion=form_reclamo.descripcion.data, 
                                              imagen=form_reclamo.imagen.data)
            
            return redirect(url_for('mostrar_reclamos_similares'))
    
    return render_template('crear_reclamo.html', form = form_reclamo)

    
@app.route("/seleccionar_reclamo_existente")
@solo_usuarios_finales
def mostrar_reclamos_similares():
    
    reclamos=admin_datos.buscar_reclamos_similares()

    return render_template('reclamos_similares.html', reclamos=reclamos)




@app.route("/confirmar_reclamo")
@solo_usuarios_finales
def crear_reclamo():

    admin_datos.crear_reclamo()
    flash("Reclamo creado con éxito")
    
    return redirect(url_for('home'))



@app.route("/reclamos", methods=['GET','POST'])
@solo_usuarios_finales
def mostrar_reclamos():
    return render_template('reclamos_usuario.html', reclamos=Reclamo.query.all(), usuario=current_user)


@app.route("/mis_reclamos", methods=['GET','POST'])
@solo_usuarios_finales
def mis_reclamos():
    return render_template('reclamos_usuario.html', reclamos=current_user.reclamos_seguidos, usuario=current_user)



@app.route("/adherir/<id>", methods=["GET"])
@solo_usuarios_finales
def adherir_a_reclamo(id):
    #reclamo=db.session.get(Reclamo, id)
    #reclamo=Reclamo.query.get(id)
    #current_user.reclamos_seguidos.append(reclamo)
    #flash("adherido a reclamo")
    admin_datos.adherir_usuario(current_user, id)
    return redirect(url_for("mis_reclamos"))



#Solo JefesDepartamentos


@app.route("/InicioJefe")
@solo_jefes
def inicio_jefes():
    return render_template('InicioJefes.html')


@app.route("/analytics")
@solo_jefes
def analitica():

    departamento = current_user.departamento
    graficador_diagrama.graficar(admin_datos, departamento, 'default', 'svg')
    graficador_nube.graficar(admin_datos, departamento, 'default', 'png')
    #informe_pdf=informante_pdf.generar_informe(current_user.departamento)
    return render_template('analitica.html')       #return render_template('analitica.html', informe_pdf=informe_pdf) retiro informe_pdf=informe_pdf



@app.route('/managecomplains')
@solo_jefes
def manejar_reclamos():
    if current_user.departamento=="secretaría técnica":
        reclamos=Reclamo.query.all()
        if len(reclamos)==0:
            flash("No tiene reclamos")
        return render_template("manejar_reclamos.html", reclamos=reclamos)
    else:
        reclamos=Reclamo.query.filter(Reclamo.__table__.c.departamento == current_user.departamento).all()
    if len(reclamos)==0:
            flash("No tiene reclamos")
    return render_template("manejar_reclamos.html", reclamos=reclamos)

@app.route('/help')
@solo_jefes
def ayuda():
    return render_template("ayuda.html")



@app.route("/editar/<id>", methods=["GET","POST"])
@solo_jefes
def editar(id):
    reclamo=Reclamo.query.get(id)

    if current_user.departamento=="secretaría técnica":

        form_editar=ParaSecretarioTecnico()
        if form_editar.validate_on_submit():

            reclamo.estado = form_editar.estado.data
            reclamo.departamento = form_editar.departamento.data
            db.session.commit()
            flash("reclamo editado con éxito")
            return redirect(url_for("manejar_reclamos"))
        
        return render_template("editar_reclamo.html", form=form_editar, reclamo=reclamo)
    
    else:
        form_editar=FormularioEditarReclamo()

        if form_editar.validate_on_submit():
            
            reclamo.estado = form_editar.estado.data
            db.session.commit()                             #cambiar estado del reclamo
            flash("reclamo editado con éxito")
            return redirect(url_for("manejar_reclamos"))
            
    return render_template("editar_reclamo.html", form=form_editar, reclamo=reclamo)


@app.route("/generar_informe/<formato>")
@solo_jefes
def generar_Informe(formato):
    if formato=="pdf":

        informante=InformantePDF(graficador_torta=graficador_diagrama, 
                                 graficador_nube=graficador_nube)
        
        
    else:    
        informante=InformanteHTML(graficador_torta=graficador_diagrama, 
                                  graficador_nube=graficador_nube)
        


    return informante.generar_informe(current_user.departamento, admin_datos)

    
    


@app.route("/estoEsReContraReMilSecretoNoVayanAEntrar")
def activar_jefes():
    secretario_tecnico = JefeDepartamento(email = 'secretariotecnico@email.com',
                                          nombre_usuario = 'Tecnico', 
                                          contraseña = generate_password_hash('12345678'), 
                                          Nombre = 'Secretario', 
                                          Apellido = 'Tecnico', 
                                          Departamento = "secretaría técnica")

    jefe_informatica = JefeDepartamento(email = 'informatico@email.com',
                                        nombre_usuario = 'Informatico', 
                                        contraseña = generate_password_hash('12345678'), 
                                        Nombre = 'Genio', 
                                        Apellido = 'Informatico', 
                                        Departamento = "soporte informático")

    jefe_maestranza = JefeDepartamento(email = 'maestranza@email.com',
                                       nombre_usuario = 'UltraCleaner', 
                                       contraseña = generate_password_hash('12345678'), 
                                       Nombre = 'Limpiador', 
                                       Apellido = 'Profesional', 
                                       Departamento = "maestranza")

    db.session.add(secretario_tecnico)
    db.session.add(jefe_informatica)
    db.session.add(jefe_maestranza)
    db.session.commit()

    return "jejeje"


@app.route('/test')
def prueba_graficador():
    graficador_diagrama=GraficadorDeDiagramaCircular()
    return graficador_diagrama.graficar('Maestranza')


if  __name__ == "__main__":
    app.run(debug=True)
    