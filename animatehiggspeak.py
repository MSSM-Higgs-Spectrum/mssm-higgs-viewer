# coding=utf-8
import ROOT
import os
import math
import gc
import time


def calc_x_min(x_list):
    return int(min(min(l) for l in x_list)) - 5


def calc_x_max(x_list):
    return int(max(max(l) for l in x_list)) + 5


def perf_time_measure(start_time, comment=''):
    end_time = time.time()
    print 'Δt =', round(end_time - start_time, 6), comment
    return end_time


def animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_boson, sigma_gaussian=None,
                       filename="animation.gif", duration=5000, skipframes=1):

    global perf
    perf = time.time()

    # disable gc
    gc.disable()

    # performance time measurement
    perf = perf_time_measure(perf)

    # remove gif file (if present)
    try:
        os.remove(filename)
    except OSError:
        pass

    num_bosons = len(list_values_mass)

    # calculate delay time per frame
    # one interval/frame per dataset
    animation_delay = math.ceil(duration * skipframes / len(list_values_mass[0]))

    rf = ROOT.RooFit

    # performance time measurement
    perf = perf_time_measure(perf, 'some calcs')

    # suppress INFO:NumericIntegration log
    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

    # x axis range (enlarged by 5 (?))
    x_min = calc_x_min(list_values_mass)
    x_max = calc_x_max(list_values_mass)
    x = ROOT.RooRealVar("x", "m / GeV", x_min, x_max)

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

    # performance time measurement
    perf = perf_time_measure(perf, 'before RooRealVar loop')

    for n in range(num_bosons):
        width.append(ROOT.RooRealVar("width", "width", 0))
        mean.append(ROOT.RooRealVar("mean", "mean", 0))
        sigma.append(ROOT.RooRealVar("sigma", "sigma", 0))
        pdf.append(ROOT.RooVoigtian("voigtian", "Voigtian", x, mean[n], width[n], sigma[n]))

    norm = []

    # performance time measurement
    perf = perf_time_measure(perf, 'before main loop')

    for i in xrange(0, len(list_values_mass[0]), skipframes):
        # performance time measurement
        perf = perf_time_measure(perf, 'loop begin')

        # run garbage collector
        print "gc: ", gc.collect()

        # performance time measurement
        perf = perf_time_measure(perf, 'loop gc')

        # create/clone new empty frame
        lframe = frame.emptyClone(frame.GetName() + "_" + str(i))

        lframe.SetTitle(title + " (m_A=" + str(values_ma[i]) + ")")

        # empty list
        norm[:] = []

        for n in range(num_bosons):
            mean[n].setVal(list_values_mass[n][i])
            width[n].setVal(list_values_width[n][i])
            if sigma_gaussian is None:
                # default sigma is 20% of mean value
                sigma[n].setVal(list_values_mass[n][i] * 0.2)
            elif (sigma_gaussian is not None) and (sigma_gaussian.find('%') >= 0):
                # sigma can be specified in percent of mean value
                sigma[n].setVal(list_values_mass[n][i] * float(sigma_gaussian[:-1]) / 100.0)
            # plot normalized gauss function on frame
            # norm.append(100.0 / pdf[n].createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal())
            norm.append(100.0 / pdf[n].createIntegral(ROOT.RooArgSet(x)).getVal())
            # norm[n] = 100
            plot_cmd_list = ROOT.RooLinkedList(3)
            plot_cmd_list.Add(rf.Normalization(norm[n]))
            plot_cmd_list.Add(rf.LineColor(n + 2))
            plot_cmd_list.Add(rf.FillColor(n + 2))
            pdf[n].plotOn(lframe, plot_cmd_list)
            if num_bosons > 1:
                if n == 0:
                    # Add legend
                    legend = ROOT.TLegend(0.70, 0.75, 0.9, 0.9)
                legend_entry = legend.AddEntry(list_higgs_boson[n], list_higgs_boson[n]
                                               + " (m = " + str(round(list_values_mass[n][i], 1))
                                               + "; w = " + str(round(list_values_width[n][i], 4)) + ")", "l")
                legend_entry.SetLineColor(n + 2)

        # performance time measurement
        perf = perf_time_measure(perf, 'loop bosons plotted')

        # remove y axis title
        lframe.SetYTitle("%")

        # set y axis maximum to 1
        lframe.SetMaximum(100)

        # draw frame
        lframe.Draw()

        if num_bosons > 1:
            # draw legend
            legend.Draw()

        # performance time measurement
        perf = perf_time_measure(perf, 'loop frame drawed')

        # animation delay in centiseconds (10ms)
        canvas.Print(filename + "+" + str(int(math.ceil(animation_delay / 10))))

        # performance time measurement
        perf = perf_time_measure(perf, 'loop canvas printed')

        # delete cloned frame
        lframe.Delete()

    # infinite loop gif
    canvas.Print(filename + "++100++")

    # run garbage collector
    print "gc: ", gc.collect()


if __name__ == '__main__':
    animate_higgs_peak([[10, 20, 40], [7, 15, 24], [9, 17, 26]], [[0.0002, 0.0001, 0.00008], [0.0001, 0.0002, 0.00015],
                        [0.0002, 0.0003, 0.00025]], [60, 70, 80], ['H', 'h', 'A'], '10%', filename='test.gif',
                        duration=1000)
