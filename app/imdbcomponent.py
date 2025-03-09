from qrlib.QRComponent import QRComponent
from RPA.Browser.Selenium import Selenium
import sqlite3
import pandas as pd
import time


class ImdbComponent(QRComponent):
    def __init__(self):
        super().__init__()
        self.browser = Selenium(auto_close=False)
        self.db_name = "data/movies.db"
        self.initialize_db()

    def initialize_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT,
            rating TEXT,
            storyline TEXT,
            genres TEXT,
            review1 TEXT,
            review2 TEXT,
            review3 TEXT,
            review4 TEXT,
            review5 TEXT,
            status TEXT
            )
        """)
        conn.commit()
        conn.close()

    def open_website(self):
        try:
            self.browser.open_available_browser(
                url="https://www.imdb.com/", headless=False
            )

        except Exception as e:
            raise e

    def get_movie_name(self, excel_file_path, sheet_name="Movies list"):
        try:
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            movie_names = df["Movie"].tolist()
            return movie_names
        except Exception as e:
            self.logger(f"Error reading Excel file: {e}")

    def search_movie(self, movie_name):
        try:
            self.browser.input_text("id= suggestion-search", movie_name)
            # self.browser.click_button('id=suggestion-search-button')
            self.browser.press_keys("id=suggestion-search", "ENTER")

        except Exception as e:
            raise e

    # Function to scroll incrementally until the element is found
    def scroll_until_element_found(self, xpath, max_attempts=10):
        attempts = 0
        while attempts < max_attempts:
            try:
                # Check if the element is visible
                if self.browser.is_element_visible(xpath):
                    return True
            except Exception as e:
                raise e

            # Scroll down a bit
            self.browser.execute_javascript("window.scrollBy(0, 500);")
            time.sleep(1)  # Wait for the content to load
            attempts += 1

        return False

    def extract_movie_data(self, movie_name):
        """Extract movie data from the search results."""
        try:
            # Check if the movie list is shown ot not
            if not self.browser.is_element_visible("css=.ipc-metadata-list"):
                return {
                    "movie_name": movie_name,
                    "rating": "Not found",
                    "storyline": "Not found",
                    "genres": "Not found",
                    "review1": "Not found",
                    "review2": "Not found",
                    "review3": "Not found",
                    "review4": "Not found",
                    "review5": "Not found",
                    "status": "No exact match found",
                }
            # Restrict search to Movies only
            try:
                self.browser.click_element(
                    "css=.more-results-ft-chip.ipc-chip.ipc-chip--on-base"
                )
            except Exception as e:
                raise e

            # Find all search results
            results = self.browser.find_elements("css=.ipc-metadata-list-summary-item")

            # Filter exact matches
            exact_matches = []
            for result in results:
                try:
                    # Extract title
                    title_element = result.find_element(
                        "css selector", ".ipc-metadata-list-summary-item__t"
                    )
                    title = title_element.text.strip()

                    # Extract year
                    year_elements = result.find_elements(
                        "css selector", ".ipc-metadata-list-summary-item__li"
                    )
                    year = None
                    for year_elem in year_elements:
                        year_text = year_elem.text.strip()
                        if year_text.isdigit():
                            year = int(year_text)
                            break  # Stop at first valid year

                    if year is None:
                        continue  # Skip if no valid year is found

                    # Check for exact match (case insensitive)
                    if movie_name.lower() == title.lower():
                        exact_matches.append((result, year))

                except Exception as e:
                    raise e

            if not exact_matches:
                return {
                    "movie_name": movie_name,
                    "rating": "Not found",
                    "storyline": "Not found",
                    "genres": "Not found",
                    "review1": "Not found",
                    "review2": "Not found",
                    "review3": "Not found",
                    "review4": "Not found",
                    "review5": "Not found",
                    "status": "No exact match found",
                }

            # Select the most recent movie
            latest_movie = max(exact_matches, key=lambda x: x[1])[0]
            latest_movie.click()

            # Extract rating
            try:
                rating = self.browser.get_text("css=.imUuxf").strip()
            except Exception as e:
                rating = f"Not found: {e}"

            # Extract storyline
            storyline_xpath = "//div[@data-testid='storyline-plot-summary']//div[@class='ipc-html-content-inner-div']"
            storyline = "Not found"
            if self.scroll_until_element_found(storyline_xpath):
                try:
                    self.browser.wait_until_element_is_visible(
                        storyline_xpath, timeout=20
                    )
                    storyline = self.browser.get_text(storyline_xpath).strip()
                except Exception as e:
                    raise e

            # Extract genres
            genres_string = "Not found"
            genre_xpath = (
                "//li[@data-testid='storyline-genres']//ul[@role='presentation']//li"
            )
            if self.browser.is_element_visible(genre_xpath):
                genre_elements = self.browser.find_elements(genre_xpath)
                if genre_elements:
                    genres_string = ", ".join(
                        [elem.text.strip() for elem in genre_elements]
                    )

            # Extract reviews
            reviews = self.extract_reviews()
            reviews = reviews + ["Not found"] * (
                5 - len(reviews)
            )  # Fill missing reviews with "Not found"

            # Scroll back to the top of the page for the next movie
            self.browser.execute_javascript("window.scrollTo(0, 0);")

            return {
                "movie_name": movie_name,
                "rating": rating,
                "storyline": storyline,
                "genres": genres_string,
                "review1": reviews[0],
                "review2": reviews[1],
                "review3": reviews[2],
                "review4": reviews[3],
                "review5": reviews[4],
                "status": "Success",
            }
        except Exception as e:
            raise e

    def extract_reviews(self):
        """Extract the first 5 user reviews. Handles cases where no reviews exist."""
        try:
            reviews_link_xpath = (
                '//div[@data-testid= "reviews-header"]//h3[@class = "ipc-title__text"]'
            )

            # Check if review section exists before clicking
            if not self.browser.is_element_visible(reviews_link_xpath):
                return []  # No reviews found, return empty list

            self.browser.scroll_element_into_view(reviews_link_xpath)
            self.browser.click_element(reviews_link_xpath)

            # Extract review texts
            review_elements = self.browser.find_elements(
                '//div[@data-testid = "review-overflow"]//div[@class = "ipc-html-content-inner-div"]'
            )

            if not review_elements:
                return []  # No reviews found

            reviews = [
                self.browser.get_text(review_element).strip()
                for review_element in review_elements[:5]
            ]
            return reviews
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []

    def save_to_db(self, data):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO movies (
                       movie_name, rating, storyline,genres,review1, review2, review3, review4, review5,status
                       ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
            (
                data["movie_name"],
                data.get("rating", ""),
                data.get("storyline", ""),
                data.get("genres", ""),
                data.get("review1", ""),
                data.get("review2", ""),
                data.get("review3", ""),
                data.get("review4", ""),
                data.get("review5", ""),
                data.get("status", ""),
            ),
        )
        conn.commit()
        conn.close()

    def save_in_excel(self):
        # Connect to the database
        db_path = "data/movies.db"
        conn = sqlite3.connect(db_path)

        # Query the movies table
        query = "SELECT * FROM movies;"
        df = pd.read_sql_query(query, conn)

        # Save the data to an Excel file
        excel_path = "movies_data.xlsx"
        df.to_excel(excel_path, index=False)
        conn.close()

    def close_bowser(self):
        self.browser.close_all_browsers()
