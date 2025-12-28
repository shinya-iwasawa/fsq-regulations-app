from flask import Flask, request, jsonify, render_template
from pathlib import Path
import json
import re
from datetime import datetime

# =========================
# App setup
# =========================
app = Flask(__name__)

BASE_DIR = Path(__file__).parent

# =========================
# Load dictionaries
# =========================
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

INGREDIENT_DICT = load_json(BASE_DIR / "ingredient_dictionary.json")
PROHIBITED_DICT = load_json(BASE_DIR / "prohibited_category_dictionary.json")
LIMIT_EXAMPLES = load_json(BASE_DIR / "regulatory_limit_examples.json")
REG_SOURCES = load_json(BASE_DIR / "regulatory_sources.json")

# =========================
# Dummy rule-based judge
# （STEP3で既存ロジックと統合）
# =========================
def rule_based_judge(normalized):
    return {
        "judgement": "判断不可",
        "reason": "明示的な使用可／禁止規定は確認できませんでした。"
    }

# =========================
# Helpers
# =========================
def normalize_ingredient(text):
    return INGREDIENT_DICT.get(text, None)

def find_prohibited_examples(normalized):
    hits = []
    for cat, info in PROHIBITED_DICT.items():
        for ex in info.get("examples", []):
            if normalized and normalized.lower() in ex.lower():
                hits.append({
                    "category": cat,
                    "example": ex,
                    "note": info.get("note", "")
                })
    return hits

# =========================
# Routes
# =========================
@app.route("/")
def index():
    """初期表示用のルート"""
    return render_template("index.html", result=None, form_country=None, form_ingredients=None, form_mode='ingredients')

@app.route("/judge", methods=["POST"])
def judge():
    """判定処理を行い、結果を埋め込んだHTMLを返すルート"""
    # フォームからデータを取得
    country = request.form.get("country", "")
    ingredients_text = request.form.get("ingredients", "").strip()
    mode = request.form.get("mode", "ingredients")

    # 改行、カンマ（全角・半角）で分割し、各要素の空白を除去し、空の要素を無視する
    ingredients_list = [
        item.strip() for item in re.split(r'[\n,、]', ingredients_text) if item.strip()
    ]
    
    individual_results = []
    sources_to_show = []
    overall_status = "OK"

    if not ingredients_list:
        overall_status = "入力エラー"
        reason = "原材料が入力されていません。"
        individual_results.append({"name": "-", "status": "エラー", "reason": reason})
    else:
        has_warning = False
        for ingredient in ingredients_list:
            # 個別の判定ロジック
            status = "OK"
            reason = "この原材料は規制対象外です。"
            if "かに" in ingredient or "カニ" in ingredient:
                status = "注意"
                reason = "甲殻類アレルギー表示の要件、および輸出先の規制を確認してください。"
                has_warning = True
                # かに関連の条文を結果に追加
                sources_to_show.extend([s for s in REG_SOURCES if "CRAB" in s.get("id", "") or "ALLERGEN" in s.get("id", "")] )
            elif "小麦" in ingredient:
                status = "注意"
                reason = "アレルギー表示の要件を確認してください。"
                has_warning = True
                # 小麦関連の条文を結果に追加
                sources_to_show.extend([s for s in REG_SOURCES if "ALLERGEN" in s.get("id", "")] )
            
            individual_results.append({"name": ingredient, "status": status, "reason": reason})
        
        if has_warning:
            overall_status = "注意"

    # 重複するソースを削除 (辞書のリストはsetに直接入れられないため、タプルに変換)
    unique_sources = [dict(t) for t in {tuple(d.items()) for d in sources_to_show}]

    # テンプレートに渡すデータを作成
    result_data = {
        "country_name": country.capitalize() if country else "N/A",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_status": overall_status,
        "results": individual_results,
        "input_text": ingredients_text,
        "sources": unique_sources
    }

    return render_template(
        "index.html",
        result=result_data,
        form_country=country,
        form_ingredients=ingredients_text,
        form_mode=mode
    )

# =========================
# Run
# =========================
# if __name__ == "__main__":
#     app.run(debug=True, port=8000)