class FlashMemo:
    def __init__(self, storage):
        self.storage = storage

    def add_card(self, question, answer, level="facile"):
        self.storage.save_card({"question": question, "answer": answer, "level": level})

    def get_all_cards(self):
        return self.storage.load_cards()

    def delete_card(self, index):
        cards = self.storage.load_cards()
        if 0 <= index < len(cards):
            del cards[index]
            self.storage.save_all(cards)
            return True
        return False

    def quiz(self):
        import random
        cards = self.storage.load_cards()
        if not cards:
            print("❌ Aucune carte enregistrée.")
            return

        random.shuffle(cards)
        correct = 0
        total = len(cards)

        for i, card in enumerate(cards):
            print(f"\n🧠 Question {i + 1} (niveau : {card.get('level', 'n/a')}): {card['question']}")
            input("Appuie sur Entrée pour voir la réponse...")
            print(f"✅ Réponse : {card['answer']}")
            reponse = input("As-tu eu bon ? (o/n) ").strip().lower()
            if reponse == "o":
                correct += 1

        score = (correct / total) * 100
        print(f"\n🏁 Quiz terminé ! Score : {correct}/{total} -> {score:.1f}%")
