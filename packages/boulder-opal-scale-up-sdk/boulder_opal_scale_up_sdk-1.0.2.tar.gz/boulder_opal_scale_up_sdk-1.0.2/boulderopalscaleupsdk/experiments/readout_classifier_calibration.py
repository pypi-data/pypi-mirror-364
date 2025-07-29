from pydantic import PrivateAttr

from boulderopalscaleupsdk.experiments.common import Experiment


class ReadoutClassifierCalibration(Experiment):
    """
    Parameters for running calibration of readout classifier for a transmon.

    Parameters
    ----------
    transmon : str
        The reference for the transmon to target in the experiment.
    recycle_delay_ns : int
        The delay time between consecutive shots of the experiment, in nanoseconds.
    shot_count : int, optional
        The number of shots to be taken in the experiment.
        Defaults to 5000.
    """

    _experiment_name: str = PrivateAttr("readout_classifier_calibration")
    transmon: str
    recycle_delay_ns: int
    shot_count: int = 5000
