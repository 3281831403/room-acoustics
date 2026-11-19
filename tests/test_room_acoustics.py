import pytest

from audio import room_acoustics as mod

CASES = [
    pytest.param('door_crossfade', (0.5, 0.2), 0.4999999999999998, True, id='01_door_crossfade'),
    pytest.param('wall_filter', (1.0, 1, 0.5), 0.25, True, id='02_wall_occlusion_filter'),
    pytest.param('source_buses', (3,), (0, 1, 2), False, id='03_per_source_buses'),
    pytest.param('align_clock', (1.0, 1.1, 0.1), 0.0, True, id='04_audio_clock_alignment'),
    pytest.param('cancel_job', ('A', 'B'), True, False, id='05_cancel_old_room_job'),
    pytest.param('resample_ir', (48000, 48000, 44100), 44100, False, id='06_ir_resample'),
    pytest.param('update_occlusion', (0.0, 0.1, 0.05), True, False, id='07_dynamic_occlusion_update'),
    pytest.param('switch_room', (1.0,), True, False, id='08_switch_after_door_animation'),
    pytest.param('hrtf_profile', ('headphones',), 'hrtf-headphones', False, id='09_headphone_hrtf'),
    pytest.param('normalize_overlap', ([1.0, 3.0],), (0.25, 0.75), True, id='10_overlap_energy_normalized'),
    pytest.param('rt60', (100.0, 200.0, 0.1), 0.805, True, id='11_sabine_rt60'),
    pytest.param('attenuation', (2.0, 0.5), 0.5, True, id='12_distance_attenuation'),
    pytest.param('door_amount', (0.5,), 0.5, True, id='13_door_mix_amount'),
    pytest.param('resample_length', (1000, 48000, 44100), 919, False, id='14_resample_length_ratio'),
    pytest.param('tail_length', (1.2, 30.0), 0.6, True, id='15_reverb_tail_length'),
]


def assert_close(actual, expected):
    if isinstance(expected, tuple):
        assert isinstance(actual, tuple) and len(actual) == len(expected)
        for a, e in zip(actual, expected):
            assert_close(a, e)
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(actual) == len(expected)
        for a, e in zip(actual, expected):
            assert_close(a, e)
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            assert_close(actual[key], expected[key])
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize("func_name,args,expected,approx", CASES)
def test_room_acoustics_contract(func_name, args, expected, approx):
    func = getattr(mod, func_name)
    result = func(*args)
    if approx:
        assert_close(result, expected)
    else:
        assert result == expected
