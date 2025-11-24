import uproot
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import time
import re

#suppress any RuntimeWarnings
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

#_________________________________________________________________________________________________________________________________

# Order of functions to call:
 # GetBranchContent: returns the timestamps and samples from root files
 # BaselineSubtract: puts the baseline of samples at zero
 # PlotWaveforms: this is mostly a healthcheck to make sure the digitized signals are good


def GetBranchContent(file_name):
    with uproot.open(file_name) as file:
        tree_name = file.keys()[0]
        tree = file[tree_name]
        branch_name = tree.keys()
        branch_array = [tree[branch_name].array() for branch_name in tree.keys()]
        
        timestamps = tree['Timestamp'].array()
        print('Got timestamps.')
        samples = branch_array[branch_name.index('Samples')]
        print('Got samples.')

    return timestamps, samples


def BaselineSubtract(samples):
    onset = 175
    #samples = [np.array(samples) for sample in samples]
    #print(samples[0],samples[1])
    #print(len(samples))
    #print([len(samples[i]) for i in range(10)])
    
    pretrases = [samples[i][:onset] for i in range(len(samples))] #get all values up to onset
    baselines = [np.mean(pretrases[i]) for i in range(len(pretrases))]
    samples = [np.array(samples[i]) - baselines[i] for i in range(len(samples))] #subtract baseline from each sample
    samples = np.stack(samples) #convert to numpy array
    # find any samples that now contain nan
    nans = [i for i, waveform in enumerate(samples) if np.isnan(waveform).any()]
    if nans:
        print(f'Warning: {len(nans)} samples contain NaN values after baseline subtraction.')
        for i in nans:
            print(f'Waveform index {i} contains NaN values after baseline subtraction.')
    
    return samples


def PlotWaveforms(file_path, save_dir, x_values, samples, pmt):

    file_path = Path(file_path)  # convert string to Path
    save_path = save_dir / f"{file_path.stem}.png"
    
    plt.figure(figsize=(15, 10))
    for i, waveform in enumerate(samples):
        plt.plot(x_values, waveform)
    plt.xlabel('Samples',fontsize=20)
    plt.ylabel('ADC',fontsize=20)
    plt.title(f'Samples on {pmt} PMT',fontsize=20)
    plt.savefig(save_path)
    print('Plot saved as:', save_path)

#_________________________________________________________________________________________________________________________________



def main():
    data_dir = input("What directory would you like to use? ")
    ch_names = ['lower left bottom',
                'lower right bottom',
                'lower left top',
                'lower right top',
                'upper left bottom',
                'upper right bottom',
                'upper left top',
                'upper right top',
                ]
    plots_dir = Path(input("What directory would you like to save plots to? ")).resolve()
    plots_dir.mkdir(parents=True, exist_ok=True)

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

        # plots waveforms
        print('\nStarting plotting...')
        for i,filename in enumerate(files):
            file_path = os.path.join(data_dir, filename)
            samples = GetBranchContent(file_path)[1]
            samples = BaselineSubtract(samples)
            x = np.arange(0,len(samples[0]),1) #will be the same for all samples across all channels
            PlotWaveforms(file_path,plots_dir, x, samples, ch_names[i])

    else:
        print("That directory does not exist.")


if __name__ == '__main__':

    main()