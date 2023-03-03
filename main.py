import time
from ui import *
from group import *
import os

class state:
    last_hover = None
    chosen_header = None
    multi_table = None
    pos_immutable = []
    information_panel = None

class sound:
    uncover = pygame.mixer.Sound('sound\\uncover.wav')
    right = pygame.mixer.Sound('sound\\right.mp3')
    wrong = pygame.mixer.Sound('sound\\wrong.wav')
    erase = pygame.mixer.Sound('sound\\erase.wav')
    swap = pygame.mixer.Sound('sound\\swap.mp3')

class multiplication_table(Group):
    def __init__(self, in_page, pos: tuple, group=None, size=(400, 400), header=True, show_number=True):
        super().__init__()
        if group:
            self.order, self.name, self.content = group.order, group.name, group.content.copy()
        self.in_page, self.pos, self.size, self.header = in_page, pos, size, header
        self.blocks, self.headers = [], []
        self.show_number = show_number
        self.draw()

    def __setitem__(self, pos, value):
        super().__setitem__(pos, value)
        self.complete_info()
        self.draw()

    def swap_element(self, element1, element2):
        super().swap_element(element1, element2)
        self.complete_info()
        self.draw()

    def clear_blocks(self):
        for block in sum(self.blocks, []) + self.headers:
            block.remove()
        self.blocks, self.headers = [], []

    def element_color(self, element: int, light=180):
        if element == -1:
            return color.background_black
        length = self.order / 3.
        gr, bl, re = length, length * 2, length * 3
        if element < gr:
            return light - element / length * light, element / length * light, 0
        elif element < bl:
            return 0, light - (element - gr) / length * light, (element - gr) / length * light
        else:
            return (element - bl) / length * light, 0, light - (element - bl) / length * light

    def font_size(self):
        return int(min(self.size) / self.order / 2)

    def draw(self):
        self.clear_blocks()
        order_with_header = self.order + 1 if self.header else self.order
        left_top = tuple_plus(self.pos, multiply(self.size, -0.5), multiply(self.size, 0.5 / order_with_header))
        for row_number, row in enumerate(self.rows()):
            self.blocks.append([])
            for column_number, element in enumerate(row):
                new_block = Block(self.in_page, tuple_plus(left_top, ((column_number + self.header) / order_with_header * self.size[0], (row_number + self.header) / order_with_header * self.size[1])),
                                  back_color=self.element_color(element), text=f"{element}" if self.show_number and element != -1 else "", font_size=self.font_size(), size=multiply(self.size, 1 / order_with_header))
                new_block.info.update({"multitable": self, "button_name": "multi", "pos": (row_number, column_number), "respond_hover_font": True, "respond_hover_border": True})
                self.blocks[row_number].append(new_block)
        if self.header:
            for row_number in range(self.order):
                new_block = Block(self.in_page, tuple_plus(left_top, (0, (row_number + 1) / order_with_header * self.size[1])),
                                  back_color=self.element_color(row_number, 150), text=f"{row_number}", font_size=self.font_size(), size=multiply(self.size, 1 / order_with_header), text_color=color.font_header_grey)
                new_block.info.update({"multitable": self, "button_name": "header", "pos": row_number})
                self.headers.append(new_block)
            for column_number in range(self.order):
                new_block = Block(self.in_page, tuple_plus(left_top, ((column_number + 1) / order_with_header * self.size[0], 0)),
                                  back_color=self.element_color(column_number, 150), text=f"{column_number}", font_size=self.font_size(), size=multiply(self.size, 1 / order_with_header), text_color=color.font_header_grey)
                new_block.info.update({"multitable": self, "button_name": "header", "pos": column_number})
                self.headers.append(new_block)

def draw_group_card(g: Group, in_page: int, pos: tuple, size: tuple, description=""):
    multiplication_table(in_page, tuple_plus(pos, (size[0] / 4, 0)), g, header=False, size=(size[0] / 2 - 5, size[1] - 5), show_number=g.order < 10)
    Block(in_page, tuple_plus(pos, (-size[0] / 4, -size[1] / 8)), size=(size[0] / 2, size[1] / 4), text=f"Order {g.order}", text_only=True, font_size=25)
    Block(in_page, tuple_plus(pos, (-size[0] / 4, -size[1] / 8 * 3)), size=(size[0] / 2, size[1] / 4), text=f"Name {g.name}", text_only=True, font_size=25)
    Block(in_page, tuple_plus(pos, (-size[0] / 4, size[1] / 4)), size=multiply(size, 0.5), text=description, text_only=True, font_size=25)
    Block(in_page, pos, size=size, layer=-1, border_width=3)

@subscribe_event("start_game")
def initialization(event):
    if not os.path.exists("save.txt"):
        with open("save.txt", 'w') as new_save:
            new_save.write("1\n0,0,0,0,0,0,0,0,0,0,0\n")
    if not os.path.exists("settings.txt"):
        with open("settings.txt", 'w') as new_settings:
            new_settings.write("1\n")
    # main menu
    new_button = Block(PAGE_MAIN_MENU, (0, -100), (150, 60), text_color=color.font_white, text="Start Game", text_only=True)
    new_button.info.update({"respond_hover_font": True, "button_name": "start game"})
    new_button = Block(PAGE_MAIN_MENU, (0, 0), (150, 60), text_color=color.font_white, text="Gallery", text_only=True)
    new_button.info.update({"respond_hover_font": True, "button_name": "gallery"})
    new_button = Block(PAGE_MAIN_MENU, (0, 100), (150, 60), text_color=color.font_white, text="Settings", text_only=True)
    new_button.info.update({"respond_hover_font": True, "button_name": "settings"})
    new_button = Block(PAGE_MAIN_MENU, (0, 200), (150, 60), text_color=color.font_white, text="Exit", text_only=True)
    new_button.info.update({"respond_hover_font": True, "button_name": "exit"})
    Block(PAGE_MAIN_MENU, (-250, 25), picture="triangle.jpg", layer=-1)
    Block(PAGE_MAIN_MENU, (0, -250), picture="title.png", layer=-1)

@subscribe_event("hover")
def __on_hover(event):
    if event.self.info.get("respond_hover_font"):
        event.self.text_color = color.font_yellow
    if event.self.info.get("respond_hover_border"):
        event.self.border_width = 2
    if event.self.info.get("button_name") == "multi":
        state.last_hover = event.self
        if page.current_page == PAGE_EXPLORATION or page.current_page == PAGE_PUZZLE:
            state.information_panel.text = f"Order\n {state.multi_table.order_of.get(state.multi_table[event.self.info.get('pos')])}\n" \
                                           f"Conjugates\n {string_of(state.multi_table.conjugates_of.get(state.multi_table[event.self.info.get('pos')]))}\n" \
                                           f"Centralizer\n {string_of(state.multi_table.centralizer_of.get(state.multi_table[event.self.info.get('pos')]))}"

@subscribe_event("cancel_hover")
def __on_cancel_hover(event):
    if event.self.info.get("respond_hover_font"):
        event.self.text_color = color.font_white
    if event.self.info.get("respond_hover_border"):
        event.self.border_width = 0

@subscribe_event("click")
def on_click(event):
    if event.self.info.get("button_name") == "exit":
        exit()
    elif event.self.info.get("button_name") == "start game":
        discovered_groups = load_discovered_group_names()
        solved_puzzles = load_solved_puzzles()
        for order_index, level_order in enumerate(level_orders):
            discovered_number = sum(group.name in discovered_groups for group in groups_by_order[level_order])
            Block(PAGE_GAME_MENU, (-300, -300 + 100 * order_index), (200, 0), text_only=True, text=f"Order {level_order}")
            new_button = Block(PAGE_GAME_MENU, (-50, -300 + 100 * order_index), (200, 60), text_only=True,
                               text=f"Discovered {discovered_number}/{len(groups_by_order[level_order])}")
            new_button.info.update({"respond_hover_font": True, "button_name": "explore", "level_order": level_order})
            new_button = Block(PAGE_GAME_MENU, (200, -300 + 100 * order_index), (200, 60), text_only=True,
                               text=f"Puzzle {solved_puzzles[order_index]}/{total_puzzles[level_order]}")
            new_button.info.update({"respond_hover_font": True, "button_name": "puzzle", "level_order": level_order})
            new_window = Block(PAGE_GAME_MENU, (0, -300 + 100 * order_index), (800, 90), back_color=color.background_black, border_color=color.border_brown, layer=-1)
            new_window.info.update({"respond_hover_border": True})
        page.set_page(PAGE_GAME_MENU)
        camera.scroll = True
    elif event.self.info.get("button_name") == "gallery":
        discovered_groups = load_discovered_group_names()
        group_index = 0
        for order in range(1, 21):
            for group_name in [gr.name for gr in groups_by_order[order]]:
                if group_name in discovered_groups:
                    draw_group_card(groups_by_name[group_name], PAGE_GALLERY, (-250 + 500 * (group_index % 2), -230 + 280 * (group_index // 2)), (450, 250), description=groups_by_name[group_name].short_description)
                else:
                    Block(PAGE_GALLERY, (-250 + 500 * (group_index % 2), -230 + 280 * (group_index // 2)), size=(450, 250), text_only=True, text="?", font_size=60)
                group_index += 1
        page.set_page(PAGE_GALLERY)
        camera.scroll = True
        camera.boundary = ((0, 0), (0, 5000))
    elif event.self.info.get("button_name") == "settings":
        page.current_page = PAGE_SETTINGS
        new_block = Block(PAGE_SETTINGS, (0, -100), (240, 60), text=f"screenshot -  {['off', 'on'][int(load_settings_of_line(SET_SCREENSHOT))]}", text_only=True)
        new_block.info.update({"button_name": "screenshot", "respond_hover_font": True})
    elif event.self.info.get("button_name") == "screenshot":
        if load_settings_of_line(SET_SCREENSHOT) == "0":
            write_settings_of_line(SET_SCREENSHOT, "1")
            event.self.text = "screenshot -  on"
        else:
            write_settings_of_line(SET_SCREENSHOT, "0")
            event.self.text = "screenshot -  off"
    elif event.self.info.get("button_name") == "explore":
        level = event.self.info.get("level_order")
        state.multi_table = multiplication_table(PAGE_EXPLORATION, (-50, 0), header=True, size=(640 + level * 3, 640 + level * 3), group=empty_group_of_order(level))
        new_block = Block(PAGE_EXPLORATION, (410, 320), (120, 60), text="Submit")
        new_block.info.update({"button_name": "submit", "respond_hover_border": True})
        state.information_panel = Block(PAGE_EXPLORATION, (410, -100), (120, 80), text_only=True, font_size=25)
        clear_page(page.current_page)
        page.set_page(PAGE_EXPLORATION)
        camera.scroll = False
        camera.set_pos((0, 0))
    elif event.self.info.get("button_name") == "submit":
        right = state.multi_table.is_group()
        if right:
            if load_settings_of_line(SET_SCREENSHOT) == "1":
                time_str = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())
                file_name = '%s.png' % time_str
                pygame.image.save(window, f'records\\{file_name}')
            event.self.info["button_name"] = "win"
            event.self.text = "You win!"
            sound.right.play()
            if page.current_page == PAGE_PUZZLE:
                solved_puzzle_increment(state.multi_table.order)
            state.multi_table.complete_info()
            completed_group = group_identify(state.multi_table)
            normal_series_tuple = state.multi_table.normal_series()
            is_new = completed_group not in load_discovered_group_names()
            for gr in normal_series_tuple[1]:
                gr_name = group_identify(groups_by_name[gr])
                if gr_name not in load_discovered_group_names():
                    record_new_group(gr_name)
            if is_new:
                msg_box(f"Congratulations!\nThis new group is {completed_group}.\nNormal series:\n{normal_series_tuple[0]}")
            else:
                msg_box(f"This group is {completed_group}.\nYou've discovered it before.\nNormal series:\n{normal_series_tuple[0]}")
        else:
            sound.wrong.play()
    elif event.self.info.get("button_name") == "puzzle" and "0/0" not in event.self.text:
        level = event.self.info.get("level_order")
        state.multi_table = multiplication_table(PAGE_PUZZLE, (-50, 0), header=True, size=(640 + level * 3, 640 + level * 3), group=empty_group_of_order(level))
        new_block = Block(PAGE_PUZZLE, (410, 320), (120, 60), text="Submit")
        new_block.info.update({"button_name": "submit", "respond_hover_border": True})
        state.information_panel = Block(PAGE_PUZZLE, (410, -100), (120, 80), text_only=True, font_size=25)
        puzzle_files = os.listdir(os.path.join("puzzle", f"{level}"))
        puzzle_solved = int(load_solved_puzzles()[level_orders.index(level)])
        with open(os.path.join("puzzle", f"{level}", puzzle_files[puzzle_solved if puzzle_solved < len(puzzle_files) else random.randint(0, len(puzzle_files) - 1)])) as puzzle_file:
            puzzle_content = [line.replace("\n", "") for line in puzzle_file.readlines() if line.replace(" ", "") != "\n"]
        state.pos_immutable = []
        for line in puzzle_content[:-1]:
            table_info = line.replace("=", ",").replace(" ", "").split(",")
            state.multi_table[int(table_info[0]), int(table_info[1])] = int(table_info[2])
            state.pos_immutable.append((int(table_info[0]), int(table_info[1])))
        Block(PAGE_PUZZLE, (410, -320), (80, 80), picture="hint.png", tooltip=puzzle_content[-1], picture_fit=True)
        clear_page(page.current_page)
        page.set_page(PAGE_PUZZLE)
        camera.scroll = False
        camera.set_pos((0, 0))
    elif page.current_page == PAGE_EXPLORATION or page.current_page == PAGE_PUZZLE:
        if event.self.info.get("button_name") == "header":
            if state.chosen_header:
                pos0, pos1 = state.chosen_header.info.get("pos"), event.self.info.get("pos")
                state.multi_table.swap_element(pos0, pos1)
                if page.current_page == PAGE_PUZZLE:
                    for pos_index, pos in enumerate(state.pos_immutable):
                        result_tuple = list(pos)
                        for i in [0, 1]:
                            result_tuple[i] = pos1 if pos[i] == pos0 else pos0 if pos[i] == pos1 else pos[i]
                        state.pos_immutable[pos_index] = tuple(result_tuple)
                state.chosen_header = None
                if pos0 != pos1:
                    sound.swap.play()
            else:
                state.chosen_header = event.self
                event.self.border_width = 3
        elif state.chosen_header:
            state.chosen_header.border_width = 0
            state.chosen_header = None

@subscribe_event("key_down")
def on_key_down(event):
    key = event.key
    if key == pygame.K_ESCAPE and page.current_page != PAGE_MAIN_MENU:
        clear_page(page.current_page)
        page.set_page(PAGE_MAIN_MENU)
        camera.scroll = False
        camera.set_pos((0, 0))
        camera.boundary = ((0, 0), (0, 500))
    elif 48 <= key <= 57 and (page.current_page == PAGE_EXPLORATION or
                              page.current_page == PAGE_PUZZLE and state.last_hover.info.get("pos") not in state.pos_immutable):
        table_pos = state.last_hover.info.get("pos")
        table = state.last_hover.info.get("multitable")
        if table[table_pos] < 0:
            sound.uncover.play()
        pre_value = max(table[table_pos], 0)
        new_value = pre_value * 10 + key - 48
        if new_value < table.order:
            table[table_pos] = new_value
    elif key == pygame.K_BACKSPACE and (page.current_page == PAGE_EXPLORATION or
                                        page.current_page == PAGE_PUZZLE and state.last_hover.info.get("pos") not in state.pos_immutable):
        table_pos = state.last_hover.info.get("pos")
        table = state.multi_table
        pre_value = max(table[table_pos], 0)
        table[table_pos] = pre_value // 10 if pre_value > 9 else -1
        sound.erase.play()

def load_discovered_group_names() -> list:
    with open("save.txt", "r") as save_file:
        save_content = [line.replace("\n", "") for line in save_file.readlines()]
    return save_content[SAVE_DISCOVERED_GROUPS].split(",")

def load_solved_puzzles() -> list:
    with open("save.txt", "r") as save_file:
        save_content = [line.replace("\n", "") for line in save_file.readlines()]
    return save_content[SAVE_SOLVED_PUZZLES].split(",")

def solved_puzzle_increment(level_order):
    with open("save.txt", "r") as save_file:
        lines = save_file.readlines()
        split_line = lines[1].split(",")
        level_index = level_orders.index(level_order)
        split_line[level_index] = f"{min(int(split_line[level_index]) + 1, total_puzzles[level_order])}"
        lines[1] = ",".join(split_line)
        write_content = "".join(lines)
    with open("save.txt", "w") as save_file:
        save_file.write(write_content)

def record_new_group(group_name):
    with open("save.txt", "r") as save_file:
        lines = save_file.readlines()
        lines[0] = f'''{group_name},{lines[0]}'''
    write_content = "".join(lines)
    with open("save.txt", "w") as save_file:
        save_file.write(write_content)

def load_settings_of_line(line_number: int):
    with open("settings.txt", "r") as settings_file:
        content = settings_file.readlines()
    return content[line_number]

def write_settings_of_line(line_number: int, content: str):
    with open("settings.txt", "r") as settings_file:
        lines = settings_file.readlines()
        lines[line_number] = content
    write_content = "".join(lines)
    with open("settings.txt", "w") as settings_file:
        settings_file.write(write_content)

PAGE_MAIN_MENU, PAGE_GAME_MENU, PAGE_GALLERY, PAGE_EXPLORATION, PAGE_PUZZLE, PAGE_SETTINGS = 0, 1, 2, 3, 4, 5
SAVE_DISCOVERED_GROUPS, SAVE_SOLVED_PUZZLES = 0, 1
SET_SCREENSHOT = 0
level_orders = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
total_puzzles = {level_order: len(os.listdir(os.path.join("puzzle", f"{level_order}"))) for level_order in level_orders}
start_game()
