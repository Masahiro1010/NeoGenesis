class PlusCardScore:
    def JokerJudge(score, joker_slots, judge_HBN = None, guess = None, card_deck = None):
        """
        ジョーカーカードのスコア計算
        """
        jokerHflg = True
        jokerBflg = True
        jokerCount = 0
        guessNCount = 0

        for judge in judge_HBN:
            redSealFlg = True
            redSealCount = 0
            while redSealFlg:
                if judge == "H":
                    for slot in joker_slots:
                        print ("slot")
                        if slot == "joker_even" and int(guess[jokerCount]) % 2 == 0:
                            score += 2
                        elif slot == "joker_odd" and int(guess[jokerCount]) % 2 == 1:
                            score += 2
                        elif slot == "joker_low" and int(guess[jokerCount]) < 5:
                            score += 2
                        elif slot == "joker_high" and int(guess[jokerCount]) >= 5:
                            score += 2
                        elif slot == "joker_pi" and int(guess[jokerCount]) in [1, 3, 4]:
                            score += 3
                if judge == "B":
                    for slot in joker_slots:
                        if slot == "joker_even" and int(guess[jokerCount]) % 2 == 0:
                            score += 1
                        elif slot == "joker_odd" and int(guess[jokerCount]) % 2 == 1:
                            score += 1
                        elif slot == "joker_low" and int(guess[jokerCount]) < 5:
                            score += 1
                        elif slot == "joker_high" and int(guess[jokerCount]) >= 5:
                            score += 1
                        elif slot == "joker_pi" and int(guess[jokerCount]) in [1, 3, 4]:
                            score += 2
                redSealFlg = False
                if card_deck[int(guess[jokerCount])]["red_seal"] == True and redSealCount < 1:
                    redSealCount += 1
                    redSealFlg = True
            jokerCount += 1

        for judge in judge_HBN:
            if judge == "N":
                guessNCount += 1
            if judge == "B":
                jokerHflg = False
        
        for judge in judge_HBN:
            if judge == "H":
                jokerBflg = False

        if jokerHflg and "joker_H" in joker_slots and guessNCount != 4:
            score += 5
        if jokerBflg and "joker_B" in joker_slots and guessNCount != 4:
            score += 3
        
        return score

    def StrongerJudge(score, card_deck, judge_HBN = None, guessList = None, game = None):
        """
        強化カードのスコア計算
        """
        for i in range(4):
            redSealFlg = True
            redSealCount = 0
            while redSealFlg:
                if card_deck[int(guessList[i])]["effect"] == "buff":
                    if judge_HBN[i] == "H":
                        score += 3
                    elif judge_HBN[i] == "B":
                        score += 2
                if card_deck[int(guessList[i])]["effect"] == "gold":
                    if judge_HBN[i] == "B":
                        game.gold += 3
                if card_deck[int(guessList[i])]["effect"] == "steel":
                    if judge_HBN[i] == "N":
                        score += 3
                if card_deck[int(guessList[i])]["gold_seal"] == True:
                    game.gold += 2
                redSealFlg = False
                if card_deck[int(guessList[i])]["red_seal"] == True and redSealCount < 1:
                    redSealCount += 1
                    redSealFlg = True
        return score