from player import get_remaining_cards

def calculate_win_prob(card, opponent_card, is_player=True):
    remaining = get_remaining_cards(card, opponent_card)
    if is_player:
        wins = sum(1 for c in remaining if c > opponent_card)
    else:
        wins = sum(1 for c in remaining if c < opponent_card)
    return int((wins / len(remaining)) * 100)

def expected_reward(win_prob, max_amount=100):
    return int(max_amount * (1 - win_prob / 100))

def resolve_round(player_card, computer_card, player_bets, player_money, computer_money, player_prob, computer_prob):
    explanation = ""
    round_result = ""

    player_expected = expected_reward(computer_prob)
    computer_expected = expected_reward(player_prob)

    if not player_bets:
        if player_card > computer_card:
            player_money -= computer_expected
            computer_money += computer_expected
            round_result = "베팅하지 않아 판을 내줬습니다."
            explanation = f"상대의 기대 수익 기준 손실: {computer_expected}원\n상대 승리 처리됨"
        elif player_card < computer_card:
            loss = int(player_money / 3)
            player_money -= loss
            computer_money += loss
            round_result = "패배! (베팅 안 함)"
            explanation = f"고정 손실 적용: 보유 자산의 1/3\n감점 금액: {loss}원"
        else:
            round_result = "무승부"
            explanation = "같은 숫자 → 금전 이동 없음"
    else:
        if player_card > computer_card:
            player_money += computer_expected
            computer_money -= computer_expected
            round_result = "승리!"
            explanation = f"상대 기대 손실 기준 수익: {computer_expected}원\n상대는 {player_prob}% 확률로 졌습니다."
        elif player_card < computer_card:
            player_money -= player_expected
            computer_money += player_expected
            round_result = "패배!"
            explanation = f"내 기대 수익 기준 손실: {player_expected}원\n나는 {computer_prob}% 확률로 졌습니다."
        else:
            round_result = "무승부"
            explanation = "같은 숫자 → 금전 이동 없음"

    return player_money, computer_money, round_result, explanation
