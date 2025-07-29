from magicfeedback_sdk.api.campaigns import CampaignsAPI
from magicfeedback_sdk.api.contacts import ContactsAPI
from magicfeedback_sdk.api.feedback import FeedbackAPI
from magicfeedback_sdk.api.metrics import MetricsAPI
from magicfeedback_sdk.api.report import ReportAPI
from magicfeedback_sdk.auth import AuthManager
from magicfeedback_sdk.logging_config import configure_logger


class MagicFeedback:
    def __init__(self, user: str, password: str, base_url: str = "https://api.magicfeedback.io", api_key: str = "AIzaSyAKcR895VURSQZSN2T_RD6jX_9y5HRmH80"):
        self.logger = configure_logger()
        self.base_url = base_url
        self.api_key = api_key
        
        self.auth = AuthManager(api_key, self.logger, user, password)

        # APIs
        self.feedbacks = FeedbackAPI(self.base_url, self.get_headers, self.logger)
        self.contacts = ContactsAPI(self.base_url, self.get_headers, self.logger)
        self.campaigns = CampaignsAPI(self.base_url, self.get_headers, self.logger)
        self.metrics = MetricsAPI(self.base_url, self.get_headers, self.logger)
        self.reports = ReportAPI(self.base_url, self.get_headers, self.logger)

    def set_logging(self, level):
        self.logger.setLevel(level)

    def get_headers(self):
        return {"Authorization": f"Bearer {self.auth.get_valid_token()}"}
