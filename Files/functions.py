from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


import re
import csv


def start_browser_Helper(proxy=None):
    '''
    Initializes the WebDriver in headless mode and returns the driver instance.
    '''
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    if proxy:
            options.add_argument(f'--proxy-server={proxy}')
    driver = webdriver.Edge(options=options)
    return driver




def open_page(driver ,link):
    '''
    Load the given URL and wait until the page is fully loaded.
    If the page does not load within 10 seconds, an exception will be raised.
    '''
    driver.get(link)
    wait_for_page_load(driver)
    assert "No results found." not in driver.page_source

def wait_for_page_load(driver, timeout=20, unique_element=None):
    """
    Wait for the page to load completely by combining document ready state and specific element visibility.
    Args:
        driver: The Selenium WebDriver instance.
        timeout: The maximum wait time in seconds.
        unique_element: A tuple (By.<method>, "value") representing the element to wait for.
    """
    try:
        # Wait for document.readyState to be 'complete'
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # Optionally wait for a specific element to be visible
        if unique_element:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(unique_element)
            )
    except Exception as e:
        print(f"Error while waiting for page load: {e}")

def button_click(driver, xpath):
    '''
    Wait for a button to be clickable and then click it.
    '''
    try:
        # Wait for the button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))

        # Find the button element by XPath
        button = driver.find_element(By.XPATH, xpath)

        # Click the button
        button.click()
        time.sleep(5)
        print("Button clicked successfully.")
    except Exception as e:
        print(f"Button not found.")

def get_data(driver, xpath):
    '''
    Extracts the text content from an element specified by the XPath on the page.
    '''
    try:
        data = driver.find_element(By.XPATH, xpath)
        return data.text.strip()
    except Exception as e:
        print(f"An error occurred while extracting the text: {e}")
        return None

def login_Helper(driver, email, password, login_page_link="https://www.linkedin.com/login"):
    '''
    Logs in to the LinkedIn account.
    '''
    open_page(driver, login_page_link)
    time.sleep(5)  

    try:
        username_field = driver.find_element(By.ID, 'username')
        username_field.send_keys(email)

        password_field = driver.find_element(By.ID, 'password')
        password_field.send_keys(password)

        password_field.send_keys(Keys.RETURN)
        time.sleep(5)  

        if "Feed | LinkedIn" in driver.title:
            print("Login successful!")
            return True
        else:
            print("Login failed. Check your credentials or other login issues.")
            return False

    except Exception as e:
        print(f"Exception occurred during login: {e}")
        return False

def remove_redundant_info(input_data):
    """
    Cleans redundant information from a dictionary, including duplicate keys/values
    and repetitive phrases within each string.

    Args:
        input_data (dict): Dictionary with keys and sets of values.

    Returns:
        dict: Cleaned dictionary with unique and normalized keys/values.
    """
    def clean_redundant_text(text):
        # Split the string into components and remove duplicates
        components = text.split()  # Splits by default on whitespace
        unique_components = []
        for component in components:
            if component not in unique_components:
                unique_components.append(component)
        return ' '.join(unique_components)

    cleaned_data = {}
    for key, values in input_data.items():
        # Clean the key
        cleaned_key = clean_redundant_text(key)
        
        # Clean each value in the set
        cleaned_values = set()
        for value in values:
            cleaned_value = clean_redundant_text(value)
            cleaned_values.add(cleaned_value)
        
        # Assign the cleaned key-value pair to the new dictionary
        cleaned_data[cleaned_key] = list(cleaned_values)
    
    return cleaned_data


def get_experience(driver,profile):
    driver.get(profile+"/details/experience/")                               
    wait_for_page_load(driver, timeout=20, unique_element=(By.CLASS_NAME, "VcfWtteOjwrkCZnXQzzxBwAnJxBIDECsnqgUVQ"))
    ul_element = driver.find_element(By.CLASS_NAME, "VcfWtteOjwrkCZnXQzzxBwAnJxBIDECsnqgUVQ")

    job_details = {}

    li_elements = ul_element.find_elements(By.TAG_NAME, "li")

    for li in li_elements:
    
        try:
            title_div = li.find_element(By.CLASS_NAME, "display-flex.align-items-center.mr1.t-bold")
            title = title_div.text.strip()  
            
            spans = li.find_elements(By.XPATH, ".//span[not(contains(@class, 'visually-hidden'))]")
            span_texts = set([span.text.strip() for span in spans if span.text.strip()])

            if title:  
                job_details[title] = list(span_texts)

        except Exception as e:
            print(f"Error processing an li element")
    
    return remove_redundant_info(job_details)
        
def get_education(driver, section_xpath):
    education = []
    print("List created")

    try:
        # Identify the section first using the provided XPath
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, section_xpath))
        )

        # Now, find the education list within the section by targeting the div[3]/ul/li
        education_elements = section.find_elements(By.XPATH, ".//div[3]/ul/li")  # Adjusted XPath to target div[3]/ul/li

        print(f"Found {len(education_elements)} education entries")

        # Loop through each element and extract the text
        for element in education_elements:
            raw_text = element.text.split("\n")  # Split text into lines
            cleaned_text = list(dict.fromkeys(raw_text))  # Remove duplicates while preserving order
            education.append(cleaned_text)  # Append cleaned data to the list
    except Exception as e:
        print(f"An error occurred while fetching education: {e}")
    
    return education

def get_Followers(driver, section):
    followers = []  
    print("List created")
    
    try:
        # Identify the section first using the provided XPath
        section_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, section))
        )
        
        # Now, go to the correct sub-path: /div[2]/div/div/div/p/span[1] to extract the follower count
        followers_element = section_element.find_element(By.XPATH, ".//div[2]/div/div/div/p/span[1]")
        
        # Extract the text (followers count)
        followers_text = followers_element.text
        print(f"Found followers: {followers_text}")
        
        # Append the followers text (or any additional processing if required) to the followers list
        followers.append(followers_text)
    
    except Exception as e:
        print(f"An error occurred while fetching followers: {e}")
    
    return followers



def get_skills(driver,profile):
    driver.get(profile+"/details/skills")                               
    wait_for_page_load(driver, timeout=20, unique_element=(By.CLASS_NAME, "VcfWtteOjwrkCZnXQzzxBwAnJxBIDECsnqgUVQ"))
    ul_element = driver.find_element(By.CLASS_NAME, "VcfWtteOjwrkCZnXQzzxBwAnJxBIDECsnqgUVQ")

    job_details = {}

    li_elements = ul_element.find_elements(By.TAG_NAME, "li")

    for li in li_elements:
        
            try:
                title_div = li.find_element(By.CLASS_NAME, "display-flex.align-items-center.mr1.t-bold")
                title = title_div.text.strip()  
                
                spans = li.find_elements(By.XPATH, ".//span[not(contains(@class, 'visually-hidden'))]")
                span_texts = set([span.text.strip() for span in spans if span.text.strip()])

                if title:  
                    job_details[title] = list(span_texts)

            except Exception as e:
                print(f"Error processing an li element")
        
    skills = remove_redundant_info(job_details)
    return list(skills.keys())
  



def find_show_all_link(driver, section_xpath):
    try:
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, section_xpath))
        )

        outer_html = section.get_attribute('outerHTML')

        if 'pvs-list__footer-wrapper' in outer_html:
            print("Footer wrapper found within the section.")

            show_all_button = section.find_element(By.XPATH, ".//div/div/a[contains(@class, 'artdeco-button')]")
            
            if show_all_button:
                link = show_all_button.get_attribute('href')
                print(f"Found 'Show All' button with link: {link}")
                return link
            else:
                print("No 'Show All' button found within the footer wrapper.")
                return None
        else:
            print("No footer wrapper found within the section.")
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None









def get_contact_info(driver, section_xpath):
    '''
    Dynamically extracts data from the specified section based on the given XPath.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        section_xpath (str): The XPath to locate the desired section.

    Returns:
        list: A list of extracted text and link values from <div> and <a> tags.
    '''
    try:
        section_element = driver.find_element(By.XPATH, section_xpath)

        div_elements = section_element.find_elements(By.TAG_NAME, "div")
        a_elements = section_element.find_elements(By.TAG_NAME, "a")

        extracted_data = []

        for div in div_elements:
            div_text = div.text.strip()
            if div_text:  
                extracted_data.append({"tag": "div", "content": div_text})

        for a in a_elements:
            a_text = a.text.strip()
            a_href = a.get_attribute("href")
            if a_text or a_href: 
                extracted_data.append({"tag": "a", "content": a_text, "href": a_href})

        return extracted_data

    except Exception as e:
        print(f"An error occurred while extracting contact info: {e}")
        return []




def get_Followers_section(driver, total_sections=10):
    followers_section = None

    for i in range(1, total_sections + 1):
        # Generate the XPath for the current section
        xpath = f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[{i}]"
        
        try:
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)) 
            )
            
            # Find the section containing followers information
            followers_section = section.find_element(By.ID, "content_collections")  # You can change this to a more specific ID or class if needed.
            if followers_section:
                print(f"Followers section found at XPath: {xpath}")
                return xpath
                
        except Exception as e:
            print(f"Section {i} not found or doesn't contain the id 'followers'.")

    if followers_section:
        return followers_section
    else:
        print("Followers section not found.")
        return None








def get_education_section(driver, total_sections=10):
    education_section = None

    for i in range(1, total_sections + 1):
        # Generate the XPath for the current section
        xpath = f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[{i}]"
        
        try:
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)) 
            )
            
            education_section = section.find_element(By.ID, "education")
            if education_section:
                print(f"Education section found at XPath: {xpath}")
                return xpath
                
            
        except Exception as e:
            print(f"Section {i} not found or doesn't contain the id 'education'.")
    
    if education_section:
        return education_section
    else:
        print("Education section not found.")
        return None










def get_experience_section(driver, total_sections=10):
    education_section = None

    for i in range(1, total_sections + 1):
        xpath = f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[{i}]"
        
        try:
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)) 
            )
            
            education_section = section.find_element(By.ID, "experience")
            if education_section:
                print(f"Education section found at XPath: {xpath}")
                return xpath
                
            
        except Exception as e:
            print(f"Section {i} not found or doesn't contain the id 'education'.")
    
    if education_section:
        return education_section
    else:
        print("Education section not found.")
        return None
    



def get_skills_section(driver, total_sections=10):
    skills_section = None

    for i in range(1, total_sections + 1):
        # Generate the XPath for the current section
        xpath = f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[{i}]"
        
        try:
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)) 
            )
            
            # Check if the section has the ID "skills"
            skills_section = section.find_element(By.ID, "skills")
            if skills_section:
                print(f"Skills section found at XPath: {xpath}")
                return xpath
            
        except Exception as e:
            print(f"Section {i} not found or doesn't contain the ID 'skills'.")
    
    if skills_section:
        return skills_section
    else:
        print("Skills section not found.")
        return None


import csv

def save_to_csv(name, followers, email, bio, location, experience_list, education_data, skills, filename='linkedin_scraped_data.csv'):
    """
    Saves the scraped data to a CSV file.

    Parameters:
    - name: Name of the person
    - followers: Number of followers the person has
    - email: Email of the person
    - bio: Bio of the person
    - location: Location of the person
    - experience_list: List of experience details (each item in the list is a list of role, company, duration, location)
    - education_data: List of education details (each item in the list is a list of degree, institution, duration)
    - skills: List of skills of the person
    - filename: Name of the CSV file to save data to (default is 'linkedin_scraped_data.csv')

    Returns:
    - None
    """
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write header row
            writer.writerow([
                'Name', 'Followers', 'Email', 'Location', 
                'Skill','Bio', 'Experience Role', 'Experience Company', 'Experience Duration', 
                'Education Degree', 'Education Institution', 'Education Duration'
            ])

            # Determine the maximum number of rows to write based on the largest list
            max_entries = max(len(experience_list), len(education_data), len(skills))
            
            for i in range(max_entries):
                # Experience details (handle missing entries gracefully)
                if i < len(experience_list):
                    experience_role = experience_list[i][0]
                    experience_company = experience_list[i][1]
                    experience_duration = experience_list[i][2]
                    # experience_location = experience_list[i][3]
                else:
                    experience_role = experience_company = experience_duration = experience_location = ''

                # Education details (handle missing entries gracefully)
                if i < len(education_data):
                    education_institution= education_data[i][0]
                    education_degree = education_data[i][1]
                    education_duration = education_data[i][2]
                else:
                    education_degree = education_institution = education_duration = ''

                # Skills (handle missing entries gracefully)
                skill = skills[i] if i < len(skills) else ''

                # Write all data to the CSV
                writer.writerow([
                    name, followers, email, location, 
                    skill, bio,experience_role, experience_company, experience_duration, 
                     education_degree, education_institution, education_duration
                ])

        print(f"Data successfully saved to {filename}")

    except Exception as e:
        print(f"Error occurred while saving data to CSV: {e}")