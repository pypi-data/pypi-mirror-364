import argparse
import cProfile
import io
import os
import pstats
import time

import torch as th
import yaml

import omnigibson as og
from omnigibson.macros import gm

NUM_STEPS = 100


def main(random_selection=False, headless=False, short_exec=False):
    # Load the config
    gm.RENDER_VIEWER_CAMERA = False
    gm.ENABLE_FLATCACHE = True
    gm.USE_GPU_DYNAMICS = False
    config_filename = os.path.join(og.example_config_path, "fetch_primitives.yaml")
    config = yaml.load(open(config_filename, "r"), Loader=yaml.FullLoader)

    config["scene"]["load_object_categories"] = ["floors", "walls", "coffee_table"]

    # Load the environment
    vec_env = og.VectorEnvironment(5, config)
    import time

    max_iterations = 100 if not short_exec else 1
    for _ in range(max_iterations):
        start_time = time.time()
        for _ in range(NUM_STEPS):
            actions = []
            for e in vec_env.envs:
                actions.append(e.action_space.sample())
            vec_env.step(actions)

        step_time = time.time() - start_time
        fps = NUM_STEPS / step_time
        effective_fps = NUM_STEPS * len(vec_env.envs) / step_time
        print("fps", fps)
        print("effective fps", effective_fps)


if __name__ == "__main__":
    main()
