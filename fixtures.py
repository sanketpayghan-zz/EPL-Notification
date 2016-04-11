
import requests
from datetime import datetime
import time
from json import loads
from gi.repository import Notify, GdkPixbuf
import pytz

class FixtureDetails(object):
    def __init__(self):
        self._context_url = 'http://live.premierleague.com/syndicationdata/context.json'
        self._score_url = ('http://live.premierleague.com/syndicationdata/'
                          'competitionId={0}/seasonId={1}/gameWeekId={2}/scores.json?{3}')
        self._sentinal_url = ('http://live.premierleague.com/syndicationdata/competitionId={0}'
                              '/seasonId={1}/gameWeekId={2}/sentinel.json')

    def get_match_details(self):
	scores = []
        now = datetime.now(pytz.timezone('Europe/London'))
        now = ''.join(str(now.date()).split('-'))
        response = requests.get(self._context_url)
        context = loads(response.text)
        if now == context['currentDay']:
            comp_id = context['competitionId']
            season_id = context['seasonId']
            gw_id = context['gameWeekId']
            response = requests.get(self._sentinal_url.format(comp_id, season_id, gw_id))
            sentinal = loads(response.text)
            score_id = sentinal['scores']
            response = requests.get(self._score_url.format(comp_id, season_id, gw_id, score_id))
            data = loads(response.text)['Data']
            for d in data:
                for score in d['Scores']:
                    scores.append(score)
        else: []
        return scores

class MatchDay(object):

    def get_match_time(self):
        scores = FixtureDetails().get_match_details()
        match_times = []
        for score in scores:
            if score['StatusId'] in [1, 2, 4]:
                match_times.append(score['DateTime'])
        return match_times


class Fixtures(object):
    def __init__(self):
        self._context_url = 'http://live.premierleague.com/syndicationdata/context.json'
        self._score_url = ('http://live.premierleague.com/syndicationdata/'
                          'competitionId={0}/seasonId={1}/gameWeekId={2}/scores.json?{3}')
        self._sentinal_url = ('http://live.premierleague.com/syndicationdata/competitionId={0}'
                              '/seasonId={1}/gameWeekId={2}/sentinel.json')

    def fixture(self):
        scores = FixtureDetails().get_match_details()
        live_scores = []
        for score in scores:
            if score['StatusId'] in [2, 4]:
                # score_str = score['HomeTeam']['Name'] +' ' + str(score['HomeTeam']['Score']) + ' ' + score['AwayTeam']['Name'] + ' ' + str(score['AwayTeam']['Score'])
                team_str = score['HomeTeam']['Name'] +' vs ' + score['AwayTeam']['Name']
                score_str = (score['HomeTeam']['Code'] + ' ' + str(score['HomeTeam']['Score']) + '\t\t' +
                            score['AwayTeam']['Code'] + ' ' + str(score['AwayTeam']['Score']))
                game_time = datetime.strptime(score['DateTime'], '%Y-%m-%dT%H:%M:%S')
                now = datetime.utcnow()

                time = now - game_time
                time_str = str(time.seconds // 60) + ' : ' + str((time.seconds//60) %60)
                live_scores.append({'team': team_str,
                                   'score': score_str,
                                   'time': unicode(time_str),
                                   'status': score['StatusId']
                                   })
        if not live_scores:
            return [], False
        return live_scores, True

class Notification(object):
    def __init__(self):
        self._icon = GdkPixbuf.Pixbuf.new_from_file("/home/sanket/sanket/selfStudy/live match notifications/icon.png")
        pass

    def notification(self):
        while(True):
            live_scores, valid = Fixtures().fixture()
            for score in live_scores:
                match_time = score['time']
                status = score['status']
                team = score['team']
                score = score['score']
                score_time = score + '    (Time:' + match_time + ')'
                if status != 1:
                    if status == 3:
                        score_time = score + '    (FT)'
                    elif status == 4:
                        score_time = score + '    (HT)'
                    Notify.init("Live Score")
                    send_notification = Notify.Notification.new(team,
                                                                score_time,
                                                                )
                    send_notification.set_icon_from_pixbuf(self._icon)
                    send_notification.show()
                    time.sleep(3)
                    send_notification.close()
                    Notify.uninit()
            if not valid:
                break
            time.sleep(300)


if __name__ == '__main__':
    Notification().notification()
