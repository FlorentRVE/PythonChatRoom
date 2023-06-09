from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from string import ascii_uppercase
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

#===== Initier le dictionnaire rooms qui contiendra les différentes rooms ===== 
# et les informations sur ces rooms : 'messages' et 'member'
rooms = {}

#====================== Génération aléatoire du code unique pour chaque room ==============
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    return code

# ===================================== ROUTES ==================================

# ===================================== '/' ==================================
# Si la requete est GET, on affiche la page d'accueil
# Si la requete est POST, on récupére les informations du formulaire. On rejoins une room si le code est valide.
# ou on en créer une si le code est fourni par l'utilisateur.
@app.route('/', methods=['GET', 'POST'])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get('name')
        code = request.form.get('code')
        colour = request.form.get('colour')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('home.html', error="Veuillez entrer un nom", code=code, name=name)
        
        if join != False and not code:
            return render_template('home.html', error="Veuillez entrer un code", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template('home.html', error="Ce code n'existe pas", code=code, name=name)

        session["room"] = room
        session["name"] = name
        session["colour"] = colour
        return redirect(url_for('room'))

    return render_template('home.html')

# ===================================== '/room' ==================================
# Si la requete est GET, on affiche la page de la room sauf s'il n'y a pas de room ou de nom
# dans ce cas, on affiche la page d'accueil
@app.route('/room')
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for('home'))
    
    return render_template('room.html', code=room, messages=rooms[room]["messages"])

#========================= Gestion des messages dans socketio =============

# A la réception d'un message émis par un client, on récupère l'id de la room, puis
# on créer un dictionnaire 'content' avec les informations du message.
# Ensuite on l'ajoute dans la liste des messages de la room et on l'envoi à la room correspondante.

@socketio.on('message')
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    content= {
        "name": session.get("name"),
        "message": data["data"],
        "colour": session.get("colour")
    }
    send(content, to=room)
    rooms[room["messages"]].append(content)
    print(f"{session.get('name')} said: {data['data']}")
    

#============== Gestion des connexions / Déconnexions socketio =============

#================= CONNECT ]
# A chaque connexion, on récupère l'id de la room et le nom de l'utilisateur via la session.
# On vérifie si la room existe dans la liste des rooms sinon on quitte la room. 
# Si elle existe on rejoint avc join_room() en affichant un message indiquant que l'utilisateur est entré dans la room.
# Enfin on met à jour le nombre de membres de la room.

@socketio.on('connect')
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} has entered {room}")

#================ DISCONNECT ]
# On récupère l'id de la room et le nom de l'utilisateur via la session.
# On quitte la room correspondante avec leave_room()
# On vérifie si la room existe dans la liste, si oui on décrémente le nombre de membre de 1
# et si le nombres de membres est inférieur ou égal à zéro on supprimme tout simplement la room
# On affiche un message indiquant que l'utilisateur a quitté la room.

@socketio.on('disconnect')
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left {room}")

# ===========================================

# Si le fichier Python est exécuté directement ( et non importé), on lance le serveur
# debug=True active le mode débogage pour afficher les erreurs.

if __name__ == '__main__':
    socketio.run(app, debug=True)