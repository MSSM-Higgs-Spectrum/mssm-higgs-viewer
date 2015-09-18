# mssm-higgs-viewer

## General

The *mssm-higgs-viewer* uses simulated data in root format to create an animated gif file from it.

The used data was created with simulations using benchmark scenarios to predict the measurements of three neutral Higgs bosons according to the MSSM (Minimal Supersymmetric Standard Model) at the CMS detector.

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
| -tb | --tangent_beta | Tangent beta value (a mssm - parameter)|
| -ma | --m_A_range |m_A range to loop trough (minimum - maximum)|
| -rfn| --root_file_name | path and name of root file to use|
| -d  | --duration | animated GIF duration in milliseconds |
| -Hb | --list_higgs_bosons | list of Higgs boson(s) to show (H A h) |


#### Optional arguments:  

| short | long | content |
|------|-------|---------|
| -o  | --output_filename | GIF output filename |
| -s  | --skip_frames | only render every nth frame (default=1)
| -sgm| --sigma_gaussian | sigma value (as fixed value or in percent to mass) for gaussian function inside voigtian function to blur the peaks|
|  -h | --help | show this help message and exit


## Tests

The program was tested on Ubuntu and Fedora Linux with Root version 5.34.


## Links

Used benchmark data: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGMSSMNeutral

Benchmark scenarios explenation: http://arxiv.org/abs/1302.7033

ROOT: https://root.cern.ch/
