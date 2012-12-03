#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u"DataFueled"
SITENAME = u"Dylan Foundry"
SITEURL = 'http://dylanfoundry.org'

TIMEZONE = 'UTC'

DEFAULT_LANG = 'en'

DEFAULT_CATEGORY = 'Dylan'

ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

# Blogroll
LINKS =  (('OpenDylan.org', 'http://opendylan.org/'),)

# Social widget
SOCIAL = (('@DylanFoundry', 'https://twitter.com/DylanFoundry'),
          ('@DylanLanguage', 'https://twitter.com/DylanLanguage'),)

GITHUB_URL = 'https://github.com/dylan-foundry/'
TWITTER_USERNAME = 'DylanFoundry'

DEFAULT_PAGINATION = 10

THEME = 'foundry-themes/pelican'
