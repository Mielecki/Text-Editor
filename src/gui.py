from tkinter import Tk, Frame, Label, Canvas, Scrollbar
from string import ascii_letters

class Line:
    def __init__(self, master, line):
        self.frame = Frame(master, borderwidth=0)
        self.content = []
        self.length = 0
        self.line = line
        self.is_first = False
        self.is_last = False
        self.pack(line)
    
    def pack(self, line):
        self.frame.grid(row = line, sticky="w")
    
    def __create_label(self):
        label = Label(self.frame, font=("UbuntuMono", 24), borderwidth=0, background="white")
        label.pack(side="left")
        return label

    def __get_character(self, index):
        return self.content[index].cget("text")
    
    def __set_character(self, index, character):
        if character == "\n":
            character = " "
        self.content[index].config(text=character)
    
    def add_character(self, character, index):
        label = self.__create_label()
        self.content.append(label)
        self.length += 1

        for i in range(self.length-1, index, -1):
            self.__set_character(i, self.__get_character(i-1))
        
        self.__set_character(index, character)

    def change_label_color(self, index, color):
        self.content[index].config(background = color)

    def remove_character(self, index):
        for i in range(index, self.length-1):
            self.__set_character(i, self.__get_character(i+1))
        self.length -= 1
        self.content.pop().destroy()

    def move_labels(self, dest, start_index):
        for i in range(start_index, self.length):
            dest.add_character(self.__get_character(i), i - start_index)
        
        for _ in range(start_index, self.length):
            self.content.pop().destroy()
        
        dest.length = self.length - start_index
        self.length = start_index


class Cursor:
    def __init__(self, line, line_position):
        self.__line_position = line_position
        self.__line = line
        self.__last_cursor = (line, 0) # line, line_position
        self.__line_changed = False
    
    def move_up(self, new_line):
        if self.__line.is_first:
            return 0
        new_line_position = self.__line_position
        new_position_change = new_line.length
        if self.__line_position > new_line.length - 1:
            new_line_position = new_line.length - 1
            new_position_change = self.__line_position + 1
        self.__line_changed = True
        self.__line_position = new_line_position
        self.__line = new_line
        self.__highlight()
        return -new_position_change

    def move_down(self, new_line, new_position=-1):
        if self.__line.is_last:
            return 0
        if new_position != -1:
            self.__line = new_line
            self.__line_position = new_position
            self.__line_changed = True
            self.__highlight()
            return 0
        new_line_position = self.__line_position
        new_position_change = self.__line.length
        if self.__line_position > new_line.length - 1:
            new_line_position = new_line.length
            new_position_change += new_line.length - self.__line_position
        self.__line_changed = True
        self.__line_position = new_line_position
        self.__line = new_line
        self.__highlight()
        return +new_position_change
    
    def move_right(self):
        if (not self.__line.is_last and self.__line_position + 1 == self.__line.length) or self.__line_position == self.__line.length:
            return 0
        self.__line_position += 1
        self.__line_changed = False
        self.__highlight()
        return 1

    def move_left(self):
        if self.__line_position == 0:
            return 0
        self.__line_position -= 1
        self.__line_changed = False
        self.__highlight()
        return -1
    
    def __highlight(self):
        if (self.__last_cursor[1] < self.__line.length or self.__line_changed) and self.__last_cursor[1] != -1:
            self.__last_cursor[0].change_label_color(self.__last_cursor[1], "white")
        if self.__line_position > 0:
            self.__line.change_label_color(self.__line_position-1, "gray")
        self.__last_cursor = (self.__line, self.__line_position-1)
    
    def get_line_postion(self):
        return self.__line_position

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
        self.__current_line = 0
        self.__lines = [Line(self.__content, self.__current_line)]
        self.__get_current_line().is_first = True
        self.__get_current_line().is_last = True
        self.__cursor = Cursor(self.__get_current_line(), self.__current_line)

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
            try:
                self.__key_events[key]()
            except KeyError:
                pass

    def __keyup(self, event):
        key = event.keysym
        if key in self.__key_history:
            self.__key_history.remove(key)

    def __update_new_piece(self, character):
        if self.__inserted_recently:
            self.__inserted_recently = False
            self.__insert_new_piece()
        self.__get_current_line().add_character(character, self.__cursor.get_line_postion())
        self.__cursor.move_right()
        self.__new_piece += character
        self.__inserted_recently = False
    
    def __insert_new_piece(self, character = None):
        if not self.__inserted_recently or character == '\n':
            self.__piece_table.insert(self.__position, self.__new_piece)
            self.__position += len(self.__new_piece)
            self.__new_piece = ""
            self.__inserted_recently = True
        if character is not None:
            self.__new_piece += character
            self.__get_current_line().add_character(character, self.__cursor.get_line_postion())
            self.__cursor.move_right()

        if character == '\n':
            self.__new_line()

    def __rearrange_lines(self):
        for i, line in enumerate(self.__lines):
            line.pack(i)
        
    def __new_line(self):
        if self.__get_current_line().is_last:
            self.__get_current_line().is_last = False
            self.__current_line += 1
            self.__lines.insert(self.__current_line, Line(self.__content, self.__current_line))
            self.__rearrange_lines()
            self.__lines[self.__current_line-1].move_labels(self.__get_current_line(), self.__cursor.get_line_postion())
            self.__cursor.move_down(self.__get_current_line())
            self.__get_current_line().is_last = True
        else:
            self.__current_line += 1
            self.__lines.insert(self.__current_line, Line(self.__content, self.__current_line))
            self.__rearrange_lines()
            self.__lines[self.__current_line-1].move_labels(self.__get_current_line(), self.__cursor.get_line_postion())
            self.__cursor.move_down(self.__get_current_line(), 0)

        
    def __move_cursor(self, direction):
        if self.__new_piece:
            self.__insert_new_piece()
        if direction == "left":
            self.__position += self.__cursor.move_left()
        elif direction == "right":
            self.__position += self.__cursor.move_right()
        elif direction == "up":
            change = self.__cursor.move_up(self.__lines[self.__current_line - 1])
            self.__position += change
            if change: self.__current_line -= 1
        elif direction == "down":
            if self.__get_current_line().is_last: return
            change = self.__cursor.move_down(self.__lines[self.__current_line + 1])
            self.__position += change
            if change: self.__current_line += 1

    def __remove_character_backspace(self):
        self.__insert_new_piece()
        if self.__cursor.get_line_postion() > 0:
            self.__piece_table.delete(self.__position-1, 1)
            self.__get_current_line().remove_character(self.__cursor.get_line_postion()-1)
            self.__position += self.__cursor.move_left()


    def __create_events(self):
        key_events = {}
        key_events.update({x: lambda x=x: self.__update_new_piece(x) for x in ascii_letters})
        key_events.update({x: lambda x=x: self.__update_new_piece(x) for x in "1234567890"})
        key_events.update({"bracketleft": lambda: self.__update_new_piece("["),
                           "bracketright": lambda: self.__update_new_piece("]"),
                           "braceleft": lambda: self.__update_new_piece("{"),
                           "braceright": lambda: self.__update_new_piece("}"),
                           "parenleft": lambda: self.__update_new_piece("("),
                           "parenright": lambda: self.__update_new_piece(")"),
                           "exclam": lambda: self.__update_new_piece("!"),
                           "quotedbl": lambda: self.__update_new_piece('"'),
                           "numbersign": lambda: self.__update_new_piece("#"),
                           "dollar": lambda: self.__update_new_piece("$"),
                           "percent": lambda: self.__update_new_piece("%"),
                           "ampersand": lambda: self.__update_new_piece("&"),
                           "apostrophe": lambda: self.__update_new_piece("'"),
                           "asterisk": lambda: self.__update_new_piece("*"),
                           "plus": lambda: self.__update_new_piece("+"),
                           "comma": lambda: self.__update_new_piece(","),
                           "minus": lambda: self.__update_new_piece("-"),
                           "period": lambda: self.__update_new_piece("."),
                           "slash": lambda: self.__update_new_piece("/"),
                           "colon": lambda: self.__update_new_piece(":"),
                           "semicolon": lambda: self.__update_new_piece(";"),
                           "less": lambda: self.__update_new_piece("<"),
                           "equal": lambda: self.__update_new_piece("="),
                           "greater": lambda: self.__update_new_piece(">"),
                           "question": lambda: self.__update_new_piece("?"),
                           "at": lambda: self.__update_new_piece("@"),
                           "backslash": lambda: self.__update_new_piece("\\"),
                           "asciicircum": lambda: self.__update_new_piece("^"),
                           "underscore": lambda: self.__update_new_piece("_"),
                           "quoteleft": lambda: self.__update_new_piece("`"),
                           "bar": lambda: self.__update_new_piece("|"),
                           "asciitilde": lambda: self.__update_new_piece("~"),
                           "grave": lambda: self.__update_new_piece("`"),
                           })
        key_events.update({"space": lambda: self.__insert_new_piece(" "),
                           "Return": lambda: self.__insert_new_piece("\n"),
                           "Left": lambda: self.__move_cursor("left"),
                           "Right": lambda: self.__move_cursor("right"),
                           "BackSpace": lambda: self.__remove_character_backspace(),
                           "Up": lambda: self.__move_cursor("up"),
                           "Down": lambda: self.__move_cursor("down"),
                           })
        return key_events

    
    def __get_current_line(self):
        return self.__lines[self.__current_line]