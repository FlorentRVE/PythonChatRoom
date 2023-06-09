// =================================  Script de gestion de message linké à room.html ========================================

// Connection au serveur socket io
let socketio = io();

// Récupération de l'endroit où on va afficher les messages
const messages = document.getElementById('messages');

// ============================= Reception et affichage des messages =======================

// Fonction permettant la création du corps du message avec les variables 'name' et 'msg'
// Puis de l'ajouter dans le DOM 
const createMessage = (name, msg) => {
    const content = `
    <div class="text">
        <span>
            <strong>${name}</strong>: ${msg}
        </span>
        <span class="muted">
            ${new Date().toLocaleString()}
        </span>
            
    </div>`;
    
    messages.innerHTML += content;
}

// On écoute l'évenement 'message'. Quand on reçoit un nouveau message,avec les datas qui l'accompagne
// on l'ajoute au DOM en construisant un nouveau message grâce à la fonction précédente 
socketio.on('message', (data) => {
    createMessage(data.name, data.message);
});

// =========================================================================================


// ============= Envoi d'un message au serveur avec emit() puis reset le champs d'input ==========
// ==== la fonction s'effectue quand on clique sur le bouton Envoyer grâce à onClick =====
const sendMessage = () => {
    const message = document.getElementById('message')
    if (message.value == "") { return; }
    socketio.emit('message', { data: message.value });
    message.value = "";
}

// ===================Ajout de l'event listener sur la touche Entrer pour envoyer un message ==============
document.addEventListener('keypress', (event)=>{

if(event.keyCode === 13) {

    sendMessage();
}
    
});