import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import time
import re


#_________________________________________________________________________________________________________________________________

def main():
    data_dir = Path(input("What integral directory would you like to use? ").strip())
    histograms_dir = data_dir / "histo_info" #Path(input("What directory would you like to save histogram data to? ")).resolve()
    histograms_dir.mkdir(parents=True, exist_ok=True)

    time.sleep(2)

    if os.path.isdir(data_dir):
        # load files
        files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
        files = sorted(files, key=lambda f: int(re.search(r'CH(\d+)', f).group(1)))
        num_files = sum(os.path.isfile(os.path.join(data_dir, f)) for f in os.listdir(data_dir))
        print(f"There are {num_files} files in {data_dir}")    
        print(f"\nFiles in this directory:")
        for f in files:
            print(f)

        # get integral information
        Integrals = []
        file_paths = []
        total = 0

        for filename in files:
            file_path = os.path.join(data_dir, filename)
            file_paths.append(file_path)
            integrals = np.load(file_path,allow_pickle=True)
            integrals = abs(integrals)
            Integrals.append(integrals)
            total += integrals
        
        total_save_path = data_dir / "integral sum located here/integral_sum.npy"
        np.save(total_save_path,total,allow_pickle=True)
        print(f'Saved integral sum to {total_save_path}')

        max_val = np.max([np.max(arr) for arr in Integrals])        
        for i in range(num_files):
            Bins = np.arange(0,max_val,4) #step size = 4 ADC
            counts, bin_edges = np.histogram(Integrals[i], bins=Bins)
            bin_centers = 0.5*(bin_edges[1:]+bin_edges[:-1])
            loc_peak = bin_centers[np.argmax(counts)]

            histo_data = {
            "counts": counts,
            "bin_edges": bin_edges,
            "bin_centers": bin_centers,
            "loc_peak": loc_peak
            }
            
            file_path = Path(file_paths[i])  # convert string to Path
            save_path = histograms_dir / f"{file_path.stem}_spectra.npy"
            np.save(save_path,histo_data,allow_pickle=True)
            print(f'Saved histo info to {save_path}')
        
        Bins = np.arange(0,np.max(total),10)
        counts, bin_edges = np.histogram(total, bins=Bins[0:])
        bin_centers = 0.5*(bin_edges[1:]+bin_edges[:-1])
        histo_data = {
            "counts": counts,
            "bin_edges": bin_edges,
            "bin_centers": bin_centers}
        save_path = histograms_dir / "binned integral sum located here/sum_integrals_binned.npy"
        np.save(save_path,histo_data,allow_pickle=True)
        print(f'Saved histo info to {save_path}')
            
        
        #save_path = data_dir / f"integrals.npy"
        #np.save(save_path,Integrals,allow_pickle=True)
        #print(f'Saved integrals to the numpy file {save_path}')
            
            
    else:
        print("That directory does not exist.")

        

if __name__ == '__main__':

    main()