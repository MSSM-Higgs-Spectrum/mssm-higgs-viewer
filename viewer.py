"""
This is the projects main file, which reads the user input
and starts the other program components.
"""

import argparse
import ROOT

# create parser, add arguments
parser = argparse.ArgumentParser()
parser.add_argument("-tb", "--tangens_beta", required=True, help="tangens beta value", type=float)
parser.add_argument("-ma", "--m_A_range", required=True, help="m_A range to loop trough (minimum-maximum)", type=str)
parser.add_argument("-rfn", "--root_file_name", required=True, help="name of root file to use", type=str)
args = parser.parse_args()

# split m_A range into minimum and maximum value, cast to int
ma_min_str, ma_max_str = args.m_A_range.split("-")
ma_min = int(ma_min_str)
ma_max = int(ma_max_str)

# store root file to use
root_file_name = args.root_file_name

#store tangens beta value
tan_beta = args.tangens_beta

# open root file
f = ROOT.TFile(root_file_name)
# only regard the branch h -> bb
t = f.Get('br_h_bb')
# read values from root file into list
values = []
for i in range(ma_min, ma_max, 1):
    j = i - ma_min
    values.append(t.Interpolate(i, tan_beta))
    print(values[j])


