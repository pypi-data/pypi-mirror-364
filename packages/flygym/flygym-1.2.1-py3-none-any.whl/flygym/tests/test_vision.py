import numpy as np
import tempfile
import pytest
import logging
from pathlib import Path

from flygym import Fly, SingleFlySimulation, is_rendering_skipped
from flygym.util import load_config
from flygym.vision import visualize_visual_input


np.random.seed(0)


@pytest.mark.skipif(is_rendering_skipped, reason="env['SKIP_RENDERING'] == 'true'")
def test_vision_dimensions():
    # Load config
    config = load_config()

    # Initialize simulation
    num_steps = 100
    fly = Fly(enable_olfaction=True, enable_vision=True, render_raw_vision=True)
    sim = SingleFlySimulation(fly=fly)

    # Run simulation
    obs_list = []
    info_list = []
    for i in range(num_steps):
        joint_pos = np.zeros(len(fly.actuated_joints))
        action = {"joints": joint_pos}
        obs, reward, terminated, truncated, info = sim.step(action)
        # nmf.render()
        obs_list.append(obs)
        info_list.append(info)
    sim.close()

    # Check dimensionality
    assert len(obs_list) == num_steps
    assert fly.vision_update_mask.shape == (num_steps,)
    assert fly.vision_update_mask.sum() == int(
        num_steps * sim.timestep * fly.vision_refresh_rate
    )
    height = config["vision"]["raw_img_height_px"]
    width = config["vision"]["raw_img_width_px"]
    assert info["raw_vision"].shape == (2, height, width, 3)
    assert obs["vision"].shape == (2, config["vision"]["num_ommatidia_per_eye"], 2)

    print((obs["vision"][:, :, 0] > 0).sum(), (obs["vision"][:, :, 1] > 0).sum())

    # Test postprocessing
    temp_base_dir = Path(tempfile.gettempdir()) / "flygym_test"
    logging.info(f"temp_base_dir: {temp_base_dir}")
    visualize_visual_input(
        fly.retina,
        output_path=temp_base_dir / "vision/eyes.mp4",
        vision_data_li=[x["vision"] for x in obs_list],
        raw_vision_data_li=[x["raw_vision"] for x in info_list],
        vision_update_mask=fly.vision_update_mask,
        vision_refresh_rate=fly.vision_refresh_rate,
        playback_speed=0.1,
    )
