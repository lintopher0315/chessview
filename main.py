from prompt_toolkit import prompt, print_formatted_text, Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
import berserk
import logging
import chess
import chess.pgn
import chess.engine
import io
import re

def print_games(games):
    for i in range(len(games)):
        if 'user' not in games[i]['players']['white']:
            print_formatted_text("\n" + str(i) + ". Computer Level "
                + str(games[i]['players']['white']['aiLevel']) + " vs. "
                + games[i]['players']['black']['user']['name'] + " "
                + str(games[i]['players']['black']['rating']) + " | "
                + games[i]['createdAt'].strftime("%B %d, %Y"))
        elif 'user' not in games[i]['players']['black']:
            print_formatted_text("\n" + str(i) + ". " + games[i]['players']['white']['user']['name']
                + " " + str(games[i]['players']['white']['rating']) + " vs. Computer Level "
                + str(games[i]['players']['black']['aiLevel']) + " | "
                + games[i]['createdAt'].strftime("%B %d, %Y"))
        else:
            print_formatted_text("\n" + str(i) + ". " + games[i]['players']['white']['user']['name']
                + " " + str(games[i]['players']['white']['rating']) + " vs. "
                + games[i]['players']['black']['user']['name'] + " "
                + str(games[i]['players']['black']['rating']) + " | "
                + games[i]['createdAt'].strftime("%B %d, %Y"))

def help():
    print_formatted_text(HTML("\nLIST OF COMMANDS:\n"
        "<red>exit</red>\t\t\tquits the program\n"
        "<red>list</red>\t\t\tlists the 10 most recent games played\n"
        "<red>info(game_num)</red>\t\tdisplays game info\n"
        "<red>view(game_num)</red>\t\tdisplays the game moves in slideshow format\n"
        "<red>analyse(game_num)</red>\tdisplays game moves along with engine suggestions\n"
        "<red>auto_view(game_num)</red>\tdisplays the game moves in gif format\n"
        "<red>auto_analyse(game_num)</red>\tdisplays game moves and engine suggestions in gif format"))

def fen_to_image(fen):
    ranks = re.split('/| ', fen)
    ranks = ranks[:8]
    uni = {
        "k": "\u2654",
        "q": "\u2655",
        "r": "\u2656",
        "b": "\u2657",
        "n": "\u2658",
        "p": "\u2659",
        "K": "\u265A",
        "Q": "\u265B",
        "R": "\u265C",
        "B": "\u265D",
        "N": "\u265E",
        "P": "\u265F"
    }
    board = ''
    color = True
    for i in range(8):
        board += '                 ' + str(8 - i)
        for j in range(len(ranks[i])):
            if ranks[i][j:j+1].isalpha():
                if ranks[i][j:j+1].islower():
                    board = board + '<p bg="salmon" fg="ansiblack">' + uni[ranks[i][j:j+1].upper()] + ' </p>' if color else board + '<p bg="brown" fg="ansiblack">' + uni[ranks[i][j:j+1].upper()] + ' </p>'
                else:
                    board = board + '<p bg="salmon">' + uni[ranks[i][j:j+1]] + ' </p>' if color else board + '<p bg="brown">' + uni[ranks[i][j:j+1]] + ' </p>'
                color = not color
            else:
                for k in range(int(ranks[i][j:j+1])):
                    board = board + '<p bg="salmon">  </p>' if color else board + '<p bg="brown">  </p>'
                    color = not color
            
        board = board + '<p>\n</p>'
        color = not color
    board += '                  a b c d e f g h'
    return board

def game_to_fenlist(moves):
    fenlist = []
    pgn = io.StringIO(moves)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    fenlist.append(board.fen().split(' ')[0])
    for move in game.mainline_moves():
        board.push(move)
        fenlist.append(board.fen())
    return fenlist

def analysis_to_move_archive(moves, engine):
    move_archive = []
    pgn = io.StringIO(moves)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    for move in game.mainline_moves():
        curr = get_engine_moves(board.fen(), engine)
        board.push(board.parse_san(curr[0]))
        curr.append(board.fen())
        board.pop()
        board.push(move)
        move_archive.append(curr)
    return move_archive

def set_simple_chess_text(game_list, game_number, moves, move_place):
    chess_text = ''
    if 'user' not in game_list[game_number]['players']['black']:
        chess_text += '<gold>\n\n\n                 Computer Level ' + str(game_list[game_number]['players']['black']['aiLevel']) + '\n\n</gold>'
    else:
        chess_text += '<gold>\n\n\n                 ' + game_list[game_number]['players']['black']['user']['name'] + ' (' + str(game_list[game_number]['players']['black']['rating']) + ')\n\n</gold>'
    chess_text += fen_to_image(moves[move_place])
    if 'user' not in game_list[game_number]['players']['white']:
        chess_text += '<gold>\n\n                 Computer Level ' + str(game_list[game_number]['players']['white']['aiLevel']) + '\n</gold>'
    else:
        chess_text += '<gold>\n\n                 ' + game_list[game_number]['players']['white']['user']['name'] + ' (' + str(game_list[game_number]['players']['white']['rating']) + ')\n</gold>'
    chess_text += '\n\n\n                 <violet>Ctrl-A: Previous Move</violet>\n                 <violet>Ctrl-D: Next Move</violet>\n                 <violet>Ctrl-Q: Exit</violet>'
    
    return chess_text

def set_simple_history_text(event, game_list, game_number, move_place):
    history_text = ''

    move_start = 0
    move_list = []
    if move_place >= 40:
        move_start = move_place - 40
        if move_place % 2 == 0:
            move_list = game_list[game_number]['moves'].split(' ')[move_start:move_place]
        else:
            move_list = game_list[game_number]['moves'].split(' ')[move_start - 1:move_place]
    else:
        move_list = game_list[game_number]['moves'].split(' ')[move_start:move_place]

    for i in range(len(move_list)):
        if i % 2 == 0:
            history_text += '\n' + str((int(i / 2) + int(move_start / 2)) + 1) + '.'
        history_text += move_list[i] + ' '
    event.app.layout.container.children[0].content.text = history_text

def display_simple_screen(event, game_list, game_number, moves, move_place):
    chess_text = set_simple_chess_text(game_list, game_number, moves, move_place)
    event.app.layout.container.children[2].content.text = HTML(chess_text)

    set_simple_history_text(event, game_list, game_number, move_place)

    event.app.renderer._last_size: Optional[Size] = None
    event.app.renderer.output.flush()

def set_analysis_chess_text(game_list, game_number, moves, move_place, analysis_archive):
    chess_text = ''
    if 'user' not in game_list[game_number]['players']['black']:
        chess_text += '<gold>                 Computer Level ' + str(game_list[game_number]['players']['black']['aiLevel']) + '\n</gold>'
    else:
        chess_text += '<gold>                 ' + game_list[game_number]['players']['black']['user']['name'] + ' (' + str(game_list[game_number]['players']['black']['rating']) + ')\n</gold>'
    chess_text += fen_to_image(moves[move_place])
    if 'user' not in game_list[game_number]['players']['white']:
        chess_text += '<gold>\n                 Computer Level ' + str(game_list[game_number]['players']['white']['aiLevel']) + '\n</gold>'
    else:
        chess_text += '<gold>\n                 ' + game_list[game_number]['players']['white']['user']['name'] + ' (' + str(game_list[game_number]['players']['white']['rating']) + ')\n</gold>'
    
    if move_place > 0:
        chess_text += fen_to_image(analysis_archive[move_place - 1][len(analysis_archive[move_place - 1]) - 1])

    return chess_text

def set_analysis_history_text(event, game_list, game_number, move_place, analysis_archive):
    history_text = ''

    move_start = 0
    move_list = []
    if move_place >= 40:
        move_start = move_place - 40
        if move_place % 2 == 0:
            move_list = game_list[game_number]['moves'].split(' ')[move_start:move_place]
        else:
            move_list = game_list[game_number]['moves'].split(' ')[move_start - 1:move_place]
    else:
        move_list = game_list[game_number]['moves'].split(' ')[move_start:move_place]

    for i in range(len(move_list)):
        if i % 2 == 0:
            history_text += '\n' + str((int(i / 2) + int(move_start / 2)) + 1) + '.'
        if move_start % 2 == 0:
            if move_list[i] in analysis_archive[i + move_start]:
                history_text += '<lime>' + move_list[i] + '</lime> '
            else:
                history_text += move_list[i] + ' '
        else:
            if move_list[i] in analysis_archive[i + move_start - 1]:
                history_text += '<lime>' + move_list[i] + '</lime> '
            else:
                history_text += move_list[i] + ' '
    event.app.layout.container.children[0].content.text = HTML(history_text)

def display_analysis_screen(event, game_list, game_number, moves, move_place, analysis_archive):
    chess_text = set_analysis_chess_text(game_list, game_number, moves, move_place, analysis_archive)
    event.app.layout.container.children[2].content.text = HTML(chess_text)

    set_analysis_history_text(event, game_list, game_number, move_place, analysis_archive)

    event.app.renderer._last_size: Optional[Size] = None
    event.app.renderer.output.flush()

def get_position_score(fen, engine):
    board = chess.Board(fen)
    info = engine.analyse(board, chess.engine.Limit(depth=20))
    return(info["score"])

def get_engine_moves(fen, engine):
    engine_moves = []
    board = chess.Board(fen)
    info = engine.analyse(board, chess.engine.Limit(depth=15), multipv=3)

    for i in range(len(info)):
        engine_moves.append(board.san(info[i]['pv'][0]))
    return engine_moves

def main():
    logging.basicConfig(filename='errors.log',level=logging.DEBUG)
    username = prompt(HTML('<violet>Enter your lichess username: </violet>'))

    client = berserk.Client()

    engine = chess.engine.SimpleEngine.popen_uci("/home/christopher/stockfish_10_x64")

    move_place = 0
    moves = []
    game_list = []
    game_number = 0
    analysis_archive = []

    kb = KeyBindings()
    kba = KeyBindings()

    @kb.add('c-q')
    def exit_(event):
        nonlocal move_place
        nonlocal moves
        move_place = 0
        moves = []
        game_list = []
        game_number = 0
        event.app.exit()

    @kb.add('c-a')
    def prev(event):
        nonlocal move_place
        nonlocal moves
        if move_place > 0:
            move_place = move_place - 1

        display_simple_screen(event, game_list, game_number, moves, move_place)

    @kb.add('c-d')
    def next(event):
        nonlocal move_place
        nonlocal moves
        if move_place < len(moves) - 1:
            move_place = move_place + 1

        display_simple_screen(event, game_list, game_number, moves, move_place)

    @kba.add('c-q')
    def exit_(event):
        nonlocal move_place
        nonlocal moves
        move_place = 0
        moves = []
        game_list = []
        game_number = 0
        analysis_archive = []
        event.app.exit()

    @kba.add('c-a')
    def prev(event):
        nonlocal move_place
        nonlocal moves
        if move_place > 0:
            move_place = move_place - 1

        display_analysis_screen(event, game_list, game_number, moves, move_place, analysis_archive)

    @kba.add('c-d')
    def next(event):
        nonlocal move_place
        nonlocal moves
        if move_place < len(moves) - 1:
            move_place = move_place + 1

        display_analysis_screen(event, game_list, game_number, moves, move_place, analysis_archive)


    try:
        game_generator = client.games.export_by_player(username, as_pgn=False, max=10)

        game_list = list(game_generator)

        command = prompt(HTML('\n\u265A <cyan>Welcome to ChessView!</cyan> \u2654\nType "help" for info on commands\n>'))
        while(command != 'exit'):
            if (command == 'list'):
                print_games(game_list)
            elif (command == 'help'):
                help()
            elif (command.startswith('info(')):
                print_formatted_text(game_list[int(command[5:6])])
            elif (command.startswith('view(')):
                game_number = int(command[5:6])
                moves = game_to_fenlist(game_list[game_number]['moves'])

                chess_text = set_simple_chess_text(game_list, game_number, moves, 0)
                
                root_container = VSplit([
                    Window(width=30, content=FormattedTextControl(), dont_extend_width=True, wrap_lines=True, allow_scroll_beyond_bottom=True, always_hide_cursor=True),
                    Window(width=1, char='|', always_hide_cursor=True),
                    Window(content=FormattedTextControl(text=HTML(chess_text)), always_hide_cursor=True)
                ])

                layout = Layout(root_container)
                app = Application(key_bindings=kb, layout=layout, full_screen=True)
                app.run()

            elif (command.startswith('analyze(')):
                game_number = int(command[8:9])
                moves = game_to_fenlist(game_list[game_number]['moves'])
                analysis_archive = analysis_to_move_archive(game_list[game_number]['moves'], engine)

                chess_text = set_analysis_chess_text(game_list, game_number, moves, 0, analysis_archive)

                root_container = VSplit([
                    Window(width=30, content=FormattedTextControl(), dont_extend_width=True, wrap_lines=True, allow_scroll_beyond_bottom=True, always_hide_cursor=True),
                    Window(width=1, char='|', always_hide_cursor=True),
                    Window(content=FormattedTextControl(text=HTML(chess_text)), always_hide_cursor=True)
                ])

                layout = Layout(root_container)
                app = Application(key_bindings=kba, layout=layout, full_screen=True)
                app.run()

            command = prompt(HTML('>'))
        engine.quit()
    except Exception as e:
        #print("Username not found or does not exist.")
        print(e)

if __name__ == "__main__":
    main()