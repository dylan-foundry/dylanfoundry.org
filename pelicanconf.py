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

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

# Pages
PAGES = (('About', '/about/'),)

# Blogroll
LINKS =  (('OpenDylan.org', 'http://opendylan.org/'),)

# Social widget
SOCIAL = (('icon-twitter', '@DylanFoundry', 'https://twitter.com/DylanFoundry'),
          ('icon-twitter', '@DylanLanguage', 'https://twitter.com/DylanLanguage'),
          ('icon-github', 'dylan-foundry/GitHub', 'https://github.com/dylan-foundry/'),
          ('icon-github', 'dylan-lang/GitHub', 'https://github.com/dylan-lang/'),
          ('icon-heart', 'Tip me via GitTip', 'https://www.gittip.com/waywardmonkeys/'),)

GITHUB_URL = 'https://github.com/dylan-foundry/'
TWITTER_USERNAME = 'DylanFoundry'
DISQUS_SITENAME = 'dylanfoundry'

DEFAULT_PAGINATION = 10

SUMMARY_MAX_LENGTH = 200

THEME = 'foundry-themes/pelican'
