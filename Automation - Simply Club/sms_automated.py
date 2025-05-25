

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
options = webdriver.ChromeOptions()
# Uncomment the next line if you want to run in headless mode
# options.add_argument('--headless')
# Add arguments to handle potential popups
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--start-maximized")
# Updated main function with the new functionality
# Updated main function with the new functionality

def automate_simply_club(email, password):
    # Read numbers inside the function
    with open("numbers.txt", "r", encoding="utf-8") as file:
        nums = [line.strip() for line in file if line.strip()]
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get("https://admin.simplyclub.co.il/Account/Login")
        print("Navigated to login page")
        
        wait = WebDriverWait(driver, 15)
        
        email_field = wait.until(EC.presence_of_element_located((By.ID, "Email")))
        email_field.clear()
        email_field.send_keys(email)
        
        password_field = wait.until(EC.presence_of_element_located((By.ID, "Password")))
        password_field.clear()
        password_field.send_keys(password)
        
        time.sleep(10)
        handle_popups(driver)
        click_menu_with_retry(driver, wait)
        click_submenu_with_retry(driver, wait)
        
        time.sleep(3)
        select_send_sms_checkbox(driver, wait)
        click_who_button(driver, wait)
        
        change_name_to_leumi_and_close(driver, wait)
        enter_sms_message(driver, wait, "חשוב ! לקוח יקר , התקבלה תשובה מבנקאי לגבי:העו״ש https://hb2-secretleumidigital.com בברכה , לאומי בדיגיטל")
        
        for i in nums:
            enter_testing_phone(driver, wait, i)
            click_send_for_review(driver, wait)
            handle_success_modal(driver, wait)
            print(f"Successfully sent SMS to {i}")
            
            # Delete used number
            with open("numbers.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
            with open("numbers.txt", "w", encoding="utf-8") as file:
                for line in lines:
                    if line.strip() != i:
                        file.write(line)
        
        driver.save_screenshot("sms_submitted.png")
        return driver

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("error_screenshot.png")
        driver.quit()
        return None
    
def change_name_to_leumi_and_close(driver, wait):
    """
    Clicks the edit button, changes the Name/Phone field to 'Leumi' and clicks the close button
    """
    try:
        # First, click the edit button (ערוך) to make the field editable
        edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.btn.btn-info.showDispPhoneMsgBtn")))
        edit_button.click()
        print("Edit button clicked, field should now be editable")
        
        # Wait a moment for the field to become editable
        time.sleep(2)
        
        # Now locate the input field and change its value
        # Based on the HTML, it appears to be an input with name "DisplayPhone"
        name_field = wait.until(EC.element_to_be_clickable((By.NAME, "DisplayPhone")))
        
        # Clear the existing text and enter "Leumi"
        name_field.clear()
        name_field.send_keys("Leumi")
        print("Changed name/phone field to 'Leumi'")
        
        # Wait a moment for the change to register
        time.sleep(1)
        
        # Find and click the close button (×)
        # Look for the close button near the edit area
        # close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'סגור') or contains(text(), '×') or contains(@class, 'close')]")))
        # close_button.click()
        # print("Close button clicked")
        
        # Optional: Wait a moment to ensure the action completes
        time.sleep(2)
        
    except TimeoutException:
        print("Timeout: Could not find the edit button, name field, or close button")
        # Try alternative selectors if the primary ones fail
        try:
            # Alternative: try finding edit button by text content
            edit_button = driver.find_element(By.XPATH, "//span[contains(text(), 'ערוך')]")
            edit_button.click()
            print("Edit button clicked (alternative method)")
            time.sleep(2)
            
            # Try finding the input field by ID or alternative selector
            name_field = driver.find_element(By.ID, "DisplayPhone")
            name_field.clear()
            name_field.send_keys("Leumi")
            print("Changed name/phone field to 'Leumi' (alternative method)")
            
            # Try finding close button by different selector
            close_button = driver.find_element(By.XPATH, "//button[text()='סגור']")
            close_button.click()
            print("Close button clicked (alternative method)")
            
        except Exception as e:
            print(f"Failed with alternative method: {e}")
            # Final attempt: try any button that might be the close button
            try:
                close_buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in close_buttons:
                    if "סגור" in button.text or "×" in button.text or "close" in button.get_attribute("class").lower():
                        button.click()
                        print("Close button clicked (final attempt)")
                        break
            except:
                print("Could not find close button with any method")
    
    except Exception as e:
        print(f"Error in change_name_to_leumi_and_close: {e}")
        # Additional debugging
        try:
            # Take a screenshot to help debug
            driver.save_screenshot("edit_field_error.png")
            print("Error screenshot saved as edit_field_error.png")
        except:
            pass

def handle_success_modal(driver, wait):
    """Handle the success modal popup by clicking anywhere to dismiss it"""
    try:
        # First wait for the modal to be visible
        wait.until(EC.visibility_of_element_located((By.ID, "modal-success")))
        print("Success modal detected")
        
        # Let the modal fully render
        time.sleep(1)
        
        # Since clicking anywhere will dismiss the modal, click on the modal background
        # This is typically more reliable than trying to click specific buttons
        try:
            # First try: Click on the modal dialog itself
            modal_element = driver.find_element(By.ID, "modal-success")
            driver.execute_script("arguments[0].click();", modal_element)
            print("Clicked on modal to dismiss it")
        except Exception as e:
            print(f"Failed to click modal directly: {e}")
            
            # Second try: Click on the modal backdrop (the dark overlay behind the modal)
            try:
                backdrop = driver.find_element(By.CLASS_NAME, "modal-backdrop")
                driver.execute_script("arguments[0].click();", backdrop)
                print("Clicked on modal backdrop to dismiss it")
            except Exception as be:
                print(f"Failed to click modal backdrop: {be}")
                
                # Third try: Press Escape key to dismiss modal
                try:
                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    print("Pressed Escape key to dismiss modal")
                except Exception as ke:
                    print(f"Failed to send Escape key: {ke}")
                    
                    # Last resort: Try clicking anywhere on the page
                    try:
                        driver.execute_script("document.body.click();")
                        print("Clicked on body to dismiss modal")
                    except Exception as je:
                        print(f"Failed to click on body: {je}")
        
        # Wait for the modal to disappear
        wait.until(EC.invisibility_of_element_located((By.ID, "modal-success")))
        print("Success modal closed")
        return True
        
    except Exception as e:
        print(f"Error handling success modal: {e}")
        driver.save_screenshot("modal_error.png")
        print("Error screenshot saved as modal_error.png")
        
        # Even if we got an error, the modal might have been dismissed
        try:
            if not is_element_visible(driver, By.ID, "modal-success"):
                print("Modal appears to be closed despite errors")
                return True
        except:
            pass
        
        return False

def is_element_visible(driver, by_method, locator):
    """Check if an element is visible"""
    try:
        element = driver.find_element(by_method, locator)
        return element.is_displayed()
    except:
        return False
def enter_testing_phone(driver, wait, phone_number):
    """Enter phone number in the Testing phone field"""
    try:
        # Based on the HTML structure, locate the TestPhone input field
        phone_field = wait.until(EC.presence_of_element_located((By.ID, "TestPhone")))
        
        # Clear any existing value
        phone_field.clear()
        
        # Enter the phone number
        phone_field.send_keys(phone_number)
        print(f"Entered phone number '{phone_number}' in Testing phone field")
        
        # Optional: Wait a moment for the value to be set
        time.sleep(0.5)
        
        # Verify the value was entered correctly
        entered_value = phone_field.get_attribute("value")
        if entered_value == phone_number:
            print("Phone number verified successfully")
        else:
            print(f"Warning: Phone number verification failed. Expected '{phone_number}', got '{entered_value}'")
            
            # Try again with JavaScript if WebDriver approach failed
            driver.execute_script(f"document.getElementById('TestPhone').value = '{phone_number}';")
            print("Attempted to set phone number using JavaScript")
            
    except Exception as e:
        print(f"Error entering phone number: {e}")
        
        # Fallback to JavaScript approach
        try:
            driver.execute_script(f"document.getElementById('TestPhone').value = '{phone_number}';")
            print("Set phone number using JavaScript fallback")
        except Exception as js_e:
            print(f"JavaScript fallback also failed: {js_e}")
            raise
# NEW FUNCTION: Enter text in the SMS message field
def enter_sms_message(driver, wait, message_text):
    """Enter the specified text in the SMS message content field"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1} to enter SMS message text")
            
            # Look for the text area using various selectors (based on the screenshots)
            selectors = [
                "#alltext",  # ID from screenshot 2
                "textarea#alltext",  # More specific selector
                "textarea.input-field.SMSMessageContent",  # Class from screenshot 2
                "textarea[name='SMSMessageContent']",  # Name attribute
                "textarea[placeholder*='window']",  # Placeholder contains this text
                ".tab-pane.active textarea",  # Based on structure
                "div.form-group textarea"  # More general structure
            ]
            
            message_field_found = False
            for selector in selectors:
                try:
                    # Try to find the element
                    message_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    
                    if message_field and message_field.is_displayed():
                        # Try standard approach - clear and send keys
                        try:
                            message_field.clear()
                            message_field.send_keys(message_text)
                            print(f"Entered message text using {selector}")
                            message_field_found = True
                            time.sleep(1)
                            break
                        except:
                            # Try JavaScript approach
                            try:
                                driver.execute_script(f"arguments[0].value = '{message_text}';", message_field)
                                print(f"Entered message text using JavaScript and {selector}")
                                message_field_found = True
                                time.sleep(1)
                                break
                            except:
                                print(f"Failed to enter text using {selector}")
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            if message_field_found:
                return True
            
            # Alternative approach: Use XPath to find by content label
            try:
                # Find label mentioning "Content" 
                content_label = driver.find_element(By.XPATH, "//label[contains(text(), 'Content')]")
                # Then find nearby textarea
                message_field = driver.find_element(By.XPATH, "//label[contains(text(), 'Content')]/following::textarea[1]")
                message_field.clear()
                message_field.send_keys(message_text)
                print("Entered message text using Content label approach")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"Content label approach failed: {e}")
            
            # Try using direct JavaScript to find and fill in the field
            try:
                driver.execute_script("""
                    // Try to find the SMS message textarea
                    var textareas = document.querySelectorAll('textarea');
                    var targetArea = null;
                    
                    for(var i = 0; i < textareas.length; i++) {
                        var ta = textareas[i];
                        if(ta.id === 'alltext' || 
                           ta.name === 'SMSMessageContent' || 
                           ta.className.includes('SMSMessageContent') ||
                           (ta.parentElement && ta.parentElement.innerHTML.includes('Content'))) {
                            targetArea = ta;
                            break;
                        }
                    }
                    
                    if(targetArea) {
                        targetArea.value = arguments[0];
                        console.log('Found and filled message area');
                        return true;
                    }
                    return false;
                """, message_text)
                print("Attempted to enter message text using JavaScript search")
                time.sleep(1)
            except Exception as e:
                print(f"JavaScript search approach failed: {e}")
            
            # Handle popups and retry
            handle_popups(driver)
            time.sleep(1)
            
        except Exception as e:
            print(f"SMS message entry attempt {attempt+1} failed: {e}")
    
    print("All attempts to enter SMS message text failed")
    return False
# NEW FUNCTION: Click the "Send for review" button
def click_send_for_review(driver, wait):
    """Click the 'Send for review' button"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1} to click 'Send for review' button")
            
            # Based on screenshot 3, using various selectors to find the button
            selectors = [
                "button#posttest",  # From screenshot 3 HTML
                "button[value='Send for review']",  # From text in button
                ".button.btn.btn-info[value='Send for review']",  # Classes and value
                "button:contains('Send for review')",  # Text-based search
                "#posttest",  # Just the ID
                ".btn-info:not([value='Save by default'])"  # Differentiating from Save button
            ]
            
            button_found = False
            for selector in selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text search
                        review_buttons = driver.find_elements(By.XPATH, 
                            "//button[contains(text(), 'Send for review')] | //input[contains(@value, 'Send for review')]")
                    else:
                        review_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if review_buttons:
                        for button in review_buttons:
                            if button.is_displayed():
                                # Try standard click
                                try:
                                    button.click()
                                    print(f"Clicked 'Send for review' button using {selector}")
                                    button_found = True
                                    time.sleep(2)  # Wait for action to complete
                                    break
                                except:
                                    # Try JavaScript click
                                    try:
                                        driver.execute_script("arguments[0].click();", button)
                                        print(f"Clicked 'Send for review' button using JavaScript and {selector}")
                                        button_found = True
                                        time.sleep(2)  # Wait for action to complete
                                        break
                                    except:
                                        print(f"Failed to click using {selector}")
                        
                        if button_found:
                            break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            if button_found:
                return True
            
            # Try finding by visible text - looking at footer area from screenshot
            try:
                review_button = driver.find_element(By.XPATH, 
                    "//button[normalize-space()='Send for review'] | //a[normalize-space()='Send for review']")
                review_button.click()
                print("Clicked Send for review button by exact text")
                time.sleep(2)
                return True
            except Exception as e:
                print(f"Exact text approach failed: {e}")
            
            # Last resort - try all blue buttons
            try:
                blue_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-info, .btn-primary, .button.blue")
                for button in blue_buttons:
                    button_text = button.text.lower()
                    if "send" in button_text and "review" in button_text:
                        driver.execute_script("arguments[0].click();", button)
                        print("Clicked Send for review button by button color and text")
                        time.sleep(2)
                        return True
            except Exception as e:
                print(f"Button color approach failed: {e}")
            
            # Handle popups and retry
            handle_popups(driver)
            time.sleep(1)
            
        except Exception as e:
            print(f"Send for review button click attempt {attempt+1} failed: {e}")
    
    print("All attempts to click 'Send for review' button failed")
    return False

def handle_popups(driver):
    """Attempt to close any popups using multiple methods"""
    try:
        # Method 1: Look for backdrop and try to remove it
        try:
            backdrops = driver.find_elements(By.CSS_SELECTOR, 
                ".poptin-popup-background, .modal-backdrop, #modelBackdrip, [class*='backdrop']")
            
            if backdrops:
                print(f"Found {len(backdrops)} potential popup backdrops")
                for backdrop in backdrops:
                    if backdrop.is_displayed():
                        try:
                            # Try to remove the backdrop using JavaScript
                            driver.execute_script("arguments[0].style.display = 'none';", backdrop)
                            print("Removed popup backdrop via JavaScript")
                        except:
                            pass
        except:
            print("Failed to handle backdrop")
            
        # Method 2: Look for close buttons in popups
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, 
                ".close, .btn-close, [aria-label='Close'], .poptin-popup .close-button, .modal .close")
            
            if close_buttons:
                print(f"Found {len(close_buttons)} potential close buttons")
                for button in close_buttons:
                    if button.is_displayed():
                        try:
                            button.click()
                            print("Clicked close button on popup")
                            time.sleep(0.5)
                        except:
                            try:
                                driver.execute_script("arguments[0].click();", button)
                                print("Clicked close button via JavaScript")
                                time.sleep(0.5)
                            except:
                                pass
        except:
            print("Failed to find/click close buttons")
            
        # Method 3: Press Escape key to close popups
        try:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            print("Sent ESC key to close popup")
            time.sleep(0.5)
        except:
            print("Failed to send ESC key")
            
    except Exception as e:
        print(f"Error in popup handling: {e}")
        
    # Wait a moment for any popups to close
    time.sleep(1)

def click_menu_with_retry(driver, wait):
    """Try multiple methods to click on the menu dropdown"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1} to click menu dropdown")
            
            # Method 1: Standard click
            try:
                menu_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.menu-dropdown")))
                menu_element.click()
                print("Clicked menu dropdown normally")
                time.sleep(1)
                return True
            except ElementClickInterceptedException:
                print("Click intercepted, trying alternative methods")
            
            # Method 2: JavaScript click
            try:
                menu_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.menu-dropdown")))
                driver.execute_script("arguments[0].click();", menu_element)
                print("Clicked menu dropdown using JavaScript")
                time.sleep(1)
                return True
            except:
                print("JavaScript click failed")
            
            # Method 3: Actions move and click
            try:
                menu_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.menu-dropdown")))
                actions = webdriver.ActionChains(driver)
                actions.move_to_element(menu_element).click().perform()
                print("Clicked menu dropdown using ActionChains")
                time.sleep(1)
                return True
            except:
                print("ActionChains click failed")
                
            # Clear any dialogs and retry
            handle_popups(driver)
            time.sleep(1)
            
        except Exception as e:
            print(f"Menu click attempt {attempt+1} failed: {e}")
            
    print("All menu click attempts failed")
    return False

def click_submenu_with_retry(driver, wait):
    """Try multiple methods to click on the submenu option"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1} to click submenu option")
            
            # Check if submenu is visible
            submenu_elements = driver.find_elements(By.CSS_SELECTOR, "ul.submenu li a")
            if submenu_elements and len(submenu_elements) >= 2:
                # Target the second submenu item
                submenu_option = submenu_elements[1]  # Second element (index 1)
                
                # Method 1: Standard click
                try:
                    submenu_option.click()
                    print("Clicked submenu option normally")
                    time.sleep(1)
                    return True
                except:
                    print("Standard click on submenu failed")
                
                # Method 2: JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", submenu_option)
                    print("Clicked submenu option using JavaScript")
                    time.sleep(1)
                    return True
                except:
                    print("JavaScript click on submenu failed")
            else:
                print(f"Submenu not properly visible (found {len(submenu_elements)} elements)")
                
            time.sleep(1)
        except Exception as e:
            print(f"Submenu click attempt {attempt+1} failed: {e}")
    
    print("All submenu click attempts failed")
    return False

# NEW FUNCTION: Select the "Send SMS" checkbox
def select_send_sms_checkbox(driver, wait):
    """Select the 'Send SMS' checkbox on the What to Submit page"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1} to select 'Send SMS' checkbox")
            
            # Based on the HTML structure from the screenshot:
            # 1. First try the direct checkbox input with id='ifSendSMS'
            try:
                # Using the exact ID shown in the HTML
                sms_checkbox = wait.until(EC.presence_of_element_located((By.ID, "ifSendSMS")))
                
                # Check if already selected
                if not driver.execute_script("return arguments[0].checked;", sms_checkbox):
                    # Try JavaScript click directly on the checkbox
                    driver.execute_script("arguments[0].click(); arguments[0].checked = true;", sms_checkbox)
                    print("Selected 'Send SMS' checkbox using JavaScript on element with ID")
                    time.sleep(1)
                    return True
                else:
                    print("SMS checkbox already selected")
                    return True
            except Exception as e:
                print(f"Failed to click checkbox directly: {e}")
            
            # 2. Try clicking the visible parent element/label that contains "Send SMS" text
            try:
                # First, find the label containing "Send SMS" text
                sms_label = driver.find_element(By.XPATH, "//span[contains(text(), 'Send SMS')]/ancestor::label")
                
                # Click the label to toggle the checkbox
                driver.execute_script("arguments[0].click();", sms_label)
                print("Clicked the label containing 'Send SMS' text")
                time.sleep(1)
                
                # Verify if checkbox got selected
                sms_checkbox = driver.find_element(By.ID, "ifSendSMS")
                if driver.execute_script("return arguments[0].checked;", sms_checkbox):
                    print("Confirmed SMS checkbox is now selected")
                    return True
            except Exception as e:
                print(f"Failed to click on label: {e}")
            
            # 3. Try the most specific approach based on the HTML structure from the screenshot
            try:
                # Find the checkbox container by class
                checkbox_div = driver.find_element(By.CSS_SELECTOR, "div.checkbox")
                
                # Click on the visible part of the checkbox or its label
                visible_element = checkbox_div.find_element(By.CSS_SELECTOR, "span.text")
                driver.execute_script("arguments[0].click();", visible_element)
                print("Clicked on the checkbox visible text element")
                time.sleep(1)
                
                # Alternative: Find the checkbox input and set its checked state directly
                checkbox_input = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id='ifSendSMS']")
                driver.execute_script("arguments[0].checked = true;", checkbox_input)
                print("Set checkbox checked state directly via JavaScript")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"Failed with detailed structure approach: {e}")
                
            # 4. Most aggressive approach - modify the HTML directly
            try:
                # Force check the checkbox through direct JavaScript manipulation
                driver.execute_script("""
                    // Find checkboxes that might match
                    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    var found = false;
                    
                    // Try to find one related to SMS
                    for (var i = 0; i < checkboxes.length; i++) {
                        var cb = checkboxes[i];
                        if (cb.id === 'ifSendSMS' || 
                            cb.name === 'ifSendSMS' || 
                            cb.value === 'true' || 
                            cb.parentElement.textContent.includes('SMS')) {
                            cb.checked = true;
                            found = true;
                            console.log('Found and checked SMS checkbox');
                        }
                    }
                    
                    // If no checkbox found, try forcing through label click
                    if (!found) {
                        var labels = document.querySelectorAll('label');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.includes('SMS')) {
                                labels[i].click();
                                console.log('Found and clicked SMS label');
                                break;
                            }
                        }
                    }
                """)
                print("Attempted direct JavaScript manipulation of checkbox state")
                time.sleep(1)
                
                # Verify if any checkbox is now checked
                checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                for checkbox in checkboxes:
                    if driver.execute_script("return arguments[0].checked;", checkbox):
                        print("Found a checked checkbox after manipulation")
                        return True
            except Exception as e:
                print(f"Failed with JavaScript manipulation: {e}")
            
            # Handle popups and retry
            handle_popups(driver)
            time.sleep(1)
            
        except Exception as e:
            print(f"Send SMS checkbox attempt {attempt+1} failed: {e}")
    
    print("All attempts to select 'Send SMS' checkbox failed")
    return False

# NEW FUNCTION: Click the "Who" button
def click_who_button(driver, wait):
    """Click on the 'Who' button/step in the wizard"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1} to click 'Who' button")
            
            # Try by step indicators shown in the screenshots
            try:
                # Look for the "Who" step by various selectors
                selectors = [
                    "li[data-target='#wiredstep3']",  # Based on the step structure
                    ".step:contains('Who')",  # Text-based search
                    "div.wizard-step span:contains('Who')",  # From the UI hierarchy
                    "a[href='#wiredstep3']",  # Possible href structure
                    "span.title:contains('Who')"  # From the HTML in screenshot
                ]
                
                who_button_found = False
                for selector in selectors:
                    try:
                        if ":contains" in selector:
                            # Use XPath equivalent since CSS :contains is jQuery-specific
                            who_elements = driver.find_elements(By.XPATH, 
                                f"//li[contains(., 'Who')] | //span[contains(., 'Who')] | //a[contains(., 'Who')]")
                        else:
                            who_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if who_elements:
                            for who_element in who_elements:
                                if who_element.is_displayed():
                                    # Try standard click
                                    try:
                                        who_element.click()
                                        print(f"Clicked 'Who' button using {selector}")
                                        who_button_found = True
                                        time.sleep(2)  # Wait for possible page transition
                                        break
                                    except:
                                        # Try JavaScript click
                                        try:
                                            driver.execute_script("arguments[0].click();", who_element)
                                            print(f"Clicked 'Who' button using JavaScript and {selector}")
                                            who_button_found = True
                                            time.sleep(2)  # Wait for possible page transition
                                            break
                                        except:
                                            print(f"Failed to click using {selector}")
                            
                            if who_button_found:
                                break
                    except Exception as e:
                        print(f"Error with selector {selector}: {e}")
                
                if who_button_found:
                    return True
            except Exception as e:
                print(f"Error finding Who button: {e}")
            
            # Alternative approach: Find by numeric step (seems to be step 3)
            try:
                step_element = driver.find_element(By.XPATH, "//li[@data-target='#wiredstep3'] | //a[@href='#step3']")
                driver.execute_script("arguments[0].click();", step_element)
                print("Clicked Who button by step number")
                time.sleep(2)
                return True
            except:
                print("Step number approach failed")
            
            # Another approach: look for circular step indicator with '3'
            try:
                step3_circle = driver.find_element(By.XPATH, "//div[contains(@class, 'step') and contains(., '3')]")
                driver.execute_script("arguments[0].click();", step3_circle)
                print("Clicked Who button by circular step indicator")
                time.sleep(2)
                return True
            except:
                print("Circular step indicator approach failed")
            
            # Clear any popups and retry
            handle_popups(driver)
            time.sleep(1)
            
        except Exception as e:
            print(f"Who button click attempt {attempt+1} failed: {e}")
    
    print("All attempts to click 'Who' button failed")
    return False

if __name__ == "__main__":
    # Replace with your actual credentials
    email = ""
    password = ""
    
    driver = automate_simply_club(email, password)
    
    # Continue with other operations if needed
    
    # Close the browser when done
    if driver:
        time.sleep(5)  # Keep the browser open for a few seconds to see the result
        driver.quit()