# -*- coding: utf-8 -*-
'''
SRF podcasts plugin.
'''

PREFIX = '/video/srf-podcasts-new'
NAME   = 'SRF Podcasts'
ART    = 'art.jpg'
ICON   = 'icon.jpg'

NUMBER_OF_EPISODES     = 50
EPISODES_API_BASE_URL  = 'https://www.srf.ch'
EPISODES_API_FIRST_URL = '/play/tv/show/{id}/latestEpisodes?numberOfEpisodes={number_of_episodes}'
PLAYER_API_URL         = 'https://il.srgssr.ch/integrationlayer/1.0/ue/srf/video/play/{id}.json'


def Start():
    '''
    Start & initialization of the SRF podcasts plugin.
    '''

    Log.Debug('Starting plugin')

    ObjectContainer.title1 = NAME
    DirectoryObject.thumb  = R(ICON)
    VideoClipObject.thumb  = R(ICON)
    VideoClipObject.art    = R(ART)

    HTTP.CacheTime = CACHE_1HOUR


@handler(PREFIX, NAME, art=ART, thumb=ICON)
def ShowMenu():
    '''
    Handler for the main / top menu.
    '''
    Log.Debug('Handling show menu')
    oc = ObjectContainer(title1=NAME)

    podcasts_html = HTML.ElementFromURL('https://www.srf.ch/podcasts')
    shows         = podcasts_html.xpath('//li[@class="shows"]')

    for show in shows:
        title   = show.xpath('./a/img')[0].get('title')
        thumb   = show.xpath('./a/img')[0].get('data-retina-src')
        summary = show.xpath('./div[@class="module-content"]/p')[0].text
        show_id  = show.xpath('.//div[contains(@class, "podcast-data")]')[0].get('data-podcast-uuid')

        oc.add(TVShowObject(
            key=Callback(EpisodesMenu, show_id=show_id, title=title),
            rating_key=show_id,
            title=title,
            summary=summary,
            thumb=Resource.ContentsOfURLWithFallback(thumb))
        )

    return oc


def get_episodes_api_url(show_id, page_url=None):
    '''
    Return the URL for the episodes API.

    The initial URL is predefined / hardcoded in this code. However, the API
    is using paging and after requesting the first "page", the URL of the next
    page is returned in the API response (see ``nextPageUrl`` parameter).

    :param str show_id: The ID of the show
    :param str page_url: An optinoal page URL

    :return: The episode API URL
    :rtype: str
    '''
    url = EPISODES_API_BASE_URL

    if page_url:
        url += page_url
    else:
        url += EPISODES_API_FIRST_URL.format(id=show_id, number_of_episodes=NUMBER_OF_EPISODES)

    return url

def get_available_episodes(api_response):
    '''
    Return all available episodes from the JSON object retreived by the API.

    :param dict api_response: The response retreived from the API

    :return: List of episodes
    :rtype: list
    '''
    episodes = []

    for episode in api_response['episodes']:
        try:
            assert 'downloadHdUrl' in episode
            episodes.append({
                'url': PLAYER_API_URL.format(id=episode['id']),
                'title': episode.get('title', L('No title available')),
                'summary': episode.get('lead', L('No summary available')),
                'thumb': episode['imageUrl'],
            })
        except AssertionError:
            pass

    return episodes

@route(PREFIX + '/episodes')
def EpisodesMenu(show_id, title, page_url=None):
    '''
    Handler for the episodes menu, which is displayed when a show is selected.
    '''
    Log.Debug('Handling episode menu for {}'.format(title))
    oc = ObjectContainer(title1=NAME, title2=title)

    url = get_episodes_api_url(show_id, page_url)
    api_response = JSON.ObjectFromURL(url, cacheTime=CACHE_1HOUR)

    episodes = get_available_episodes(api_response)
    if not episodes:
        return ObjectContainer(
            header=L('No episodes available'),
            message=L('Sorry, there are no episodes available for this show.')
        )

    for episode in episodes:
        try:
            oc.add(VideoClipObject(**episode))
        except AssertionError:
            pass

    try:
        page_url = api_response['nextPageUrl']
        assert page_url
        assert len(episodes) == NUMBER_OF_EPISODES

        oc.add(NextPageObject(
            key=Callback(
                EpisodesMenu,
                title=title,
                show_id=show_id,
                page_url=page_url
            ),
            title=L('More Episodes')
        ))
    except (AssertionError, KeyError):
        pass

    return oc
