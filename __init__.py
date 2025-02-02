import os
import platform

import Pyro4


def get_version():
    """Read library version from qick_lib/qick/VERSION (a text file containing only the version number).

    Parameters
    ----------

    Returns
    -------
    str
        version number, in major.minor.PR format
    """
    versionpath = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(versionpath) as version_file:
        version = version_file.read().strip()
        return version


__version__ = get_version()


def bitfile_path():
    """Choose the default firmware path for this board.

    Parameters
    ----------

    Returns
    -------
    str
        absolute path to the firmware bitfile distributed with the QICK library
    """
    board2file = {
        "ZCU216": "qick_216.bit",
        "ZCU111": "qick_111.bit",
        "RFSoC4x2": "qick_4x2.bit",
    }
    filename = board2file[os.environ["BOARD"]]
    src = os.path.join(os.path.dirname(qick.__file__), filename)
    return src


# tie in to rpyc, if using
try:
    from rpyc.utils.classic import obtain
except ModuleNotFoundError:

    def obtain(i):
        return i


from .asm_v1 import QickProgram
from .averager_program import AveragerProgram, NDAveragerProgram, RAveragerProgram
from .qick_asm import DummyIp, QickConfig

# only import the hardware drivers if running on a Zynq
# also import if we're in the ReadTheDocs Sphinx build (the imports won't really work but they will be mocked)
if (
    platform.machine() in ["aarch64", "armv7l"]
    or os.getenv("READTHEDOCS", default="False") == "True"
):
    try:
        from .ip import SocIp
        from .qick import QickSoc
    except Exception as e:
        print("Could not import QickSoc:", e)
else:
    import numpy as np

    # if we're not on a Zynq, we need to mock the QickSoc class
    SocIp = list

    class QickSoc:
        def __init__(self):
            self.autoproxy = []

        @Pyro4.expose
        def get_cfg(self):
            return {}

        def adcfreq(self, fpt, *args, **kwargs):
            return fpt

        def us2cycles(self, us, *args, **kwargs):
            if isinstance(us, np.ndarray):
                return (us * 1e3).astype(int)
            return int(us * 1e3)

        def cycles2us(self, cycles, *args, **kwargs):
            if isinstance(cycles, np.ndarray):
                return cycles.astype(float) / 1e3
            return float(cycles) / 1e3

    class QickConfig:
        def __init__(self, cfg=None):
            pass

        def __repr__(self):
            return "Dummy QickConfig"

        def adcfreq(self, fpt, *args, **kwargs):
            return fpt

        def us2cycles(self, us, *args, **kwargs):
            if isinstance(us, np.ndarray):
                return (us * 1e3).astype(int)
            return int(us * 1e3)

        def cycles2us(self, cycles, *args, **kwargs):
            if isinstance(cycles, np.ndarray):
                return cycles.astype(float) / 1e3
            return float(cycles) / 1e3
