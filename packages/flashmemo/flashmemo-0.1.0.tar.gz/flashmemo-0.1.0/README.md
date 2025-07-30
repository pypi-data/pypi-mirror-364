# flashmemo

**flashmemo** est un outil en ligne de commande simple et léger pour créer, gérer et réviser des fiches de mémorisation (flashcards). Il facilite l’apprentissage en permettant aux utilisateurs d’ajouter des questions/réponses, de lancer des sessions de quiz interactifs, de lister, modifier ou supprimer des fiches, et même d’utiliser une interface web.

---

## Fonctionnalités

- Ajouter facilement de nouvelles fiches de révision avec un **niveau de difficulté** (facile, moyen, difficile)  
- Lister toutes les fiches existantes  
- Modifier ou supprimer une fiche par son index  
- Lancer une session de quiz aléatoire pour réviser les fiches avec score détaillé à la fin  
- Exporter les fiches en **fichier HTML** pour une consultation hors-ligne  
- Gérer les fiches via une **interface web** intuitive (ajout, modification, suppression, quiz)

---

## Installation

Installez le package via `pip` en local ou depuis PyPI :

```bash
pip install flashmemo
Utilisation en ligne de commande

Le package fournit une interface CLI flashmemo avec les commandes suivantes :
flashmemo --help

Ajouter une fiche
flashmemo add "Question ici" "Réponse ici" --level facile
Le paramètre --level est optionnel (par défaut : facile).

Lancer une session de quiz
flashmemo quiz
Le quiz affichera les questions, vous invitera à saisir vos réponses et calculera un score final détaillé.

Lister les fiches
flashmemo list

Supprimer une fiche
flashmemo delete <index>

Exporter les fiches en HTML
flashmemo export-html
Génère un fichier flashcards.html avec toutes les fiches au format consultable dans un navigateur.

Lancer l’interface web
flashmemo web
Ouvre un serveur local (par défaut sur http://localhost:5000) avec une interface graphique pour gérer les fiches et lancer le quiz.


