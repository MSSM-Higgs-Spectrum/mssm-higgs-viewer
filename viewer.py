#!/usr/bin/env python

"""
This is the projects main file, which reads the user input
and starts the other program components.
"""

import argparse
import ROOT
from animatehiggspeak import animate_higgs_peak


def main():
    # create parser, add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-tb", "--tangent_beta", required=True, help="tangent beta value", type=float)
    parser.add_argument("-ma", "--m_A_range", required=True, help="m_A range to loop trough (min-max)", type=str)
    parser.add_argument("-rfn", "--root_file_name", required=True, help="name of root file to use", type=str)
    parser.add_argument("-d", "--duration", required=True, help="animated GIF duration in milliseconds", type=int)
    parser.add_argument("-o", "--output_filename", required=False, help="GIF output filename", type=str)
    parser.add_argument("-s", "--skip_frames", required=False, help="only render every nth frame (default=1)", type=int)
    parser.add_argument("-Hb", "--list_higgs_bosons", nargs='+', required=True, help="disintegrating Higgs boson(s) (H A h)")
    args = parser.parse_args()

    # split m_A range into minimum and maximum value, cast to int
    ma_min_str, ma_max_str = args.m_A_range.split("-")
    ma_min = int(ma_min_str)
    ma_max = int(ma_max_str)

    # store args
    root_file_name = args.root_file_name
    tan_beta = args.tangent_beta
    output_filename = args.output_filename
    skip_frames = args.skip_frames
    duration = args.duration
    list_higgs_bosons = args.list_higgs_bosons

    list_values_mass = []
    list_values_width = []
    values_ma = []

    # loop through the Higgs bosons list
    for i in range(0, len(list_higgs_bosons)):

        higgs_boson = list_higgs_bosons[i]

        # construct dataset name
        dataset_mass_name = "m_" + higgs_boson
        dataset_width_name = "width_" + higgs_boson

        # open root file
        f = ROOT.TFile(root_file_name)

        # create mass and width list
        t = f.Get(dataset_mass_name)
        u = f.Get(dataset_width_name)
        # read values from root file into list
        values_mass = []
        values_width = []
        # loop trough the m_A range
        for i in range(ma_min, ma_max, 1):
            j = i - ma_min
            values_mass.append(t.Interpolate(i, tan_beta))
            values_width.append(u.Interpolate(i, tan_beta))
            values_ma.append(i)

        # if Higgs boson A is chosen, overwrite the only zeros containing mass list with values_ma
        if higgs_boson == 'A':
            values_mass = values_ma

        list_values_mass.append(values_mass)
        list_values_width.append(values_width)

    # for debugging
    print(list_higgs_bosons)
    print(list_values_width)
    print(list_values_mass)

    if output_filename is not None and skip_frames is not None:
        animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_bosons, duration=duration, skipframes=skip_frames,
                           filename=output_filename)
    elif output_filename is not None:
        animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_bosons, duration=duration,
                           filename=output_filename)
    elif skip_frames is not None:
        animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_bosons, duration=duration, skipframes=skip_frames)
    else:
        animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_bosons, duration=duration)


if __name__ == '__main__':
    main()
