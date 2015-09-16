import ROOT
import os
import math


def calc_x_min(x_list):
    return int(min(min(l) for l in x_list)) - 5


def calc_x_max(x_list):
    return int(max(max(l) for l in x_list)) + 5


def animate_higgs_peak(list_values_mass, list_values_width, values_ma, list_higgs_boson, filename="animation.gif",
                       duration=5000, skipframes=1):
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

    # x axis range (enlarged by 5 (?))
    x_min = calc_x_min(list_values_mass)
    x_max = calc_x_max(list_values_mass)
    x = ROOT.RooRealVar("x", "m", x_min, x_max)

    frame = x.frame(rf.Bins(1))

    if num_bosons > 1:
        title = "Higgs bosons peaks"
    else:
        title = list_higgs_boson + " Higgs Boson peak"
    frame.SetTitle(title)

    canvas = ROOT.TCanvas("canvas", "canvas", 1300, 750)

    width = ROOT.RooRealVar("width", "width", 0)
    mean = ROOT.RooRealVar("mean", "mean", 0)
    gaus = ROOT.RooBreitWigner("breitwigner", "BreitWigner", x, mean, width)

    if num_bosons > 1:
        width2 = ROOT.RooRealVar("width", "width", 0)
        mean2 = ROOT.RooRealVar("mean", "mean", 0)
        gaus2 = ROOT.RooBreitWigner("breitwigner", "BreitWigner", x, mean2, width2)

    if num_bosons > 2:
        width3 = ROOT.RooRealVar("width", "width", 0)
        mean3 = ROOT.RooRealVar("mean", "mean", 0)
        gaus3 = ROOT.RooBreitWigner("breitwigner", "BreitWigner", x, mean3, width3)

    for i in xrange(0, len(list_values_mass[0]), skipframes):
        print i
        # create/clone new empty frame
        lframe = frame.emptyClone(frame.GetName() + "_" + str(i))

        lframe.SetTitle(title + " (m_A=" + str(values_ma[i]) + ")")

        mean.setVal(list_values_mass[0][i])
        width.setVal(list_values_width[0][i])

        # plot normalized gauss function on frame
        norm = gaus.createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal() / (x_max - x_min)
        plot_cmd_list = ROOT.RooLinkedList(2)
        plot_cmd_list.Add(rf.Normalization(norm, ROOT.RooAbsReal.NumEvent))
        plot_cmd_list.Add(rf.LineColor(ROOT.kRed))
        gaus.plotOn(lframe, plot_cmd_list)

        if num_bosons > 1:
            mean2.setVal(list_values_mass[1][i])
            width2.setVal(list_values_width[1][i])
            # plot normalized gauss function on frame
            norm2 = gaus2.createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal() / (x_max - x_min)
            plot_cmd_list = ROOT.RooLinkedList(2)
            plot_cmd_list.Add(rf.Normalization(norm2, ROOT.RooAbsReal.NumEvent))
            plot_cmd_list.Add(rf.LineColor(ROOT.kGreen))
            gaus2.plotOn(lframe, plot_cmd_list)

        if num_bosons > 2:
            mean3.setVal(list_values_mass[2][i])
            width3.setVal(list_values_width[2][i])
            # plot normalized gauss function on frame
            norm3 = gaus3.createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal() / (x_max - x_min)
            plot_cmd_list = ROOT.RooLinkedList(2)
            plot_cmd_list.Add(rf.Normalization(norm3, ROOT.RooAbsReal.NumEvent))
            plot_cmd_list.Add(rf.LineColor(ROOT.kBlue))
            gaus3.plotOn(lframe, plot_cmd_list)

        # remove y axis title
        lframe.SetYTitle("")

        # set y axis maximum to 1
        lframe.SetMaximum(1)

        # draw frame
        lframe.Draw()

        # animation delay in centiseconds (10ms)
        canvas.Print(filename + "+" + str(int(math.ceil(animation_delay / 10))))

    # infinite loop gif
    canvas.Print(filename + "++100++")


if __name__ == '__main__':
    animate_higgs_peak([[10, 20, 40], [7, 15, 24], [9, 17, 26]], [[0.0002, 0.0001, 0.00008], [0.0001, 0.0002, 0.00015],
                        [0.0002, 0.0003, 0.00025]], [60, 70, 80], ['H', 'h', 'A'], filename='test.gif', duration=1000)
