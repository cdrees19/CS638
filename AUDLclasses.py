#!/usr/bin/python

import statget
import urllib2, json
import feedparser as fp
import MediaClasses


base_url = 'http://www.ultimate-numbers.com/rest/view'

class League():
    """ 
    Class which acts as a central node for all other classes
    on the AUDL server.
    """
    def __init__(self):
         # A dictionary containing all video link class instances
        self.Videos = {};
        # A list of information about the upcoming
        # week in the AUDL
        self.This_week = [];
        # A list of apple product device IDs
        # on which the AUDL app is installed
        self.Apple_users = [];
        # A list of android OS device IDs on
        # which the AUDL app is installed
        self.Android_users = [];
        # A list of video feeds that the server is
        # to glean information from
        self.Video_feeds = [];
        # A list of RSS feeds the server is to
        # glean information from 
        self.RSS_feeds = ['http://www.theaudl.com/appfeed.xml'];
        # A dictionary containing lists of the top five 
        # players for a given statistic and their stat
        # in sorted order
        self.Top_fives = {};


    def add_teams(self):
        """
        This method retrieves all known teams from the ultimate-numbers
        server using a dictionary that keeps track of team IDs we care about. 

        For each team, the basic info for that team is taken from a file
        in the repository and their game information is retrieved from the 
        ultimate-numbers server. 
        """
        # Dictionary for all team instances 
        self.Teams = {} 

        teams = statget.team_dict()
      
        # Restructures the teams dict so that the keys are the Team IDs
        # Also creates a new team class instance for each Team ID
        for team in teams: 
            self.Teams[teams[team]] = Team()
        # Right now the list of teams is taken from the team dictionary object in statget.
        # Eventually we will want to grab this list from the server and create
        # new Team classes accordingly.

        # Gives each team its ID value so it can grab its own information from the server.
        for team in self.Teams:
            self.Teams[team].ID = team
            self.Teams[team].get_info()
            self.Teams[team].add_games()
            self.Teams[team].add_players()
            self.Teams[team].populate_team_stats()

    def get_news(self):

        # A dictionary containing all related news article
        # class instances
        self.News = {};

        for feed in self.RSS_feeds:
            # parse the feed into a python dictionary
            data = fp.parse(feed)
            # create a new article for each article in the feed
            # later, we will need to limit the number of articles in the feed
            for ent in data.entries:
                temp_news_class = MediaClasses.Article(ent.published, ent.link, ent.title)
                self.News[id(temp_news_class)] = temp_news_class
    
    def team_list(self):
        """
        A method for populating the Teams page in the UI. Returns a list of all teams in the 
        League class along with their IDs.
        """
        data_out = []
        for team in self.Teams:
            if hasattr(self.Teams[team], 'Name'):
                new_tup = (self.Teams[team].Name, self.Teams[team].ID)
                data_out.append(new_tup)
        return data_out

    def news_page_info(self):
        # Init the output list, add a header
        art_list=["AUDL News"]
        # shorten the path to the News dictionary
        News = self.News
        # Get the title and article url for every article
        # create a tuple and append to the output lits
        for art in News:
            art_tup = (News[art].Title, News[art].url)
            art_list.append(art_tup)

        return art_list

    def refresh_league(self):
        self.add_teams()
        self.get_news()
        
class Team():
    """
    This class keeps all of the statistical information 
    for a given team in the league. (player info, statistics,
    game schedules, etc.)
    """
    def __init__(self):
         # The team's ultimate-numbers ID. This is how we recognize this team on the 
         # ultimate numbers server. It is also our way of giving each team a 
         # unique identifier.
         self.ID = 0
         # A string containing the team's current win or 
         # loss streak.
         self.Streak = ''

    def get_info(self):
         """
         This method grabs information from a local file in the 
         repository for a given team. This file contains the teams
         city, coach, ID, and team name. Teams are identified using 
         their team ID from the ultimate-numbers server.
         """
         teams_info = open('Teams_Info', 'r')
         found = False
         for line in teams_info: 
              # See if we've reached the beginning of
              # some team info

              if line.count("ID") == 1 and line[4:].rstrip() == str(self.ID):
                       found = True
                       line = teams_info.next().split(":")[1]
                       # A string containing the team's name. 
                       self.Name = line[1:].rstrip()
                       line = teams_info.next().split(":")[1]
                       # A string containing the team's home city. 
                       self.City = line[1:].rstrip()
                       line = teams_info.next().split(":")[1]
                       # A string containing the name of the team's coach
                       self.Coach = line[1:].rstrip()
         if not found: print "No Team with that ID on record"
         teams_info.close()


    def add_players(self):
        """
        Adds players to the Team class attribute 'Players' from the ultimate-numbers
        server.
        """

        # A dictionary containing a set of Player class
        # instances pertaining to this team.
        self.Players = {}

        # Get information from ultimate-numbers server
        base_url = 'http://www.ultimate-numbers.com/rest/view'
        req = urllib2.Request(base_url + '/team/' + str(self.ID) + '/stats/player')
        response =  urllib2.urlopen(req)
        page = response.read()
        # Decode json string as python dict
        data = json.loads(page)

        # For every player in the data, 
        # create a new player
        

        for player in data:
            #Add player to team's Players dictionary
            self.Players[player['playerName']] = Player()
            self.add_player_info(player)

    def add_player_info(self, player_info):
        """
        Adds player name, number, stats, etc. to a player class. 

        Assumes the ultimate-numbers info has already been loaded.
        """
        
        #Add player's info to new Player class instance
        self.Players[player_info['playerName']].First_name = player_info['playerName']
        self.Players[player_info['playerName']].Stats['Assists']  = player_info['assists']
        self.Players[player_info['playerName']].Stats['Goals']  = player_info['goals']
        self.Players[player_info['playerName']].Stats['PMC']  = player_info['plusMinusCount']
        self.Players[player_info['playerName']].Stats['Drops']  = player_info['drops']
        self.Players[player_info['playerName']].Stats['Throwaways']  = player_info['throwaways']
        self.Players[player_info['playerName']].Stats['Ds'] = player_info['ds']
        # Check the ultimate-numbers server to see if they have a player number
        # that matches this player. 
        self.add_player_number(self.Players[player_info['playerName']])

    def add_player_number(self,player_class):
        """
        Grabs a different player info endpoint from the ultimate-numbers server
        to match player numbers to name
        """
        # Get data from the appropriate ultimate-numbers 
        # endpoint
        base_url = 'http://www.ultimate-numbers.com/rest/view'
        req = urllib2.Request(base_url+"/team/"+str(self.ID)+"/players/")
        response = urllib2.urlopen(req)
        if response.code == 111: print "add_player_number fail", self.Name, player_class.First_name
        data = json.loads(response.read())
        
        # Check each player in the Team instance for a name that matches
        # a player in this endpoint (by name). If they exist, then add 
        # the player's number to their Player class instance.
        for player in data:
            if player['name'] == player_class.First_name:
               try:
                   player_class.Number = player['number']
               except:
                   print "Could not match player number for", player['name'],
                   print "on the", statget.name_to_id('',team_id=self.ID,reverse=True)
                   pass

            
    def top_five(self, stat):
        """
        Generates a list of tuples for the a given *stat*. 
        Each tuple contains a player name and value of their 
        statistic. Tuples are sorted before being returned.
        """
        # Make sure the team has the information needed to get
        # the stats 
        if not hasattr(self, "City"): self.get_info()
        if not hasattr(self, "Players"): self.add_players()
        # Establish list of players on the team
        Players = self.Players
        # init sorted stat list
        player_stat_list = []
        # Get the name and stat for each player and add the tuple to the list
        for player in self.Players:
            player_name = Players[player].First_name
            player_stat = Players[player].Stats[stat]
            player_stat_list.append((player_name, player_stat))
        # sort the list of tuples by the stat value
        # reverse=True means sort highest to lowest
        player_stat_list.sort(key= lambda set: set[1], reverse=True)
        # return the top 5 tuples from the list.
        return player_stat_list[0:5]

    
    def roster(self):
        """
        Generates a tuple for each player in the Team.Players dict 
        containing their name and number. 

        Also tacks on a team city and name at the front. 
        """
        # init the list of return info
        # Add the city and name as the first entry
        if not hasattr(self, 'City'): self.get_info()
        rost=[(self.City, self.Name, self.ID)]
        # Loop through players, create tuple and add to list
        for player in self.Players: 
            p = self.Players[player]
            if "Anon" not in p.First_name:
                rost.append((p.First_name,p.Number))
        # return the list
        return rost

    def add_games(self):

        # create a name that will match one in the json doc
        AUDL_Name = self.City + " " + self.Name

        # open the json schedule doc
        schedule = open("2014_AUDL_Schedule.json", 'r')
        # turn the file info into a python object
        data = json.loads(schedule.read())
        self.Games={}
        # if the game belongs to the current team, create it
        for game in data:
            if AUDL_Name in game['team']: #or AUDL_Name in game['opponent']:
                d = game['date']
                t = game['time']
                y = game['Year']
                if game['home/away'] == 'Home':
                    ht = game['team']
                    at = game['opponent']
                else:
                    at = game['team']
                    ht = game['opponent']
                self.Games[game['date']] = Game(d,t,y,ht,at)

    def populate_team_stats(self):
       """
       Gets the top five players for each stat in stat_list (hardcoded)
       and returns the players and their corresponding values into a tuple. 

       Tuples are appended into a list and returned to the Team class's 
       Top_Fives attribute.
       """
       if not hasattr(self,"Players"): self.add_players()
       stat_list=["Goals","Assists","Drops","Throwaways", "PMC", "Ds"]

       if not hasattr(self, 'City'): self.get_info()
       stat_out = [(self.City, self.Name, self.ID)]
       for stat in stat_list:
           stat_tup = (stat, self.top_five(stat))
           stat_out.append(stat_tup)
       
       # A dictionary containing the top five players for 
       # a given statistic (key) whose value is a tuple
       # containing the name of the player and their 
       # in sorted order. 
       self.Top_Fives = stat_out

    def return_schedule(self):
        AUDL_Name = self.City+ " " + self.Name
        sched = [AUDL_Name, self.ID ]
        for game in self.Games:
            if AUDL_Name in self.Games[game].home_team:
                opponent = self.Games[game].away_team
            else:
                opponent = self.Games[game].home_team
            game_tup = (self.Games[game].date, self.Games[game].time, opponent)
            sched.append(game_tup)

        return sched

    def return_scores(self):
        # set the Team's games to a shorter variable
        AUDL_Name = self.City+ " " + self.Name
        games = self.Games
        scores_list=[self.City + " " + self.Name]
        for game in games:
            # set game score. if the game hasn't started yet, default to 0-0
            score = '0-0' if games[game].Score == [] else games[game].Score
            # set oppponent name to whichever team doesn't match the team for which we're 
            # returning score info
            opp = games[game].home_team if games[game].away_team == AUDL_Name else games[game].away_team
            # create a tuple for this information
            game_tup = (games[game].date, opp, score)
            # add the tuple to the scores list for the current team
            scores_list.append(game_tup)
        return scores_list

class Player():
    """
    A class for containing information about a player.
    """
    def __init__(self):
        # A dictionary containing the players stats.
        # Keys: stat names Values: player's statistic 
        self.Stats = {}
        # String containing the player's first name
        self.First_name = ''
        # String containing the player's last name
        self.Last_name = ''
        # Intger of the players number
        self.Number = 0
        # string containing the player's height (in ft. & in.)
        self.Height = ''
        # string containing the player's weight (in lbs) 
        self.Weight = ''
        # string containing the player's age
        self.Age = 0

class Game():
    """
    A class for information about a given game in the AUDL
    """
    def __init__(self, date, time, year, home_team, away_team):
        # a string containing a has that uniquely identifies a game on the 
        # ultimate numbers server
        self.ID = ''    
        # a string containing the year of the season
        self.year = year
        # a string containing the date of the game
        self.date = date
        # a string containing a scheduled beginning time of the game
        self.time = time
        # a boolean declaring whether or not a game is over
        self.Finished = False
        # a list containing two tuples. 
        #each tuple contains a team name and their current score
        self.Score = []
        # a string containing the location of the game
        self.Location =''
        # a string containing the name of the away_team
        self.away_team = away_team
        # a string containing the name of the home_team
        self.home_team = home_team
        # a dictionary containing the home team's leader in a set of stats for this game
        # Keys: Statistic names Values: Tuple of a player name and their statistic
        self.Home_stats = {}
        # a dictionary containing the home team's leader in a set of stats for this game
        # Keys: Statistic names Values: Tuple of a player name and their statistic
        self.Away_stats = {}
        # a dictionary containing information about who scored each goal for each point
        # in the game
        self.Goals = {}
        # an int returning the current quarter 
        self.Quarter = 0

 
        
