import numpy as np
from pathlib import Path
import time
import os
import re

#suppress any RuntimeWarnings
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

#_________________________________________________________________________________________________________________________________

### THIS SCRIPT IS NOT VERY GENERALIZED BECAUSE OF THE STUPID SPECIFIC INDEXING ###

indices_top_layer = [2, 3, 6, 7]
indices_bottom_layer = [0, 1, 4, 5]


def main():

    data_dir = input("What integral directory would you like to use? ")
    ratios_dir = input("What calibration ratios directory would you like to use? ")
    fit_params_dir = input("What fit parameters directory would you like to use? ")
    save_dir = input("What directory would you like to save shifted integrals? ")
    new_fit_params = input("What directory would you like to save shifted fit parameters? (sigma will remain unchanged)")

    time.sleep(2)
    

    if os.path.isdir(data_dir) and os.path.isdir(ratios_dir) and os.path.isdir(fit_params_dir):



        # load files
        files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
        files = sorted(files, key=lambda f: int(re.search(r'CH(\d+)', f).group(1)))
        num_files = sum(os.path.isfile(os.path.join(data_dir, f)) for f in os.listdir(data_dir))
        print(f"There are {num_files} files in {data_dir}")    
        print(f"\nFiles in this directory:") 
        for f in files:
            print(f)

        ratio_files = [f for f in os.listdir(ratios_dir) if os.path.isfile(os.path.join(ratios_dir, f))]
        num_ratio_files = sum(os.path.isfile(os.path.join(ratios_dir, f)) for f in os.listdir(ratios_dir))
        print(f"There are {num_ratio_files} files in {ratios_dir}")    
        print(f"\nFiles in this directory:")
        for f in ratio_files:
            print(f)

        fit_params_files = [f for f in os.listdir(fit_params_dir) if os.path.isfile(os.path.join(fit_params_dir, f))]
        num_fit_param_files = sum(os.path.isfile(os.path.join(fit_params_dir, f)) for f in os.listdir(fit_params_dir))
        print(f"There are {num_fit_param_files} files in {fit_params_dir}")    
        print(f"\nFiles in this directory:")
        for f in fit_params_files:
            print(f)



        # get integral information
        Integrals = []
        for filename in files:
            file_path = os.path.join(data_dir, filename)
            integrals = np.load(file_path,allow_pickle=True)
            Integrals.append(integrals)
        
        print([len(Integrals[i]) for i in range(len(Integrals))])
        
        # get calibration information
        calibration_ratios = [] # it's gonna be shaped like this [ [layer 1 ratios] [layer 2 ratios ] ...]
        for filename in ratio_files:
            file_path = os.path.join(ratios_dir, filename)
            ratios = np.load(file_path,allow_pickle=True)
            calibration_ratios.append(ratios)

        # get fit params
        Mu_values = []
        Sigma_values = []
        for filename in fit_params_files:
            file_path = os.path.join(fit_params_dir, filename)
            fit_data = np.load(file_path, allow_pickle=True).item()
            mu_values = [i for i in fit_data["Mu"]] #.tolist()
            sigma_values = [i for i in fit_data["Sigma"]] #.tolist()
            Mu_values.append(mu_values)
            Sigma_values.append(sigma_values)



        # shift top layer pmt integrals
        for i,value in enumerate(indices_top_layer): # i goes like 0,1,2,3. value goes like 2,3,6,7
            print(f'Using top layer ratio {i} on pmt {value}')
            len_integral = len(Integrals[i])
            Integrals[value] = [Integrals[value][j]*calibration_ratios[0][i] for j in range(len_integral)]

        # shift bottom layer pmt integrals
        for i,value in enumerate(indices_bottom_layer): # i goes like 0,1,2,3. value goes like 0,1,4,5
            print(f'Using bottom layer ratio {i} on pmt {value}')
            Integrals[value] = [Integrals[value][j]*calibration_ratios[1][i] for j in range(len_integral)]

        # shift top layer mu_opts
        for i,value in enumerate(indices_top_layer): # i goes like 0,1,2,3. value goes like 2,3,6,7
            print(f'Using top layer ratio {i} on pmt {value}')
            Mu_values[value] = Mu_values[value]*calibration_ratios[0][i]

        # shift bottom layer mu_opts
        for i,value in enumerate(indices_bottom_layer): # i goes like 0,1,2,3. value goes like 0,1,4,5
            print(f'Using bottom layer ratio {i} on pmt {value}')
            Mu_values[value] = Mu_values[value]*calibration_ratios[1][i]


        print([len(Integrals[i]) for i in range(len(Integrals))])
        

    
        #save shifted integrals
        save_path = save_dir / f"shifted_integrals.npy"
        np.save(save_path, Integrals,allow_pickle=True)
        print(f'Saved {save_path}')

        #save shifted fit params
        shifted_histo_data = {
        "Mu": Mu_values, #.astype(int)
        "Sigma": Sigma_values, #.astype(int)
        }

        save_path = fit_params_dir / "fit_params_shifted.npy"
        np.save(save_path, shifted_histo_data,allow_pickle=True)
        print(f'Saved {save_path}')




    else:
        print("One or more of your directories does not exist.")

        
if __name__ == '__main__':

    main()

