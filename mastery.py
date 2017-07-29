from riotwatcher import RiotWatcher
from collections import defaultdict

# constants
RANK_SOLO = 'RANKED_SOLO_5x5'
RANK_FLEX = 'RANKED_FLEX_SR'

# specifics
watcher = RiotWatcher('RGAPI-6c3cba46-35c1-40cb-89ed-07be45fc5093')
def_region = 'euw1'
"""
test values
name: lordcigm - summonerId: 85738091
champId: 222 - Jinx
"""

static_champid_map = {}


def load_champid_map():
    global static_champid_map
    print('Loading champid_map')
    data = watcher.static_data.champions(def_region)['data']
    static_champid_map = {d['id']: d['name'] for (name, d) in data.items()}
    print('Got champid_map')


def get_summoner_id(name, region=def_region):
    try:
        pl = watcher.summoner.by_name(region, name)
        return pl['id']
    except Exception:
        return None


def get_mastery_data(name, region=def_region):
    return get_mastery_data_id(get_summoner_id(name, region), region)


def get_mastery_data_id(id, region=def_region):
    """
    Output format:
    [{'championPoints': 113528, 'chestGranted': True,
        'championPointsSinceLastLevel': 91928, 'playerId': 85738091,
        'lastPlayTime': 1500807096000, 'championPointsUntilNextLevel': 0,
        'championId': 222, 'championLevel': 7, 'tokensEarned': 0}]
    """
    mastery = watcher.champion_mastery.by_summoner(region, id)
    for c in mastery:
        c['championName'] = get_champion_name(c['championId'])
    return mastery


def get_mastery_champ_id(id, champ, region=def_region):
    """
    picks from mastery_data based on champ id
    Output format:
    {'championPoints': 113528, 'chestGranted': True,
        'championPointsSinceLastLevel': 91928, 'playerId': 85738091,
        'lastPlayTime': 1500807096000, 'championPointsUntilNextLevel': 0,
        'championId': 222, 'championLevel': 7, 'tokensEarned': 0}
    """
    data = get_mastery_data_id(id, region)

    def search():
        for c in data:
            if c['championId'] == champ:
                return c
        return None
    champ = search()
    if champ is None:
        print("couldnt find championId", champ)
    else:
        return {
            "masteryPoints": champ["championPoints"],
            "masteryLevel": champ["championLevel"]
        }


def get_champion_name(champ_id, region=def_region):
    return static_champid_map[champ_id]


def get_league_data(name, region=def_region):
    data = watcher.league.positions_by_summoner(
        region, get_summoner_id(name, region))
    return {l['queueType']: '%s %s %d LP' % (l['tier'], l['rank'], l['leaguePoints']) for l in data}


def get_league_data_id(id, region=def_region):
    data = watcher.league.positions_by_summoner(
        region, id)
    return {l['queueType']: '%s %s %d LP' % (l['tier'], l['rank'], l['leaguePoints']) for l in data}


def get_current_game(name, region=def_region):
    id = get_summoner_id(name, region)
    current = watcher.spectator.by_summoner(region, id)
    partic = current['participants']

    def process_player(player):
        pl = {
            "name": player["summonerName"],
            "id": player["summonerId"],
            "championId": player["championId"],
            "championName": get_champion_name(player["championId"])
        }
        ranks = get_league_data_id(pl["id"], region)
        # print(ranks)
        pl["rank_solo"] = ranks.get(RANK_SOLO, "UR")
        pl["rank_flex"] = ranks.get(RANK_FLEX, "UR")
        # pl["ranks"] = ranks
        mastery = get_mastery_champ_id(pl["id"], pl["championId"], region)
        pl["mastery"] = "Level %d, %d points" % (
            mastery['masteryLevel'], mastery['masteryPoints'])
        return pl

    myteam = ''
    team_grp = defaultdict(list)
    for pl in partic:
        team_grp[pl['teamId']].append(process_player(pl))
        if pl['summonerId'] == id:
            myteam = pl['teamId']
    # a -> my team, b -> other team
    team_grp = {("a" if k == myteam else "b"): v for (k, v) in team_grp.items()}
    return team_grp


load_champid_map()
