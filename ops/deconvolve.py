# from deconv_methods import elephant_preprocess, elephant_deconv
# import rpy2.robjects.packages
# from c2s import c2s
# from cmt.models import MCGSM
# from c2s import robust_linear_regression
from numpy import *
import sys
sys.path.append('/home/mwinter')

from OASIS.oasis.functions import deconvolve as oasis_deconv
from OASIS.oasis import oasisAR1, oasisAR2

class deconvolve(object):
    """Wrapper class for deconvolving spikes from Ca2+ data."""

    def __getitem__(self, name):
        """Get attribute from class."""
        return getattr(self, name)

    def __contains__(self, name):
        """Check if class contains attribute."""
        return hasattr(self, name)

    def __init__(self, kwargs=None):
        """Class global variable init."""
        self.data_fps = 30.  # Ca2+ FPS for Allen.
        self.batch_size = 4096
        self.update_params(kwargs)
        self.check_params()
        self.deconvolved_trace = self.deconvolve()


    def check_params(self):
        if not hasattr(self, 'deconv_method'):
            print 'Skipping deconvolution'
        if not hasattr(self, 'batch_size'):
            raise RuntimeError(
                'You must pass a batch_size.')
        if not hasattr(self, 'deconv_dir'):
            raise RuntimeError(
                'You must pass a deconv_dir.')
        if not hasattr(self, 'data_fps'):
            raise RuntimeError(
                'You must pass a data_fps.')
        if not hasattr(self, 'neural_trace'):
            raise RuntimeError(
                'You must pass a neural_trace.')

    def update_params(self, kwargs):
        """Update the class attributes with kwargs."""
        if kwargs is not None:
            for k, v in kwargs.iteritems():
                setattr(self, k, v)

    # def deconvolve(self, neural_data):
    #     """Wrapper for deconvolution operations."""
    #     preproc_op, deconv_op = self.interpret_deconv(self.deconv_method)
    #     if preproc_op is not None:
    #         print 'Preprocessing neural data.'
    #         neural_data = preproc_op(neural_data)
    #     else:
    #         print 'Don\' need preprocessing.'
    #     print 'Deconvolving neural data.'
    #     return deconv_op(neural_data)
    def deconvolve(self):
        """Wrapper for deconvolution operations."""
        preproc_op, deconv_op = self.interpret_deconv(self.deconv_method)
        if preproc_op is not None:
            # print 'Preprocessing neural data.'
            self.neural_trace = preproc_op(self.neural_trace)
        else:
            # print 'Don\'t need preprocessing.'
        # print 'Deconvolving neural data.'
        return deconv_op(double(self.neural_trace))

    def interpret_deconv(self, method):
        """Wrapper for returning the preprocessing and main operations."""
        if method == 'elephant':
            return (
                elephant_preprocess.preprocess,
                elephant_deconv.deconv)
        elif method == 'lzerospikeinference':
            lzsi = rpy2.robjects.packages.importr("LZeroSpikeInference")
            preprocess = lambda x: x.tolist()
            method = lambda x: lzsi.estimateSpikes(x, **{'gam': 0.998, 'lambda': 8, 'type': "ar1"})
            return (preprocess, method)
        elif method == 'c2s':
            def preprocess(x, fps=30.):
                d = []
                for ce in x:
                    d += [{'calcium': ce, 'fps': fps}]
                return c2s.preprocess(d, fps=fps)
            method = lambda x: c2s.predict(x)
            return (preprocess, method)
        elif method == 'oasis':
            return (None, oasis_deconv)
        else:
            return None
