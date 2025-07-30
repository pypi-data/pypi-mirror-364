from getpass import getpass

from harwest.abstractworkflow import AbstractWorkflow
from harwest.codeforces.client import CodeforcesClient


class CodeforcesWorkflow(AbstractWorkflow):
    def __init__(self, user_data):
        super().__init__(CodeforcesClient(user_data["codeforces"]), user_data)

    @staticmethod
    def setup(handle):
        print(
            "\U0001f510",
            "To access the platform's data, we’ll need your API credentials",
            "\n",
        )
        print(
            "You can retrieve your API Key and Secret by following this instructions:"
            "\n"
            "\U0001f449 https://codeforces.com/apiHelp/"
            "\n",
        )
        api_key = getpass("> Could you please enter your API Key? ")
        api_secret = getpass("> And your API Secret? ")

        return {
            "handle": handle,
            "api_key": api_key,
            "api_secret": api_secret,
        }

    def enrich_submission(self, submission):
        pass
