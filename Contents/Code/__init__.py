####################################################################################################################
#
#                                  Reddit Videos Plex Channel
#
# This is a channel for Plex.  It allows users to browse videos that have been submitted to reddit.com.
# Users can store and delete favorite subreddits, multireddits, and browse supplied categories.  All menu options
# can be customized in the preferences.  If you have any questions or requests, find me on reddit at
# u/seagullcanfly or at github https://github.com/seagullcanfly/RedditVideos.bundle.
#
####################################################################################################################

from view.menu import Menu

NAME = "Reddit Videos"
PREFIX = "/video/redditvideos"

def Start():
    ObjectContainer.title1 = NAME


@handler(PREFIX, NAME)
def MainMenu():
    return Menu.build_main_menu(Prefs)


