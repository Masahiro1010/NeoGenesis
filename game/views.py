from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from .models import GameSession
from django.views.generic.edit import FormView
import random
from .forms import GuessForm, NumberChoiceForm
from .models import GameSession
import json
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .cards import ALL_CARDS
from django.contrib import messages
from django.views.decorators.http import require_POST
from .plus import PlusCardScore
from .effects import EffectsApply
from django.views import View
from django.shortcuts import render
import uuid

class GameSessionCreateView(TemplateView):
    template_name = 'game/start.html'

    def post(self, request, *args, **kwargs):
        # 詳細構造付きの初期デッキ（0〜9）
        default_deck = [
            {
                "number": str(i),
                "effect": None,         # "double", "gold", or None
                "red_seal": False,
                "gold_seal": False
            } for i in range(10)
        ]
        # セッション作成
        game = GameSession.objects.create(
            deck_numbers=default_deck,
            gold=4,
        )
        
        # セッションIDをセッションに保存（1人プレイ用）
        request.session['game_id'] = str(game.id)
        # 次へ（Ante 1へ進む画面は後で作る）
        return redirect('ante_start', ante_num=1)
    
class AnteStartView(TemplateView):
    template_name = 'game/ante_start.html'

    def get(self, request, *args, **kwargs):
        game_id = request.session.get('game_id')
        if not game_id:
            return redirect('game_start')  # セッション切れ時

        try:
            game = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return redirect('game_start')

        ante_num = kwargs.get('ante_num')
        game.gold += 0
        game.save()

        # deck_numbers の中から4枚ランダムに選ぶ（重複なし）
        selected_cards = random.sample(game.deck_numbers, 4)
        # 各カードの数字を文字列に変換して連結（例: 1, 2, 3, 4 → "1234"）
        problem = ''.join(card["number"] for card in selected_cards)

        # セッションに保存
        if 'problems' not in request.session:
            request.session['problems'] = {}

        problems = request.session['problems']
        problems[str(ante_num)] = problem
        request.session['problems'] = problems

        context = self.get_context_data(**kwargs)
        context['game'] = game
        context['ante_num'] = ante_num
        context['problem'] = problem  # デバッグ時にテンプレートでも確認可能

        return self.render_to_response(context)
    
class GuessView(View):
    template_name = 'game/guess.html'
    form_class = GuessForm

    def post(self, request, *args, **kwargs):
        ante_num = str(self.kwargs['ante_num'])
        guess = request.POST.get('guess')
        indexes = self.request.POST.get('indexes')      # 例: '0246'
        index_list = list(indexes) if indexes else []   # → ['0', '2', '4', '6']
        request = self.request
        game_id = request.session.get("game_id")
        game = get_object_or_404(GameSession, id=game_id)

        if not guess or len(guess) != 4:
            messages.error(request, "4桁の数字を入力してください。")
            return redirect("guess_start", ante_num=ante_num)

        # 問題の取得
        problem_dict = request.session.get('problems', {})
        problem = problem_dict.get(ante_num)
        """
        if not problem:
            form.add_error(None, "問題が見つかりません。")
            return self.form_invalid(form)
        """

        # Hit & Blow 判定
        hit = 0
        blow = 0
        judge_HBN = ["N"] * len(guess)  # 判定済みのインデックスを管理
        used_indices_in_problem = [False] * len(problem)
        used_indices_in_guess = [False] * len(guess)

        # Step 1: Hit の判定
        for i in range(len(guess)):
            if guess[i] == problem[i]:
                hit += 1
                used_indices_in_problem[i] = True
                used_indices_in_guess[i] = True
                judge_HBN[i] = "H"  # Hit 判定済み

        # Step 2: Blow の判定
        for i in range(len(guess)):
            if used_indices_in_guess[i]:
                continue
            for j in range(len(problem)):
                if not used_indices_in_problem[j] and guess[i] == problem[j]:
                    blow += 1
                    used_indices_in_problem[j] = True
                    judge_HBN[i] = "B"  # Blow 判定済み
                    break

        # 役点の計算
        def calculate_score(hit, blow):
            score_table = {
                (0, 0): 2, (0, 1): 3, (1, 0): 3,
                (0, 2): 5, (1, 1): 5, (2, 0): 7,
                (0, 3): 11, (1, 2): 11, (2, 1): 13,
                (3, 0): 17, (0, 4): 19, (1, 3): 19,
                (2, 2): 23, (4, 0): 29
            }
            return score_table.get((hit, blow), 0)

        yaku_score = calculate_score(hit, blow)
        card_score = 1
        card_score = PlusCardScore.JokerJudge(
            card_score,
            game.joker_slots,
            judge_HBN,
            guess,
            game.deck_numbers,
            ) # ジョーカー効果の適用
        card_score = PlusCardScore.StrongerJudge(
            card_score,
            game.deck_numbers,
            judge_HBN,
            index_list,
            game
        )
        print(problem)
        total_score = yaku_score * card_score

        # 結果をセッションに保存
        if 'results' not in request.session:
            request.session['results'] = {}
        if ante_num not in request.session['results']:
            request.session['results'][ante_num] = []

        request.session['results'][ante_num].append({
            'guess': guess,
            'hit': hit,
            'blow': blow,
            'yaku_score': yaku_score,
            'card_score': card_score,
            'total_score': total_score
        })
        request.session.modified = True
        game.save()

        # 5回目の予想でショップに進む
        if len(request.session['results'][ante_num]) >= 5:
            game_id = request.session.get('game_id')
            if not game_id:
                return redirect('game_start')
            game = GameSession.objects.get(id=game_id)
            # ✅ アンティー番号を1つ進める
            game.current_ante_number += 1
            game.gold += 10  # 所持金を10プラス
            game.save()
            total_ante_score = sum(r['total_score'] for r in request.session['results'][ante_num])
            if 'scores' not in request.session:
                request.session['scores'] = {}
            request.session['scores'][ante_num] = total_ante_score
            return redirect('score_summary', ante_num=ante_num)

        return redirect('guess_start', ante_num=self.kwargs['ante_num'])

    def get(self, request, *args, **kwargs):
        ante_num = str(kwargs['ante_num'])
        results = request.session.get('results', {}).get(ante_num, [])
        return render(request, 'game/guess.html', {
            'ante_num': ante_num,
            'results': results
        })

@require_POST
def reset_game(request):
    request.session.flush()  # セッションをすべて削除（cookieも変更）
    return redirect('game_start')

class ScoreSummaryView(TemplateView):
    template_name = 'game/score_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ante_num = str(self.kwargs['ante_num'])
        results = self.request.session.get('results', {}).get(ante_num, [])

        total_score = sum(r.get('total_score', 0) for r in results)

        context['ante_num'] = ante_num
        context['results'] = results
        context['total_score'] = total_score

        # スコア保存
        scores = self.request.session.get('scores', {})
        scores[ante_num] = total_score
        self.request.session['scores'] = scores
        self.request.session.modified = True

        return context
    
class ShopView(TemplateView):
    template_name = 'game/shop.html'

    def get(self, request, *args, **kwargs):
        game_id = request.session.get('game_id')
        if not game_id:
            return redirect('game_start')

        game = get_object_or_404(GameSession, id=game_id)
        ante_num = str(game.current_ante_number)

        shop_data = game.shop_data.get(ante_num)
        if not shop_data:
            shop_data = self.generate_shop_data()
            game.shop_data[ante_num] = shop_data
            game.save()

        # 所持しているカードコード一覧
        owned_codes = set(game.joker_slots + game.consume_slots)

        # カード購入候補（すでに買ったカードは除く）
        random_cards = [
            ALL_CARDS[code]
            for code in shop_data["cards"]
            if code not in owned_codes
        ]

        # パック購入候補（同じkindのパックは1回限りにする想定）
        # たとえば `game.shop_data['purchased_packs'] = ['tarot', 'joker']` などで保存していた場合
        purchased_kinds = game.shop_data.get("purchased_packs", [])
        pack_options = [
            pack for pack in shop_data["packs"]
            if pack["kind"] not in purchased_kinds
        ]

        # 使用可能な強化カード（tarot / spectral）
        enhancement_cards = [
            ALL_CARDS[code]
            for code in game.consume_slots
            if ALL_CARDS[code].kind in ['tarot', 'spectral']
        ]

        context = self.get_context_data(**kwargs)
        context.update({
            'gold': game.gold,
            'random_cards': random_cards,
            'pack_options': pack_options,
            'next_ante_num': game.current_ante_number,
            'enhancement_cards': enhancement_cards,
        })
        return self.render_to_response(context)
    
    def generate_shop_data(self):
        # ランダムカード2枚
        random_cards = random.sample(
            [c for c in ALL_CARDS.values() if c.kind in ['joker', 'spectral', 'tarot', 'item']],
            2
        )

        # パック2種（ランダム）
        pack_kinds = ['joker', 'tarot', 'spectral', 'item']
        pack_options = []
        for kind in random.sample(pack_kinds, 2):
            cards_of_kind = [c for c in ALL_CARDS.values() if c.kind == kind]
            card_pool = random.sample(cards_of_kind, 3 if kind in ['tarot', 'item'] else 5)
            pack_options.append({
                'kind': kind,
                'codes': [card.code for card in card_pool],
                'price': 3 if kind in ['tarot', 'item'] else 6,
                'select_count': 1 if kind in ['tarot', 'item'] else 2,
            })

        return {
            'cards': [card.code for card in random_cards],
            'packs': pack_options
        }
    
@require_POST
def reroll_shop_view(request):
    game_id = request.session.get("game_id")
    game = get_object_or_404(GameSession, id=game_id)
    ante_num = str(game.current_ante_number)

    # 該当アンティーのショップデータ削除
    if ante_num in game.shop_data:
        del game.shop_data[ante_num]

    game.save()
    return redirect("shop", ante_num=game.current_ante_number)
    
@require_POST
def buy_card_view(request):
    code = request.POST.get("code")
    card = ALL_CARDS.get(code)
    if not card:
        messages.error(request, "カードが存在しません。")
        return redirect("shop", ante_num=1)

    game_id = request.session.get("game_id")
    game = get_object_or_404(GameSession, id=game_id)
    ante_num = game.current_ante_number

    if game.gold < card.price:
        messages.error(request, "所持金が足りません。")
        return redirect("shop", ante_num=ante_num)

    if card.kind == "joker":
        if len(game.joker_slots) >= 3:
            messages.warning(request, f"スロット上限で {card.name} は登録できませんでした。")
            return redirect("shop", ante_num=ante_num)
        else:
            game.joker_slots.append(code)
    else:
        if len(game.consume_slots) >= 3:
            messages.warning(request, f"スロット上限で {card.name} は登録できませんでした。")
            return redirect("shop", ante_num=ante_num)
        else:
            game.consume_slots.append(code)

    game.gold -= card.price

    # ✅ ショップリスト（このアンティー）の中から購入カードを削除
    ante_key = str(ante_num)
    if ante_key in game.shop_data:
        if "cards" in game.shop_data[ante_key]:
            if code in game.shop_data[ante_key]["cards"]:
                game.shop_data[ante_key]["cards"].remove(code)

    game.save()

    messages.success(request, f"{card.name} を購入しました。")
    return redirect("shop", ante_num=ante_num)

@require_POST
def buy_pack_view(request):
    selected_kind = request.POST.get("kind")
    price = int(request.POST.get("price"))

    game_id = request.session.get("game_id")
    game = get_object_or_404(GameSession, id=game_id)
    ante_num = game.current_ante_number

    # ショップデータから該当パックを取得
    ante_key = str(ante_num)
    shop_data = game.shop_data.get(ante_key, {})
    pack = next((p for p in shop_data.get("packs", []) if p["kind"] == selected_kind), None)

    if not pack:
        messages.error(request, "パックが見つかりません。")
        return redirect("shop", ante_num=ante_num)

    if game.gold < price:
        messages.error(request, "所持金が足りません。")
        return redirect("shop", ante_num=ante_num)

    # 所持金減算
    game.gold -= price

    # 購入済みリストに追加
    purchased = game.shop_data.get("purchased_packs", [])
    if selected_kind not in purchased:
        purchased.append(selected_kind)
        game.shop_data["purchased_packs"] = purchased

    game.save()

    # ✅ セッションにパック保存（未開封）
    token = str(uuid.uuid4())
    request.session.modified = True
    pending = request.session.get("pending_packs", {})
    pending[token] = {
        "kind": selected_kind,
        "codes": pack["codes"],
        "select_count": pack["select_count"],
    }
    request.session["pending_packs"] = pending

    return redirect("open_pack", token=token)

class PackOpenView(View):
    def get(self, request, token):
        request.session.modified = True
        request.session.save()  # ← この行が重要
        print("pending_packs:", request.session.get("pending_packs", {}))
        print("checking token:", token)
        pack_data = request.session.get("pending_packs", {}).get(str(token))
        if not pack_data:
            messages.error(request, "このパックはすでに開封済みです。")

            # ✅ game_id から GameSession を取得して、current_ante_number を使う
            game_id = request.session.get("game_id")
            if not game_id:
                return redirect("game_start")
            game = get_object_or_404(GameSession, id=game_id)
            return redirect("shop", ante_num=game.current_ante_number)

        cards = [ALL_CARDS[code] for code in pack_data["codes"]]

        return render(request, "game/pack_open.html", {
            "token": token,
            "cards": cards,
            "select_count": pack_data["select_count"],
        })

    def post(self, request, token):
        selected_codes = request.POST.getlist("selected_codes")
        pack_data = request.session.get("pending_packs", {}).get(str(token))
        if not pack_data:
            messages.error(request, "すでに開封済みか無効なパックです。")

            game_id = request.session.get("game_id")
            if not game_id:
                return redirect("game_start")
            game = get_object_or_404(GameSession, id=game_id)
            return redirect("shop", ante_num=game.current_ante_number)

        if len(selected_codes) > pack_data["select_count"]:
            messages.error(request, f"{pack_data['select_count']}枚選んでください。")
            return redirect("open_pack", token=token)

        # スロット追加処理
        game_id = request.session.get("game_id")
        game = get_object_or_404(GameSession, id=game_id)

        for code in selected_codes:
            card = ALL_CARDS.get(code)
            if not card:
                continue
            if card.kind == "joker":
                if len(game.joker_slots) < 3:
                    game.joker_slots.append(code)
            else:
                if len(game.consume_slots) < 3:
                    game.consume_slots.append(code)

        game.save()

        # ✅ このパックは開封済みとして削除
        request.session["pending_packs"].pop(token, None)
        request.session.modified = True

        messages.success(request, "カードを取得しました。")
        return redirect("shop", ante_num=game.current_ante_number)


@require_POST
def use_item_card_view(request):
    code = request.POST.get("code")
    game_id = request.session.get("game_id")

    if not code or not game_id:
        messages.error(request, "セッションまたはコードが無効です。")
        return redirect("game_start")

    game = get_object_or_404(GameSession, id=game_id)

    # 判定系アイテムなら → 特別な選択画面に遷移
    if code in ["item_highlow", "item_evenodd"]:
        if code not in game.consume_slots:
            messages.error(request, "このカードは使用できません。")
            return redirect("guess_start", ante_num=game.current_ante_number)

        request.session["pending_card"] = code  # カードコードをセッションに記録
        return redirect("card_select_numbers", ante_num=game.current_ante_number)

    # その他の item カード → 通常処理へ
    request.POST = request.POST.copy()
    request.POST["code"] = code
    return _use_card_common(request, card_type="item", redirect_name="guess_start")

@require_POST
def use_tarot_card_view(request):
    code = request.POST.get("code")
    game = get_object_or_404(GameSession, id=request.session.get("game_id"))

    card = ALL_CARDS.get(code)
    if not card or card.kind != "tarot":
        messages.error(request, "無効なカードです。")
        return redirect("shop", ante_num=game.current_ante_number)

    if card.code == "tarot_gold" or card.code == "tarot_steel" or card.code == "tarot_buff":
        # ✅ 数字選択ページへ誘導
        request.session["waiting_card_effect"] = {"code": code}
        return redirect("select_number")
    
    return _use_card_common(request, card_type="tarot", redirect_name="shop", game=game, code=code)


@require_POST
def use_spectral_card_view(request):
    code = request.POST.get("code")
    game = get_object_or_404(GameSession, id=request.session.get("game_id"))

    card = ALL_CARDS.get(code)
    if not card or card.kind != "spectral":
        messages.error(request, "無効なカードです。")
        return redirect("shop", ante_num=game.current_ante_number)

    if card.code == "spectral_change" or card.code == "spectral_red" or card.code == "spectral_gold" or card.code == "spectral_trim":
        # ✅ 数字選択ページへ誘導
        request.session["waiting_card_effect"] = {"code": code}
        return redirect("select_number")
    
    return _use_card_common(request, card_type="spectal", redirect_name="shop", game=game, code=code)

def _use_card_common(request, card_type, redirect_name, game=None, code=None):

    if code not in game.consume_slots:
        messages.error(request, "このカードは使用できません。")
        return redirect(redirect_name, ante_num=game.current_ante_number)

    card = ALL_CARDS.get(code)
    if not card or card.kind != card_type:
        messages.error(request, "カード種別が一致しません。")
        return redirect(redirect_name, ante_num=game.current_ante_number)

    # 効果の適用（効果文言を返すようにする）
    effect_text = EffectsApply.apply_card_effect(game, card)
    # 使用済みとして削除
    game.consume_slots.remove(code)
    game.save()
    messages.success(request, f"{card.name} を使用：{effect_text}")
    return redirect(redirect_name, ante_num=game.current_ante_number)

@method_decorator(csrf_protect, name='dispatch')
class SelectNumberView(FormView):
    template_name = 'game/select_number.html'
    form_class = NumberChoiceForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        game_id = request.session.get("game_id")
        game = get_object_or_404(GameSession, id=game_id)

        context["deck_numbers"] = game.deck_numbers
        return context

    def form_valid(self, form):
        number = form.cleaned_data['number']
        index = int(self.request.POST.get("index", -1))  # ← 追加（存在しない場合は -1）

        request = self.request
        game_id = request.session.get("game_id")
        game = get_object_or_404(GameSession, id=game_id)

        effect = request.session.get("waiting_card_effect", {})
        code = effect.get("code")
        card = ALL_CARDS.get(code)

        if not card or index < 0 or index >= len(game.deck_numbers):
            messages.error(request, "カード情報またはインデックスが不正です。")
            return redirect("shop", ante_num=game.current_ante_number)

        target_card = game.deck_numbers[index]
        if str(target_card["number"]) != str(number):
            messages.warning(request, "数字とインデックスの整合性に注意してください。")
        
        # 効果付与
        if code == "tarot_gold":
            target_card["effect"] = "gold"
            messages.success(request, f"{number} をゴールドカードにしました！")
        elif code == "tarot_steel":
            target_card["effect"] = "steel"
            messages.success(request, f"{number} にスチール効果を設定しました！")
        elif code == "tarot_buff":
            target_card["effect"] = "buff"
            messages.success(request, f"{number} にカード点アップ効果を付与しました！")
        elif code == "spectral_red":
            target_card["red_seal"] = True
            messages.success(request, f"{number} にレッドシールを付与しました！")
        elif code == "spectral_gold":
            target_card["gold_seal"] = True
            messages.success(request, f"{number} にゴールドシールを付与しました！")
        elif code == "spectral_trim":
            del game.deck_numbers[index]
            messages.success(request, f"{number} をデッキから削除しました！")

        # カード削除・保存
        if code in game.consume_slots:
            game.consume_slots.remove(code)
        game.save()

        # セッション情報クリア
        request.session.pop("waiting_card_effect", None)

        return redirect("shop", ante_num=game.current_ante_number)
    
class ItemCardSelectView(View):
    template_name = "game/item_card_select.html"

    def get(self, request, ante_num):
        problem_dict = request.session.get("problems", {})
        problem = problem_dict.get(str(ante_num))
        if not problem:
            messages.error(request, "問題が見つかりません")
            return redirect("guess_start", ante_num=ante_num)
        return render(request, self.template_name, {
            "ante_num": ante_num,
            "problem_length": len(problem),
        })

    def post(self, request, ante_num):
        game_id = request.session.get("game_id")
        game = get_object_or_404(GameSession, id=game_id)
        code = request.session.get("pending_card")
        problem = request.session.get("problems", {}).get(str(ante_num))

        indexes = request.POST.getlist("indexes")  # ['1', '3'] など
        if len(indexes) != 2:
            messages.error(request, "2つ選んでください")
            return redirect("card_select_numbers", ante_num=ante_num)

        indexes = list(map(int, indexes))
        revealed = [problem[i] for i in indexes]

        if code == "item_evenodd":
            texts = [f"{i+1}番目：{'偶数' if int(d)%2==0 else '奇数'}" for i,d in zip(indexes, revealed)]
        elif code == "item_highlow":
            texts = [f"{i+1}番目：{'0〜4' if int(d)<=4 else '5〜9'}" for i,d in zip(indexes, revealed)]
        else:
            texts = ["不明な効果です"]

        # 消費処理
        game.consume_slots.remove(code)
        game.save()
        del request.session["pending_card"]

        return render(request, self.template_name, {
            "ante_num": ante_num,
            "problem_length": len(problem),
            "revealed_texts": texts,
            "revealed_indexes": indexes,
        })