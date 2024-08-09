import os
import time
import logging

from crewai_tools import tool
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from tools.utils import get_linkedin_posts


class LinkedinToolException(Exception):
    def __init__(self):
        super().__init__("You need to set the LINKEDIN_EMAIL and LINKEDIN_PASSWORD env variables")


def scrape_linkedin_posts_fn() -> str:
    """
    A tool that can be used to scrape LinkedIn posts
    """
    linkedin_username = os.environ.get("LINKEDIN_EMAIL")
    linkedin_password = os.environ.get("LINKEDIN_PASSWORD")
    linkedin_profile_name = os.environ.get("LINKEDIN_PROFILE_NAME")

    if not (linkedin_username and linkedin_password and linkedin_profile_name):
        raise LinkedinToolException()

    logging.info("Starting Edge browser for LinkedIn scraping.")
    edge_service = EdgeService(EdgeChromiumDriverManager().install())
    browser = webdriver.Edge(service=edge_service)

    try:
        browser.get("https://www.linkedin.com/login")

        username_input = browser.find_element("id", "username")
        password_input = browser.find_element("id", "password")
        username_input.send_keys(linkedin_username)
        password_input.send_keys(linkedin_password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(3)

        logging.info("Navigating to the LinkedIn profile activity page.")
        browser.get(f"https://www.linkedin.com/in/{linkedin_profile_name}/recent-activity/all/")

        for _ in range(2):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        logging.info("Extracting posts from the LinkedIn page source.")
        posts = get_linkedin_posts(browser.page_source)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise e
    finally:
        logging.info("Closing the browser.")
        browser.quit()

    # We'll just return 2 of the latest posts, since it should be enough for the LLM to get the overall style
    return str(posts[:2])


@tool("ScrapeLinkedinPosts")
def scrape_linkedin_posts_tool() -> str:
    """
    A tool that can be used to scrape LinkedIn posts
    """
    return scrape_linkedin_posts_fn()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(scrape_linkedin_posts_tool())
