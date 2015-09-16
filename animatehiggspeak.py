import ROOT
import os
import math


def animate_higgs_peak(m_boson, width_boson, mA_min, mA_max, filename="animation.gif", duration=5000):
    # remove gif file (if present)
    try:
        os.remove(filename)
    except OSError:
        pass

    x_min = mA_min
    x_max = mA_max

    # one interval/frame per data set
    x_width = x_max - x_min

    # calculate delay time per frame
    animation_delay = math.ceil(duration / x_width)

    width = ROOT.RooRealVar("width", "width", 0)
    mean = ROOT.RooRealVar("mean", "mean", 0)

    rf = ROOT.RooFit

    x = ROOT.RooRealVar("x", "x", x_min, x_max)
    x_frame = x.frame(rf.Bins(1))

    canvas = ROOT.TCanvas("canvas", "canvas", 600, 600)

    gaus = ROOT.RooBreitWigner("breitwigner", "BreitWigner", x, mean, width)

    for i in xrange(x_width + 1):
        # create/clone new empty frame
        frame = x_frame.emptyClone(x_frame.GetName() + "_" + str(i))

        mean.setVal(m_boson[i])
        width.setVal(width_boson[i])

        # debug output
        if i%10 == 0: print "creating image", i
        print "mean=", mean.getVal(), "  x=", x.getVal(), "  sigma=", width.getVal()

        # plot normalized gauss function on frame
        norm = gaus.createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal()/x_width
        gaus.plotOn(frame, rf.Normalization(norm, ROOT.RooAbsReal.NumEvent))

        frame.SetMaximum(1)
        frame.Draw()

        # animation delay in centiseconds (10ms)
        canvas.Print(filename + "+" + str(int(math.ceil(animation_delay / 10))))

    # infinite loop gif
    canvas.Print(filename + "++" + str(int(math.ceil(animation_delay / 10))) + "++")
    print filename + " created"


if __name__ == '__main__':
    animate_higgs_peak([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [2, 2, 3, 2, 2, 3, 3, 2, 3, 2], 0, 9)
