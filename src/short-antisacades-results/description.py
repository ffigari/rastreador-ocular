import matplotlib.pyplot as plt

from utils.main import load_trials
from utils.main import group_by_run

trials = load_trials()
ts_by_run = group_by_run(trials)

ages = []
glasses = { 'si': 0, 'no': 0 }
video_cards = { 'integrada': 0, 'externa': 0, 'no especificado': 0 }
for run_id, ts in ts_by_run.items():
    sd = ts[0]['subject_data']

    ages.append(int(sd['edad']))

    if sd['anteojos'] == 'si':
        glasses['si'] += 1
    else:
        glasses['no'] += 1

    hw_response = sd['hardware'] if 'hardware' in sd else None
    is_integrated_card = hw_response is not None and any([
        hw in hw_response
        for hw
        in [
            'Intel Iris Plus Graphics',
            'MacBook pro 2019 16-inch',
            'Thinkpad E470',
            'no gpu externa',
            'interna',
            'Intel HD Graphics 3000',
            'Notebook Lenovo t14s',
            ' No (creo)',
            ' Laptop con placa integrada',
            'placa integrada'
        ]
    ])
    is_external_card = hw_response is not None and any([
        hw in sd['hardware']
        for hw
        in [
            'placa de video gt 635M2GB Intel5',
            'geforce gtx 1070',
            'radeon rx 540',
            'Placa de video externa'
        ]
    ])
    if is_integrated_card:
        video_cards['integrada'] += 1
    elif is_external_card:
        video_cards['externa'] += 1
    else:
        video_cards['no especificado'] += 1

fig, ax = plt.subplots()
fig.suptitle('distribución de edades')
ax.hist(ages, bins=list(range(min(ages), max(ages) + 1)), ec='black')
plt.show()

print("anteojos?")
for k, v in glasses.items():
    print("%s: %d" % (k, v))

print("placa interna?")
for k, v in video_cards.items():
    print("%s: %d" % (k, v))
