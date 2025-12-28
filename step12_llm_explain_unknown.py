# step12_llm_explain_unknown.py
# -----------------------------------------
# ③ ハイブリッド判定（説明補助・無料版）
# 目的：
# - ①ルールベースで「判断不可」になった理由を
#   日本語で説明する
# - 判定自体は変更しない
# -----------------------------------------

from typing import List, Dict

# =========================
# ①の出力（サンプル）
# ※ 実運用では step11 の結果を渡す
# =========================
unknown_result = {
    "item": "crab extract",
    "result": "判断不可",
    "evidence": [
        {"article_id": "Reg_152.txt", "title": "Meat extract or meat essence"},
        {"article_id": "Reg_158.txt", "title": "Cured, pickled or salted fish"},
        {"article_id": "Reg_165.txt", "title": "Repealed regulation"}
    ]
}

# =========================
# 説明生成ロジック（無料）
# =========================
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
        "item": item,
        "final_result": "判断不可",
        "explanation": explanation,
        "related_articles": [e["article_id"] for e in evidence],
        "next_actions": next_actions
    }

# =========================
# 実行
# =========================
result = explain_unknown(
    unknown_result["item"],
    unknown_result["evidence"]
)

print("================================================")
print(f"原料名: {result['item']}")
print("最終判定: 判断不可（説明補助）")

print("\n■ 判定理由")
for r in result["explanation"]:
    print(f"- {r}")

print("\n■ 関連条文")
for a in result["related_articles"]:
    print(f"- {a}")

print("\n■ 次に確認すべきポイント")
for n in result["next_actions"]:
    print(f"- {n}")
print("================================================")
# =========================================
# Flask から呼ばれるためのラッパー関数
# =========================================
def explain_with_llm(text: str) -> dict:
    """
    Flask API 用ラッパー
    step11 から渡される text を元に、
    仮の unknown_result を使って説明を返す
    """
    return explain_unknown(
        unknown_result["item"],
        unknown_result["evidence"]
    )

