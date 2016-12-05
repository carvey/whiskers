import argparse

class CommandLineOptions:
    """
    Manages any command line options passed to whiskers
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Whiskers Settings")
        self.args = None

    def get(self, setting_name):
        if not hasattr(self.args, setting_name):
            self.args = self.parser.parse_args()

        return getattr(self.args, setting_name)
