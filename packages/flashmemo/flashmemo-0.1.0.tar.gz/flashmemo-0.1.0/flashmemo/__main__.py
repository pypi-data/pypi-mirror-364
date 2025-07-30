import argparse
from flashmemo.core import FlashMemo
from flashmemo.storage import Storage
from flashmemo.html_export import export_to_html

def main():
    parser = argparse.ArgumentParser(
        prog="flashmemo",
        description="🧠 Gère et révise des fiches mémoire facilement."
    )
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_parser = subparsers.add_parser("add", help="➕ Ajouter une nouvelle carte")
    add_parser.add_argument("question", help="Question de la carte")
    add_parser.add_argument("answer", help="Réponse de la carte")
    add_parser.add_argument("--level", choices=["facile", "moyen", "difficile"], default="moyen", help="Niveau de difficulté")

    # quiz
    subparsers.add_parser("quiz", help="🎯 Démarrer une session de révision")

    # list
    subparsers.add_parser("list", help="📋 Afficher toutes les cartes")

    # delete
    delete_parser = subparsers.add_parser("delete", help="❌ Supprimer une carte")
    delete_parser.add_argument("index", type=int, help="Index de la carte à supprimer")

    # export-html
    subparsers.add_parser("export-html", help="📄 Exporter les cartes en fichier HTML")

    # web
    subparsers.add_parser("web", help="🌐 Lancer l'interface web")

    # exécution
    args = parser.parse_args()
    app = FlashMemo(Storage())

    if args.command == "add":
        app.add_card(args.question, args.answer, args.level)
        print(f"✅ Carte ajoutée avec le niveau '{args.level}' !")
    elif args.command == "quiz":
        app.quiz()
    elif args.command == "list":
        cards = app.get_all_cards()
        for i, card in enumerate(cards):
            print(f"{i}. ❓ {card['question']} -> ✅ {card['answer']} (niveau : {card.get('level', 'inconnu')})")
    elif args.command == "delete":
        if app.delete_card(args.index):
            print("🗑️ Carte supprimée.")
        else:
            print("❌ Index invalide.")
    elif args.command == "export-html":
        export_to_html()
    elif args.command == "web":
        import flashmemo.web
        flashmemo.web.run_server()
    else:
        parser.print_help()
