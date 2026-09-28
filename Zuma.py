import pygame as pg
import math
import random as rd
pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Zuma")
clock = pg.time.Clock()
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),(255,255,255)]
BALLRADIUS = 15
BALL_SPEED = 1 / 50
centerx, centery = WIDTH // 2, HEIGHT // 2
OFFSET = 1
INITIALBALLS = 33
score = 0
SCORE_PERBALL = 10
TARGET_SCORE=2000
blind_timer=0
wormhole_timer=0
EFFECT_TYPES = ['aim', 'slow', 'reverse', 'explode', 'freeze', 'clear_color', 'lightning', 'forward', 'dizzy', 'arrow', 'add_score', 'dye', 'rainbow', 'block', 'rearrange', 'sluggish','blind','wormhole','question']
EFFECT_NAMES = {'aim': 'Aim', 'slow': 'Slow', 'reverse': 'Reverse', 'explode': 'Explode',
    'freeze': 'Freeze', 'clear_color': 'Clear Color', 'lightning': 'Lightning',
    'forward': 'Forward', 'dizzy': 'Dizzy', 'arrow': 'Arrow', 'add_score': 'Add 100 Score',
    'dye': 'Dye', 'rainbow': 'Rainbow', 'block': 'Block', 'rearrange': 'Rearrange',
    'sluggish':'Sluggish','blind':'Blind','question': 'Random','wormhole':'Wormhole'}
effect_spawn_timer = 0
EFFECT_SPAWN_INTERVAL = 150
chain_effect = None
chain_effect_timer = 0
shooter_effect = None
shooter_effect_timer = 0
EFFECT_DURATION = 10 * 60
next_shot_piercing = False
arrow_shots_left = 0
next_shot_dye_color = None
next_shot_rainbow = False
trackpoints = []
theta = 0
r = 280
targetdist = 33
drscale = 220 / math.radians(900)
while r > 60:
    x = centerx + r * math.cos(theta)
    y = centery + r * math.sin(theta)
    trackpoints.append((x, y))
    dtheta = targetdist / r
    theta += dtheta
    r -= drscale * dtheta
holeradius = 40
balls = []
for i in range(INITIALBALLS):
    idx = i * OFFSET
    if idx >= len(trackpoints):
        break
    balls.append({"color": rd.choice(COLORS), "index": idx, "x": trackpoints[idx][0], "y": trackpoints[idx][1],"initial":True})
shooterpos = (centerx, centery)
shooterangle = 0
current_ball_color = rd.choice(COLORS)
flying_balls = []
running = True
win = False
lose = False
start = False
spawned_balls_count = INITIALBALLS
spawn_timer = 0.0
pending_rearrange = False
def check_local_match(center_idx):
    global score, chain_effect, chain_effect_timer, shooter_effect, shooter_effect_timer,blind_timer,wormhole_timer
    global next_shot_piercing, arrow_shots_left, next_shot_dye_color, next_shot_rainbow,pending_rearrange
    if center_idx < 0 or center_idx >= len(balls):
        return
    target_color = balls[center_idx]["color"]
    left = center_idx
    while left - 1 >= 0 and balls[left - 1]["color"] == target_color:
        left -= 1
    right = center_idx
    while right + 1 < len(balls) and balls[right + 1]["color"] == target_color:
        right += 1
    count = right - left + 1
    if count >= 3:
        all_initial = all(balls[k].get("initial", False) for k in range(left, right + 1))
        has_effect = False
        for k in range(left, right + 1):
            if "effect" in balls[k]:
                has_effect = True
                break
        if all_initial and not has_effect:
            return
        all_protected = all(balls[k].get("protected", False) for k in range(left, right + 1))
        if all_protected:
            return
        has_explode = False
        clear_color_target = None
        for k in range(left, right + 1):
            if "effect" in balls[k]:
                eff = balls[k]["effect"]
                if eff == 'explode':
                    has_explode = True
                elif eff == 'clear_color':
                    clear_color_target = balls[k]["color"]
                elif eff == 'lightning':
                    next_shot_piercing = True
                elif eff == 'arrow':
                    arrow_shots_left = 6
                elif eff == 'add_score':
                    score += 100
                elif eff == 'dye':
                    next_shot_dye_color = balls[k]["color"]
                elif eff == 'rainbow':
                    next_shot_rainbow = True
                elif eff in ('slow', 'forward', 'reverse', 'freeze'):
                    chain_effect = eff
                    chain_effect_timer = EFFECT_DURATION
                elif eff in ('aim', 'dizzy', 'block','sluggish'):
                    shooter_effect = eff
                    shooter_effect_timer = EFFECT_DURATION
                elif eff == 'blind':
                    blind_timer = 10 * 60
                elif eff == 'wormhole':
                    wormhole_timer = 10 * 60
                elif eff == 'question':
                    possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                    random_eff = rd.choice(possible_effects)
                    if random_eff == 'explode':
                        has_explode = True
                    elif random_eff == 'clear_color':
                        clear_color_target = balls[k]["color"]
                    elif random_eff == 'lightning':
                        next_shot_piercing = True
                    elif random_eff == 'arrow':
                        arrow_shots_left = 6
                    elif random_eff == 'add_score':
                        score += 100
                    elif random_eff == 'dye':
                        next_shot_dye_color = balls[k]["color"]
                    elif random_eff == 'rainbow':
                        next_shot_rainbow = True
                    elif random_eff == 'rearrange':
                        pending_rearrange = True
                    elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                        chain_effect = random_eff
                        chain_effect_timer = EFFECT_DURATION
                    elif random_eff in ('aim', 'dizzy', 'block','sluggish'):
                        shooter_effect = random_eff
                        shooter_effect_timer = EFFECT_DURATION
                    elif random_eff == 'blind':
                        blind_timer = 10 * 60
                    elif random_eff == 'wormhole':
                        wormhole_timer = 10 * 60
        score += count * SCORE_PERBALL
        min_idx = min(balls[k]["index"] for k in range(left, right + 1))
        for _ in range(count):
            balls.pop(left)
        for b in balls:
            if b["index"] > min_idx:
                b["index"] -= count * OFFSET
                safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                b["x"] = trackpoints[safe_idx][0]
                b["y"] = trackpoints[safe_idx][1]
        if clear_color_target is not None:
            remove_list = [b for b in balls if b["color"] == clear_color_target]
            remove_list.sort(key=lambda b: b["index"], reverse=True)
            for b in remove_list:
                score += SCORE_PERBALL
                current_idx = b["index"]
                balls.remove(b)
                for other in balls:
                    if other["index"] > current_idx:
                        other["index"] -= OFFSET
                        safe_idx = max(0, min(int(round(other["index"])), len(trackpoints) - 1))
                        other["x"] = trackpoints[safe_idx][0]
                        other["y"] = trackpoints[safe_idx][1]
        if has_explode and balls:
            nearest_idx = 0
            min_dist = float('inf')
            for idx, b in enumerate(balls):
                dist = abs(b["index"] - min_idx)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = idx
            remove_indices = []
            for offset in range(-4, 5):
                idx = nearest_idx + offset
                if 0 <= idx < len(balls):
                    remove_indices.append(idx)
            if remove_indices:
                remove_indices.sort(reverse=True)
                for idx in remove_indices:
                    b = balls[idx]
                    if "effect" in b:
                        eff = b["effect"]
                        if eff not in ('explode', 'lightning'):
                            if eff == 'arrow':
                                arrow_shots_left = 6
                            elif eff == 'add_score':
                                score += 100
                            elif eff == 'dye':
                                next_shot_dye_color = b["color"]
                            elif eff == 'rainbow':
                                next_shot_rainbow = True
                            elif eff in ('slow', 'forward', 'reverse', 'freeze'):
                                chain_effect = eff
                                chain_effect_timer = EFFECT_DURATION
                            elif eff in ('aim', 'dizzy', 'block','sluggish'):
                                shooter_effect = eff
                                shooter_effect_timer = EFFECT_DURATION
                            elif eff == 'blind':
                                blind_timer=10*60
                            elif eff == 'wormhole':
                                wormhole_timer = 10 * 60
                            elif eff == 'question':
                                possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                                random_eff = rd.choice(possible_effects)
                                if random_eff == 'add_score':
                                    score += 100
                                elif random_eff == 'rearrange':
                                    pending_rearrange = True
                                elif random_eff == 'lightning':
                                    next_shot_piercing = True
                                elif random_eff == 'arrow':
                                    arrow_shots_left = 6
                                elif random_eff == 'dye':
                                    next_shot_dye_color = b["color"]
                                elif random_eff == 'rainbow':
                                    next_shot_rainbow = True
                                elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                                    chain_effect = random_eff
                                    chain_effect_timer = EFFECT_DURATION
                                elif random_eff in ('aim', 'dizzy', 'block','sluggish'):
                                    shooter_effect = random_eff
                                    shooter_effect_timer = EFFECT_DURATION
                                elif random_eff == 'blind':
                                    blind_timer=10*60
                                elif random_eff == 'wormhole':
                                    wormhole_timer = 10 * 60
                exp_min_idx = min(balls[idx]["index"] for idx in remove_indices)
                score += len(remove_indices) * SCORE_PERBALL
                for idx in remove_indices:
                    balls.pop(idx)
                for b in balls:
                    if b["index"] > exp_min_idx:
                        b["index"] -= len(remove_indices) * OFFSET
                        safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                        b["x"] = trackpoints[safe_idx][0]
                        b["y"] = trackpoints[safe_idx][1]
        clear_matches()
def clear_matches():
    global score, chain_effect, chain_effect_timer, shooter_effect, shooter_effect_timer,blind_timer,wormhole_timer
    global next_shot_piercing, arrow_shots_left, next_shot_dye_color, next_shot_rainbow, pending_rearrange
    combo = 1
    while True:
        found = False
        i = 0
        while i < len(balls):
            j = i
            while j + 1 < len(balls) and balls[j + 1]["color"] == balls[i]["color"]:
                j += 1
            count = j - i + 1
            if count >= 3:
                all_initial = all(balls[k].get("initial", False) for k in range(i, j + 1))
                has_effect = False
                for k in range(i, j + 1):
                    if "effect" in balls[k]:
                        has_effect = True
                        break
                if all_initial and not has_effect:
                    i += 1
                    continue
                all_protected = all(balls[k].get("protected", False) for k in range(i, j + 1))
                if all_protected:
                    i += 1
                    continue
                has_explode = False
                clear_color_target = None
                for k in range(i, j + 1):
                    if "effect" in balls[k]:
                        eff = balls[k]["effect"]
                        if eff == 'explode':
                            has_explode = True
                        elif eff == 'clear_color':
                            clear_color_target = balls[k]["color"]
                        elif eff == 'lightning':
                            next_shot_piercing = True
                        elif eff == 'arrow':
                            arrow_shots_left = 6
                        elif eff == 'add_score':
                            score += 100
                        elif eff == 'dye':
                            next_shot_dye_color = balls[k]["color"]
                        elif eff == 'rainbow':
                            next_shot_rainbow = True
                        elif eff == 'rearrange':
                            pending_rearrange = True
                        elif eff == 'question':
                            possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                            random_eff = rd.choice(possible_effects)
                            if random_eff == 'explode':
                                has_explode = True
                            elif random_eff == 'clear_color':
                                clear_color_target = balls[k]["color"]
                            elif random_eff == 'lightning':
                                next_shot_piercing = True
                            elif random_eff == 'arrow':
                                arrow_shots_left = 6
                            elif random_eff == 'add_score':
                                score += 100
                            elif random_eff == 'dye':
                                next_shot_dye_color = balls[k]["color"]
                            elif random_eff == 'rainbow':
                                next_shot_rainbow = True
                            elif random_eff == 'rearrange':
                                pending_rearrange = True
                            elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                                chain_effect = random_eff
                                chain_effect_timer = EFFECT_DURATION
                            elif random_eff in ('aim', 'dizzy', 'block','sluggish'):
                                shooter_effect = random_eff
                                shooter_effect_timer = EFFECT_DURATION
                            elif random_eff == 'blind':
                                blind_timer=10*60
                            elif random_eff == 'wormhole':
                                wormhole_timer = 10 * 60
                        else:
                            if eff in ('slow', 'forward', 'reverse', 'freeze'):
                                chain_effect = eff
                                chain_effect_timer = EFFECT_DURATION
                            elif eff in ('aim', 'dizzy', 'block','sluggish'):
                                shooter_effect = eff
                                shooter_effect_timer = EFFECT_DURATION
                            elif eff == 'blind':
                                blind_timer=10*60
                            elif eff == 'wormhole':
                                wormhole_timer = 10 * 60
                score += count * SCORE_PERBALL * combo
                combo += 1
                min_idx = min(balls[k]["index"] for k in range(i, j + 1))
                for _ in range(count):
                    balls.pop(i)
                for b in balls:
                    if b["index"] > min_idx:
                        b["index"] -= count * OFFSET
                        safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                        b["x"] = trackpoints[safe_idx][0]
                        b["y"] = trackpoints[safe_idx][1]
                if clear_color_target is not None:
                    remove_list = [b for b in balls if b["color"] == clear_color_target]
                    remove_list.sort(key=lambda b: b["index"], reverse=True)
                    for b in remove_list:
                        score += SCORE_PERBALL * combo
                        current_idx = b["index"]
                        balls.remove(b)
                        for other in balls:
                            if other["index"] > current_idx:
                                other["index"] -= OFFSET
                                safe_idx = max(0, min(int(round(other["index"])), len(trackpoints) - 1))
                                other["x"] = trackpoints[safe_idx][0]
                                other["y"] = trackpoints[safe_idx][1]
                    found = True
                    break
                if has_explode and balls:
                    nearest_idx = 0
                    min_dist = float('inf')
                    for idx, b in enumerate(balls):
                        dist = abs(b["index"] - min_idx)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_idx = idx
                    remove_indices = []
                    for offset in range(-4, 5):
                        idx = nearest_idx + offset
                        if 0 <= idx < len(balls):
                            remove_indices.append(idx)
                    if remove_indices:
                        remove_indices.sort(reverse=True)
                        for idx in remove_indices:
                            b = balls[idx]
                            if "effect" in b:
                                eff = b["effect"]
                                if eff not in ('explode', 'lightning'):
                                    if eff == 'arrow':
                                        arrow_shots_left = 6
                                    elif eff == 'add_score':
                                        score += 100
                                    elif eff == 'dye':
                                        next_shot_dye_color = b["color"]
                                    elif eff == 'rainbow':
                                        next_shot_rainbow = True
                                    elif eff in ('slow', 'forward', 'reverse', 'freeze'):
                                        chain_effect = eff
                                        chain_effect_timer = EFFECT_DURATION
                                    elif eff in ('aim', 'dizzy', 'block','sluggish'):
                                        shooter_effect = eff
                                        shooter_effect_timer = EFFECT_DURATION
                                    elif eff == 'blind':
                                        blind_timer = 10 * 60
                                    elif eff == 'wormhole':
                                        wormhole_timer = 10 * 60
                                    elif eff == 'question':
                                        possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                                        random_eff = rd.choice(possible_effects)
                                        if random_eff == 'add_score':
                                            score += 100
                                        elif random_eff == 'rearrange':
                                            pending_rearrange = True
                                        elif random_eff == 'lightning':
                                            next_shot_piercing = True
                                        elif random_eff == 'arrow':
                                            arrow_shots_left = 6
                                        elif random_eff == 'dye':
                                            next_shot_dye_color = b["color"]
                                        elif random_eff == 'rainbow':
                                            next_shot_rainbow = True
                                        elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                                            chain_effect = random_eff
                                            chain_effect_timer = EFFECT_DURATION
                                        elif random_eff in ('aim', 'dizzy', 'block','sluggish'):
                                            shooter_effect = random_eff
                                            shooter_effect_timer = EFFECT_DURATION
                                        elif random_eff == 'blind':
                                            blind_timer = 10 * 60
                                        elif random_eff == 'wormhole':
                                            wormhole_timer = 10 * 60
                        exp_min_idx = min(balls[idx]["index"] for idx in remove_indices)
                        score += len(remove_indices) * SCORE_PERBALL
                        for idx in remove_indices:
                            balls.pop(idx)
                        for b in balls:
                            if b["index"] > exp_min_idx:
                                b["index"] -= len(remove_indices) * OFFSET
                                safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                                b["x"] = trackpoints[safe_idx][0]
                                b["y"] = trackpoints[safe_idx][1]
                        found = True
                        break
                found = True
                break
            i += 1
        if not found:
            break
def draw_effect_icon(surface, cx, cy, effect_type):
    icon_color = (0, 0, 0)
    if effect_type == 'aim':
        pg.draw.circle(surface, icon_color, (cx, cy), BALLRADIUS - 4, 2)
        pg.draw.line(surface, icon_color, (cx - 8, cy), (cx + 8, cy), 2)
        pg.draw.line(surface, icon_color, (cx, cy - 8), (cx, cy + 8), 2)
    elif effect_type == 'slow':
        pg.draw.line(surface, icon_color, (cx - 5, cy - 8), (cx - 5, cy + 8), 3)
        pg.draw.line(surface, icon_color, (cx + 5, cy - 8), (cx + 5, cy + 8), 3)
    elif effect_type == 'reverse':
        pg.draw.polygon(surface, icon_color, [(cx + 6, cy - 8), (cx - 2, cy), (cx + 6, cy + 8)])
    elif effect_type == 'forward':
        pg.draw.polygon(surface, icon_color, [(cx - 2, cy - 8), (cx + 6, cy), (cx - 2, cy + 8)])
        pg.draw.polygon(surface, icon_color, [(cx + 6, cy - 8), (cx + 14, cy), (cx + 6, cy + 8)])
    elif effect_type == 'explode':
        for i in range(8):
            angle = i * math.pi / 4
            pg.draw.line(surface, icon_color, (cx + math.cos(angle)*4, cy + math.sin(angle)*4), (cx + math.cos(angle)*11, cy + math.sin(angle)*11), 2)
        pg.draw.circle(surface, icon_color, (cx, cy), 3)
    elif effect_type == 'freeze':
        pg.draw.rect(surface, icon_color, (cx - 8, cy - 10, 16, 2))
        pg.draw.rect(surface, icon_color, (cx - 8, cy + 8, 16, 2))
        pg.draw.polygon(surface, icon_color, [(cx - 7, cy - 8), (cx + 7, cy - 8), (cx, cy)])
        pg.draw.polygon(surface, icon_color, [(cx - 7, cy + 8), (cx + 7, cy + 8), (cx, cy)])
        pg.draw.line(surface, icon_color, (cx, cy), (cx, cy + 3), 2)
    elif effect_type == 'clear_color':
        r = 5
        d = 4 * math.sqrt(3)
        pg.draw.circle(surface, icon_color, (round(cx), round(cy - d)), r)
        pg.draw.circle(surface, icon_color, (round(cx + (d * math.sqrt(3) / 2)), round(cy + d / 2)), r)
        pg.draw.circle(surface, icon_color, (round(cx - (d * math.sqrt(3) / 2)), round(cy + d / 2)), r)
    elif effect_type == 'lightning':
        pg.draw.polygon(surface, icon_color, [(cx - 2, cy - 10), (cx + 6, cy - 2), (cx + 1, cy), (cx + 4, cy + 10), (cx - 4, cy + 2), (cx + 1, cy), (cx - 2, cy - 10)])
    elif effect_type == 'dizzy':
        pg.draw.line(surface, icon_color, (cx - 8, cy - 5), (cx - 3, cy), 2)
        pg.draw.line(surface, icon_color, (cx - 3, cy - 5), (cx - 8, cy), 2)
        pg.draw.line(surface, icon_color, (cx + 3, cy - 5), (cx + 8, cy), 2)
        pg.draw.line(surface, icon_color, (cx + 8, cy - 5), (cx + 3, cy), 2)
        pg.draw.arc(surface, icon_color, (cx - 6, cy + 2, 12, 6), 0, math.pi, 2)
    elif effect_type == 'arrow':
        pg.draw.polygon(surface, icon_color, [(cx - 8, cy - 8), (cx + 6, cy), (cx - 8, cy + 8)])
        pg.draw.line(surface, icon_color, (cx - 8, cy), (cx - 12, cy), 3)
    elif effect_type == 'add_score':
        pg.draw.line(surface, icon_color, (cx, cy - 8), (cx, cy + 8), 3)
        pg.draw.line(surface, icon_color, (cx - 8, cy), (cx + 8, cy), 3)
    elif effect_type == 'dye':
        pg.draw.polygon(surface, icon_color, [(cx, cy - 10), (cx - 8, cy + 4), (cx + 8, cy + 4)])
        pg.draw.circle(surface, icon_color, (cx, cy + 4), 8)
    elif effect_type == 'rainbow':
        pg.draw.arc(surface, icon_color, (cx - 10, cy - 10, 20, 20), 0, math.pi, 2)
        pg.draw.arc(surface, icon_color, (cx - 7, cy - 7, 14, 14), 0, math.pi, 2)
        pg.draw.arc(surface, icon_color, (cx - 4, cy - 4, 8, 8), 0, math.pi, 2)
    elif effect_type == 'block':
        pg.draw.line(surface, icon_color, (cx - 8, cy - 8), (cx + 8, cy + 8), 3)
        pg.draw.line(surface, icon_color, (cx + 8, cy - 8), (cx - 8, cy + 8), 3)
    elif effect_type == 'rearrange':
        pg.draw.arc(surface, icon_color, (cx - 8, cy - 8, 16, 16), 0.15 * math.pi, 0.85 * math.pi, 2)
        pg.draw.arc(surface, icon_color, (cx - 8, cy - 8, 16, 16), 1.15 * math.pi, 1.85 * math.pi, 2)
        pg.draw.polygon(surface, icon_color, [(cx + 8, cy - 4), (cx + 4, cy - 8), (cx + 2, cy - 2)])
        pg.draw.polygon(surface, icon_color, [(cx - 8, cy + 4), (cx - 4, cy + 8), (cx - 2, cy + 2)])
    elif effect_type == 'sluggish':
        pg.draw.circle(surface, icon_color, (cx, cy), BALLRADIUS - 4, 2)
        pg.draw.line(surface, icon_color, (cx - 7, cy), (cx + 7, cy), 3)
    elif effect_type == 'blind':
        pg.draw.arc(surface, icon_color, (cx - 10, cy - 6, 20, 12), 0.1 * math.pi, 0.9 * math.pi, 2)
        pg.draw.arc(surface, icon_color, (cx - 10, cy - 6, 20, 12), 1.1 * math.pi, 1.9 * math.pi, 2)
        pg.draw.circle(surface, icon_color, (cx, cy), 3)
        pg.draw.line(surface, icon_color, (cx - 9, cy - 9), (cx + 9, cy + 9), 3)
        pg.draw.line(surface, icon_color, (cx + 9, cy - 9), (cx - 9, cy + 9), 3)
    elif effect_type == 'wormhole':
        pg.draw.circle(surface, icon_color, (cx - 2, cy - 2), 9, 2)
        pg.draw.circle(surface, icon_color, (cx + 2, cy + 2), 6, 2)
        pg.draw.circle(surface, icon_color, (cx, cy), 3)
    elif effect_type == 'question':
        font = pg.font.SysFont('comicsans', 24, bold=True)
        text = font.render('?', True, icon_color)
        surface.blit(text, text.get_rect(center=(cx, cy)))
first_shot_done=False
while running:
    if start and not lose and len(balls) == 0 and score >= TARGET_SCORE:
        win = True
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                if not start:
                    start = True
                elif win or lose:
                    running = False
        if event.type == pg.QUIT:
            running = False
        if start and not win and not lose and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if shooter_effect=='block':
                continue
            shoot_speed = 15
            if shooter_effect == 'aim':
                shoot_speed = shoot_speed*3
            elif shooter_effect == 'sluggish':
                shoot_speed = shoot_speed/3
            dx = math.cos(shooterangle) * shoot_speed
            dy = math.sin(shooterangle) * shoot_speed
            if shooter_effect == 'dizzy':
                dx = -dx
                dy = -dy
            is_arrow_shot = False
            is_dye_shot = False
            is_rainbow_shot = False
            shot_color = current_ball_color
            if next_shot_dye_color is not None:
                is_dye_shot = True
                shot_color = next_shot_dye_color
                next_shot_dye_color = None
                next_shot_piercing = False
                next_shot_rainbow = False
                arrow_shots_left = 0
            elif next_shot_rainbow:
                is_rainbow_shot = True
                shot_color = (255, 255, 255)
                next_shot_rainbow = False
                next_shot_piercing = False
                next_shot_dye_color = None
                arrow_shots_left = 0
            elif next_shot_piercing:
                next_shot_dye_color = None
                next_shot_rainbow = False
                arrow_shots_left = 0
            elif arrow_shots_left > 0:
                is_arrow_shot = True
                arrow_shots_left -= 1
                next_shot_dye_color = None
                next_shot_rainbow = False
                next_shot_piercing = False
            flying_balls.append({
                "color": shot_color,
                "x": shooterpos[0], "y": shooterpos[1],
                "dx": dx, "dy": dy,
                "trail": [],
                "piercing": next_shot_piercing,
                "is_arrow": is_arrow_shot,
                "is_dye": is_dye_shot,
                "is_rainbow": is_rainbow_shot
            })
            if next_shot_piercing:
                next_shot_piercing = False
            current_ball_color = rd.choice(COLORS)
    mx, my = pg.mouse.get_pos()
    shooterangle = math.atan2(my - shooterpos[1], mx - shooterpos[0])
    if start and not win and not lose:
        effect_spawn_timer += 1
        if effect_spawn_timer >= EFFECT_SPAWN_INTERVAL:
            effect_spawn_timer = 0
            if len(balls) > 0:
                spawn_idx = rd.randint(0, len(balls) - 1)
                effect_type = rd.choice(EFFECT_TYPES)
                balls[spawn_idx]["effect"] = effect_type
                balls[spawn_idx]["effect_timer"] = 20 * 60
        for ball in balls[:]:
            if "effect" in ball:
                ball["effect_timer"] -= 1
                if ball["effect_timer"] <= 0:
                    del ball["effect"]
                    del ball["effect_timer"]
        if chain_effect:
            chain_effect_timer -= 1
            if chain_effect_timer <= 0:
                chain_effect = None
                chain_effect_timer = 0
        if shooter_effect:
            shooter_effect_timer -= 1
            if shooter_effect_timer <= 0:
                shooter_effect = None
                shooter_effect_timer = 0
        if blind_timer > 0:
            blind_timer -= 1
        if wormhole_timer > 0:
            wormhole_timer -= 1
    if start and not win and not lose:
        move_speed = BALL_SPEED
        if chain_effect == 'freeze':
            move_speed = 0
        elif chain_effect == 'slow':
            move_speed *= 0.5
        elif chain_effect == 'forward':
            move_speed *= 2
        elif chain_effect == 'reverse':
            move_speed *= -1
            if balls:
                tail_ball = min(balls, key=lambda b: b["index"])
                if tail_ball["index"] <= 0.0:
                    score += 10
                    balls.remove(tail_ball)
                    move_speed = 0
        balls_to_remove = []
        for ball in balls:
            ball["index"] += move_speed
            if ball["index"] >= len(trackpoints):
                if wormhole_timer > 0:
                    balls_to_remove.append(ball)
                else:
                    lose = True
            elif ball["index"] < 0:
                ball["index"] = 0
            else:
                idx = max(0, min(int(round(ball["index"])), len(trackpoints) - 1))
                ball["x"] = trackpoints[idx][0]
                ball["y"] = trackpoints[idx][1]
        for b in balls_to_remove:
            if b in balls:
                balls.remove(b)
                score += SCORE_PERBALL
        if move_speed > 0:
            speed_ratio = move_speed / BALL_SPEED
            current_spawn_interval = max(1, int(45 / speed_ratio))
        else:
            current_spawn_interval = 45
        if move_speed > 0:
            speed_ratio = move_speed / BALL_SPEED
            current_spawn_interval = max(1, int(45 / speed_ratio))
        else:
            current_spawn_interval = 45
        if not lose:
            if move_speed > 0:
                spawn_timer += move_speed
            if spawn_timer >= 1.0:
                if score < TARGET_SCORE:
                    if chain_effect not in ('reverse', 'freeze'):
                        if balls:
                            tail_ball = min(balls, key=lambda b: b["index"])
                            if tail_ball["index"] >= 1.0:
                                spawn_timer -= 1.0
                                spawned_balls_count += 1
                                new_idx = tail_ball["index"] - 1.0
                                safe_idx = max(0, min(int(round(new_idx)), len(trackpoints) - 1))
                                balls.insert(0, {
                                    "color": rd.choice(COLORS),
                                    "index": new_idx,
                                    "x": trackpoints[safe_idx][0],
                                    "y": trackpoints[safe_idx][1],
                                    "initial":True
                                })
                        else:
                            spawn_timer = 0.0
                            spawned_balls_count += 1
                            balls.insert(0, {
                                "color": rd.choice(COLORS),
                                "index": 0,
                                "x": trackpoints[0][0],
                                "y": trackpoints[0][1],
                                "initial":True
                            })
    for fball in flying_balls[:]:
        if shooter_effect == 'aim' or fball.get("piercing", False) or fball.get("is_arrow", False) or fball.get(
                "is_dye", False) or fball.get("is_rainbow", False):
            fball["trail"].append((fball["x"], fball["y"]))
            if len(fball["trail"]) > 6:
                fball["trail"].pop(0)
        fball["x"] += fball["dx"]
        fball["y"] += fball["dy"]
        if fball["x"] < 0 or fball["x"] >= WIDTH or fball["y"] < 0 or fball["y"] >= HEIGHT:
            flying_balls.remove(fball)
            continue
        if fball.get("piercing", False):
            hit_balls = []
            for chainball in balls:
                dist = math.hypot(fball["x"] - chainball["x"], fball["y"] - chainball["y"])
                if dist < BALLRADIUS * 2:
                    hit_balls.append(chainball)
            if hit_balls:
                prev_x = fball["x"] - fball["dx"]
                prev_y = fball["y"] - fball["dy"]
                hit_balls.sort(key=lambda b: math.hypot(b["x"] - prev_x, b["y"] - prev_y))
                for hb in hit_balls:
                    if "effect" in hb:
                        eff = hb["effect"]
                        if eff not in ('explode', 'lightning'):
                            if eff == 'arrow':
                                arrow_shots_left = 6
                            elif eff == 'add_score':
                                score += 100
                            elif eff == 'dye':
                                next_shot_dye_color = hb["color"]
                            elif eff == 'rainbow':
                                next_shot_rainbow = True
                            elif eff in ('slow', 'forward', 'reverse', 'freeze'):
                                chain_effect = eff
                                chain_effect_timer = EFFECT_DURATION
                            elif eff in ('aim', 'dizzy', 'block','sluggish'):
                                shooter_effect = eff
                                shooter_effect_timer = EFFECT_DURATION
                            elif eff == 'blind':
                                blind_timer = 10 * 60
                            elif eff == 'wormhole':
                                wormhole_timer = 10 * 60
                            elif eff == 'question':
                                possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                                random_eff = rd.choice(possible_effects)
                                if random_eff == 'explode':
                                    has_explode = True
                                elif random_eff == 'clear_color':
                                    clear_color_target = hitball["color"]
                                elif random_eff == 'lightning':
                                    next_shot_piercing = True
                                elif random_eff == 'arrow':
                                    arrow_shots_left = 6
                                elif random_eff == 'add_score':
                                    score += 100
                                elif random_eff == 'dye':
                                    next_shot_dye_color = hitball["color"]
                                elif random_eff == 'rainbow':
                                    next_shot_rainbow = True
                                elif random_eff == 'rearrange':
                                    pending_rearrange = True
                                elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                                    chain_effect = random_eff
                                    chain_effect_timer = EFFECT_DURATION
                                elif random_eff in ('aim', 'dizzy', 'block','sluggish'):
                                    shooter_effect = random_eff
                                    shooter_effect_timer = EFFECT_DURATION
                                elif random_eff == 'blind':
                                    blind_timer = 10 * 60
                                elif random_eff == 'wormhole':
                                    wormhole_timer = 10 * 60
                hit_balls.sort(key=lambda b: b["index"], reverse=True)
                for hb in hit_balls:
                    if hb in balls:
                        current_idx = hb["index"]
                        balls.remove(hb)
                        score += SCORE_PERBALL
                        for b in balls:
                            if b["index"] > current_idx:
                                b["index"] -= OFFSET
                                safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                                b["x"] = trackpoints[safe_idx][0]
                                b["y"] = trackpoints[safe_idx][1]
                clear_matches()
        elif fball.get("is_arrow", False):
            hitball = None
            mindist = float('inf')
            for chainball in balls:
                dist = math.hypot(fball["x"] - chainball["x"], fball["y"] - chainball["y"])
                if dist < BALLRADIUS * 2 and dist < mindist:
                    mindist = dist
                    hitball = chainball
            if hitball:
                hitindex = next((i for i, b in enumerate(balls) if b is hitball), -1)
                if hitindex != -1:
                    if "effect" in hitball:
                        eff = hitball["effect"]
                        fball["piercing"] = False
                        fball["is_arrow"] = False
                        fball["is_dye"] = False
                        fball["is_rainbow"] = False
                        if eff == 'lightning':
                            fball["piercing"] = True
                        elif eff == 'dye':
                            fball["is_dye"] = True
                            fball["color"] = hitball["color"]
                        elif eff == 'arrow':
                            fball["is_arrow"] = True
                        elif eff == 'rainbow':
                            fball["is_rainbow"] = True
                    if "effect" in hitball:
                        eff = hitball["effect"]
                        if eff == 'explode':
                            remove_indices = []
                            for offset in range(-4, 5):
                                idx = hitindex + offset
                                if 0 <= idx < len(balls):
                                    remove_indices.append(idx)
                            if remove_indices:
                                remove_indices.sort(reverse=True)
                                min_idx = min(balls[idx]["index"] for idx in remove_indices)
                                score += len(remove_indices) * SCORE_PERBALL
                                for idx in remove_indices:
                                    balls.pop(idx)
                                for b in balls:
                                    if b["index"] > min_idx:
                                        b["index"] -= len(remove_indices) * OFFSET
                                        safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                                        b["x"] = trackpoints[safe_idx][0]
                                        b["y"] = trackpoints[safe_idx][1]
                        elif eff == 'lightning':
                            next_shot_piercing = True
                        elif eff == 'arrow':
                            arrow_shots_left = 6
                        elif eff == 'add_score':
                            score += 100
                        elif eff == 'dye':
                            next_shot_dye_color = hitball["color"]
                        elif eff == 'rainbow':
                            next_shot_rainbow = True
                        elif eff == 'question':
                            possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                            random_eff = rd.choice(possible_effects)
                            if random_eff == 'explode':
                                has_explode = True
                            elif random_eff == 'clear_color':
                                clear_color_target = hitball["color"]
                            elif random_eff == 'lightning':
                                next_shot_piercing = True
                            elif random_eff == 'arrow':
                                arrow_shots_left = 6
                            elif random_eff == 'add_score':
                                score += 100
                            elif random_eff == 'dye':
                                next_shot_dye_color = hitball["color"]
                            elif random_eff == 'rainbow':
                                next_shot_rainbow = True
                            elif random_eff == 'rearrange':
                                pending_rearrange = True
                            elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                                chain_effect = random_eff
                                chain_effect_timer = EFFECT_DURATION
                            elif random_eff in ('aim', 'dizzy', 'block','sluggish'):
                                shooter_effect = random_eff
                                shooter_effect_timer = EFFECT_DURATION
                            elif random_eff == 'blind':
                                blind_timer = 10 * 60
                            elif random_eff == 'wormhole':
                                wormhole_timer = 10 * 60
                        else:
                            if eff in ('slow', 'forward', 'reverse', 'freeze'):
                                chain_effect = eff
                                chain_effect_timer = EFFECT_DURATION
                            elif eff in ('aim', 'dizzy','block','sluggish'):
                                shooter_effect = eff
                                shooter_effect_timer = EFFECT_DURATION
                            elif eff == 'blind':
                                blind_timer = 10 * 60
                            elif eff == 'wormhole':
                                wormhole_timer = 10 * 60
                        if eff != 'explode':
                            current_idx = hitball["index"]
                            balls.pop(hitindex)
                            score += SCORE_PERBALL
                            for b in balls:
                                if b["index"] > current_idx:
                                    b["index"] -= OFFSET
                                    safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                                    b["x"] = trackpoints[safe_idx][0]
                                    b["y"] = trackpoints[safe_idx][1]
                    else:
                        current_idx = hitball["index"]
                        balls.pop(hitindex)
                        score += SCORE_PERBALL
                        for b in balls:
                            if b["index"] > current_idx:
                                b["index"] -= OFFSET
                                safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                                b["x"] = trackpoints[safe_idx][0]
                                b["y"] = trackpoints[safe_idx][1]
                    flying_balls.remove(fball)
                    clear_matches()
        elif fball.get("is_dye", False):
            hitball = None
            mindist = float('inf')
            for chainball in balls:
                dist = math.hypot(fball["x"] - chainball["x"], fball["y"] - chainball["y"])
                if dist < BALLRADIUS * 2 and dist < mindist:
                    mindist = dist
                    hitball = chainball
            if hitball:
                hit_idx = hitball["index"]
                for b in balls:
                    if abs(b["index"] - hit_idx) <= 4:
                        b["color"] = fball["color"]
                        b["protected"]=True
                flying_balls.remove(fball)
        elif fball.get("is_rainbow", False):
            hitball = None
            mindist = float('inf')
            for chainball in balls:
                dist = math.hypot(fball["x"] - chainball["x"], fball["y"] - chainball["y"])
                if dist < BALLRADIUS * 2 and dist < mindist:
                    mindist = dist
                    hitball = chainball
            if hitball:
                hitindex = next((i for i, b in enumerate(balls) if b is hitball), -1)
                if hitindex != -1:
                    newindex = hitball["index"]
                    for b in balls[hitindex:]:
                        b["index"] += OFFSET
                        safe_idx = min(int(round(b["index"])), len(trackpoints) - 1)
                        b["x"] = trackpoints[safe_idx][0]
                        b["y"] = trackpoints[safe_idx][1]
                    safe_new = min(int(round(newindex)), len(trackpoints) - 1)
                    rainbow_ball = {
                        "color": (255, 255, 255),
                        "index": newindex,
                        "x": trackpoints[safe_new][0],
                        "y": trackpoints[safe_new][1],
                        "is_rainbow_card": True
                    }
                    balls.insert(hitindex, rainbow_ball)
                    flying_balls.remove(fball)
                    rainbow_idx_in_list = hitindex
                    left_target_color = None
                    if rainbow_idx_in_list - 1 >= 0:
                        left_target_color = balls[rainbow_idx_in_list - 1]["color"]
                    right_target_color = None
                    if rainbow_idx_in_list + 1 < len(balls):
                        right_target_color = balls[rainbow_idx_in_list + 1]["color"]
                    remove_indices = [rainbow_idx_in_list]
                    if left_target_color is not None:
                        i = rainbow_idx_in_list - 1
                        while i >= 0 and balls[i]["color"] == left_target_color:
                            remove_indices.append(i)
                            i -= 1
                    if right_target_color is not None:
                        i = rainbow_idx_in_list + 1
                        while i < len(balls) and balls[i]["color"] == right_target_color:
                            remove_indices.append(i)
                            i += 1
                    remove_indices.sort(reverse=True)
                    score += len(remove_indices) * SCORE_PERBALL
                    min_idx_removed = min(balls[idx]["index"] for idx in remove_indices)
                    num_removed = len(remove_indices)
                    for idx in remove_indices:
                        b = balls[idx]
                        if "effect" in b:
                            eff = b["effect"]
                            # 过滤掉 explode 和 lightning，防止引发连锁爆炸导致死循环
                            if eff not in ('explode', 'lightning'):
                                if eff == 'arrow':
                                    arrow_shots_left = 6
                                elif eff == 'add_score':
                                    score += 100
                                elif eff == 'dye':
                                    next_shot_dye_color = b["color"]
                                elif eff == 'rainbow':
                                    next_shot_rainbow = True
                                elif eff in ('slow', 'forward', 'reverse', 'freeze'):
                                    chain_effect = eff
                                    chain_effect_timer = EFFECT_DURATION
                                elif eff in ('aim', 'dizzy', 'block', 'sluggish'):
                                    shooter_effect = eff
                                    shooter_effect_timer = EFFECT_DURATION
                                elif eff == 'blind':
                                    blind_timer = 10 * 60
                                elif eff == 'wormhole':
                                    wormhole_timer = 10 * 60
                                elif eff == 'question':
                                    possible_effects = [e for e in EFFECT_TYPES if e != 'question']
                                    random_eff = rd.choice(possible_effects)
                                    if random_eff == 'add_score':
                                        score += 100
                                    elif random_eff == 'rearrange':
                                        pending_rearrange = True
                                    elif random_eff == 'lightning':
                                        next_shot_piercing = True
                                    elif random_eff == 'arrow':
                                        arrow_shots_left = 6
                                    elif random_eff == 'dye':
                                        next_shot_dye_color = b["color"]
                                    elif random_eff == 'rainbow':
                                        next_shot_rainbow = True
                                    elif random_eff in ('slow', 'forward', 'reverse', 'freeze'):
                                        chain_effect = random_eff
                                        chain_effect_timer = EFFECT_DURATION
                                    elif random_eff in ('aim', 'dizzy', 'block', 'sluggish'):
                                        shooter_effect = random_eff
                                        shooter_effect_timer = EFFECT_DURATION
                                    elif random_eff == 'blind':
                                        blind_timer = 10 * 60
                                    elif random_eff == 'wormhole':
                                        wormhole_timer = 10 * 60
                    for idx in remove_indices:
                        balls.pop(idx)
                    for b in balls:
                        if b["index"] > min_idx_removed:
                            b["index"] -= num_removed * OFFSET
                            safe_idx = max(0, min(int(round(b["index"])), len(trackpoints) - 1))
                            b["x"] = trackpoints[safe_idx][0]
                            b["y"] = trackpoints[safe_idx][1]
                    clear_matches()
        else:
            hitball = None
            mindist = float('inf')
            for chainball in balls:
                dist = math.hypot(fball["x"] - chainball["x"], fball["y"] - chainball["y"])
                if dist < BALLRADIUS * 2 and dist < mindist:
                    mindist = dist
                    hitball = chainball
            if hitball:
                hitindex = next((i for i, b in enumerate(balls) if b is hitball), -1)
                if hitindex != -1:
                    newindex = hitball["index"]
                    for b in balls[hitindex:]:
                        b["index"] += OFFSET
                        safe_idx = min(int(round(b["index"])), len(trackpoints) - 1)
                        b["x"] = trackpoints[safe_idx][0]
                        b["y"] = trackpoints[safe_idx][1]
                    safe_new = min(int(round(newindex)), len(trackpoints) - 1)
                    balls.insert(hitindex, {
                        "color": fball["color"],
                        "index": newindex,
                        "x": trackpoints[safe_new][0],
                        "y": trackpoints[safe_new][1]
                    })
                    flying_balls.remove(fball)
                    if not first_shot_done:
                        check_local_match(hitindex)
                        first_shot_done = True
                    else:
                        clear_matches()
    if pending_rearrange:
        pending_rearrange = False
        if balls:
            colors = [b["color"] for b in balls]
            rd.shuffle(colors)
            for b, c in zip(balls, colors):
                b["color"] = c
    if not start:
        screen.fill((40, 40, 40))
        title_font = pg.font.SysFont("comicsans", 60)
        tip_font = pg.font.SysFont("comicsans", 30)
        title_text = title_font.render("Zuma", True, (255, 255, 255))
        tip_text = tip_font.render("Press SPACE to start", True, (200, 200, 200))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(tip_text, (WIDTH // 2 - tip_text.get_width() // 2, HEIGHT // 2 + 20))
    else:
        if win or lose:
            screen.fill((40, 40, 40))
            font1 = pg.font.SysFont("comicsans", 30)
            font2 = pg.font.SysFont("comicsans", 30)
            font3 = pg.font.SysFont("comicsans", 30)
            if win:
                text1 = font1.render("Congratulations! You win!", True, (255, 255, 255))
                text2 = font2.render("Press SPACE to quit!", True, (255, 255, 255))
                text3 = font3.render(f"Score: {score}", True, (255, 255, 255))
            else:
                text1 = font1.render("What a pity! You lose!", True, (255, 0, 0))
                text2 = font2.render("Press SPACE to quit!", True, (255, 0, 0))
                text3 = font3.render(f"Score: {score}", True, (255, 0, 0))
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2))
            screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 50))
        else:
            screen.fill((40, 40, 40))
            pg.draw.circle(screen, (20, 20, 20), (centerx, centery), holeradius)
            pg.draw.circle(screen, (100, 100, 100), (centerx, centery), holeradius, 3)
            for p in trackpoints:
                pg.draw.circle(screen, (120, 120, 120), (int(p[0]), int(p[1])), 2)
            if blind_timer <= 0:
                for ball in balls:
                    if "effect" in ball:
                        pg.draw.circle(screen, (0, 0, 0), (round(ball["x"]), round(ball["y"])), BALLRADIUS + 1)
                        pg.draw.circle(screen, ball["color"], (round(ball["x"]), round(ball["y"])), BALLRADIUS)
                        draw_effect_icon(screen, round(ball["x"]), round(ball["y"]), ball["effect"])
                    elif ball.get("is_rainbow_card", False):
                        pg.draw.circle(screen, (0, 0, 0), (round(ball["x"]), round(ball["y"])), BALLRADIUS + 2)
                        pg.draw.circle(screen, (255, 255, 255), (round(ball["x"]), round(ball["y"])), BALLRADIUS)
                        draw_effect_icon(screen, round(ball["x"]), round(ball["y"]), 'rainbow')
                    else:
                        pg.draw.circle(screen, (0, 0, 0), (round(ball["x"]), round(ball["y"])), BALLRADIUS + 2)
                        pg.draw.circle(screen, ball["color"], (round(ball["x"]), round(ball["y"])), BALLRADIUS)
            pg.draw.circle(screen, (200, 200, 200), shooterpos, 30)
            pg.draw.circle(screen, (100, 100, 100), shooterpos, 30, 3)
            endx = shooterpos[0] + math.cos(shooterangle) * 50
            endy = shooterpos[1] + math.sin(shooterangle) * 50
            pg.draw.line(screen, current_ball_color, shooterpos, (endx, endy), 12)
            pg.draw.circle(screen, current_ball_color, shooterpos, BALLRADIUS)
            for fball in flying_balls:
                trail_color = None
                if fball.get("piercing", False):
                    trail_color = (0, 255, 255)
                elif fball.get("is_arrow", False):
                    trail_color = (255, 255, 255)
                elif fball.get("is_dye", False):
                    trail_color = (200, 200, 200)
                elif fball.get("is_rainbow", False):
                    trail_color = (255, 255, 255)
                elif shooter_effect == 'aim':
                    trail_color = (255, 100, 100)
                if trail_color:
                    for i, (tx, ty) in enumerate(fball["trail"]):
                        alpha = (i + 1) / len(fball["trail"])
                        radius = int(BALLRADIUS * alpha)
                        pg.draw.circle(screen, trail_color, (round(tx), round(ty)), radius)
                pg.draw.circle(screen, (0, 0, 0), (round(fball["x"]), round(fball["y"])), BALLRADIUS + 2)
                pg.draw.circle(screen, fball["color"], (round(fball["x"]), round(fball["y"])), BALLRADIUS)
                if fball.get("is_arrow", False):
                    draw_effect_icon(screen, round(fball["x"]), round(fball["y"]), 'arrow')
                elif fball.get("is_dye", False):
                    draw_effect_icon(screen, round(fball["x"]), round(fball["y"]), 'dye')
                elif fball.get("is_rainbow", False):
                    draw_effect_icon(screen, round(fball["x"]), round(fball["y"]), 'rainbow')
            score_font = pg.font.SysFont("comicsans", 28, bold=True)
            score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))
            bar_width = 300
            bar_height = 20
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = 10
            progress = min(score / TARGET_SCORE, 1.0)
            if score >= TARGET_SCORE:
                bar_color = (0, 255, 0)
            else:
                bar_color = (255, 255, 0)
            pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            pg.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_width * progress), bar_height))
            pg.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
            y_offset = 10
            if shooter_effect:
                effect_font = pg.font.SysFont("comicsans", 22, bold=True)
                total_seconds = shooter_effect_timer // 60
                time_str = f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"
                effect_text = effect_font.render(f"Shooter: {EFFECT_NAMES[shooter_effect]}  {time_str}", True,(255, 255, 100))
                screen.blit(effect_text, (WIDTH - effect_text.get_width() - 10, y_offset))
                y_offset += 30
            if chain_effect:
                effect_font = pg.font.SysFont("comicsans", 22, bold=True)
                total_seconds = chain_effect_timer // 60
                time_str = f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"
                effect_text = effect_font.render(f"Chain: {EFFECT_NAMES[chain_effect]}  {time_str}", True,(100, 255, 100))
                screen.blit(effect_text, (WIDTH - effect_text.get_width() - 10, y_offset))
                y_offset += 30
            if blind_timer > 0:
                blind_font = pg.font.SysFont("comicsans", 22, bold=True)
                total_seconds = blind_timer // 60
                time_str = f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"
                blind_text = blind_font.render(f"Blind: {time_str}", True, (255, 100, 100))
                screen.blit(blind_text, (WIDTH - blind_text.get_width() - 10, y_offset))
                y_offset += 30
            if wormhole_timer > 0:
                wormhole_font = pg.font.SysFont("comicsans", 22, bold=True)
                total_seconds = wormhole_timer // 60
                time_str = f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"
                wormhole_text = wormhole_font.render(f"Wormhole: {time_str}", True, (180, 0, 255))
                screen.blit(wormhole_text, (WIDTH - wormhole_text.get_width() - 10, y_offset))
                y_offset += 30
            if next_shot_dye_color is not None:
                state_font = pg.font.SysFont("comicsans", 22, bold=True)
                state_text = state_font.render("Dye Ready!", True, (200, 200, 200))
                screen.blit(state_text, (WIDTH - state_text.get_width() - 10, y_offset))
                y_offset += 30
            elif next_shot_rainbow:
                state_font = pg.font.SysFont("comicsans", 22, bold=True)
                state_text = state_font.render("Rainbow Ready!", True, (255, 255, 255))
                screen.blit(state_text, (WIDTH - state_text.get_width() - 10, y_offset))
                y_offset += 30
            elif next_shot_piercing:
                state_font = pg.font.SysFont("comicsans", 22, bold=True)
                state_text = state_font.render("Lightning Ready!", True, (0, 255, 255))
                screen.blit(state_text, (WIDTH - state_text.get_width() - 10, y_offset))
                y_offset += 30
            elif arrow_shots_left > 0:
                state_font = pg.font.SysFont("comicsans", 22, bold=True)
                state_text = state_font.render(f"Arrows Left: {arrow_shots_left}", True, (255, 255, 255))
                screen.blit(state_text, (WIDTH - state_text.get_width() - 10, y_offset))
                y_offset += 30
    pg.display.flip()
    clock.tick(60)
pg.quit()