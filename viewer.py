#!/usr/bin/env python
# coding=utf-8

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
    parser.add_argument("-i", "--input_filename",  required=True, type=str, help="ROOT input filename")
    parser.add_argument("-o", "--output_filename", required=True, type=str, help="GIF output filename")

    parser.add_argument("-b", "--higgs_bosons",   required=True, help="disintegrating Higgs boson(s) (H A h)",
                        nargs='+', dest="list_higgs_bosons")
    parser.add_argument("-t", "--tangent_beta",   required=True,  type=float, help="tangent beta value")
    parser.add_argument("-m", "--m_A_range",      required=True,  type=str, help="m_A range to loop trough (min-max)")
    parser.add_argument("-s", "--sigma_gaussian", required=False, type=str,
                        help="sigma value (as fixed value or in percent to mass) for gaussian function inside voigtian"
                             " function to blur the values")

    parser.add_argument("-d", "--duration", required=True,  type=int, help="GIF animation duration in milliseconds")
    parser.add_argument("--frame_time",     required=False, type=int, default=30,
                        help="Time (in milliseconds) per GIF animation frame (default=30)")
    parser.add_argument("--fast_mode",      required=False, action="store_true", default=False,
                        help="use fast gif creation mode (larger filesize)")

    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")

    args = parser.parse_args()

    # split m_A range into minimum and maximum value, cast to int
    ma_min_str, ma_max_str = args.m_A_range.split("-")
    ma_min = int(ma_min_str)
    ma_max = int(ma_max_str)

    # store args
    input_filename = args.input_filename
    tan_beta = args.tangent_beta
    output_filename = args.output_filename
    duration = args.duration
    list_higgs_bosons = args.list_higgs_bosons
    frame_time = args.frame_time
    debug = args.verbose

    fast_mode = args.fast_mode

     # check, if min and max values are in diagram range
    if ma_min < 90 or ma_max > 2000:
        raise argparse.ArgumentTypeError("m_A has to be in range of 90 - 2000")

    if tan_beta < 0.5 or tan_beta > 60:
        raise argparse.ArgumentTypeError("tangent_beta has to be in range of 0.5 - 60")

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
        f = ROOT.TFile(input_filename)

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

    if debug > 1:
        print "list_higgs_bosons =", list_higgs_bosons
        print "list_values_width =", list_values_width
        print "list_values_mass = ", list_values_mass

    animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_bosons, args.sigma_gaussian,
                       duration=duration, filename=output_filename, fast_mode=fast_mode, frame_time=frame_time,
                       debug=debug)


if __name__ == '__main__':
    main()
