class SubSites():
    sites_100_DE = ['http://www.google.de', 'http://www.google.com', 'http://www.youtube.com', 'http://www.facebook.com', 'http://www.amazon.de', 'http://www.ebay.de', 'http://www.wikipedia.org', 'http://www.ebay-kleinanzeigen.de', 'http://www.vk.com', 'http://www.instagram.com', 'http://www.mail.ru', 'http://www.ok.ru', 'http://www.web.de', 'http://www.xhamster.com', 'http://www.twitter.com', 'http://www.gmx.net', 'http://www.yahoo.com', 'http://www.paypal.com', 'http://www.yandex.ru', 'http://www.t-online.de', 'http://www.livejasmin.com', 'http://www.pornhub.com', 'http://www.spiegel.de', 'http://www.google.com.ua', 'http://www.reddit.com', 'http://www.google.ru', 'http://www.bild.de', 'http://www.live.com', 'http://www.zdf.de', 'http://www.bing.com', 'http://www.txxx.com', 'http://www.chip.de', 'http://www.netflix.com', 'http://www.whatsapp.com', 'http://www.twitch.tv', 'http://www.focus.de', 'http://www.otto.de', 'http://www.welt.de', 'http://www.postbank.de', 'http://www.wetter.com', 'http://www.blogspot.com', 'http://www.tumblr.com', 'http://www.mobile.de', 'http://www.microsoft.com', 'http://www.xvideos.com', 'http://www.immobilienscout24.de', 'http://www.dhl.de', 'http://www.msn.com', 'http://www.bahn.de', 'http://www.booking.com', 'http://www.aliexpress.com', 'http://www.amazon.com', 'http://www.wikia.com', 'http://www.idealo.de', 'http://www.pinterest.de', 'http://www.github.com', 'http://www.youporn.com', 'http://www.wordpress.com', 'http://www.sportschau.de', 'http://www.wetteronline.de', 'http://www.1und1.de', 'http://www.chaturbate.com', 'http://www.heise.de', 'http://www.tagesschau.de', 'http://www.zeit.de', 'http://www.deutsche-bank.de', 'http://www.bs.to', 'http://www.telekom.com', 'http://www.imdb.com', 'http://www.rambler.ru', 'http://www.stackoverflow.com', 'http://www.wetter.de', 'http://www.vodafone.de', 'http://www.sueddeutsche.de', 'http://www.linkedin.com', 'http://www.hclips.com', 'http://www.commerzbank.de', 'http://www.gutefrage.net', 'http://www.faz.net', 'http://www.computerbild.de', 'http://www.mediamarkt.de', 'http://www.n-tv.de', 'http://www.ing-diba.de', 'http://www.shop-apotheke.com', 'http://www.upornia.com', 'http://www.imgur.com', 'http://www.xing.com', 'http://www.ardmediathek.de', 'http://www.kicker.de', 'http://www.xnxx.com', 'http://www.check24.de', 'http://www.adobe.com', 'http://www.dict.cc', 'http://www.redtube.com', 'http://www.bongacams.com', 'http://www.apple.com', 'http://www.autoscout24.de', 'http://www.lidl.de', 'http://www.dkb.de', 'http://www.vice.com']

    ## ACHTUNG HIER WURDEN 4 ABGEZOGEN, AUS DEM NAECHST GROESSTEN HINZUFUEGEN
    # t.co
    # deref-web-02.de
    # deref-gmx.de
    # crptentry.com

    _sub_sites = ['','','','']
    @property
    def sub_sites(self):
        return self.__class__._sub_sites
    @sub_sites.setter
    def sub_sites(self, sites):
        self.__class__._sub_sites = sites


