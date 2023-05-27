import vlc

Instance = vlc.Instance()
player = Instance.media_player_new()
Media = Instance.media_new("./second_trialcurrent.mp3")
Media.get_mrl()
player.set_media(Media)
player.play()
