import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import time
import re


#_________________________________________________________________________________________________________________________________

def ParameterizeMuOptsInX(mu_values, num_pmts, num_rows, x_coords):

    curve_fits = np.empty((num_rows,num_pmts)) # [row][pmt]
    one_sigma_errors = np.empty((num_rows,num_pmts)) # [row][pmt]

    for row in range(num_rows): #first enter the row index
        for pmt in range(num_pmts): # now enter the pmt index
            points = mu_values[row][pmt] 
            print('points to fit:',points)
            curve_fit, cov = np.polyfit(x_coords,points,2,cov=True) #degree-2
            one_sigma_error = np.sqrt(np.diag(cov))
            curve_fits[row].append(curve_fit)
            one_sigma_errors[row].append(one_sigma_error)
            print('fit curve')

    return curve_fits, one_sigma_errors


def ParameterizeMuOptsInY(x_fits,x_fits_err,num_pmts,y_coords):

    y_curves = np.empty((num_pmts,len(x_fits))) #[pmt][coeff]
    one_sigma_errors = np.empty((num_pmts,len(x_fits))) #[pmt][coeff]

    for pmt in range(num_pmts):
        for coeff_curve in range(len(y_coords)):
            y_fit, cov = np.polyfit(y_coords,x_fits[pmt][coeff_curve],1,cov=True)
            one_sigma_error = np.sqrt(np.diag(cov))
            y_curves[pmt].append(y_fit)
            one_sigma_errors[pmt].append(one_sigma_error)
            print('fit curve in x')

    y_fits_UR, y_fits_LR, y_fits_UL, y_fits_LL = y_curves[0], y_curves[1], y_curves[2], y_curves[3]
    y_fit_errs_UR, y_fit_errs_LR, y_fit_errs_UL, y_fit_errs_LL = one_sigma_errors[0], one_sigma_errors[1], one_sigma_errors[2], one_sigma_errors[3]

    return y_fits_UR, y_fits_LR, y_fits_UL, y_fits_LL, y_fit_errs_UR, y_fit_errs_LR, y_fit_errs_UL, y_fit_errs_LL


#_________________________________________________________________________________________________________________________________

def main():

    parent_dir = input("What is the parent directory where all of your fit parameters reside? ")
    # /home/nrj7/MetalSando/hodoscope/data/four_scint_layers_12_hours/
    # position_12/shifted_integrals/histo_info
    # <hodoscope position>/shifted_integrals/histo_info
    fit_params_dir = input("What fit parameters directory would you like to use? ")
    save_curve_fits = input("What directory would you like to save curve fits in x and y? ")

    num_pmts = input("Please type the number of pmts on the detector: ")
    num_rows,num_cols = input("Please type the number of rows and columns with a ',' inbetween: ")
    x_coords = input("Please type x coordinates as n array: ") #[6,12,18,24,30]
    y_coords = input("Please type y coordinates as an array: ")

    time.sleep(2)
    

    if os.path.isdir(fit_params_dir):
        
        #load data
        fit_params_files = [f for f in os.listdir(fit_params_dir) if os.path.isfile(os.path.join(fit_params_dir, f))]
        num_fit_param_files = sum(os.path.isfile(os.path.join(fit_params_dir, f)) for f in os.listdir(fit_params_dir))
        print(f"There are {num_fit_param_files} files in {fit_params_dir}")    
        print(f"\nFiles in this directory:")
        for f in fit_params_files:
            print(f)

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