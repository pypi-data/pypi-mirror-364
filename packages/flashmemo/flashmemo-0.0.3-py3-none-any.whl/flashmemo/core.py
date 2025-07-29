class FlashMemo:
    def __init__(self, storage):
        self.storage = storage

    def add_card(self, question, answer):
        self.storage.save_card({"question": question, "answer": answer})

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
        for i, card in enumerate(cards):
            print(f"\n🧠 Question {i + 1}: {card['question']}")
            input("Appuie sur Entrée pour voir la réponse...")
            print(f"✅ Réponse : {card['answer']}")
