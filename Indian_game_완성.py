import pygame
import sys
import random

pygame.init()
pygame.font.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("확률 기반 인디언 포커")

# 타이틀 배경 이미지
background = pygame.image.load("배경1차.png")
title_background = pygame.image.load("타이틀1차.png").convert_alpha()
title_background = pygame.transform.smoothscale(title_background, (700, 450))

# 카드 앞뒤 이미지
CARD_WIDTH, CARD_HEIGHT = 120, 180
card_back_img = pygame.image.load("카드_뒤.png").convert_alpha()
card_back_img = pygame.transform.scale(card_back_img, (CARD_WIDTH, CARD_HEIGHT))

card_front_img = pygame.image.load("카드_앞.png").convert_alpha()
card_front_img = pygame.transform.scale(card_front_img, (CARD_WIDTH, CARD_HEIGHT))

# 카드 애니메이션
flipping = False
flip_progress = 0
flip_speed = 0.05

# 결과화면 이미지
result_win_img = pygame.image.load("승리.png").convert_alpha()
result_lose_img = pygame.image.load("패배.png").convert_alpha()
result_draw_img = pygame.image.load("무승부.png").convert_alpha()

result_win_img = pygame.transform.scale(result_win_img, (400, 270))
result_lose_img = pygame.transform.scale(result_lose_img, (400, 270))
result_draw_img = pygame.transform.scale(result_draw_img, (400, 270))

clock = pygame.time.Clock()
font = pygame.font.SysFont("nanumgothicextrabold", 28)
small_font = pygame.font.SysFont("nanumgothicbold", 22)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 70, 20)
BLUE = (3, 154, 255)
GRAY = (160, 160, 160)

player_money = 1000
computer_money = 1000
player_card = None
computer_card = None
player_prob = 0
computer_prob = 0
round_result = ""
betting_done = False
player_bets = False
explanation = ""
final_result = ""
money_change_text = ""
money_change_alpha = 0
money_change_timer = 0

deck = [i for i in range(1, 10) for _ in range(2)]
random.shuffle(deck)

def draw_card(x, y, value=None, flipping=False, flip_progress=0.0):
    # 카드 애니메이션
    if flipping:
        if flip_progress <= 0.5:
            scale = 1 - (flip_progress * 2)
            show_front = False
        else:
            scale = (flip_progress - 0.5) * 2
            show_front = True
    else:
        scale = 1.0
        show_front = value is not None

    width = max(1, int(CARD_WIDTH * scale))

    if show_front:
        img = card_front_img.copy()
        if value is not None:
            text = font.render(str(value), True, BLACK)
            text_rect = text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
            img.blit(text, text_rect)
    else:
        img = card_back_img.copy()

    scaled_img = pygame.transform.scale(img, (width, CARD_HEIGHT))
    screen.blit(scaled_img, (x + (CARD_WIDTH - width) // 2, y))

def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=5)
    label = small_font.render(text, True, BLACK)
    label_rect = label.get_rect(center = (x + w // 2, y + h // 2))
    screen.blit(label, label_rect)
    return pygame.Rect(x, y, w, h)

def get_remaining_cards():
    full_deck = [i for i in range(1, 10) for _ in range(2)]
    used = [player_card, computer_card]
    for c in used:
        full_deck.remove(c)
    return full_deck

def calculate_player_win_prob(computer_card):
    remaining = get_remaining_cards()
    wins = sum(1 for c in remaining if c > computer_card)
    return int((wins / len(remaining)) * 100)

def calculate_computer_win_prob(player_card):
    remaining = get_remaining_cards()
    wins = sum(1 for c in remaining if c > player_card)
    return int((wins / len(remaining)) * 100)

def expected_reward(win_prob):
    # 승리 확률에 따른 금액 이동
    if 0 <= win_prob < 20:
        return 200
    elif 20 <= win_prob < 40:
        return 150
    elif 40 <= win_prob < 60:
        return 100
    elif 60 <= win_prob < 80:
        return 60
    elif 80 <= win_prob <= 100:
        return 30
    return 0

def deal_cards():
    global player_card, computer_card, player_prob, computer_prob
    global round_result, betting_done, player_bets, explanation

    player_card = deck.pop()
    computer_card = deck.pop()
    player_prob = calculate_player_win_prob(computer_card)
    computer_prob = calculate_computer_win_prob(player_card)
    round_result = ""
    betting_done = False
    player_bets = False
    explanation = ""

game_state = "title"

def draw_title_screen():
    # 타이틀 화면
    screen.blit(background, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(80)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    screen.blit(title_background, (WIDTH // 2 - title_background.get_width() // 2, -50))

    start_btn = draw_button("게임 시작", WIDTH // 2 - 100, 350, 200, 50, BLUE)
    quit_btn = draw_button("게임 종료", WIDTH // 2 - 100, 430, 200, 50, RED)
    return start_btn, quit_btn

def draw_result_screen():
    # 결과 화면
    screen.blit(background, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(80)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    if final_result == "승리":
        screen.blit(result_win_img, (WIDTH // 2 - 200, 60))
    elif final_result == "패배":
        screen.blit(result_lose_img, (WIDTH // 2 - 200, 60))
    else:
        screen.blit(result_draw_img, (WIDTH // 2 - 200, 60))

    restart_btn = draw_button("다시하기", WIDTH // 2 - 100, 350, 200, 50, BLUE)
    quit_btn = draw_button("종료하기", WIDTH // 2 - 100, 430, 200, 50, RED)
    return restart_btn, quit_btn
def resolve_round():
    global player_money, computer_money, round_result, betting_done, explanation
    global flipping, flip_progress, money_change_text, money_change_alpha, money_change_timer

    money_change_text = ""
    money_change_alpha = 255
    money_change_timer = 60

    if not player_bets:
        # 베팅 안 했을 경우
        if player_card > computer_card:
            loss = expected_reward(computer_prob)
            player_money -= loss
            computer_money += loss
            round_result = "베팅하지 않아 판을 내줬습니다."
            money_change_text = f"-{loss}"
        elif player_card < computer_card:
            loss = 50
            player_money -= loss
            computer_money += loss
            round_result = "패배! (베팅 안 함)"
            money_change_text = f"-{loss}"
        else:
            round_result = "무승부!"
    else:
        # 베팅한 경우
        if player_card > computer_card:
            reward = expected_reward(player_prob)
            player_money += reward
            computer_money -= reward
            round_result = "승리!"
            money_change_text = f"+{reward}"
        elif player_card < computer_card:
            loss = expected_reward(computer_prob)
            player_money -= loss
            computer_money += loss
            round_result = "패배!"
            money_change_text = f"-{loss}"
        else:
            round_result = "무승부"

    flipping = True
    flip_progress = 0.0

    betting_done = True

def draw_ui():
    global money_change_alpha, money_change_timer
    screen.blit(font.render(f"내 돈 : {player_money}", True, WHITE), (50, 40))
    screen.blit(font.render(f"상대 돈 : {computer_money}", True, WHITE), (670, 40))

    # 이동 금액 애니메이션
    if money_change_timer > 0:
        if "+" in money_change_text :
            color = BLUE
        elif "-" in money_change_text :
            color = RED
        else :
            color = WHITE
        
        text_surface = font.render(money_change_text, True, color)
        text_surface.set_alpha(money_change_alpha)
        screen.blit(text_surface, (130, 75))

        money_change_timer -= 1
        money_change_alpha = max(0, money_change_alpha - 4)

    # 남은 라운드 표시
    rounds_left = len(deck) // 2
    screen.blit(small_font.render(f"남은 라운드 수 : {rounds_left}", True, WHITE), (360, 30))

    draw_card(240, 190, None if not betting_done else player_card, flipping, flip_progress)
    draw_card(535, 190, computer_card)
    screen.blit(font.render("VS", True, WHITE), (430, 260))
    
    if not betting_done:
        expected_win_amount = expected_reward(player_prob)
        screen.blit(small_font.render(f"승리 시 획득 금액 : {expected_win_amount}원", True, WHITE), (330, 60))

    # 결과 화면 출력
    if betting_done and round_result:
        text = font.render(round_result, True, WHITE)
        text_rect = text.get_rect(center=(240 + CARD_WIDTH // 2, 400))
        screen.blit(text, text_rect)

    for i, line in enumerate(explanation.split("\n")):
        screen.blit(small_font.render(line, True, WHITE), (50, 460 + i * 20))
    if not betting_done:
        return draw_button("베팅하기", 200, 480, 200, 50, BLUE), draw_button("베팅하지 않기", 500, 480, 200, 50, RED)
    else:
        if len(deck) >= 2 :
            return draw_button("다음 라운드", 350, 480, 200, 50, GRAY), None
        else :
            return draw_button("결과 보기", 350, 480, 200, 50, GRAY), None

deal_cards()
running = True
while running:
    if game_state == "title":
        buttons = draw_title_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons[0].collidepoint(event.pos):  # 게임 시작
                    game_state = "playing"
                elif buttons[1].collidepoint(event.pos):  # 게임 종료
                    running = False

    elif game_state == "playing":
        screen.blit(background, (0, 0))
        if flipping :
            flip_progress += flip_speed
            if flip_progress >= 1.0 :
                flip_progress = 0.0
                flipping = False
        buttons = draw_ui()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons:
                    if buttons[0].collidepoint(event.pos):
                        if not betting_done:
                            player_bets = True
                            resolve_round()
                        else:
                            if len(deck) >= 2:
                                deal_cards()
                            else:
                                if player_money > computer_money:
                                    final_result = "승리"
                                elif player_money < computer_money:
                                    final_result = "패배"
                                else:
                                    final_result = "무승부"
                                game_state = "result"
                    elif buttons[1] and buttons[1].collidepoint(event.pos):
                        player_bets = False
                        resolve_round()


    elif game_state == "result":
        buttons = draw_result_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons[0].collidepoint(event.pos):  # 다시하기
                    player_money = 1000
                    computer_money = 1000
                    deck = [i for i in range(1, 10) for _ in range(2)]
                    random.shuffle(deck)
                    deal_cards()
                    game_state = "playing"
                elif buttons[1].collidepoint(event.pos):  # 종료하기
                    running = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
