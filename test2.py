class PodEpisode():
    def __init__(self):
        self.pod_name = None
        self.episode_name = None
        self.episode_title = None
        self.episode_description = None
        self.episode_url = None
        self.episode_published = None
        self.playback_speed = None
    

pod = PodEpisode()
pod.pod_name = 'Pod Name'
print(pod.pod_name)
