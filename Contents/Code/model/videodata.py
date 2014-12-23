
class VideoData:
    def __init__(self, video_post_data):
        self.urls = []
        self.domain = video_post_data['data'].get('domain')
        self.title = video_post_data['data'].get('title')
        self.score = str(video_post_data['data'].get('score'))
        self.id = str(video_post_data['data'].get('id'))
        self.subreddit = video_post_data['data'].get('subreddit')
        self.thumbnail = video_post_data['data'].get('thumbnail')
        self.nsfw = video_post_data['data'].get('over_18')  # working on this
        if self.domain in ['youtube.com', 'vimeo.com']:
            try:
                self.summary = video_post_data['data']['media']['oembed'].get('description')
            except AttributeError:
                self.summary = self.title
            self.urls = [video_post_data['data'].get('url')]
        if video_post_data['data'].get('is_self'):
            self.summary = video_post_data['data']['selftext']
            text_post = self.summary
            youtube_prefix = 'http://www.'
            youtube_key = 'youtube.com/watch?v='
            youtube_length = len(youtube_key) + 11
            start_index = text_post.find(youtube_key)
            while start_index > 0:
                text_post = text_post[start_index::]
                end_index = youtube_length
                vid_url = youtube_prefix + text_post[:end_index]
                if vid_url not in self.urls and good_url(vid_url):
                    self.urls.append(vid_url)
                text_post = text_post[end_index::]
                start_index = text_post.find(youtube_key)
