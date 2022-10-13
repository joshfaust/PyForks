import pandas as pd
import os
import requests
import urllib.parse
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import as_completed, ThreadPoolExecutor
from PyForks.trailforks import Trailforks
import re


class TrailforksUser(Trailforks):
    def get_user_info(self) -> dict:
        """
        Obtains user information via the user profile page
        and recent ridelogs

        Returns:
            dict: {username, profile, <location...>, recent rides}
        """
        user = self.username.split(" ")[0]
        user_data = {
            "username": user,
            "profile_link": f"https://www.trailforks.com/profile/{user}",
            "city": None,
            "state": None,
            "country": None,
            "recent_ride_locations": self.__get_user_recent_rides(),
        }
        (
            user_data["city"],
            user_data["state"],
            user_data["country"],
        ) = self.__get_user_city_state_country()
        return user_data

    def rescan_ridelogs_for_badges(self, ride_ids: list) -> bool:
        """
        If you add a new badge or new badges have been added that your
        old rides are currently not counting for, you can rescan them to
        and receive the credit deserved.

        Args:
            ride_ids (list): A list of ride IDs obtained via user ridelogs

        Returns:
            bool: True:Success;False:Failed
        """
        try:
            for id in ride_ids:
                uri = f"https://www.trailforks.com/ridelog/view/{id.strip()}/rescanbadges/"
                headers = {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
                }
                r = requests.get(
                    uri, allow_redirects=True, cookies=self.cookie, headers=headers
                )
            return True
        except Exception as e:
            print(e)
            return False

    def get_user_all_ridelogs(self) -> pd.DataFrame:
        """
        Scrape all of the users ridelogs and throw that into a pandas
        dataframe.

        Returns:
            pd.DataFrame: Pandas dataframe of all rides ever subject to the user
        """
        uri = f"https://www.trailforks.com/profile/{self.uri_encode(self.username)}/ridelog/?sort=l.timestamp&activitytype=1&year=0&bikeid=0&raceid=0"
        r = requests.get(uri)
        df = pd.read_html(r.text)[0]
        with open("data.html", "w") as f:
            f.write(r.text)
        df["ridelog_link"] = self.__get_ridelog_links(r.text)
        df["ride_id"] = self._parse_ride_ids(df.ridelog_link.to_list())
        return df

    def __get_ridelog_links(self, html_data: str) -> list:
        """
        Parses the ridelog links from the users ridelog data

        Args:
            html_data (str): HTML of the users ridelog page

        Returns:
            list: List of unique ridelog links
        """
        soup = BeautifulSoup(html_data, "html.parser")
        table = soup.find("table")

        links = set()
        for tr in table.findAll("tr"):
            trs = tr.findAll("td")
            for each in trs:
                try:
                    link = each.find("a")["href"]
                    if "ridelog/view" in link and "achievements" not in link:
                        links.add(link)
                except:
                    pass
        return list(links)

    def _parse_ride_ids(self, ridelog_links: list) -> list:
        """
        Parses out the ridelog IDs from a ridelog link

        Args:
            ridelog_links (list): A list of ridelog links

        Returns:
            list: List of unique ride IDs
        """

        rex = re.compile(r"view\/(\d{8})/$")
        ids = []
        for link in ridelog_links:
            try:
                ids.append(rex.search(link).group(1))
            except AttributeError as e:
                pass
        return ids

    def __get_user_city_state_country(self) -> tuple:
        """
        From HTML Source of the users profile page, parse out the
        city, state, and country attributes.

        Returns:
            tuple: (city, state, country)
        """

        user_uri = (
            f"https://www.trailforks.com/profile/{self.uri_encode(self.username)}"
        )
        page = requests.get(user_uri)
        soup = BeautifulSoup(page.text, "html.parser")

        city = "unknown"
        state = "unknown"
        country = "unknown"
        # get the users city and state
        try:
            location = soup.find("li", class_="location").getText()
            city, state = location.strip().split(",")
            city = city.strip()
            state = state.strip()
            country = "USA"
        except AttributeError as e:
            pass
        except ValueError as e:
            try:
                city, state, country = location.strip().split(",")
                city = city.strip()
                state = "unknown"
                country = country.strip()
            except Exception as e:
                state = location.strip()

        return (city, state, country)

    def __get_user_recent_rides(self) -> list:
        """
        Obtain a list of the most recent rides by region

        Returns:
            list: List of unique regions
        """
        # get the users most recent (current year) riding locations
        try:
            activity_uri = f"https://www.trailforks.com/profile/{self.uri_encode(self.username)}/ridelog/?sort=l.timestamp&activitytype=1&year=0&bikeid=0"
            activity_df = pd.read_html(activity_uri)[0]
            activity_df = activity_df.fillna('')
            recent_ride_locations = activity_df.location.unique().tolist()
        except ValueError as e:
            recent_ride_locations = []

        return recent_ride_locations

    def get_user_gear(self) -> list:
        """
        Get the users bike/gear they're using

        Requires Authorization:
            True

        Returns:
            list: a list of tuples [(brand, model), (brand, model)]
        """
        self.check_cookie()
        uri = f"https://www.trailforks.com/profile/{self.username}/bikes/"
        r = requests.get(uri, cookies=self.cookie)
        try:
            df = pd.read_html(r.text)[0]
            df = df[df["model"].notna()]
            user_gear = list(zip(df.brand, df.model))
        except ValueError as e:
            user_gear = []
        return user_gear
        