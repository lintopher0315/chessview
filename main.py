import berserk
from colorama import Fore

def print_games(games):
    for i in range(len(games)):
        print(Fore.LIGHTGREEN_EX + "\n" + str(i) + ". " + games[i]['players']['white']['user']['name']
            + " " + str(games[i]['players']['white']['rating']) + " vs. "
            + games[i]['players']['black']['user']['name'] + " "
            + str(games[i]['players']['black']['rating']) + " | "
            + games[i]['createdAt'].strftime("%B %d, %Y") + Fore.RESET)

def help():
    print("\nLIST OF COMMANDS:" +
        "\n" + Fore.RED + "exit" + Fore.RESET + "\t\t\tquits the program" +
        "\n" + Fore.RED + "list" + Fore.RESET + "\t\t\tlists the 10 most recent games played" +
        "\n" + Fore.RED + "info(game_num)" + Fore.RESET + "\t\tdisplays game info" +
        "\n" + Fore.RED + "view(game_num)" + Fore.RESET + "\t\tdisplays the game moves in slideshow format" +
        "\n" + Fore.RED + "analyse(game_num)" + Fore.RESET + "\tdisplays game moves along with engine suggestions" +
        "\n" + Fore.RED + "auto_view(game_num)" + Fore.RESET + "\tdisplays the game moves in gif format" +
        "\n" + Fore.RED + "auto_analyse(game_num)" + Fore.RESET + "\tdisplays game moves and engine suggestions in gif format")

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

    for i in range(17):
        if i % 2 == 0:
            print("._._._._._._._._.")
        else:
            for j in range(len(ranks[int(i / 2)])):
                if ranks[int(i / 2)][j:j+1].isalpha():
                    print("|" + uni[ranks[int(i / 2)][j:j+1]], end='')
                else:
                    print("| " * int(ranks[int(i / 2)][j:j+1]), end='')
            print("|")

username = input(Fore.LIGHTMAGENTA_EX + "Enter your lichess username: " + Fore.RESET)

client = berserk.Client()

try:
    game_generator = client.games.export_by_player(username, as_pgn=False, max=10)

    game_list = list(game_generator)

    command = input("\n\u265A " + Fore.CYAN + "Welcome to ChessView!" + Fore.RESET + "\u2654\nType 'help' for info on commands\n>")
    while(command != 'exit'):
        if (command == 'list'):
            print_games(game_list)
        elif (command == 'help'):
            help()
        elif (command.startswith('info(')):
            print(Fore.LIGHTCYAN_EX)
            print(game_list[int(command[5:6])])
            print(Fore.RESET)
        command = input(">")

except Exception as e:
    #print("Username not found or does not exist.")
    print(e)