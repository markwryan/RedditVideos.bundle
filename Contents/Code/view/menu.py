__author__ = 'markryan'

from model.videodata import VideoData
from controller.reddit import Reddit as reddit

USER_AGENT = 'seagullcanfly on Reddit RedditVideos Plex plugin'  # https://github.com/reddit/reddit/wiki/API
MULTI_SUMMARY = '''Enter the user who created the subreddit, a comma (",") followed by the name
of the multireddit.  For example, you could enter this without the quotation marks to enter my
gamingvideos multireddit, "seagullcanfly, gamingvideos"'''
MULTI_PROMPT = '''Enter the user who created the multireddit, a comma, then the multireddit's name
e.g., seagullcanfly, gamingvideos'''
FAVORITES_SUMMARY = ''''Enter the name of a subreddit.
Do not include "r/".  e.g., "r/videos" should be entered as "videos."'''
FAVORITES_PROMPT = '''Enter the name of a subreddit.'''
SUBREDDIT_DISCOVERY_URL = "http://www.reddit.com/user/seagullcanfly/m/plexsubreddits"
GAMING_URL = "http://www.reddit.com/user/seagullcanfly/m/gamingvideos"
SUBREDDIT_BASE = 'http://www.reddit.com/r/%s/.json'

class Menu():
    def build_main_menu(self, Prefs):
        """ Creates the following menus: Videos, Custom Favorites, Enter Multireddit, Enter Manual, All domains,
         Subreddit Discovery, Gaming Discovery """
        oc = ObjectContainer()
        # Videos Menu
        if Prefs['show_videos']:
            oc.add(DirectoryObject(key=Callback(self.view_sort, url=SUBREDDIT_BASE % 'videos'),
                                   title='Videos Subreddit', summary='This is the most popular r/videos subreddit.'))
        # Custom Favorites Menu
        if Prefs['show_custom_favorites']:
            oc.add(DirectoryObject(key=Callback(self.custom_favorites),
                                   title='Custom Favorites', summary='Store your favorite subreddits'))
        # Enter Multireddit
        if Prefs['show_enter_multireddit']:
            oc.add(DirectoryObject(key=Callback(self.enter_multireddit),
                                   title='Enter a multireddit', summary='Add a favorite multireddit.'))
        # Enter Manual Menu
        if Prefs['show_enter_manual']:
            oc.add(InputDirectoryObject(key=Callback(self.enter_manual),
                                        title='Enter a subreddit',
                                        summary='Manually entered subreddits are not saved. Enter the name of a subreddit.' +
                                                '\nDo not include "r/".  e.g., "r/videos" should be entered as "videos"',
                                        prompt="Enter the name of a subreddit"))
        # Search Reddit
        if Prefs['show_search_reddit']:
            oc.add(InputDirectoryObject(key=Callback(self.domain_search),
                                        title='Search Reddit',  summary='This will search all youtube videos uploaded to reddit.',
                                        prompt="Enter your search term"))
        # All Domains Menu
        if Prefs['show_domains']:
            oc.add(DirectoryObject(key=Callback(self.get_domains),
                                   title='All Domains', summary='Lists the most popular videos from a domain like Youtube regardless' +
                                                                'of what subreddit they come from.'))
        # Subreddit Discovery Menu
        if Prefs['show_subreddit_discovery']:
            oc.add(DirectoryObject(key=Callback(self.subreddit_discovery, url=SUBREDDIT_DISCOVERY_URL),
                                   title="Subreddit Discovery", summary="A collection of subreddits maintained by u/seagullcanfly."))
        # Gaming Subreddits
        if Prefs['show_gaming_subreddits']:
            oc.add(DirectoryObject(key=Callback(self.subreddit_discovery, url=GAMING_URL),
                                   title="Gaming Subreddits", summary="A collection of gaming subreddits."))
        # Preferences
        oc.add(PrefsObject
               (title='Change channel settings', summary="Customize the menus, and enable scores or comments."))
        return oc

    def subreddit_discovery(self, url):
        """ subreddit_discovery polls a maintained list of popular subreddits from a published multireddit."""
        oc = ObjectContainer()
        oc.add(DirectoryObject(key=Callback(self.get_videos, url=url + ".json"), title="All Subreddits Combined.."))
        content = HTML.ElementFromURL(url)
        multi_subreddits = content.xpath('//ul[@class="subreddits"]//li/a/text()')
        clean_subreddits = []
        for sub in multi_subreddits:
            sub = sub.split('r/')[-1]
            clean_subreddits.append(sub.title())
        subreddits = clean_subreddits
        for subreddit in sorted(subreddits):
            url = SUBREDDIT_BASE % subreddit
            title = 'r/%s' % subreddit
            oc.add(DirectoryObject(key=Callback(self.view_sort, url=url), title=title))
        return oc

    def enter_multireddit(self):
        """ Has the following menus: Add a Multireddit, Delete a Multireddit, Custom Favorites Populated """
        oc = ObjectContainer()
        multireddits = Dict['multireddits']
        if not multireddits:
            Dict['multireddits'] = []
        else:
            # List stored Multireddits
            for user, multi in multireddits:
                user, multi = user.strip(), multi.strip()
                url = 'http://www.reddit.com/user/%s/m/%s' % (user, multi)
                title = "%s's %s" % (user, multi)
                oc.add(DirectoryObject(key=Callback(self.subreddit_discovery, url=url),
                                       title=title, summary="This is a stored multireddit."))

                # Add a Multireddit
        oc.add(InputDirectoryObject(key=Callback(self.enter_multi),
                                    title='Add a Multireddit', summary=MULTI_SUMMARY, prompt=MULTI_PROMPT))

        # Delete a Multireddit
        oc.add(InputDirectoryObject(key=Callback(self.delete_multi),
                                    title='Delete a Multireddit', summary=MULTI_SUMMARY, prompt=MULTI_PROMPT))
        return oc

    def enter_multi(self, query):
        """ This adds a user-generated multireddit in persistent storage."""
        self.handle_multi(query, operation='add')


    def delete_multi(self, query):
        """ This deletes a user-generated multireddit from persistent storage."""
        self.handle_multi(query, operation='delete')


    def handle_multi(self, query, operation='add'):
        """ This adds a user-generated multireddit in persistent storage."""
        multireddits = Dict['multireddits']
        query = query.split(',')
        query = (query[0], query[1])
        if not multireddits:
            multireddits = []
        if operation == 'add':
            multireddits.append(query)
        else:
            multireddits.remove(query)
        Dict['multireddits'] = multireddits

    def view_sort(self, url):
        """ All videos can be sorted by hot, new, and top.  Top includes all time, year, month, week, day, and hour."""
        oc = ObjectContainer()
        url_list = url.split('.json')
        top_url, new_url = url_list[0] + 'top/.json', url_list[0] + 'new/.json'
        oc.add(DirectoryObject(key=Callback(self.get_videos, url=url), title="Hot"))
        oc.add(DirectoryObject(key=Callback(self.get_videos, url=new_url), title="New"))
        sortings = {'all': 'Top - All Time', 'year': 'Top - Year', 'month': 'Top - Month', 'week': 'Top - Week',
                    'day': 'Top - Day', 'hour': 'Top - Hour'}
        sort_order = ['all', 'year', 'month', 'week', 'day', 'hour']
        for view in sort_order:
            oc.add(DirectoryObject(key=Callback(self.get_videos, url=top_url, sort=view), title=sortings[view]))
        return oc

    def get_videos(self, url, count=0, limit=100, after='', sort=None):
        """ This method returns all the video links for any specific page. """
        oc = ObjectContainer()
        url += '?count=%d&limit=%d&after=%s' % (count, limit, after)
        if sort:
            url += '&sort=top&t=%s' % sort
        search_page = JSON.ObjectFromURL(url, sleep=2.0, cacheTime=600, headers={'User-Agent': USER_AGENT})
        @parallelize
        def get_video_links():
            for video_child in search_page['data']['children']:
                @task
                def get_video(video_post=video_child):
                    reddit_video = VideoData(video_post)
                    if Prefs['show_score']:
                        video_title = reddit_video.score + " | " + reddit_video.title
                    for video_url in reddit_video.urls:
                        if reddit.good_url(video_url):
                            if Prefs['show_comment_menu']:
                                oc.add(DirectoryObject(key=Callback(
                                    commented_videos, video_url=video_url, video_id=reddit_video.id,
                                    video_subreddit=reddit_video.subreddit, video_title=video_title,
                                    video_summary=reddit_video.summary), title=video_title, thumb=reddit_video.thumbnail))
                            else:
                                video_object = URLService.MetadataObjectForURL(video_url)
                                video_object.title = String.StripTags(video_title)
                                video_object.summary = String.StripTags(reddit_video.summary)
                                oc.add(video_object)
        # Find/Add Next Menu
        after = search_page['data'].get('after')
        count += limit
        if after:
            oc.add(NextPageObject(key=Callback(videos, url=url, count=count, limit=limit, after=after), title='Next ...'))
        return oc


    def commented_videos(self, video_url, video_id, video_subreddit, video_title, video_summary):
        """Shows the top-rated comments for a video dependent on preferences."""
        oc = ObjectContainer()
        video_object = URLService.MetadataObjectForURL(video_url)
        video_object.title = String.StripTags(video_title)
        video_object.summary = String.StripTags(video_summary)
        oc.add(video_object)
        comment_url = 'http://www.reddit.com/r/' + video_subreddit + '/' + video_id + '.json'
        comment_page = JSON.ObjectFromURL(comment_url, sleep=2.0, cacheTime=600, headers={'User-Agent': USER_AGENT})
        comments = comment_page[1]['data']['children']
        for comment in comments:
            comment_text = comment['data'].get('body')
            if not comment_text:
                comment_text = "Not yet commented on."
            oc.add(DirectoryObject(key=Callback(show_comment, comment=comment_text), title=comment_text[0:30] + "...",
                                   summary=comment_text))
        return oc


    def show_comment(self, comment):
        return ObjectContainer(header='Video Comment', message=comment)

    ###############################################  FAVORITES  ########################################################


    def custom_favorites(self):
        """ Has the following menus: Add a Custom Favorite, Delete a Custom Favorite, Custom Favorites Populated"""
        oc = ObjectContainer()
        oc.add(InputDirectoryObject(key=Callback(enter_favorite),
                                    title='Add a Custom Favorite', summary=FAVORITES_SUMMARY, prompt=FAVORITES_PROMPT))
        oc.add(InputDirectoryObject(key=Callback(delete_favorite),
                                    title='Delete a Custom Favorite', summary=FAVORITES_SUMMARY, prompt=FAVORITES_PROMPT))
        custom_faves = Dict['favorites']
        if not custom_faves:
            custom_faves = ['enterfavorites']
            Dict['favorites'] = custom_faves
        for subreddit in custom_faves:
            url = SUBREDDIT_BASE % subreddit
            title = 'r/%s' % subreddit
            oc.add(DirectoryObject(key=Callback(view_sort, url=url), title=title))
        return oc


    def enter_favorite(self, query):
        """ This adds a user-generated subreddit in persistent storage."""
        handle_favorites(query, 'add')


    def delete_favorite(self, query):
        """ This deletes a user-generated subreddit from persistent storage."""
        handle_favorites(query, 'delete')


    def handle_favorites(self, query, operation):
        """ Mains favorites in the persistent dictionary."""
        favorites = Dict['favorites']
        if not favorites:
            favorites = []
        if operation == 'add':
            favorites.append(query)
        else:
            favorites.remove(query)
        Dict['favorites'] = favorites

    ###############################################  DOMAINS  ##########################################################


    def get_domains(self):
        """ get_domains lists all the videos on reddit for the domains in domain_list."""
        oc = ObjectContainer()
        domain_list = ['youtube.com', 'vimeo.com']
        for domain in sorted(domain_list):
            url = 'http://www.reddit.com/domain/%s/.json' % domain
            title = 'domain/' + domain
            oc.add(DirectoryObject(key=Callback(videos, url=url), title=title))
        return oc

    ###############################################  SEARCH  ###########################################################


    def domain_search(self, query):
        """ domain_search searches for any video uploaded to reddit on youtube that matches the query."""
        oc = ObjectContainer()
        search_url = "http://www.reddit.com/domain/youtube.com/search.json?q=%s&restrict_sr=on" % query
        title = 'Searching for "%s"....' % query
        oc.add(DirectoryObject(key=Callback(videos, url=search_url), title=title))
        return oc

    ###############################################  MANUAL  ###########################################################


    def enter_manual(self, query):
        """ enter_manual allows a user to enter a subreddit manually."""
        oc = ObjectContainer()
        url = SUBREDDIT_BASE % query
        title = 'r/' + query
        oc.add(DirectoryObject(key=Callback(view_sort, url=url), title=title))
        return oc