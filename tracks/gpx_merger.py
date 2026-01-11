# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 19:16:45 2025

@author: ostap
"""

import os
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def merge_gpx_files(input_folder, output_file):
    # Создаем новый GPX файл для объединенных данных
    merged_gpx = gpxpy.gpx.GPX()
    
    # Создаем один трек в объединенном файле
    merged_track = gpxpy.gpx.GPXTrack()
    merged_gpx.tracks.append(merged_track)
    
    # Создаем один сегмент в объединенном треке
    merged_segment = gpxpy.gpx.GPXTrackSegment()
    merged_track.segments.append(merged_segment)
    
    # Перебираем все файлы в папке
    for filename in os.listdir(input_folder):
        if filename.endswith('.gpx'):
            filepath = os.path.join(input_folder, filename)
            print(f"Обработка файла: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as gpx_file:
                try:
                    gpx = gpxpy.parse(gpx_file)
                    
                    # Добавляем все точки из всех треков и сегментов
                    for track in gpx.tracks:
                        for segment in track.segments:
                            merged_segment.points.extend(segment.points)
                except Exception as e:
                    print(f"Ошибка при обработке файла {filename}: {e}")
    
    # Сортируем точки по времени
    merged_segment.points.sort(key=lambda point: point.time if point.time else datetime.min)
    
    # Сохраняем объединенный файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(merged_gpx.to_xml())
    
    print(f"Объединенный файл сохранен как: {output_file}")
    
    return merged_gpx

def plot_elevation_data(gpx):
    if not gpx.tracks or not gpx.tracks[0].segments or not gpx.tracks[0].segments[0].points:
        print("Нет данных для построения графиков")
        return
    
    points = gpx.tracks[0].segments[0].points
    
    # Подготовка данных
    elevations = []
    times = []
    distances = [0]
    prev_point = points[0]
    
    for i, point in enumerate(points[1:], 1):
        elevations.append(point.elevation)
        times.append(point.time)
        
        # Рассчитываем накопленное расстояние
        distance = prev_point.distance_2d(point)
        distances.append(distances[-1] + distance)
        prev_point = point
    
    # Первая точка (для согласования размеров массивов)
    elevations.insert(0, points[0].elevation)
    times.insert(0, points[0].time)
    
    # Преобразуем расстояния в километры
    distances_km = np.array(distances) / 1000
    
    # Создаем графики
    plt.figure(figsize=(15, 6))
    
    # График высоты от расстояния
    plt.subplot(1, 2, 1)
    plt.plot(distances_km, elevations, 'b-')
    plt.xlabel('Расстояние (км)')
    plt.ylabel('Высота (м)')
    plt.title('Зависимость высоты от расстояния')
    plt.grid(True)
    
    # График высоты от времени
    plt.subplot(1, 2, 2)
    plt.plot(times, elevations, 'r-')
    plt.xlabel('Дата и время')
    plt.ylabel('Высота (м)')
    plt.title('Зависимость высоты от времени')
    plt.grid(True)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # input_folder = input("Введите путь к папке с GPX-файлами: ").strip()
    # output_file = input("Введите имя выходного GPX-файла (например: merged_tracks.gpx): ").strip()
    
    
    
    if not os.path.isdir(input_folder):
        print("Указанная папка не существует!")
    else:
        merged_gpx = merge_gpx_files(input_folder, output_file)
        plot_elevation_data(merged_gpx)