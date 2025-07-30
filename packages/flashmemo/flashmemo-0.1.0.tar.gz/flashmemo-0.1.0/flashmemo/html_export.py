import os
import webbrowser
from flashmemo.core import FlashMemo
from flashmemo.storage import Storage

def export_to_html(output_path="flashcards.html"):
    app = FlashMemo(Storage())
    cards = app.get_all_cards()

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <title>Cartes mémoire</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
        h1 { text-align: center; color: #333; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .question { font-weight: bold; color: #007bff; }
        .answer { margin-top: 10px; color: #28a745; }
        .tag { font-size: 0.9em; color: #6c757d; margin-top: 5px; }
        button { display: block; margin: 0 auto 30px auto; padding: 10px 20px;
                 font-size: 16px; cursor: pointer; border: none; background: #007bff; color: white;
                 border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🧠 Mes cartes mémoire</h1>
    <button id="toggleAnswers">Masquer les réponses</button>
"""

    for card in cards:
        tag = card.get("tag", "général")
        html += f"""
    <div class="card">
        <div class="question">❓ {card['question']}</div>
        <div class="answer">✅ {card['answer']}</div>
        <div class="tag">🏷️ Thème : {tag}</div>
    </div>
"""

    html += """
<script>
const toggleBtn = document.getElementById('toggleAnswers');
const answers = document.querySelectorAll('.answer');
let visible = true;

toggleBtn.addEventListener('click', () => {
    visible = !visible;
    answers.forEach(ans => {
        ans.style.display = visible ? 'block' : 'none';
    });
    toggleBtn.textContent = visible ? 'Masquer les réponses' : 'Afficher les réponses';
});

// Par défaut, les réponses sont visibles (tu peux changer ici si tu veux)
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Export HTML terminé : {output_path}")
    print("Le fichier s’ouvre dans votre navigateur par défaut.")
    abs_path = os.path.abspath(output_path)
    webbrowser.open(f"file://{abs_path}")
