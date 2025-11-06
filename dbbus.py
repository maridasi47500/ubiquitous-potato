import sqlite3
import json
def clean_and_parse_json(text):
    try:
        #cleaned = text.replace("'", '"').replace('\\\"', "'")
        cleaned = str(json.dumps(text))
        return (cleaned)
    except json.JSONDecodeError:
        return []


DB_PATH = "bus.db"
def nettoyer_json_embedded(data, max_depth=5):
    """Essaie de décoder un JSON encodé plusieurs fois."""
    for _ in range(max_depth):
        if isinstance(data, list):
            return data
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            break
    return data if isinstance(data, list) else []


def get_connection():
    return sqlite3.connect(DB_PATH)



def get_all_bus():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bus")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_bus_by_id(bus_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bus WHERE id = ?", (bus_id,))
    row = cursor.fetchone()
    hey =  (
            row[0],
            row[1],

             row[2],
             row[3],
             row[4],
             row[5],
clean_and_parse_json(nettoyer_json_embedded(row[6])), 
clean_and_parse_json(nettoyer_json_embedded(row[7])), 

             row[8],
            row[9],
            row[10],
clean_and_parse_json(nettoyer_json_embedded(row[11]))
       ) 

    conn.close()
    return hey

def save_bus(theme, nom, musique, lumiere_dedans, lumiere_dehors, directions, motivations,
                nombre_max_tours, duree_phase, nbmintours,popstar, bus_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if bus_id:
        cursor.execute("""
            UPDATE bus SET theme=?, nom=?, musique=?, lumiere_dedans=?, lumiere_dehors, directions=?, motivations=?,
            nombre_max_tours=?, duree_phase=?, nbmintours=?, popstar=? WHERE id=?
        """, (
            theme, nom, musique, lumiere_dedans, lumiere_dehors,
            (directions),
            (motivations),
            nombre_max_tours, duree_phase, nbmintours, (popstar), bus_id
        ))
    else:
        cursor.execute("""
            INSERT INTO bus (theme, nom, musique, lumiere_dedans, lumiere_dehors, directions, motivations,
            nombre_max_tours, duree_phase, nbmintours, popstar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            theme, nom, musique, lumiere_dedans, lumiere_dehors,
            json.dumps(directions),
            json.dumps(motivations),
            nombre_max_tours, duree_phase, nbmintours, json.dumps(popstar)
        ))
    conn.commit()
    conn.close()

def ajouter_bus(theme, nom, musique, lumiere_dedans, lumiere_dehors, directions, messages, nombre_max_tours, duree_phase, popstar, nbmintours=2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bus (theme, nom, musique, lumiere_dehors, lumiere_dedans, directions, messages, nombre_max_tours, duree_phase, nbmintours, popstar)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        theme, nom, musique, lumiere_dedans, lumiere_dehors,
        json.dumps(directions),
        json.dumps(messages),
        nombre_max_tours, duree_phase, nbmintours, json.dumps(popstar)
    ))
    conn.commit()

# Exemple d'ajout
#ajouter_bus(
#    theme="zen_fluidite",
#    nom="Zen et Fluidité",
#    musique="https://stunnel1.cyber-streaming.com:9162/stream?",
#    lumiere="bleu doux",
#    directions=["gauche"],
#    motivations=["Respire profondément", "Laisse le mouvement te guider", "Tu es en harmonie"],
#    nombre_max_tours=20,
#    duree_phase=10,
#    pas_tours=2,
#    repetitions=2
#)




def get_all_effets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM effets_lumineux ORDER BY id ASC")
    effets = cursor.fetchall()
    conn.close()
    return effets

def get_effet_by_id(effet_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM effets_lumineux WHERE id = ?", (effet_id,))
    effet = cursor.fetchone()
    conn.close()
    return effet

def get_etapes_effet(effet_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type, valeur FROM effet_etapes WHERE effet_id = ? ORDER BY id ASC", (effet_id,))
    etapes = cursor.fetchall()
    conn.close()
    return [(t, json.loads(v)) for t, v in etapes]

def create_effet(nom):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO effets_lumineux (nom) VALUES (?)", (nom,))
    effet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return effet_id

def create_type_effet(effet_id, mytype, myvalue):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO effet_etapes (effet_id, type, valeur)
        VALUES (?, ?, ?)
    """, (effet_id, mytype, json.dumps(myvalue)))
    conn.commit()
    conn.close()

def get_all_bus():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bus ORDER BY id ASC")
    bus = cursor.fetchall()
    conn.close()
    return bus

#def get_bus_by_id(bus_id):
#    conn = get_connection()
#    cursor = conn.cursor()
#    cursor.execute("SELECT * FROM bus WHERE id = ?", (bus_id,))
#    bus = cursor.fetchone()
#    conn.close()
#    return bus


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table des séances
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        theme TEXT,
        nom TEXT,
        musique TEXT,
        lumiere_dedans TEXT,
        lumiere_dehors TEXT,
        directions TEXT,
        motivations TEXT,
        nombre_max_tours INTEGER,
        duree_phase INTEGER,
        nbmintours INTEGER,
        popstar TEXT
    )
    """)

    # Table des effets lumineux
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS effets_lumineux (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL
    )
    """)

    # Table des étapes d'effet
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS effet_etapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        effet_id INTEGER,
        type TEXT,
        valeur TEXT,
        FOREIGN KEY (effet_id) REFERENCES effets_lumineux(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()
