import mysql.connector
from rapidfuzz import process, fuzz
import logging
import os

# Configure logging
logging.basicConfig(level=logging.ERROR)

ID = 'id'

CATALOGO_COORDINACIONES = 'catalogo_coordinaciones'
COORDINACION_FIELD = 'coordinacion'

CATALOGO_PROGRAMAS = 'catalogo_programas'
PROGRAMA_FIELD = 'programa'

CATALOGO_ROLES_TESIS = 'catalogo_roles_tesis'
ROL_TESIS_FIELD = 'rol_tesis'

CATALOGO_TESIS = 'tesis'
TITULO_FIELD = 'titulo'

CATALOGO_MAESTROS = 'maestros'
LABEL = 'label'

SCORER = fuzz.token_set_ratio

class Matcher:
    def __init__(self, host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"), user=os.getenv("DB_USERNAME"), password=os.getenv("DB_PASSWORD")):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        # Load catalogs on initialization.
        self.catalogos = self.get_catalogos()

    def get_catalogos(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            cursor = connection.cursor(dictionary=True)
            try:
                # Retrieve each catalog as a dictionary mapping IDs to the field values.
                catalogo_coordinaciones = { d[ID]: d[COORDINACION_FIELD] for d in self.get_catalogo(CATALOGO_COORDINACIONES, cursor) }
                catalogo_programas = { d[ID]: d[PROGRAMA_FIELD] for d in self.get_catalogo(CATALOGO_PROGRAMAS, cursor) }
                catalogo_roles_tesis = { d[ID]: d[ROL_TESIS_FIELD] for d in self.get_catalogo(CATALOGO_ROLES_TESIS, cursor) }
                catalogo_tesis = { d[ID]: d[TITULO_FIELD] for d in self.get_catalogo(CATALOGO_TESIS, cursor) }
                catalogo_maestros = { d[ID]: d[LABEL] for d in self.get_catalogo_maestros(cursor) }

                return {
                    'catalogo_coordinaciones': catalogo_coordinaciones,
                    'catalogo_programas': catalogo_programas,
                    'catalogo_roles_tesis': catalogo_roles_tesis,
                    'catalogo_maestros': catalogo_maestros,
                    'catalogo_tesis': catalogo_tesis
                }
            finally:
                # Ensure resources are closed.
                cursor.close()
                connection.close()
        except mysql.connector.Error as err:
            logging.error(f"Error connecting to database: {err}")
            return None

    def get_catalogo(self, table, cursor):
        query = f"SELECT * FROM {table}"
        cursor.execute(query)
        return cursor.fetchall()
    
    def get_catalogo_maestros(self, cursor):
        query = "SELECT id, CONCAT_WS(' ', grado, nombre, apellido) AS label FROM maestros"
        cursor.execute(query)
        return cursor.fetchall()

    def match_coordinacion(self, text):
        if text is None or self.catalogos is None:
            return None
        result = process.extract(
            text,
            self.catalogos['catalogo_coordinaciones'],
            scorer=SCORER,
            limit=1
        )
        if result:
            return result[0][2]
            # return {
            #     'id': result[0][2],
            #     'coordinacion': result[0][0]
            # }
        return None

    def match_programa(self, text):
        if text is None or self.catalogos is None:
            return None
        result = process.extract(
            text,
            self.catalogos['catalogo_programas'],
            scorer=SCORER,
            limit=1
        )
        if result:
            return result[0][2]
            # return {
            #     'id': result[0][2],
            #     'grado': result[0][0]
            # }
        return None
    

    def match_maestro(self, text):
        if text is None or self.catalogos is None:
            return None
        result = process.extract(
            text,
            self.catalogos['catalogo_maestros'],
            scorer=SCORER,
            limit=1
        )
        if result:
            return result[0][2]
        

    def match_tesis(self, text):
        if text is None or self.catalogos is None:
            return None
        result = process.extract(
            text,
            self.catalogos['catalogo_tesis'],
            scorer=SCORER,
            limit=1
        )
        if result:
            return result[0][2]

    def match_rol_tesis(self, text):
        if text is None or self.catalogos is None:
            return None
        if 'codirector' in text or 'co-director' in text:
            return 2
        elif 'director' in text:
            return 1
        else:
            return 3

    def match_pronace(self, id_pronace):
        if id_pronace is None:
            return None
        #Estas estan hardcodeadas porque con estos valores se entreno el modelo,
        #hay que tener cuidado en caso de que por algun motivo cambien los ids
        #del catalogo en la base de datos, deben ser estos o se debe reentrenar el
        #modelo de clasificacion
        pronaces_list = [
            {'id': 1, 'pronace': 'Agentes Tóxicos y Procesos Contaminantes' },
            {'id': 2, 'pronace': 'Agua' },
            {'id': 3, 'pronace': 'Cultura' },
            {'id': 4, 'pronace': 'Educación' },
            {'id': 5, 'pronace': 'Energía y Cambio Climático' },
            {'id': 6, 'pronace': 'Salud' },
            {'id': 7, 'pronace': 'Seguridad Humana' },
            {'id': 8, 'pronace': 'Sistemas Socio-Ecológicos' },
            {'id': 9, 'pronace': 'Soberanía Alimentaria' },
            {'id': 10, 'pronace': 'Vivienda' },
            {'id': 11, 'pronace': 'Otro' },
            {'id': 12, 'pronace': 'Economía' },
            {'id': 13, 'pronace': 'Materiales' },
        ]
        for pronace in pronaces_list:
            if pronace['id'] == id_pronace:
                return pronace
        return None

    def match_fecha(self, fecha):
        if fecha is None:
            return None
        
        if 'enero' in fecha:
            mes = '01'
        elif 'febrero' in fecha:
            mes = '02'
        elif 'marzo' in fecha:
            mes = '03'
        elif 'abril' in fecha:
            mes = '04'
        elif 'mayo' in fecha:
            mes = '05'
        elif 'junio' in fecha:
            mes = '06'
        elif 'julio' in fecha:
            mes = '07'
        elif 'agosto' in fecha:
            mes = '08'
        elif 'septiembre' in fecha:
            mes = '09'
        elif 'octubre' in fecha:
            mes = '10'
        elif 'noviembre' in fecha:
            mes = '11'
        elif 'diciembre' in fecha:
            mes = '12'
        else:
            return None
        
        for year in range(1980, 2050):
            if str(year) in fecha:
                return f"{year}-{mes}-01"
        return None

    def match_comite(self, comite):
        if comite is None or self.catalogos is None:
            return None
        miembros_comite = []
        for miembro in comite:
            id_maestro = self.match_maestro(miembro)
            id_rol = self.match_rol_tesis(miembro)
            miembros_comite.append({
                'id_rol': id_rol,
                'id_maestro': id_maestro
            })
        return miembros_comite
