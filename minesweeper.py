import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mine_cell = set()
        self.safe_cell = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if count = number of cells being searched, return the set
        # return empty set if none found to be consitant
        # otherwise currently unsure
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # check it is in the list, remove it and reduce count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -=1
            self.mine_cell.add(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.safe_cell.add(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        known_mines_count = 0
        neighbours = set()
        if cell not in self.moves_made:
            self.moves_made.add(cell)
            self.safes.add(cell)
            # cell is (row, column)
            # loop through each neighbour cell
            # unsure how to handle negative index?
            # row -1 is left and 0 is current and +1 is right
            for row in range(cell[0] - 1, cell[0] +2):
                for collumn in range(cell[1] -1, cell[1] + 2):
                    # if it is the working cell, skip
                    if (row, collumn) == cell:
                        continue
                    # check we wont go out of range
                    if 0 <= row < self.height and \
                        0 <= collumn < self.width:
                        # if it is a mine, add to a counter
                        if (row, collumn) in self.mines:
                            known_mines_count += 1
                        # if unknown add to neighbours to add later
                        elif (row, collumn) not in self.safes:
                            neighbours.add((row, collumn))
        #  add to knowledge db
        adjusted_count = count - known_mines_count

        if neighbours:
            self.knowledge.append(Sentence(neighbours, adjusted_count))
            
        self.update_knowledge()

    def update_knowledge(self):
        """
        Updates the knowledge base to mark new cells as safe or mine
        """
        updated = True
        while updated:
            updated = False
            new_mines = set()
            new_safes = set()
            #  Get all mines and safe squares
            for sentence in self.knowledge:
                mines = sentence.known_mines()
                safes = sentence.known_safes() 
                # Add to a set to process
                if mines:
                    new_mines.update(mines)
                if safes:
                    new_safes.update(safes)
            # update the mine set and set to updated to loop again
            for mine in new_mines:
                if mine not in self.mines:
                    self.mark_mine(mine)
                    updated = True
            for safe in new_safes:
                self.mark_safe(safe)
                updated = True
            
            # clear empty sentences
            self.knowledge = [sentence_ for sentence_ in self.knowledge if sentence_.cells]

            # Generate new sentences by combining
            new_sentences = []
            for sentence_1 in self.knowledge:
                for sentence_2 in self.knowledge:
                    if sentence_1 != sentence_2 and sentence_2.cells.issubset(sentence_1.cells) and sentence_2.cells:
                        new_cells = sentence_1.cells - sentence_2.cells
                        new_count = sentence_1.count - sentence_2.count
                        # if more than 1 mine, new sentence
                        if new_count >= 0:
                            inferred_sentence = Sentence(new_cells, new_count) 
                            if inferred_sentence not in self.knowledge and \
                                inferred_sentence not in new_sentences:
                                new_sentences.append(inferred_sentence)
                                updated = True
            self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #  wont work as can't break if all moves are done
        # move = (
        #     random.randint(0, self.height +1),
        #     random.randint(0, self.width +1)
        #     )
        # while move in self.moves_made:
        #     move = (
        #         random.randint(0, self.height +1),
        #         random.randint(0, self.width +1)
        #         )
        all_cells = set(itertools.product(range(self.height), range(self.width)))
        possible_moves = list(all_cells - self.moves_made - self.mines)
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return None
        
