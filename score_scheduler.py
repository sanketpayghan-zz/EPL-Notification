from datetime import datetime, timedelta
from threading import Timer
from fixtures import MatchDay, Fixtures, Notification
import schedule
import pytz
import time
from requests import ConnectionError

class ScheduleRun(object):

    def schedule_run(self):

        def get_time():
            try:
                timings = MatchDay().get_match_time()
                if timings:
                    time_str = timings[0]
                    game_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
                    game_time = game_time.replace(tzinfo=pytz.timezone('Europe/London')
                                                        ).astimezone(pytz.timezone('Europe/London'))
                    exec_date = game_time - datetime.now(pytz.timezone('Europe/London'))
                    if not exec_date > timedelta(seconds=1):
                        t = Timer(0, get_notification)
                        t.start()
                    seconds = int(exec_date.total_seconds())
                    print 'notification() scheduled at-'
                    print datetime.now() + timedelta(0, seconds)
                    t = Timer(seconds, get_notification)
                    t.start()
                else:
                    exec_date = datetime.now(pytz.timezone('Europe/London'))
                    print exec_date
                    exec_date = datetime(exec_date.year,
                                               exec_date.month,
                                               exec_date.day,
                                               tzinfo=pytz.timezone('Europe/London'))
                    exec_date = exec_date.astimezone(pytz.timezone('Asia/Kolkata'))
                    
                    exec_date = exec_date + timedelta(days=1, seconds=1)
                    exec_date = exec_date - datetime.now(pytz.timezone('Asia/Kolkata'))
                    print exec_date
                    seconds = int(exec_date.total_seconds())
                    print seconds
                    print 'get_time() scheduled at-'
                    print datetime.now() + timedelta(seconds=seconds)
                    t = Timer(seconds, get_time)
                    t.start()
            except ConnectionError, e:
                print str(e)
                print 'No internet connection. Will try again in 5 minutes.'
                t = Timer(300, get_time)
                t.start()
            except Exception, e:
                print str(e)
                return                 
        t = Timer(0, get_time)
        t.start()

        def get_notification():
            Notification().notification()
            t = Timer(0, get_time)
            t.start()
            pass

if __name__ == '__main__':
    ScheduleRun().schedule_run()