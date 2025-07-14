from dataclasses import dataclass

@dataclass
class Card:
    code: str           # 一意の識別子
    name: str           # 表示名
    price: int          # 値段（ショップ価格）
    description: str    # 効果の説明
    kind: str           # カード種別（'ジョーカー', 'アイテム', 'タロット', 'スペクトル', 'パック' など）

# ------------------------------
# ジョーカーカード一覧
# ------------------------------
JOKER_CARDS = {
    "joker_even": Card("joker_even", "偶数カード", 5, "偶数のヒット+2、ブロー+1", "joker"),
    "joker_odd": Card("joker_odd", "奇数カード", 5, "奇数のヒット+2、ブロー+1", "joker"),
    "joker_low": Card("joker_low", "ローカード", 5, "0〜4のヒット+2、ブロー+1", "joker"),
    "joker_high": Card("joker_high", "ハイカード", 5, "5〜9のヒット+2、ブロー+1", "joker"),
    "joker_pi": Card("joker_pi", "円周率カード", 6, "1,3,4のヒット+3、ブロー+2", "joker"),
    "joker_H": Card("joker_H", "Hカード", 4, "ヒットのみ時に+5", "joker"),
    "joker_B": Card("joker_B", "Bカード", 3, "ブローのみ時に+3", "joker"),
    "joker_reroll": Card("joker_reroll", "リロールカード", 2, "ショップリロール可", "joker"),
}

# ------------------------------
# アイテムカード一覧
# ------------------------------
ITEM_CARDS = {
    "item_highlow": Card("item_highlow", "ハイローカード", 2, "2つの数字が0-4 or 5-9かを判別", "item"),
    "item_evenodd": Card("item_evenodd", "偶奇判定カード", 2, "2つの数字が偶数か奇数か判別", "item"),
    "item_randomize": Card("item_randomize", "randomカード", 3, "問題をランダムに変更", "item"),
}

# ------------------------------
# タロットカード一覧（例）
# ------------------------------
TAROT_CARDS = {
    "tarot_buff": Card("tarot_buff", "強化カード", 3, "数字1つをヒット時役点*2に", "tarot"),
    "tarot_gold": Card("tarot_gold", "ゴールドカード", 3, "数字1つをブロー時金+3に", "tarot"),
    "tarot_steel": Card("tarot_steel", "スチールカード", 4, "その数字を予想が外れたら+2", "tarot"),
    "tarot_jokergold": Card("tarot_jokergold", "ジョーカー金作カード", 5, "ジョーカーの値段合計を得る", "tarot"),
    "tarot_goldx2": Card("tarot_goldx2", "金倍カード", 5, "金を倍にする", "tarot"),
}

# ------------------------------
# スペクトルカード一覧（例）
# ------------------------------
SPECTRAL_CARDS = {
    "spectral_trim": Card("spectral_trim", "デッキ圧縮カード", 3, "デッキの数字を1つ削除", "spectral"),
    "spectral_add": Card("spectral_add", "相手デッキ追加カード", 3, "相手デッキに数字を1つ追加", "spectral"),
    "spectral_change": Card("spectral_change", "デッキ変更カード", 3, "デッキ内数字を任意のものに変更", "spectral"),
    "spectral_red": Card("spectral_red", "レッドシールカード", 4, "予想時ジョーカー/強化効果再発動", "spectral"),
    "spectral_gold": Card("spectral_gold", "ゴールドシールカード", 4, "その数字を使うだけで+2ドル", "spectral"),
}

# ------------------------------
# パック一覧（例）
# ------------------------------
PACKS = {
    "pack_tarot_small": Card("pack_tarot_small", "🔮 タロット小パック", 3, "3枚から1枚選べる", "pack"),
    "pack_tarot_large": Card("pack_tarot_large", "🔮 タロット大パック", 6, "5枚から2枚選べる", "pack"),
    "pack_spectral_small": Card("pack_spectral_small", "👻 スペクトル小パック", 3, "3枚から1枚選べる", "pack"),
    "pack_spectral_large": Card("pack_spectral_large", "👻 スペクトル大パック", 6, "5枚から2枚選べる", "pack"),
    "pack_joker_small": Card("pack_joker_small", "🃏 ジョーカー小パック", 3, "3枚から1枚選べる", "pack"),
    "pack_joker_large": Card("pack_joker_large", "🃏 ジョーカー大パック", 6, "5枚から2枚選べる", "pack"),
    "pack_item_small": Card("pack_item_small", "🧪 アイテム小パック", 3, "3枚から1枚選べる", "pack"),
    "pack_item_large": Card("pack_item_large", "🧪 アイテム大パック", 6, "5枚から2枚選べる", "pack"),
}

# ------------------------------
# すべてのカードを統合
# ------------------------------
ALL_CARDS = {
    **JOKER_CARDS,
    **ITEM_CARDS,
    **TAROT_CARDS,
    **SPECTRAL_CARDS,
    **PACKS
}