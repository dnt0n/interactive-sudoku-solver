'''
Interactive Sudoku Solver by dnt0n

Main functions:
Draw a 9x9 sudoku board
When clicked on a box, highlight the box
You can add a number, change a number or delete a number when you are at a box
Press space bar or direction keys to move about the boxes
Entry validation: If entry is not valid eg. enter a number that already exists in a paricular row, print the error message
Print message function
Press C to clear the sudoku board
Press S key to solve the sudoku
'''

import pygame, sys

pygame.init()

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 24, 7)
GREEN = (4, 180, 7)

# dimensions
GRID_WIDTH, GRID_HEIGHT = 11, 11.5
BOX_SIZE = 50
WIDTH, HEIGHT = BOX_SIZE * GRID_WIDTH, BOX_SIZE * GRID_HEIGHT

# FPS
FPS = 30

# board line thickness
THICK_LINE = 4
THIN_LINE = 2

# main fonts
light_font_dir = "./fonts/Roboto-Light.ttf"
bold_font_dir = "./fonts/Roboto-Bold.ttf"

number_font_size = 35
roboto_number = pygame.font.Font(light_font_dir, number_font_size)

message_font_size = 18
roboto_message = pygame.font.Font(bold_font_dir, message_font_size)

# default message
default_message = "Enter the numbers  |  Press S to Solve  |  Press C to Clear"

################################################################

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def display_board(board, selected_pos, old_board=None): # board is a 9x9 matrix
    for r in range(9):
        for c in range(9):
            curr_box_num = board[r][c]
            if (r, c) == selected_pos: # display selected box
                select_surf = pygame.Surface((BOX_SIZE, BOX_SIZE))
                select_surf.fill(BLACK)
                screen.blit(select_surf, ((1 + c) * BOX_SIZE, (1 + r) * BOX_SIZE))

                if curr_box_num != 0: # display number in selected box
                    num_surf = roboto_number.render(str(curr_box_num), True, WHITE)
                    num_rect = num_surf.get_rect(center = ((1.5 + c) * BOX_SIZE, (1.5 + r) * BOX_SIZE))
                    screen.blit(num_surf, num_rect)     

            else:
                if curr_box_num != 0:
                    if old_board is not None and old_board[r][c] != board[r][c]: # if board is solved and curr box is part of the solution
                        num_surf = roboto_number.render(str(curr_box_num), True, GREEN)
                    else:
                        num_surf = roboto_number.render(str(curr_box_num), True, BLACK)
                    num_rect = num_surf.get_rect(center = ((1.5 + c) * BOX_SIZE, (1.5 + r) * BOX_SIZE))
                    screen.blit(num_surf, num_rect)   

    # draw gridlines
    for r in range(10):
        if r in (0, 3, 6, 9):
            pygame.draw.line(screen, BLACK, ((1 + r) * BOX_SIZE, 1 * BOX_SIZE), ((1 + r) * BOX_SIZE, 10 * BOX_SIZE), THICK_LINE)
        else:
            pygame.draw.line(screen, BLACK, ((1 + r) * BOX_SIZE, 1 * BOX_SIZE), ((1 + r) * BOX_SIZE, 10 * BOX_SIZE), THIN_LINE)
    for c in range(10):
        if c in (0, 3, 6, 9):
            pygame.draw.line(screen, BLACK, (1 * BOX_SIZE, (1 + c) * BOX_SIZE), (10 * BOX_SIZE, (1 + c) * BOX_SIZE), THICK_LINE) 
        else:
            pygame.draw.line(screen, BLACK, (1 * BOX_SIZE, (1 + c) * BOX_SIZE), (10 * BOX_SIZE, (1 + c) * BOX_SIZE), THIN_LINE)     

def get_next_selected_pos(pos):
    r, c = pos
    if c < 8:
        c += 1
    else: # c == 8
        if r < 8:
            c = 0
            r += 1   
    return (r, c)

def display_message(msg):
    msg_surf = roboto_message.render(msg, True, BLACK)
    msg_rect = msg_surf.get_rect(center = (5.5 * BOX_SIZE, 10.75 * BOX_SIZE))
    screen.blit(msg_surf, msg_rect)

def get_rows(board):
    return board.copy()

def get_cols(board):
    return [[board[r][c] for r in range(9)] for c in range(9)]

def get_grids(board):
    all_grids = []
    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            grid = []
            for i in range(r, r + 3):
                for j in range(c, c + 3):
                    grid.append(board[i][j])
            all_grids.append(grid)
    return all_grids

def get_grid_number(r, c):
    grid_positions = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    return grid_positions[r // 3][c // 3]

def check_entry(entry, pos, board):
    # check the validity of the entry
    # if valid return True
    # else return the error message: eg. grid 1 already has a 2! / row 1 already has a 7!
    all_rows = board
    all_cols = get_cols(board)
    all_grids = get_grids(board)

    r, c = pos
    g = get_grid_number(r, c)
    
    # row check
    if entry in all_rows[r]: return f"Invalid Input !  Row {r+1} already has a {entry} !"   
    # column check
    elif entry in all_cols[c]: return f"Invalid Input !  Column {c+1} already has a {entry} !"
    # grid check
    elif entry in all_grids[g-1]: return f"Invalid Input !  Grid {g} already has a {entry} !"   
    # if all checks pass, return True
    else: return True

# check whether the board is a valid solution
def is_valid_sudoku(board):
    all_rows = board
    all_cols = get_cols(board)
    all_grids = get_grids(board)
    distinct_numbers = set([i for i in range(1, 10)])

    for row in all_rows:
        if set(row) != distinct_numbers:
            return False
    for col in all_cols:
        if set(col) != distinct_numbers:
            return False
    for grid in all_grids:
        if set(grid) != distinct_numbers:
            return False
    return True

# IN-PLACE sudoku solver algorithm with backtracking    
def solve_sudoku(board):
    
    def get_candidates(board, r, c):
        all_rows = board
        all_cols = get_cols(board)
        all_grids = get_grids(board)
        g = get_grid_number(r, c)
        distinct_numbers = set([i for i in range(1, 10)])

        curr_row = all_rows[r]
        curr_col = all_cols[c]
        curr_grid = all_grids[g-1]

        candidates = distinct_numbers - set(curr_row) - set(curr_col) - set(curr_grid)

        return candidates
    
    def backtrack(board):
        if is_valid_sudoku(board):
            return True
        
        for r in range(9):
            for c in range(9):
                curr_box = board[r][c]
                if curr_box == 0: # empty box
                    for candidate in get_candidates(board, r, c):
                        board[r][c] = candidate
                        solved = backtrack(board)
                        if solved:
                            return True
                        else:
                            board[r][c] = 0
                    return False # tried all candidates for this box but none works
        return True # box is not empty - treat it as already solved
            
    backtrack(board) # solving in place, nothing is returned

################################################################

def main():
    board = [[0 for _ in range(9)] for _ in range(9)]
    curr_selected_pos = (-1, -1)
    curr_message = default_message
    solved = False
    old_board = [[0 for _ in range(9)] for _ in range(9)]

    while True:
        clock.tick(FPS) # while loop runs maximally at FPS times per second

        pygame.display.set_caption("Sudoku Solver")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # mouse down to select a box
            if event.type == pygame.MOUSEBUTTONDOWN:
                c, r = pygame.mouse.get_pos()
                row = r // BOX_SIZE - 1
                col = c // BOX_SIZE - 1
                curr_message = default_message
                if 0 <= row <= 8 and 0 <= col <= 8:
                    curr_selected_pos = (row, col)
                else:
                    curr_selected_pos = (-1, -1)

            # key down events:
            # NUMBER key down to enter a number in the selected box
            # BACKSPACE to delete the number in the selected box
            # SPACE key down to jump to the next box (in zigzag fashion)
            # DIRECTION keys to move about
            # C key down to clear the board
            if event.type == pygame.KEYDOWN:
                curr_r, curr_c = curr_selected_pos

                # move about the selected box
                if event.key == pygame.K_SPACE:
                    curr_r, curr_c = get_next_selected_pos(curr_selected_pos)
                if event.key == pygame.K_UP:
                    if curr_r >= 0: curr_r -= 1
                    if curr_r == -1: curr_r = 8
                if event.key == pygame.K_DOWN:
                    if curr_r <= 8: curr_r += 1 
                    if curr_r == 9: curr_r = 0    
                if event.key == pygame.K_LEFT:
                    if curr_c >= 0: curr_c -= 1
                    if curr_c == -1: curr_c = 8
                if event.key == pygame.K_RIGHT:
                    if curr_c <= 8: curr_c += 1 
                    if curr_c == 9: curr_c = 0         
                curr_selected_pos = (curr_r, curr_c) # update selected position

                # enter a number
                key_num = pygame.key.name(event.key)
                if key_num.isdigit() and 1 <= int(key_num) <= 9 and curr_selected_pos != (-1, -1):
                    entry_validation = check_entry(int(key_num), curr_selected_pos, board)
                    if entry_validation == True:
                        solved = False
                        board[curr_r][curr_c] = int(key_num)
                        curr_message = default_message
                    else:
                        # print error message
                        curr_message = entry_validation
                
                # delete a number
                if event.key == pygame.K_BACKSPACE and curr_selected_pos != (-1, -1):
                    solved = False
                    board[curr_r][curr_c] = 0

                # clear the board
                if event.key == pygame.K_c:
                    solved = False
                    board = [[0 for _ in range(9)] for _ in range(9)]
                    curr_selected_pos = (-1, -1)
                    curr_message = default_message

                # solve the board
                if event.key == pygame.K_s:
                    if board == [[0 for _ in range(9)] for _ in range(9)]:
                        curr_message = "Please enter the numbers before solving !"
                    else:
                        solved = True
                        if not is_valid_sudoku(board): # prevent repeated entry of key S
                            old_board = [row.copy() for row in board] # note that we can't just do board.copy() as it is a shallow copy!!!
                        solve_sudoku(board)
                        curr_selected_pos = (-1, -1)
                        curr_message = "Sudoku Solved !  Press C to clear the board"

        screen.fill(WHITE)
        display_message(curr_message)
        if not solved:
            display_board(board, curr_selected_pos)
        else:
            display_board(board, curr_selected_pos, old_board)
        pygame.display.update()

if __name__ == "__main__":
    main()
