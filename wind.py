"""Creates a dict of wind directions for weather.py"""

import numpy as np


dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
        'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW',
        'Calm']
L = len(dirs) - 1  # '-1' útaf logni
n = np.linspace(start=0,
                stop=360*(1-1/L),
                num=L)
n = np.append(n, 0)  # 'Calm'

wind = dict(zip(dirs, n))
