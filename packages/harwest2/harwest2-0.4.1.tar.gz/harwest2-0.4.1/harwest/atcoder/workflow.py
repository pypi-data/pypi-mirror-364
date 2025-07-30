from harwest.abstractworkflow import AbstractWorkflow
from harwest.atcoder.client import AtcoderClient


class AtcoderWorkflow(AbstractWorkflow):
    def __init__(self, user_data):
        super().__init__(AtcoderClient(user_data["atcoder"]), user_data)

    @staticmethod
    def setup(handle):
        return {
            "handle": handle,
        }

    def enrich_submission(self, submission):
        problem_full_name = self.client.get_problem_name(submission["submission_url"])
        submission["problem_index"] = problem_full_name.split("-")[0].strip()
        submission["problem_name"] = problem_full_name.split("-", 1)[1].strip()
