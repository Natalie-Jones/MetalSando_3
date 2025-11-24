import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import time
import re

from MoyalFit import Model

#_________________________________________________________________________________________________________________________________


def PlotSpectraPerCH(counts1,bin_edges1,counts2,bin_edges2,mu,sigma,ch_names):
    x = np.linspace(0,1000,5000)
    fig, ax = plt.subplots(int(len(counts1)/2), 2, figsize=(20,20), sharex=True)
    ax = ax.flatten()

    max_val = np.max([np.max(arr) for arr in counts1]) 

    for i in range(len(counts1)):
        ax[i].stairs(counts1[i],bin_edges1[i],alpha=0.5,label='set 1', fill=True)

        if len(counts2) != 0 and len(bin_edges2) != 0:
            ax[i].stairs(counts2[i],bin_edges1[i],alpha=0.5,label='set 2', fill=True)

        if mu != 0 and sigma != 0:
            y = Model(x, 1, mu[i], sigma[i], 0,0,0)[0]
            ax[i].plot(x,y,color='k',label='fit')

        ax[i].set_xlim(0,400)
        ax[i].set_ylim(0,max_val)
        ax[i].legend(loc='upper right',fontsize=20)
        ax[i].set_title(ch_names[i],fontsize=20)

    plt.tight_layout()
    #plt.show()
    plt.close()

    return fig

def PlotTotalSpectra(counts1,bin_edges1,counts2,bin_edges2,mu,sigma):
    fig = plt.figure(figsize=(11,6))
    
    for i in range(len(counts1)):
        print(counts1[i][:100])
    counts1_arr = np.array(counts1)
    total1 = counts1_arr.sum(axis=0) 
    print(total1[:100])
    plt.stairs(total1, bin_edges1[0], color='red', fill=False, label='Sum 1')
    
    if len(counts2) != 0 and len(bin_edges2) != 0:
        counts2_arr = np.array(counts2) 
        total2 = counts2_arr.sum(axis=0)
        plt.stairs(total2, bin_edges2[0], color='red', fill=False, label='Sum 2')

    if mu != 0 and sigma != 0:
        print('Oops, not ready to include fits to total spectra. Please try again later!')

    plt.xlim(0,2000)
    plt.ylim(0,np.max(total1)+50)
    plt.title('Total Energy Spectrum \n 12 hours of midle hodoscope data',fontsize=15)
    plt.xlabel('Energy (ADC)',fontsize=15)
    plt.ylabel('Counts/10 ADC',fontsize=15)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=15)

    plt.tight_layout()
    #plt.show()
    plt.close()

    return fig


#_________________________________________________________________________________________________________________________________


def main():
    histo_dir = input("In what directory are your first set of histograms located? ")
    plots_dir = Path(input("Where would you like to save your plots to? "))
    ch_names = ['lower left bottom',
                'lower right bottom',
                'lower left top',
                'lower right top',
                'upper left bottom',
                'upper right bottom',
                'upper left top',
                'upper right top',
                ]

    time.sleep(2)


    # initialize
    counts1 = []
    counts2 = []
    bin_edges1 = []
    bin_edges2 = []
    mu_values = 0
    sigma_values = 0

    # start with the first set of histograms
    if os.path.isdir(histo_dir):
        # load files
        files = [f for f in os.listdir(histo_dir) if os.path.isfile(os.path.join(histo_dir, f))]
        files = sorted(files, key=lambda f: int(re.search(r'CH(\d+)', f).group(1)))
        num_files = sum(os.path.isfile(os.path.join(histo_dir, f)) for f in os.listdir(histo_dir))
        print(f"There are {num_files} files in {histo_dir}")    
        print(f"\nFiles in this directory:")
        for f in files:
            print(f)

        for filename in files:
            file_path = os.path.join(histo_dir, filename)
            histo_data = np.load(file_path, allow_pickle=True).item()

            counts = [i for i in histo_data["counts"]] #.tolist()
            bin_edges = [i for i in histo_data["bin_edges"]] #.tolist()

            counts1.append(counts)
            bin_edges1.append(bin_edges)


        # ask about shifted histograms (if just plotting shifted above, say 'no')
        ask_for_shifted = str(input("Do you have shifted histograms? (yes or no). \n If your first set of histograms are shifted, say 'no'. "))
        if ask_for_shifted == 'yes':
            shifted_histo_dir = input("In what directory are your shifted histograms located? ")

            if os.path.isdir(shifted_histo_dir):
                # load files
                files = [f for f in os.listdir(shifted_histo_dir) if os.path.isfile(os.path.join(shifted_histo_dir, f))]
                files = sorted(files, key=lambda f: int(re.search(r'CH(\d+)', f).group(1)))
                num_files = sum(os.path.isfile(os.path.join(shifted_histo_dir, f)) for f in os.listdir(shifted_histo_dir))
                print(f"There are {num_files} files in {shifted_histo_dir}")    
                print(f"\nFiles in this directory:")
                for f in files:
                    print(f)
                
                for filename in files:
                    file_path = os.path.join(shifted_histo_dir, filename)
                    shifted_histo_data = np.load(file_path, allow_pickle=True).item()

                    counts = [i for i in shifted_histo_data["counts"]] #.tolist()
                    bin_edges = [i for i in shifted_histo_data["bin_edges"]] #.tolist()

                    counts2.append(counts)
                    bin_edges2.append(bin_edges)
            else:
                print("That directory does not exist.")


        # ask if want to include Moyal fits on top of histograms
        ask_for_fit = str(input("Do you have fits to include? (yes or no) "))
        if ask_for_fit == 'yes':
            fit_dir = input("What directory is your fit information in? ")

            if os.path.isdir(fit_dir):
                # load files
                files = [f for f in os.listdir(fit_dir) if os.path.isfile(os.path.join(fit_dir, f))]
                files = sorted(files, key=lambda f: int(re.search(r'CH(\d+)', f).group(1)))
                num_files = sum(os.path.isfile(os.path.join(fit_dir, f)) for f in os.listdir(fit_dir))
                print(f"There are {num_files} files in {fit_dir}")    
                print(f"\nFiles in this directory:")
                for f in files:
                    print(f)
                
                for filename in files:
                    file_path = os.path.join(fit_dir, filename)
                    fit_data = np.load(file_path, allow_pickle=True).item()
                    mu_values = [i for i in fit_data["Mu"]] #.tolist()
                    sigma_values = [i for i in fit_data["Sigma"]] #.tolist()
            else:
                print("That directory does not exist.")


    else:
        print("That directory does not exist.")

    Subplots = PlotSpectraPerCH(counts1,bin_edges1,counts2,bin_edges2,mu_values,sigma_values,ch_names)
    Sumplots = PlotTotalSpectra(counts1,bin_edges1,counts2,bin_edges2,mu_values,sigma_values)

    save_path_for_subplots = plots_dir/ f"subplots.png"
    save_path_for_sumplots = plots_dir / f"total.png"

    Subplots.savefig(save_path_for_subplots)
    Sumplots.savefig(save_path_for_sumplots)  

    print(f'Plot saved as {save_path_for_subplots}')    
    print(f'Plot saved as {save_path_for_sumplots}')


if __name__ == '__main__':

    main()


