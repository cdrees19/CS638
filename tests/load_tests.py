#!/usr/bin/python 


import sys, gc

#Append the parent dir to the module search path
sys.path.append('..')
import AUDLclasses

def load_team_test():
    """
    Tests that the method add_teams can find a single team in the test file 
    and create an instance for it.
    """
    test_league = AUDLclasses.League()
    test_league.add_teams('single_team_info', games = False, players = False, stats = False)
    assert 1 == len(test_league.Teams)

    assert test_league.Teams[224002].Name == 'Radicals'
    assert test_league.Teams[224002].City == 'Madison'

def load_teams_test():
    """
    Tests that the method add_teams can find multiple teams in the test file 
    and create an instance for it.
    """
    test_league = AUDLclasses.League()
    test_league.add_teams('multiple_teams_info', games = False, players = False, stats = False)
    assert 2 == len(test_league.Teams)
    assert 1 == len(test_league.Divisions)
    
    assert test_league.Teams[224002].Name == "Radicals"
    assert test_league.Teams[224002].City == "Madison"

    assert test_league.Teams[210001].Name == "Wind Chill"
    assert test_league.Teams[210001].City == "Minnesota"
    
def load_all_team_data_test():
    """
    Tests that the method add_teams can find a single team in the test file, create an
    instance of the team class, and populate its players and their statistics.
    """
    test_league = AUDLclasses.League()
    test_league.add_teams('single_team_info', games= False, players=False, stats=False)
    for team in test_league.Teams:
        test_league.Teams[team].add_games('test_game_data.json')
        test_league.Teams[team].add_players(filename='test_players.json')

    assert 1 == len(test_league.Teams)

def test_single_game_merge():
    """
    Creates two team instances that share a game in the same file.
    Upon loading games from this file for both teams,
    there should be only one game in the Python instance 
    if game merging is working properly.
    """

    test_league = AUDLclasses.League()
    test_league.add_teams('multiple_teams_info', games = False, players = False, stats = False)
    
    for team in test_league.Teams:
        test_league.Teams[team].add_games('test_game_data.json')

    game_instances = []
   
    for team in test_league.Teams:
        games = test_league.Teams[team].Games
        for game in games:
            if games[game] not in game_instances:
                game_instances.append(games[game])

    assert 1 == len(game_instances)
    for team in test_league.Teams:
        games = test_league.Teams[team].Games
        assert 1== len(games), "%i" % len(games)

def test_match_games():
    
    game_dict =  [{"teamId":"5182111044599808","gameId":"game-8ECA8C1D-6968-4FD0-A361-DE4EFF20203D","opponentName":"Cincinnati Revolution","tournamentName":"","gamePoint":1000,"wind":{"mph":0,"degrees":-1},"timestamp":"2014-04-12 19:26","date":"Sat, 4/12","time":"7:26","msSinceEpoch":1397330760000,"ours":25,"theirs":16,"timeoutDetailsJson":"{\"takenSecondHalf\":2,\"quotaPerHalf\":2,\"takenFirstHalf\":2,\"quotaFloaters\":0}"},{"teamId":"5182111044599808","gameId":"game-47F12B4E-52A2-4AC4-8047-FAC93845A51B","opponentName":"Indianapolis alleyCats","tournamentName":"","gamePoint":1000,"wind":{"mph":0,"degrees":-1},"timestamp":"2014-04-13 15:42","date":"Sun, 4/13","time":"3:42","msSinceEpoch":1397403720000,"ours":26,"theirs":21,"timeoutDetailsJson":"{\"takenSecondHalf\":2,\"quotaPerHalf\":2,\"takenFirstHalf\":2,\"quotaFloaters\":0}"}]


    test_game = AUDLclasses.Game('4/12/14','7:00 EST','2014','Cincinnati Revolution','Madison Radicals')


    test_game.match_game(game_dict,False)

    assert test_game.home_score == 16, test_game.home_score
    assert test_game.away_score == 25, test_game.away_score
