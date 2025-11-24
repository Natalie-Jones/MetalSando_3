import ROOT
import numpy as np

#suppress any RuntimeWarnings
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

#_________________________________________________________________________________________________________________________________

def Model(x, A1, mu1, sigma1, A2, mu2, sigma2):  # μ = loc, σ = scale
    # the sum of two Moyal functions
    exp1 = A1*np.exp(-0.5*((x-mu1)/sigma1 + np.exp(-(x-mu1)/sigma1))) / (sigma1*np.sqrt(2*np.pi))
    exp2 = A2*np.exp(-0.5*((x-mu2)/sigma2 + np.exp(-(x-mu2)/sigma2))) / (sigma2*np.sqrt(2*np.pi))
    return exp1, exp2, exp1 + exp2

def BinnedMoyalFitSinglePeak(bin_centers,counts,bin_edges,loc_peak,plot_dir,pmt):

    # fill histogram for fitting
    x = ROOT.RooRealVar("x", "x", 0, min(bin_edges), 416)
    x.setBins(100)
    data_hist = ROOT.RooDataHist("data_hist", "data_hist", ROOT.RooArgList(x))

    for center, count in zip(bin_centers, counts):
        if center <= 416:
            x.setVal(center)
            data_hist.add(ROOT.RooArgSet(x), count)
    
    # define primary peak (Moyal) variables and PDF
    
    mu1 = ROOT.RooRealVar("mu1", "mu1", loc_peak, min(bin_edges), max(bin_edges))
    sigma1 = ROOT.RooRealVar("sigma1", "sigma1", np.std(bin_centers), 0, np.std(bin_centers)*2) 
    A1 = ROOT.RooRealVar("A1", "A1", max(counts)/2., 0, 100*max(counts))
    moyal_expr1 = "exp(-0.5*((x-mu1)/sigma1 + exp(-(x-mu1)/sigma1))) / (sigma1*sqrt(2*pi))"
    moyal = ROOT.RooGenericPdf("moyal", "Moyal PDF for primary peak", moyal_expr1, ROOT.RooArgList(x, mu1, sigma1))
    moyal1 = ROOT.RooAddPdf("moyal1", "moyal1", ROOT.RooArgList(moyal), ROOT.RooArgList(A1))

    # fit
    r = moyal1.fitTo(data_hist, ROOT.RooFit.Verbose(ROOT.kFALSE), Save = True) 
    r.Print('v')
    hcorr = r.correlationHist()


    # Calculate the NLL and PLL
    '''
    nll = moyal1.createNLL(data_hist)
    pll = nll.createProfile({mu1, sigma1, A1})
    '''

    #plot
    c = ROOT.TCanvas("c", "c", 800, 600)
    frame = x.frame()
    data_hist.plotOn(frame)
    moyal1.plotOn(frame)

    # get the minimum values
    mu1_min = mu1.getVal()
    sigma1_min = sigma1.getVal()
    A1 = A1.getVal()

    #legend = ROOT.TLegend(0.4, 0.7, 0.9, 0.9)  
    #legend.SetTextSize(0.04) 
    #legend.AddEntry(frame.findObject("model"), "Model (Sum of Moyals)", "l")
    #legend.AddEntry(frame.findObject("Primary Peak"), "Primary Peak (Moyal)", "l")
    #legend.AddEntry(frame.findObject("Secondary Peak"), "Secondary Peak (Moyal)", "l")
    #frame.addObject(legend)

    frame.Draw()
    c.Draw()
    c.Modified()
    c.Update()


    c_corr = ROOT.TCanvas("c_corr", "c_corr", 800, 600)
    hcorr.Draw("colz")
    c_corr.Draw()
    c_corr.Modified()
    c_corr.Update()

    save_path = plot_dir / f"moyal_model_fit_{pmt}.png"
    c.SaveAs(str(save_path))

    save_path = plot_dir / f"fit_correlation_{pmt}.png"
    c_corr.SaveAs(str(save_path))

    try:
        input("Press Enter")
    except SyntaxError:
        pass



    return A1, mu1_min, sigma1_min


def BinnedMoyalFitDoublePeak(bin_centers,counts,bin_edges):

    # fill histogram for fitting
    x = ROOT.RooRealVar("x", "x", min(bin_edges), max(bin_edges))
    x.setBins(len(bin_centers))
    data_hist = ROOT.RooDataHist("data_hist", "data_hist", ROOT.RooArgList(x))
    for center, count in zip(bin_centers, counts):
        x.setVal(center)
        data_hist.add(ROOT.RooArgSet(x), count)

    # define primary peak (Moyal) variables and PDF
    mu1 = ROOT.RooRealVar("mu1", "mu1", 50, min(bin_edges), max(bin_edges)) #bin_centers[np.argmax(counts)]
    sigma1 = ROOT.RooRealVar("sigma1", "sigma1", np.std(bin_centers), 0, 100) 
    A1 = ROOT.RooRealVar("A1", "A1", max(counts)/2, 0, max(counts))
    moyal_expr1 = "A1*exp(-0.5*((x-mu1)/sigma1 + exp(-(x-mu1)/sigma1))) / (sigma1*sqrt(2*pi))"
    moyal1 = ROOT.RooGenericPdf("moyal1", "Moyal PDF for primary peak", moyal_expr1, ROOT.RooArgList(x, mu1, sigma1, A1))

    # define secondary peak (Moyal) variables and PDF
    mu2 = ROOT.RooRealVar("mu2", "mu2", 1000, min(bin_edges)+10, max(bin_edges))  # bin_centers[np.argmax(counts)]+20
    sigma2 = ROOT.RooRealVar("sigma2", "sigma2", np.std(bin_centers), 0, 100)
    A2 = ROOT.RooRealVar("A2", "A2", max(counts)/10/2, 0, max(counts)/10)
    moyal_expr2 = "A2*exp(-0.5*((x-mu2)/sigma2 + exp(-(x-mu2)/sigma2))) / (sigma2*sqrt(2*pi))"
    moyal2 = ROOT.RooGenericPdf("moyal2", "Moyal PDF for secondary peak", moyal_expr2, ROOT.RooArgList(x, mu2, sigma2, A2))
    
    # combine the two PDFs with a coefficient to fit both peaks
    moyal1_ext = ROOT.RooExtendPdf("moyal1_ext", "moyal1_ext", moyal1, A1) # weight by amplitude
    moyal2_ext = ROOT.RooExtendPdf("moyal2_ext", "moyal2_ext", moyal2, A2) # weight by amplitude
    model = ROOT.RooAddPdf("model", "Primary + Secondary Peak Model", ROOT.RooArgList(moyal1_ext, moyal2_ext))

    # fit
    model.fitTo(data_hist, ROOT.RooFit.Verbose(ROOT.kFALSE)) 

    # Calculate the NLL and PLL
    nll = model.createNLL(data_hist)
    pll = nll.createProfile({mu1, sigma1, A1, mu2, sigma2, A2})

    # get the minimum values
    mu1_min = mu1.getVal()
    sigma1_min = sigma1.getVal()
    A1 = A1.getVal()
    mu2_min = mu2.getVal()
    sigma2_min = sigma2.getVal()
    A2 = A2.getVal()

    # plot
    '''
    c = ROOT.TCanvas("c", "c", 800, 600)
    frame = x.frame()
    data_hist.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kGray))
    model.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlack))
    model.plotOn(frame, ROOT.RooFit.Components("moyal1_ext"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.Name("Primary Peak"))
    model.plotOn(frame, ROOT.RooFit.Components("moyal2_ext"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlue), ROOT.RooFit.Name("Secondary Peak"))
    
    legend = ROOT.TLegend(0.4, 0.7, 0.9, 0.9)  
    legend.SetTextSize(0.04) 
    legend.AddEntry(frame.findObject("model"), "Model (Sum of Moyals)", "l")
    legend.AddEntry(frame.findObject("Primary Peak"), "Primary Peak (Moyal)", "l")
    legend.AddEntry(frame.findObject("Secondary Peak"), "Secondary Peak (Moyal)", "l")
    frame.addObject(legend)

    frame.Draw()
    c.Draw()
    c.SaveAs(f"/home/nrj7/MetalSando/hodoscope/plots/1hour_runs/moyal_model_fit_{position}.png")
    '''

    return A1, mu1_min, sigma1_min, A2, mu2_min, sigma2_min
