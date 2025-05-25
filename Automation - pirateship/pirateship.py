'''
to run this first run ch65001
then run this python code using python pirateship.py    

make sure to change the path of chrome and profile path to your own path

more over change the headers in the code and also change the the emails and passwords as you want 
'''



import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Set Chrome executable path and open a specific profile
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
profile_path = r"C:\Users\mar20\OneDrive\Desktop\Abubakar - Chrome.lnk"  # Change this for your profile

# ✅ List of emails to create accounts
email_list = [
 
    # Add more emails as needed
]

# --- 1️⃣ Configure Chrome Options ---
options = uc.ChromeOptions()
options.binary_location = chrome_path
options.add_argument(f"--user-data-dir={profile_path}")
options.add_argument("--profile-directory=Profile 1")
options.add_argument("--disable-popup-blocking")
options.add_argument("--start-maximized")

# ✅ Launch Chrome only once
driver = uc.Chrome(options=options, use_subprocess=True)

# ✅ Loop through each email
for email in email_list:
    print(f"\n🔄 Starting process for {email}...\n")

    try:
        # --- 2️⃣ Open Website ---
        driver.get("https://ship.pirateship.com/")
        time.sleep(5)

        # ✅ Click "Create a FREE Account" button
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Create a FREE account"))).click()

        # ✅ Fill registration form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
        driver.find_element(By.NAME, "password").send_keys("abubakarsuper123")  # Change password if needed
        driver.find_element(By.XPATH, "//button[contains(text(), 'Create your FREE account')]").click()

        # --- 3️⃣ Fill Shipping Form ---
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "originAddress.fullName"))).send_keys("John Test")
        driver.find_element(By.NAME, "originAddress.address1").send_keys("123 main st")
        time.sleep(2)
        driver.find_element(By.NAME, "originAddress.city").send_keys("Houston")

        driver.find_element(By.NAME, "originAddress.regionCode").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "//option[text()='Texas']").click()
        driver.find_element(By.NAME, "originAddress.postcode").send_keys("77002")
        time.sleep(2)
        driver.find_element(By.NAME, "originAddress.phone").send_keys("5124476356")

        # --- 4️⃣ Click "Start Shipping" Button ---
        try:
            start_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Shipping')]"))
            )
            start_button.click()
            print("✅ 'Start Shipping' button clicked!")
        except Exception as e:
            print(f"❌ Could not click 'Start Shipping' button: {e}")

        time.sleep(30)
        
        

        # --- 5️⃣ Click "Create a Single Label" Button ---
        try:
            create_label_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'https://ship.pirateship.com/ship/single')]"))
            )
            create_label_button.click()
            print("✅ 'Create a Single Label' button clicked!")
        except Exception as e:
            print(f"❌ Could not click 'Create a Single Label' button: {e}")

        # --- 6️⃣ Wait for form load ---
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "shipment-full-name"))
        )

        print("✅ Form loaded! Filling in details...")

        # --- 7️⃣ Fill in shipment details ---
        driver.find_element(By.ID, "shipment-full-name").send_keys("John Doe")
        driver.find_element(By.ID, "shipment-address1").send_keys("1234 Elm Street")
        driver.find_element(By.ID, "shipment-city").send_keys("Los Angeles")
        driver.find_element(By.ID, "shipment-region-id").send_keys("California")
        driver.find_element(By.ID, "shipment-zip").send_keys("90001")

        # --- 8️⃣ Fill in package dimensions ---
        driver.find_element(By.ID, "configuration-key-length").send_keys("10")
        driver.find_element(By.ID, "configuration-key-width").send_keys("5")
        driver.find_element(By.ID, "configuration-key-height").send_keys("8")

        # --- 9️⃣ Fill in weight ---
        driver.find_element(By.ID, "configuration-key-weight-pounds").send_keys("2")

        print("✅ Form filled successfully!")

        # --- 🔟 Click "Get Rates" Button ---
        try:
            get_rates_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "origin-submit"))
            )
            get_rates_button.click()
            print("✅ 'Get Rates' button clicked!")
        except Exception as e:
            print(f"❌ Could not click 'Get Rates' button: {e}")

        time.sleep(5)

        # # --- 11️⃣ Click "Buy Label" Button ---
        # try:
        #     buy_label_button = WebDriverWait(driver, 15).until(
        #         EC.element_to_be_clickable((By.ID, "buy-button"))
        #     )
        #     buy_label_button.click()
        #     print("✅ 'Buy Label' button clicked!")
        # except Exception as e:
        #     print(f"❌ Could not click 'Buy Label' button: {e}")

        time.sleep(5)

        # --- 12️⃣ Click "Logout" Button ---
        try:
            logout_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '#logout')]"))
            )
            logout_button.click()
            print(f"✅ Logged out for {email}. Starting next account...\n")

            # ✅ Click "Create a FREE account" again for the next loop
            time.sleep(5)
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Create a FREE account"))).click()

        except Exception as e:
            print(f"❌ Could not click 'Logout' button: {e}")

    except Exception as e:
        print(f"❌ Error processing {email}: {e}")

print("\n✅ All accounts processed successfully!")




'''
<a class="action-btn" href="https://ship.pirateship.com/ship/single">
                                    <span class="action-btn-icon-rebranded">
                                        <img src="/assets/skin/default/images/ship-icons/single.png" alt="">
                                    </span>

                                    <span class="action-btn-label">Create a<br>Single Label</span>
                                    <span class="action-btn-label-sidebar">Single</span>
                                </a>

'''