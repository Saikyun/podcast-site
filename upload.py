import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pyautogui
import json
import click
import episode_parser as ep
import re


def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 0)
    return driver
 
def login_libsyn(login, passwd):
    driver = init_driver()
    driver.get("https://login.libsyn.com/")
    try:
        email = driver.find_element_by_id("email")
        email.send_keys(login)
        pwd = driver.wait.until(EC.element_to_be_clickable(
            (By.NAME, "password")))
        pwd.send_keys(passwd)
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type = 'submit']")))
        button.submit()
    except TimeoutException:
        print("Box or Button not found in google.com")
    return driver


def upload(title, description, date, login, passwd):
    driver = login_libsyn(login, passwd)
    driver.get("https://four.libsyn.com/content_edit/index/mode/episode")
    details_tab_xpath = "//node()[@data-label='Details']"
    details_tab = driver.wait.until(EC.element_to_be_clickable((By.XPATH, details_tab_xpath)))
    details_tab.click()
    title_field = driver.wait.until(EC.element_to_be_clickable((By.ID, "item_title")))
    title = title
    title_field.send_keys(title)

    src_btn = driver.wait.until(EC.element_to_be_clickable((By.ID, "mceu_18")))
    src_btn.click()

    iframe = driver.find_element_by_xpath("//iframe[@src='https://four.libsyn.com/lib/tinymce_4-6-5/plugins/codemirror/source.html']")
    driver.switch_to.frame(iframe)
    time.sleep(3)
    driver.execute_script('codemirror.getDoc().setValue({})'.format(json.dumps(description)));
    time.sleep(3)
    driver.switch_to.default_content()
    ok_btn = driver.wait.until(EC.element_to_be_clickable((By.ID, "mceu_44")))
    ok_btn.click()
    scheduling_xpath = "//node()[@data-label='Scheduling']"
    scheduling_tab = driver.wait.until(EC.element_to_be_clickable((By.XPATH, scheduling_xpath)))
    scheduling_tab.click()
    time.sleep(1)
    basic_release_xpath = "//node()[@aria-controls='release_scheduler_tab-basic']"
    basic_release_tab = driver.wait.until(EC.element_to_be_clickable((By.XPATH, basic_release_xpath)))
    basic_release_tab.click()
    time.sleep(1)
    new_release_option_id = 'set_basic_release_date-2'
    new_release_option = driver.wait.until(EC.element_to_be_clickable((By.ID, new_release_option_id)))
    new_release_option.click()
    time.sleep(1)
    date_id = "basic_release_date_date"
    time_id = "basic_release_date_time_input"
    javascript = "document.getElementById('{}').setAttribute('value', '01:00 AM')".format(time_id)
    driver.execute_script(javascript);
    date_string = date.strftime('%Y-%m-%d')
    javascript = "document.getElementById('{}').setAttribute('value', '{}')".format(date_id, date_string)
    driver.execute_script(javascript);


    media_xpath = "//node()[@data-label='Media']"
    media_tab = driver.wait.until(EC.element_to_be_clickable((By.XPATH, media_xpath)))
    media_tab.click()
    time.sleep(1)

    button = driver.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//text()[contains(.,'Add Media File')]/../..")))
    button.click()
    time.sleep(2)
    button = driver.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//text()[contains(.,'Upload from Hard Drive')]/../..")))
    button.click()
 
def extract_file_details(title, u, p):
    driver = login_libsyn(u, p)
    #url = "https://four.libsyn.com/content/previously-published"
    url = "https://four.libsyn.com/content/scheduled-posts"
    driver.get(url)

    xpath = "//node()[contains(@data-sort-val,'{}')]//text()[contains(.,'Link/Embed')]/../..".format(title)
    btn = driver.find_element_by_xpath(xpath)
    btn.click()
    time.sleep(2)
    url = driver.wait.until(EC.element_to_be_clickable((By.XPATH,"//text()[contains(.,'Direct Download')]/../..//input"))).get_attribute('value')
    dir_url = driver.wait.until(EC.element_to_be_clickable((By.XPATH,"//text()[contains(.,'Libsyn Directory URL')]/../..//input"))).get_attribute('value')
    pattern = r'.*/id/(\d*)'
    libsyn_id = re.compile(pattern).match(dir_url).group(1)
    return url, libsyn_id

def replace(param, value, number):
    regex = r"{}.*=".format(param)
    replacement = '{} ="{}"\n'.format(param, value)
    path = ep.episode_file_path(number)
    program = re.compile(regex)
    with open(path,'r') as f:
        newlines = []
        for line in f.readlines():
            if program.match(line):
                newlines.append(replacement)
            else:
                newlines.append(line)
    with open(path, 'w') as f:
        for line in newlines:
            f.write(line)


@click.command() 
@click.option('-u', prompt=True)
@click.option('-p', prompt=True, hide_input=True)
@click.argument('number')
@click.argument('feature')
def start(u, p, number, feature):
    title = ep.extract_title(number)
    if feature == 'extract':
        url, libsyn_id = extract_file_details(title, u, p)
        replace('audiofile', url, number)
        replace('libsynid', libsyn_id, number)
    elif feature == 'upload':
        description = ep.extract_description(number)
        date = ep.extract_date(number)
        upload(title, description, date, u, p)
    input("Press Enter to continue...")


if __name__ == "__main__":
    start()
