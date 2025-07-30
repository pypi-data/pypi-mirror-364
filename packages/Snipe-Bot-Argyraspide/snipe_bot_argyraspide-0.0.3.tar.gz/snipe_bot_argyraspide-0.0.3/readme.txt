1  - Objectif et usage

    Cette application a pour but de générer un chatbot twitch qui se connecte à une chaine spécifique.
    Sa seule fonction est une réponse à la commande !snipe (insérée dans le chat twitch).
    Le chatbot produit alors un compte à rebours de ma forme 
    ---- 5 ----
    ---- 4 ----
    ---- 3 ----
    ---- 2 ----
    ---- 1 ----
    ---- GO ! ----

    Le chatbot dispose d'un temps de rechargement, configurable, afin d'éviter le spamm.

2  - Paramètres

    Les paramètres sont listés dans le fichier config.py, éditable à l'aide du bloc-note ou de tout autre éditeur de texte 

    + CLIENT_ID : Paramètre spécifique à l'API twitch 
    + CLIENT_SECRET : Paramètre spécifique à l'API Twitch

    Nous recommendons à l'utilisateur de ne pas modifier ces valeurs avant de s'être bien renseigné.

    +cooldown : Paramètre du temps de rechargement en secondes


3  - Construction et fonctionnement.

    Cette application est construite sur le modèle proposé dans cette vidéo, il est assez rudimentaire.
    https://youtu.be/Vq6nRADd6ns?si=-XSR2_ynmGl4KZdt

    Le passage du programme python à l'application dédiée et utilisable par le système windows est expliqué dans la page :
    https://stevedower.id.au/blog/build-a-python-app

    