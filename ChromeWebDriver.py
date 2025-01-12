import selenium
import time
import os
import shutil
import psutil
import traceback

import seleniumwire
from seleniumwire import webdriver

from selenium.webdriver.common.proxy import Proxy, ProxyType
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random



class ChromeWebDriver:
  DRIVER_PATH = '/Downloads/scarping'
  DEBUG_PATH = '/Downloads/scarping/webdriver_debug/'

  

  def __init__(self, proxy):

    self.driver = None
    self.port = random.randint(1000,10000)
    self.error = None
    self.proxy = proxy

    # Configure Proxy Option
    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL

    # Proxy IP & Port
    prox.http_proxy = proxy
    prox.ssl_proxy = proxy

    # Configure capabilities
    capabilities = webdriver.DesiredCapabilities.CHROME
    
    self.close() # kill previous instances
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--incognito')
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument("--disable-javascript")

    chromeOptions.add_argument('--no-sandbox')
    chromeOptions.add_argument('--disable-dev-shm-usage')
    chromeOptions.add_argument('--blink-settings=imagesEnabled=false')
    chromeOptions.add_argument('--disable-infobars')
    chromeOptions.add_argument('--disable-browser-side-navigation')
    chromeOptions.add_argument('--disable-features=VizDisplayCompositor')
    chromeOptions.add_argument('--disable-gpu')
    chromeOptions.add_argument('--force-device-scale-factor=1')
    chromeOptions.add_argument('--disable-backgrounding-occluded-windows')
    chromeOptions.add_argument('--disable-extensions')
    chromeOptions.add_argument('--start-maximized')
    chromeOptions.add_argument('--ignore-certificate-errors')
    #chromeOptions.add_argument('--remote-debugging-port=' + self.port)
    chromeOptions.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
    chromeOptions.add_argument('--window-size=1280,1024')
    #chromeOptions.add_argument('--user-data-dir=/Downloads/port/' + self.port)
    chromeOptions.add_argument('--allow-running-insecure-content')
    
    chromeOptions.add_argument("window-size=1200x600")
    chromeOptions.add_argument("--disable-blink-features=AutomationControlled") 
    chromeOptions.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})

 

    chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"]) 
 
    chromeOptions.add_experimental_option("useAutomationExtension", False) 


    print('creating driver')
    options = {
        'proxy': {
            'http': 'http://' + self.proxy,
            'https': 'https://' + self.proxy,
           # 'no_proxy': 'localhost,127.0.0.1'
        },
    }
    print ('Test Selenium Options', options)
    self.driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chromeOptions,seleniumwire_options=options,desired_capabilities=capabilities)
    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    

    print('finished creating driver')
   
    self.driver.set_page_load_timeout(10)
    print('Created browser: ', self.port, self.proxy)

  def ResetCookie(self):
    if self.driver:
      self.driver.delete_all_cookies()
      time.sleep(1)

  def close(self):
    if self.driver:
      self.driver.quit()
      self.driver = None

    # kill all chrome processes w/ assigned debug port
    for retries in range(0, 5):
      try:
        for process in psutil.process_iter():
          if process.name() == 'chrome' and '--remote-debugging-port=' + self.port in process.cmdline():

            print('Terminating: ', process.pid, '--remote-debugging-port=' + self.port)
            if retries > 1:
              process.kill()
            else:
              process.terminate()
            if retries > 0:
              process.wait(5)
      except Exception as err:
        continue

 

  

  def handleException(self, method, exception):
    self.stats['exception'] += 1
    self.printStatus('[' + type(exception).__name__ +':' + method +']: ', exception, self.saveScreenshot(method + '.exception', True))
    traceback.print_exc()

  def requestUrl(self, url, condition = None, timeout = 300):
    self.stats['request_url'] += 1
    for retries in range(0, 4):
      if not self.driver or retries > 1:
        self.initialize()
      try:
        self.driver.get(url)
        if condition:
          return self.waitUntil(condition, timeout)
        else:
          return True
      except Exception as error:
        self.handleException('requestUrl', error)

  def waitUntil(self, condition, timeout = 300):
    try:
      return WebDriverWait(self.driver, timeout).until(condition)
    except Exception as error:
      print ("waitUntil Timeout")
      # self.handleException('waitUntil', error)
    return None

 
  def clickElement(self, startCondition, endCondition = None, allowUrlRefresh = True, expectNewUrl = True, timeout = 300):
    self.stats['click_element'] += 1
    oldUrl = None
    for retries in (range(0, 5) if allowUrlRefresh else range (0, 1)):
      try:
        if not oldUrl:
          oldUrl = self.driver.current_url # record original URL before click
        if oldUrl:
          if retries > 0 and allowUrlRefresh:
            self.requestUrl(oldUrl)
          element = self.waitUntil(startCondition)
          if element:
            print(self.index, ': clicking...')
            element.click()
            print(self.index, ': clicked')
            if expectNewUrl: # default: URL changes after click
              print(self.index, ': waiting for url change: ', oldUrl)
              self.waitUntil(EC.url_changes(oldUrl), timeout)
              print(self.index, ': new url', self.driver.current_url)
            if endCondition:
              print(self.index, ': waiting for end condition')
              return self.waitUntil(endCondition, timeout)
            return True
      except Exception as error:
        self.handleException('clickElement', error)
    return False

  def getElementAttribute(self, element, attribute):
    try:
      return element.get_attribute(attribute)
    except Exception as error:
      self.handleException('getElementAttribute', error)
      return ''

  def getElementText(self, element):
    try:
      return element.text
    except Exception as error:
      self.handleException('getElementAttribute', error)
      return ''

  def clickElementByXPath(self, xpath):
    try:
      element = self.driver.find_element(By.XPATH, xpath)
      return element.click()
    except Exception as error:
      self.handleException('clickElement', error)
      return ''
    
  

  def execute_script(self, script):
    try:
        self.driver.execute_script(script)
    except Exception as error:
      self.handleException('execute_script', error)
      return ''

  def getElementByXPath(self, xpath):
    try:
        element = self.driver.find_element(By.XPATH, xpath)
        return element
    except Exception as error:
      self.handleException('getElement', error)
      return ''

  def getElementsByXPath(self, xpath):
    try:
        elements = self.driver.find_elements(By.XPATH, xpath)
        return elements
    except Exception as error:
      self.handleException('getElements', error)
      return ''

  def getCurrentPage(self):
    return self.driver.title.strip() + ' [' + self.driver.current_url + ']'

  def saveScreenshot(self, filename, unique = False):
    screenshotPath = self.paths['screenshots']
    if unique:
      screenshotPath += 'S' + str(self.screenshotCount) + '_'
      self.screenshotCount += 1
    screenshotPath += filename + '.png'
    print (screenshotPath)
    try:
      self.driver.get_screenshot_as_file(screenshotPath)
      return screenshotPath
    except Exception as error:
      return '[error: ' + str(error) + ']';

  
  def getDriver(self):
    return self.driver

 
 
  def scroll_down(self, max_scroll_tries=10, step_delay=1, diff_threshold=1000, scroll_pane=None):
    """
    Scrolls down a webpage dynamically to load additional content.

    Parameters:
    - max_scroll_tries: Maximum number of scroll attempts
    - step_delay: Delay (in seconds) between scroll steps
    - diff_threshold: Minimum difference in content size to detect new content
    - scroll_pane: Optional WebElement for a specific scrollable container

    Returns:
    - True if scrolling loaded new content, False otherwise.
    """
    try:
        before_content =self.driver.page_source
        scroll_attempts = 0
        scrolled = False

        while scroll_attempts < max_scroll_tries:
            scroll_attempts += 1
            print(f"Scroll attempt {scroll_attempts}...")

            # Scroll logic
            if scroll_pane:
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_pane)
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(step_delay)  # Allow time for content to load

            after_content = self.driver.page_source
            diff_size = len(after_content) - len(before_content)

            print(f"Diff size: {diff_size} | Threshold: {diff_threshold}")

            if diff_size > diff_threshold:
                before_content = after_content
                scrolled = True
                scroll_attempts = 0  # Reset attempts if new content is found
            else:
                break

        return scrolled

    except Exception as e:
        print("Error during scroll_down:", traceback.format_exc())
        return False
