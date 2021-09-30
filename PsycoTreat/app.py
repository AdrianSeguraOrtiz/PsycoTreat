from flask import Flask, render_template, url_for, request, session, redirect
from flask_restful import reqparse, abort, Resource
from flask_pymongo import pymongo
import json
import base64
import datetime
import enfermedades
import formulario_aprox

CONNECTION_STRING_MY_DB = "mongodb+srv://adriansegura:adrianseguraortiz1999@psicotreatbd.e4kvw.mongodb.net/PsycoTreat?retryWrites=true&w=majority"
my_client = pymongo.MongoClient(CONNECTION_STRING_MY_DB)
my_db = my_client.get_database('PsycoTreat')
col_psiquiatras = pymongo.collection.Collection(my_db, 'psiquiatra')
col_pacientes = pymongo.collection.Collection(my_db, 'paciente')
col_administrativos = pymongo.collection.Collection(my_db, 'administrativo')
col_familiares = pymongo.collection.Collection(my_db, 'familiar autorizado')
col_formularios = pymongo.collection.Collection(my_db, 'formulario consulta')
col_mensajes = pymongo.collection.Collection(my_db, 'mensaje')
col_citas = pymongo.collection.Collection(my_db, 'cita')
col_enfermedades = pymongo.collection.Collection(my_db, 'enfermedad')
col_facturas = pymongo.collection.Collection(my_db, 'factura')

CONNECTION_STRING_GROUP_DB = "mongodb+srv://adriansegura:adrianseguraortiz1999@cluster0.k8hpd.mongodb.net/<Estandares>?retryWrites=true&w=majority"
group_client = pymongo.MongoClient(CONNECTION_STRING_GROUP_DB)
group_db = group_client.get_database("Estandares")
col_aplicaciones = pymongo.collection.Collection(group_db, "Aplicaciones")
col_usuarios = pymongo.collection.Collection(group_db, "Usuarios")

horarios = ['09:00-09:30', '09:30-10:00', '10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', '13:00-13:30', '13:30-14:00']

def EncriptarContraseña(contraseña):
    contraseña_encriptada = base64.b64encode(contraseña.encode("utf-8"))
    return (str(contraseña_encriptada).split("'")[1])

def IniciaSesion(nombre_app, usuario, contraseña): 
    # Compruebo que el usuario tenga acceso a la aplicación
    app = col_aplicaciones.find_one({"nombre" : nombre_app})
    app_usuarios = json.dumps(app["usuarios"])
    obj_usuario = json.dumps({'usuario': usuario})
    cond_1 = obj_usuario in app_usuarios
    # Verifico la contraseña
    if cond_1:
        user = col_usuarios.find_one({"_id" : usuario})
        cond_2 = user["contraseña"] == EncriptarContraseña(contraseña)
    else:
        cond_2 = False
    # Solo se permite el acceso si se cumplen ambos requisitos
    return cond_1 and cond_2

def DimePagina(usuario):
    pagina = None
    if 'psiquiatra' in usuario:
        pagina = '/psiquiatra/' + usuario + '/mis_pacientes'
    elif 'familiar' in usuario:
        pagina = '/familiar/' + usuario + '/mensajes'
    elif 'admin' in usuario:
        pagina = '/administrativo/' + usuario + '/registros'
    elif 'paciente' in usuario:
        pagina = '/paciente/' + usuario + '/citas'
    return pagina

def EncuentraMensajeroPorId (id):
    mensajero = None
    if 'psiquiatra' in id:
        mensajero = col_psiquiatras.find_one({"_id" : id})
    elif 'familiar' in id:
        mensajero = col_familiares.find_one({"_id" : id})
    elif 'admin' in id:
        mensajero = col_administrativos.find_one({"_id" : id})
    return mensajero

def EncuentraMensajerosPorId (mensajes, tipo):
    mensajeros = []
    for mensaje in mensajes:
        mensajeros.append(EncuentraMensajeroPorId(mensaje[tipo]))
    return mensajeros

def AñadirMensajeEnReceptor(id_receptor, id_mensaje):
    if 'familiar' in id_receptor:
        col_familiares.update_one({"_id" : id_receptor}, {"$push" : {"mensajes recibidos" : {"mensaje" : id_mensaje}}})
    elif 'admin' in id_receptor:
        col_administrativos.update_one({"_id" : id_receptor}, {"$push" : {"mensajes recibidos" : {"mensaje" : id_mensaje}}})

def lista_los_pacientes_citas(citas):
    res = {}
    for dia in citas:
        id_pacientes = list(dia.values())[3:]
        nom_pacientes = []
        for id_paciente in id_pacientes:
            paciente = col_pacientes.find_one({"_id" : id_paciente})
            nom_pacientes.append(paciente['nombre'] + ' ' + paciente['apellidos'])
        res[str(dia['fecha'])] = nom_pacientes
    return res

def buscaCitasAlPaciente(id_paciente, id_psiquiatra):
    res = []
    for dia in col_citas.find({"psiquiatra" : id_psiquiatra}):
        for k,v in dia.items():
            if (v == id_paciente):
                mi_cita = {"fecha" : dia['fecha'], "franja" : k}
                res.append(mi_cita)
    return res

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def pagina_principal():
    return render_template("home.html")

@app.route('/index')
def iniciar_sesion():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['username']
    contraseña = request.form['password']
    login_user = IniciaSesion("PsycoTreat", usuario, contraseña)

    if login_user:
        session['username'] = usuario 
        redireccion = DimePagina(usuario)  
        return redirect(redireccion)

    return 'Invalid username/password combination'



@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes')
def psiquiatra_mis_pacientes(id_psiquiatra):
    cursor_pacientes_nuevos = col_pacientes.find({"psiquiatra asignado" : id_psiquiatra, "patologia actual" : {"$exists": False}, "patologias previas" : {"$exists": False}})
    cursor_pacientes_actuales = col_pacientes.find({"psiquiatra asignado" : id_psiquiatra, "patologia actual" : {"$exists": True}})
    cursor_pacientes_antiguos = col_pacientes.find({"patologias previas" : { "$elemMatch" : {"psiquiatra asignado" : id_psiquiatra}}, "patologia actual" : {"$exists": False}})
    return render_template("psiquiatra/psiquiatra_pacientes.html.j2", pacientes_nuevos = cursor_pacientes_nuevos, pacientes_actuales = cursor_pacientes_actuales, pacientes_antiguos = cursor_pacientes_antiguos, id_psiquiatra = id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/ver/<id_paciente>')
def psiquiatra_mis_pacientes_ver(id_psiquiatra, id_paciente):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    return render_template("visualizaciones/visualización_paciente.html.j2", paciente = paciente, tipo_usuario = 'psiquiatra', id_psiquiatra = id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/tratar/<id_paciente>')
def psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    familiares = col_familiares.find({"paciente asociado" : id_paciente})
    administrativos = col_administrativos.find()
    return render_template("psiquiatra/psiquiatra_paciente_tratar.html.j2", paciente = paciente, familiares = familiares, administrativos = administrativos, id_psiquiatra = id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/finalizar/<id_paciente>')
def psiquiatra_mis_pacientes_finalizar(id_psiquiatra, id_paciente):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    patologia_actual = paciente['patologia actual']
    fecha_inicio = paciente['fecha inicio']
    fecha_final = datetime.date.today().strftime('%Y-%m-%d')
    psiquiatra_asignado = paciente['psiquiatra asignado']
    if 'formularios consultas' in paciente:
        formularios = paciente['formularios consultas']
    if 'medicamentos asignados' in paciente:
        medicamentos = paciente['medicamentos asignados']
    if 'pruebas complementarias' in paciente:
        pruebas = paciente['pruebas complementarias']
    col_pacientes.update_one({"_id" : id_paciente}, {"$unset" : {"patologia actual" : "", "fecha inicio" : "", "formularios consultas" : "",
    "medicamentos asignados" : "", "pruebas complementarias" : ""}, "$push" : {"patologias previas" : {"patologia" : patologia_actual, 
    "fecha inicio" : fecha_inicio, "fecha final" : fecha_final, "psiquiatra asignado" : psiquiatra_asignado}}})
    return psiquiatra_mis_pacientes(id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/empezar/<id_paciente>')
def psiquiatra_mis_pacientes_empezar(id_psiquiatra, id_paciente):
    fecha_inicio = datetime.date.today().strftime('%Y-%m-%d')
    col_pacientes.update_one({"_id" : id_paciente}, {"$set" : {"patologia actual" : "Sin especificar", "fecha inicio" : fecha_inicio}})
    return psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/anadir_consulta/<id_paciente>', methods = ['GET', 'POST'])
def psiquiatra_mis_pacientes_anadir_consulta(id_psiquiatra, id_paciente):
    if request.method == 'GET':
        return render_template("formularios/formulario_consulta.html.j2", id_psiquiatra = id_psiquiatra)
    elif request.method == 'POST':
        id_form = "g1_id_form_" + str(col_formularios.count() + 1).zfill(3)
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        motivo = request.form['motivo']
        desencadenante = request.form['desencadenante']
        observaciones = request.form['observaciones']
        diagnostico = request.form['diagnostico']
        tratamiento = request.form['tratamiento']
        frecuencia = request.form['frecuencia']
        aproximacion = formulario_aprox.damePorcentajes(motivo, desencadenante, observaciones, diagnostico)
        formulario = {"_id" : id_form, "psiquiatra" : id_psiquiatra, "paciente" : id_paciente, "fecha consulta" : fecha, 
        "motivo consulta" : motivo, "desencadenante" : desencadenante, "observaciones" : observaciones, "diagnostico" : diagnostico,
        "tratamiento" : tratamiento, "frecuencia tratamiento" : frecuencia, "aproximacion computacional" : aproximacion}
        col_formularios.insert_one(formulario)
        col_pacientes.update_one({"_id" : id_paciente}, {"$push" : {"formularios consultas" : {"formulario" : id_form}}})
        return psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/anadir_medicamento/<id_paciente>', methods = ['GET', 'POST'])
def psiquiatra_mis_pacientes_anadir_medicamento(id_psiquiatra, id_paciente):
    if request.method == 'GET':
        return render_template("formularios/formulario_medicamento.html.j2", id_psiquiatra = id_psiquiatra)
    elif request.method == 'POST':
        medicamento = request.form['medicamento']
        col_pacientes.update_one({"_id" : id_paciente}, {"$push" : {"medicamentos asignados" : {"medicamento": medicamento}}})
        return psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/anadir_prueba/<id_paciente>', methods = ['GET', 'POST'])
def psiquiatra_mis_pacientes_anadir_prueba(id_psiquiatra, id_paciente):
    if request.method == 'GET':
        return render_template("formularios/formulario_prueba.html.j2", id_psiquiatra = id_psiquiatra)
    elif request.method == 'POST':
        prueba = request.form['prueba']
        col_pacientes.update_one({"_id" : id_paciente}, {"$push" : {"pruebas complementarias" : {"prueba" : prueba}}})
        return psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/editar_patologia/<id_paciente>', methods = ['GET', 'POST'])
def psiquiatra_mis_pacientes_editar_patologia(id_psiquiatra, id_paciente):
    if request.method == 'GET':
        paciente = col_pacientes.find_one({"_id" : id_paciente})
        return render_template("formularios/formulario_patologia.html.j2", paciente = paciente, id_psiquiatra = id_psiquiatra)
    elif request.method == 'POST':
        patologia = request.form['patologia']
        paciente = col_pacientes.find_one({"_id" : id_paciente})
        if 'formularios consultas' in paciente:
            for formulario in paciente['formularios consultas']:
                if formulario['formulario'] in request.form:
                    col_pacientes.update_one({"_id" : id_paciente}, {"$pull" : {"formularios consultas" : {"formulario" : formulario['formulario']}}})
                    col_formularios.delete_one({"_id" : formulario['formulario']})
        if 'medicamentos asignados' in paciente:
            for medicamento in paciente['medicamentos asignados']:
                if medicamento['medicamento'] in request.form:
                    col_pacientes.update_one({"_id" : id_paciente}, {"$pull" : {"medicamentos asignados" : {"medicamento" : medicamento['medicamento']}}})
        if 'pruebas complementarias' in paciente:
            for prueba in paciente['pruebas complementarias']:
                if prueba['prueba'] in request.form:
                    col_pacientes.update_one({"_id" : id_paciente}, {"$pull" : {"pruebas complementarias" : {"prueba" : prueba['prueba']}}})
        return redirect('/psiquiatra/' + id_psiquiatra + '/mis_pacientes/editar_patologia/' + id_paciente + '/' + patologia)


@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/editar_patologia/<id_paciente>/<patologia>', methods = ['GET', 'POST'])
def psiquiatra_mis_pacientes_editar_patologia_codigo(id_psiquiatra, id_paciente, patologia):
    enfermedad_oficial = enfermedades.correction(patologia)
    if request.method == 'GET':
        if enfermedad_oficial == None:
            mensaje1 = "Todos los cambios han sido realizados excepto la asignación de la nueva patología"
            mensaje2 = "No se ha encontrado ninguna efermedad que se relacione con el término introducido"
            motivo = "error"
        else:
            mensaje1 = "Todos los cambios se han realizado correctamente"
            mensaje2 = "La patología ha sido reconocida como " + enfermedad_oficial + " a partir de la búsqueda aproximada de " + patologia
            motivo = "confirmación"
        return render_template("formularios/formulario_aproximacion.html.j2", id_psiquiatra = id_psiquiatra, m1 = mensaje1, m2 = mensaje2, motivo = motivo)
    elif request.method == 'POST':
        if request.form['opcion'] == 'Si':
            col_pacientes.update_one({"_id" : id_paciente}, {"$set" : {"patologia actual" : enfermedad_oficial}})
        return psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/consulta/ver/<id_consulta>')
def psiquiatra_mis_pacientes_ver_consulta(id_psiquiatra, id_consulta):
    consulta = col_formularios.find_one({"_id" : id_consulta})
    paciente = col_pacientes.find_one({"_id" : consulta['paciente']})
    psiquiatra = col_psiquiatras.find_one({"_id" : consulta['psiquiatra']})
    return render_template("visualizaciones/visualización_consulta.html.j2", consulta = consulta, paciente = paciente, psiquiatra = psiquiatra, id_psiquiatra = id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/mis_pacientes/tratar/<id_paciente>/enviar_mensaje/<id_receptor>', methods = ['GET', 'POST'])
def psiquiatra_mis_pacientes_enviar_mensaje(id_psiquiatra, id_paciente, id_receptor):
    if request.method == 'GET':
        posibles_receptores = {}
        return render_template("formularios/formulario_mensaje.html.j2", posibles_receptores = posibles_receptores, id_psiquiatra = id_psiquiatra, tipo_usuario = 'psiquiatra')
    if request.method == 'POST':
        id = "g1_id_mensaje_" + str(col_mensajes.count() + 1).zfill(3)
        emisor = id_psiquiatra
        receptor = id_receptor
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        contenido = request.form['contenido']
        mensaje = {"_id" : id, "emisor" : emisor, "receptor" : receptor, "fecha de envio" : fecha, "contenido" : contenido}
        col_mensajes.insert_one(mensaje)
        AñadirMensajeEnReceptor(id_receptor, id)
        return psiquiatra_mis_pacientes_tratar(id_psiquiatra, id_paciente)

@app.route('/psiquiatra/<id_psiquiatra>/citas')
def psiquiatra_citas(id_psiquiatra):
    citas = col_citas.find({"psiquiatra" : id_psiquiatra})
    d_pacientes = lista_los_pacientes_citas(col_citas.find({"psiquiatra" : id_psiquiatra}))
    return render_template("visualizaciones/visualización_citas.html.j2", id_psiquiatra = id_psiquiatra, citas = citas, pacientes = d_pacientes, tipo_usuario = 'psiquiatra')

@app.route('/psiquiatra/<id_psiquiatra>/citas/borrar/<id_cita>/<franja>')
def psiquiatra_citas_borrar(id_psiquiatra, id_cita, franja):
    col_citas.update_one({"_id" : id_cita}, {"$unset" : {franja : ""}})
    return psiquiatra_citas(id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/datos')
def psiquiatra_datos(id_psiquiatra):
    psiquiatra = col_psiquiatras.find_one({"_id" : id_psiquiatra})
    return render_template("visualizaciones/visualización_psiquiatra.html.j2", psiquiatra = psiquiatra, tipo_usuario = 'psiquiatra', id_psiquiatra = id_psiquiatra)

@app.route('/psiquiatra/<id_psiquiatra>/mensajes')
def psiquiatra_mensajes(id_psiquiatra):
    mensajes_enviados = list(col_mensajes.find({"emisor" : id_psiquiatra}))
    mensajes_recibidos = list(col_mensajes.find({"receptor" : id_psiquiatra}))
    receptores = EncuentraMensajerosPorId(mensajes_enviados, 'receptor')
    emisores = EncuentraMensajerosPorId(mensajes_recibidos, 'emisor')
    return render_template("mensajes.html.j2", tipo_usuario = 'psiquiatra', mensajes_enviados = mensajes_enviados, mensajes_recibidos = mensajes_recibidos, emisores = emisores, receptores = receptores, id_usuario = id_psiquiatra)

@app.route('/psiquiatra/<id_usuario>/mensajes/ver/<id_mensaje>')
def psiquiatra_mensajes_ver(id_usuario, id_mensaje):
    mensaje = col_mensajes.find_one({"_id" : id_mensaje})
    emisor = EncuentraMensajeroPorId(mensaje['emisor'])
    receptor = EncuentraMensajeroPorId(mensaje['receptor'])
    return render_template("visualizaciones/visualización_mensaje.html.j2", mensaje = mensaje, tipo_usuario = 'psiquiatra', emisor = emisor, receptor = receptor, id_psiquiatra = id_usuario)

@app.route('/psiquiatra/<id_emisor>/responder_mensaje/<id_receptor>', methods = ['GET', 'POST'])
def psiquiatra_responder_mensaje(id_emisor, id_receptor):
    if request.method == 'GET':
        posibles_receptores = {}
        return render_template("formularios/formulario_mensaje.html.j2", posibles_receptores = posibles_receptores, id_psiquiatra = id_emisor, tipo_usuario = 'psiquiatra')
    elif request.method == 'POST':
        id = "g1_id_mensaje_" + str(col_mensajes.count() + 1).zfill(3)
        emisor = id_emisor
        receptor = id_receptor
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        contenido = request.form['contenido']
        mensaje = {"_id" : id, "emisor" : emisor, "receptor" : receptor, "fecha de envio" : fecha, "contenido" : contenido}
        col_mensajes.insert_one(mensaje)
        AñadirMensajeEnReceptor(id_receptor, id)
        return psiquiatra_mensajes(id_emisor)

@app.route('/psiquiatra/<id_usuario>/eliminar_mensaje/<id_mensaje>')
def psiquiatra_eliminar_mensaje(id_usuario, id_mensaje):
    mensaje = col_mensajes.find_one({"_id" : id_mensaje})
    if mensaje['emisor'] == id_usuario:
        if 'familiar' in mensaje['receptor']:
            col_familiares.update_one({"_id" : mensaje['receptor']}, {"$pull" : {"mensajes recibidos" : {"mensaje" : id_mensaje}}})
        elif 'admin' in mensaje['receptor']:
            col_administrativos.update_one({"_id" : mensaje['receptor']}, {"$pull" : {"mensajes recibidos" : {"mensaje" : id_mensaje}}})
    col_mensajes.delete_one({"_id" : id_mensaje})
    return psiquiatra_mensajes(id_usuario)

@app.route('/psiquiatra/<id_usuario>/redactar_mensaje', methods = ['GET', 'POST'])
def psiquiatra_redactar_mensaje(id_usuario):
    if request.method == 'GET':
        administrativos = col_administrativos.find()
        familiares = col_familiares.find()
        posibles_receptores = list(administrativos) + list(familiares)
        return render_template("formularios/formulario_mensaje.html.j2", posibles_receptores = posibles_receptores, id_psiquiatra = id_usuario, tipo_usuario = 'psiquiatra')
    elif request.method == 'POST':
        id = "g1_id_mensaje_" + str(col_mensajes.count() + 1).zfill(3)
        emisor = id_usuario
        receptor = request.form['receptor']
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        contenido = request.form['contenido']
        mensaje = {"_id" : id, "emisor" : emisor, "receptor" : receptor, "fecha de envio" : fecha, "contenido" : contenido}
        col_mensajes.insert_one(mensaje)
        AñadirMensajeEnReceptor(receptor, id)
        return psiquiatra_mensajes(id_usuario)

@app.route('/paciente/<id_paciente>/citas')
def paciente_citas(id_paciente):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    citas = buscaCitasAlPaciente(id_paciente, paciente['psiquiatra asignado'])
    return render_template("paciente/paciente_citas.html.j2", tipo_usuario = 'paciente', id_paciente = id_paciente, citas = citas)

@app.route('/paciente/<id_paciente>/citas/borrar/<fecha>/<franja>')
def paciente_citas_borrar(id_paciente, fecha, franja):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    col_citas.update_one({"fecha" : fecha, "psiquiatra" : paciente['psiquiatra asignado']}, {"$unset" : {franja : ""}})
    return paciente_citas(id_paciente)

@app.route('/paciente/<id_paciente>/citas/anadir', methods = ['GET', 'POST'])
def paciente_citas_anadir(id_paciente):
    if request.method == 'GET':
        return render_template("formularios/formulario_citas_calendario.html.j2", tipo_usuario = 'paciente', id_paciente = id_paciente)
    elif request.method == 'POST':
        return redirect('/paciente/' + id_paciente +'/citas/anadir/' + request.form['fecha'])

@app.route('/paciente/<id_paciente>/citas/anadir/<fecha>',  methods = ['GET', 'POST'])
def paciente_citas_anadir_franjas(id_paciente, fecha):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    id_psiquiatra = paciente['psiquiatra asignado']
    if request.method == 'GET':
        citas_dia = col_citas.find_one({"fecha" : fecha, "psiquiatra" : id_psiquiatra})
        if citas_dia == None:
            id_cita = "g1_id_cita_" + str(col_citas.count() + 1).zfill(3)
            col_citas.insert_one({"_id" : id_cita, "psiquiatra" : id_psiquiatra, "fecha" : fecha})
            horarios_disponibles = horarios
        else:
            horarios_disponibles = list(set(horarios) - set(list(citas_dia.keys())[3:]))
            horarios_disponibles.sort()
        return render_template("formularios/formulario_citas_franjas.html.j2", tipo_usuario = 'paciente', id_paciente = id_paciente, horarios_disponibles = horarios_disponibles)
    elif request.method == 'POST':
        col_citas.update_one({"psiquiatra" : id_psiquiatra, "fecha" : fecha}, {"$set" : {request.form['opcion'] : id_paciente}})
        return paciente_citas(id_paciente)

@app.route('/paciente/<id_paciente>/datos')
def paciente_datos(id_paciente):
    paciente = col_pacientes.find_one({"_id" : id_paciente})
    return render_template("visualizaciones/visualización_paciente.html.j2", paciente = paciente, tipo_usuario = 'paciente', id_paciente = id_paciente)

@app.route('/paciente/<id_paciente>/facturas')
def paciente_facturas(id_paciente):
    facturas = col_facturas.find({"paciente" : id_paciente})
    return render_template("paciente/paciente_facturas.html.j2", tipo_usuario = 'paciente', id_paciente = id_paciente, facturas = facturas)

@app.route('/paciente/<id_paciente>/psiquiatras')
def paciente_psiquiatras(id_paciente):
    cursor_psiquiatras = col_psiquiatras.find()
    return render_template("paciente/paciente_psiquiatras.html.j2", psiquiatras = cursor_psiquiatras, id_paciente = id_paciente)

@app.route('/administrativo/<id_admin>/registros')
def admin_registros(id_admin):
    return render_template("administrativo/administrativo_registros.html", id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/pacientes')
def admin_registros_pacientes(id_admin):
    cursor_pacientes = col_pacientes.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_pacientes, tipo = 'pacientes', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/psiquiatras')
def admin_registros_psiquiatras(id_admin):
    cursor_psiquiatras = col_psiquiatras.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_psiquiatras, tipo = 'psiquiatras', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/familiares')
def admin_registros_familiares(id_admin):
    cursor_familiares = col_familiares.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_familiares, tipo = 'familiares autorizados', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/administrativos')
def admin_registros_administrativos(id_admin):
    cursor_administrativos = col_administrativos.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_administrativos, tipo = 'administrativos', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/familiar/ver/<id_usuario>')
def admin_registros_familiar_ver(id_admin, id_usuario):
    familiar = col_familiares.find_one({"_id" : id_usuario})
    paciente_asociado = col_pacientes.find_one({"_id" : familiar['paciente asociado']})
    return render_template('visualizaciones/visualización_familiar.html.j2', familiar = familiar, paciente_asociado = paciente_asociado, id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/familiar/anadir', methods = ['GET', 'POST'])
def admin_registros_familiar_anadir(id_admin):
    if request.method == 'GET':
        familiar = {}
        pacientes = col_pacientes.find()
        return render_template("formularios/formulario_familiar.html.j2", id_admin = id_admin, objetivo = 'añadir', familiar = familiar, pacientes = pacientes)
    elif request.method == 'POST':
        id = "g1_id_familiar_" + str(col_familiares.count() + 1).zfill(3)
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        paciente_asociado = request.form['paciente']
        relacion = request.form['relacion']
        nivel_auto = request.form['nivel autorizacion']
        familiar = {"_id" : id, "nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "paciente asociado" : paciente_asociado, "relacion" : relacion, 
        "nivel de autorizacion" : nivel_auto}
        col_familiares.insert_one(familiar)
        cursor_familiares = col_familiares.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_familiares, tipo = 'familiares autorizados', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/familiar/editar/<id_usuario>', methods = ['GET', 'POST'])
def admin_registros_familiar_editar(id_admin, id_usuario):
    if request.method == 'GET':
        familiar = col_familiares.find_one({"_id" : id_usuario})
        pacientes = col_pacientes.find()
        return render_template("formularios/formulario_familiar.html.j2", id_admin = id_admin, objetivo = 'editar', familiar = familiar, pacientes = pacientes)
    elif request.method == 'POST':   
        id = id_usuario
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        paciente_asociado = request.form['paciente']
        relacion = request.form['relacion']
        nivel_auto = request.form['nivel autorizacion']
        familiar = {"nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "paciente asociado" : paciente_asociado, "relacion" : relacion, 
        "nivel de autorizacion" : nivel_auto}
        col_familiares.update({"_id" : id}, {'$set' : familiar})
        cursor_familiares = col_familiares.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_familiares, tipo = 'familiares autorizados', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/familiar/borrar/<id_usuario>')
def admin_registros_familiar_borrar(id_admin, id_usuario):
    col_familiares.delete_one({"_id" : id_usuario})
    cursor_familiares = col_familiares.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_familiares, tipo = 'familiares autorizados', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/paciente/ver/<id_usuario>')
def admin_registros_paciente_ver(id_admin, id_usuario):
    paciente = col_pacientes.find_one({"_id" : id_usuario})
    psiquiatra = col_psiquiatras.find_one({"_id" : paciente['psiquiatra asignado']})
    paciente['nombre apellidos psiquiatra'] = psiquiatra['nombre'] + ' ' + psiquiatra['apellidos']
    return render_template("visualizaciones/visualización_paciente.html.j2", paciente = paciente, tipo_usuario = 'administrativo', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/paciente/anadir', methods = ['GET', 'POST'])
def admin_registros_paciente_anadir(id_admin):
    if request.method == 'GET':
        paciente = {}
        psiquiatras = col_psiquiatras.find()
        return render_template("formularios/formulario_paciente.html.j2", id_admin = id_admin, objetivo = 'añadir', paciente = paciente, psiquiatras = psiquiatras)
    elif request.method == 'POST':
        id = "g1_id_paciente_" + str(col_pacientes.count() + 1).zfill(3)
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        psiquiatra_asignado = request.form['psiquiatra']
        paciente = {"_id" : id, "nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "psiquiatra asignado" : psiquiatra_asignado}
        col_pacientes.insert_one(paciente)
        cursor_pacientes = col_pacientes.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_pacientes, tipo = 'pacientes', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/paciente/editar/<id_usuario>', methods = ['GET', 'POST'])
def admin_registros_paciente_editar(id_admin, id_usuario):
    if request.method == 'GET':
        paciente = col_pacientes.find_one({"_id" : id_usuario})
        psiquiatras = col_psiquiatras.find()
        return render_template("formularios/formulario_paciente.html.j2", id_admin = id_admin, objetivo = 'editar', paciente = paciente, psiquiatras = psiquiatras)
    elif request.method == 'POST':   
        id = id_usuario
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        psiquiatra_asignado = request.form['psiquiatra']
        paciente = {"nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "psiquiatra asignado" : psiquiatra_asignado}
        col_pacientes.update({"_id" : id}, {'$set' : paciente})
        cursor_pacientes = col_pacientes.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_pacientes, tipo = 'pacientes', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/paciente/borrar/<id_usuario>')
def admin_registros_paciente_borrar(id_admin, id_usuario):
    col_pacientes.delete_one({"_id" : id_usuario})
    col_familiares.delete({"paciente asociado" : id_usuario})
    col_formularios.delete({"paciente" : id_usuario})
    cursor_pacientes = col_pacientes.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_pacientes, tipo = 'pacientes', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/psiquiatra/ver/<id_usuario>')
def admin_registros_psiquiatra_ver(id_admin, id_usuario):
    psiquiatra = col_psiquiatras.find_one({"_id" : id_usuario})
    return render_template("visualizaciones/visualización_psiquiatra.html.j2", psiquiatra = psiquiatra, tipo_usuario = 'administrativo', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/psiquiatra/anadir', methods = ['GET', 'POST'])
def admin_registros_psiquiatra_anadir(id_admin):
    if request.method == 'GET':
        psiquiatra = {}
        return render_template("formularios/formulario_psiquiatra.html.j2", id_admin = id_admin, objetivo = 'añadir', psiquiatra = psiquiatra)
    elif request.method == 'POST':
        id = "g1_id_psiquiatra_" + str(col_psiquiatras.count() + 1).zfill(3)
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        titulacion = request.form['titulacion']
        universidad = request.form['universidad']
        especialidad = request.form['especialidad']
        psiquiatra = {"_id" : id, "nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "titulacion" : titulacion, "universidad" : universidad, "especialidad" : especialidad, 
        "años antiguedad en centro" : 0, "numero de pacientes" : 0}
        col_psiquiatras.insert_one(psiquiatra)
        cursor_psiquiatras = col_psiquiatras.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_psiquiatras, tipo = 'psiquiatras', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/psiquiatra/editar/<id_usuario>', methods = ['GET', 'POST'])
def admin_registros_psiquiatra_editar(id_admin, id_usuario):
    if request.method == 'GET':
        psiquiatra = col_psiquiatras.find_one({"_id" : id_usuario})
        return render_template("formularios/formulario_psiquiatra.html.j2", id_admin = id_admin, objetivo = 'editar', psiquiatra = psiquiatra)
    elif request.method == 'POST':   
        id = id_usuario
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        titulacion = request.form['titulacion']
        universidad = request.form['universidad']
        especialidad = request.form['especialidad']
        años_antiguedad = request.form['años antiguedad']
        num_pacientes = request.form['numero pacientes']
        psiquiatra = {"nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "titulacion" : titulacion, "universidad" : universidad, "especialidad" : especialidad, 
        "años antiguedad en centro" : años_antiguedad, "numero de pacientes" : num_pacientes}
        col_psiquiatras.update({"_id" : id}, {'$set' : psiquiatra})
        cursor_psiquiatras = col_psiquiatras.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_psiquiatras, tipo = 'psiquiatras', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/psiquiatra/borrar/<id_usuario>')
def admin_registros_psiquiatra_borrar(id_admin, id_usuario):
    col_psiquiatras.delete_one({"_id" : id_usuario})
    cursor_psiquiatras = col_psiquiatras.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_psiquiatras, tipo = 'psiquiatras', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/administrativo/ver/<id_usuario>')
def admin_registros_administrativo_ver(id_admin, id_usuario):
    administrativo = col_administrativos.find_one({"_id" : id_usuario})
    return render_template("visualizaciones/visualización_administrativo.html.j2", administrativo = administrativo, tipo_usuario = 'administrativo', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/administrativo/anadir', methods = ['GET', 'POST'])
def admin_registros_administrativo_anadir(id_admin):
    if request.method == 'GET':
        administrativo = {}
        return render_template("formularios/formulario_administrativo.html.j2", id_admin = id_admin, objetivo = 'añadir', administrativo = administrativo)
    elif request.method == 'POST':
        id = "g1_id_administrativo_" + str(col_administrativos.count() + 1).zfill(3)
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        titulacion = request.form['titulacion']
        administrativo = {"_id" : id, "nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "titulacion" : titulacion, "años antiguedad en centro" : 0}
        col_administrativos.insert_one(administrativo)
        cursor_administrativos = col_administrativos.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_administrativos, tipo = 'administrativos', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/administrativo/editar/<id_usuario>', methods = ['GET', 'POST'])
def admin_registros_administrativo_editar(id_admin, id_usuario):
    if request.method == 'GET':
        administrativo = col_administrativos.find_one({"_id" : id_usuario})
        return render_template("formularios/formulario_administrativo.html.j2", id_admin = id_admin, objetivo = 'editar', administrativo = administrativo)
    elif request.method == 'POST':   
        id = id_usuario
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        fecha_nacimiento = request.form['fecha de nacimiento']
        sexo = request.form['sexo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        codigo_postal = request.form['codigo postal']
        localidad = request.form['localidad']
        provincia = request.form['provincia']
        archivo = request.form['archivo']
        titulacion = request.form['titulacion']
        administrativo = {"_id" : id, "nombre" : nombre, "apellidos" : apellidos, "dni" : dni, "fecha_de_nacimiento" : fecha_nacimiento,
        "sexo" : sexo, "email" : email, "telefono" : telefono, "direccion" : direccion, "codigo postal" : codigo_postal, "localidad" : localidad,
        "provincia" : provincia, "fotografia" : archivo, "titulacion" : titulacion, "años antiguedad en centro" : 0}
        col_administrativos.update({"_id" : id}, {'$set' : administrativo})
        cursor_administrativos = col_administrativos.find()
        return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_administrativos, tipo = 'administrativos', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/registros/administrativo/borrar/<id_usuario>')
def admin_registros_administrativo_borrar(id_admin, id_usuario):
    col_administrativos.delete_one({"_id" : id_usuario})
    cursor_administrativos = col_administrativos.find()
    return render_template("administrativo/administrativo_registros_usuarios.html.j2", usuarios = cursor_administrativos, tipo = 'administrativos', id_admin = id_admin)

@app.route('/administrativo/<id_admin>/citas')
def admin_citas(id_admin):
    return render_template("administrativo/administrativo_citas.html.j2", id_admin = id_admin, psiquiatras = col_psiquiatras.find())

@app.route('/administrativo/<id_admin>/citas/ver/<id_psiquiatra>')
def admin_citas_ver(id_admin, id_psiquiatra):
    citas = col_citas.find({"psiquiatra" : id_psiquiatra})
    d_pacientes = lista_los_pacientes_citas(col_citas.find({"psiquiatra" : id_psiquiatra}))
    return render_template("visualizaciones/visualización_citas.html.j2", id_admin = id_admin, citas = citas, pacientes = d_pacientes, tipo_usuario = 'administrativo')

@app.route('/administrativo/<id_admin>/citas/borrar/<id_psiquiatra>/<id_cita>/<franja>')
def admin_citas_borrar(id_admin, id_psiquiatra, id_cita, franja):
    col_citas.update_one({"_id" : id_cita}, {"$unset" : {franja : ""}})
    return admin_citas_ver(id_admin, id_psiquiatra)

@app.route('/administrativo/<id_admin>/citas/anadir/<id_psiquiatra>',  methods = ['GET', 'POST'])
def admin_citas_anadir(id_admin, id_psiquiatra):
    if request.method == 'GET':
        return render_template("formularios/formulario_citas_calendario.html.j2", tipo_usuario = 'administrativo', id_admin = id_admin)
    elif request.method == 'POST':
        return redirect('/administrativo/'+ id_admin +'/citas/anadir/' + id_psiquiatra + '/' + request.form['fecha'])

@app.route('/administrativo/<id_admin>/citas/anadir/<id_psiquiatra>/<fecha>',  methods = ['GET', 'POST'])
def admin_citas_anadir_franjas(id_admin, id_psiquiatra, fecha):
    if request.method == 'GET':
        citas_dia = col_citas.find_one({"fecha" : fecha, "psiquiatra" : id_psiquiatra})
        if citas_dia == None:
            id_cita = "g1_id_cita_" + str(col_citas.count() + 1).zfill(3)
            col_citas.insert_one({"_id" : id_cita, "psiquiatra" : id_psiquiatra, "fecha" : fecha})
            horarios_disponibles = horarios
        else:
            horarios_disponibles = list(set(horarios) - set(list(citas_dia.keys())[3:]))
            horarios_disponibles.sort()
        return render_template("formularios/formulario_citas_franjas.html.j2", id_admin = id_admin, tipo_usuario = 'administrativo', horarios_disponibles = horarios_disponibles)
    elif request.method == 'POST':
        return redirect('/administrativo/'+ id_admin +'/citas/anadir/' + id_psiquiatra + '/' + fecha + '/' + request.form['opcion'])

@app.route('/administrativo/<id_admin>/citas/anadir/<id_psiquiatra>/<fecha>/<franja>',  methods = ['GET', 'POST'])
def admin_citas_anadir_paciente(id_admin, id_psiquiatra, fecha, franja):
    if request.method == 'GET':
        return render_template("formularios/formulario_citas_paciente.html.j2", id_admin = id_admin, pacientes = col_pacientes.find({"psiquiatra asignado" : id_psiquiatra}))
    elif request.method == 'POST':
        col_citas.update_one({"psiquiatra" : id_psiquiatra, "fecha" : fecha}, {"$set" : {franja : request.form['paciente']}})
        return admin_citas(id_admin)

@app.route('/administrativo/<id_admin>/facturas')
def admin_facturas(id_admin):
    facturas = col_facturas.find()
    pacientes = {}
    for factura in col_facturas.find():
        paciente = col_pacientes.find_one({"_id" : factura['paciente']})
        pacientes[factura['paciente']] = paciente['nombre'] + ' ' + paciente['apellidos']
    return render_template("administrativo/administrativo_facturas.html.j2", id_admin = id_admin, facturas = facturas, pacientes = pacientes)

@app.route('/administrativo/<id_admin>/facturas/borrar/<id_factura>')
def admin_facturas_borrar(id_admin, id_factura):
    col_facturas.delete_one({"_id" : id_factura})
    return admin_facturas(id_admin)

@app.route('/administrativo/<id_admin>/facturas/anadir', methods = ['GET', 'POST'])
def admin_facturas_anadir(id_admin):
    if request.method == 'GET':
        pacientes = col_pacientes.find()
        return render_template("formularios/formulario_facturas.html.j2", id_admin = id_admin, pacientes = pacientes)
    elif request.method == 'POST':
        id_fact = "g1_id_factura_" + str(col_facturas.count() + 1).zfill(3)
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        paciente = request.form['paciente']
        archivo = request.form['archivo']
        archivo = 'pdf/' + archivo
        factura = {"_id" : id_fact, "fecha" : fecha, "paciente" : paciente, "archivo" : archivo}
        col_facturas.insert_one(factura)
        return admin_facturas(id_admin)

@app.route('/administrativo/<id_admin>/mensajes')
def admin_mensajes(id_admin):
    mensajes_enviados = list(col_mensajes.find({"emisor" : id_admin}))
    mensajes_recibidos = list(col_mensajes.find({"receptor" : id_admin}))
    receptores = EncuentraMensajerosPorId(mensajes_enviados, 'receptor')
    emisores = EncuentraMensajerosPorId(mensajes_recibidos, 'emisor')
    return render_template("mensajes.html.j2", tipo_usuario = 'administrativo', mensajes_enviados = mensajes_enviados, mensajes_recibidos = mensajes_recibidos, emisores = emisores, receptores = receptores, id_usuario = id_admin)

@app.route('/administrativo/<id_usuario>/mensajes/ver/<id_mensaje>')
def admin_mensajes_ver(id_usuario, id_mensaje):
    mensaje = col_mensajes.find_one({"_id" : id_mensaje})
    emisor = EncuentraMensajeroPorId(mensaje['emisor'])
    receptor = EncuentraMensajeroPorId(mensaje['receptor'])
    return render_template("visualizaciones/visualización_mensaje.html.j2", mensaje = mensaje, tipo_usuario = 'administrativo', emisor = emisor, receptor = receptor, id_admin = id_usuario)

@app.route('/administrativo/<id_emisor>/responder_mensaje/<id_receptor>', methods = ['GET', 'POST'])
def admin_responder_mensaje(id_emisor, id_receptor):
    if request.method == 'GET':
        posibles_receptores = {}
        return render_template("formularios/formulario_mensaje.html.j2", posibles_receptores = posibles_receptores, id_admin = id_emisor, tipo_usuario = 'administrativo')
    elif request.method == 'POST':
        id = "g1_id_mensaje_" + str(col_mensajes.count() + 1).zfill(3)
        emisor = id_emisor
        receptor = id_receptor
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        contenido = request.form['contenido']
        mensaje = {"_id" : id, "emisor" : emisor, "receptor" : receptor, "fecha de envio" : fecha, "contenido" : contenido}
        col_mensajes.insert_one(mensaje)
        return admin_mensajes(id_emisor)

@app.route('/administrativo/<id_usuario>/eliminar_mensaje/<id_mensaje>')
def admin_eliminar_mensaje(id_usuario, id_mensaje):
    mensaje = col_mensajes.find_one({"_id" : id_mensaje})
    if mensaje['receptor'] == id_usuario:
        col_administrativos.update_one({"_id" : id_usuario}, {"$pull" : {"mensajes recibidos" : {"mensaje" : id_mensaje}}})
    col_mensajes.delete_one({"_id" : id_mensaje})
    return admin_mensajes(id_usuario)

@app.route('/administrativo/<id_usuario>/redactar_mensaje', methods = ['GET', 'POST'])
def admin_redactar_mensaje(id_usuario):
    if request.method == 'GET':
        posibles_receptores = col_psiquiatras.find()
        return render_template("formularios/formulario_mensaje.html.j2", posibles_receptores = posibles_receptores, id_admin = id_usuario, tipo_usuario = 'administrativo')
    elif request.method == 'POST':
        id = "g1_id_mensaje_" + str(col_mensajes.count() + 1).zfill(3)
        emisor = id_usuario
        receptor = request.form['receptor']
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        contenido = request.form['contenido']
        mensaje = {"_id" : id, "emisor" : emisor, "receptor" : receptor, "fecha de envio" : fecha, "contenido" : contenido}
        col_mensajes.insert_one(mensaje)
        return admin_mensajes(id_usuario)


@app.route('/familiar/<id_familiar>/citas')
def familiar_citas(id_familiar):
    familiar = col_familiares.find_one({"_id" : id_familiar})
    if familiar['nivel de autorizacion'] == 'Total':
        paciente = col_pacientes.find_one({"_id" : familiar['paciente asociado']})
        citas = buscaCitasAlPaciente(paciente['_id'], paciente['psiquiatra asignado'])
        return render_template("paciente/paciente_citas.html.j2", tipo_usuario = 'familiar', id_familiar = id_familiar, citas = citas)
    else:
        return render_template("familiar/familiar_citas.html", id_familiar = id_familiar)

@app.route('/familiar/<id_familiar>/citas/borrar/<fecha>/<franja>')
def familiar_citas_borrar(id_familiar, fecha, franja):
    familiar = col_familiares.find_one({"_id" : id_familiar})
    paciente = col_pacientes.find_one({"_id" : familiar['paciente asociado']})
    col_citas.update_one({"fecha" : fecha, "psiquiatra" : paciente['psiquiatra asignado']}, {"$unset" : {franja : ""}})
    return familiar_citas(id_familiar)

@app.route('/familiar/<id_familiar>/citas/anadir', methods = ['GET', 'POST'])
def familiar_citas_anadir(id_familiar):
    if request.method == 'GET':
        return render_template("formularios/formulario_citas_calendario.html.j2", tipo_usuario = 'familiar', id_familiar = id_familiar)
    elif request.method == 'POST':
        return redirect('/familiar/' + id_familiar +'/citas/anadir/' + request.form['fecha'])

@app.route('/familiar/<id_familiar>/citas/anadir/<fecha>',  methods = ['GET', 'POST'])
def familiar_citas_anadir_franjas(id_familiar, fecha):
    familiar = col_familiares.find_one({"_id" : id_familiar})
    paciente = col_pacientes.find_one({"_id" : familiar['paciente asociado']})
    id_psiquiatra = paciente['psiquiatra asignado']
    if request.method == 'GET':
        citas_dia = col_citas.find_one({"fecha" : fecha, "psiquiatra" : id_psiquiatra})
        if citas_dia == None:
            id_cita = "g1_id_cita_" + str(col_citas.count() + 1).zfill(3)
            col_citas.insert_one({"_id" : id_cita, "psiquiatra" : id_psiquiatra, "fecha" : fecha})
            horarios_disponibles = horarios
        else:
            horarios_disponibles = list(set(horarios) - set(list(citas_dia.keys())[3:]))
            horarios_disponibles.sort()
        return render_template("formularios/formulario_citas_franjas.html.j2", tipo_usuario = 'familiar', id_familiar = id_familiar, horarios_disponibles = horarios_disponibles)
    elif request.method == 'POST':
        col_citas.update_one({"psiquiatra" : id_psiquiatra, "fecha" : fecha}, {"$set" : {request.form['opcion'] : paciente['_id']}})
        return familiar_citas(id_familiar)

@app.route('/familiar/<id_familiar>/facturas')
def familiar_facturas(id_familiar):
    familiar = col_familiares.find_one({"_id" : id_familiar})
    if familiar['nivel de autorizacion'] == 'Parcial' or familiar['nivel de autorizacion'] == 'Total':
        facturas = col_facturas.find({"paciente" : familiar['paciente asociado']})
        return render_template("paciente/paciente_facturas.html.j2", tipo_usuario = 'familiar', id_familiar = id_familiar, facturas = facturas)
    else:
        return render_template("familiar/familiar_facturas.html", id_familiar = id_familiar)

@app.route('/familiar/<id_familiar>/mensajes')
def familiar_mensajes(id_familiar):
    mensajes_recibidos = list(col_mensajes.find({"receptor" : id_familiar}))
    emisores = EncuentraMensajerosPorId(mensajes_recibidos, 'emisor')
    receptores = []
    mensajes_enviados = {}
    return render_template("mensajes.html.j2", tipo_usuario = 'familiar', mensajes_enviados = mensajes_enviados, mensajes_recibidos = mensajes_recibidos, emisores = emisores, receptores = receptores, id_usuario = id_familiar)

@app.route('/familiar/<id_usuario>/mensajes/ver/<id_mensaje>')
def familiar_mensajes_ver(id_usuario, id_mensaje):
    mensaje = col_mensajes.find_one({"_id" : id_mensaje})
    emisor = EncuentraMensajeroPorId(mensaje['emisor'])
    receptor = EncuentraMensajeroPorId(mensaje['receptor'])
    return render_template("visualizaciones/visualización_mensaje.html.j2", mensaje = mensaje, tipo_usuario = 'familiar', emisor = emisor, receptor = receptor, id_familiar = id_usuario)


if __name__ == '__main__':
    app.run(debug=True)