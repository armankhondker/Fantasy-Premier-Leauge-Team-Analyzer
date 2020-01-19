import requests, traceback, re, getpass

#Team checker is intended of users to check their team selection for future gameweeks. 

#Hardcode team-id and login email. ***Never hardcode password!***
credentials = {'password': None,
               'login': 'armankhondker@gmail.com',
               'redirect_uri': 'https://fantasy.premierleague.com/a/login',
               'app': 'plfpl-web'
               }

team_id = 351353

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

#getpass method stops password echoing in terminal, menaing it remains hidden. 
else:
    print ("Password: ", end = '')
    credentials['password'] = getpass.getpass()

#Bootstrap API
bootstrap_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
get_data_bootstrap = requests.get(bootstrap_url).json()

#Establish session
session = requests.session()
session.post('https://users.premierleague.com/accounts/login/', data=credentials)

#Team API
team_api = 'https://fantasy.premierleague.com/api/my-team/%s/' % (team_id)
get_data_team = session.get(team_api).json()

sp = ' '

print('\n')
print('{0: >47}'.format("+/-"), '{0:>11}'.format('Purchase'), '{0: >8}'.format('Chance'))
print('Name', '{0:>36}'.format('Price'), '{0: >6}'.format('(GW)'), '{0: >7}'.format('Price'), '{0: >11}'.format('NextGW'), '{0: >7}'.format("News\n"))

for j in range(len(get_data_team['picks'])):
    id = get_data_team['picks'][j]['element']
    multiplier = get_data_team['picks'][j]['multiplier']
    vice_captain = get_data_team['picks'][j]['is_vice_captain']
    position = get_data_team['picks'][j]['position']

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
            price = get_data_bootstrap['elements'][i]['now_cost'] / 10
            price_change = get_data_bootstrap['elements'][i]['cost_change_event'] / 10
            next_round = get_data_bootstrap['elements'][i]['chance_of_playing_next_round']
            if next_round == None:
                next_round = 100
            news = get_data_bootstrap['elements'][i]['news']

            print("%-25s %-9s %-7.1f %-6.1f %-10.1f %-8d %s" %
                (name, player_status, price, price_change, (get_data_team['picks'][j]['purchase_price'] / 10),next_round, news))

            break

print ("\nFree transfers: %d" % (get_data_team['transfers']["limit"]))
print("Transfers used: %d" %  get_data_team['transfers']["made"])
print ("Team value: £%.1fM" % (get_data_team['transfers']["value"] / 10))
print ("Money in da bank: £%.1fM" % (get_data_team['transfers']["bank"] / 10))

print("\nWildcard: %s" % ("Yes" if len(get_data_team["chips"][0]["played_by_entry"]) == 0 else "No"))
print("Free hit: %s" % ("Yes" if len(get_data_team["chips"][1]["played_by_entry"]) == 0 else "No"))
print("Bench boost: %s" % ("Yes" if len(get_data_team["chips"][2]["played_by_entry"]) == 0 else "No"))
print("Triple captain: %s" % ("Yes" if len(get_data_team["chips"][2]["played_by_entry"]) == 0 else "No"))

#Transfers
#Latest transfers API
latest_transfer_url = 'https://fantasy.premierleague.com/api/entry/%s/transfers-latest/' % (team_id)
get_latest_transfer = session.get(latest_transfer_url).json()
print('\nTransfers:')
print('Player out' + 21*sp + 'Player in\n')

for j in range(len(get_latest_transfer)):
    trade = get_latest_transfer[j]
    flag_in = False
    flag_out = False
    name_in = None
    name_out = None
    
    i = 0
    while flag_out == False or flag_in == False:
        if flag_in == False and get_data_bootstrap['elements'][i]['id'] == trade["element_in"]:
            name_in = get_data_bootstrap['elements'][i]['web_name']
            flag_in = True

        if flag_out == False and get_data_bootstrap['elements'][i]['id'] == trade['element_out']:
            name_out = get_data_bootstrap['elements'][i]['web_name']
            flag_out = True
        
        i += 1
    print("%-30s %s" % (name_out, name_in))

print()

