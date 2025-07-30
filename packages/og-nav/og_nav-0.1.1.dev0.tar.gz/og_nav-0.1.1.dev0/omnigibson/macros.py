"""
Set of macros to use globally for OmniGibson. These are generally magic numbers that were tuned heuristically.

NOTE: This is generally decentralized -- the monolithic @settings variable is created here with some global values,
but submodules within OmniGibson may import this dictionary and add to it dynamically
"""

import os
import pathlib

from addict import Dict


class MacroDict(Dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["_read"] = set()

    def __setattr__(self, name, value):
        if name in self.get("_read", set()):
            raise AttributeError(f"Cannot set attribute {name} in MacroDict, it has already been used.")
        # Use the super's setattr for setting attributes, but handle _read directly to avoid recursion.
        if name == "_read":
            self[name] = value
        else:
            super().__setattr__(name, value)

    def __getattr__(self, item):
        # Directly check and modify '_read' to avoid going through __getattr__ or __setattr__.
        if item != "_read":
            self["_read"].add(item)
        # Use direct dictionary access to avoid infinite recursion.
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"'MacroDict' object has no attribute '{item}'")


# Initialize settings
macros = MacroDict()
gm = macros.globals


def determine_gm_path(default_path, env_var_name):
    # Start with the default path
    path = default_path
    # Override with the environment variable, if set
    if env_var_name in os.environ:
        path = os.environ[env_var_name]
    # Expand the user directory (~)
    path = os.path.expanduser(path)
    # Make the path absolute if it's not already
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
    return path


# Path (either relative to OmniGibson/omnigibson directory or global absolute path) for data
# Assets correspond to non-objects / scenes (e.g.: robots), and dataset incliudes objects + scene
# can override assets_path and dataset_path from environment variable
gm.ASSET_PATH = determine_gm_path(os.path.join("~/Projects/data/omnigibson", "assets"), "OMNIGIBSON_ASSET_PATH")
gm.DATASET_PATH = determine_gm_path(os.path.join("~/Projects/data/omnigibson", "og_dataset"), "OMNIGIBSON_DATASET_PATH")
gm.KEY_PATH = determine_gm_path(os.path.join("~/Projects/data/omnigibson", "omnigibson.key"), "OMNIGIBSON_KEY_PATH")

# Which GPU to use -- None will result in omni automatically using an appropriate GPU. Otherwise, set with either
# integer or string-form integer
gm.GPU_ID = os.getenv("OMNIGIBSON_GPU_ID", None)

# Whether to generate a headless or non-headless application upon OmniGibson startup
gm.HEADLESS = os.getenv("OMNIGIBSON_HEADLESS", "False").lower() in ("true", "1", "t")

# Whether to enable remote streaming. None disables it, other valid options are "native", "webrtc".
gm.REMOTE_STREAMING = os.getenv("OMNIGIBSON_REMOTE_STREAMING", None)

# What port the webrtc and http servers should run on. This is only used if REMOTE_STREAMING is set to "webrtc"
gm.HTTP_PORT = os.getenv("OMNIGIBSON_HTTP_PORT", 8211)
gm.WEBRTC_PORT = os.getenv("OMNIGIBSON_WEBRTC_PORT", 49100)

# Whether only the viewport should be shown in the GUI or not (if not, other peripherals are additionally shown)
# CANNOT be set at runtime
gm.GUI_VIEWPORT_ONLY = False

# Whether to use the viewer camera or not
gm.RENDER_VIEWER_CAMERA = True

# Do not suppress known omni warnings / errors, and also put omnigibson in a debug state
# This includes extra information for things such as object sampling, and also any debug
# logging messages
gm.DEBUG = os.getenv("OMNIGIBSON_DEBUG", "False").lower() in ("true", "1", "t")

# Whether to print out disclaimers (i.e.: known failure cases resulting from Omniverse's current bugs / limitations)
gm.SHOW_DISCLAIMERS = False

# Whether to use omni's GPU dynamics
# This is necessary for certain features; e.g. particles (fluids / cloth)
gm.USE_GPU_DYNAMICS = False

# Whether to use high-fidelity rendering (this includes, e.g., isosurfaces)
gm.ENABLE_HQ_RENDERING = False

# Whether to use omni's flatcache feature or not (can speed up simulation)
gm.ENABLE_FLATCACHE = False

# Whether to use continuous collision detection or not (slower simulation, but can prevent
# objects from tunneling through each other)
gm.ENABLE_CCD = False

# Pairs setting -- USD default is 256 * 1024, physx default apparently is 32 * 1024.
gm.GPU_PAIRS_CAPACITY = 256 * 1024
# Aggregate pairs setting -- default is 1024, but is often insufficient for large scenes
gm.GPU_AGGR_PAIRS_CAPACITY = (2**14) * 1024

# Maximum particle contacts allowed
gm.GPU_MAX_PARTICLE_CONTACTS = 1024 * 1024

# Maximum rigid contacts -- 524288 is default value from omni, but increasing too much can sometimes lead to crashes
gm.GPU_MAX_RIGID_CONTACT_COUNT = 524288 * 4

# Maximum rigid patches -- 81920 is default value from omni, but increasing too much can sometimes lead to crashes
gm.GPU_MAX_RIGID_PATCH_COUNT = 81920 * 4

# Whether to enable object state logic or not
gm.ENABLE_OBJECT_STATES = True

# Whether to enable transition rules or not
gm.ENABLE_TRANSITION_RULES = True

# Default settings for the omni UI viewer
gm.DEFAULT_VIEWER_WIDTH = 1280
gm.DEFAULT_VIEWER_HEIGHT = 720

# Default physics / rendering / sim step frequencies (Hz)
# rendering must be a multiple of physics frequency, and sim_step must be a multiple of rendering frequency
gm.DEFAULT_SIM_STEP_FREQ = 30
gm.DEFAULT_RENDERING_FREQ = 30
gm.DEFAULT_PHYSICS_FREQ = 120

# (Demo-purpose) Whether to activate Assistive Grasping mode for Cloth (it's handled differently from RigidBody)
gm.AG_CLOTH = False

# Forced light intensity for all DatasetObjects. None if the USD-provided intensities should be respected.
gm.FORCE_LIGHT_INTENSITY = 150000

# Forced roughness for all DatasetObjects. None if the USD-provided roughness maps should be respected.
gm.FORCE_ROUGHNESS = 0.7


# Create helper function for generating sub-dictionaries
def create_module_macros(module_path):
    """
    Creates a dictionary that can be populated with module macros based on the module's @module_path

    Args:
        module_path (str): Relative path from the package root directory pointing to the module. This will be parsed
            to generate the appropriate sub-macros dictionary, e.g., for module "dirty" in
            omnigibson/object_states_dirty.py, this would generate a dictionary existing at macros.object_states.dirty

    Returns:
        MacroDict: addict/macro dictionary which can be populated with values
    """
    # Sanity check module path, make sure omnigibson/ is in the path
    module_path = pathlib.Path(module_path)
    omnigibson_path = pathlib.Path(__file__).parent

    # Trim the .py, and anything before and including omnigibson/, and split into its appropriate parts
    try:
        subsections = module_path.with_suffix("").relative_to(omnigibson_path).parts
    except ValueError:
        raise ValueError(
            "module_path is expected to be a filepath including the omnigibson root directory, got: {module_path}!"
        )

    # Create and return the generated sub-dictionary
    def _recursively_get_or_create_dict(dic, keys):
        # If no entry is in @keys, it returns @dic
        # Otherwise, checks whether the dictionary contains the first entry in @keys, if so, it grabs the
        # corresponding nested dictionary, otherwise, generates a new MacroDict() as the value
        # It then recurisvely calls this function with the new dic and the remaining keys
        if len(keys) == 0:
            return dic
        else:
            key = keys[0]
            if key not in dic:
                dic[key] = MacroDict()
            return _recursively_get_or_create_dict(dic=dic[key], keys=keys[1:])

    return _recursively_get_or_create_dict(dic=macros, keys=subsections)
