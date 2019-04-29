# -*- coding: utf-8 -*-
'''
SRF podcasts plugin.
'''

PREFIX = '/video/srf'
NAME   = 'SRF Podcasts'
ART    = 'art.jpg'
ICON   = 'icon.jpg'


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
def VideoMainMenu():
    '''
    Handler for the top / main menu.
    '''
    Log.Debug('Handling main menu')
    oc = ObjectContainer(title1=L('SRF Podcasts'))
    return oc
