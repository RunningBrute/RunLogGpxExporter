import re
import requests
from itertools import chain


def open_run_log_session(user, passwd):
    run_log_session = requests.session()
    run_log_session.post('https://run-log.com/account/login/', data={'username': user,
                                                                     'password': passwd})
    return run_log_session


def get_num_of_pages(session):
    def extract_pagenum(page_str):
        return int(page_str.replace('page=', ''))
    training_list = session.get('https://run-log.com/training/list')
    pages = re.findall('page=\d+', training_list.text)
    num_of_page = max([extract_pagenum(page_str) for page_str in pages])
    print('Found {} pages of training to download.'.format(num_of_page))
    return num_of_page


def workout_ids(session, num_of_pages):
    def extract_id(s):
        return int(s.replace('show_workout(', ''))
    def ids_from_page(page_num):
        page_code = session.get('https://run-log.com/training/list?page={}'.format(page_num))
        workouts = re.findall('show_workout\(\d+', page_code.text)
        return [extract_id(workout_str) for workout_str in workouts]
    def get_ids(pages):
        print("Fetching workouts from {} pages.".format(pages))
        return [ids_from_page(page_num) for page_num in range(1, pages + 1)]
    return list(chain(*get_ids(num_of_pages)))


def get_id(page):
    id = re.findall('wt_id&quot;: \d+', page.text)[0]
    return id.replace('wt_id&quot;: ', '')


def get_date(page):
    date = re.findall('Data:</span><span class="value">\d+-\d+-\d+', page.text)[0]
    return date.replace('Data:</span><span class="value">', '')


def gpx_ids(session, workouts):
    print("Fetching workouts in search for gpx ids.")
    ids = []
    for count, workout_id in enumerate(workouts):
        page_code = session.get('https://run-log.com/workout/workout_show/{}'.format(workout_id))
        print('{}/{}'.format(count + 1, len(workouts)))
        try:
            workout = get_id(page_code), get_date(page_code)
            ids.append(workout)
        except:
            print('No gpx found for workout id {}!'.format(workout_id))
            pass
    return ids


def save_gpx(gpx, id, day):
    with open("dupa/{}_{}.gpx".format(day, id), "w") as f:
        f.write(gpx)


def download_gpxies(session, ids):
    def get_gpx(id):
        return session.get('https://run-log.com/tracks/export_workout_track/Rysmen/{}/gpx'.format(id)).text
    def correct_dates(gpx):
        return re.sub('\d+-\d+-\d+', day, gpx)
    def fill_activity_type(gpx):
        return re.sub('<trk><trkseg>', '<trk><type>RUNNING</type><trkseg>', gpx)
    for count, (id, day) in enumerate(ids):
        print("Downloading gpx: {} {}/{}".format(id, count + 1, len(ids)))
        gpx = fill_activity_type(correct_dates(get_gpx(id)))
        save_gpx(gpx, id, day)


run_log_session = open_run_log_session('Rysmen', 'testowe')
#ids = gpx_ids(run_log_session, workout_ids(run_log_session, get_num_of_pages(run_log_session)))
ids = gpx_ids(run_log_session, workout_ids(run_log_session, 1))
download_gpxies(run_log_session, ids)
