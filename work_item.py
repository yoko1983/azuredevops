import requests
from requests import RequestException
import datetime
import os
import json
import urllib
import settings
import git_repo
from logging import getLogger

settings_data=settings.get_settings_app_data()

logger = getLogger(__name__)

id=settings_data['ads']['id']
pw=settings_data['ads']['pw']
organization = settings_data['ads']['organization']
project=settings_data['ads']['project']
url_core=settings_data['ads']['url_core']
url_base=url_core + organization + '/'+ project +'/_apis/wit/'
api_version=settings_data['ads']['api_version']

work_item_field_date='Microsoft.VSTS.CodeReview.AcceptedDate'

def convert_str_to_datetime(str):
    """

    文字列のISO8601のUTC（協定世界時）をdatetimeに変換

    Args:
        str (str): ISO8601のUTC（協定世界時）の文字列

    Returns:
        datetime

    """    
    # yyyymmddhhmmss.を設定
    yyyymmddhhmmss= str[:20]
    # SZ/SSZ/SSSZのうちZをトリムし、S/SS/SSSに対して固定値3桁でゼロパティングして設定
    sss=str[20:].replace('Z', '').rjust(3, '0')
    # yyyymmddhhmmss.SSS+00:00を返却
    return datetime.datetime.fromisoformat(yyyymmddhhmmss + sss + '+00:00')
    

def get_nowdate(work_item_id):
    """

    日付を取得する。

    Args:
        work_item_id (int): WorkItemのID

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        datetime: 取得した日付

    """
    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.get(
        url,
        params=params,
        auth=(id, pw)
        )

    res.raise_for_status()

    res_data = res.json()
    
    return res_data["fields"][work_item_field_date]

def get_pr_id_dict(work_item_id):
    """

    PRリンクよりPRリストを取得する。

    Args:
        work_item_id (int): WorkItemのID

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        PRID-リポジトリID辞書(key:pr_id(int), value:repo_id(str))

    """

    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.get(
        url,
        params=params,
        auth=(id, pw)
        )

    res.raise_for_status()

    res_data = res.json()
    pr_dict = {}
    for relation in res_data["relations"]:
        if relation['rel'] == 'ArtifactLink':
            if relation['attributes']['name'] == 'Pull Request':
                pr_url = relation['url']
                pr_url_base_len=len("vstfs:///Git/PullRequestId/")
                pr_url_parts = urllib.parse.unquote(pr_url[pr_url_base_len:])
                pr = pr_url_parts.split('/')
                pr_id=int(pr[2])
                repo_id=pr[1]
                pr_dict[pr_id] = repo_id

    return pr_dict

def get_repo_list(work_item_id):
    """

    リポジトリリンク（ブランチリンク）よりリポジトリIDリストを取得する。

    Args:
        work_item_id (int): WorkItemのID

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        str[]: リポジトリIDのリスト

    """
    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.get(
        url,
        params=params,
        auth=(id, pw)
        )

    res.raise_for_status()

    res_data = res.json()
    repo_list=[]
    for relation in res_data["relations"]:
        if relation['rel'] == 'ArtifactLink':
            if relation['attributes']['name'] == 'Branch':
                repo_url = relation['url']
                repo_url_base_len=len("vstfs:///Git/Ref/")
                repo_url_parts = urllib.parse.unquote(repo_url[repo_url_base_len:])
                repo_name = repo_url_parts.split('/')
                repo_list.append(repo_name[1])

    return repo_list

def get_attachement(id):
    """

    添付ファイルを取得する。

    Args:
        id (str): ファイルID

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        str: ファイルパス

    """
    params = { 
        'download' : True,
        'api-version': api_version
    }

    url = url_base + 'attachments/' + id

    res = requests.get(
        url,
        params=params,
        auth=(id, pw)
        )

    res.raise_for_status()

    save_file_name = id + '.xlsx'
    save_file_path = os.path.join('./', save_file_name)
    with open(save_file_path, 'wb') as save_file:
        save_file.write(res.content)

    return save_file_path

def get_file(work_item_id, file_name):
    """

    ファイル添付リンクより添付ファイルを取得する。
    なお、同名ファイルの場合は、最新作成日付のファイルを取得する。

    Args:
        work_item_id (int): WorkItemのID
        file_name (str): ファイル名

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        str: ファイルパス

    """
    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.get(
        url,
        params=params,
        auth=(id, pw)
        )
    
    res.raise_for_status()

    res_data = res.json()
    file_id_newest = None
    file_datetime_newest = datetime.datetime.fromisoformat('1900-01-01T00:00:00.000+00:00')
    for relation in res_data["relations"]:
        if relation['rel'] == 'AttachedFile':
            file_url = relation['url']
            _file_name = relation['attributes']['name']
            created_date = relation['attributes']['resourceCreatedDate']
            file_datetime = convert_str_to_datetime(created_date)
            if _file_name == file_name:
                if file_datetime_newest < file_datetime:
                    file_url_splited = file_url.split('/')
                    file_id_newest = file_url_splited[len(file_url_splited)-1]
                    file_datetime_newest = file_datetime

    if file_id_newest == None:
        return None

    return get_attachement(file_id_newest)

def get(work_item_id):
    """

    WorkItemのJSON形式データを取得する。

    Args:
        work_item_id (int): WorkItemのID

    Raises:
        RequestException: HttpRequestに失敗した場合

    Returns:
        Json形式のデータ

    """
    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.get(
        url,
        params=params,
        auth=(id, pw)
        )

    res.raise_for_status()

    res_data = res.json()

    return json.dumps(res_data) 

def update_repolink(work_item_id, repo_name, branch_name):
    """

    リポジトリリンク（ブランチリンク）を追加する。

    Args:
        work_item_id (int): WorkItemのID
        repo_name (str): リポジトリ名
        branch_name (str): ブランチ名

    Raises:
        RequestException: HttpRequestに失敗した場合

    """

    headers = { 
        'Content-Type': 'application/json-patch+json'
    }

    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    repo_id = git_repo.get_repo_id(repo_name)
    if repo_id == None:
        return None

    url_parts = urllib.parse.quote(project +'/' + repo_id + '/GB' + branch_name)
    data = { 
        'op': 'add',
        'path': '/relations/-',
        'value': {
            'rel': 'ArtifactLink',
            'url': 'vstfs:///Git/Ref/'+ url_parts,
            'attributes': {
                'comment': repo_name,
                'name': 'Branch'
            }
        }
    }
    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.patch(
        url,
        headers=headers,
        params=params,
        json=[data],
        auth=(id, pw)
        )

    res.raise_for_status()

    return True


def update_nowdate(work_item_id):
    """

    現在時刻で日付を更新する。

    Args:
        arg1 (int): WorkItemのID
        arg2 (str): リポジトリ名
        arg3 (str): ブランチ名

    Raises:
        RequestException: HttpRequestに失敗した場合

    """

    headers = { 
        'Content-Type': 'application/json-patch+json'
    }

    params = { 
        '$expand': 'all',
        'api-version': api_version
    }

    dt_now = datetime.datetime.now()
    data = { 
        'op': 'replace',
        'path': '/fields/' + work_item_field_date,
        'value': dt_now.isoformat(timespec='seconds')
    }

    url = url_base + 'workitems/' +str(work_item_id)

    res = requests.patch(
        url,
        headers=headers,
        params=params,
        json=[data],
        auth=(id, pw)
        )

    res.raise_for_status()

    return True

