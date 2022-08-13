import requests
from requests import RequestException
import settings
# import git_models
from git_models import PullRequest
from logging import getLogger
logger = getLogger(__name__)


settings_data=settings.get_settings_app_data()

id=settings_data['ads']['id']
pw=settings_data['ads']['pw']
organization = settings_data['ads']['organization']
project=settings_data['ads']['project']
url_core=settings_data['ads']['url_core']
url_base=url_core + organization + '/'+ project +'/_apis/git/repositories/'
api_version=settings_data['ads']['api_version']


def get_repo_name(repo_id):
    """

    リポジトリ名を取得する。

    Args:
        repo_id (str): レポジトリのID

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        str: レポジトリ名。

    """    
    params = { 
        'api-version': api_version
    }

    url = url_base + repo_id
    res = requests.get(url, params=params, auth=(id, pw))

    res.raise_for_status()

    res_data = res.json()
    return res_data['name']

def get_repo_id(repo_name):
    """

    リポジトリIDを取得する。

    Args:
        repo_name (str): レポジトリ名

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        str: レポジトリID。

    """    
    params = { 
        'api-version': api_version
    }

    url = url_base + repo_name
    res = requests.get(url, params=params, auth=(id, pw))

    res.raise_for_status()

    res_data = res.json()
    return res_data['id']

def get_pr(repo_id, pr_id, target_branch):
    """

    PRを取得する。

    Args:
        repo_id (str): レポジトリのID
        pr_id (int): レポジトリのID
        branch_name (str): ブランチ名

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        PullRequest:取得したPR。

    """    

    params = { 
        'api-version': api_version
    }

    url = url_base + repo_id + '/pullrequests/' + str(pr_id)

    res = requests.get(url, params=params, auth=(id, pw))

    res.raise_for_status()

    res_data = res.json()

    targetRefNames=res_data['targetRefName'].split('/')
    sourceRefNames=res_data['sourceRefName'].split('/')

    if targetRefNames[2]!=target_branch: 
        return None

    pr = PullRequest(
        repo_id=res_data['repository']['id'],
        repo_name=res_data['repository']['name'],
        pr_id=res_data['pullRequestId'],
        status=res_data['status'],
        target_branch=targetRefNames[2],
        source_branch=sourceRefNames[2]
    )

    return pr

def get_pr_dict(repo_id, branch_name, status):
    """

    PR辞書を取得する。

    Args:
        repo_id (str): レポジトリのID
        branch_name (str): ブランチ名
        status (str): GITステータス

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        PR辞書(key:pr_id(int), value:PR(PullRequest))。

    """    
    pr_dict = {}

    params = { 
        'searchCriteria.status': status,
        'searchCriteria.targetRefName': 'refs/heads/'+branch_name,
        'api-version': api_version
    }

    url = url_base + repo_id + '/pullrequests'

    res = requests.get(url, params=params, auth=(id, pw))

    res.raise_for_status()

    res_data = res.json()
    for pr_data in res_data["value"]:
        targetRefNames=pr_data['targetRefName'].split('/')
        sourceRefNames=pr_data['sourceRefName'].split('/')
        pr_id=pr_data['pullRequestId']
        pr = PullRequest(
            repo_id=repo_id,
            repo_name=None,
            pr_id=pr_id,
            status=pr_data['status'],
            target_branch=targetRefNames[2],
            source_branch=sourceRefNames[2]
        )

        pr_dict[pr_id] = pr
    
    return pr_dict

def get_pr_id_list(repo_id, branch_name, status):
    """

    PRIDのリストを取得する。

    Args:
        repo_id (str): レポジトリのID
        branch_name (str): ブランチ名
        status (str): GITステータス

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        list: PRIDのリスト。

    """    
    list=[]

    params = { 
        'searchCriteria.status': status,
        'searchCriteria.targetRefName': 'refs/heads/'+branch_name,
        'api-version': api_version
    }

    url = url_base + repo_id + '/pullrequests'

    res = requests.get(url, params=params, auth=(id, pw))

    res.raise_for_status()

    res_data = res.json()
    for pull_request in res_data["value"]:
        pull_request_id = pull_request['pullRequestId']
        list.append(pull_request_id)
    
    return list

def get_pr_path_dict_by_pr(repo_id, pr_id):
    """

    PRIDのリストを取得する。

    Args:
        repo_id (str): レポジトリのID
        branch_name (str): ブランチ名

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        dict: 変更パス-変更種類辞書(key:変更パス(str), value:変更種類(str))

    """    
    params = { 
        'api-version': api_version
    }

    url_commits = url_base + repo_id + '/pullrequests/'+ str(pr_id) + '/commits'

    res_commits = requests.get(
        url_commits,
        params=params,
        auth=(id, pw)
        )

    res_commits.raise_for_status()

    path_dict = {}

    res_commits_data = res_commits.json()


    for commit in res_commits_data["value"]:
        commit_id = commit['commitId']

        url_changes = url_base + repo_id + '/commits/'+ commit_id + '/changes'

        resChanges = requests.get(
            url_changes,
            params=params,
            auth=(id, pw)
            )

        resChanges.raise_for_status()

        resChangesData = resChanges.json()

        for change in resChangesData["changes"]:
            path = change['item']['path']
            change_type = change['changeType']
            git_object_type = change['item']['gitObjectType']
            if git_object_type == 'blob':
                path_dict[path] = change_type

    return path_dict

def get_pr_path_dict_by_diff_branch(repo_id, source_branch_name, target_branch_name):
    """

    RepoIDよりのリストを取得する。

    Args:
        repo_id (str): レポジトリのID
        source_branch_name (str): マージ元ブランチ名
        target_branch_name (str): マージ先ブランチ名

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        list: PRIDのリスト。

    """    
    list=[]

    params = { 
        '$top': 100000,
        'baseVersion': target_branch_name,
        'targetVersion': source_branch_name,
        'api-version': api_version
    }

    url = url_base + repo_id + '/diffs/commits'

    res = requests.get(url, params=params, auth=(id, pw))

    res.raise_for_status()

    res_data = res.json()

    path_dict = {}
    for change in res_data["changes"]:
        path = change['item']['path']
        change_type = change['changeType']
        git_object_type = change['item']['gitObjectType']
        if git_object_type == 'blob':
            path_dict[path] = change_type

    return path_dict
