from __future__ import absolute_import
from automation import TaskManager, CommandSequence
from six.moves import range

# The list of sites that we wish to crawl
NUM_BROWSERS = 1

#sites = ['www.google.de', 'www.youtube.com', 'www.facebook.com', 'www.amazon.de', 'www.ebay.de', 'www.vk.com', 'www.web.de', 'www.gmx.net', 'www.reddit.com', 'www.t-online.de']
#sites = ['http://www.spiegel.de', 'http://www.zalando.de', 'http://www.web.de', 'http://www.wetter.de', 'http://www.tvspielfilm.de']
sites = ['https://www.google.de']

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
    #browser_params[i]['profile_archive_dir'] = '/home/tobi/Schreibtisch/Tests/Profile/'
    # if profile should be loaded
    #browser_params[i]['profile_tar'] = '/home/tobi/Schreibtisch/Tests/Profile/'

    #self written
    browser_params[i]['scroll_down'] = False
    browser_params[i]['login'] = False

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = '/home/tobi/Schreibtisch/Tests/'
manager_params['log_directory'] = '/home/tobi/Schreibtisch/Tests/'

default_timeout = 140

manager = TaskManager.TaskManager(manager_params, browser_params)

# Visits the sites with all browsers simultaneously
for site in sites:
    # define crawl actions
    command_sequence_get = CommandSequence.CommandSequence(site, reset=False)
   # command_sequence_get.exec_script()
    command_sequence_get.get(sleep=0, timeout=default_timeout)
    command_sequence_get.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get.dump_flash_cookies(timeout=default_timeout)

    #command_sequence_browse1 = CommandSequence.CommandSequence(site, reset=True)
    #command_sequence_browse1.browse(num_links=1, sleep=0, timeout=(2*default_timeout))
    #command_sequence_browse1.dump_profile_cookies(timeout=(2*default_timeout))
    #command_sequence_browse1.dump_flash_cookies(timeout=(2*default_timeout))

    command_sequence_browse2 = CommandSequence.CommandSequence(site, reset=False)
    command_sequence_browse2.browse(num_links=2, sleep=0, timeout=(3*default_timeout))
    command_sequence_browse2.dump_profile_cookies(timeout=(3*default_timeout))
    command_sequence_browse2.dump_flash_cookies(timeout=(3*default_timeout))

    #command_sequence_browse3 = CommandSequence.CommandSequence(site, reset=True)
    #command_sequence_browse3.browse(num_links=3, sleep=0, timeout=(4*default_timeout))
    #command_sequence_browse3.dump_profile_cookies(timeout=(4*default_timeout))
    #command_sequence_browse3.dump_flash_cookies(timeout=(4*default_timeout))

    #command_sequence_browse4 = CommandSequence.CommandSequence(site, reset=True)
    #command_sequence_browse4.browse(num_links=4, sleep=0, timeout=(5*default_timeout))
    #command_sequence_browse4.dump_profile_cookies(timeout=(5*default_timeout))
    #command_sequence_browse4.dump_flash_cookies(timeout=(5*default_timeout))

    print "We will visit ", site
    manager.execute_command_sequence(command_sequence_get, index='**') # ** = synchronized browsers
    #manager.execute_command_sequence(command_sequence_browse1, index='**') # ** = synchronized browsers
    manager.execute_command_sequence(command_sequence_browse2, index='**') # ** = synchronized browsers
    #manager.execute_command_sequence(command_sequence_browse3, index='**') # ** = synchronized browsers
    #manager.execute_command_sequence(command_sequence_browse4, index='**') # ** = synchronized browsers
    
# Shuts down the browsers and waits for the data to finish logging
manager.close()
