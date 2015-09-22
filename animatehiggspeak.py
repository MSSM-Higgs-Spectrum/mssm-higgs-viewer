# coding=utf-8
import ROOT
import os
import gc
import time
from PIL import Image
from images2gif import writeGif
import math


def calc_max_voigt_height(width, sigma_gaussian, mass, xs, num_bosons, int_lumi=1e-15):
    """
    method estimates maximum voigt profile height (normalized to xs * int_lumi) for given lists of width and sigma
    estimation, see https://en.wikipedia.org/wiki/Voigt_profile
    :param width: list of voigt width values lists (gamma)
    :param sigma_gaussian: sigma value (string)
    :param mass list of mass value lists
    :param xs: list of cross section values lists
    :param num_bosons number of higgs bosons
    :param int_lumi: luminosity
    :return: estimated maximum voigt profile height
    """
    # calc sigma
    sigma = []
    for n in xrange(num_bosons):
        if sigma_gaussian is None:
            # default sigma is 20% of mean value
            for i in xrange(len(mass[n])):
                sigma.append(mass[n][i] * 0.2)
        elif (sigma_gaussian is not None) and (sigma_gaussian.find('%') >= 0):
            # sigma can be specified in percent of mean value
            for i in xrange(len(mass[n])):
                sigma.append(mass[n][i] * float(sigma_gaussian[:-1]) / 100.0)
        else:
            # sigma is fixed and absolute
            for i in xrange(len(mass[n])):
                sigma.append(float(sigma_gaussian))

    height_list = []
    for i in xrange(len(width)):
        l_height = []
        for n in xrange(num_bosons):
            # # voigtian height ~= 15 * A / voigt_fwhm
            # more precise calculation:
            # f_g = 2 * sigma[i] * math.sqrt(2 * math.log(2))
            f_g = sigma[i] * 2.35482
            f_l = 2 * width[n][i]
            # f_v = (0.5346 * f_l) + sqrt((0.2166 * sqr(f_l)) + sqr(2 * sigma * f_g))
            f_v = (0.5346 * f_l) + math.sqrt((0.2166 * math.pow(f_l, 2)) + math.pow(f_g, 2))
            height = 15 * (xs[n][i] * int_lumi) / f_v
            # if height is greater than all past heights save
            l_height.append(height)
        height_list.append(max(l_height))
    return max(height_list)


def perf_time_measure(start_time, comment=''):
    end_time = time.time()
    print 'Δt =', round(end_time - start_time, 6), comment
    return end_time


def get_ma_val(ma_list, bin, nr_bins):
    ma_min = min(ma_list)
    ma_max = max(ma_list)
    ma_range = ma_max - ma_min
    ma_delta = float(ma_range) / float(nr_bins)
    return ma_min + (bin * ma_delta)


def animate_higgs_peak(list_values_mass, list_values_width, list_values_xs, values_ma, list_higgs_boson,
                       sigma_gaussian=None, filename="animation.gif", duration=5000, frame_time=20, fast_mode=False,
                       keep_frames=True, debug=0):
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

    if not os.path.exists(filename[:-4] + '/'):
        os.makedirs(filename[:-4] + '/')

    num_bosons = len(list_values_mass)

    # calculate plot y axis range (max height)
    y_height = calc_max_voigt_height(list_values_width, sigma_gaussian, list_values_mass, list_values_xs, num_bosons)
    print "height", y_height

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

    num_bins_visible = 1000
    for n in range(num_bosons):
        width.append(ROOT.RooRealVar("width", "width", 0))
        mean.append(ROOT.RooRealVar("mean", "mean", 0))
        sigma.append(ROOT.RooRealVar("sigma", "sigma", 0))
        pdf.append(ROOT.RooVoigtian("voigtian", "Voigtian", x, mean[n], width[n], sigma[n]))
        hist.append(ROOT.TH1F(list_higgs_boson[n], "", num_bins_visible,
                              float(min(values_ma)), float(max(values_ma))))
    hist_sum = ROOT.TH1F("sum", "", num_bins_visible,
                          float(min(values_ma)), float(max(values_ma)))
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
            num_bins_visible = hist[n].GetNbinsX() - 2
            for k in xrange(num_bins_visible):
                x.setVal(get_ma_val(values_ma, k, num_bins_visible))
                val = pdf[n].getVal(ROOT.RooArgSet(x))
                hist[n].SetBinContent(k + 1, val)
            # calculate normalization factor
            # get cross section from list, multiply by luminosity
            N = list_values_xs[n][i] * 10 * (10 ** -15)
            scale_factor = N / pdf[n].createIntegral(ROOT.RooArgSet(x), "integrate").getVal()
            hist[n].Scale(scale_factor)

        # set sum of histogram bin values as hist_sum histogram value
        for l in xrange(hist_sum.GetNbinsX()):
            val = 0.0
            for m in xrange(num_bosons):
                val += hist[m].GetBinContent(l)
            hist_sum.SetBinContent(l, val)

        # set previous estimated height
        hist_sum.SetMaximum(y_height)
        # set histogram style
        # https://root.cern.ch/doc/master/classTAttFill.html#F2
        ROOT.gStyle.SetHistFillColor(1)
        ROOT.gStyle.SetHistFillStyle(3003)
        ROOT.gStyle.SetHistLineColor(1)
        ROOT.gStyle.SetHistLineStyle(0)
        ROOT.gStyle.SetHistLineWidth(2)
        hist_sum.UseCurrentStyle()
        # set x axis range
        hist_sum.GetXaxis().SetRange(1, num_bins_visible)
        # draw histogram
        hist_sum.Draw("HIST SAME")

        for n in range(num_bosons):
            # set previous estimated height
            hist[n].SetMaximum(y_height)
            # set histogram style
            ROOT.gStyle.SetHistFillColor(n + 2)
            ROOT.gStyle.SetHistFillStyle(3003)
            ROOT.gStyle.SetHistLineColor(n + 2)
            ROOT.gStyle.SetHistLineStyle(0)
            ROOT.gStyle.SetHistLineWidth(2)
            hist[n].UseCurrentStyle()
            # set x axis range
            hist[n].GetXaxis().SetRange(1, num_bins_visible)
            # draw histogram
            hist[n].Draw("HIST SAME")

        if debug > 2:
            # performance time measurement
            perf = perf_time_measure(perf, 'loop bosons plotted')

        if not fast_mode:
            # animation delay in centiseconds (10ms)
            canvas.Print(filename + "+" + str(int(round(frame_time / 10))))

        if fast_mode:
            frame_filename = filename[:-4] + '/' + filename[:-4] + "_" + str(i) + '.png'
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

        if not keep_frames:
            for frame_filename in frame_filenames:
                try:
                    os.remove(frame_filename)
                except OSError:
                    print "error removing ", frame_filename
                    pass
            try:
                os.rmdir(filename[:-4])
            except OSError:
                print "error removing ", filename[:-4] + '/'
                pass

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
