import pandas as pd
from pymongo import MongoClient
import re
import numpy as np
from bs4 import BeautifulSoup
import requests

df = pd.read_csv("path to csv file")

# Remove 'Overview' from 'Company Name'
df["Company Name"] = df["Company Name"].apply(lambda x: x.split(" ")[0])

# Remove non-numeric characters from 'Company Rating'
df["Company Rating"] = df["Company Rating"].str.extract("(\d+\.\d+)")

# Remove '%' sign and convert to float in 'Experience' column
df["Experience"] = df["Experience"].str.replace("%", "")


# Remove brackets and quotes from 'Popular Careers'
df["Popular Careers"] = df["Popular Careers"].str.replace("[\[\]']", "")


def remove_special_chars(text):
    """
    Remove special characters from the text.

    Parameters:
        text (str): The text from which special characters need to be removed.

    Returns:
        str: Text with special characters removed.
    """
    return re.sub(r"[^\w\s]", "", text)


df["Experience"] = df["Experience"].apply(remove_special_chars)


def extract_data_from_url(url):
    # Prepend 'http://' or 'https://' if scheme is missing
    url = str(url)
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        html_content = requests.get(url, timeout=20)
        soup = BeautifulSoup(html_content.text, "html.parser")

        # Extract meta tags
        meta_tags = soup.find_all("meta")

        # Extract title tag
        title_tag = soup.find("title")
        title = title_tag.text if title_tag else "No title found"

        # Extract description from meta tags
        description = None
        for tag in meta_tags:
            if tag.get("name", "").lower() == "description":
                description = tag.get("content")
                break

        og_image_tag = soup.find("meta", property="og:image")
        og_image = (
            og_image_tag.get("content") if og_image_tag else "No og:image found"
        )

        return title, description, og_image
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return "Error", "Error", "Error"


def convert_to_dict(string):
    # Remove unnecessary characters and split the string to get individual tuples
    tuples = string.strip("[]()").split("), (")

    # Initialize an empty dictionary
    result_dict = {}

    # Iterate over each tuple
    for tuple_str in tuples:
        # Split each tuple into key and value
        key, value = tuple_str.split(", ")
        # Remove any surrounding quotes from the key
        key = key.strip("'")
        # Remove any surrounding quotes from the value
        value = value.strip("'")
        # Add key-value pair to the dictionary
        result_dict[key] = value

    return result_dict


# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://admin:<EMAIL>/JobPostings?retryWrites=true&w=majority"
)
db = client["JobPostings"]
collection = db["Companies"]


for index, row in df.iterrows():

    # Check if company already exists
    if not collection.find_one(
        {"company_name": row["Company Name"], "Revenue": {"$exists": False}}
    ):
        # prepare columns
        Experience = row["Experience"].split(" ")
        Positive = Experience[1]
        Negative = Experience[3]
        Neutral = Experience[5]
        dict_interview = convert_to_dict(row["Interview"])
        title, description, og_image = extract_data_from_url(row["URL"])
        if not pd.isnull(row["Popular Careers"]):
            list_Popular_Careers = row["Popular Careers"].strip("[]()")
            list_Popular_Careers = list_Popular_Careers.split(",")
        else:
            list_Popular_Careers = None
            # Prepare document to insert
            company_data = {
                "company_name": row["Company Name"],
                "Revenue": row["Revenue"],
                "Type": row["Type"],
                "Num_Branches": row["Branches"],
                "rate": row["Company Rating"],
                "Interviews": {
                    "Experience": {
                        "Positive": Positive,
                        "Negative": Negative,
                        "Neutral": Neutral,
                    },
                    "Getting an Interview": dict_interview,
                    "Difficulty": row["Difficulty"],
                },  # Assuming interviews data is not available in CSV
                "Popular Careers": list_Popular_Careers,  # Assuming 'Popular Careers' is a column in CSV
                "Size": row["Size"],
                "Industry": row["Industry"],
                "Company_url": row["URL"],
                "title": title,
                "description": description,
                "og_image": og_image,
            }
            # Insert document into MongoDB
            collection.insert_one(company_data)
            print(f"Inserted {row['Company Name']} into Companies collection.")
    else:
        print(f"{row['Company Name']} already exists in Companies collection.")

print("Data insertion complete.")
