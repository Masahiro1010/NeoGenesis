class EffectsApply:
    def apply_card_effect(game, card):
        effect_text = "効果が適用されました"

        if card.kind == "tarot":
            # タロットカードの効果を適用
            if card.code == "tarot_goldx2":
                if game.gold < 20:
                    # 所持金を倍にする
                    game.gold *= 2
                    effect_text = "所持金が2倍になった!"
                else:
                    game.gold += 20
                    effect_text = "所持金が20増えた!"
            if card.code == "tarot_jokergold":
                # タロットカードのゴールド効果
                gameGoldPlus = len(game.joker_slots) * 3
                game.gold += gameGoldPlus
                effect_text = "所持金がジョーカー*3増えた!"

        # ✅ 状態変更がある場合は保存が必須
        game.save()
        return effect_text
        
    
    