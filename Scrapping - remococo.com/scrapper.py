from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import sys
import time


sys.stdout.reconfigure(encoding='utf-8')

def scrape_user_tables(credentials):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    all_data_str = "\n📋 SCRAPING REPORT STARTED\n" + "=" * 50 + "\n"

    try:
        for index, cred in enumerate(credentials, start=1):
            username = cred["username"]
            password = cred["password"]

            all_data_str += f"\n**{username}**\n" + "\n"

            # Step 1: Go to the login page
            driver.get("http://remococo.com/index.php")

            # Step 2: Log in
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id"))).clear()
            driver.find_element(By.ID, "id").send_keys(username)
            driver.find_element(By.ID, "pw").clear()
            driver.find_element(By.ID, "pw").send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]").click()

            # Step 3: Wait for the table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered"))
            )

            # Step 4: Scrape table rows
            rows = driver.find_elements(By.CSS_SELECTOR, "table.table.table-bordered tbody tr")
            user_data = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                cols_text = [col.text.strip() for col in cols]
                if len(cols_text) == 4:  # Ensure the expected number of columns
                    user_data.append(cols_text)

            # Step 5: Process user data
            if user_data:
                df = pd.DataFrame(user_data, columns=["Item", "Code", "Value", "Status"])
                # print(df["Status"])

                summary = []
                for item, code ,status in zip(df["Item"], df["Value"],df["Status"]):
                    if "No." in item:
                        try:
                            no_part = item.split("No.")[-1].split()[0]
                            summary.append(f"No.{no_part} {code} {status} \n")
                        except IndexError:
                            continue  

                if summary:
                    all_data_str += f""+ "\n".join(summary) + "\n"
                else:
                    all_data_str += "⚠️ No data found.\n"
            else:
                all_data_str += "⚠️ No data found.\n"

            # Step 6: Logout
            logout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/ul/li[5]/a"))
            )
            logout_button.click()

            time.sleep(2)

    finally:
        driver.quit()

    all_data_str += "\n📁 SCRAPING COMPLETED FOR ALL USERS\n" + "=" * 50 + "\n"
    return all_data_str
