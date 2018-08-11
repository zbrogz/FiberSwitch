from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from time import sleep
from time import time
import _thread
import logging
from flask import Flask, request


class FiberSwitch:
    EMAIL = 'email@email.com'
    PASSWORD = 'password'

    def __init__(self):
        self.driver = None
        self.wait = None

    def click(self, css_selector):
        for _ in range(0, 5):
            try:
                self.driver.find_element_by_css_selector(css_selector).click()
                logging.info("SUCCESS. Clicked on {}".format(css_selector))
                sleep(2)
                return
            except Exception as err:
                logging.info("No click error: {}".format(err))
                pass
            sleep(2)

    def change_plan(self):
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        profile = webdriver.FirefoxProfile()
        profile.native_events_enabled = False
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get("https://fiber.google.com/myfiber/")
        # Enter username
        self.driver.find_element_by_css_selector(
            '#identifierId').send_keys(self.EMAIL)
        # Click next
        self.click('#identifierNext')
        # Enter password
        self.driver.find_element_by_css_selector(
            '#password input').send_keys(self.PASSWORD)
        # Click next
        self.click('#passwordNext > content > span')
        # Click on manage plan
        self.click('button.manage-plan')
        # Click on change plan
        self.click('button.change-plan')

    def accept_plan(self):
        self.click('ul.terms-and-conditions > li:nth-child(1)')
        self.click('ul.terms-and-conditions > li:nth-child(2)')
        self.click('ul.terms-and-conditions > li:nth-child(3) span')
        self.click('button.continue-button')
        sleep(10)

    def choose_fiber_free(self):
        """ Switches to free (5 Mbps) plan """
        try:
            self.change_plan()
            # Click on one more plan
            self.click(
                "select-plan-step > div > div > div.hidden-items-label > span")
            # Click on Basic Internet
            self.click('select-plan-item > li > label[for="plan-free"]')
            # Click on continue
            self.click('button.continue-button')
            # Click on continue
            self.click('button.continue-button')
            self.accept_plan()
        except Exception as err:
            logging.info("Error: {}".format(err))
            pass
        finally:
            if self.driver:
                self.driver.quit()
            if self.display:
                self.display.stop()

    def choose_fiber_100(self):
        """ Switches to fast (100 Mbps) plan for 7¢ per hour """
        try:
            self.change_plan()
            logging.info("About to click on plan")
            # Click on 100 Mbps plan
            self.click('select-plan-item:nth-child(3) > li > label')
            # Click on continue
            self.click('button.continue-button')
            # Click on continue
            self.click('button.continue-button')
            # Click on continue
            logging.info("About to click continue again")
            self.click('button.continue-button')
            self.accept_plan()
        except Exception as err:
            logging.info("Error: {}".format(err))
            pass
        finally:
            if self.driver:
                self.driver.quit()
            if self.display:
                self.display.stop()

    def speed_boost(self):
        """ Turns fast internet on for 3 hours (total cost = 21¢) """
        # TODO: Parameterize this for variable times
        self.choose_fiber_100()
        # 3 hours
        sleep(10800)
        self.choose_fiber_free()


app = Flask(__name__)


@app.route('/api/free', methods=['GET', 'POST'])
def free():
    logging.info(request.headers)
    logging.info(request.data)
    try:
        fs = FiberSwitch()
        # fs.choose_fiber_free()
        _thread.start_new_thread(fs.choose_fiber_free, ())
    except Exception as err:
        logging.info(err)
        return err
    return "OK"


@app.route('/api/fast', methods=['GET', 'POST'])
def fast():
    # TODO: Remove GET requests
    logging.info(request.headers)
    logging.info(request.data)
    try:
        fs = FiberSwitch()
        # fs.choose_fiber_100()
        _thread.start_new_thread(fs.speed_boost, ())
    except Exception as err:
        logging.info(err)
        return err
    return "OK"

logging.basicConfig(filename='fiber_switch.log',level=logging.DEBUG)
app.run(host='0.0.0.0', debug=False)
