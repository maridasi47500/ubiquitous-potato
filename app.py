from flask import Flask, render_template, request, redirect, url_for
from dbbus import init_db, get_all_bus, get_bus_by_id, save_bus
from flask import send_file
from hey_generate_yaml import generer_yaml_depuis_formulaire
import json
from led_nest_mini_python import generer_bus_yaml, menu_bus  # Ton script renommé en module
import json
from dbbus import create_effet, create_type_effet  # Assure-toi que ces fonctions existent
from dbbus import get_effet_by_id, get_etapes_effet
import asyncio
from dbbus import get_all_effets
import asyncio
import websockets
import threading

async def envoyer_lumiere(style):
    uri = "ws://192.168.1.18:8765"  # IP du serveur WebSocket
    async with websockets.connect(uri) as websocket:
        await websocket.send(style)


def envoyer_lumiere_thread(style):
    def run():
        asyncio.run(envoyer_lumiere(style))
    threading.Thread(target=run).start()



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






app = Flask(__name__)

init_db()

def charger_bus_depuis_db():
    rows = get_all_bus()
    bus = {}
    for row in rows:
        theme = row[1]
        bus[theme] = {
            "id": row[0],
            "theme": row[1],
            "nom": row[2],
            "musique": row[3],
            "lumiere": row[4],
            "directions": nettoyer_json_embedded(row[5]),
            "motivations": nettoyer_json_embedded(row[6]),
            "nombre_max_tours": row[7],
            "duree_phase": row[8],
            "nbmintours": row[9],
            "popstar": nettoyer_json_embedded(row[10])
        }
    return bus

menu_bus = charger_bus_depuis_db()

@app.route("/effet/<int:id>")
def voir_effet(id):
    effet = get_effet_by_id(id)
    etapes = get_etapes_effet(id)
    return render_template("voir_effet.html", effet=effet, etapes=etapes, message=None)



@app.route("/effet/<int:id>", methods=["POST"])
def rejouer_effet(id):
    effet = get_effet_by_id(id)
    etapes = get_etapes_effet(id)
    envoyer_lumiere_thread(effet[1])
    message="effet est en train d'être rejoué"
    return render_template("voir_effet.html", effet=effet, etapes=etapes, message=message)
@app.route("/effets", methods=["GET","POST"])
def liste_effets():
    effets = get_all_effets()
    message=""
    if request.method == 'POST':
        effet = request.form.get('effet')
        effet = get_effet_by_id(effet)
        envoyer_lumiere_thread(effet[1])
        message="effet '"+effet[1]+"' lancé avec succes"
    return render_template("liste_effets.html", effets=effets, message=message)


@app.route("/formlamp", methods=["GET"])
def form_lamp():
    return render_template("formlamp.html")


@app.route("/effet", methods=["POST"])
def effet():
    name = request.form["name"]
    effets = json.loads(request.form["effets_json"])

    # Créer l'effet principal
    effet_id = create_effet(name)

    # Enregistrer chaque étape de l'effet
    for effet in effets:
        mytype = effet["type"]
        myvalue = effet["value"]
        create_type_effet(effet_id, mytype, myvalue)
        print(f"{mytype} → {myvalue}")

    return "✅ Effets lumineux enregistrés avec succès !"





@app.route("/generer_yaml", methods=["POST"])
def generer_yaml():
    bus_id = request.form.get('theme')
    bus = get_bus_by_id(bus_id)

    if not bus:
        return "❌ Séance introuvable", 404

    # Préparer les paramètres comme tuple
    params = (
        bus[1],  # theme
        bus[2],  # nom
        bus[3],  # musique
        bus[4],  # lumiere
        bus[5],  # directions (JSON string)
        bus[6],  # motivations (JSON string)
        bus[7],  # nombre_max_tours
        bus[8],  # duree_phase
        bus[9],  # nbmintours
        bus[10]  # motivations (JSON string)
    )

    # Générer le fichier YAML
    nom_fichier = generer_yaml_depuis_formulaire(params)

    # Optionnel : proposer le téléchargement
    return send_file(nom_fichier, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    bus = charger_bus_depuis_db()
    if request.method == 'POST':
        randomlist = request.form.get('randomlist')
        theme = request.form.get('theme')
        if theme in bus:
            generer_bus_yaml(theme, randomlist=randomlist)
            message = f"Séance '{bus[theme]['nom']}' lancée avec succès !"
        else:
            message = "Thème invalide."

        return render_template('index.html', bus=bus, menu=bus, message=message)
    return render_template('index.html', bus=bus, menu=bus)





@app.route("/edit/<int:bus_id>")
def edit(bus_id):
    bus = get_bus_by_id(bus_id)
    return render_template("form.html", bus=bus)

@app.route("/new")
def new():
    return render_template("form.html", bus=None)

@app.route("/save", methods=["POST"])
def save():
    bus_id = request.form.get("id")
    save_bus(
        request.form["theme"],
        request.form["nom"],
        request.form["musique"],
        request.form["lumiere"],
        json.dumps(request.form["directions"]),
        json.dumps(request.form["motivations"]),
        int(request.form["nombre_max_tours"]),
        int(request.form["duree_phase"]),
        int(request.form["nbmintours"]),
        json.dumps(request.form["popstar"]),
        bus_id=bus_id
    )

    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

