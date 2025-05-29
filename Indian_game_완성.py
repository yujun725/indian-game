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

def expected_reward(win_prob, max_amount=100):
    return int(max_amount * (1 - win_prob / 100))

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