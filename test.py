import os

from selenium import webdriver
from selenium.webdriver.firefox.options import  Options


# initializinwebdriver for Chrome
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

_dir = os.path.dirname(__file__)

# getting GeekForGeeks webpage
driver.get(f'file://{os.path.join(_dir, "index.html")}')

driver.get_screenshot_as_file("screenshot.png")