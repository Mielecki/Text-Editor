from tkinter import Tk, Frame, Label, Canvas, Scrollbar
from string import ascii_letters

class Line:
    def __init__(self, master):
        self.frame = Frame(master, borderwidth=0)
        self.content = []
        self.length = 0
        self.__pack()
    
    def __pack(self):
        self.frame.pack(side='top', anchor='nw', pady=1)
    
    def add_character(self, character, label, index):
        self.content.append(label)
        self.length += 1

        for i in range(self.length-1, index, -1):
            self.content[i].config(text=self.content[i-1].cget("text"))
        
        if character != "\n":
            self.content[index].config(text=character)

    def change_label_color(self, index, color):
        self.content[index].config(background = color)

    def remove_character(self, index):
        for i in range(index, self.length-1):
            self.content[i].config(text=self.content[i+1].cget("text"))
        self.length -= 1
        self.content.pop().destroy()

class Window:

    def __init__(self, width, height, piece_table):
        self.__root = Tk()
        self.__root.title("Text editor")
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.__root.geometry(f'{width}x{height}')
        self.__container = Frame(self.__root)
        self.__container.pack(fill="both", expand=True, side="top")
        self.__canvas = Canvas(self.__container)
        self.__canvas.pack(side="left", fill="both", expand=True)
        self.__scrollbar = Scrollbar(self.__canvas, orient="horizontal", command=self.__canvas.xview)
        self.__scrollbar.pack(side="bottom", fill="x")
        self.__canvas.configure(xscrollcommand=self.__scrollbar.set)
        self.__content = Frame(self.__canvas)
        self.__canvas.create_window((0, 0), window=self.__content, anchor="nw")
        self.__content.bind("<Configure>", lambda e: self.__canvas.configure(scrollregion=self.__canvas.bbox("all")))
        self.__running = False
        self.__key_events = self.__create_events()
        self.__key_history = set()
        self.__root.bind("<KeyPress>", self.__keydown)
        self.__root.bind("<KeyRelease>", self.__keyup)
        self.__piece_table = piece_table
        self.__position = 0
        self.__new_piece = ""
        self.__inserted_recently = False
        self.__lines = [Line(self.__content)]
        self.__current_line = 0
        self.__line_position = 0
        self.__last_cursor = (0, 0)
        self.__line_changed = False


    def close(self):
        self.__running = False

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True

        while self.__running:
            self.redraw()
    
    def __keydown(self, event):
        key = event.keysym
        if not key in self.__key_history:
            self.__key_history.add(key)
            self.__key_events[key]()

        print(self.__piece_table)

    def __keyup(self, event):
        key = event.keysym
        if key in self.__key_history:
            self.__key_history.remove(key)

    def __create_label(self):
        label = Label(self.__lines[self.__current_line].frame, font=("Helvetica", 24), borderwidth=0, background="white")
        label.pack(side="left")
        return label

    def __update_new_piece(self, character):
        self.__lines[self.__current_line].add_character(character, self.__create_label(), self.__line_position)
        self.__line_position += 1
        self.__highlight_cursor()
        self.__new_piece += character
        self.__inserted_recently = False
    
    def __insert_new_piece(self, character = None):
        if character == '\n':
            self.__new_line()
            self.__inserted_recently = False
        if not self.__inserted_recently:
            self.__piece_table.insert(self.__position, self.__new_piece)
            self.__position += len(self.__new_piece)
            self.__new_piece = ""
            self.__inserted_recently = True
        if character is not None:
            self.__new_piece += character
            self.__lines[self.__current_line].add_character(character, self.__create_label(), self.__line_position)
            self.__line_position += 1
            self.__highlight_cursor()
            self.__line_changed = False
        
    def __new_line(self):
        self.__line_position = 0
        self.__current_line += 1
        self.__line_changed = True
        if self.__current_line >= len(self.__lines):
            self.__lines.append(Line(self.__content))
        
    def __move_cursor(self, direction):
        if self.__new_piece:
            self.__insert_new_piece()
        if direction == "left":
            if self.__line_position > 0:
                self.__position -= 1
                self.__line_position -= 1
                self.__highlight_cursor()
        elif direction == "right":
            if self.__line_position < self.__lines[self.__current_line].length:
                self.__position += 1
                self.__line_position += 1
                self.__highlight_cursor()
    
    def __remove_character_backspace(self):
        self.__insert_new_piece()
        if self.__line_position > 0:
            self.__piece_table.delete(self.__position-1, 1)
            self.__lines[self.__current_line].remove_character(self.__line_position-1)
            if self.__line_position > self.__lines[self.__current_line].length:
                self.__line_position -= 1
                self.__position -= 1
                self.__highlight_cursor()


    def __create_events(self):
        key_events = {}
        key_events = {x: lambda x=x: self.__update_new_piece(x) for x in ascii_letters}
        key_events.update({"space": lambda: self.__insert_new_piece(" "),
                           "Return": lambda: self.__insert_new_piece("\n"),
                           "Left": lambda: self.__move_cursor("left"),
                           "Right": lambda: self.__move_cursor("right"),
                           "BackSpace": lambda: self.__remove_character_backspace(),
                           })
        #             "Shift_L": lambda: False,
        return key_events
    
    def __highlight_cursor(self):
        if self.__last_cursor[1] < self.__get_current_line().length or self.__line_changed:
            self.__lines[self.__last_cursor[0]].change_label_color(self.__last_cursor[1], "white")
        if self.__line_position > 0:
            self.__lines[self.__current_line].change_label_color(self.__line_position-1, "gray")
        self.__last_cursor = (self.__current_line, self.__line_position-1)

    
    def __get_current_line(self):
        return self.__lines[self.__current_line]