import os
import sys
import pycarta
# from pycarta import *
from pycarta.auth import CartaLoginUI
from .ui import AimpfCartaProfile
from warnings import warn

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


# ##### Import pycarta submodules ##### #
from pycarta import (
    admin,
    auth,
    graph,
    # mqtt,  # This masks the aimpf.mqtt package.
    sbg,
    services,
)


# ##### Top-level pycarta resources ##### #
from pycarta import (
    __CONTEXT,
    AuthenticationError,
    CartaAgent,
    CartaLoginUI,
    Group,
    Profile,
    PycartaContext,
    SbgLoginManager,
    Singleton,
    User,
    authorize,
    get_agent,
    ioff,
    ion,
    is_authenticated,
    is_interactive,
    service,
    set_agent,
)


# ##### Manage Carta Environment and Setup ##### #
CARTA_PROFILE = os.environ.get('CARTA_PROFILE', 'aimpf')


def set_profile():
    app = AimpfCartaProfile(profile=CARTA_PROFILE)

from pycarta import login
