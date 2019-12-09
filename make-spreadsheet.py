from __future__ import print_function
import pickle
import os.path
import base64
import email
import csv
import requests
import settings
import json
from datetime import datetime
from titlecase import titlecase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    # Call the Gmail API
    results = (
        service.users().messages().list(userId="me", q="in:IR is:unread").execute()
    )
    messages = results.get("messages", [])

    # handle the data
    output_data = []

    # loop through the email messages
    for message in messages:
        data = service.users().messages().get(userId="me", id=message["id"]).execute()
        data_b = base64.urlsafe_b64decode(data["payload"]["body"]["data"])
        data_s = data_b.decode("utf-8")

        # beacause there may be multiple items per email, split it up into chunks
        data_split = data_s.split(
            '<h3 style="font-weight:normal;margin:0;font-size:17px;line-height:20px;">'
        )
        for item in data_split[1:]:
            soup = BeautifulSoup(item, features="html.parser")

            # fetch the title
            title = soup.find("a", class_="gse_alrt_title").text
            title = titlecase(title)
            try:
                del title["style"]
            except TypeError:
                pass

            # fetch the url
            url_soup = soup.find("a", class_="gse_alrt_title", href=True)
            url = url_soup["href"]

            # fetch the author and publication
            auth_and_pub = str(soup.select("div[style='color:#006621']")[0])
            clean_auth_and_pub = BeautifulSoup(auth_and_pub, "lxml").text

            spl1 = clean_auth_and_pub.split("\xa0- ")
            if len(spl1) == 1:
                spl2 = spl1[0].split(" - ")
            else:
                spl2 = spl1
            author = spl2[0] if 0 < len(spl2) else ""
            journal = spl2[1] if 1 < len(spl2) else ""
            if journal in ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]:
                journal = ""
            else:
                journal = titlecase(str(journal))
            if journal[-6:] in [
                ", 2019",
                ", 2020",
                ", 2021",
                ", 2022",
                ", 2023",
                ", 2024",
                ", 2025",
            ]:
                journal = journal[:-6]

            rights = fetch_rights(journal)
            # append the data
            output_data.append((datetime.now(), author, title, journal, url, rights))
    return output_data


def fetch_rights(journal):
    if journal == "":
        return ""
    resp = requests.get("https://v2.sherpa.ac.uk/cgi/retrieve/cgi/retrieve?item-type=publication&api-key=" + settings.romeo2 + "&format=Json&limit=5&filter=[[%22title%22,%22equals%22,%22" + journal + "%22]]")
    try:
        data = resp.json()
        policies = data["items"][0]["publisher_policy"]
        policy_urls = "" 
        for policy in policies:
            for urls in policy['urls']:
                url = urls['url']
                policy_urls = url + "\n" + policy_urls
        return policy_urls
    except IndexError:
        return "" 
    except:
        raise


def make_csv(data):
    """ make a csv file with all the data """
    with open("output.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Date",
                "Prof",
                "Article",
                "Journal",
                "URL",
                "Allowed?",
                "Emailed?",
                "Status",
            ]
        )
        writer.writerows(data)


if __name__ == "__main__":
    data = main()
    make_csv(data)