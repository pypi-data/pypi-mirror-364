from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__, template_folder="templates")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "flashcards.json")

def load_cards():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cards(cards):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)

@app.route("/")
def index():
    cards = load_cards()
    return render_template("index.html", cards=cards)

@app.route("/add", methods=["GET", "POST"])
def add_card():
    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")
        level = request.form.get("level", "facile")
        cards = load_cards()
        cards.append({"question": question, "answer": answer, "level": level})
        save_cards(cards)
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_card(index):
    cards = load_cards()
    if index < 0 or index >= len(cards):
        return "Index invalide", 404

    if request.method == "POST":
        cards[index]["question"] = request.form.get("question")
        cards[index]["answer"] = request.form.get("answer")
        cards[index]["level"] = request.form.get("level", "facile")
        save_cards(cards)
        return redirect(url_for("index"))

    return render_template("edit.html", card=cards[index], index=index)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_card(index):
    cards = load_cards()
    if index < 0 or index >= len(cards):
        return "Index invalide", 404
    cards.pop(index)
    save_cards(cards)
    return redirect(url_for("index"))

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

# API REST inchangée
@app.route("/api/cards", methods=["GET", "POST", "PUT", "DELETE"])
def manage_cards():
    cards = load_cards()

    if request.method == "GET":
        return jsonify(cards)

    if request.method == "POST":
        new_card = request.json
        cards.append(new_card)
        save_cards(cards)
        return jsonify({"success": True})

    if request.method == "PUT":
        updated_card = request.json
        index = updated_card.get("index")
        if index is not None and 0 <= index < len(cards):
            cards[index] = updated_card
            save_cards(cards)
            return jsonify({"success": True})
        return jsonify({"error": "Index invalide"}), 400

    if request.method == "DELETE":
        index = request.json.get("index")
        if index is not None and 0 <= index < len(cards):
            cards.pop(index)
            save_cards(cards)
            return jsonify({"success": True})
        return jsonify({"error": "Index invalide"}), 400

def run_server():
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    run_server()
