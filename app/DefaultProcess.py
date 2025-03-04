from qrlib.QRProcess import QRProcess
from qrlib.QRDecorators import run_item
from qrlib.QRRunItem import QRRunItem
# from DefaultComponent import DefaultComponent
from imdbcomponent import ImdbComponent
from EmailComponent import EmailComponent
from qrlib.QRDecorators import run_item

class DefaultProcess(QRProcess):

    def __init__(self):
        super().__init__()
        self.run_item = QRRunItem(logger_name="IMDB Bot")
        self.notify(self.run_item)
        self.logger = self.run_item.logger
        self.imdb_component = ImdbComponent() 
        self.email_component = EmailComponent(self.logger)
        self.register(self.imdb_component) 
        self.register(self.email_component) 
        self.data = []

    @run_item(is_ticket=False)
    def before_run(self, *args, **kwargs):
        recipient_email = "shrijanabudhathoki2001@gmail.com"
        result_path = "C:\\Users\\Shrijana\\Downloads\\bot-starter-kit-v2.0\\bot-starter-kit-v2.0\\movies_data.xlsx"
        excel_file_path = "C:\\Users\\Shrijana\\Downloads\\bot-starter-kit-v2.0\\bot-starter-kit-v2.0\\files\\Movie list.xlsx"
        sheet_name = "Movies list"
        movie_names = self.imdb_component.get_movie_name(excel_file_path, sheet_name)
        self.imdb_component.open_website()
        # Process each movie
        for movie_name in movie_names:
            self.imdb_component.search_movie(movie_name)
            movie_data = self.imdb_component.extract_movie_data(movie_name)
            self.imdb_component.save_to_db(movie_data)
        self.imdb_component.save_in_excel()
        self.email_component.send_email_with_attachment(result_path, subject="IMDB Scraped Data", body="Attached is the scraped movie data from IMDB")
        

    @run_item(is_ticket=False, post_success=False)
    def before_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        # run_item: QRRunItem = kwargs["run_item"]
        # self.notify(run_item)
        pass
    @run_item(is_ticket=True)
    def execute_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)        

    @run_item(is_ticket=False, post_success=False)
    def after_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

    @run_item(is_ticket=False, post_success=False)
    def after_run(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

        # self.default_component.logout()
        # self.imdb_component.close()
        # self.send_email()
 
    def execute_run(self):
        pass
        # for movie in self.data:
        #     self.before_run_item(movie)
        #     self.execute_run_item(movie)
        #     self.after_run_item(movie)

    