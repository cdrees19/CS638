# Module for retrieving statistics from www.ultimate-numbers.com

import urllib2
import json

def top_three( team_id, stat, debug = False ):
    """ Get's the top five players on a team

    takes a team_id requests data from the ultimate-numbers
    server. Then sorts the data by the given stat and
    prints the top five players for that stat. """

    
  
    baseurl = 'http://www.ultimate-numbers.com/rest/view/team/'
    full_url= baseurl + str(team_id) + '/stats/player'


    #print full_url

    req = urllib2.Request(full_url)
    response = urllib2.urlopen(req)
    the_page = response.read()

    data = json.loads(the_page)

    data.sort(key = lambda player_asst: player_asst[stat], reverse= True )

    top_three = data[0:3]
    output = []
    for player in top_three[:]:
        if (debug): print "{0:10} {1:5}".format(player['playerName'], player[stat])
        output.append((player['playerName'],player[stat]))

    return output

def return_roster(team_id, debug = False):
    
    base_url='http://www.ultimate-numbers.com/rest/view/team/'
    full_url= base_url + team_id +'/players'
    if debug: print full_url

    req = urllib2.Request(full_url)
    response = urllib2.urlopen(req)
    page = response.read()

    data = json.loads(page)
    
    print name_to_id('', team_id=int(team_id), reverse=True) + ' roster:'
    output=[]

    for player in data:
        deets = json.loads(player['leaguevinePlayer'])
        print ( "%s %s %s" % ( deets['player']['first_name'], deets ['player']['last_name'], deets['number']))
        output.append((deets['player']['first_name'], deets ['player']['last_name'], deets['number']))
    return output

def name_to_id(team_name, team_id=0, reverse=False):
    """ Converts a team name to it's corresponding ID"""

    
    teams = {'Minnesota Wind Chill': 210001,
      'New York Empire': 208003,
      'DC Breeze': 206001,
      'Cincinnati Revolution': 183001,
      'Rochester Dragons': 208005,
      'Windy City Wildfire': 207003,
      'Toronto Rush': 195002,
      'Madison Radicals': 224002,
      'New Jersey Hammerheads': 230001,
      'Philadelphia Phoenix': 208004,
      'Detroit Mechanix': 219001,
      'Indianapolis Alley Cats': 253001}

    if reverse:
        for name, number in teams.items():
            if  team_id == number:
                return name
    else:
        return teams[team_name]

if __name__ == "__main__":
    import sys
    top_three(name_to_id(sys.argv[1]),sys.argv[2])
