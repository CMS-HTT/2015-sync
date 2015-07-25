import ROOT
import math
import copy

def applyHistStyle(h, i):
    h.SetLineColor(colours[i])
    h.SetLineStyle(styles[i])
    h.SetLineWidth(3)
    h.SetStats(False)

def LegendSettings(leg):
    leg.SetBorderSize(0)
    leg.SetFillColor(10)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
#    leg.SetTextSize(0.035)
#    leg.SetTextFont(42)


def createRatioCanvas(name, errorBandFillColor=14, errorBandStyle=3354):
    cv = ROOT.TCanvas(name.replace('.pdf',''), name.replace('.pdf',''), 10, 10, 700, 600)

    #this is the tricky part...
    # Divide with correct margins
    cv.Divide(1, 2, 0.0, 0.0)

    # Set Pad sizes
    cv.GetPad(1).SetPad(0.0, 0.32, 1., 1.0)
    cv.GetPad(2).SetPad(0.0, 0.00, 1., 0.34)
        
    cv.GetPad(1).SetFillStyle(4000)
    cv.GetPad(2).SetFillStyle(4000)


    # Set pad margins 1
    cv.cd(1)
    ROOT.gPad.SetTopMargin(0.08)
    ROOT.gPad.SetLeftMargin(0.12)
    ROOT.gPad.SetBottomMargin(0.03)
    ROOT.gPad.SetRightMargin(0.1)

    # Set pad margins 2
    cv.cd(2)
    ROOT.gPad.SetBottomMargin(0.35)
    ROOT.gPad.SetLeftMargin(0.12)
    ROOT.gPad.SetRightMargin(0.1)
        
    bogyHist = ROOT.TH1F("legendPseudoHist", "", 1, 1., 2.)
    bogyHist.SetFillColor(errorBandFillColor)
    bogyHist.SetFillStyle(errorBandStyle)
    bogyHist.SetLineColor(0)

    cv.cd(1)
    return cv
   


class DisplayManager(object):
    def __init__(self, name, ratio):
        
        if ratio:
            self.canvas = createRatioCanvas(name.replace('pdf',''))
        else:
            self.canvas = ROOT.TCanvas(name.replace('.pdf',''))

        self.name = name
        self.ratio = ratio
        self.histos=[]
        self.Legend = ROOT.TLegend(0.15,0.79,0.5,0.89)
        LegendSettings(self.Legend)

        self.RatioLegend = ROOT.TLegend(0.15,0.79,0.5,0.89)
        LegendSettings(self.RatioLegend)

        self.pullRange = 0.8
        self.canvas.Print(self.name + '[')

    def __del__(self):
        self.canvas.Print(self.name + ']')

    def Draw(self, histos, titles):

        self.histos = histos
        ymax = max(h.GetMaximum() for h in self.histos)

        self.Legend.Clear()
        self.RatioLegend.Clear()

        for i, h in enumerate(self.histos):
            title = titles[i]
            h.GetYaxis().SetRangeUser(0., ymax * 1.3)
            self.Legend.AddEntry(h, title + ': ' + str(h.Integral()))

            if i == 0:
                h.Draw('HIST E')
            else:
                h.Draw('SAME HIST E')

        self.Legend.Draw()

        if self.ratio:
            self.canvas.cd(2)

            for ihist in range(1, len(self.histos)):
                histPull = copy.deepcopy(self.histos[ihist])
                histPull.Divide(self.histos[0])
                histPull.UseCurrentStyle()

                histPull.SetLineColor(self.histos[ihist].GetLineColor())
                histPull.SetMarkerColor(self.histos[ihist].GetLineColor())
                histPull.SetLineStyle(self.histos[ihist].GetLineStyle())
                histPull.SetLineWidth(self.histos[ihist].GetLineWidth())

    
                histPull.GetYaxis().SetRangeUser(-self.pullRange + 1., self.pullRange + 1.)
                
#                defaultYtoPixel = 472. # height in pixels of default canvas
                defaultYtoPixel = 300. # height in pixels of default canvas
                
                pad1YtoPixel = float(self.canvas.GetPad(1).YtoPixel(0))
                pad2YtoPixel = float(self.canvas.GetPad(2).YtoPixel(0))
        
                pad1XaxisFactor = defaultYtoPixel / pad1YtoPixel
                pad2XaxisFactor = defaultYtoPixel / pad2YtoPixel
                

                histPull.GetXaxis().SetLabelSize(self.histos[0].GetXaxis().GetLabelSize()*pad2XaxisFactor)
                histPull.GetXaxis().SetLabelOffset(self.histos[0].GetXaxis().GetLabelOffset()*pad2XaxisFactor)
                histPull.GetXaxis().SetTitleSize(self.histos[0].GetXaxis().GetTitleSize()*pad2XaxisFactor)
                histPull.GetXaxis().SetTitleOffset(self.histos[0].GetXaxis().GetTitleOffset()/pad2XaxisFactor*2.5)
        
                histPull.GetYaxis().SetLabelSize(self.histos[0].GetYaxis().GetLabelSize()*pad2XaxisFactor)
                histPull.GetYaxis().SetLabelOffset(self.histos[0].GetYaxis().GetLabelOffset()*pad2XaxisFactor)
                histPull.GetYaxis().SetTitleSize(self.histos[0].GetYaxis().GetTitleSize()*pad2XaxisFactor)
                histPull.GetYaxis().SetTitleOffset(self.histos[0].GetYaxis().GetTitleOffset()/pad2XaxisFactor)
    
                histPull.GetYaxis().CenterTitle()    
                histPull.GetXaxis().SetTickLength(histPull.GetXaxis().GetTickLength()*pad2XaxisFactor)
                histPull.GetYaxis().SetNdivisions(306)


                histPull.GetXaxis().SetTitle('')
                histPull.GetYaxis().SetTitle("Ratio to " + titles[0])
                histPull.SetTitle('')
                histPull.Draw("ep")


                self.RatioLegend.AddEntry(histPull, titles[ihist])


#            self.RatioLegend.Draw()

            # This is a little bit ugly though ...

            for i, h in enumerate(self.histos):
                h.GetXaxis().SetLabelSize(0)

            self.canvas.cd(1)



        self.canvas.Update()
        self.canvas.Print(self.name)

        
