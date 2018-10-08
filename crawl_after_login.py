from __future__ import absolute_import
from automation import TaskManager, CommandSequence
from six.moves import range
from crawl_sites import SubSites

# The list of sites that we wish to crawl
NUM_BROWSERS = 1

global sub_sites_instance
sub_sites_instance = SubSites()
sites_to_crawl = sub_sites_instance.sites_1000_DE
#sites_to_crawl = ['http://www.facebook.com']

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
    browser_params[i]['profile_archive_dir'] = 'Output/Profiles/Facebook_2'
    #browser_params[i]['profile_archive_dir'] = 'Output/Profile'
    # if profile should be loaded
    #browser_params[i]['profile_tar'] = '/home/OpenWPM/Output/Profiles/Facebook'
    browser_params[i]['profile_tar'] = 'Output/Profiles/Facebook_2'

    #self written
    browser_params[i]['scroll_down'] = False
    browser_params[i]['login'] = False
    browser_params[i]['execute_tshark'] = False

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = 'Output/Data'
manager_params['log_directory'] = 'Output/Data'
#manager_params['database_name'] = 'output.sqlite'

default_timeout = 60
default_sleep = 5

manager = TaskManager.TaskManager(manager_params, browser_params)

# Visits the sites with all browsers simultaneously
for site in sites_to_crawl:
    # define crawl actions
    command_sequence_get1 = CommandSequence.CommandSequence(site, reset=False)
    command_sequence_get1.get(step=0, sleep=default_sleep, timeout=default_timeout)
    command_sequence_get1.dump_profile_cookies(timeout=default_timeout)
    command_sequence_get1.dump_flash_cookies(timeout=default_timeout)

    manager.execute_command_sequence(command_sequence_get1, index='**') # ** = synchronized browsers
    
# Shuts down the browsers and waits for the data to finish logging
manager.close()
 