import numpy as np
import os
from pathlib import Path
import time
import re

#suppress any RuntimeWarnings
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


from LookAtWaveforms_usethisone import GetBranchContent, BaselineSubtract

#_________________________________________________________________________________________________________________________________


def IntegrateSamples(file_path, save_dir, samples, threshold):

    file_path = Path(file_path)  # convert string to Path
    save_path = save_dir / f"{file_path.stem}_integrals.npy"
    
    onsets = 175 # look at waveforms to know this. it's usually this number. 
    integrated_samples = []
    for i in range(len(samples)):
        samples[i] = np.array(samples[i])
        maximum = np.max(abs(samples[i]))
        if maximum > threshold:
            integrated_sample = np.sum(samples[i][onsets-10:onsets+50]) # look at spread of waveforms to know what range to use 
            integrated_samples.append(integrated_sample)

    np.save(save_path,integrated_samples)
    print(f'Saved integrals to {save_path}')

#_________________________________________________________________________________________________________________________________



def main():
    data_dir = input("What directory would you like to use? ")
    integrals_dir = Path(input("What directory would you like to save the integrals to? ")).resolve()
    integrals_dir.mkdir(parents=True, exist_ok=True)

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

        # integrate waveforms
        print('\nIntegrating...')
        for i,filename in enumerate(files):
            file_path = os.path.join(data_dir, filename)
            samples = GetBranchContent(file_path)[1]
            samples = BaselineSubtract(samples)
            IntegrateSamples(file_path,integrals_dir,samples,0)


if __name__ == '__main__':

    main()