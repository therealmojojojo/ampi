from components import music_box
import time
import pytest

@pytest.fixture
def get_spotify_client():
    print("----- getting spotify -------")
    player = music_box.get_client("spotify")
    player.connect_to_provider()
    state = player.get_current_state()
    assert state is not None
    player.stop()
    player.clear()
    return player

def test_connection(get_spotify_client):
    player = get_spotify_client


def test_play(get_spotify_client):
    print("----- test_play -------")
    player = get_spotify_client
    player.play_new("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    time.sleep(5)
    state = player.get_current_state()
    assert state == "playing"

def test_playpause(get_spotify_client):
    print("----- test_playpause -------")
    player = get_spotify_client
    state = player.get_current_state()
    assert state == "stopped"
    player.play_new("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    time.sleep(5)
    state = player.get_current_state()
    assert state == "playing"
    player.pause()
    state = player.get_current_state()
    assert state == "paused"
    player.play()
    state = player.get_current_state()
    assert state == "playing"
    player.stop()
    state = player.get_current_state()
    assert state == "stopped"


def test_currenttrack(get_spotify_client):
    print("----- currentrack -------")
    player = get_spotify_client
    player.play_new("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    time.sleep(5)

    current_track = player.get_current_track()
    print(current_track)
    assert "ANIMA" == current_track["album"]["name"]
    assert "Thom Yorke" == current_track["artists"][0]["name"]
    assert "2019" == current_track["date"]
    assert 160 <= current_track["bitrate"]
    assert 318000 == current_track["length"]
    
