__author__ = 'markryan'

class Reddit():
    def good_url(self, url):
        """ This will filter out unwanted words in the url."""
        return ('playlist' not in url) and ('crackle.com' not in url) and url