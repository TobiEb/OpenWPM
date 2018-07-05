from __future__ import absolute_import
from automation import TaskManager, CommandSequence
from six.moves import range
from crawl_sites import SubSites

# The list of sites that we wish to crawl
NUM_BROWSERS = 1

#sites = ['www.google.de', 'www.youtube.com', 'www.facebook.com', 'www.amazon.de', 'www.ebay.de', 'www.vk.com', 'www.web.de', 'www.gmx.net', 'www.reddit.com', 'www.t-online.de']
sites = ['http://www.web.de', 'http://www.zalando.de', 'http://www.spiegel.de', 'http://www.wetter.de', 'http://www.tvspielfilm.de', 'http://www.gmx.net', 'http://www.t-online.de', 'http://www.ebay.de']
#sites = ['http://google.de']

# Loads the manager preference and 3 copies of the default browser dictionaries
manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)

# Update browser configuration (use this for per-browser settings)
for i in range(NUM_BROWSERS):
    browser_params[i]['headless'] = True
    browser_params[i]['http_instrument'] = True
    browser_params[i]['js_instrument'] = True
    browser_params[i]['save_javascript'] = True
    browser_params[i]['cookie_instrument'] = True
    browser_params[i]['disable_flash'] = False
    browser_params[i]['tp_cookies'] = 'always' # or never or from_visited
    browser_params[i]['bot_mitigation'] = False # throws a lot of errors if enabled
    # add ons related
    browser_params[i]['disconnect'] = False
    browser_params[i]['ghostery'] = False
    browser_params[i]['ublock-origin'] = False
    # if profile should be saved
    #browser_params[i]['profile_archive_dir'] = '/home/OpenWPM/Output/Profile'
    # if profile should be loaded
    #browser_params[i]['profile_tar'] = '/home/OpenWPM/Output/Profile'

    #self written
    browser_params[i]['scroll_down'] = False
    browser_params[i]['login'] = False
    browser_params[i]['execute_script'] = False

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = '/home/OpenWPM/Output'
manager_params['log_directory'] = '/home/OpenWPM/Output'
#manager_params['database_name'] = 'output.sqlite'

default_timeout = 60
default_sleep = 5
a = SubSites()

manager = TaskManager.TaskManager(manager_params, browser_params)

# Visits the sites with all browsers simultaneously
for site in sites:
    # define crawl actions
    # define prior login
    #command_sequence_google = CommandSequence.CommandSequence('http://accounts.google.de', reset=False)
    #command_sequence_google.get(sleep=default_sleep, timeout=default_timeout)
    #command_sequence_google.dump_profile_cookies(timeout=default_timeout)
    #command_sequence_google.dump_flash_cookies(timeout=default_timeout)

    command_sequence_get1 = CommandSequence.CommandSequence(site, reset=False)
    command_sequence_get1.get(initiator=True, sleep=default_sleep, timeout=default_timeout)
    #command_sequence_get1.stop_tshark(timeout=10)
    command_sequence_get1.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get1.dump_flash_cookies(timeout=default_timeout)

    command_sequence_get2 = CommandSequence.CommandSequence(a.sub_sites[0], reset=False)
    command_sequence_get2.get(initiator=False, sleep=default_sleep, timeout=default_timeout)
    #command_sequence_get2.stop_tshark(timeout=10)
    command_sequence_get2.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get2.dump_flash_cookies(timeout=default_timeout)

    command_sequence_get3 = CommandSequence.CommandSequence(a.sub_sites[1], reset=False)
    command_sequence_get3.get(initiator=False, sleep=default_sleep, timeout=default_timeout)
    #command_sequence_get3.stop_tshark(timeout=10)
    command_sequence_get3.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get3.dump_flash_cookies(timeout=default_timeout)

    command_sequence_get4 = CommandSequence.CommandSequence(a.sub_sites[2], reset=False)
    command_sequence_get4.get(initiator=False, sleep=default_sleep, timeout=default_timeout)
    #command_sequence_get4.stop_tshark(timeout=10)
    command_sequence_get4.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get4.dump_flash_cookies(timeout=default_timeout)

    command_sequence_get5 = CommandSequence.CommandSequence(a.sub_sites[3], reset=True)
    command_sequence_get5.get(initiator=False, sleep=default_sleep, timeout=default_timeout)
    #command_sequence_get5.stop_tshark(timeout=10)
    command_sequence_get5.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get5.dump_flash_cookies(timeout=default_timeout)

    command_sequence_browse5 = CommandSequence.CommandSequence(site, reset=True)
    command_sequence_browse5.browse(num_links=4, sleep=default_sleep, timeout=(5*default_timeout))
    command_sequence_browse5.dump_profile_cookies(timeout=(5*default_timeout))
    command_sequence_browse5.dump_flash_cookies(timeout=(5*default_timeout))

    #manager.execute_command_sequence(command_sequence_google, index='**')
    manager.execute_command_sequence(command_sequence_get1, index='**') # ** = synchronized browsers
    print "dazwischen"
    print a.sub_sites
    manager.execute_command_sequence(command_sequence_get2, index='**') # ** = synchronized browsers
    manager.execute_command_sequence(command_sequence_get3, index='**') # ** = synchronized browsers
    manager.execute_command_sequence(command_sequence_get4, index='**') # ** = synchronized browsers
    manager.execute_command_sequence(command_sequence_get5, index='**') # ** = synchronized browsers
    manager.execute_command_sequence(command_sequence_browse5, index='**') # ** = synchronized browsers
    print "We will visit ", site
    
# Shuts down the browsers and waits for the data to finish logging
manager.close()
