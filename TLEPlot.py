import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import Loader, EarthSatellite, Topos

# We really just want the filedialog from tkinter
import tkinter as tk
from tkinter import filedialog

from datetime import datetime
from os import path


def _calculateGroundTrack(earth, satellite, timeset):
    topoZero = Topos(latitude_degrees=0.0, longitude_degrees=0.0)
    satAbs = earth + satellite

    earthPosition = earth.at(timeset).position.km
    zeroPosition  = topoZero.at(timeset).position.km
    satPosition   = satAbs.at(timeset).position.km - earthPosition

    earthRotation = np.arctan2(zeroPosition[1], zeroPosition[2])
    sinRot = np.sin(-earthRotation)
    cosRot = np.cos(-earthRotation)
    
    xAdj = satPosition[0] * cosRot - satPosition[1] * sinRot
    yAdj = satPosition[0] * sinRot + satPosition[1] * cosRot

    rxy = np.sqrt(xAdj**2 + yAdj**2)
    satLat  = np.arctan2(satPosition[2], rxy)
    satLong = np.arctan2(yAdj, xAdj)

    plt.plot(np.rad2deg(satLong), np.rad2deg(satLat))


def main():
    # Set up and hide tkinter root window
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    if not path.exists(file_path):
        print("Error - no such file")
        quit()

    root.destroy()

    # Load earth position from ephemeris data
    sfLoader  = Loader('resources')
    ephemeris = sfLoader('de421.bsp')
    earth     = ephemeris['earth']

    # Setup timescale for calculating ground track
    ts    = sfLoader.timescale()
    now   = datetime.utcnow()
    steps = np.arange(0, 180, 1)
    time  = ts.utc(now.year, now.month, now.day, now.hour, steps)

    # Load satellite data from tle file
    satellites = sfLoader.tle_file(file_path)

    # Set up plot
    plt.figure()
    img = plt.imread('resources/map.png')
    plt.imshow(img, extent=[-180,180,-90,90])

    for sat in satellites:
        _calculateGroundTrack(earth, sat, time)

    plt.show()

if __name__ == "__main__":
    main()
