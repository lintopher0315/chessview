from prompt_toolkit import prompt, print_formatted_text, Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
import berserk
import chess.pgn
import io

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
    ranks = fen.split('/')
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
        board += '                 '
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
    return board

def game_to_fenlist(moves):
    fenlist = []
    pgn = io.StringIO(moves)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    fenlist.append(board.fen().split(' ')[0])
    for move in game.mainline_moves():
        board.push(move)
        fenlist.append(board.fen().split(' ')[0])
    return fenlist

def main():

    username = prompt(HTML('<violet>Enter your lichess username: </violet>'))

    client = berserk.Client()

    kb = KeyBindings()
    move_place = 0
    moves = []
    game_list = []
    game_number = 0

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
        if move_place > 0:
            move_place = move_place - 1

        chess_text = ''
        if 'user' not in game_list[game_number]['players']['black']:
            chess_text += '\n\n\n                 Computer Level ' + str(game_list[game_number]['players']['black']['aiLevel']) + '\n\n'
        else:
            chess_text += '\n\n\n                 ' + game_list[game_number]['players']['black']['user']['name'] + ' (' + str(game_list[game_number]['players']['black']['rating']) + ')\n\n'
        chess_text += fen_to_image(moves[move_place])
        if 'user' not in game_list[game_number]['players']['white']:
            chess_text += '\n                 Computer Level ' + str(game_list[game_number]['players']['white']['aiLevel']) + '\n'
        else:
            chess_text += '\n                 ' + game_list[game_number]['players']['white']['user']['name'] + ' (' + str(game_list[game_number]['players']['white']['rating']) + ')\n'
        chess_text += '\n\n\n                 <violet>Ctrl-A: Previous Move</violet>\n                 <violet>Ctrl-D: Next Move</violet>\n                 <violet>Ctrl-Q: Exit</violet>'
        event.app.layout.container.children[2].content.text = HTML(chess_text)

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

        event.app.renderer._last_size: Optional[Size] = None
        event.app.renderer.output.flush()

    @kb.add('c-d')
    def next(event):
        nonlocal move_place
        nonlocal moves
        if move_place < len(moves) - 1:
            move_place = move_place + 1

        chess_text = ''
        if 'user' not in game_list[game_number]['players']['black']:
            chess_text += '\n\n\n                 Computer Level ' + str(game_list[game_number]['players']['black']['aiLevel']) + '\n\n'
        else:
            chess_text += '\n\n\n                 ' + game_list[game_number]['players']['black']['user']['name'] + ' (' + str(game_list[game_number]['players']['black']['rating']) + ')\n\n'
        chess_text += fen_to_image(moves[move_place])
        if 'user' not in game_list[game_number]['players']['white']:
            chess_text += '\n                 Computer Level ' + str(game_list[game_number]['players']['white']['aiLevel']) + '\n'
        else:
            chess_text += '\n                 ' + game_list[game_number]['players']['white']['user']['name'] + ' (' + str(game_list[game_number]['players']['white']['rating']) + ')\n'
        chess_text += '\n\n\n                 <violet>Ctrl-A: Previous Move</violet>\n                 <violet>Ctrl-D: Next Move</violet>\n                 <violet>Ctrl-Q: Exit</violet>'
        event.app.layout.container.children[2].content.text = HTML(chess_text)

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

        event.app.renderer._last_size: Optional[Size] = None
        event.app.renderer.output.flush()

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
                moves = game_to_fenlist(game_list[int(command[5:6])]['moves'])

                chess_text = ''
                if 'user' not in game_list[game_number]['players']['black']:
                    chess_text += '\n\n\n                 Computer Level ' + str(game_list[game_number]['players']['black']['aiLevel']) + '\n\n'
                else:
                    chess_text += '\n\n\n                 ' + game_list[game_number]['players']['black']['user']['name'] + ' (' + str(game_list[game_number]['players']['black']['rating']) + ')\n\n'
                chess_text += fen_to_image(moves[0])
                if 'user' not in game_list[game_number]['players']['white']:
                    chess_text += '\n                 Computer Level ' + str(game_list[game_number]['players']['white']['aiLevel']) + '\n'
                else:
                    chess_text += '\n                 ' + game_list[game_number]['players']['white']['user']['name'] + ' (' + str(game_list[game_number]['players']['white']['rating']) + ')\n'
                chess_text += '\n\n\n                 <violet>Ctrl-A: Previous Move</violet>\n                 <violet>Ctrl-D: Next Move</violet>\n                 <violet>Ctrl-Q: Exit</violet>'
                
                root_container = VSplit([
                    Window(width=30, content=FormattedTextControl(), dont_extend_width=True, wrap_lines=True, allow_scroll_beyond_bottom=True, always_hide_cursor=True),
                    Window(width=1, char='|', always_hide_cursor=True),
                    Window(content=FormattedTextControl(text=HTML(chess_text)), always_hide_cursor=True)
                ])

                layout = Layout(root_container)
                app = Application(key_bindings=kb, layout=layout, full_screen=True)
                app.run()

            command = prompt(HTML('>'))
    except Exception as e:
        #print("Username not found or does not exist.")
        print(e)

if __name__ == "__main__":
    main()