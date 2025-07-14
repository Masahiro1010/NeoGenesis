from .models import GameSession
from .cards import ALL_CARDS

def card_slots(request):
    game_id = request.session.get("game_id")
    if not game_id:
        return {}

    try:
        game = GameSession.objects.get(id=game_id)
    except GameSession.DoesNotExist:
        return {}

    # カード情報を取得（code → Cardインスタンス）
    joker_cards = [ALL_CARDS.get(code) for code in game.joker_slots if code in ALL_CARDS]
    consume_cards = [ALL_CARDS.get(code) for code in game.consume_slots if code in ALL_CARDS]

    # deck_numbersはテンプレートで直接使えるリストのまま返す（辞書リスト）
    deck_numbers = game.deck_numbers

    return {
        'joker_cards': joker_cards,
        'consume_cards': consume_cards,
        'deck_numbers': deck_numbers,  
        'gold': game.gold,
    }

def score_table_context(request):
    raw_table = {
        (0, 0): 2, (0, 1): 3, (1, 0): 3,
        (0, 2): 5, (1, 1): 5, (2, 0): 7,
        (0, 3): 11, (1, 2): 11, (2, 1): 13,
        (3, 0): 17, (0, 4): 19, (1, 3): 19,
        (2, 2): 23, (4, 0): 29
    }

    # 👉 ("2H1B", 13) のように変換
    items = [ (f"{k[0]}H{k[1]}B", v) for k, v in raw_table.items() ]

    # 👉 2つずつペアにする
    paired_rows = [ items[i:i+2] for i in range(0, len(items), 2) ]

    return {'score_table_rows': paired_rows}
