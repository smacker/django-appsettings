import appsettings
from settingsobj import Settings
settingsinst = Settings()

Settings.using_middleware = True

class SettingsMiddleware(object):
    """
    Load the settings from the database for each request (thread), do not use with caching.
    """
    def process_request(self, request):
        appsettings.autodiscover()
        settingsinst.update_from_db()
