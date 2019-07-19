import berserk

def print_games(games):
    print("\n")
    for i in range(len(games)):
        print(str(i + 1) + ". " + games[i]['players']['white']['user']['name']
            + " " + str(games[i]['players']['white']['rating']) + " vs. "
            + games[i]['players']['black']['user']['name'] + " "
            + str(games[i]['players']['black']['rating']) + " | "
            + games[i]['createdAt'].strftime("%B %d, %Y") + "\n")

def help():
    print("""
        \nList of commands:
        \nexit\tquits the program
        \nlist\tlists the 10 most recent games played
        \ninfo(game_num)\tdisplays game info
        \nview(game_num)\tdisplays the game moves in slideshow format
        \nanalyse(game_num)\tdisplays game moves along with engine suggestions
        \nauto_view(game_num)\tdisplays the game moves in gif format
        \nauto_analyse(game_num)\tdisplays game moves and engine suggestions in gif format
        \n
        """)

username = input("Enter your lichess username: ")

client = berserk.Client()

try:
    game_generator = client.games.export_by_player(username, as_pgn=False, max=10)

    game_list = list(game_generator)

    command = input("\nType 'help' for info on commands\n>")
    while(command != 'exit'):
        if (command == 'list'):
            print_games(game_list)
        elif (command == 'help'):
            help()
        command = input(">")

except Exception as e:
    #print("Username not found or does not exist.")
    print(e)