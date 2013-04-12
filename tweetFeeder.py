#!/usr/bin/python
import twitter
import re
import pinboard
import urllib2
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
import gzip

# The Pinboard account credentials to use
pyAccount = 'aUserAccount'
pyPass = 'anAwesomePassword'

# The Twitter API Keys. You need your own.
api = twitter.Api(consumer_key='gibberish', consumer_secret='moregibberish', access_token_key='evenlongergibberish', access_token_secret='thelastbitofgibberish')
#print api.VerifyCredentials()

#Twitter users with interesting links
feedList = ['binaryghost', 'viticci', 'marksiegal', 'ttscoff', 'gromble', 'drbunsen', 'waltonjones', 'TJLuoma', 'eddie_smith', 'chewingpencils', 'jeffhunsberger', 'nateboateng']

# The adventure begins
for user in feedList:
    # Get all of the user tweets
    statuses = api.GetUserTimeline(user)
    # Loop through all tweets and look for URLs
    for status in statuses:
        # A reasonably generous URL regex pattern to match
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', status.text)
        # Everytime we find a URL, do some magic
        if urls:
            for url in urls:
                # Put together the tweet info
                tweetMsg = status.text
                rssTag = ['rss_'+user, 'rss_tweets']
                sourceURL = 'https://twitter.com/'+user+'/status/'+str(status.id)
                try:
                    # Let's make sure the URL is valid by trying to visit it
                    request = urllib2.Request(url)
                    request.add_header('Accept-encoding', 'gzip')
                    response = urllib2.urlopen(request)
                    data = response
                    maintype = response.headers['Content-Type'].split(';')[0].lower()
                    # We don't want image links
                    if maintype not in ('image/png', 'image/jpeg', 'image/gif'):
                        # Need to handle gzip content if we want to grab the page title. Lots of sites send gzip now.
                        if response.info().get('Content-Encoding') == 'gzip':
                            buf = StringIO(response.read())
                            f = gzip.GzipFile(fileobj=buf)
                            data = f.read()
                        # I guess I just prefer a real link to shitty t.co links
                        fullURL = response.url

                        if fullURL is not None:
                            print fullURL
                            # This could be done with lxml but BeautifulSoup is easy
                            soup = BeautifulSoup(data)
                            # Get the title for the page
                            myTitle = soup.html.head.title
                            pyTitle = myTitle.string
                            print pyTitle
                            # Assemble the bookmark notes. Create Twitter link for RSS viewing
                            bookmarkExtended = '<p>'+user+'</p>\n<p>' + tweetMsg + '</p>\n\n' + '<a href="'+sourceURL+'">Twitter Source</a>'
                            try:
                                p = pinboard.open(pyAccount, pyPass)
                                postResult = p.add(url=fullURL, description=pyTitle, extended=bookmarkExtended, tags= (rssTag))
                            except (RuntimeError, TypeError, NameError):
                                print RuntimeError
                                print NameError
                                print TypeError
                except urllib2.HTTPError, err:
                    # If it's an http error like 404, just skip the link. We don't have time for this junk.
                    continue