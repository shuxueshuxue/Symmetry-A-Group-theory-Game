import os
import pygame
from mathtools import *

class color:
    button_background_grey = (50, 50, 50)
    tool_tip_purple = (30, 0, 70)
    tool_tip_orange = (220, 120, 0)
    font_white = (180, 180, 180)
    font_header_grey = (160, 160, 160)
    font_yellow = (200, 200, 100)
    border_brown = (160, 82, 45)
    border_grey = (100, 100, 100)
    background_black = (0, 0, 0)

event_processors = dict()

def register_event(func):
    def new_func(*args):
        event_info = {"name": func.__name__}
        event_info.update(zip(func.__code__.co_varnames, args))
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, event_info))
        func(*args)
    return new_func

def subscribe_event(*event_names):
    def new_decorator(func):
        for event_name in event_names:
            if event_name in event_processors:
                event_processors[event_name].append(func)
            else:
                event_processors[event_name] = [func]
        return func
    return new_decorator

class page:
    current_page = 0

    @staticmethod
    def set_page(new_page: int):
        page.current_page = new_page

class camera:
    pos = (0, 0) # this refers to the center of the screen
    scroll = False
    boundary = ((0, 0), (0, 500))

    @staticmethod
    @register_event
    def set_pos(new_pos):
        camera.pos = new_pos

def blit_text(pos: tuple, width, font_size: int, text, text_color=color.font_white):
    temp_font = FONT_ARIAL[font_size]
    white_space = temp_font.render(" ", False, (0, 0, 0))
    white_space_width = white_space.get_size()[0]
    # general thought: split the words and render them one by one, if the total length surpasses the width of
    # the object, then change to the next line
    words = []  # words[line number][word's index in the line]
    text = text.replace("\n", " \n ")
    split_text = text.split(" ")
    words_from_text = [temp_font.render(word, True, text_color) for word in split_text]
    line_lengths = []
    line_count = 0
    word_index = 0
    while word_index < len(words_from_text):
        new_word = words_from_text[word_index]
        if split_text[word_index] == "\n":
            word_index += 1
            new_word = words_from_text[word_index]
        line_length = new_word.get_size()[0]
        words.append([new_word])
        word_index += 1
        if not word_index == len(words_from_text):
            new_word = words_from_text[word_index]
            while line_length + white_space_width + new_word.get_size()[0] <= width:
                if split_text[word_index] == "\n":
                    break
                line_length += white_space_width + new_word.get_size()[0]
                words[line_count].append(new_word)
                word_index += 1
                if word_index == len(words_from_text):
                    break
                new_word = words_from_text[word_index]
        line_count += 1
        line_lengths.append(line_length)
    font_height = temp_font.render("x", False, (0, 0, 0)).get_size()[1]
    for line_index, line_words in enumerate(words):
        pos_y = pos[1] + font_height * (line_index - line_count / 2)
        pos_x = pos[0] - line_lengths[line_index] / 2
        line_length = 0
        for word in line_words:
            window.blit(word, screen_pos_from_real_pos((pos_x + line_length, pos_y)))
            line_length += word.get_size()[0] + white_space_width

class Block:
    all = []
    in_layer = {layer: [] for layer in range(-5, 6)}

    def __init__(self, in_page, pos, size=(100, 100), back_color=color.button_background_grey, name='', hidden=False, picture="",
                 picture_fit=False, text="", font_size=32, text_only=False, text_color=color.font_white, layer=0, border_width=0, border_color=color.border_brown,
                 tooltip=""):
        self.id = len(Block.all)
        Block.all.append(self)
        self.layer = layer
        Block.in_layer[self.layer].append(self)
        self.in_page = in_page
        self.pos = pos  # pos = coordinates of its center
        self.size, self.color = size, back_color
        self.name = name
        self.hidden = hidden
        self.picture = pictures.get(picture)
        if picture_fit:
            self.picture = pygame.transform.scale(self.picture, self.size)
        self.text, self.font_size, self.text_only, self.text_color = text, font_size, text_only, text_color
        self.hovered = False
        self.border_width, self.border_color = border_width, border_color
        self.tooltip = tooltip
        self.info = {}

    def blit(self):
        if not self.text_only:
            if self.picture:
                window.blit(self.picture, tuple_plus(screen_pos_from_real_pos(self.pos), multiply(self.picture.get_size(), -0.5)))
            else:
                pygame.draw.rect(window, self.color, pygame.Rect(tuple_plus(screen_pos_from_real_pos(self.pos), multiply(self.size, -0.5)), self.size))
                if self.border_width:
                    pygame.draw.rect(window, self.border_color, pygame.Rect(tuple_plus(screen_pos_from_real_pos(self.pos), multiply(self.size, -0.5)), self.size), width=self.border_width)
        if self.text:
            blit_text(self.pos, self.size[0], self.font_size, self.text, self.text_color)

    def display_tool_tip(self):
        pygame.draw.rect(window, color.tool_tip_purple, pygame.Rect(
            tuple_plus(pygame.mouse.get_pos(), (25 if pygame.mouse.get_pos()[0] < 730 else -285, 15)), (270, 100)))
        blit_text(tuple_plus(real_pos_from_screen_pos(pygame.mouse.get_pos()), (160 if pygame.mouse.get_pos()[0] < 730 else -150, 65)), 270, 20, self.tooltip, text_color=color.tool_tip_orange)

    @staticmethod
    def blit_all(ignore_hidden=False):
        for layer_number in range(-5, 6):
            for block in Block.in_layer[layer_number]:
                if block.in_page == page.current_page and (not block.hidden or ignore_hidden) and \
                        abs(block.pos[1] - camera.pos[1]) < SCREEN_CENTER[1] + block.size[1] / 2 and \
                        abs(block.pos[0] - camera.pos[0]) < SCREEN_CENTER[0] + block.size[0] / 2:
                    block.blit()
        for layer_number in range(-5, 6):
            for block in Block.in_layer[layer_number]:
                if block.tooltip and block.in_page == page.current_page and block.is_collide(real_pos_from_screen_pos(pygame.mouse.get_pos())):
                    block.display_tool_tip()
                    return

    def is_collide(self, pos):
        return abs(self.pos[0] - pos[0]) <= self.size[0] / 2 and abs(self.pos[1] - pos[1]) <= self.size[1] / 2

    @register_event
    def click(self, pos):
        pass

    def change_layer(self, layer):
        Block.in_layer[self.layer].remove(self)
        self.layer = layer
        Block.in_layer[self.layer].append(self)

    def remove(self):
        Block.all.remove(self)
        Block.in_layer[self.layer].remove(self)

    @register_event
    def hover(self):
        self.hovered = True

    @register_event
    def cancel_hover(self):
        self.hovered = False

@register_event
def start_game():
    while True:
        Block.blit_all()
        pygame.display.flip()
        clock.tick(FPS)
        for block in Block.all:
            if block.in_page == page.current_page:
                if block.is_collide(real_pos_from_screen_pos(pygame.mouse.get_pos())):
                    if not block.hovered:
                        block.hover()
                else:
                    if block.hovered:
                        block.cancel_hover()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                key_down(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    flag = False
                    for layer_number in range(5, -6, -1):
                        for block in Block.in_layer[layer_number]:
                            if block.in_page == page.current_page:
                                if block.is_collide(real_pos_from_screen_pos(event.pos)):
                                    block.click(real_pos_from_screen_pos(event.pos))
                                    flag = True
                                    break
                        if flag:
                            break
            if event.type == pygame.MOUSEWHEEL:
                if camera.scroll:
                    camera.set_pos((camera.pos[0], max(camera.boundary[0][1], min(camera.pos[1] + event.y * -20, camera.boundary[1][1]))))
            if "name" in event.__dir__() and event.name in event_processors:
                for processor in event_processors[event.name]:
                    processor(event)
        window.fill(color.background_black)


def clear_page(page_number):
    for block in [bloc for bloc in Block.all if bloc.in_page == page_number]:
        block.remove()

def msg_box(msg: str):
    new_msg_box = Block(page.current_page, (0, -50), (500, 300), layer=1, border_width=3, border_color=color.border_grey)
    new_msg_text = Block(page.current_page, (0, -70), (500, 250), text=msg, text_only=True, layer=1)
    new_msg_box_button = Block(page.current_page, (0, 65), (100, 50), text="Confirm", layer=2, border_width=2, border_color=color.border_grey, font_size=25)
    new_msg_box_button.info.update({"msg_box": new_msg_box, "msg_text": new_msg_text})

@subscribe_event("click")
def click_msg_box(event):
    if event.self.info.get("msg_box"):
        event.self.info.get("msg_box").remove()
        event.self.info.get("msg_text").remove()
        event.self.remove()

@register_event
def key_down(key):
    pass


WINDOW_SIZE = (1024, 768)
SCREEN_CENTER = (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)
FPS = 30

pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(WINDOW_SIZE)
pictures = {image_name: pygame.image.load(os.path.join("image", image_name)) for image_name in os.listdir("image")}
FONT_ARIAL = [pygame.font.SysFont("arial", __font_size) for __font_size in range(200)] # preload to pretend retarding

def real_pos_from_screen_pos(screen_pos):
    return tuple_plus(screen_pos, camera.pos, negative(SCREEN_CENTER))

def screen_pos_from_real_pos(real_pos):
    return tuple_plus(real_pos, negative(camera.pos), SCREEN_CENTER)

if __name__ == "__main__":
    start_game()
