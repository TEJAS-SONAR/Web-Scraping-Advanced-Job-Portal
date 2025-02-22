import requests
import time
import datetime
import os

import pandas as pd
import numpy as np

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

CHROMEDRIVER_PATH = r"C:\Webdrivers\chromedriver.exe"
WINDOW_SIZE = "1920,1080"
chrome_options = Options()

# chrome_options.add_argument("--headless")
chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')

service = Service(CHROMEDRIVER_PATH)

def main():
    # Initialize the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://www.naukri.com/python-developer-jobs-in-remote?k=python%20developer&l=remote"
    driver.get(url)

    time.sleep(3)
    try:
        driver.find_element(By.XPATH, '//*[@id="root"]/div[4]/div[1]/div/section[2]/div[1]/div[2]/span/span[2]/p').click()
        driver.find_element(By.XPATH, '//*[@id="root"]/div[4]/div[1]/div/section[2]/div[1]/div[2]/span/span[2]/ul/li[2]').click()
    except Exception as e:
        pass

    pages = np.arange(1, 5)

    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for page_num, page in enumerate(pages, start=1):
        dff = pd.DataFrame(columns=['Job Title', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find(id='listContainer')
        job_elems = results.find_all('div', class_='srp-jobtuple-wrapper')
        
        for job_elem in job_elems:
            # Extract job details
            T = job_elem.find('a', class_='title')
            Title = T.text

            try:
                D = job_elem.find('span', class_='job-desc')
                Description = D.text
            except Exception as e:
                Description = None

            E = job_elem.find('span', class_='expwdth')
            Exp = E.text if E else "Not-Mentioned"

            C = job_elem.find('a', class_='comp-name')
            Company = C.text

            try:
                City = job_elem.find('span', class_='locWdth').text
            except Exception as e:
                City = None

            try:
                S = job_elem.find('span', 'ni-job-tuple-icon ni-job-tuple-icon-srp-rupee sal')
                Salary = S.text
            except Exception as e:
                Salary = "Not-Mentioned"

            D = job_elem.find('span', class_='job-post-day')
            Date = 'Today' if D == 'Just Now' else D.text if D else None

            U = job_elem.find('a', class_='title').get('href')
            URL = U

            # Add the job to the DataFrame
            dff = pd.concat([dff, pd.DataFrame([[Title, Description, Exp, Company, City, Salary, Date, URL]], columns = ['Job Title','Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])], ignore_index=True)

        # Save the page data to a separate JSON file (job1.txt, job2.txt, etc.)
        file_path = os.path.join(save_dir, f"job{page_num}.txt")
        dff.to_json(file_path, orient='records', lines=True)
        print(f"Data for page {page_num} saved to {file_path}")

        # Scroll and navigate to the next page
        driver.execute_script("window.scrollTo(0, (document.body.scrollHeight) - 1500)")
        time.sleep(0.75)
        driver.find_element(By.XPATH, '//*[@id="lastCompMark"]/a[2]/span').click()
        time.sleep(3)

    print("*********************CONCLUSION: FINISHED FETCHING DATA FROM NAUKRI.COM*********************")
    driver.close()

main()
