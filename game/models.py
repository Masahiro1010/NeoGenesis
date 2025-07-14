from django.db import models
import uuid


class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    final_score = models.IntegerField(null=True, blank=True)
    current_ante_number = models.IntegerField(default=1)
    gold = models.IntegerField(default=10)

    # 🔄 deck_numbers を構造付きJSONにする（強化カード対応）
    deck_numbers = models.JSONField(default=list)  # [
                                                    #   {"number": "0", "effect": "double", "red_seal": False, "gold_seal": True},
                                                    #   ...
                                                    # ]

    # 💾 使用カードのログ（カード名, アンティー番号, タイプ等）
    used_cards = models.JSONField(default=list)

    # ✅ 購入したジョーカーカード（コードで保持）
    joker_slots = models.JSONField(default=list)

    # ✅ 購入した消費アイテム（最大3スロット）
    consume_slots = models.JSONField(default=list)

    def __str__(self):
        return f"Session {self.id} - Ante {self.current_ante_number}"

    def initialize_deck(self):
        """初期化：0〜9の数字に効果なしのデッキを生成"""
        return [
            {
                "number": str(i),
                "effect": None,         # "double", "gold", or buff（強化カード）
                "red_seal": False,
                "gold_seal": False
            } for i in range(10)
        ]

    def save(self, *args, **kwargs):
        if not self.deck_numbers:
            self.deck_numbers = self.initialize_deck()
        if self.joker_slots is None:
            self.joker_slots = []
        if self.consume_slots is None:
            self.consume_slots = []
        if self.used_cards is None:
            self.used_cards = []
        super().save(*args, **kwargs)


class Round(models.Model):
    game = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='rounds')
    ante_number = models.IntegerField()
    answer_code = models.CharField(max_length=4)  # 例: '1234'
    score_total = models.IntegerField(default=0)
    shop_choices = models.JSONField(default=dict)  # 例: {"joker_pack": ["奇数カード", ...]}

    def __str__(self):
        return f"Ante {self.ante_number} - Game {self.game.id}"


class Guess(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='guesses')
    guess_code = models.CharField(max_length=4)
    hit = models.IntegerField()
    blow = models.IntegerField()
    role_score = models.IntegerField()
    card_score = models.IntegerField()
    total_score = models.IntegerField()

    def __str__(self):
        return f"Guess {self.guess_code} - H{self.hit}B{self.blow}"

"""
class Card(models.Model):
    CARD_TYPE_CHOICES = [
        ('joker', 'ジョーカー'),
        ('tarot', 'タロット'),
        ('spectral', 'スペクトル'),
        ('item', 'アイテム'),
    ]
    SLOT_TYPE_CHOICES = [
        ('joker', 'ジョーカースロット'),
        ('consumable', '消費スロット'),
    ]

    game = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='cards')
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    card_name = models.CharField(max_length=50)
    slot_type = models.CharField(max_length=20, choices=SLOT_TYPE_CHOICES)
    is_used = models.BooleanField(default=False)
    target_number = models.IntegerField(null=True, blank=True)  # 強化対象数字などに使用

    def __str__(self):
        return f"{self.card_name} ({self.card_type})"
"""