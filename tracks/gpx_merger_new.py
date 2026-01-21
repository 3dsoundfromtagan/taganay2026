# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 00:13:54 2026

@author: ostap
"""

import os
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def merge_gpx_files_simple(input_folder, output_file):
    """Объединение GPX файлов без расширений Garmin"""
    merged_gpx = gpxpy.gpx.GPX()
    merged_track = gpxpy.gpx.GPXTrack()
    merged_gpx.tracks.append(merged_track)
    merged_segment = gpxpy.gpx.GPXTrackSegment()
    merged_track.segments.append(merged_segment)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.gpx'):
            filepath = os.path.join(input_folder, filename)
            print(f"Обработка файла: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as gpx_file:
                try:
                    gpx = gpxpy.parse(gpx_file)
                    
                    for track in gpx.tracks:
                        for segment in track.segments:
                            for point in segment.points:
                                # Создаем новую точку без extensions
                                new_point = gpxpy.gpx.GPXTrackPoint(
                                    latitude=point.latitude,
                                    longitude=point.longitude,
                                    elevation=point.elevation,
                                    time=point.time
                                )
                                # Не копируем extensions
                                merged_segment.points.append(new_point)
                except Exception as e:
                    print(f"Ошибка при обработке файла {filename}: {e}")
    
    # Сортируем точки по времени
    merged_segment.points.sort(key=lambda point: point.time if point.time else datetime.min)
    
    # Сохраняем
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(merged_gpx.to_xml())
    
    print(f"Объединенный файл сохранен как: {output_file}")
    return merged_gpx

if __name__ == "__main__":
    input_folder = r'D:\adventures\taganay2026\taganay2026\tracks'
    output_file = 'merged.gpx'
    merged_gpx = merge_gpx_files_simple(input_folder, output_file)