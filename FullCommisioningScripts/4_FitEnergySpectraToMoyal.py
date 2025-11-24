import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import time
import os
import re

#suppress any RuntimeWarnings
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from MoyalFit import BinnedMoyalFitSinglePeak, BinnedMoyalFitDoublePeak

#_________________________________________________________________________________________________________________________________


def main():
    histo_dir = Path(input("What set of histograms would you like to fit? ").strip())
    parent_dir = histo_dir.parent
    parent2_dir = histo_dir.parent.parent
    ratios_dir = Path(parent2_dir / "calibration_ratios")
    plots_dir = Path(input("RooFit will generate plots. Where would you like to save them? "))
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



    if os.path.isdir(histo_dir):
        # load files
        files = [f for f in os.listdir(histo_dir) if os.path.isfile(os.path.join(histo_dir, f))]
        files = sorted(files, key=lambda f: int(re.search(r'CH(\d+)', f).group(1)))
        num_files = sum(os.path.isfile(os.path.join(histo_dir, f)) for f in os.listdir(histo_dir))
        print(f"There are {num_files} files in {histo_dir}")    
        print(f"\nFiles in this directory:")
        for f in files:
            print(f)


        Amplitudes = []
        Mu_opts = []
        One_sigmas = []

        for i,filename in enumerate(files):
            file_path = os.path.join(histo_dir, filename)
            histo_data = np.load(file_path, allow_pickle=True).item()
            counts = [i for i in histo_data["counts"]] #.tolist()
            bin_edges = [i for i in histo_data["bin_edges"]] #.tolist()
            bin_centers = [i for i in histo_data["bin_centers"]] #.tolist()
            loc_peak = histo_data["loc_peak"] #.tolist()

            n_peaks = int(input("How many peaks do you want to fit? (1 or 2): "))
            if n_peaks == 1:
                A1, mu_min, one_sigma_min = BinnedMoyalFitSinglePeak(bin_centers,counts,bin_edges,loc_peak,plots_dir,ch_names[i])
                Amplitudes.append(A1)
                Mu_opts.append(mu_min)
                One_sigmas.append(one_sigma_min)

            else:
                print('Oops, not yet ready to fit for double peaks!')

        histo_data = {
        "Mu": Mu_opts, #.astype(int)
        "Sigma": One_sigmas, #.astype(int)
        }

        save_path = histo_dir / "fit_params.npy"
        np.save(save_path, histo_data,allow_pickle=True)
        print(f'Saved {save_path}')


        center_position = str(input("Would you like to create calibration ratios with this fit data? (yes or no) "))

        if center_position == 'yes':
            save_path1 = ratios_dir / "ratio_top_layer.npy"
            save_path2 = ratios_dir / "ratio_bottom_layer.npy"

            ratios_top_layer = [Mu_opts[2]/Mu_opts[i] for i in [2,3,6,7]] # top indices: 2,3,67
            ratios_bottom_layer = [Mu_opts[0]/Mu_opts[i] for i in [0,1,4,5]] # bottom indices: 0,1,4,5
            
            np.save(save_path1, [ratios_top_layer])
            np.save(save_path2, [ratios_bottom_layer])


    else:
        print("That directory does not exist.")

        

if __name__ == '__main__':

    main()