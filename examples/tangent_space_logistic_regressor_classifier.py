import os
import argparse

import numpy as np

from mne import read_epochs
from mne.filter import notch_filter
from joblib import Parallel, delayed
from pyriemann.estimation import Covariances
from sklearn.preprocessing import LabelEncoder
from pyriemann.tangentspace import TangentSpace
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--classes', nargs='+')
args = parser.parse_args()

# Initialize processing components
le = LabelEncoder()
cov = Covariances(estimator='lwf')  # Covariance matrix estimator
ts = TangentSpace()  # Tangent space projection for Riemannian geometry
lr = LogisticRegression()
s_scaler = StandardScaler()

directory = os.fsencode(os.path.abspath(os.getcwd()))

classes = args.classes
power_noise = [60]  # Power line noise frequency
max_freq = 127  # Maximum frequency limit
n_fts = 400
fs = 256  # Sampling frequency

def run_all(classes, top_n_bands=5):
    """Main pipeline: process all subjects and save scores."""
    s=0
    all_scores, all_coeffs, all_folds = [], [], []
    for dr in os.listdir(directory):
        if os.path.isdir(dr):
            if os.path.exists(os.path.join(dr, 'ica_epo.fif'.encode("utf-8"))):
                print('sub ', s+1)
                x, y = get_data(str(dr).split("'")[1])  # Load subject data
                score = run_l1_cv(x,y, top_n_bands)  # Run classification
                all_scores.append(score)
                s += 1

    np.save('ts_lr_scs_'+classes[0]+'_'+classes[1]+'_.npy', all_scores)

def run_l1_cv(x, y, top_n_bands):
    """Run L1-regularized logistic regression with cross-validation."""
    lr = LogisticRegression(max_iter=600, penalty='l1', solver='saga', n_jobs=16)
    x = filter_data(x)  # Filter into frequency bands
    x = [cov.fit_transform(freq) for freq in x]  # Compute covariance matrices
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=36)

    cv_split = cv.split(x[0], y)
    all_scores = []

    for train_idx, test_idx in cv_split:
        train, test = [], []
        y_train, y_test = y[train_idx], y[test_idx]

        # Parallel tangent space transformation for each frequency band
        result = Parallel(n_jobs=16)(delayed(run_ts_transform)(band[train_idx], band[test_idx])for band in x)

        for res in result:
            train.append(res[0])
            test.append(res[1])

        # Reshape: concatenate features from all bands
        train, test = np.transpose(train, (1, 0, 2)), np.transpose(test, (1, 0, 2))
        train, test = train.reshape(train.shape[0], -1), test.reshape(test.shape[0], -1)

        lr.fit(train, y_train)
        score = lr.score(test, y_test)
        all_scores.append(score)

    print('final:::::')
    print(np.median(all_scores))
    return all_scores

def run_ts_transform(train, test):
    """Apply tangent space transformation to covariance matrices."""
    return ts.fit_transform(train), ts.transform(test)

def filter_data(x):
    """Filter EEG data into multiple frequency bands and apply notch filtering."""
    x_all = []
    for freq in freqs:
        # Bandpass filter for current frequency range
        data = x.copy().filter(freq[0], freq[1], verbose=False, n_jobs=8).crop(time[0], time[1]).get_data()

        # Apply notch filter if power line noise is in band
        for noise_freq in power_noise:
            if noise_freq > freq[0] and noise_freq < freq[1]:
                print('notching at', noise_freq, 'for:', freq)
                data = np.apply_along_axis(notch_filter, -1, data, Fs=fs, method='iir', freqs=noise_freq, verbose=False)

        x_all.append(data)

    return np.array(x_all)

def get_data(sub):
    """Load and preprocess EEG epochs for a subject."""
    epochs = read_epochs(sub+'/ica_epo.fif')
    epochs = epochs.drop_channels(epochs.info['bads'])  # Remove bad channels

    # Select specific classes and preprocess
    epochs_data = epochs[classes].copy().pick('eeg').apply_baseline((-.3,0))
    labels = le.fit_transform(epochs_data.events[:,2])  # Encode class labels

    return epochs_data.resample(fs), labels  # Resample to target frequency

def get_possible_freqs(min_freq=2, freq_step=6, freq_size=8):
    """Generate overlapping frequency bands for filtering."""
    frequency_ranges = []
    start_freq = min_freq
    while start_freq < max_freq:
        end_freq = start_freq + freq_size
        if end_freq <= max_freq:
            frequency_ranges.append((start_freq, end_freq))
        start_freq += freq_step

    unique_ranges = sorted(list(set(frequency_ranges)))
    return unique_ranges

# Define frequency bands and time window
freqs = get_possible_freqs()
time = 0.1, 1.7

if __name__ == "__main__":
    run_all(classes)