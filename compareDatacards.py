import sys
import fnmatch

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from optparse import OptionParser

from varCfg import category_dict
from DisplayManager import DisplayManager

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

colours = [1, 2, 3, 6, 8]
styles = [2, 1, 3, 4, 5]

def getHist(f,cat,histn):
    histogram = f.Get('%(cat)s/%(histn)s'%vars())
    if isinstance(histogram, ROOT.TH1):
        return histogram
    print 'Failed to find a histogram %(cat)s/%(histn)s in file'%vars(), f
    return None

def applyHistStyle(h, i):
    h.SetLineColor(colours[i])
    h.SetLineStyle(styles[i])
    h.SetLineWidth(3)
    h.SetFillColor(0)
    h.SetMarkerSize(0)
    h.SetStats(False)


def comparisonPlots(files, titles, category, pname='sync.pdf', ratio=True):

    display = DisplayManager(pname, ratio)
    contributions= ['ZTT','ZLL','VV','W','QCD','TT','data_obs','ggH125','ZJ','ZL']
    
    for template in contributions:
    
        hists = []
        hist_exists = True
        for i, t in enumerate(files):
            if isinstance(getHist(t,category,template),ROOT.TH1):
                hist_exists=True
                h = getHist(t,category,template)
                h.SetTitle(template)
                h.GetXaxis().SetTitle("Visible mass [GeV]")
                applyHistStyle(h,i) 
                hists.append(h)
            else :
                hist_exists =False
                
        if hist_exists == True:
            display.Draw(hists,titles)


if __name__ == '__main__':
        
    usage = '''
%prog [options] arg1 arg2 ... argN

    Compares N input datacards - categories to make comparison plots for are specified in varCfg.py/category_dict

'''

    parser = OptionParser(usage=usage)

    parser.add_option('-t', '--titles', type='string', dest='titles', default='Imperial,KIT', help='Comma-separated list of titles for the N input files (e.g. Imperial,KIT)')
    parser.add_option('-r', '--no-ratio', dest='do_ratio', action='store_false', default=True, help='Do not show ratio plots')

    (options,args) = parser.parse_args()

    if len(args) < 2:
        print 'provide at least 2 input root files'
        sys.exit(1)

    titles = options.titles.split(',')
    
    if len(titles) < len(args):
        print 'Provide at least as many titles as input files'
        sys.exit(1)

    for i, arg in enumerate(args):
        if arg.endswith('.txt'):
            f_txt = open(arg)
            for line in f_txt.read().splitlines():
                line.strip()
                if line.startswith('/afs'):
                    args[i] = line
                    break

    tfiles = [ROOT.TFile(arg) for arg in args]
    categories = []
    if fnmatch.fnmatch(args[0],'*htt_mt.inputs*'):
        categories = category_dict['mt']
    if fnmatch.fnmatch(args[0],'*htt_et.inputs*'):
        categories = category_dict['et']
    if fnmatch.fnmatch(args[0], '*htt_em.inputs*'):
        categories = category_dict['em']
    if fnmatch.fnmatch(args[0], '*htt_tt.inputs*'):
        categories = category_dict['tt']
    

    for category in categories:
        comparisonPlots(tfiles, titles, category, '%(category)s-datacard-sync.pdf'%vars(), options.do_ratio)

   
