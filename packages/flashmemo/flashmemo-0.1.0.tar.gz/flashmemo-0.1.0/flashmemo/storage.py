import json
import os

class Storage:
    def __init__(self, path=None):
        if path is None:
            self.path = os.path.expanduser("~/.flashmemo_cards.json")
        else:
            self.path = path

    def load_cards(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_card(self, card):
        cards = self.load_cards()
        cards.append(card)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)

    def save_all(self, cards):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)
