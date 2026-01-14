# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 23:48:09 2024

@author: ostap
"""

import gpxpy
import gpxpy.gpx
import pathlib
import matplotlib.pyplot as plt
import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
import numpy as np
import pandas as pd
from scipy import ndimage
from scipy import interpolate
from scipy import signal
from matplotlib.ticker import MaxNLocator, AutoMinorLocator, FuncFormatter
from matplotlib.dates import DateFormatter


import gpxpy
import gpxpy.gpx
from geopy.distance import great_circle
# Parsing an existing file:
# -------------------------


gpx_file = open('merged.gpx', 'r')

gpx = gpxpy.parse(gpx_file)
#опытным путем установлено что трек уже не пушистый но еще не режется при удалении 6 точек из 7
gpx.reduce_points(1300)
# times = []
# elevations = []
# for track in gpx.tracks:
#     for segment in track.segments:
#         for point in segment.points:
#             times.append(point.time)
#             elevations.append(point.elevation)
#             # plt.plot(point.time, point.elevation)
#             # print(f'Point at ({point.time},{point.longitude}) -> {point.elevation}')
            
# plt.plot(elevations)


def get_data(gpx):
    '''Currently Only does the first track and first segment'''
    tzf = TimezoneFinder()
    # Use lists for the data not a DataFrame
    lat = []
    lon = []
    ele = []
    time = []
    n_trk = len(gpx.tracks)
    for trk in range(n_trk):
        n_seg = len(gpx.tracks[trk].segments)
        first = True  # Flag to get the timezone for this track
        for seg in range(n_seg):
            points = gpx.tracks[trk].segments[seg].points
            for point in points:
                if(first):
                    # Get the time zone from the first point in first segment
                    tz_name = tzf.timezone_at(lng=point.longitude, lat=point.latitude)
                    first = False
                lat.append(point.latitude)
                lon.append(point.longitude)
                ele.append(point.elevation)
                try:
                    new_time = point.time.astimezone(ZoneInfo(tz_name))
                except:
                    new_time = point.time.astimezone(ZoneInfo('UTC'))
                time.append(new_time)
    return lat, lon, ele, time

# %%
_, _, elevations, times = get_data(gpx)
plt.plot(times, elevations)

# %%
df = pd.DataFrame([] , index = [], columns = ['time','seconde', 'lat', 'long',
                                              'elevation','dist'])
i=0
t0 = gpx.tracks[0].segments[0].points[0].time
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if i==0:
                df.loc[i]=[(point.time-t0),(point.time-t0).seconds,
                           point.latitude, point.longitude, point.elevation,0.]
            else:
                dist = df.dist[i-1] + great_circle((point.latitude,
                                                    point.longitude),
                                                   (df.lat[i-1],df.long[i-1])).km
                df.loc[i]=[(point.time-t0),(point.time-t0).seconds,
                           point.latitude, point.longitude, point.elevation,dist]
            i=i+1
            
# %%
passes = {
    'Перья': {
        'point_num': 50,
        'elevation': 1080,
        },
    
    'Круглица': {
        'point_num': 130,
        'elevation': 1220,
        },
    
    'Метеостанция': {
        'point_num': 330,
        'elevation': 1220,
        },
    
    'Ицыл': {
        'point_num': 520,
        'elevation': 1080,
        },
    
    'Крутой Ключ': {
        'point_num': 656,
        'elevation': 800,
        },
}





# %% distance plot

fig, ax = plt.subplots(figsize=(15, 6))
my_params = {'font.size':24}
plt.rcParams.update(my_params)
ax.plot(1.2*df.dist,df.elevation,'b',label = "Elevation",
        linewidth=5)
ax.set_xlabel("Расстояние, км")
ax.set_ylabel("Высота, м")
# ax.grid()
ax.set_ylim(0, 1500)
ax.set_xlim(0, 100)
for count, name in enumerate(passes.keys()):
    ax.annotate(name, (df.dist.iloc[passes[name]['point_num']],
                       passes[name]['elevation']))
plt.tight_layout()
# fig.savefig('../pics/elevation_vs_distance.pdf')

# %%
passes = {
    'Перья': {
        'point_num': 0,
        'elevation': 1080,
        },
    
    'Круглица': {
        'point_num': 100,
        'elevation': 1220,
        },
    
    'Метеостанция': {
        'point_num': 255,
        'elevation': 1220,
        },
    
    'Ицыл': {
        'point_num': 445,
        'elevation': 1080,
        },
    
    'Крутой Ключ': {
        'point_num': 610,
        'elevation': 800,
        },
}
# %% time plot

fig, ax = plt.subplots(figsize=(15, 6))
my_params = {'font.size':24}
plt.rcParams.update(my_params)
ax.plot(times ,elevations,'b',label = "Elevation",
        linewidth=5)
ax.set_xlabel("Время, дни")
ax.set_ylabel("Высота, м") 

date_form = DateFormatter("%d")
ax.xaxis.set_major_locator(MaxNLocator(500, integer=True))
ax.xaxis.set_major_formatter(date_form)
# ax.grid()
ax.set_ylim(0, 1500)
# ax.set_xlim(0, 120)
for count, name in enumerate(passes.keys()):
    ax.annotate(name, (times[passes[name]['point_num']],
                       passes[name]['elevation']))
fig.tight_layout()
# %%
fig.savefig('../pics/elevation_vs_time.pdf')

# %% perepad calc

# Сглаживаем данные для уменьшения влияния шума GPS
window_sizes = np.arange(1, 100, dtype=int)  # количество точек для скользящего среднего
ascs = []
for window_size in window_sizes:
    df['elevation_smooth'] = df['elevation'].rolling(window=window_size, center=True).mean()
    
    # Заполняем NaN значения
    df['elevation_smooth'] = df['elevation_smooth'].interpolate()
    
    # Пересчитываем перепады по сглаженным данным
    df['elevation_smooth_diff'] = df.elevation_smooth.diff()
    
    # Суммарный подъем по сглаженным данным
    ascents_smooth = df[df['elevation_smooth_diff'] > 0]['elevation_smooth_diff']
    total_ascent_smooth = ascents_smooth.sum()
    ascs.append(total_ascent_smooth)
    print(f"Суммарный подъем (сглаженные данные): {total_ascent_smooth:.0f} м")
    
# зашло window_size = 4
window_size = 4
df['elevation_smooth'] = df['elevation'].rolling(window=window_size, center=True).mean()

# Заполняем NaN значения
df['elevation_smooth'] = df['elevation_smooth'].interpolate()

# Пересчитываем перепады по сглаженным данным
df['elevation_smooth_diff'] = df.elevation_smooth.diff()

# Суммарный подъем по сглаженным данным
ascents_smooth = df[df['elevation_smooth_diff'] > 0]['elevation_smooth_diff']
total_ascent_smooth = ascents_smooth.sum()

print(f"Суммарный подъем (сглаженные данные): {total_ascent_smooth:.0f} м")