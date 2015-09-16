import ROOT
import os
import math


def animate_higgs_peak(m_boson, width_boson, m_A, higgs_boson, filename="animation.gif", duration=5000, skipframes=1):
    # remove gif file (if present)
    try:
        os.remove(filename)
    except OSError:
        pass

    # x axis range (enlarged by 5 (?))
    x_min = int(min(m_boson)) - 5
    x_max = int(max(m_boson)) + 5

    # debug output
    print "x_min =", x_min, "x_max =", x_max

    # calculate delay time per frame
    # one interval/frame per data set
    animation_delay = math.ceil(duration * skipframes / len(m_boson))

    width = ROOT.RooRealVar("width", "width", 0)
    mean = ROOT.RooRealVar("mean", "mean", 0)

    rf = ROOT.RooFit

    x = ROOT.RooRealVar("x", "m_" + higgs_boson, x_min, x_max)
    x_frame = x.frame(rf.Bins(1))

    title = higgs_boson + " Higgs Boson peak"
    x_frame.SetTitle(title)

    canvas = ROOT.TCanvas("canvas", "canvas", 1000, 600)

    gaus = ROOT.RooBreitWigner("breitwigner", "BreitWigner", x, mean, width)

    print " len=", len(m_boson), " len=", len(width_boson)
    for i in xrange(0, len(m_boson), skipframes):
        print i
        # create/clone new empty frame
        frame = x_frame.emptyClone(x_frame.GetName() + "_" + str(i))

        frame.SetTitle(title + " (m_A=" + str(m_A[i]) + ")")

        mean.setVal(m_boson[i])
        width.setVal(width_boson[i])

        # debug output
        if i%10 == 0: print "creating image", i
        print "mean=", mean.getVal(), "  x=", x.getVal(), "  width=", width.getVal()

        # plot normalized gauss function on frame
        norm = gaus.createIntegral(ROOT.RooArgSet(x), rf.NormSet(ROOT.RooArgSet(x))).getVal() / (x_max - x_min)
        gaus.plotOn(frame, rf.Normalization(norm, ROOT.RooAbsReal.NumEvent))

        # remove y axis title, set y axis maximum to 1
        frame.SetYTitle("")
        frame.SetMaximum(1)

        # draw frame
        frame.Draw()

        # animation delay in centiseconds (10ms)
        canvas.Print(filename + "+" + str(int(math.ceil(animation_delay / 10 ))))

    # infinite loop gif
    canvas.Print(filename + "++100++")


if __name__ == '__main__':
    animate_higgs_peak([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [2, 2, 3, 2, 2, 3, 3, 2, 3, 2], 0, 9)
