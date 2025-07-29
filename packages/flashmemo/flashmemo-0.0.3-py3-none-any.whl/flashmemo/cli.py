# flashmemo/cli.py

import argparse
from flashmemo.core import FlashMemo
from flashmemo.storage import Storage

def main():
    parser = argparse.ArgumentParser(prog="flashmemo", description="Génère et révise des fiches mémoire facilement.")
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_parser = subparsers.add_parser("add", help="➕ Ajouter une nouvelle carte")
    add_parser.add_argument("question", help="Question de la carte")
    add_parser.add_argument("answer", help="Réponse de la carte")

    # quiz
    subparsers.add_parser("quiz", help="Démarrer une session de révision")

    # list
    subparsers.add_parser("list", help="Afficher toutes les cartes")

    # delete
    delete_parser = subparsers.add_parser("delete", help=" Supprimer une carte")
    delete_parser.add_argument("index", type=int, help="Index de la carte à supprimer")

    args = parser.parse_args()
    app = FlashMemo(Storage())

    if args.command == "add":
        app.add_card(args.question, args.answer)
        print("✅ Carte ajoutée !")
    elif args.command == "quiz":
        app.quiz()
    elif args.command == "list":
        cards = app.get_all_cards()
        for i, card in enumerate(cards):
            print(f"{i}. ❓ {card['question']} -> ✅ {card['answer']}")
    elif args.command == "delete":
        if app.delete_card(args.index):
            print("Carte supprimée.")
        else:
            print(" Index invalide.")
    else:
        parser.print_help()
