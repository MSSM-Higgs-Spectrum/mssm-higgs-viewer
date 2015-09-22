# coding=utf-8
import ROOT
import os
import gc
import time
from PIL import Image
from images2gif import writeGif
import math


def calc_max_voigt_height(width, sigma, xs, int_lumi=1e-15):
    """
    method estimates maximum voigt profile height (normalized to xs * int_lumi) for given lists of width and sigma
    estimation, see https://en.wikipedia.org/wiki/Voigt_profile
    :param width: list of voigt width values (gamma)
    :param sigma: list of voigt sigma values
    :param xs: list of cross section values
    :param int_lumi: luminosity
    :return: estimated maximum voigt profile height
    """
    height_list = []
    for i in xrange(len(width)):
        # # voigtian height ~= 15 * A / voigt_fwhm
        # more precise calculation:
        # f_g = 2 * sigma[i] * math.sqrt(2 * math.log(2))
        f_g = sigma[i] * 2.35482
        f_l = 2 * width[i]
        # f_v = (0.5346 * f_l) + sqrt((0.2166 * sqr(f_l)) + sqr(2 * sigma * f_g))
        f_v = (0.5346 * f_l) + math.sqrt((0.2166 * math.pow(f_l, 2)) + math.pow(f_g, 2))
        height = 15 * (xs[i] * int_lumi) / f_v
        # if height is greater than all past heights save
        height_list.append(height)
    return max(height_list)


def perf_time_measure(start_time, comment=''):
    end_time = time.time()
    print 'Δt =', round(end_time - start_time, 6), comment
    return end_time


def animate_higgs_peak(list_values_mass, list_values_width, list_values_xs, values_ma, list_higgs_boson, sigma_gaussian=None,
                       filename="animation.gif", duration=5000, frame_time=20, fast_mode=False, debug=0):
    if debug > 2:
        global perf
        perf = time.time()

    # disable gc
    gc.disable()

    if debug > 2:
        # performance time measurement
        perf = perf_time_measure(perf)

    # remove gif file (if present)
    try:
        os.remove(filename)
    except OSError:
        pass

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    num_bosons = len(list_values_mass)

    # calculate plot y axis range (max height)
    y_height = 0
    for n in xrange(num_bosons):
        # calc sigma:
        sigma = []
        if sigma_gaussian is None:
            # default sigma is 20% of mean value
            for i in xrange(len(list_values_mass[n])):
                sigma.append(list_values_mass[n][i] * 0.2)
        elif (sigma_gaussian is not None) and (sigma_gaussian.find('%') >= 0):
            # sigma can be specified in percent of mean value
            for i in xrange(len(list_values_mass[n])):
                sigma.append(list_values_mass[n][i] * float(sigma_gaussian[:-1]) / 100.0)
        else:
            # sigma is fixed and absolute
            for i in xrange(len(list_values_mass[n])):
                sigma.append(float(sigma_gaussian))
        height = calc_max_voigt_height(list_values_width[n], sigma, list_values_xs[n])
        print "height", height
        if height > y_height:
            y_height = height
    print "y_height", y_height

    ## animation_delay = math.ceil(duration * skip_frames / len(list_values_mass[0]))
    # animation_delay = 4 -> 40ms per frame -> 25fps (frame_time = 40)
    skip_frames = int(round(frame_time * len(list_values_mass[0]) / duration))
    if skip_frames < 1:
        # minimum
        skip_frames = 1

    rf = ROOT.RooFit

    if debug > 2:
        # performance time measurement
        perf = perf_time_measure(perf, 'some calcs')

    # suppress INFO:NumericIntegration log
    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

    ma_min = min(values_ma)
    ma_max = max(values_ma)
    ma_range = ma_max - ma_min
    x = ROOT.RooRealVar("x", "m / GeV", ma_min - ma_range, ma_max + ma_range)
    x.setRange("integrate", ma_min - ma_range, ma_max + ma_range)

    frame = x.frame()

    if num_bosons > 1:
        title = "Higgs bosons peaks"
    else:
        title = list_higgs_boson[0] + " Higgs Boson peak"
    frame.SetTitle(title)

    canvas = ROOT.TCanvas("canvas", "canvas", 1300, 750)

    width = []
    mean = []
    pdf = []
    sigma = []
    hist = []

    if debug > 2:
        # performance time measurement
        perf = perf_time_measure(perf, 'before RooRealVar loop')

    # do not modify ROOT file
    ROOT.TH1.AddDirectoryStatus()
    ROOT.TH1.AddDirectory(False)

    num_bins = int(round(len(values_ma) / skip_frames)) + 2
    for n in range(num_bosons):
        width.append(ROOT.RooRealVar("width", "width", 0))
        mean.append(ROOT.RooRealVar("mean", "mean", 0))
        sigma.append(ROOT.RooRealVar("sigma", "sigma", 0))
        pdf.append(ROOT.RooVoigtian("voigtian", "Voigtian", x, mean[n], width[n], sigma[n]))
        hist.append(ROOT.TH1F(list_higgs_boson[n], "", num_bins,
                              float(min(values_ma)), float(max(values_ma))))
    frame_filenames = []

    if debug > 2:
        # performance time measurement
        perf = perf_time_measure(perf, 'before main loop')

    if debug > 1:
        print 'Rendering', round(len(list_values_mass[0]) / skip_frames), 'frames ...'
        print 'Animation time:', round(len(list_values_mass[0]) / skip_frames) * 40, 'ms'

    for i in xrange(0, len(values_ma)):
        if debug > 2:
            # performance time measurement
            perf = perf_time_measure(perf, 'loop begin')

        if debug > 3:
            # run garbage collector
            print "gc: ", gc.collect()
            # performance time measurement
            perf = perf_time_measure(perf, 'loop gc')
        else:
            gc.collect()

        for n in range(num_bosons):
            mean[n].setVal(list_values_mass[n][i])
            width[n].setVal(list_values_width[n][i])
            if sigma_gaussian is None:
                # default sigma is 20% of mean value
                sigma[n].setVal(list_values_mass[n][i] * 0.2)
            elif (sigma_gaussian is not None) and (sigma_gaussian.find('%') >= 0):
                # sigma can be specified in percent of mean value
                sigma[n].setVal(list_values_mass[n][i] * float(sigma_gaussian[:-1]) / 100.0)
            else:
                # sigma is fixed and absolute
                sigma[n].setVal(float(sigma_gaussian))

            # fill and draw TH1F Histogram
            for k in xrange(hist[n].GetNbinsX() - 2):
                x.setVal(float(values_ma[k]))
                val = pdf[n].getVal(ROOT.RooArgSet(x))
                hist[n].SetBinContent(k + 1, val)
            # calculate normalization factor
            # get cross section from list, multiply by luminosity
            N = list_values_xs[n][i] * 10 * (10 ** -15)
            scale_factor = N / pdf[n].createIntegral(ROOT.RooArgSet(x), "integrate").getVal()
            print "scale_factor", scale_factor
            hist[n].Scale(scale_factor)
            # set previous estimated height
            hist[n].SetMaximum(y_height)
            ROOT.gStyle.SetHistFillColor(n + 2)
            ROOT.gStyle.SetHistFillStyle(3003)  # https://root.cern.ch/doc/master/classTAttFill.html#F2
            ROOT.gStyle.SetHistLineColor(n + 2)
            ROOT.gStyle.SetHistLineStyle(0)
            ROOT.gStyle.SetHistLineWidth(2)
            hist[n].UseCurrentStyle()
            hist[n].GetXaxis().SetRange(1, hist[n].GetNbinsX() - 1)
            hist[n].Draw("HIST SAME C")

        if debug > 2:
            # performance time measurement
            perf = perf_time_measure(perf, 'loop bosons plotted')

        if not fast_mode:
            # animation delay in centiseconds (10ms)
            canvas.Print(filename + "+" + str(int(round(frame_time / 10))))

        if fast_mode:
            frame_filename = 'tmp/' + filename + "_" + str(i) + '.png'
            canvas.Print(frame_filename)
            frame_filenames.append(frame_filename)

        if debug > 2:
            # performance time measurement
            perf = perf_time_measure(perf, 'loop canvas printed')

    if debug > 2:
        # performance time measurement
        perf = perf_time_measure(perf, 'loop done')

    if not fast_mode:
        # infinite loop gif
        canvas.Print(filename + "++100++")

    if fast_mode:
        # open frame images
        images = [Image.open(img) for img in frame_filenames]

        if debug > 2:
            # performance time measurement
            perf = perf_time_measure(perf, 'imgs loaded')

        # write gif
        writeGif(filename, images, duration=(frame_time/1000.0))

    if debug > 2:
        # performance time measurement
        perf = perf_time_measure(perf, 'GIF file created')

    if debug > 3:
        # run garbage collector
        print "gc: ", gc.collect()
    else:
        gc.collect()


if __name__ == '__main__':
    animate_higgs_peak([[10, 20, 40], [7, 15, 24], [9, 17, 26]], [[0.0002, 0.0001, 0.00008], [0.0001, 0.0002, 0.00015],
                        [0.0002, 0.0003, 0.00025]], [60, 70, 80], ['H', 'h', 'A'], '10%', filename='test.gif',
                        duration=1000, debug=3)
