from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import csv
import time
import os
import re

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
#driver = webdriver.Chrome(options=chrome_options) 
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
driver.implicitly_wait(15)
driver.find_element(by=By.XPATH, value="/html/body/div[2]/header/div[4]/div/div/button").click()
driver.implicitly_wait(5)
driver.find_element(by=By.XPATH, value="/html/body/div[2]/header/div[3]/div[1]/nav/ul/li[2]/a").click()
driver.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div/div/div[2]/div[3]/div[1]/div/div[2]/div/div/div/div/table/tbody/tr[4]/td[2]/a").click()
driver.implicitly_wait(5)


original_window_handle = driver.current_window_handle

page_list = driver.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div/div/div[2]/div/div/div/div/div[3]/div[4]/div/ul")
pages = page_list.find_elements(by=By.TAG_NAME, value="li")
max_page = len(pages) - 4


usefulInformation = {"Job Title",
                        "Level", 
                        "Region",
                        "Job - City", 
                        "Job - Province / State", 
                        "Job Responsibilities",
                        " Required Skills" 
                        }


with open('jobInfo.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    def write_in_csv(driver):
        jobInfo = {}
        usefulInformation = {"Job Title",
                            "Level", 
                            "Region",
                            "Job - City", 
                            "Job - Province / State", 
                            "Job Responsibilities",
                            " Required Skills" 
                            }
        
        table = driver.find_elements(by=By.TAG_NAME, value="table")[1]
        try:
            rows = table.find_elements(by=By.TAG_NAME, value="tr")
            # print('1')
            pattern = r'\s*:\s*'

            for row in rows:
                cells = row.find_elements(by=By.TAG_NAME, value="td")
                if len(cells)>=2: 
                    text = cells[0].text
                    cleaned_text = re.sub(pattern, '', text)
                    if cleaned_text in usefulInformation:
                        jobInfo[cleaned_text] = cells[1].text

        except Exception as e:
            print(f"not able to find tr:{e}")
        write_job_info_to_csv(jobInfo)

    index = 0
    def write_job_info_to_csv(job_info):
        # Define the order of columns based on the provided keys
        fieldnames = [
            "Job Title",
            "Level",
            "Region",
            "Job - City",
            "Job - Province / State",
            "Job Responsibilities",
            "Required Skills"  # Make sure there's no leading space as in the provided keys
        ]
        
        # Open the CSV file for writing
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write the job information row
        # Ensure the dictionary keys match exactly, including whitespace
        # This step might require cleaning the keys in the actual job_info dictionary if they come with extra spaces
        cleaned_job_info = {key.strip(): value for key, value in job_info.items()}  # Stripping spaces from keys
        writer.writerow(cleaned_job_info)
    index+=1
    
    for page in range(0, max_page):
        postingsTable = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "postingsTable")))
        rows = postingsTable.find_elements(by = By.TAG_NAME, value="tr")

        for row in rows:
            try:
                cell = row.find_elements(By.TAG_NAME, "td")[3]
                link = cell.find_element(By.TAG_NAME, "a")
                link.click()

                # Wait for the new window/tab to open
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

                # Switch to the new window
                new_window_handle = [handle for handle in driver.window_handles if handle != original_window_handle][0]
                driver.switch_to.window(new_window_handle)

                # Here you can call your function to write in csv or perform other actions
                write_in_csv(driver)

                # Close the current window and switch back to the original window
                driver.close()
                driver.switch_to.window(original_window_handle)

            except Exception as e:
                print(f"Error processing a cell in row: {e}")

        print(len(rows))
        print(index)
        driver.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div/div/div[2]/div/div/div/div/div[3]/div[4]/div/ul/li[12]/a").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "postingsTable")))


driver.quit()


        