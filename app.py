from flask import Flask, request, render_template, redirect, url_for, flash, session
import datetime
import pyodbc

app = Flask(__name__)

# SETTINGS
app.secret_key = "mysecretkey"

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-L44MSJ2;"
    "DATABASE=sistemas;"
    "UID=sa;"
    "PWD=1256"
)

mydb = pyodbc.connect(conn_str)

global alumno
alumno = None

@app.route('/')
def Index():
    publicaciones = consultarTodasPublicaciones()
    return render_template('index.html', publicaciones=publicaciones)

@app.route('/registro-publicacion')
def page_registro_publicacion():
    return render_template('registro-publicacion.html')

@app.route('/agregar-publicacion', methods=['POST'])
def agregar_publicacion():
    global alumno
    if request.method == 'POST':
        try:
            fecha = str(datetime.datetime.now())
            idAlumno = alumno[0]
            contenido = request.form['contenido']

            cursor = mydb.cursor()
            query = "INSERT INTO publicaciones (idAlumno, contenido, fecha) VALUES (?, ?, ?)"
            values = (idAlumno, contenido, fecha)
            cursor.execute(query, values)
            mydb.commit()
            cursor.close()

            flash("Se ha registrado de manera correcta!")
        except Exception as e:
            flash(f"Error al realizar el registro: {e}")
            return render_template('registro-publicacion.html')

    return render_template('registro-publicacion.html')

@app.route('/registro-usuario')
def registro_usuario():
    return render_template('registro-usuario.html')

@app.route('/agregar-usuario', methods=['POST', 'GET'])
def agregar_usuario():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            correo = request.form['correo']
            codigo = request.form['codigo']

            cursor = mydb.cursor()
            query = "INSERT INTO alumnos (nombre, apellido, correo, codigo) VALUES (?, ?, ?, ?)"
            values = (nombre, apellido, correo, codigo)
            cursor.execute(query, values)
            mydb.commit()
            cursor.close()

            flash('Usuario agregado de manera correcta: {}'.format(nombre))
        except Exception as e:
            flash("Error al realizar el registro: {}".format(e))
            return render_template('registro-usuario.html')

    return render_template('registro-usuario.html')

@app.route('/login-face')
def login_render():
    return render_template('loginFace.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    global alumno
    if request.method == 'POST':
        correo = request.form['correo']
        codigo = request.form['codigo']
        cursor = mydb.cursor()
        query = "SELECT * FROM alumnos WHERE correo = ? AND codigo = ?"
        values = (correo, codigo)
        cursor.execute(query, values)
        alumno = cursor.fetchone()
        cursor.close()

        if alumno:
            # Obtener la fecha y hora actual
            fecha = str(datetime.datetime.now())
            
            try:
                cursor = mydb.cursor()
                idAlumno = alumno[0]

                query = "INSERT INTO logs (idAlumno, fecha) VALUES (?, ?)"
                values = (idAlumno, fecha)
                cursor.execute(query, values)
                mydb.commit()
                cursor.close()

                session['logged_in'] = True
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f"Error al registrar Log: {e}")
        else:
            flash("Error de autenticación")

    return render_template('loginFace.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    global alumno
    alumno = None
    session.pop('logged_in', None)
    return redirect(url_for('Index'))

@app.route('/dashboard')
def dashboard():
    global alumno
    publicaciones = None
    sesiones = None
    if alumno != None:
        idAlumno = alumno[0]
        publicaciones = consultarPublicaciones(idAlumno=idAlumno)
        sesiones = consultarSesiones(idAlumno=idAlumno)
    return render_template('dashboard.html', alumno=alumno, publicaciones=publicaciones, sesiones=sesiones)

def consultarTodasPublicaciones():
    try:
        cursor = mydb.cursor()
        query = '''
            SELECT alumnos.nombre, alumnos.correo, publicaciones.contenido, publicaciones.fecha
            FROM alumnos
            JOIN publicaciones ON alumnos.idAlumno = publicaciones.idAlumno
        '''
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except Exception as e:
        flash(f"Error al consultar publicaciones: {e}")
        return None

def consultarPublicaciones(idAlumno):
    try:
        cursor = mydb.cursor()
        query = '''
            SELECT contenido, fecha
            FROM publicaciones WHERE idAlumno = ?
        '''
        values = (idAlumno,)
        cursor.execute(query, values)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except Exception as e:
        flash(f"Error al consultar publicaciones: {e}")
        return None

def consultarSesiones(idAlumno):
    try:
        cursor = mydb.cursor()
        query = '''
            SELECT idLog, fecha
            FROM logs WHERE idAlumno = ?
        '''
        values = (idAlumno,)
        cursor.execute(query, values)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except Exception as e:
        flash(f"Error al consultar sesiones: {e}")
        return None

def getAlumnos():
    try:

        cursor = mydb.cursor()
        cursor.execute("SELECT idAlumno,nombre,apellido,correo, codigo,imagen,imagenEncoding FROM alumnos")
        alumnos = cursor.fetchall()
        cursor.close()
        return alumnos
    except:
        return None        

if __name__ == '__main__':
    app.run(port=3000, debug=True)
