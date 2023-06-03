// =================================  Script de gestion de message linké à room.html ========================================

// Chargement de socket io côté client
let socketio = io();

// Récupération de l'endroit où on va afficher les messages
const messages = document.getElementById('messages');

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

// On écoute l'évenement 'message'. Quand celui-ci est reçu,avec les datas qui l'accompagne
// on l'ajoute au DOM en montant un nouveau message grâce à la fonction précédente 
socketio.on('message', (data) => {
    createMessage(data.name, data.message);
});

// ==== Envoi d'un message au serveur avec emit() puis reset le champs d'input ====
// ==== la fonction s'effectue quand on clique sur le bouton Envoyer grâce à onClick =====
const sendMessage = () => {
    const message = document.getElementById('message')
    if (message.value == "") { return; }
    socketio.emit('message', { data: message.value });
    message.value = "";
}