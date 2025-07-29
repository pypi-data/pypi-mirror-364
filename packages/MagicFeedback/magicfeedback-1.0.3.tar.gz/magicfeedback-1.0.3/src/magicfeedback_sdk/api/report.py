from magicfeedback_sdk.utils.request import make_request


class ReportAPI:
    def __init__(self, base_url, headers, logger):
        self.base_url = base_url
        self.headers = headers
        self.logger = logger

    def get(self, filter=None):
        url = f"{self.base_url}/reporting/report"
        if filter:
            import json
            url += f"?filter={json.dumps(filter)}"
        return make_request("GET", url, self.headers, logger=self.logger)

    def update(self, contact_id, contact):
        url = f"{self.base_url}/reporting/report/{contact_id}"
        return make_request("PATCH", url, self.headers, json=contact, logger=self.logger)
