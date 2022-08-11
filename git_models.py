class PullRequest():
    repo_id=None
    repo_name=None
    pr_id=None
    status=None
    source_branch=None
    target_branch=None

    def __init__(self, repo_id:str, repo_name:str, pr_id:int, status:str, source_branch:str, target_branch:str):
        self.repo_id = repo_id
        self.repo_name = repo_name
        self.pr_id = pr_id
        self.status = status
        self.source_branch = source_branch
        self.target_branch = target_branch
