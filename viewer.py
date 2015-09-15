"""
This is the projects main file, which reads the user input
and starts the other program components.
"""

import argparse

# create parser, add arguments
parser = argparse.ArgumentParser()
parser.add_argument("-tb", "--tan_beta", required=True, help="tangens beta value", type=float)
parser.add_argument("-ma", "--m_A_range", required=True, help="m_A range to loop trough (minimum-maximum)", type=str)
parser.add_argument("-rfn", "--root_file_name", required=True, help="name of root file to use", type=str)
args = parser.parse_args()

# split m_A range into minimum and maximum value
ma_min, ma_max = args.m_A_range.split("-")

# store root file to use
root_file_name=args.root_file_name
print(root_file_name)

