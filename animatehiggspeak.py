import ROOT
import os
import math


def animate_higgs_peak(values_mass, values_width, values_ma, higgs_boson, filename="animation.gif", duration=5000,
                       skipframes=1):
    # remove gif file (if present)
    try:
        os.remove(filename)
    except OSError:
        pass

    # x axis range (enlarged by 5 (?))
    x_min = int(min(values_mass)) - 5
    x_max = int(max(values_mass)) + 5

    # debug output
    print "x_min =", x_min, "x_max =", x_max

    # calculate delay time per frame
    # one interval/frame per dataset
    animation_delay = math.ceil(duration * skipframes / len(values_mass))

    width = ROOT.RooRealVar("width", "width", 0)
    mean = ROOT.RooRealVar("mean", "mean", 0)

    rf = ROOT.RooFit

    x = ROOT.RooRealVar("x", "m_" + higgs_boson, x_min, x_max)
    x_frame = x.frame(rf.Bins(1))

    title = higgs_boson + " Higgs Boson peak"
    x_frame.SetTitle(title)

    canvas = ROOT.TCanvas("canvas", "canvas", 1000, 600)

    gaus = ROOT.RooBreitWigner("breitwigner", "BreitWigner", x, mean, width)

    print " len=", len(values_mass), " len=", len(values_width)
    for i in xrange(0, len(values_mass), skipframes):
        print i
        # create/clone new empty frame
        frame = x_frame.emptyClone(x_frame.GetName() + "_" + str(i))

        frame.SetTitle(title + " (m_A=" + str(values_ma[i]) + ")")

        mean.setVal(values_mass[i])
        width.setVal(values_width[i])

        # plot normalized gauss function on frame
        norm = gaus.createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal() / (x_max - x_min)
        gaus.plotOn(frame, rf.Normalization(norm, ROOT.RooAbsReal.NumEvent))

        # remove y axis title, set y axis maximum to 1
        frame.SetYTitle("")
        frame.SetMaximum(1)

        # draw frame
        frame.Draw()

        # animation delay in centiseconds (10ms)
        canvas.Print(filename + "+" + str(int(math.ceil(animation_delay / 10))))

    # infinite loop gif
    canvas.Print(filename + "++100++")
