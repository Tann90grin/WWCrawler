from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException 
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import time
import os

# a flag configures which 2FA method selenium is going to use, use for dev only -yt
isUsingDuoPush = True

load_dotenv()
passcode = os.getenv('passcode')
email = os.getenv('email')
password = os.getenv('password')

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Initialize the driver, the option configures the browser to headless, comment one out -yt
# driver = webdriver.Chrome(options=chrome_options) 
driver = webdriver.Chrome()

driver.get("https://waterlooworks.uwaterloo.ca/")

driver.find_element(by=By.CLASS_NAME, value="btn--landing").click()
emailInput = driver.find_element(by=By.ID, value="userNameInput").send_keys(email)
nextButton = driver.find_element(by=By.ID, value="nextButton").click()
driver.find_element(by=By.ID, value="passwordInput").send_keys(password)
driver.find_element(by=By.ID, value="submitButton").click()
driver.implicitly_wait(8)

if(isUsingDuoPush):
    #Waiting for the user 
    wait = WebDriverWait(driver, 60)
    try:
        # Wait for the condition where h1 is either not present or its text is not one of the specified strings
        wait.until_not(lambda driver: (
            (lambda: driver.find_element(By.ID, "header-text").text in ["Open Duo Mobile", "Check for a Duo Push"])() if driver.find_elements(By.ID, "header-text") else False
        ))
        print("Condition met: h1 is either not present or its text is no longer the specified strings.")
    except TimeoutException:
        print("Timed out: h1 still exists with the specified text.")
        exit()
else:
    #Use Passcode Authentication
    driver.find_element(by=By.XPATH, value='/html/body/div/div/div[1]/div/div[2]/div[6]/a').click()
    driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div[1]/ul/li[2]/a").click()
    driver.find_element(by=By.ID, value="passcode-input").send_keys(passcode)
    driver.find_element(by=By.XPATH, value="/html/body/div/div/div[1]/div/div[2]/form/div[3]/button").click()

driver.implicitly_wait(8)
driver.find_element(by=By.ID, value="dont-trust-browser-button").click()
driver.implicitly_wait(8)
driver.find_element(by=By.XPATH, value="/html/body/div[2]/header/div[3]/div[1]/nav/ul/li[2]/a").click()

time.sleep(10)
driver.quit()