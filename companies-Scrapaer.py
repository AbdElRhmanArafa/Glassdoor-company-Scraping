from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    element_to_be_clickable,
    presence_of_all_elements_located,
)
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
)
from bs4 import BeautifulSoup
import time
import csv


def extract_information_overview(soup, information_list=[]):
    """
    Extracts overview information about a company.

    Args:
        soup (BeautifulSoup): The parsed HTML soup of the company page.
        information_list (list): List to store extracted information.

    Returns:
        None
    """
    overview_containers = soup.find_all(
        "div",
        class_="employer-overview__employer-overview-module__employerOverviewContainer",
    )
    for overview_container in overview_containers:
        information = {}
        overview_header = overview_container.find(
            "header",
            class_="employer-overview__employer-overview-module__employerOverviewHeader",
        )
        if overview_header:
            overview_heading = overview_header.find(
                "h2",
                class_="employer-overview__employer-overview-module__employerOverviewHeading",
            )
            if overview_heading:
                information["Company Name"] = overview_heading.text.strip()
            overview_rating = overview_header.find(
                "span",
                class_="employer-overview__employer-overview-module__employerOverviewRating",
            )
            if overview_rating:
                information["Company Rating"] = overview_rating.text.strip()

        # Extracting details
        details = overview_container.find(
            "ul",
            class_="employer-overview__employer-overview-module__employerDetails",
        )

        if details:
            details_list = details.find_all("li")
            for index, detail in enumerate(details_list):
                detail = str(detail.text).strip()
                if ":" in detail:
                    key, value = detail.split(":")
                    information[key.strip()] = value.strip()
                elif " in " in detail:
                    key, value = detail.split("in")
                    information[key.strip()] = value.strip()
                elif "Locations" in detail:
                    detail = detail.split(" ")
                    information["Branches"] = detail[0]
                elif "Employees" in detail:
                    detail = detail.split(" ")
                    information["Size"] = detail[0]
                elif index == 0:
                    information["URL"] = detail
                if index == len(details_list) - 1:
                    information["Industry"] = detail
        information_list.append(information)


def extract_interviews(soup, information_list):
    """
    Extracts interview-related information about a company.

    Args:
        soup (BeautifulSoup): The parsed HTML soup of the company page.
        information_list (list): List to store extracted information.

    Returns:
        None
    """
    experience_section = soup.find(
        "div", {"data-test": "interviewStatsContainer"}
    )
    experience_divs = experience_section.find_all("div", class_="ml-xsm")

    # Initialize lists
    experience = []
    getting_interview = []

    # Process experience data
    for div in experience_divs:
        spans = div.find_all("span", class_="mr-xsm")
        for span in spans:
            text = span.get_text(strip=True)
            percentage = span.find_next("span", class_="ml-auto").get_text(
                strip=True
            )
            if text == "Positive" or text == "Negative" or text == "Neutral":
                experience.append((text, percentage))
            else:
                getting_interview.append((text, percentage))

    # Extracting difficulty
    difficulty_section = soup.find(
        "div", {"data-test": "interviewDifficultyContainer"}
    )
    difficulty = difficulty_section.find(
        "div", class_="css-155sv15"
    ).text.strip()
    information_list[0].update(
        {
            "Difficulty": difficulty,
            "Experience": experience,
            "Interview": getting_interview,
        }
    )


def extract_career(soup, information_list):
    """
    Extracts popular career information related to a company.

    Args:
        soup (BeautifulSoup): The parsed HTML soup of the company page.
        information_list (list): List to store extracted information.

    Returns:
        None
    """
    popular_careers_div = soup.find(
        "div", {"data-test": "PopularJobRecommendations"}
    )
    if popular_careers_div:
        # Find all the career links within the div
        career_links = popular_careers_div.find_all("div", class_="p-std")
        # Extract and print the names of popular careers
        popular_careers = [link.find("a").text for link in career_links]
        information_list[0].update({"Popular Careers": popular_careers})


def save_to_csv(information_list, filename):
    """
    Saves extracted company information to a CSV file.

    Args:
        information_list (list): List containing extracted company information.
        filename (str): Name of the CSV file to save data into.

    Returns:
        None
    """
    fieldnames = [
        "Company Name",
        "Company Rating",
        "URL",
        "Size",
        "Branches",
        "Type",
        "Founded",
        "Revenue",
        "Industry",
        "Experience",
        "Interview",
        "Difficulty",
        "Popular Careers",
    ]
    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # If the file is empty, write header
        if file.tell() == 0:
            writer.writeheader()
        writer.writerows(information_list)


def main(start_page, end_page):

    # Initialize webdriver
    driver = webdriver.Chrome()

    for page in range(start_page, end_page + 1):
        url_main = f"https://www.glassdoor.com/Explore/browse-companies.htm?overall_rating_low=0&page={page}&sgoc=1011,1016&filterType=RATING_OVERALL"
        driver.get(url_main)
        # Find all initial div elements
        wait = WebDriverWait(driver, 10)
        initial_divs = wait.until(
            presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div[data-test="employer-card-single"]')
            )
        )
        for initial_div in initial_divs:
            information_list = []
            try:
                wait.until(
                    element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            'div[data-test="employer-card-single"]',
                        )
                    )
                )
                initial_div.click()
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)
                # extrat iunformations Funcation
                html_source = driver.page_source
                soup = BeautifulSoup(html_source, "lxml")

                extract_information_overview(soup, information_list)
                extract_interviews(soup, information_list)
                extract_career(soup, information_list)

                save_to_csv(information_list, "companies_info.csv")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(10)
            except ElementNotInteractableException:
                print("Element is not clickable. continuos  loop.")
                continue
            except TimeoutException:
                print(
                    f"TimeoutException: Couldn't find elements on page {page}"
                )
                continue
            except Exception as e:
                print(f"Error while trying to click: {e}")


if __name__ == "__main__":
    start_page, end_page = int(
        input("Enter the start page and end page: ").split(" ")
    )
    main(start_page, end_page)
