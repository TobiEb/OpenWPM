# -*- coding: utf-8 -*-

from __future__ import absolute_import
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from hashlib import md5
from glob import glob
from PIL import Image
import traceback
import random
import json
import time
import sys
import gzip
import os

from ..SocketInterface import clientsocket
from ..MPLogger import loggingclient
from .utils.lso import get_flash_cookies
from .utils.firefox_profile import get_cookies
from .utils.webdriver_extensions import (scroll_down,
                                         scroll_to_bottom, is_loaded,
                                         wait_until_loaded,
                                         get_intra_links,
                                         my_get_intra_stable_link,
                                         my_get_intra_link,
                                         is_active,
                                         execute_in_all_frames,
                                         execute_script_with_retry)
from six.moves import range
import six

import subprocess # to execute shell script for tshark
from tld import get_tld
import sys, os
from crawl_sites import SubSites

# Constants for bot mitigation
NUM_MOUSE_MOVES = 10  # Times to randomly move the mouse
RANDOM_SLEEP_LOW = 1  # low (in sec) for random sleep between page loads
RANDOM_SLEEP_HIGH = 7  # high (in sec) for random sleep between page loads

global browser_commands_subsite_instance
browser_commands_subsite_instance = SubSites()

def bot_mitigation(webdriver):
    """ performs three optional commands for bot-detection
    mitigation when getting a site """

    # bot mitigation 1: move the randomly around a number of times
    window_size = webdriver.get_window_size()
    num_moves = 0
    num_fails = 0
    while num_moves < NUM_MOUSE_MOVES + 1 and num_fails < NUM_MOUSE_MOVES:
        try:
            if num_moves == 0:  # move to the center of the screen
                x = int(round(window_size['height']/2))
                y = int(round(window_size['width']/2))
            else:  # move a random amount in some direction
                move_max = random.randint(0, 500)
                x = random.randint(-move_max, move_max)
                y = random.randint(-move_max, move_max)
            action = ActionChains(webdriver)
            action.move_by_offset(x, y)
            action.perform()
            num_moves += 1
        except MoveTargetOutOfBoundsException:
            num_fails += 1
            pass

    # bot mitigation 2: scroll in random intervals down page
    scroll_down(webdriver)

    # bot mitigation 3: randomly wait so page visits happen with irregularity
    time.sleep(random.randrange(RANDOM_SLEEP_LOW, RANDOM_SLEEP_HIGH))


def close_other_windows(webdriver):
    """
    close all open pop-up windows and tabs other than the current one
    """
    main_handle = webdriver.current_window_handle
    windows = webdriver.window_handles
    if len(windows) > 1:
        for window in windows:
            if window != main_handle:
                webdriver.switch_to_window(window)
                webdriver.close()
        webdriver.switch_to_window(main_handle)


def tab_restart_browser(webdriver):
    """
    kills the current tab and creates a new one to stop traffic
    """
    # note: this technically uses windows, not tabs, due to problems with
    # chrome-targeted keyboard commands in Selenium 3 (intermittent
    # nonsense WebDriverExceptions are thrown). windows can be reliably
    # created, although we do have to detour into JS to do it.
    close_other_windows(webdriver)

    if webdriver.current_url.lower() == 'about:blank':
        return

    # Create a new window.  Note that it is not practical to use
    # noopener here, as we would then be forced to specify a bunch of
    # other "features" that we don't know whether they are on or off.
    # Closing the old window will kill the opener anyway.
    webdriver.execute_script("window.open('')")

    # This closes the _old_ window, and does _not_ switch to the new one.
    webdriver.close()

    # The only remaining window handle will be for the new window;
    # switch to it.
    assert len(webdriver.window_handles) == 1
    webdriver.switch_to_window(webdriver.window_handles[0])


def get_website(url, step, sleep, visit_id, webdriver,
                browser_params, extension_socket):

    """
    goes to <url> using the given <webdriver> instance
    """

    if browser_params['execute_tshark']:
        # set readable url name to for tshark file names
        if 'http' in url:
            r = url.replace('://', '/')
            p = r.split('/')
            o = p[1]
            if 'www' in o:
                w = o.split('.')
                f = w[1]
                subprocess.call(['/home/OpenWPM/start_tshark.sh', str(f), str(visit_id)])
        else:
            subprocess.call(['/home/OpenWPM/start_tshark.sh', str(url), str(visit_id)])

    if 'sub1' in url or 'sub2' in url or 'sub3' in url or 'sub4' in url:
        print browser_commands_subsite_instance.sub_sites
        try:
            if 'http' in browser_commands_subsite_instance.sub_sites[step-1]:
                url = browser_commands_subsite_instance.sub_sites[step-1]
                print "new url: ", url
            else:
                print "im else nach timeout exception zb"
                step = 0
                tld_url = url[:-5]
                # set to base domain and get subsites again
                url = tld_url
                print url
        except TypeError:
            step = 0
            # set to 0, so we visit top level domain and then get intra links again
            raise ValueError("No links found. Browsing not possible!")

        # if len(browser_commands_subsite_instance.sub_sites) > 0 and browser_commands_subsite_instance.sub_sites is not None and browser_commands_subsite_instance.sub_sites[step-1] is not None:

    tab_restart_browser(webdriver)

    if extension_socket is not None:
        extension_socket.send(visit_id)

    # Execute a get through selenium
    try:
        webdriver.get(url)
    except TimeoutException:
        pass

    # if step == 0:
        # get 4 sub_sites and set them to visit now
        # links = []
        # for i in range(4):
        #     el = my_get_intra_link(webdriver, url)
        #     links.append(el)
        # browser_commands_subsite_instance.sub_sites = links

    # Sleep after get returns
    time.sleep(sleep)

    # Close modal dialog if exists
    try:
        WebDriverWait(webdriver, .5).until(EC.alert_is_present())
        alert = webdriver.switch_to_alert()
        alert.dismiss()
        time.sleep(1)
    except TimeoutException:
        pass

    if browser_params['scroll_down']:
        my_scroll_down(webdriver)
    #login
    if browser_params['login']:
        if "facebook" in url:
            try:
                email = webdriver.find_element_by_id("email")
                pw = webdriver.find_element_by_id("pass")
                email.send_keys("admin")
                pw.send_keys("admin")
                webdriver.find_element_by_id("loginbutton").click()
                time.sleep(10)
            except Exception:
                pass
        elif "accounts.google" in url:
            time.sleep(5)
            email = webdriver.find_element_by_id("identifierId")
            email.send_keys("admin")
            webdriver.find_element_by_id("identifierNext").click()
            time.sleep(10)
            pw = webdriver.find_element_by_id("password")
            pw.send_keys("admin")
            webdriver.find_element_by_id("passwordNext").click()
            time.sleep(10)
        elif "amazon" in url:
            try:
                email = webdriver.find_element_by_id("ap_email")
                email.send_keys("admin")
                webdriver.find_element_by_id("continue").click()
                time.sleep(10)
                pw = webdriver.find_element_by_id("ap_password")
                pw.send_keys("admin")
                webdriver.find_element_by_id("signInSubmit").click()
                time.sleep(10)
            except Exception:
                pass

    close_other_windows(webdriver)

def extract_links(webdriver, browser_params, manager_params):
    link_elements = webdriver.find_elements_by_tag_name('a')
    link_urls = set(element.get_attribute("href") for element in link_elements)

    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])
    create_table_query = ("""
    CREATE TABLE IF NOT EXISTS links_found (
      found_on TEXT,
      location TEXT
    )
    """, ())
    sock.send(create_table_query)

    if len(link_urls) > 0:
        current_url = webdriver.current_url
        insert_query_string = """
        INSERT INTO links_found (found_on, location)
        VALUES (?, ?)
        """
        for link in link_urls:
            sock.send((insert_query_string, (current_url, link)))

    sock.close()

def browse_website(url, num_links, sleep, visit_id, webdriver,
                   browser_params, manager_params, extension_socket):
    """Calls get_website before visiting <num_links> present on the page.

    Note: the site_url in the site_visits table for the links visited will
    be the site_url of the original page and NOT the url of the links visited.
    """

    # execute tshark is not necessary here, since it is executed in the get request which comes here as well

    # First get the site
    # set step (second parameter) to 0 will lead to generating new sub_sites
    get_website(url, 0, sleep, visit_id, webdriver,
                browser_params, extension_socket)

    # Connect to logger
    logger = loggingclient(*manager_params['logger_address'])

    for i in range(num_links):
        try:
            logger.info("BROWSER %i: visiting internal link by get %s" % (browser_params['crawl_id'], browser_commands_subsite_instance.sub_sites[i]))
            # Execute a get through selenium
            webdriver.get(browser_commands_subsite_instance.sub_sites[i])
        except TimeoutException:
            logger.info("im browse Timeout exception")
            pass
        except StaleElementReferenceException:
            logger.info("beim getten im stale exception")
            pass
        time.sleep(sleep)


def dump_flash_cookies(start_time, visit_id, webdriver, browser_params,
                       manager_params):
    """ Save newly changed Flash LSOs to database

    We determine which LSOs to save by the `start_time` timestamp.
    This timestamp should be taken prior to calling the `get` for
    which creates these changes.
    """
    # Set up a connection to DataAggregator
    tab_restart_browser(webdriver)  # kills window to avoid stray requests
    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])

    # Flash cookies
    flash_cookies = get_flash_cookies(start_time)
    for cookie in flash_cookies:
        query = ("INSERT INTO flash_cookies (crawl_id, visit_id, domain, "
                 "filename, local_path, key, content) VALUES (?,?,?,?,?,?,?)",
                 (browser_params['crawl_id'], visit_id, cookie.domain,
                  cookie.filename, cookie.local_path, cookie.key,
                  cookie.content))
        sock.send(query)

    # Close connection to db
    sock.close()


def dump_profile_cookies(start_time, visit_id, webdriver,
                         browser_params, manager_params):

    """ Save changes to Firefox's cookies.sqlite to database

    We determine which cookies to save by the `start_time` timestamp.
    This timestamp should be taken prior to calling the `get` for
    which creates these changes.

    Note that the extension's cookieInstrument is preferred to this approach,
    as this is likely to miss changes still present in the sqlite `wal` files.
    This will likely be removed in a future version.
    """
    # Set up a connection to DataAggregator
    tab_restart_browser(webdriver)  # kills window to avoid stray requests
    sock = clientsocket()
    sock.connect(*manager_params['aggregator_address'])

    # Cookies
    rows = get_cookies(browser_params['profile_path'], start_time)
    if rows is not None:
        for row in rows:
            query = ("INSERT INTO profile_cookies (crawl_id, visit_id, "
                     "baseDomain, name, value, host, path, expiry, accessed, "
                     "creationTime, isSecure, isHttpOnly) VALUES "
                     "(?,?,?,?,?,?,?,?,?,?,?,?)", (browser_params['crawl_id'],
                                                   visit_id) + row)
            sock.send(query)

    # Close connection to db
    sock.close()


def save_screenshot(visit_id, crawl_id, driver, manager_params, suffix=''):
    """ Save a screenshot of the current viewport"""
    if suffix != '':
        suffix = '-' + suffix

    urlhash = md5(driver.current_url.encode('utf-8')).hexdigest()
    outname = os.path.join(manager_params['screenshot_path'],
                           '%i-%s%s.png' %
                           (visit_id, urlhash, suffix))
    driver.save_screenshot(outname)


def _stitch_screenshot_parts(visit_id, crawl_id, logger, manager_params):
    # Read image parts and compute dimensions of output image
    total_height = -1
    max_scroll = -1
    max_width = -1
    images = dict()
    parts = list()
    for f in glob(os.path.join(manager_params['screenshot_path'],
                               'parts',
                               '%i*-part-*.png' % visit_id)):

        # Load image from disk and parse params out of filename
        img_obj = Image.open(f)
        width, height = img_obj.size
        parts.append((f, width, height))
        outname, _, index, curr_scroll = os.path.basename(f).rsplit('-', 3)
        curr_scroll = int(curr_scroll.split('.')[0])
        index = int(index)

        # Update output image size
        if curr_scroll > max_scroll:
            max_scroll = curr_scroll
            total_height = max_scroll + height

        if width > max_width:
            max_width = width

        # Save image parameters
        img = {}
        img['object'] = img_obj
        img['scroll'] = curr_scroll
        images[index] = img

    # Output filename same for all parts, so we can just use last filename
    outname = outname + '.png'
    outname = os.path.join(manager_params['screenshot_path'], outname)
    output = Image.new('RGB', (max_width, total_height))

    # Compute dimensions for output image
    for i in range(max(images.keys())+1):
        img = images[i]
        output.paste(im=img['object'], box=(0, img['scroll']))
        img['object'].close()
    try:
        output.save(outname)
    except SystemError:
        logger.error(
            "BROWSER %i: SystemError while trying to save screenshot %s. \n"
            "Slices of image %s \n Final size %s, %s." %
            (crawl_id, outname, '\n'.join([str(x) for x in parts]),
             max_width, total_height)
        )
        pass


def screenshot_full_page(visit_id, crawl_id, driver, manager_params,
                         suffix=''):
    logger = loggingclient(*manager_params['logger_address'])

    outdir = os.path.join(manager_params['screenshot_path'], 'parts')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    if suffix != '':
        suffix = '-' + suffix
    urlhash = md5(driver.current_url.encode('utf-8')).hexdigest()
    outname = os.path.join(outdir, '%i-%s%s-part-%%i-%%i.png' %
                           (visit_id, urlhash, suffix))

    try:
        part = 0
        max_height = execute_script_with_retry(
            driver, 'return document.body.scrollHeight;')
        inner_height = execute_script_with_retry(
            driver, 'return window.innerHeight;')
        curr_scrollY = execute_script_with_retry(
            driver, 'return window.scrollY;')
        prev_scrollY = -1
        driver.save_screenshot(outname % (part, curr_scrollY))
        while ((curr_scrollY + inner_height) < max_height
               and curr_scrollY != prev_scrollY):

            # Scroll down to bottom of previous viewport
            try:
                driver.execute_script('window.scrollBy(0, window.innerHeight)')
            except WebDriverException:
                logger.info(
                    "BROWSER %i: WebDriverException while scrolling, "
                    "screenshot may be misaligned!" % crawl_id)
                pass

            # Update control variables
            part += 1
            prev_scrollY = curr_scrollY
            curr_scrollY = execute_script_with_retry(
                driver, 'return window.scrollY;')

            # Save screenshot
            driver.save_screenshot(outname % (part, curr_scrollY))
    except WebDriverException:
        excp = traceback.format_exception(*sys.exc_info())
        logger.error(
            "BROWSER %i: Exception while taking full page screenshot \n %s" %
            (crawl_id, ''.join(excp)))
        return

    _stitch_screenshot_parts(visit_id, crawl_id, logger, manager_params)


def dump_page_source(visit_id, driver, manager_params, suffix=''):
    if suffix != '':
        suffix = '-' + suffix

    outname = md5(driver.current_url.encode('utf-8')).hexdigest()
    outfile = os.path.join(manager_params['source_dump_path'],
                           '%i-%s%s.html' % (visit_id, outname, suffix))

    with open(outfile, 'wb') as f:
        f.write(driver.page_source.encode('utf8'))
        f.write(b'\n')


def recursive_dump_page_source(visit_id, driver, manager_params, suffix=''):
    """Dump a compressed html tree for the current page visit"""
    if suffix != '':
        suffix = '-' + suffix

    outname = md5(driver.current_url.encode('utf-8')).hexdigest()
    outfile = os.path.join(manager_params['source_dump_path'],
                           '%i-%s%s.json.gz' % (visit_id, outname, suffix))

    def collect_source(driver, frame_stack, rv={}):
        is_top_frame = len(frame_stack) == 1

        # Gather frame information
        doc_url = driver.execute_script("return window.document.URL;")
        if is_top_frame:
            page_source = rv
        else:
            page_source = dict()
        page_source['doc_url'] = doc_url
        source = driver.page_source
        if type(source) != six.text_type:
            source = six.text_type(source, 'utf-8')
        page_source['source'] = source
        page_source['iframes'] = dict()

        # Store frame info in correct area of return value
        if is_top_frame:
            return
        out_dict = rv['iframes']
        for frame in frame_stack[1:-1]:
            out_dict = out_dict[frame.id]['iframes']
        out_dict[frame_stack[-1].id] = page_source

    page_source = dict()
    execute_in_all_frames(driver, collect_source, {'rv': page_source})

    with gzip.GzipFile(outfile, 'wb') as f:
        f.write(json.dumps(page_source).encode('utf-8'))

def my_scroll_down(webdriver):
    scroll_to_bottom(webdriver)

def stop_tshark(webdriver):
    subprocess.call(['/home/OpenWPM/stop_tshark.sh'])
