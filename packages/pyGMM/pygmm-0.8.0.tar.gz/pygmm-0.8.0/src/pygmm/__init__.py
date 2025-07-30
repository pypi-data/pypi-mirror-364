"""pyGMM: Ground motion models implemented in Python."""

import logging

try:
    from ._version import __version__
except ImportError:
    # For development installs
    __version__ = "unknown"

from .abrahamson_bhasin_2020 import AbrahamsonBhasin2020
from .abrahamson_gregor_addo_2016 import AbrahamsonGregorAddo2016
from .abrahamson_silva_1996 import AbrahamsonSilva1996
from .abrahamson_silva_kamai_2014 import AbrahamsonSilvaKamai2014
from .afshari_stewart_2016 import AfshariStewart2016
from .akkar_sandikkaya_bommer_2014 import AkkarSandikkayaBommer2014
from .atkinson_boore_2006 import AtkinsonBoore2006
from .bayless_abrahamson_2018 import BaylessAbrahamson2018
from .bayless_abrahamson_2019 import BaylessAbrahamson2019
from .boore_stewart_seyhan_atkinson_2014 import BooreStewartSeyhanAtkinson2014
from .campbell_2003 import Campbell2003
from .campbell_bozorgnia_2014 import CampbellBozorgnia2014
from .chiou_youngs_2014 import ChiouYoungs2014
from .coppersmith_bommer_2014 import CoppersmithBommer2014
from .derras_bard_cotton_2014 import DerrasBardCotton2014
from .gulerce_abrahamson_2011 import GulerceAbrahamson2011
from .idriss_2014 import Idriss2014
from .kempton_stewart_2006 import KemptonStewart2006
from .model import Scenario
from .pezeshk_zandieh_tavakoli_2011 import PezeshkZandiehTavakoli2011
from .stafford_2017 import Stafford2017
from .tavakoli_pezeshk_2005 import TavakoliPezeshk05

__all__ = [
    "Scenario",
    "AbrahamsonBhasin2020",
    "AbrahamsonSilvaKamai2014",
    "AbrahamsonGregorAddo2016",
    "AfshariStewart2016",
    "AkkarSandikkayaBommer2014",
    "AtkinsonBoore2006",
    "BaylessAbrahamson2018",
    "BaylessAbrahamson2019",
    "BooreStewartSeyhanAtkinson2014",
    "Campbell2003",
    "CampbellBozorgnia2014",
    "ChiouYoungs2014",
    "CoppersmithBommer2014",
    "DerrasBardCotton2014",
    "GulerceAbrahamson2011",
    "KemptonStewart2006",
    "Idriss2014",
    "PezeshkZandiehTavakoli2011",
    "TavakoliPezeshk05",
    "Stafford2017",
]

__author__ = "Albert Kottke"
__copyright__ = "Copyright 2016 Albert Kottke"
__license__ = "MIT"
__title__ = "pyGMM"

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())

models = [
    AbrahamsonSilva1996,
    AbrahamsonSilvaKamai2014,
    AfshariStewart2016,
    AkkarSandikkayaBommer2014,
    AtkinsonBoore2006,
    BaylessAbrahamson2019,
    BooreStewartSeyhanAtkinson2014,
    Campbell2003,
    CampbellBozorgnia2014,
    ChiouYoungs2014,
    CoppersmithBommer2014,
    DerrasBardCotton2014,
    GulerceAbrahamson2011,
    KemptonStewart2006,
    Idriss2014,
    PezeshkZandiehTavakoli2011,
    TavakoliPezeshk05,
    Stafford2017,
]
