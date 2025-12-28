from flask import Flask, request, jsonify, render_template
from typing import List, Dict

app = Flask(__name__, template_folder="templates")

# ====== UI ======
@app.route("/")
def index():
    return render_template("index.html")

# ====== ③Aの説明ロジック ======
def explain_unknown(item: str, evidence: List[Dict]) -> Dict:
    explanation = [
        f"{item} を直接定義または明示的に規制する条文が Food Regulations 1985 本文中に存在しません。",
        "近接概念（例：meat extract 等）の規定は確認されましたが、甲殻類由来原料との包含関係は条文上明確ではありません。",
        "Schedules（別表）や個別通知における指定の有無については、本文条文のみからは判断できません。"
    ]
    next_actions = [
        "Food Regulations 1985 の Schedules（別表）の確認",
        "Codex Alimentarius における甲殻類由来原料の扱いの確認",
        "FSQ（マレーシア食品安全当局）への事前照会（Pre-market approval）の検討"
    ]
    return {
        "final_result": "判断不可",
        "explanation": explanation,
        "related_articles": [e["article_id"] for e in evidence],
        "next_actions": next_actions
    }

# ====== API ======
@app.route("/judge", methods=["POST"])
def judge():
    data = request.get_json(force=True)
    item = data.get("item", "")
    evidence = data.get("evidence", [])

    # ※ ①の判定が「判断不可」の場合のみ③Aを使う想定（今は常に説明補助）
    result = explain_unknown(item, evidence)

    return jsonify({
        "item": item,
        "result": result["final_result"],
        "explanation": result["explanation"],
        "related_articles": result["related_articles"],
        "next_actions": result["next_actions"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
