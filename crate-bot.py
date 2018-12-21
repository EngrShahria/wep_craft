__author__ = "mdn522"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "3.0.0"
__maintainer__ = "mdn522"
__status__ = "beta"

import os
import sys
import json
import re
import signal
import time
import traceback
from datetime import datetime, timedelta

import requests

import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

auto_open = True
crate_blacklist = []
auto_claim = True
sync_code = True
check_every_x_seconds = 30
log_to_file = True

driver = None
last_time_loaded_page = 0  # useless

class MyComNotLoggedIn(Exception):
    pass

class CrateStartFailed(Exception):
    pass

class CrateOpenFailed(Exception):
    pass


# thanks to https://stackoverflow.com/a/46276781/4854605
class js_variable_evals_to_true(object):
    def __init__(self, variable):
        self.variable = variable
    def __call__(self, driver):
        return driver.execute_script("return {0};".format(self.variable))


def reload_settings():
    try:
        url = os.environ.get('PA_URL') + '/files/get'
        user = os.environ.get('PA_USER')
        key = os.environ.get('PA_KEY')

        obj = requests.get(url, params={'filename': '{}_crafting_settings.json'.format(user), 'key':key}).json()
        for k, v in obj.items():
            globals()[k] = v

    except Exception as e:
        print('reload_settings()', e)


# Print with datetime
def printwd(msg, show=True, log=True):
    s = datetime.today().strftime("%Y-%m-%d %I:%M %p") + ': ' + msg
    key = os.environ.get('PA_KEY')

    if show:
        print(s)

    if log:
        url = os.environ.get('PA_URL')
        user = os.environ.get('PA_USER')
        try:
            requests.post(url + 'log', {'user': '{}_crafting'.format(user), 'message': s}, params={'key': key})
        except Exception as e:
            print('printwd()', e)


def get_file(filename):
    url = os.environ.get('PA_URL')
    key = os.environ.get('PA_KEY')
    return requests.get(url + 'files/get',
                        params={'key': key, 'filename': filename})

def save_file(filename, content):
    url = os.environ.get('PA_URL')
    key = os.environ.get('PA_KEY')

    return requests.post(url + 'files/put', 
                        {'filename': filename, 'content': content},
                        params={'key': key}).json()

def save_cookies(driver):
    user = os.environ.get('PA_USER')
    return save_file(filename='{}_wf_cookies.json'.format(user), content=json.dumps(driver.get_cookies())).json()


def load_cookies(driver):
    user = os.environ.get('PA_USER')
    resp = get_file(filename='{}_wf_cookies.json'.format(user))

    if resp.status_code == 200:
        driver.get('https://wf.my.com/')
        cookies = resp.json()

        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    
    return False


def run_browser():
    print('Running browser')

    if 'driver' in globals():
        try:
            if hasattr(driver, 'quit'):
                print('variable "driver" already defined. trying to quit it')
                driver.quit()
        except Exception as e:
            print(type(e))
            print('run_browser()', e)

    GOOGLE_CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver" 

    options = webdriver.ChromeOptions()

    cap = DesiredCapabilities.CHROME

    cap['loggingPrefs'] = { 'browser':'ALL' }

    options.binary_location = GOOGLE_CHROME_BIN

    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("user-data-dir=chrome_profile")

    options.add_argument('--disable-web-security ')
    options.add_argument('--allow-running-insecure-content')

    globals()['driver'] = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options, desired_capabilities=cap)


def load_page():
    driver.get('https://wf.my.com/create')

    # ToDo: DRY
    driver.execute_script('''	
    var script = document.createElement("script");
    script.src = "https://code.jquery.com/jquery-3.3.1.min.js";
    document.head.appendChild(script);

    var script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/js-cookie@2/src/js.cookie.min.js";
    document.head.appendChild(script);
    ''')

    last_time_loaded_page = int(datetime.now().timestamp())


def update_mg_token():
    global driver
    driver.execute_script('''
    Cookies.remove("mg_token", {path: "/"});
    $.get("https://wf.my.com/minigames/user/info", function(data) {
        Cookies.set("mg_token", data.data.token, {expires: 7, path: '/'});
    });

    ''')


def is_logged_in(on_exc_return_false=False):
    try:
        driver.get('https://wf.my.com/dynamic/auth/?a=checkuser')
        obj_pattern = r'(.*)<body>(.*)<\/body>'
        obj_json = re.match(obj_pattern, driver.page_source).group(2)
        obj = json.loads(obj_json)

        return bool(obj['enable'])
    except Exception as e:
        if on_exc_return_false:
            return False
        else:
            raise e


def prompt_login_spam():
    while not is_logged_in(True):
        print('Still logged out. Please update cookie file. sleeping for 30 seconds and will load cookies...')
        time.sleep(30)
        load_cookies(driver)
    
    print('Logged in again')

try:
    reload_settings()

    run_browser()

    if not is_logged_in():
        loaded_cookies = load_cookies(driver)

        prompt_login_spam()

    load_page()

except Exception as e:
    print('\n' * 2)
    print('-' * 32)
    print('''RUNTIME ERROR!\n''')
    print('Please contact facebook.com/mdn522\n')
    print('An error "{0}" has occured.'.format(type(e)))
    print(e)
    traceback.print_tb(e.__traceback__)

    driver.quit()
    sys.exit(0)


def signal_handler(signal, frame):
    global driver
    try:
        driver.quit()
    except:
        pass

    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)


had_exception = False

print('Bot started...\n')
while True:
    try:
        reload_settings()
    except Exception as e:
        print('Failed to reload settings. Using old settings', type(e), e)

    try:
        if had_exception:
            load_page()
            had_exception = False

        # https://wf.my.com/minigames/bp4/craft/user-craft-info
        js = '''
        window.chests = null;
        async function job() {
            var resp = await $.get("https://wf.my.com/minigames/craft/api/user-info");
            window.chests = resp
        }
        job();'''

        driver.execute_script(js)

        obj = WebDriverWait(driver, 10).until(js_variable_evals_to_true("window.chests"))
        if len(obj['data']['user_chests']) != 0:
            for chest in obj['data']['user_chests']:
                if str(chest['state']) == 'new':
                    if not (auto_open and chest['type'] not in crate_blacklist):
                        continue

                    data = json.dumps({'chest_id': chest['id']})

                    # https://wf.my.com/minigames/bp4/craft/start
                    js = '''
                    window.start_resp = null;
                    async function job() {
                        var resp = await $.post("https://wf.my.com/minigames/craft/api/start", data=%s);
                        window.start_resp = resp;
                    }
                    job();''' % (data,)

                    driver.execute_script(js)

                    try:
                        start_resp = WebDriverWait(driver, 5).until(js_variable_evals_to_true("window.start_resp"))
                    except selenium.common.exceptions.TimeoutException:
                        raise CrateStartFailed

                    if start_resp['state'] == "Success":
                        printwd("New " + chest['type'] + " crate available")

                elif chest['ended_at'] < 0:
                    if not auto_claim:
                        continue

                    data = json.dumps({'chest_id': chest['id'], 'paid': 0})

                    # https://wf.my.com/minigames/bp4/craft/open
                    js = '''
                    window.open_resp = null;
                    async function job() {
                        var resp =  await $.post("https://wf.my.com/minigames/craft/api/open", data=%s);
                        window.open_resp = resp;
                    }
                    job();''' % (data,)

                    driver.execute_script(js)

                    try:
                        open_resp = WebDriverWait(driver, 5).until(js_variable_evals_to_true("window.open_resp"))
                    except selenium.common.exceptions.TimeoutException:
                        raise CrateOpenFailed

                    printwd('Opening ' + chest['type'] + ' crate', log=False)
                    printwd('Reward: Level: {} | Amount: {}'.format(open_resp['data']['resource']['level'],
                                                                    open_resp['data']['resource']['amount']), log=False)

                    printwd('Opened {} crate -> Level: {} | Amount: {}'.format(chest['type'],
                                                                               open_resp['data']['resource']['level'],
                                                                               open_resp['data']['resource']['amount']),
                            show=False)

                    time.sleep(0.5)

    except Exception as e:
        skip_wait = False
        had_exception = True

        if type(e) == CrateStartFailed or type(e) == CrateOpenFailed:
            update_mg_token()
            skip_wait = True
        else:
            print(type(e))
            print(e)
            traceback.print_exc()
            if type(e) == selenium.common.exceptions.WebDriverException:
                run_browser()
                skip_wait = True
            else:
                first_login_check = True
                login_check_failed = False
                while first_login_check or login_check_failed:
                    first_login_check = False
                    try:
                        if not is_logged_in(True):
                            prompt_login_spam()
                        login_check_failed = False
                    except Exception as login_exc:
                        print("Can't check if user is logged in or not. will check again after 30 seconds")
                        login_check_failed = True
                        time.sleep(30)

        if skip_wait:
            time.sleep(1)
            continue
        pass
    else:
        pass
    finally:
        pass

    time.sleep(check_every_x_seconds)

# Quit the fucking browser.
driver.quit()