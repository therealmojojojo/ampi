from components import music_box
from ampi import AmpiController
import time
import pytest

@pytest.fixture
def init_ampi():
    ampi = AmpiController()
    return ampi

def test_ampi_load(init_ampi):
    ampi = init_ampi
    print("----- print startup -------")
    
    ampi.save_state("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    ampi.load_old_state()

    assert ampi.playlist == "spotify:album:1sKj6LEXiEfCmsiKwPy5uG"

def test_ampi_volume(init_ampi):
    ampi = init_ampi

