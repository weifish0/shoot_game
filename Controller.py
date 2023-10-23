from tkinter import RIGHT
import pygame as pg
import random
from Config import *
from GameObject import *
from typing import List, Union, Tuple, Sequence

"""
Helper Functions
"""
def is_player_bullet(bullet) -> bool:
    return isinstance(bullet.owner, Player)


def is_enemy_bullet(bullet) -> bool:
    return isinstance(bullet.owner, Enemy)


def enemy_move(enemy: Enemy, movement: Tuple[int, int]) -> None:
    
    """
    依照 movement 來移動敵人位置
    """
    enemy.rect.move_ip(ENEMY_SPEED * pg.Vector2(movement))


def bullet_move(bullet: Bullet) -> bool:
    """
    依照 bullet.speed 來移動子彈位置
    """
    check = in_border_check(bullet.rect, (0, bullet.speed))
    if check:
        bullet.rect.move_ip(0, bullet.speed)

    return check


def in_border_check(rect: pg.Rect, movement: Tuple) -> bool:

    """
    檢查 Rect 在移動後，是否有在螢幕內
    """
    
    # 在螢幕內就 return True，否則 return False
    if rect.right + movement[0] > SCREEN_WIDTH:
        return False
    if rect.left + movement[0] < 0:
        return False
    if rect.top + movement[1] < 0:
        return False
    if rect.bottom + movement[1] > SCREEN_HEIGHT:
        return False
    return True


def check_collision(a: pg.Rect, b: pg.Rect) -> bool:
    """
    檢查兩個 Rect 是否有碰撞發生
    """
    # a 與 b 碰撞就 return True，否則 return False
    # 碰撞檢測好難 QAQ
    if (a.x < b.x + b.width and
    a.x + a.width > b.x and
    a.y < b.y + b.height and
    a.height + a.y > b.y):
        return True
    return False


def player_move(rect: pg.Rect, pressed_keys: Sequence) -> None:
    """
    依照 pressed_keys 來移動玩家位置
    """
    # 依照按鍵調整 movement 變數
    movement = (0, 0)
    if pressed_keys[pg.K_RIGHT]:
        movement = (PLAYER_SPEED,0)
    if pressed_keys[pg.K_LEFT]:
        movement = (-PLAYER_SPEED,0)
    
    # 檢查邊界
    if in_border_check(rect,movement):
        # 移動
        rect.move_ip(movement)

    

def handle_player_shoot(player: Player, bullets: List[Bullet], w_space_count: int, shoot_thres: int) -> Tuple[int, int]:
    """
    處理玩家射擊，並回傳新的 w_space_count, shoot_thres
    射第 n 發需要按下 n 次空白鍵
    """

    # 更新 w_space_count, shoot_thres，若可以射擊則呼叫 player.shoot(bullets)
    w_space_count += 1
    if w_space_count == shoot_thres:
        player.shoot(bullets)
        shoot_thres += 1
        w_space_count = 0
        return w_space_count, shoot_thres
    else:    
        return w_space_count, shoot_thres


# generate bullet from enemies
def enemy_shoot(bullets: List[Enemy], enemies: List[Enemy]) -> None:
    '''
    # 隨機挑選敵人進行射擊
    # 從 enemies 中隨機挑選一個發射子彈，可以呼叫 enemy.shoot(bullets)
    will_shoot_enemy = random.choice(enemies)
    will_shoot_enemy.shoot(bullets)
    '''
    
    '''
    進階: 從每一直行離使用者最近的敵人中隨機挑一個發射
    '''
    player_site = SCREEN_HEIGHT-50
    default_small = SCREEN_HEIGHT
    will_shoot_enemies = []
    for enemy in enemies:
        if abs(player_site - enemy.rect.centery) <= default_small:
            default_small = player_site - enemy.rect.centery
    for enemy in enemies:
        if abs(player_site - enemy.rect.centery) == default_small:
            will_shoot_enemies.append(enemy)
    random.choice(will_shoot_enemies).shoot(bullets)
    
    
def set_enemy_movement_timer(enemies: List[Enemy]) -> None:
    """
    依據剩餘敵人數量，計算敵人移動時間間隔
    以線性的方式調整，最大為 ENEMY_MOVE_TIME_MAX；最小為 ENEMY_MOVE_TIME_MIN，取整數
    """
    # 將下方之 ENEMY_MOVE_TIME_MAX 改為計算新的間隔時間
    delta_y = ENEMY_MOVE_TIME_MAX - ENEMY_MOVE_TIME_MIN
    delta_x = ENEMY_X_COUNT * ENEMY_Y_COUNT
    slope = delta_y / delta_x
    new_time = int(slope * len(enemies) + ENEMY_MOVE_TIME_MIN)
    

    # 設定計時器
    pg.time.set_timer(ENEMYMOVE_EVENT, new_time)


def get_enemy_movement(movements: List[tuple]) -> Tuple[int, int]:
    """
    回傳 movements 的第一個元素，然後將其放入 movements 的最後以達到循環
    """
    # 將下方的 movement 改為 movements 第一個元素，然後使 movements 循環
    movement = movements[0]
    movements.append(movement)
    movements.remove(movement)
    return movement


def detect_bullet_collision(score: int, player: Player, bullets: List[Bullet], enemies: List[Enemy]) -> int:
    """
    檢查玩家子彈碰到敵人 / 敵人子彈碰到玩家，回傳新分數

    如果玩家子彈打到敵人:
    1. 得分 (+ SCORE)
    2. 刪除敵人
    3. 刪除子彈
    4. 更新敵人移動計時器 (待

    如果敵人子彈打到玩家:
    1. 扣除玩家一條命
    2. 刪除子彈
    """
    # 檢查所有子彈是否打到玩家/敵人，並執行相關動作
    # 玩家打敵人
    for bullet in bullets:
        for enemy in enemies:
            if check_collision(bullet.rect,enemy.rect) and is_player_bullet(bullet):
                score += SCORE
                enemies.remove(enemy)
                bullets.remove(bullet)
                set_enemy_movement_timer(enemies)
                
    # 敵人打玩家
    for bullet in bullets:
        if check_collision(bullet.rect,player.rect) and is_enemy_bullet(bullet):
            player.life -= 1
            bullets.remove(bullet)
    # hint: 可以用 is_player_bullet() 跟 is_enemy_bullet() 判斷是誰的子彈

    # 回傳分數
    return score


def game_over(player: Player, enemies: List[Enemy]) -> bool:
    """
    判斷遊戲結束，條件:
    1. 玩家血量 <= 0
    2. 任一敵人觸底
    """
    # 判斷遊戲結束，若結束則回傳 True
    if player.life <= 0:
        return True
    for enemy in enemies:
        if enemy.rect.bottom >= SCREEN_HEIGHT:
            return True
    return False
