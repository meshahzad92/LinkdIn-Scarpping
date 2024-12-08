from importlib import reload
from Files import constants, functions  # Import modules

# Reload modules
reload(constants)
reload(functions)

from Files.constants import *
from Files.functions import *


def scrape_linkedin_profile(profile_url, my_email, password):

    driver = start_browser() 

    try:
        login(driver, email=my_email, password=password)
        open_page(driver, profile_url)
        # Namr
        xpath = "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/span[1]/a/h1"
        name = get_data(driver, xpath)
        # Number of followers 
        section = get_Followers_section(driver)
        followers_uncleaned = get_Followers(driver, section)
        followers = int(re.sub(r'\D', '', followers_uncleaned[0]))
        # Bio
        xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]'
        bio = get_data(driver, xpath)
        # Location
        xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]'
        location = get_data(driver, xpath)
        # Education
        section = get_education_section(driver)
        education_data = get_education(driver, section)
        # Contact Info
        path = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[2]/a'
        button_click(driver, path)
        section_xpath = "/html/body/div[4]/div/div/div[2]/section/div"
        contact_info = get_contact_info(driver, section_xpath)
        email = next((info['content'] for info in contact_info if '@' in info.get('content', "")), None)
        # Experience
        experience_list = get_experience(driver,profile_url)
        # Skills
        skills_list = get_skills(driver, profile_url)
        driver.quit()

        return {
            "name": name,
            "followers": followers,
            "email": email,
            "bio": bio,
            "location": location,
            "experience": list(experience_list) if isinstance(experience_list, set) else experience_list,
            "education": education_data,
            "skills": list(skills_list) if isinstance(skills_list, set) else skills_list,
        }


    except Exception as e:
        driver.quit()
        raise e