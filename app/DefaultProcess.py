from qrlib.QRProcess import QRProcess
from qrlib.QRDecorators import run_item
import logging
from imdbcomponent import ImdbComponent
from EmailComponent import EmailComponent


class DefaultProcess(QRProcess):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ImdbScraper")
        self.imdb_component = ImdbComponent()
        self.email_component = EmailComponent()
        self.register(self.imdb_component)
        self.register(self.email_component)
        self.data = []

    @run_item(is_ticket=False)
    def before_run(self, *args, **kwargs):
        """Prepares everything before execution. Runs once before all items."""
        self.logger.info("Starting the IMDB scraping process...")
        self.excel_file_path = "C:\\Users\\Shrijana\\Downloads\\bot-starter-kit-v2.0\\bot-starter-kit-v2.0\\files\\Movie list.xlsx"
        self.sheet_name = "Movies list"

        # Get the list of movies
        self.movie_names = self.imdb_component.get_movie_name(
            self.excel_file_path, self.sheet_name
        )

        # Open the website
        self.imdb_component.open_website()

    @run_item(is_ticket=False, post_success=False)
    def before_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        # run_item: QRRunItem = kwargs["run_item"]
        # self.notify(run_item)
        pass

    @run_item(is_ticket=True)
    def execute_run_item(self, *args, **kwargs):
        """Processes a single movie entry. Runs for each movie in the list."""

        if not self.movie_names:
            self.logger.warning("No movies found to process.")
            return

        for movie_name in self.movie_names:
            self.logger.info(f"Processing movie: {movie_name}")
            self.imdb_component.search_movie(movie_name)
            movie_data = self.imdb_component.extract_movie_data(movie_name)

            if movie_data:
                self.imdb_component.save_to_db(movie_data)
                self.data.append(movie_data)
            else:
                self.logger.warning(f"No exact match found for {movie_name}")

    @run_item(is_ticket=False, post_success=False)
    def after_run_item(self, *args, **kwargs):
        """Performs cleanup tasks after processing each movie."""
        # run_item: QRRunItem = kwargs["run_item"]
        # self.notify(run_item)
        # self.logger.info("Completed processing one movie entry.")
        pass

    @run_item(is_ticket=False, post_success=False)
    def after_run(self, *args, **kwargs):
        """Runs after all movies are processed. Performs final cleanup."""

        # Save data to Excel and close the browser
        if self.data:
            self.logger.info("Saving extracted data to Excel...")
            self.imdb_component.save_in_excel()
        else:
            self.logger.warning("No data to save.")

        self.imdb_component.close_bowser()

        # Send email with the result
        self.email_component.send_email_with_attachment()

    def execute_run(self):
        """Main execution method which handles the entire process."""
        self.execute_run_item()