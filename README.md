# mssm-higgs-viewer

## General

The *mssm-higgs-viewer* uses calculated data stored in root format to create an animated gif file from it.

The used data was created with theory calculations using benchmark scenarios to predict the measurements of three neutral Higgs bosons according to the MSSM (Minimal Supersymmetric Standard Model).

In the plot you can show the neutral Higgs bosons peaks in relation to a fixed tangent beta value and an over time changing m_A value.


## Requirements

To use the mssm higgs viwer you need to have installed:

* Python
* ROOT 5.34 with PyRoot and Roofit


## Usage 

The viewer.py is executable and can be started from command line like a shell script.

  
#### Required arguments:

| short | long | content |
|------|-------|---------|
| -i  | --input_filename | GIF output filename |
| -t  | --tangent_beta | Tangent beta value (a mssm - parameter)|
| -m  | --m_A_range |m_A range to loop trough (minimum - maximum)|
| -d  | --duration | animated GIF duration in milliseconds |
| -b  | --higgs_bosons  | list of Higgs boson(s) to show (H A h) |


#### Optional arguments:  

| short | long | content |
|------|-------|---------|
| -o  | --output_filename | GIF output filename |
| -d  | --duration | animated GIF duration in milliseconds
| -s  | --sigma_gaussian | sigma value (as fixed value or in percent to mass) for gaussian function inside voigtian function to blur the peaks|
| -h  | --help | show this help message and exit
|     | --frame_time | Time (in milliseconds) per GIF animation frame (default=30) |
|     | --fast_mode | use fast gif creation mode (larger filesize) |
| -v  | --verbose | increase output verbosity |


## Tests

The program was tested on Ubuntu and Fedora Linux with Root version 5.34.


## Sample

![sample animation](https://ww2.rleh.de/mssm/higgs-viewer.gif)


## Links

Used benchmark data: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGMSSMNeutral

Benchmark scenarios explenation: http://arxiv.org/abs/1302.7033

ROOT: https://root.cern.ch/
