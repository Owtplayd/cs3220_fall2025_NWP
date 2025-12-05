from collections import defaultdict

class Board5Misery(defaultdict):
    """A board has the current value of the counter,
    the player to move, 
    a cached utility value, 
    where player is 'X' or 'O'."""
  
    
    def __init__(self, counter=1, to_move=None, utility=0):
        #print(f"!!!{to_move}")
        self.__dict__.update(counter=counter, to_move=to_move, utility=utility)
        
        
        
    def new(self, player, act) -> 'Board5Misery':
        #print(f"the {player}")
        board = Board5Misery(counter=self.counter+act, to_move=player) 

        board.update(self)
        return board
        

    
    def __repr__(self):
        return f"state ({self.counter,self.to_move})"
        #def row(y): return ' '.join(self[x, y] for x in range(self.width))
        #return '\n'.join(map(row, range(self.height))) +  '\n'