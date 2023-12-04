# song_difficulty
Projet personnel : Calculer un score de difficulté à partir d'une partition téléchargée depuis Musescore

# Utilisation
Pour utiliser le script il faut télécharger une partition au format "musicXML" depuis le site de Musescore. 
Il faut ensuite indiquer le chemin jusqu'au fichier téléchargé dans la fonction "mxlConvert()" avant de lancer le script.

# Résultat
- Un score indique la difficulté de plusieurs paramètres, tels que le nombre de notes par seconde, la distance moyenne entre les notes, ...
- Une seconde partie divise la musique en sections pour distinguer les passages complexes des passages plus simples, et affiche en conséquence 
les scores des paramètres cités précédemment, cette fois spécifiques à la section, afin d'obtenir des résultats plus précis.
- Un résultat issu de la moyenne des sections est ensuite affiché, avec un score global sur toute la musique.
