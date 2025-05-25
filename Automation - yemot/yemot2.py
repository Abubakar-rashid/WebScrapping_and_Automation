from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from selenium.webdriver.common.action_chains import ActionChains

# Setup WebDriver
service = Service()
driver = webdriver.Chrome(service=service)

# Login to Yemot SMS
driver.get("https://new.yemot-sms.co.il/login")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

email_field = driver.find_element(By.ID, "email")
password_field = driver.find_element(By.ID, "password")
email_field.send_keys("meirbaa@mail.com")
password_field.send_keys("Abank0909@")
password_field.send_keys(Keys.RETURN)

time.sleep(3)

# Function to delete all messages from history
def delete_sms_history():
    try:
        print("🗑️ מחיקת הודעות מהיסטוריית ה-SMS...")
        while True:
            # Find the first delete button
            delete_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".menu-icon.delete"))
            )
            delete_button.click()
            
            # Wait for the confirmation dialog and click "Yes"
            confirm_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".button.answer.yes"))
            )
            confirm_button.click()

            time.sleep(2)  # Wait for deletion to process
            
    except Exception:
        print("✅ אין עוד הודעות למחיקה.")

# Read phone numbers
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "test.txt")

try:
    with open(file_path, 'r') as file:
        phone_numbers = [line.strip() for line in file.readlines() if line.strip()]
    print(f"📄 נמצאו {len(phone_numbers)} מספרים בקובץ.")
except FileNotFoundError:
    print("❌ קובץ מספרים לא נמצא.")
    driver.quit()
    exit()

# Send SMS messages
batch_size = 15

def send_sms_batch(batch):
    for index, phone_number in enumerate(batch):
        try:
            print(f"📨 שליחת הודעה למספר: {phone_number}")
            phone_number_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "test_sms_phone_number"))
            )
            phone_number_field.clear()
            phone_number_field.send_keys(phone_number)

            if index == 0:
                time.sleep(3)

            send_button = driver.find_element(By.CLASS_NAME, "send")
            driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(send_button))
            driver.execute_script("arguments[0].click();", send_button)

            print("✅ הודעה נשלחה בהצלחה!")
            time.sleep(2)

        except Exception as e:
            print(f"❌ שגיאה בשליחת הודעה למספר {phone_number}: {e}")
            


def confirm_delete():
    try:
        confirm_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".button.answer.yes"))
        )
        
        # Scroll into view and click
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
        time.sleep(1)
        ActionChains(driver).move_to_element(confirm_button).click().perform()

        print("✅ Successfully clicked 'Yes' on confirmation popup!")
        time.sleep(2)  # Wait to ensure the deletion happens

    except Exception as e:
        print(f"❌ Failed to click 'Yes' on confirmation popup: {e}")


def test_delete_click():
    try:
        delete_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".menu-icon.delete"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
        time.sleep(1)
        
        # Perform click action
        ActionChains(driver).move_to_element(delete_button).click().perform()
        print("✅ Trash button clicked!")
        time.sleep(2)  # Wait to see if confirmation appears
        
    except Exception as e:
        print(f"❌ Trash button not found or not clickable: {e}")
        
def test_confirmation_popup():
    try:
        confirm_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".button.answer.yes"))
        )
        print("✅ Confirmation popup detected!")
        
    except Exception as e:
        print("❌ No confirmation popup appeared:", e)


for i in range(0, len(phone_numbers), batch_size):
    batch = phone_numbers[i:i + batch_size]

    time.sleep(7)
    print("\n🔄 מעבר לדף 'הודעה חדשה'...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "הודעה חדשה")))
    driver.find_element(By.LINK_TEXT, "הודעה חדשה").click()

    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "sms_content")))

    message_content_field = driver.find_element(By.NAME, "sms_content")
    message_content_field.clear()
    message_content_field.send_keys("שלום ובוקר טוב")

    sender_field = driver.find_element(By.NAME, "sms_sender")
    sender_field.clear()
    sender_field.send_keys("testalc")

    time.sleep(15)

    send_sms_batch(batch)
    try:
        print("🔘 לוחץ על הכפתור הנוסף לאחר שליחת 15 הודעות...")
        additional_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/nav/ul/li[1]/a/span"))
        )
        driver.execute_script("arguments[0].click();", additional_button)
        print("✅ הכפתור הנוסף נלחץ בהצלחה!")
        ## deleting the output
        test_delete_click()
        test_confirmation_popup()
        confirm_delete()
        time.sleep(2)
    except Exception as e:
        print(f"❌ שגיאה בלחיצה על הכפתור הנוסף: {e}")
    
    

time.sleep(5)
print("📢 סיום שליחת ההודעות וסגירת הדפדפן...")
driver.quit()
