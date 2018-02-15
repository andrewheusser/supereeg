from __future__ import print_function
import os
import pickle
import warnings
import numpy as np
import deepdish as dd
import pandas as pd
import nibabel as nib
from nilearn.input_data import NiftiMasker
from .brain import Brain
from .model import Model
from .helpers import tal2mni, _fullfact

def load(fname):
    """
    Load nifti file, brain or model object, or example data.

    This function can load in example data, as well as nifti files, brain objects (.bo)
    and model objects (.mo) by detecting the extension and calling the appropriate
    load function.  Thus, be sure to include the file extension in the fname
    parameter.

    Parameters
    ----------
    fname : string
        The name of the example data or a filepath.

        Example data includes:

        example_data - example brain object (n = 64)

        example_model - example model object with locations from gray_mask_20mm_brain.nii (n = 170)

        example_locations - example location from gray_mask_20mm_brain.nii (n = 170)

        example_nifti - example nifti file from gray_mask_20mm_brain.nii (n = 170)

        pyFR_k10r20_20mm - model used for analyses from
        `Owen LLW and Manning JR (2017) Towards Human Super EEG.  bioRxiv: 121020` with 20mm resolution (n = 170)
        
        pyFR_k10r20_6mm - model used for analyses from
        `Owen LLW and Manning JR (2017) Towards Human Super EEG.  bioRxiv: 121020` with 6 mm resolution (n = 10K)

    Returns
    ----------
    data : nibabel.Nifti1, supereeg.Brain or supereeg.Model
        Data to be returned

    """

    if fname is 'example_data':
        with open(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/CH003.npz', 'rb') as handle:
            f = np.load(handle)
            data = f['Y']
            sample_rate = f['samplerate']
            sessions = f['fname_labels']
            locs = tal2mni(f['R'])
            meta = 'CH003'

        return Brain(data=data, locs=locs, sessions=sessions, sample_rate=sample_rate, meta= meta)

    elif fname is 'example_model':
        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/mini_model.mo', 'rb') as handle:
                example_model = pickle.load(handle)
            return example_model

        except:
            try:
                mo = dd.io.load(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/mini_model.mo')
                return Model(numerator=mo['numerator'], denominator=mo['denominator'],
                             locs=mo['locs'], n_subs=mo['n_subs'], meta=mo['meta'],
                             date_created=mo['date_created'])
            except:
                model = pd.read_pickle(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/mini_model.mo')
                return model


    elif fname is 'pyFR_k10r20_20mm':
        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/mini_model.mo', 'rb') as handle:
                example_model = pickle.load(handle)
            return example_model
        except:
            try:
                mo = dd.io.load(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/mini_model.mo')
                return Model(numerator=mo['numerator'], denominator=mo['denominator'],
                             locs=mo['locs'], n_subs=mo['n_subs'], meta=mo['meta'],
                             date_created=mo['date_created'])
            except:
                model = pd.read_pickle(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/mini_model.mo')
                return model


    elif fname is 'pyFR_k10r20_6mm':
        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_mask_6mm_brain.mo', 'rb') as handle:
                example_model = pickle.load(handle)
            return example_model
        except:
            try:
                mo = dd.io.load(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_mask_6mm_brain.mo')
                return Model(numerator=mo['numerator'], denominator=mo['denominator'],
                             locs=mo['locs'], n_subs=mo['n_subs'], meta=mo['meta'],
                             date_created=mo['date_created'])
            except:
                model = pd.read_pickle(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_mask_6mm_brain.mo')
                return model


    elif fname is 'example_locations':
        with open(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_20mm_locs.npy', 'rb') as handle:
            locs = np.load(handle)
        return locs

    elif fname is 'example_nifti':
        bo = load_nifti(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_mask_8mm_brain.nii')
        return bo

    elif fname is 'example_filter':
        bo = dd.io.load(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/example_filter.bo')
        return Brain(data=bo['data'], locs=bo['locs'], sessions=bo['sessions'],
                    sample_rate=bo['sample_rate'], meta=bo['meta'],
                    date_created=bo['date_created'])

    elif fname is 'pyFR_union':
        with open(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/pyFR_k10_locs.npz', 'rb') as handle:
            data = np.load(handle)
            locs = data['locs']
            print(('subjects = ', data['subjs']))
        return locs

    elif fname is 'gray_mask_20mm_brain':
        bo = load_nifti(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_mask_20mm_brain.nii')
        return bo

    elif fname is 'gray_mask_6mm_brain':
        bo = load_nifti(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/gray_mask_6mm_brain.nii')
        return bo

    elif fname is 'std.nii':
        bo = load_nifti(os.path.dirname(os.path.abspath(__file__)) + '/../supereeg/data/std.nii')
        return bo

    # load brain object
    elif fname.split('.')[-1]=='bo':
        bo = dd.io.load(fname)
        return Brain(data=bo['data'], locs=bo['locs'], sessions=bo['sessions'],
                     sample_rate=bo['sample_rate'], meta=bo['meta'],
                     date_created=bo['date_created'])

    # load model object
    elif fname.split('.')[-1]=='mo':
        mo = dd.io.load(fname)
        return Model(numerator=mo['numerator'], denominator=mo['denominator'],
                     locs=mo['locs'], n_subs=mo['n_subs'], meta=mo['meta'],
                     date_created=mo['date_created'])

    # load nifti
    elif fname.split('.')[-1]=='nii' or '.'.join(fname.split('.')[-2:])=='nii.gz':
        return load_nifti(fname)


def load_nifti(nifti_file, mask_file=None):
    """
    Load nifti file and convert to brain object

    Parameters
    ----------
    fname : string
        Filepath to nifti file.


    Returns
    ----------
    results : brain object
        Brain object from nifti file

    """


    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        img = nib.load(nifti_file)
        mask = NiftiMasker(mask_strategy='background')
        if mask_file is None:
            mask.fit(nifti_file)
        else:
            mask.fit(mask_file)

    hdr = img.header
    S = img.get_sform()
    _vox_size = hdr.get_zooms()
    im_size = img.shape

    if len(img.shape) > 3:
        N = img.shape[3]
    else:
        N = 1

    Y = np.float64(mask.transform(nifti_file)).copy()
    vmask = np.nonzero(np.array(np.reshape(mask.mask_img_.dataobj, (1, np.prod(mask.mask_img_.shape)), order='C')))[1]
    vox_coords = _fullfact(img.shape[0:3])[vmask, ::-1]-1

    R = np.array(np.dot(vox_coords, S[0:3, 0:3])) + S[:3, 3]

    return Brain(data=Y, locs=R, meta={'header': hdr})
