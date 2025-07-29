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


def login(interactive: None | bool=None) -> bool:
    # Log into Carta
    try:
        # Using default profile name
        pycarta.login(profile=CARTA_PROFILE)
        return True
    except:
        pass
    try:
        # Using environment variables
        pycarta.login(
            username=os.environ['CARTA_USER'],
            password=os.environ.get('CARTA_PASS'),
            environment=os.environ.get('CARTA_ENV', 'production')
        )
        return True
    except:
        pass
    # Interactively
    if interactive or is_interactive():
        try:
            set_agent(
                CartaLoginUI(
                    title="Carta login credentials for AIMPF").login(
                        environment=os.environ.get('CARTA_ENV', 'production'),
                        host=os.environ.get('CARTA_HOST', None),
                        )
            )
            return True
        except:
            pass
    warn("Could not login to Carta. Please run `aimpf.login` to try again.")
    return False
