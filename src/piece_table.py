from enum import Enum

class Source(Enum):
    ORIGINAL = 0
    ADDED = 1

class Node:
    def __init__(self, next=None, prev=None, piece=None):
        self.next = next
        self.prev = prev
        self.piece = piece

    def split(self, position):
        if position == 0:
            return self.prev, self
        if position == self.piece.length:
            return self, self.next

        piece_prev, piece_next = self.piece.split(position)
        node_prev = Node(None, self.prev, piece_prev)
        node_next = Node(self.next, None, piece_next)
        node_prev.next = node_next
        node_next.prev = node_prev
        self.prev.next = node_prev
        self.next.prev = node_next
        return node_prev, node_next
    
    def insert(self, position, start, length):
        new_piece = Piece(start, length, Source.ADDED)
        if position == 0:
            new_node = Node(self, self.prev, new_piece)
            self.prev.next = new_node
            self.prev = new_node
        elif position == self.piece.length:
            new_node = Node(self.next, self, new_piece)
            self.next.prev = new_node
            self.next = new_node
        else:
            new_node = Node(piece=new_piece)
            piece_prev, piece_next = self.piece.split(position)
            node_prev = Node(new_node, self.prev, piece_prev)
            node_next = Node(self.next, new_node, piece_next)
            new_node.prev = node_prev
            new_node.next = node_next
            self.prev.next = node_prev
            self.next.prev = node_next
            

    def __repr__(self):
        return f"Node({self.piece})"
    
class Piece:
    def __init__(self, start, length, source):
        self.start = start
        self.length = length
        self.source = source
    
    def split(self, position):
        piece_prev = Piece(self.start, position, self.source)
        piece_next = Piece(self.start + position, self.length - position, self.source)
        return piece_prev, piece_next

    def __repr__(self):
        return f"Piece(start={self.start}, length={self.length}, source={self.source})"

class PieceTable:
    def __init__(self, original):
        self.original = original
        self.added = ""
        self.head = Node()
        self.tail = Node()
        original_node = Node(self.tail, self.head, Piece(0, len(self.original), Source.ORIGINAL))
        self.head.next = original_node
        self.tail.prev = original_node

    def __find_node_and_position(self, position):
        curr_postion = 0
        node = self.head.next

        while node.next:
            piece = node.piece
            curr_postion += piece.length
            if curr_postion >= position:
                break
            node = node.next
        
        if node == self.tail:
            raise Exception("Piece not found")
        
        position_in_piece = position - (curr_postion - piece.length)
        return (node, position_in_piece)

    def insert(self, position, buffer):
        node, position_in_piece = self.__find_node_and_position(position)

        self.added += buffer

        node.insert(position_in_piece, len(self.added) - len(buffer), len(buffer))

    def delete(self, position, length):
        node1, position_in_piece = self.__find_node_and_position(position)
        node1 = node1.split(position_in_piece)[0]
        
        node2, position_in_piece = self.__find_node_and_position(position + length)
        node2 = node2.split(position_in_piece)[1]

        node1.next = node2
        node2.prev = node1

    def get_buffer(self):
        p = self.head.next
        buffer = ""
        while p.next:
            piece = p.piece
            if piece.source == Source.ORIGINAL:
                buffer += self.original[piece.start:piece.start+piece.length]
            else:
                buffer += self.added[piece.start:piece.start+piece.length]
            p = p.next
    
        return buffer
        

    def __repr__(self):
        pieces = []
        p = self.head.next
        while p.next:
            pieces.append(p)
            p = p.next
        
        buffer = ""
        for piece in pieces:
            piece = piece.piece
            if piece.source == Source.ORIGINAL:
                buffer += self.original[piece.start:piece.start+piece.length]
            else:
                buffer += self.added[piece.start:piece.start+piece.length]
            
        return f"original: {self.original}\nadd: {self.added}\npieces: {pieces}\nbuffer: {buffer}"