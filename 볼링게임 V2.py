import turtle
import random
import time

# =========================
# 화면 설정
# =========================
screen = turtle.Screen()
screen.title("볼링 게임 🎳")
screen.bgcolor("black")
screen.setup(width=600, height=700)
screen.tracer(0)

# =========================
# 점수 / 프레임 관리
# =========================
score = 0
high_score = 0

MAX_FRAMES = 10
frame_num = 1
ball_in_frame = 1
pins_before_throw = 10

frame_results = [[] for _ in range(MAX_FRAMES)]

score_display = turtle.Turtle()
score_display.hideturtle()
score_display.color("white")
score_display.penup()
score_display.goto(0, 310)

frame_display = turtle.Turtle()
frame_display.hideturtle()
frame_display.color("yellow")
frame_display.penup()
frame_display.goto(0, 280)

guide_display = turtle.Turtle()
guide_display.hideturtle()
guide_display.color("light gray")
guide_display.penup()
guide_display.goto(0, -330)


def update_score():
    score_display.clear()
    score_display.write(
        f"점수: {score}   최고점수: {high_score}   프레임: {min(frame_num, MAX_FRAMES)}/{MAX_FRAMES}",
        align="center",
        font=("Arial", 15, "normal")
    )


def format_frame(results):
    if not results:
        return "-"

    display_parts = []
    for i, val in enumerate(results):
        if val == "X":
            display_parts.append("X")
            continue

        if i > 0 and results[i - 1] != "X":
            prev = results[i - 1]
            if isinstance(prev, int) and prev + val == 10:
                display_parts.append("/")
                continue

        display_parts.append(str(val))

    return " ".join(display_parts)


def update_frame_display():
    frame_display.clear()
    line = "  |  ".join(
        f"{i+1}:{format_frame(frame_results[i])}" for i in range(MAX_FRAMES)
    )
    frame_display.write(line, align="center", font=("Arial", 10, "normal"))


def all_balls():
    balls = []
    for f in frame_results:
        for b in f:
            balls.append(10 if b == "X" else b)
    return balls


def calculate_score():
    balls = all_balls()
    total = 0
    idx = 0

    for _ in range(MAX_FRAMES):
        if idx >= len(balls):
            break

        if balls[idx] == 10:
            if idx + 2 < len(balls):
                total += 10 + balls[idx + 1] + balls[idx + 2]
                idx += 1
            else:
                break
        elif idx + 1 < len(balls) and balls[idx] + balls[idx + 1] == 10:
            if idx + 2 < len(balls):
                total += 10 + balls[idx + 2]
                idx += 2
            else:
                break
        elif idx + 1 < len(balls):
            total += balls[idx] + balls[idx + 1]
            idx += 2
        else:
            break

    return total


update_score()
update_frame_display()

guide_display.write(
    "방향키(← / →)로 위치를 조정하고, 스페이스바로 투구하세요",
    align="center",
    font=("Arial", 13, "normal")
)

# =========================
# 볼링 레인 만들기
# =========================
lane = turtle.Turtle()
lane.hideturtle()
lane.color("white")
lane.penup()

lane.goto(-160, -300)
lane.pendown()
lane.goto(-160, 260)

lane.penup()
lane.goto(160, -300)
lane.pendown()
lane.goto(160, 260)

# =========================
# 볼링공 만들기 (1.5배 확대)
# =========================
BALL_SCALE = 1.3 * 1.5  # 기존 1.3에서 1.5배 → 1.95

ball = turtle.Turtle()
ball.shape("circle")
ball.color("dodgerblue")
ball.shapesize(BALL_SCALE, BALL_SCALE)
ball.penup()
ball.goto(0, -260)

ball_moving = False

# =========================
# 핀 만들기 (뒤집은 방향: 아래 1개 -> 위로 갈수록 넓어짐)
# =========================
pins = []
knocked_pins = []

pin_positions = [
    (0, 120),

    (-25, 150),
    (25, 150),

    (-50, 180),
    (0, 180),
    (50, 180),

    (-75, 210),
    (-25, 210),
    (25, 210),
    (75, 210)
]

CHAIN_REACTION_RADIUS = 45        # 이 거리 안이면 확률적으로 연쇄 반응
CHAIN_REACTION_CHANCE = 0.5       # 근처에 있을 때 넘어질 확률 50%
COLLISION_OVERLAP_DISTANCE = 20   # 이 거리 이내면 "실제로 부딪힌 것"으로 간주해 무조건 넘어짐


def make_pins():
    global pins, knocked_pins

    for pin in pins:
        pin.hideturtle()
    pins.clear()

    for pin in knocked_pins:
        pin.hideturtle()
    knocked_pins.clear()

    for x, y in pin_positions:
        pin = turtle.Turtle()
        pin.shape("circle")
        pin.color("white")
        pin.shapesize(0.8, 0.8)
        pin.penup()
        pin.goto(x, y)

        pins.append(pin)


make_pins()

# =========================
# 공용 사각형 그리기 함수
# =========================
def draw_box(t, x1, y1, x2, y2, fill_color):
    t.goto(x1, y1)
    t.pendown()
    t.fillcolor(fill_color)
    t.begin_fill()
    for _ in range(2):
        t.setx(x2)
        t.sety(y2)
        t.setx(x1)
        t.sety(y1)
    t.end_fill()
    t.penup()


# =========================
# 오른쪽 상단 메뉴 (새 게임 / 종료)
# =========================
menu_open = False
menu_buttons = {}

MENU_ICON_BOX = (235, 305, 275, 345)
MENU_ICON_CENTER = (255, 325)

menu_layer = turtle.Turtle()
menu_layer.hideturtle()
menu_layer.penup()
menu_layer.speed(0)


def render_menu():
    menu_layer.clear()
    menu_buttons.clear()

    # 메뉴 아이콘
    draw_box(menu_layer, *MENU_ICON_BOX, "gray15")
    menu_layer.goto(MENU_ICON_CENTER[0], MENU_ICON_CENTER[1] - 10)
    menu_layer.color("white")
    menu_layer.write("🎮", align="center", font=("Arial", 18, "normal"))
    menu_buttons["menu_icon"] = MENU_ICON_BOX

    if menu_open:
        options = ["새로운 게임", "게임 종료하기"]
        option_height = 36
        dropdown_width = 150
        top_y = MENU_ICON_BOX[1] - 5

        for i, label in enumerate(options):
            y2 = top_y - i * option_height
            y1 = y2 - option_height
            x2 = MENU_ICON_BOX[2]
            x1 = x2 - dropdown_width

            draw_box(menu_layer, x1, y1, x2, y2, "gray25")
            menu_layer.goto((x1 + x2) / 2, (y1 + y2) / 2 - 6)
            menu_layer.color("white")
            menu_layer.write(label, align="center", font=("Arial", 12, "normal"))
            menu_buttons[label] = (x1, y1, x2, y2)

    screen.update()


def start_new_game():
    global frame_num, ball_in_frame, frame_results, score, ball_moving
    frame_num = 1
    ball_in_frame = 1
    frame_results = [[] for _ in range(MAX_FRAMES)]
    score = 0
    ball_moving = False
    ball.goto(0, -260)
    make_pins()
    update_score()
    update_frame_display()
    screen.update()


# =========================
# 종료 확인 팝업 (마우스 클릭)
# =========================
dialog_active = False       # 팝업이 떠 있는 동안 True (게임 조작 막기용)
dialog_stage = None         # "game_over" 또는 "confirm_exit"
dialog_buttons = {}         # 버튼 이름 -> (x1, y1, x2, y2) 클릭 판정 영역

dialog_layer = turtle.Turtle()
dialog_layer.hideturtle()
dialog_layer.penup()
dialog_layer.speed(0)


def draw_dialog(message_lines, button_labels):
    global dialog_buttons
    dialog_layer.clear()
    dialog_buttons = {}

    # 어두운 배경 오버레이 (화면 전체)
    draw_box(dialog_layer, -280, -330, 280, 330, "gray10")

    # 팝업 박스 (화면 정중앙 기준, 세로로 더 넉넉하게)
    box_x1, box_y1, box_x2, box_y2 = -220, -160, 220, 160
    draw_box(dialog_layer, box_x1, box_y1, box_x2, box_y2, "gray20")

    dialog_layer.goto(box_x1, box_y1)
    dialog_layer.pendown()
    dialog_layer.pencolor("white")
    dialog_layer.goto(box_x2, box_y1)
    dialog_layer.goto(box_x2, box_y2)
    dialog_layer.goto(box_x1, box_y2)
    dialog_layer.goto(box_x1, box_y1)
    dialog_layer.penup()

    # 문구 출력 (박스 위쪽에 여백을 두고, 줄 간격 넉넉히)
    line_start_y = box_y2 - 50
    line_spacing = 32
    dialog_layer.color("white")
    for i, line in enumerate(message_lines):
        dialog_layer.goto(0, line_start_y - i * line_spacing)
        dialog_layer.write(line, align="center", font=("Arial", 14, "normal"))

    # 버튼 두 개 (예 / 아니오) - 박스 아래쪽에 배치
    button_y = box_y1 + 50
    button_positions = [(-90, button_y), (90, button_y)]
    for (bx, by), label in zip(button_positions, button_labels):
        x1, y1, x2, y2 = bx - 55, by - 20, bx + 55, by + 20
        draw_box(dialog_layer, x1, y1, x2, y2, "steelblue")
        dialog_layer.goto(bx, by - 7)
        dialog_layer.color("white")
        dialog_layer.write(label, align="center", font=("Arial", 13, "bold"))
        dialog_buttons[label] = (x1, y1, x2, y2)

    screen.update()


def point_in_box(x, y, box):
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def show_game_over_dialog(final_score):
    global dialog_active, dialog_stage
    dialog_active = True
    dialog_stage = "game_over"
    draw_dialog(
        [f"당신의 점수 : {final_score}", "", "게임을 계속 진행하시겠습니까?"],
        ["예", "아니오"]
    )


def show_confirm_exit_dialog():
    global dialog_stage
    dialog_stage = "confirm_exit"
    draw_dialog(
        ["프로그램이 종료됩니다.", "그래도 괜찮습니까?"],
        ["예", "아니오"]
    )


def close_dialog_and_restart():
    global dialog_active, dialog_stage
    dialog_layer.clear()
    dialog_active = False
    dialog_stage = None
    start_new_game()


def handle_dialog_click(x, y):
    global dialog_stage

    if dialog_stage == "game_over":
        if point_in_box(x, y, dialog_buttons.get("예", (0, 0, 0, 0))):
            close_dialog_and_restart()
        elif point_in_box(x, y, dialog_buttons.get("아니오", (0, 0, 0, 0))):
            show_confirm_exit_dialog()

    elif dialog_stage == "confirm_exit":
        if point_in_box(x, y, dialog_buttons.get("예", (0, 0, 0, 0))):
            screen.bye()
        elif point_in_box(x, y, dialog_buttons.get("아니오", (0, 0, 0, 0))):
            show_game_over_dialog(score)


def handle_click(x, y):
    global menu_open

    if dialog_active:
        handle_dialog_click(x, y)
        return

    if point_in_box(x, y, MENU_ICON_BOX):
        menu_open = not menu_open
        render_menu()
        return

    if menu_open:
        if point_in_box(x, y, menu_buttons.get("새로운 게임", (0, 0, 0, 0))):
            menu_open = False
            render_menu()
            start_new_game()
        elif point_in_box(x, y, menu_buttons.get("게임 종료하기", (0, 0, 0, 0))):
            screen.bye()
        else:
            menu_open = False
            render_menu()


screen.onclick(handle_click)
render_menu()

# =========================
# 방향키
# =========================
def go_left():
    if not ball_moving and not dialog_active:
        x = ball.xcor()
        if x > -130:
            ball.setx(x - 20)


def go_right():
    if not ball_moving and not dialog_active:
        x = ball.xcor()
        if x < 130:
            ball.setx(x + 20)


def throw_ball():
    global ball_moving, pins_before_throw
    if not ball_moving and not dialog_active:
        pins_before_throw = len(pins)
        ball_moving = True


screen.listen()
screen.onkeypress(go_left, "Left")
screen.onkeypress(go_right, "Right")
screen.onkeypress(throw_ball, "space")

# =========================
# 핀 하나 넘어뜨리기 (연쇄 반응 + 실제 충돌 판정)
# =========================
def knock_down_pin(pin):
    """핀 하나를 넘어뜨리고, 주변 핀에 물리적으로 영향을 줌"""
    if pin not in pins:
        return

    pin.color("red")
    pin.setx(pin.xcor() + random.randint(-60, 60))
    pin.sety(pin.ycor() + random.randint(-20, 40))

    pins.remove(pin)
    knocked_pins.append(pin)

    # 아직 서 있는 핀들에 대해 물리적 충돌 여부 확인
    for other_pin in pins[:]:
        distance = pin.distance(other_pin)

        if distance < COLLISION_OVERLAP_DISTANCE:
            # 실제로 겹칠 만큼 가까움 = 진짜로 부딪힌 것 -> 무조건 넘어짐
            knock_down_pin(other_pin)
        elif distance < CHAIN_REACTION_RADIUS:
            # 근처에 있음 -> 확률적으로 연쇄 반응
            if random.random() < CHAIN_REACTION_CHANCE:
                knock_down_pin(other_pin)


# =========================
# 투구 결과 처리 (볼링 규칙)
# =========================
def process_throw(pins_knocked):
    global frame_num, ball_in_frame, score, high_score

    frame = frame_results[frame_num - 1]

    if frame_num < MAX_FRAMES:
        if ball_in_frame == 1:
            if pins_knocked == 10:
                frame.append("X")
                advance_frame()
            else:
                frame.append(pins_knocked)
                ball_in_frame = 2
        else:
            frame.append(pins_knocked)
            advance_frame()
    else:
        if ball_in_frame == 1:
            frame.append("X" if pins_knocked == 10 else pins_knocked)
            ball_in_frame = 2
            if pins_knocked == 10:
                make_pins()
        elif ball_in_frame == 2:
            first = frame[0]
            first_val = 10 if first == "X" else first
            frame.append(pins_knocked)

            if first == "X":
                if pins_knocked == 10:
                    make_pins()
                ball_in_frame = 3
            elif first_val + pins_knocked == 10:
                make_pins()
                ball_in_frame = 3
            else:
                trigger_game_over()
                return
        else:
            frame.append(pins_knocked)
            trigger_game_over()
            return

    score = calculate_score()
    if score > high_score:
        high_score = score

    update_score()
    update_frame_display()


def advance_frame():
    global frame_num, ball_in_frame
    frame_num += 1
    ball_in_frame = 1
    if frame_num > MAX_FRAMES:
        trigger_game_over()
    else:
        make_pins()


def trigger_game_over():
    global score, high_score
    score = calculate_score()
    if score > high_score:
        high_score = score
    update_score()
    update_frame_display()
    show_game_over_dialog(score)


# =========================
# 게임 루프
# =========================
def game_loop():
    global ball_moving

    screen.update()

    if dialog_active:
        screen.ontimer(game_loop, 30)
        return

    if ball_moving:
        ball.sety(ball.ycor() + 12)

        for pin in pins[:]:
            if ball.distance(pin) < 25:
                knock_down_pin(pin)

        if ball.ycor() > 280:
            time.sleep(0.5)

            knocked_this_throw = pins_before_throw - len(pins)
            process_throw(knocked_this_throw)

            ball.goto(0, -260)
            ball_moving = False

    screen.ontimer(game_loop, 30)


game_loop()
screen.mainloop()