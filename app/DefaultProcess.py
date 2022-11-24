from qrlib.QRProcess import QRProcess
from qrlib.QRDecorators import run_item_tt, run_item_tf
from DefaultComponent import DefaultComponent
from RPA.Browser.Selenium import Selenium

class DefaultProcess(QRProcess):
    
    def __init__(self):
        super().__init__()
        self.default_component = DefaultComponent(self)
        self.data = []


    @run_item_tt()
    def execute_run_item(self, *args, **kwargs):
        self.default_component.test()

    @run_item_tf()
    def before_run(self, *args, **kwargs):  
        self.default_component.login()
        self.data = ["a","b"]

    @run_item_tf()
    def after_run(self, *args, **kwargs):
        self.default_component.logout()
    
    @run_item_tf()
    def before_run_item(self, *args, **kwargs):
        self.run_item.logger.info(f"In pre run item = {args[0]}")

    @run_item_tf()
    def after_run_item(self, *args, **kwargs):
        self.run_item.logger.info(f"In post run item = {args[0]}")

    def run(self):
        for item in self.data:
            self.before_run_item(item)
            self.execute_run_item(item)
            self.after_run_item(item)


