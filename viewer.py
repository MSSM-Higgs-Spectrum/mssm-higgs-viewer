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

    parser.add_argument("-b", "--higgs_bosons",   required=True, help="Higgs boson(s) (H A h) to show",
                        nargs='+', dest="list_higgs_bosons")
    parser.add_argument("-t", "--tan_beta",       required=True,  type=float, help="tangent beta value")
    parser.add_argument("-m", "--m_A_range",      required=True,  type=str, help="m_A range to loop trough (min-max)")
    parser.add_argument("-s", "--sigma_gaussian", required=False, type=str,
                        help="sigma value (as fixed value or in percent to higgs boson mass) for gaussian function"
                             " inside voigtian function to blur the values")
    parser.add_argument("-p", "--production_mode", required=False, type=str, default="gg",
                        help="Higgs boson production mode (default=gg)", choices=['gg', 'bb5F', 'bb4F'])
    parser.add_argument("-y", "--decay_branch", required=False, type=str, help="select decay branch")
    parser.add_argument("-l", "--log_scale",      required=False, type=float, action='store', nargs='?', default=False,
                        help="use logarithmic scale for y axis (optional set y axis minimum; default=1e-18)")
    # args.log_scale: False if not set, None if set without value, else specified value

    parser.add_argument("-d", "--duration", required=True,  type=int, help="GIF animation duration in milliseconds")
    parser.add_argument("--frame_time",     required=False, type=int, default=30,
                        help="Time (in milliseconds) per GIF animation frame (default=30)")
    parser.add_argument("--fast_mode",      required=False, action="store_true", default=False,
                        help="use fast gif creation mode (larger filesize)")
    parser.add_argument("--keep_pictures",      required=False, action="store_true", default=False,
                        help="do not delete frame images (saved in '<filename>/<filename>_N.png') "
                             "(useful for LaTeX/beamer)")

    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")

    args = parser.parse_args()

    # split m_A range into minimum and maximum value, cast to int
    ma_min_str, ma_max_str = args.m_A_range.strip().split("-")
    ma_min = int(ma_min_str)
    ma_max = int(ma_max_str)
    ma_range = (ma_max - ma_min)

    fast_mode = args.fast_mode

    if args.keep_pictures and not fast_mode:
        fast_mode = True
        print "--fast_mode enabled (required for --keep_pictures)"

    # check, if min and max values are in diagram range
    if ma_min < 90 or ma_max > 2000:
        raise argparse.ArgumentTypeError("m_A has to be in range of 90 - 2000")

    if args.tan_beta < 0.5 or args.tan_beta > 60:
        raise argparse.ArgumentTypeError("tangent_beta has to be in range of 0.5 - 60")

    list_values_mass = []
    list_values_width = []
    list_values_xs = []
    list_values_br = []
    values_ma = []

    num_frames = int(round(float(args.duration) / float(args.frame_time)))
    ma_delta = (float(ma_range) / float(num_frames))

    for frame in xrange(1, (num_frames + 1)):
        values_ma.append(ma_min + (ma_delta * frame))

    # open root file
    f = ROOT.TFile(args.input_filename)

    # loop through the Higgs bosons list
    for boson_index in xrange(0, len(args.list_higgs_bosons)):
        # open TH2F histograms from root file for inline created dataset names
        root_mass = f.Get("m_" + args.list_higgs_bosons[boson_index])
        root_width = f.Get("width_" + args.list_higgs_bosons[boson_index])
        root_xs = f.Get("xs_" + args.production_mode + "_" + args.list_higgs_bosons[boson_index])
        # only read branching ratio dataset if decay branch is specified
        if args.decay_branch is not None:
            root_br = f.Get("br_" + args.list_higgs_bosons[boson_index] + "_" + args.decay_branch)

        # read values from root file into list
        values_mass = []
        values_width = []
        values_xs = []
        if args.decay_branch is not None:
            values_br = []
        # loop trough the m_A range
        for frame_index in xrange(num_frames):
            values_mass.append(root_mass.Interpolate(values_ma[frame_index], args.tan_beta))
            values_width.append(root_width.Interpolate(values_ma[frame_index], args.tan_beta))
            values_xs.append(root_xs.Interpolate(values_ma[frame_index], args.tan_beta))
            if args.decay_branch is not None:
                values_br.append(root_br.Interpolate(values_ma[frame_index], args.tan_beta))

        # if Higgs boson A is chosen, overwrite the only zeros containing mass list with values_ma
        if args.list_higgs_bosons[boson_index] == 'A':
            values_mass = values_ma

        list_values_mass.append(values_mass)
        list_values_width.append(values_width)
        list_values_xs.append(values_xs)
        if args.decay_branch is not None:
            list_values_br.append(values_br)

    if args.verbose > 1:
        print "list_higgs_bosons =", args.list_higgs_bosons
        print "list_values_width =", list_values_width
        print "list_values_mass = ", list_values_mass
        print "list_values_xs = ", list_values_xs

    animate_higgs_peak(values_ma,
                       list_values_mass,
                       list_values_width,
                       list_values_xs,
                       list_values_br,
                       args.tan_beta,
                       args.list_higgs_bosons,
                       args.sigma_gaussian,
                       args.production_mode,
                       args.output_filename,
                       fast_mode=fast_mode,
                       keep_frames=args.keep_pictures,
                       frame_time=args.frame_time,
                       debug=args.verbose,
                       log_scale=args.log_scale)


if __name__ == '__main__':
    main()
