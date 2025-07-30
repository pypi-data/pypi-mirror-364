import tempfile
import os
import json
import pytest

from flashmemo.core import FlashMemo
from flashmemo.storage import Storage

def test_add_card_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        # On crée un storage avec un chemin personnalisé
        storage = Storage(path=os.path.join(tmpdir, "cards.json"))
        flashmemo = FlashMemo(storage)

        # Au début, aucun fichier ni carte
        assert not os.path.exists(storage.path)
        assert storage.load_cards() == []

        # Ajouter une carte
        flashmemo.add_card("Quelle est la capitale de la France?", "Paris")

        # Le fichier est créé
        assert os.path.exists(storage.path)

        # Les données sont bien écrites
        cards = storage.load_cards()
        assert len(cards) == 1
        assert cards[0]["question"] == "Quelle est la capitale de la France?"
        assert cards[0]["answer"] == "Paris"

def test_delete_card():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(path=os.path.join(tmpdir, "cards.json"))
        flashmemo = FlashMemo(storage)

        # Ajouter 2 cartes
        flashmemo.add_card("Q1", "A1")
        flashmemo.add_card("Q2", "A2")

        cards = storage.load_cards()
        assert len(cards) == 2

        # Supprimer la première carte
        result = flashmemo.delete_card(0)
        assert result is True

        cards = storage.load_cards()
        assert len(cards) == 1
        assert cards[0]["question"] == "Q2"

        # Supprimer un index invalide
        result = flashmemo.delete_card(10)
        assert result is False

def test_get_all_cards():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(path=os.path.join(tmpdir, "cards.json"))
        flashmemo = FlashMemo(storage)

        flashmemo.add_card("Q1", "A1")
        flashmemo.add_card("Q2", "A2")

        cards = flashmemo.get_all_cards()
        assert len(cards) == 2
        assert cards[0]["question"] == "Q1"
        assert cards[1]["answer"] == "A2"
