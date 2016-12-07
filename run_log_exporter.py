import re
import requests

run_log_session = requests.session()
run_log_session.post('https://run-log.com/account/login/', data={'username':'Rysmen', 'password':'testowe'})

r = run_log_session.get('https://run-log.com/training/list')

pages = re.findall('page=\d+', r.text)
max_page = max([int(i.replace('page=', '')) for i in pages])

print(max_page)
n = []

for i in range(1, max_page + 1):
    r = run_log_session.get('https://run-log.com/training/list?page={}'.format(i))
    m = re.findall('show_workout\(\d+', r.text)
    n += [int(j.replace('show_workout(', '')) for j in m]
        
k = []

for i in n:
    q = run_log_session.get('https://run-log.com/workout/workout_show/{}'.format(i))
    try:
        z = re.findall('wt_id&quot;: \d+', q.text)[0]
        c = re.findall('Data:</span><span class="value">\d+-\d+-\d+', q.text)[0]
        k.append((z.replace('wt_id&quot;: ', ''), c.replace('Data:</span><span class="value">', '')))
    except:
        print('No gpx!')
        pass
       
for i, d in k:
    r = run_log_session.get('https://run-log.com/tracks/export_workout_track/Rysmen/{}/gpx'.format(i))
    a = re.sub('\d+-\d+-\d+', d, r.text)
    with open("dupa/{}_{}.gpx".format(d,i),"w") as f:
        print('{}/{}'.format(b, len(k)))
        b += 1
        f.write(a)

print(a)
print(n) 
print(k)
print(len(n))
