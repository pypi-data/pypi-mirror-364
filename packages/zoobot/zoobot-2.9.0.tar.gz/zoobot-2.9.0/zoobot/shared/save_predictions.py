import json
from typing import List
import logging

import numpy as np
import pandas as pd
import h5py


def predictions_to_hdf5(predictions, id_str, label_cols, save_loc, compression="gzip"):
    logging.info(f'Saving predictions to {save_loc}')
    assert save_loc.endswith('.hdf5')
    if label_cols is None:
        label_cols = get_default_label_cols(predictions)
    # sometimes throws a "could not lock file" error but still saves fine. I don't understand why
    with h5py.File(save_loc, "w") as f:
        f.create_dataset(name='predictions', data=predictions, compression=compression)
        # https://docs.h5py.org/en/stable/special.html#h5py.string_dtype
        dt = h5py.string_dtype(encoding='utf-8')
        # predictions_dset.attrs['label_cols'] = label_cols  # would be more conventional but is a little awkward
        f.create_dataset(name='id_str', data=id_str, dtype=dt)
        f.create_dataset(name='label_cols', data=label_cols, dtype=dt)

def predictions_to_csv(predictions, id_str, label_cols, save_loc):
    
    # not recommended - hdf5 is much more flexible and pretty easy to use once you check the package quickstart
    assert save_loc.endswith('.csv')
    if label_cols is None:
        label_cols = get_default_label_cols(predictions)
    data = [prediction_to_row(predictions[n], id_str[n], label_cols=label_cols) for n in range(len(predictions))]
    predictions_df = pd.DataFrame(data)
    # logging.info(predictions_df)
    predictions_df.to_csv(save_loc, index=False)


def prediction_to_row(prediction: np.ndarray, id_str: str, label_cols: List):
    """
    Convert prediction on image into dict suitable for saving as csv
    Predictions are encoded as a json e.g. "[1., 0.9]" for 2 repeat predictions on one galaxy
    This makes them easy to read back with df[col] = df[col].apply(json.loads)

    Args:
        prediction (np.ndarray): model output for one galaxy, including repeat predictions e.g. [[1., 0.9], [0.3, 0.24]] for model with output_dim=2 and 2 repeat predictions
        id_str (str): path to image
        label_cols (list): semantic labels for model output dim e.g. ['smooth', 'bar'].

    Returns:
        dict: of the form {'id_str': 'path', 'smooth_pred': "[1., 0.9]", 'bar_pred: "[0.3, 0.24]"}
    
    """
    row = {
        'id_str': id_str  # may very well be a path to an image, if using an image dataset - just rename later
    }
    for n in range(len(label_cols)):
        answer = label_cols[n]
        answer_pred = prediction[n].astype(float)  # (n_samples,) shape
        if isinstance(answer_pred, float) or isinstance(answer_pred, np.float64):
            row[answer + '_pred'] = answer_pred  # it's a scalar already, life is good
        elif len(answer_pred) == 1:  # i.e. if only one sample
            row[answer + '_pred'] = answer_pred.squeeze()  # it's a scalar in disguise, make it a scalar 
        else:
            row[answer + '_pred'] = json.dumps(list(answer_pred))  # it's not a scalar, write as json
    return row

def get_default_label_cols(predictions):
    logging.warning('No label_cols passed - using default names e.g. feat_0, feat_1...')
    label_cols = [f'feat_{n}' for n in range(predictions.shape[1])]
    return label_cols
