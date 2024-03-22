from typing import Any
import pygame
import subprocess
import threading
from time import sleep
import asyncio
from random import randint

player = 0

BotPlaying = True

FlipBoard = False

time_1 = 2
time_2 = 2.5

xshift = 50
yshift = 0

WIDTHBOARD = 800
HEIGHTBOARD = 800

WIDTH = WIDTHBOARD + xshift
HEIGHT = HEIGHTBOARD + yshift

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("StockShark v11.3")
pygame.display.set_icon(pygame.image.load("Images\Icon.png"))

clock = pygame.time.Clock()
FPS = 60

bg = pygame.image.load("Images\Chessboard.png")
P = pygame.image.load("Images\WhitePawn.png")
N = pygame.image.load("Images\WhiteKnight.png")
B = pygame.image.load("Images\WhiteBishop.png")
R = pygame.image.load("Images\WhiteRook.png")
Q = pygame.image.load("Images\WhiteQueen.png")
K = pygame.image.load("Images\WhiteKing.png")
p = pygame.image.load("Images\BlackPawn.png")
n = pygame.image.load("Images\BlackKnight.png")
b = pygame.image.load("Images\BlackBishop.png")
r = pygame.image.load("Images\BlackRook.png")
q = pygame.image.load("Images\BlackQueen.png")
k = pygame.image.load("Images\BlackKing.png")

new_size = (WIDTHBOARD / 8, HEIGHTBOARD / 8)

bg = pygame.transform.scale(bg, (WIDTHBOARD, HEIGHTBOARD))
P = pygame.transform.scale(P, new_size)
N = pygame.transform.scale(N, new_size)
B = pygame.transform.scale(B, new_size)
R = pygame.transform.scale(R, new_size)
Q = pygame.transform.scale(Q, new_size)
K = pygame.transform.scale(K, new_size)
p = pygame.transform.scale(p, new_size)
n = pygame.transform.scale(n, new_size)
b = pygame.transform.scale(b, new_size)
r = pygame.transform.scale(r, new_size)
q = pygame.transform.scale(q, new_size)
k = pygame.transform.scale(k, new_size)

ChooseColor = pygame.image.load("Images\ChooseColor.png")
ChooseColor = pygame.transform.scale(ChooseColor, (ChooseColor.get_size()[0] / 2, ChooseColor.get_size()[1] / 2))


capture_sound = pygame.mixer.Sound("SFX/capture.mp3")
castle_sound = pygame.mixer.Sound("SFX/castle.mp3")
gameEnd_sound = pygame.mixer.Sound("SFX/game-end.mp3")
gameStart_sound = pygame.mixer.Sound("SFX/game-start.mp3")
illegal_sound = pygame.mixer.Sound("SFX/illegal.mp3")
moveCheck_sound = pygame.mixer.Sound("SFX/move-check.mp3")
moveOpponent_sound = pygame.mixer.Sound("SFX/move-opponent.mp3")
moveSelf_sound = pygame.mixer.Sound("SFX/move-self.mp3")
notify_sound = pygame.mixer.Sound("SFX/notify.mp3")
premove_sound = pygame.mixer.Sound("SFX/premove.mp3")
promote_sound = pygame.mixer.Sound("SFX/promote.mp3")
tenseconds_sound = pygame.mixer.Sound("SFX/tenseconds.mp3")

font = pygame.font.SysFont("ebrima", 17, bold = True)

gameend = False

def show_legals(i, j):
    global legal_moves, legal_moves_draw
    for move in legal_moves:
        if (i, j) == (7 - ((move >> 3) & 7), move & (7)):
            legal_moves_draw[7 - (move >> 9) & 7][((move >> 6) & 7)] = 1 if position[0][move & 63] % 6 != 0 else 2

def hide_legals():
    global legal_moves_draw
    legal_moves_draw = [[0 for _ in range(8)] for _ in range(8)]

def Legal_moves(position):
    if gameend:
        return []
    FEN = position_to_FEN(position)
    process = subprocess.Popen(["main.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

    process.stdin.write(FEN + "\nlm\n")
    process.stdin.close()

    legals = []

    while True:
        output = process.stdout.readline().rstrip()
        if output != "" and output != FEN:
            legals.append(int(output))

        if process.poll() is not None:
            break
    process.terminate()
    return legals

def Check(position):
    FEN = position_to_FEN(position)
    process = subprocess.Popen(["main.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

    process.stdin.write(FEN + "\nck\n")
    process.stdin.close()

    check = False

    while True:
        output = process.stdout.readline().rstrip()
        if output != "" and output != FEN:
            check = output == '1'

        if process.poll() is not None:
            break
    process.terminate()
    return check

def position_to_FEN(position):
    global history
    FEN = "" #rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0
    pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    empty_squares = 0
    for i in range(7, -1, -1):
        for j in range(8):
            if position[0][i * 8 + j] == -1 or position[0][i * 8 + j] == 12:
                empty_squares += 1
            else:
                if empty_squares > 0:
                    FEN += str(empty_squares)
                    empty_squares = 0
                FEN += pieces[position[0][i * 8 + j]]
        if empty_squares > 0:
            FEN += str(empty_squares)
            empty_squares = 0
        if i != 0:
            FEN += '/'
    
    if position[1][0] == 1:
        FEN += ' w '
    else:
        FEN += ' b '
    
    if position[1][1]: FEN += 'K'
    if position[1][2]: FEN += 'Q'
    if position[1][3]: FEN += 'k'
    if position[1][4]: FEN += 'q'
    
    if max(position[1][1], position[1][2], position[1][3], position[1][4]) == 0:
        FEN += '-'

    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    en = -1
    for i in range(64):
        if position[0][i] == 12:
            en = i
            break
    
    if en == -1:
        FEN += ' - '
    else:
        FEN += f' {letters[en % 8]}{en // 8 + 1} '
    
    FEN += str(position[1][5])
    FEN += f' {(len(history) - 1) // 2 + 1}'

    return FEN


async def go_time(t1, t2):
    global rate
    FEN = position_to_FEN(position_start)
    process = subprocess.Popen(["main.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    request = FEN + "\ngo time " + str(t1) + " " + str(t2) + "\n"
    for i in history[1:]:
        request += str(i[1]) + "\n"
    request += "-1\n"
    process.stdin.write(request)
    process.stdin.close()
    while True:
        sleep(0.1)
        output = process.stdout.readline().rstrip()
        if output != "" and output != FEN:
            rate = list(map(int, output.split()))
            process.terminate()
            return


async def go_infinity():
    global RateOfPosition
    FEN = position_to_FEN(position_start)
    global rating_process
    rating_process = subprocess.Popen(["main.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    request = FEN + "\ngo infinity \n"
    for i in history[1:]:
        request += str(i[1]) + "\n"
    request += "-1\n"
    rating_process.stdin.write(request)
    rating_process.stdin.close()
    while True:
        output = rating_process.stdout.readline().rstrip()
        if output != "" and output != FEN:
            RateOfPosition = list(map(int, output.split()))[0]
        if rating_process.poll() is not None:
            return


def notEnoughtPiece():
    global position
    cnt = [0 for _ in range(12)]
    for i in range(12):
        cnt[i] = position[0].count(i)
    c = sum(cnt)
    
    if cnt[0] or cnt[6]:  return False
    if cnt[3] or cnt[9]:  return False
    if cnt[4] or cnt[10]: return False
    if c <= 3:            return True
    if c >= 5 :           return False
    if cnt[2]+cnt[8]==0:  return False
    if cnt[1]+cnt[7]==0:
        if (position.index(2) % 2) ^ (position.index(8) % 2):
            return False
        else:
            return True


def make_move(move, do_moving):
    global position, is_moving_now, legal_moves, player, pos, images
    tomove = position[1][0] * (-6) + 6
    fr = move & 63
    to = (move >> 6) & 63
    piece = ((move >> 12) & 7) % 6 + tomove
    promotion = (move >> 15) & 7
    if piece == tomove and (to//8 == 0 or to//8 == 7) and promotion == 0:
        promotion = 4
    if promotion != 0:
        promotion += tomove
    en_passing = (piece == tomove) and (position[0][to] == 12)
    capture = (position[0][to] != -1)
    position[0][to] = position[0][fr]
    position[0][fr] = -1
    if en_passing:
        if tomove == 0:
            position[0][to - 8] = -1
            pos[8 - to // 8][to % 8] = 0
        else:
            position[0][to + 8] = -1
            pos[6 - to // 8][to % 8] = 0
    for i in range(64):
        if position[0][i] == 12:
            position[0][i] = -1
    if move == 20868:
        position[0][5] = 3
        position[0][7] = -1
        is_moving_now.append([(7 - 7 // 8) * 100, (7 % 8) * 100, (7 - 7 // 8) * 100, (7 % 8) * 100, (7 - 5 // 8) * 100, (5 % 8) * 100, R])
        pos[7][7] = 0
    if move == 20612:
        position[0][3] = 3
        position[0][0] = -1
        is_moving_now.append([(7 - 0 // 8) * 100, (0 % 8) * 100, (7 - 0 // 8) * 100, (0 % 8) * 100, (7 - 3 // 8) * 100, (3 % 8) * 100, R])
        pos[7][0] = 0
    if move == 24508:
        position[0][61] = 9
        position[0][63] = -1
        is_moving_now.append([(7 - 63 // 8) * 100, (63 % 8) * 100, (7 - 63 // 8) * 100, (63 % 8) * 100, (7 - 61 // 8) * 100, (61 % 8) * 100, r])
        pos[0][7] = 0
    if move == 24252:
        position[0][59] = 9
        position[0][56] = -1
        is_moving_now.append([(7 - 56 // 8) * 100, (56 % 8) * 100, (7 - 56 // 8) * 100, (56 % 8) * 100, (7 - 59 // 8) * 100, (59 % 8) * 100, r])
        pos[0][0] = 0

    
    if (piece == tomove) and abs(fr - to) == 16:
        position[0][(fr + to) // 2] = 12
    
    if promotion:
        position[0][to] = promotion
        pos[7 - to // 8][to % 8] = images[promotion]
    
    if position[0][4] != 5:
        position[1][1] = 0
        position[1][2] = 0
    if position[0][60] != 11:
        position[1][3] = 0
        position[1][4] = 0
    if position[0][7] != 3:
        position[1][1] = 0
    if position[0][0] != 3:
        position[1][2] = 0
    if position[0][63] != 9:
        position[1][3] = 0
    if position[0][56] != 9:
        position[1][4] = 0

    if capture or piece == tomove:
        position[1][5] = 0
    else:
        position[1][5] += 1
    
    position[1][0] ^= 1

    history.append([[[el for el in position[0]], [el for el in position[1][:5]]], fr + (to << 6) + ((piece % 6) << 12) + ((promotion) % 6 << 15)])
    print(position_to_FEN(position))

    global gameend
    
    legal_moves = Legal_moves(position)
    
    if Check(position) and len(legal_moves) == 0:
        gameend = True
    if len(legal_moves) == 0 or history.count([[position[0], position[1][:5]], fr + (to << 6) + ((piece % 6) << 12) + ((promotion) % 6 << 15)]) >= 3 or\
        position[1][5] >= 100 or notEnoughtPiece():
        gameend = True

    rating_process.terminate()
    global thread_rating
    thread_rating.join()
    
    if not gameend:
        thread_rating = threading.Thread(target=asyncio.run, args=(go_infinity(),))
        thread_rating.start()
    
    if Check(position):
        moveCheck_sound.play()
        if len(legal_moves) == 0:
            pygame.time.delay(50)
            gameEnd_sound.play()
    else:
        if capture:
            capture_sound.play()
        elif promotion != 0:
            promote_sound.play()
        elif move == 20868 or move == 20612 or move == 24508 or move == 24252:
            castle_sound.play()
        elif position[1][0] != player:
            moveSelf_sound.play()
        else:
            moveOpponent_sound.play()
        
        if len(legal_moves) == 0 or history.count([[position[0], position[1][:5]], fr + (to << 6) + ((piece % 6) << 12) + ((promotion) % 6 << 15)]) >= 3 or\
            position[1][5] >= 100 or notEnoughtPiece():
            pygame.time.delay(50)
            gameEnd_sound.play()
    if gameend:
        legal_moves = []
    if do_moving:
        pos[7 - fr // 8][fr % 8] = 0
        if promotion != 0: piece = promotion
        is_moving_now.append([(7 - fr // 8) * 100, (fr % 8) * 100, (7 - fr // 8) * 100, (fr % 8) * 100, (7 - to // 8) * 100, (to % 8) * 100, images[piece]])
        
def is_legal(move, figure, promotion = 0):
    global legal_moves
    for el in legal_moves:
        if el == move[1] + ((7 - move[0]) << 3) + (move[3] << 6) + ((7 - move[2]) << 9) + ((figure % 6) << 12) + (promotion << 15):
            return True
        if el == move[1] + ((7 - move[0]) << 3) + (move[3] << 6) + ((7 - move[2]) << 9) + ((figure % 6) << 12) + (4 << 15):
            return True
    return False

pos = [[r, n, b, q, k, b, n, r],
       [p, p, p, p, p, p, p, p],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [P, P, P, P, P, P, P, P],
       [R, N, B, Q, K, B, N, R]]

images = [P, N, B, R, Q, K, p, n, b, r, q, k]

position_start = [[3,  1,  2,  4,  5,  2,  1,  3,
                   0,  0,  0,  0,  0,  0,  0,  0,
                  -1, -1, -1, -1, -1, -1, -1, -1,
                  -1, -1, -1, -1, -1, -1, -1, -1,
                  -1, -1, -1, -1, -1, -1, -1, -1,
                  -1, -1, -1, -1, -1, -1, -1, -1,
                   6,  6,  6,  6,  6,  6,  6,  6,
                   9,  7,  8, 10, 11,  8,  7,  9],

                  [1, 1, 1, 1, 1, 0]]

position = [[_ for _ in position_start[0]], [_ for _ in position_start[1]]]

history = [[position, 0]]

legal_moves = Legal_moves(position)

legal_moves_draw = [[0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

yellow_squares = [[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

is_moving_now = []

flag_mouse_1 = False
flag = 0
flag_calculating = False
frame_flag = False

game_run = True

FEN = ""
rate = [0, 0]
RateOfPosition = 0

async def main():
    global pos, position_start, legal_moves_draw, yellow_squares, is_moving_now, flag_mouse_1, flag, flag_calculating, frame_flag
    global game_run, FEN, rate, legal_moves, images, thread_rating, RateOfPosition, font
    
    cnt = -1
    
    rect_coords = (-1, -1)
    
    while game_run and cnt != 0:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    flag_mouse_1 = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    flag_mouse_1 = False
        screen.fill((38, 37, 34))
        screen.blit(ChooseColor, ChooseColor.get_rect(center=(400 + xshift, 400 + yshift)))
        
        x_m = pygame.mouse.get_pos()[0]
        y_m = pygame.mouse.get_pos()[1]
        
        if flag_mouse_1:
            if 199 <= x_m <= 324 and 359 <= y_m <= 483:
                rect_coords = (136, 346)
                player = 1
                FlipBoard = False
                cnt = 0.7 * FPS
            elif 386 <= x_m <= 511 and 359 <= y_m <= 483:
                rect_coords = (323, 346)
                if randint(0, 1) == 1:
                    player = 1
                    FlipBoard = False
                else:
                    player = 0
                    FlipBoard = True
                cnt = 0.7 * FPS
            elif 573 <= x_m <= 698 and 359 <= y_m <= 483:
                rect_coords = (510, 346)
                player = 0
                FlipBoard = True
                cnt = 0.7 * FPS
            flag_mouse_1 = False
        
        cnt -= 1
        if rect_coords != (-1, -1):
            pygame.draw.rect(screen, (129, 182, 76), (rect_coords[0] + xshift, rect_coords[1] + yshift, 151, 151), 6, 15)
        
        pygame.display.flip()
        
    
    if not game_run:
        pygame.quit()
        return
    
    flag = 0
    h = 0
    bar_moving = [400, 400, 400]
    
    thread_rating = threading.Thread(target=asyncio.run, args=(go_infinity(),))
    thread_rating.start()

    gameStart_sound.play()
    
    while game_run:

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    flag_mouse_1 = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    flag_mouse_1 = False
            
        screen.fill((48, 46, 43))
        screen.blit(bg, (0 + xshift, 0 + yshift))
        for w1 in range(8):
            for w2 in range(8):
                if yellow_squares[w1][w2] != 0:
                    if (w1 + w2) % 2 == FlipBoard:
                        if FlipBoard:
                            pygame.draw.rect(screen, (244, 246, 128), (100 * w2 + xshift, 700 - 100 * w1 + yshift, 100, 100))    
                        else:
                            pygame.draw.rect(screen, (244, 246, 128), (100 * w2 + xshift, 100 * w1 + yshift, 100, 100))
                    else:
                        if FlipBoard:
                            pygame.draw.rect(screen, (187, 204, 68), (100 * w2 + xshift, 700 - 100 * w1 + yshift, 100, 100))
                        else:
                            pygame.draw.rect(screen, (187, 204, 68), (100 * w2 + xshift, 100 * w1 + yshift, 100, 100))
        for w1 in range(8):
            for w2 in range(8):
                if pos[w2][w1] != 0:
                    if FlipBoard:
                        screen.blit(pos[w2][w1], (w1 * 100 + xshift, 700 - w2 * 100 + yshift))
                    else:
                        screen.blit(pos[w2][w1], (w1 * 100 + xshift, w2 * 100 + yshift))
        if frame_flag:
            screen.blit(frame, frame_coords)
            frame_flag = False

        for w1 in range(8):
            for w2 in range(8):
                if legal_moves_draw[w1][w2]:
                    #print(w1, w2, (7 - w2) * 8 + w1, position[0][(7 - w2) * 8 + w1])
                    if position[0][(7 - w1) * 8 + w2] == -1 or (position[0][(7 - w1) * 8 + w2] == 12 and legal_moves_draw[w1][w2] != 2):
                        move = pygame.Surface((100, 100), pygame.SRCALPHA)
                        move.set_alpha(35)
                        pygame.draw.circle(move, pygame.Color(0, 0, 0), (50, 50), 16)
                        if FlipBoard:
                            screen.blit(move, (w2 * 100 + xshift, 700 - w1 * 100 + yshift))
                        else:
                            screen.blit(move, (w2 * 100 + xshift, w1 * 100 + yshift))
                    else:
                        move = pygame.Surface((100, 100), pygame.SRCALPHA)
                        move.set_alpha(35)
                        pygame.draw.circle(move, pygame.Color(0, 0, 0), (50, 50), 50, 8)
                        if FlipBoard:
                            screen.blit(move, (w2 * 100 + xshift, 700 - w1 * 100 + yshift))
                        else:
                            screen.blit(move, (w2 * 100 + xshift, w1 * 100 + yshift))

        if position[1][0] == 1 - player and not gameend and BotPlaying:
            if not flag_calculating:
                legal_moves = []
                rate = [-1, -1]
                flag_calculating = True
                thread = threading.Thread(target=asyncio.run, args=(go_time(time_1, time_2),))
                thread.start()
            elif rate != [-1, -1]:
                flag_calculating = False
                yellow_squares = [[0 for _ in range(8)] for _ in range(8)]
                yellow_squares[7 - ((rate[1] >> 3) & 7)][rate[1] & 7] = 2
                yellow_squares[7 - ((rate[1] >> 9) & 7)][(rate[1] >> 6) & 7] = 2
                print(position_to_FEN(position))
                if (flag == 1 or flag == 3) and (7 - ((rate[1] >> 3) & 7), rate[1] & 7) == (i, j):
                    if (7 - ((rate[1] >> 3) & 7), rate[1] & 7) == (i, j) or \
                    (rate[1] == 20868 and (i, j) == (7, 7)) or \
                    (rate[1] == 20612 and (i, j) == (7, 0)) or \
                    (rate[1] == 24508 and (i, j) == (0, 7)) or \
                    (rate[1] == 24252 and (i, j) == (0, 0)):
                        flag = -1
                        pos[i][j] = chosen_figure
                make_move(rate[1], True)
                print("rate:", rate[0] / 100)
        
        delete_movings = []
        for moving in is_moving_now:
            speed_x = (moving[4] - moving[0]) / (0.07 * FPS)
            speed_y = (moving[5] - moving[1]) / (0.07 * FPS)
            moving[2] += speed_x
            moving[3] += speed_y
            if ((moving[0] <= moving[2]) ^ (moving[2] <= moving[4])) or ((moving[1] <= moving[3]) ^ (moving[3] <= moving[5])):
                moving[2] = moving[4]
                moving[3] = moving[5]
                delete_movings.append(moving)
                pos[moving[4] // 100][moving[5] // 100] = moving[6]
            if FlipBoard:
                screen.blit(moving[6], (moving[3] + xshift, 700 - moving[2] + yshift))
            else:
                screen.blit(moving[6], (moving[3] + xshift, moving[2] + yshift))
        for moving in delete_movings:
            is_moving_now.remove(moving)
        
        h_old = h
        
        absRate = abs(RateOfPosition)
        
        if RateOfPosition > -5:
            sign = 1
        else:
            sign = -1
        
        if absRate > 500000:
            h = 400
        elif absRate > 390:
            h = 360
        else:
            h = absRate * 12 / 13
        
        h *= -1 * sign
        
        if h_old != h:
            bar_moving = [bar_moving[2], h + 400, bar_moving[2]]
        
        bar_moving[2] += (bar_moving[1] - bar_moving[0]) / (1 * FPS)
        
        if ((bar_moving[0] <= bar_moving[2]) ^ (bar_moving[2] <= bar_moving[1])):
            bar_moving[2] = bar_moving[1]
        
        if absRate > 500000:
            if gameend:
                if position[1][0] == 0:
                    score = "1-0"
                else:
                    score = "0-1"
            else:
                score = "M" + str((1000001 - absRate) // 2)
        elif absRate >= 950:
            score = str((absRate + 50) // 100 * sign)
        else:
            score = str((absRate + 5) // 10 / 10 * sign)

        if FlipBoard:
            pygame.draw.rect(screen, WHITE, (xshift - 50, yshift, 40, 800))
            pygame.draw.rect(screen, (64, 61, 57), (xshift - 50, 801 - yshift - bar_moving[2], 40, bar_moving[2] + 1))
        else:
            pygame.draw.rect(screen, WHITE, (xshift - 50, yshift, 40, 800))
            pygame.draw.rect(screen, (64, 61, 57), (xshift - 50, yshift, 40, bar_moving[2]))
        
        if sign == 1:
            text = font.render(score, True, (64, 61, 57))
            if FlipBoard:
                screen.blit(text, text.get_rect(center = (xshift - 30, 20 + yshift)))
            screen.blit(text, text.get_rect(center = (xshift - 30, 780 + yshift)))
        else:
            text = font.render(score, True, WHITE)
            if FlipBoard:
                screen.blit(text, text.get_rect(center = (xshift - 30, 780 + yshift)))
            else:
                screen.blit(text, text.get_rect(center = (xshift - 30, 20 + yshift)))
        
        x_m = pygame.mouse.get_pos()[0] - xshift
        y_m = pygame.mouse.get_pos()[1] - yshift
        if x_m < 0:
            x_m = 0
        if x_m >= 800:
            x_m = 799
        if y_m < 0:
            y_m = 0
        if y_m >= 800:
            y_m = 799
        x = y_m // 100
        y = x_m // 100
        
        if FlipBoard:
            x = 7 - x

        if flag_mouse_1:
            if pos[x][y] == 0 and flag == 0:
                flag = -1
            if flag == 0:
                flag = 1
                i = x
                j = y
                show_legals(i, j)
                if (yellow_squares[i][j] == 0): yellow_squares[i][j] = 1
                chosen_figure = pos[i][j]
                pos[i][j] = 0
            if flag == 1:
                show_legals(i, j)
                frame = pygame.Surface((100, 100), pygame.SRCALPHA)
                frame.set_alpha(150)
                pygame.draw.rect(frame, pygame.Color(255, 255, 255), (0, 0, 100, 100), 5)
                frame_flag = True
                if FlipBoard:
                    frame_coords = (y * 100 + xshift, 700 - x * 100 + yshift)
                else:
                    frame_coords = (y * 100 + xshift, x * 100 + yshift)
                screen.blit(chosen_figure, (x_m - 50 + xshift, y_m - 50 + yshift))
        if flag == -1 and not flag_mouse_1:
            flag = 0
        if flag == 1 and not flag_mouse_1:
            if is_legal([i, j, x, y], position[0][(7 - i) * 8 + j]):
                hide_legals()
                yellow_squares = [[0 for _ in range(8)] for _ in range(8)]
                yellow_squares[i][j] = 2
                yellow_squares[x][y] = 2
                if FlipBoard:
                    screen.blit(chosen_figure, (y * 100, 700 - x * 100))
                else:
                    screen.blit(chosen_figure, (y * 100, x * 100))
                pos[x][y] = chosen_figure
                make_move(j + ((7 - i) << 3) + (y << 6) + ((7 - x) << 9) + ((position[0][(7 - i) * 8 + j] % 6) << 12), False)
                flag = 0
            else:
                if FlipBoard:
                    screen.blit(chosen_figure, (j * 100 + xshift, 700 - i * 100 + yshift))
                else:
                    screen.blit(chosen_figure, (j * 100 + xshift, i * 100 + yshift))
                if (i, j) != (x, y) and Check(position):
                    illegal_sound.play()
                flag = 2
                pos[i][j] = chosen_figure
        if flag == 2 and flag_mouse_1:
            if is_legal([i, j, x, y], position[0][(7 - i) * 8 + j]):
                hide_legals()
                yellow_squares = [[0 for _ in range(8)] for _ in range(8)]
                yellow_squares[i][j] = 2
                yellow_squares[x][y] = 2
                pos[i][j] = 0
                make_move(j + ((7 - i) << 3) + (y << 6) + ((7 - x) << 9) + ((position[0][(7 - i) * 8 + j] % 6) << 12), True)
                flag = -1
            elif (x, y) == (i, j):
                flag = 3
                i = x
                j = y
                chosen_figure = pos[i][j]
                pos[i][j] = 0
            elif pos[x][y] != 0:
                if (yellow_squares[i][j] == 1): yellow_squares[i][j] = 0
                flag = 1
                i = x
                j = y
                chosen_figure = pos[i][j]
                pos[i][j] = 0
                hide_legals()
                if yellow_squares[i][j] == 0: yellow_squares[i][j] = 1
                show_legals(i, j)
            else:
                flag = 0
                hide_legals()
                if (yellow_squares[i][j] == 1): yellow_squares[i][j] = 0
        if flag == 3 and flag_mouse_1:
            show_legals(i, j)
            frame = pygame.Surface((101, 101), pygame.SRCALPHA)
            frame.set_alpha(150)
            pygame.draw.rect(frame, pygame.Color(255, 255, 255), (0, 0, 100, 100), 5)
            frame_flag = True
            if FlipBoard:
                frame_coords = (y * 100 + xshift, 700 - x * 100 + yshift)
            else:
                frame_coords = (y * 100 + xshift, x * 100 + yshift)
            screen.blit(chosen_figure, (x_m - 50 + xshift, y_m - 50 + yshift))
        if flag == 3 and not flag_mouse_1:
            if is_legal([i, j, x, y], position[0][(7 - i) * 8 + j]):
                yellow_squares = [[0 for _ in range(8)] for _ in range(8)]
                yellow_squares[i][j] = 2
                yellow_squares[x][y] = 2
                screen.blit(chosen_figure, (y * 100 + xshift, x * 100 + yshift))
                pos[x][y] = chosen_figure
                make_move(j + ((7 - i) << 3) + (y << 6) + ((7 - x) << 9) + ((position[0][(7 - i) * 8 + j] % 6) << 12), False)
                flag = 0
                hide_legals()
            else:
                if FlipBoard:
                    screen.blit(chosen_figure, (j * 100 + xshift, 700 - i * 100 + yshift))
                else:
                    screen.blit(chosen_figure, (j * 100 + xshift, i * 100 + yshift))
                pos[i][j] = chosen_figure
                if (x, y) != (i, j):
                    if (i, j) != (x, y) and Check(position):
                        illegal_sound.play()
                    flag = 2
                else:
                    flag = 0
                    hide_legals()
                    if (yellow_squares[i][j] == 1) : yellow_squares[i][j] = 0
        delete_movings = []
        pygame.display.flip()

    rating_process.terminate()
    thread_rating.join()
    pygame.quit()
    



asyncio.run(main())