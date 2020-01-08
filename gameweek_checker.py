import requests, traceback, re, getpass

#Gameweek checker is used to check the amount of points you received in a week and where you rank in your leauges

#Hardcode team-id and login email. ***Never hardcode password!***
credentials = {'password': None,
               'login': 'armankhondker@gmail.com',
               'redirect_uri': 'https://fantasy.premierleague.com/a/login',
               'app': 'plfpl-web'
               }

team_id = 351353

#Only ask for validation if team_id, email and password havn't been set
if team_id == None or credentials['login'] == None:
    while True:
        print ("Enter team ID: ", end = '')
        team_id = input()
        try:
            int(team_id)
        except:
            print("Your game id is an all integer code")
            continue
        
        print ("Email: ", end = '')
        email = input()
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if match == None:
            print('Bad email please re-enter')
            continue
        credentials['login'] = email

        print ("Password: ", end = '')
        credentials['password'] = getpass.getpass()
        break

#getpass method stops password echoing in terminal.
else:
    print ("Password: ", end = '')
    credentials['password'] = getpass.getpass()

#Bootstrap API
bootstrap_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
get_data_bootstrap = requests.get(bootstrap_url).json()

#Establish session
session = requests.session()
session.post('https://users.premierleague.com/accounts/login/', data=credentials)

#Entry section
entry_api = 'https://fantasy.premierleague.com/api/entry/%s/' % team_id
get_data_entry = session.get(entry_api).json()

#gw_Team API
gw_team_api = 'https://fantasy.premierleague.com/api/entry/%s/event/%s/picks/' % (team_id, get_data_entry["current_event"])
get_gw_team = session.get(gw_team_api).json()

sp = ' '
speed_gw_points = 0

print()
print('{0: >42}'.format("Points"), '{0:>13}'.format('+/-'), '{0: >9}'.format('Chance'))
print('Name', '{0:>35}'.format('(GW)'), '{0: >9}'.format('Price'), '{0: >6}'.format('(GW)'), '{0: >8}'.format('NextGW'), '{0: >7}'.format("News\n"))

for j in range(len(get_gw_team['picks'])):
    id = get_gw_team['picks'][j]['element']
    multiplier = get_gw_team['picks'][j]['multiplier']
    vice_captain = get_gw_team['picks'][j]['is_vice_captain']
    position = get_gw_team['picks'][j]['position']

    if multiplier == 2:
        player_status = "(C)"
    elif multiplier == 3:
        player_status = "(TC)"
    elif vice_captain == True:
        player_status = "(VC)"
    elif multiplier == 0:
        player_status = "(Bench)"
    else:
        player_status = ""

    for i in range(len(get_data_bootstrap['elements'])):
        if get_data_bootstrap['elements'][i]['id'] == id:
            name = get_data_bootstrap['elements'][i]['web_name']
            gw_points = get_data_bootstrap['elements'][i]['event_points']
            if multiplier == 2:
                gw_points *= 2
            elif multiplier == 3:
                gw_points *= 3
            price = get_data_bootstrap['elements'][i]['now_cost'] / 10
            price_change = get_data_bootstrap['elements'][i]['cost_change_event'] / 10
            next_round = get_data_bootstrap['elements'][i]['chance_of_playing_next_round']
            if next_round == None:
                next_round = 100
            news = get_data_bootstrap['elements'][i]['news']

            if multiplier > 0:
                speed_gw_points += gw_points

            print("%-25s %-9s %-8d %-7.1f %-6.1f %-8d %s" %
                (name, player_status, gw_points, price, price_change, next_round, news))
            
            break

print ("\n\nGameweek points: %d (%d)       \tOverall points: %-7d" %
    (speed_gw_points, get_gw_team["entry_history"]["event_transfers_cost"], 
        get_gw_team["entry_history"]["total_points"]))

print ("Gameweek rank:   %-7s\tOverall rank:   %-7s\n" %
    (get_gw_team["entry_history"]["rank"], get_gw_team["entry_history"]["overall_rank"]))

print ("\nH2H Leagues:\n")
print (sp*40 + "Prev" + sp*7 + "Curr" + sp*7 + "Rank" + sp*7 + "Leader")
print ("League Name" + sp*29 + "Rank" + sp*7 + "Rank" + sp*7 + "Diff" + sp*7 + "Points\n")

for i in range(len(get_data_entry['leagues']['h2h'])):
    league_id = get_data_entry['leagues']['h2h'][i]['id']
    league_name = get_data_entry['leagues']['h2h'][i]['name']
    previous_rank = get_data_entry['leagues']['h2h'][i]['entry_last_rank']
    current_rank = get_data_entry['leagues']['h2h'][i]['entry_rank']
    rank_difference = get_data_entry['leagues']['h2h'][i]['entry_last_rank'] - current_rank

    league_api = 'https://fantasy.premierleague.com/api/leagues-h2h/%s/standings/' % league_id
    get_data_league = session.get(league_api).json()
    league_leader = get_data_league['standings']['results'][0]['total']
    point_differential = league_leader - get_data_league['standings']['results'][current_rank - 1]['total']

    print ("%-39s %-10d %-10d %-10d %d (%d)" %
        (league_name, previous_rank, current_rank, rank_difference, league_leader, point_differential))

print ("\n\nClassic Leagues:\n")
print (sp*40 + "Prev" + sp*7 + "Curr" + sp*7 + "Rank" + sp*7 + "Leader")
print ("League Name" + sp*29 + "Rank" + sp*7 + "Rank" + sp*7 + "Diff" + sp*7 + "Points\n")

for i in range (len(get_data_entry['leagues']['classic'])):
    league_id = get_data_entry['leagues']['classic'][i]['id']
    league_name = get_data_entry['leagues']['classic'][i]['name']
    previous_rank = get_data_entry['leagues']['classic'][i]['entry_last_rank']
    current_rank = get_data_entry['leagues']['classic'][i]["entry_rank"]
    rank_difference = previous_rank - current_rank

    league_api = 'https://fantasy.premierleague.com/api/leagues-classic/%s/standings/' % league_id
    get_data_league = session.get(league_api).json()

    league_leader = get_data_league['standings']['results'][0]['total']
    league_difference = league_leader - get_data_entry['summary_overall_points']

    print ("%-39s %-10d %-10d %-10d %d (%d)" % (league_name, previous_rank, current_rank,
        rank_difference, league_leader, league_difference))

print ()