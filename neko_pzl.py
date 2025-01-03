import tkinter
import random

# グローバル変数
mouse_x = 0
mouse_y = 0
dragging = False
drag_start_x = 0
drag_start_y = 0
drag_item = 0
current_x = 0
current_y = 0
clearing_in_progress = False
marked_sets = []

# マウス移動時
def mouse_move(e):
    global mouse_x, mouse_y
    mouse_x = e.x
    mouse_y = e.y
    if dragging:
        drag_update()

# ドラッグ開始
def drag_start(e):
    global dragging, drag_start_x, drag_start_y, drag_item, current_x, current_y
    if 24 <= e.x < 24 + 72 * 8 and 24 <= e.y < 24 + 72 * 10:
        drag_start_x = (e.x - 24) // 72
        drag_start_y = (e.y - 24) // 72
        drag_item = neko[drag_start_y][drag_start_x]
        current_x, current_y = drag_start_x, drag_start_y
        if drag_item > 0:
            dragging = True

# ドラッグ終了
def drag_end(e):
    global dragging, drag_item
    if clearing_in_progress:
        return  # 消去中は操作無効
    dragging = False
    drag_item = 0
    check_and_process_matches()

# ドラッグ中の更新
def drag_update():
    global current_x, current_y
    if 24 <= mouse_x < 24 + 72 * 8 and 24 <= mouse_y < 24 + 72 * 10:
        new_x = (mouse_x - 24) // 72
        new_y = (mouse_y - 24) // 72
        if abs(new_x - current_x) + abs(new_y - current_y) == 1:  # 隣接している場合
            # ドロップを入れ替える
            neko[current_y][current_x], neko[new_y][new_x] = neko[new_y][new_x], neko[current_y][current_x]
            update_neko(new_x, new_y)
            update_neko(current_x, current_y)
            current_x, current_y = new_x, new_y  # 現在位置を更新

# 揃いチェックと処理開始
def check_and_process_matches():
    global clearing_in_progress, marked_sets
    clearing_in_progress = True
    marked_sets = find_matches()
    if marked_sets:
        process_next_match()
    else:
        clearing_in_progress = False

# 揃いの探索
def find_matches():
    matches = []
    checked = [[False] * 8 for _ in range(10)]

    # 縦揃いチェック
    for x in range(8):
        count = 0
        for y in range(10):
            if y == 0 or neko[y][x] != neko[y-1][x] or neko[y][x] == 0:
                if count >= 3:
                    matches.append([(y-i-1, x) for i in range(count)])
                count = 0
            count += 1
        if count >= 3:
            matches.append([(10-i-1, x) for i in range(count)])

    # 横揃いチェック
    for y in range(10):
        count = 0
        for x in range(8):
            if x == 0 or neko[y][x] != neko[y][x-1] or neko[y][x] == 0:
                if count >= 3:
                    matches.append([(y, x-i-1) for i in range(count)])
                count = 0
            count += 1
        if count >= 3:
            matches.append([(y, 8-i-1) for i in range(count)])

    return matches

# 次の揃いを処理
def process_next_match():
    if not marked_sets:
        root.after(500, drop_and_refill)  # 揃いがなくなったら補充
        return

    match = marked_sets.pop(0)  # 次の揃いを取得
    for y, x in match:
        neko[y][x] = 7
        update_neko(x, y)
    root.after(500, lambda: remove_match(match))

# 揃いの消去
def remove_match(match):
    for y, x in match:
        neko[y][x] = 0
        update_neko(x, y)
    process_next_match()

# ドロップを落とし、新しいドロップを補充
def drop_and_refill():
    for x in range(8):
        stack = [neko[y][x] for y in range(10) if neko[y][x] > 0]
        for y in range(9, -1, -1):
            if stack:
                neko[y][x] = stack.pop()
            else:
                neko[y][x] = random.randint(1, 6)
            update_neko(x, y)
    root.after(500, check_after_refill)

# 補充後に再チェック
def check_after_refill():
    if check_and_process_matches():  # 再び揃ったドロップがある場合
        process_next_match()
    else:
        global clearing_in_progress
        clearing_in_progress = False  # 消去処理終了

# 特定のドロップのみ更新
def update_neko(x, y):
    cvs.delete(f"NEKO_{x}_{y}")
    if neko[y][x] > 0:
        img = img_neko[neko[y][x]]
        cvs.create_image(x * 72 + 60, y * 72 + 60, image=img, tag=f"NEKO_{x}_{y}")

# 初期盤面生成
def initialize_board():
    for y in range(10):
        for x in range(8):
            while True:
                rand = random.randint(1, 6)
                if (x >= 2 and rand == neko[y][x-1] and rand == neko[y][x-2]) or \
                (y >= 2 and rand == neko[y-1][x] and rand == neko[y-2][x]):
                    continue
                neko[y][x] = rand
                break

# ゲームメイン処理
def game_main():
    root.after(100, game_main)

# 初期化
neko = [[0 for _ in range(8)] for _ in range(10)]
root = tkinter.Tk()
root.title("パズルゲーム")
root.resizable(False, False)
root.bind("<Motion>", mouse_move)
root.bind("<ButtonPress-1>", drag_start)
root.bind("<ButtonRelease-1>", drag_end)
cvs = tkinter.Canvas(root, width=912, height=768)
cvs.pack()

bg = tkinter.PhotoImage(file="neko_bg.png")
img_neko = [
    None,
    tkinter.PhotoImage(file="neko1.png"),
    tkinter.PhotoImage(file="neko2.png"),
    tkinter.PhotoImage(file="neko3.png"),
    tkinter.PhotoImage(file="neko4.png"),
    tkinter.PhotoImage(file="neko5.png"),
    tkinter.PhotoImage(file="neko6.png"),
    tkinter.PhotoImage(file="neko_niku.png"),  # 消去時の画像
]

# 背景と初期盤面を設定
cvs.create_image(456, 384, image=bg)
initialize_board()
for y in range(10):
    for x in range(8):
        update_neko(x, y)

game_main()
root.mainloop()
