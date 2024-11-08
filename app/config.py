import os

class App:
    """
    The App class defines basic configurations and attributes for the application.

    Attributes:
    version (str): Specifies the current version of the application.
    cache_path (str): Defines the default path where cached files will be stored.
    """
    version = '1.0.0'
    app_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(app_dir, 'cache')