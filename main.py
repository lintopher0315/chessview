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
    logging.info(ranks)
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
        board.push(board.parse_san(get_engine_moves(board.fen(), engine)[0]))
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

    event.app.layout.container.children[0].content.text = ''
    for i in range(len(move_list)):
        if i % 2 == 0:
            event.app.layout.container.children[0].content.text += '\n' + str((int(i / 2) + int(move_start / 2)) + 1) + '.'
        event.app.layout.container.children[0].content.text += move_list[i] + ' '

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

    event.app.layout.container.children[0].content.text = ''
    for i in range(len(move_list)):
        if i % 2 == 0:
            event.app.layout.container.children[0].content.text += '\n' + str((int(i / 2) + int(move_start / 2)) + 1) + '.'
        event.app.layout.container.children[0].content.text += move_list[i] + ' '

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
    info = engine.analyse(board, chess.engine.Limit(depth=10), multipv=3)

    for i in range(len(info)):
        engine_moves.append(board.san(info[i]['pv'][0]))
    return engine_moves

def main():

    username = prompt(HTML('<violet>Enter your lichess username: </violet>'))

    client = berserk.Client()

    engine = chess.engine.SimpleEngine.popen_uci("/home/christopher/stockfish_10_x64")

    #get_engine_moves("r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4", engine)
    #analysis_to_move_archive('e4 d5 exd5 Qxd5 Nc3 Qe6+ Be2 Nf6 Nf3 c6 O-O b5 Re1 Qd6 a3 e6 d3 a5 b3 h6 Bb2 a4 bxa4 Ra5 axb5 Qd8 bxc6 Ba6 Ne4 Nxe4 dxe4 Nxc6 Qxd8+ Nxd8 Rad1 Bxe2 Rxe2 Nc6 Red2 f6 e5 Be7 exf6 Bxf6 Bxf6 gxf6 Rd6 Rc5 Rxe6+ Kf7 Ree1 Ne5 Nxe5+ fxe5 h3 Ra8 Ra1 Ra4 f3 Kf6 Re4 Ra7 a4 h5 Ra2 Ra8 Kf2 Rac8 Re2 R8c6 Ke1 Ra5 Kd1 Rc4 Re4 Rc8 Kd2 Ra6 c3 Rc5 Rb2 Rca5 Rb5 Rxa4 Rbxe5 Rxe4 Rxe4 Ra2+ Ke3 Rxg2 c4 Kf5 c5 Rc2 Kd4 Rd2+ Kc3 Rf2 Re3 Kf4 Kd4 Rd2+ Rd3 Rc2 Kd5 Kg3 c6 Kxh3 Kd6 Kg2 Kd7 Kg3 c7 h4 c8=Q Rxc8 Kxc8 Kg2 f4 Kh2 f5 Kg2 f6 Kf2 f7 Ke2 Rh3 Ke1 f8=Q Ke2 Qf3+ Ke1 Rh2 h3 Qh1#', engine)

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