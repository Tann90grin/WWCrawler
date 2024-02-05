from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://waterlooworks.uwaterloo.ca/")

driver.find_element(by=By.CLASS_NAME, value="btn--landing").click()
emailInput = driver.find_element(by=By.ID, value="userNameInput").send_keys("EMAIL")
nextButton = driver.find_element(by=By.ID, value="nextButton").click()
driver.find_element(by=By.ID, value="passwordInput").send_keys("PASSWORD")
driver.find_element(by=By.ID, value="submitButton").click()
driver.implicitly_wait(8)
driver.find_element(by=By.CLASS_NAME, value='other-options-link').click()

#Use Passcode Authentication
element = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div[1]/ul/li[2]/a").click()
driver.find_element(by=By.ID, value="passcode-input").send_keys("PASSCODE")
driver.find_element(by=By.XPATH, value="/html/body/div/div/div[1]/div/div[2]/form/div[3]/button").click()

driver.implicitly_wait(8)
driver.find_element(by=By.ID, value="dont-trust-browser-button").click()
# print(1)
time.sleep(10)
# print(1)
