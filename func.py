from requests import RequestException
import work_item
import git_repo
from logging import getLogger

logger = getLogger(__name__)

def get_pr_dict(work_item_id, branch_name):
    """

    WorkItemに設定されたPRについてPR辞書を取得する。

    Args:
        work_item_id (str): WorkItemのID
        branch_name (str): ターゲットブランチ名

    Returns:
        PR辞書(key:pr_id(int), value:PR(PullRequest))。取得不可の場合はNone。

    """   
    try:
        work_item_pr_id_dict = work_item.get_pr_id_dict(work_item_id)

        # WorkItemに設定されたPRのリポジトリ一覧(repo_list)を作成(重複リポジトリは排除)する
        # pr_list(repo_id(str)) 
        repo_list = []
        for pr_id in work_item_pr_id_dict.keys():
            repo_id = work_item_pr_id_dict[pr_id]
            repo_list.append(repo_id)
        repo_list = list(set(repo_list))

        # リポジトリ一覧(repo_list)の全リポジトリについて、
        # GitRepoを照会し、該当するターゲットブランチ向けの全PRを取得の上、
        # GitRepoPR辞書(git_repo_list_pr_dict)を作成する
        # git_repo_list_pr_dict(key:pr_id(int)、value:PR(PullRequest))
        git_repo_list_pr_dict = {}
        for repo_id in repo_list:
            git_repo_pr_dict = git_repo.get_pr_dict(repo_id, branch_name, 'all')
            for pr_id in git_repo_pr_dict.keys():
                pr = git_repo_pr_dict[pr_id]
                git_repo_list_pr_dict[pr_id] = pr

        # WorkItemに設定されたPRについて、
        # GitRepoPR辞書(git_repo_list_pr_dict)をもとにPR辞書(pr_dict)を作成する
        # pr_dict(key:pr_id(int)、value:PR(PullRequest)) 
        pr_dict = {}
        for pr_id in work_item_pr_id_dict.keys():
            pr = git_repo_list_pr_dict.get(pr_id)
            if pr != None and pr.target_branch == branch_name:
                pr_dict[pr_id] = pr
    except RequestException as e:
        logger.error(e)
        logger.error("request failed. error=(%s)", e.response.text)
        raise e
    except Exception as e:
        logger.error(e)
        raise e

    return pr_dict

def print_changed_filepath_dict_by_pr(work_item_id, branch_name):
    """

    WorkItemに設定されたPRより変更パス-変更種類辞書を作成し、ログ出力する

    Args:
        work_item_id (str): WorkItemのID
        branch_name (str): ターゲットブランチ名

    """   
    try:
        # WorkItemに設定されたPRよりPR辞書を取得
        pr_dict = get_pr_dict(work_item_id, branch_name)

        # PR辞書より、リポジトリID-PRIDリスト辞書を作成する
        repo_id_pr_id_list_dict = {}
        for pr_id in pr_dict.keys():
            pr = pr_dict[pr_id]
            pr_id_list = repo_id_pr_id_list_dict.get(pr.repo_id)
            if pr_id_list == None:
                pr_id_list = []
            pr_id_list.append(pr_id)
            repo_id_pr_id_list_dict[pr.repo_id] = pr_id_list
        
        return print_changed_filepath_dict(repo_id_pr_id_list_dict)
    except RequestException as e:
        logger.error(e)
        logger.error("request failed. error=(%s)", e.response.text)
        raise e
    except Exception as e:
        logger.error(e)
        raise e

def print_changed_filepath_dict_by_repo(work_item_id, branch_name):
    """

    WorkItemに設定されたリポジトリより変更パス-変更種類辞書を作成し、ログ出力する

    Args:
        work_item_id (str): WorkItemのID
        branch_name (str): ターゲットブランチ名

    """   
    try:
        repo_id_list = work_item.get_repo_list(work_item_id)
        
        repo_id_pr_id_list_dict = {}
        for repo_id in repo_id_list:
            pr_id_list = git_repo.get_pr_id_list(repo_id, branch_name, 'completed')
            if len(pr_id_list) != 0:
                repo_id_pr_id_list_dict[repo_id] = pr_id_list

        return print_changed_filepath_dict(repo_id_pr_id_list_dict)
    except RequestException as e:
        logger.error(e)
        logger.error("request failed. error=(%s)", e.response.text)
        raise e
    except Exception as e:
        logger.error(e)
        raise e


def print_changed_filepath_dict(repo_id_pr_id_list_dict:dict):
    """

    リポジトリID-PRID辞書より、変更パス-変更種類辞書を作成し、ログ出力する

    Args:
        repo_id_pr_id_list_dict (dict): レポジトリID-PRIDリスト辞書

    """  

    try:
            
        for repo_id in repo_id_pr_id_list_dict.keys():
            logger.info('■' + git_repo.get_repo_name(repo_id))

            pr_id_list = repo_id_pr_id_list_dict[repo_id]

            # 古いPRIDから順に処理するようにするため、PR_IDの昇順ソートを行う
            pr_id_list.sort()

            # PRID毎に変更パス-変更種類辞書を取得し、変更パス-変更種類辞書リストを取得する。、
            path_type_dict_list = []
            for pr_id in pr_id_list:
                path_type_dict = git_repo.get_pr_path_dict(repo_id, pr_id)
                path_type_dict_list.append(path_type_dict)

            # # 古いPRから順に処理するようにするため、PR_IDの昇順ソートを行う
            # path_type_dict_list.reverse()

            # 変更パス-変更種類辞書リストより、最新の変更パス-変更種類辞書を作成する。
            # 変更パス-変更種類辞書リストは古い順にソートされているため、
            # 順番に処理していることで重複パスは最新状態に更新され、非重複パスは追加される。
            newest_path_type_dict = {}
            for path_type_dict in path_type_dict_list:
                for path in path_type_dict:
                    newest_path_type_dict[path] = path_type_dict[path]

            # 最新の変更パス-変更種類辞書を昇順ソートする。
            # ソートではリスト型となるため、辞書型へ変換する
            newest_path_type_sorted_list = sorted(newest_path_type_dict.items(), key=lambda x:x[0])
            newest_path_type_dict.clear()
            newest_path_type_dict.update(newest_path_type_sorted_list)

            for path in newest_path_type_dict:
                logger.info(
                    newest_path_type_dict[path].ljust(10)
                    + ': '
                    + path
                    )

    except RequestException as e:
        logger.error(e)
        logger.error("request failed. error=(%s)", e.response.text)
        raise e
    except Exception as e:
        logger.error(e)
        raise e


def check_merged(work_item_id, branch_name):
    """

    リポジトリID-PRID辞書より、変更パス-変更種類辞書を作成し、ログ出力する

    Args:
        work_item_id (str): WorkItemのID
        branch_name (str): ターゲットブランチ名

    """  

    # PRマージ済みフラグ
    is_all_merged=True

    # WorkItemに設定されたPRよりPR辞書を取得
    pr_dict = get_pr_dict(work_item_id, branch_name)

    # PR辞書より、リポジトリID-PRIDリスト辞書を作成する
    repo_id_pr_id_list_dict = {}
    for pr_id in pr_dict.keys():
        pr = pr_dict[pr_id]
        pr_id_list = repo_id_pr_id_list_dict.get(pr.repo_id)
        if pr_id_list == None:
            pr_id_list = []
        pr_id_list.append(pr_id)
        repo_id_pr_id_list_dict[pr.repo_id] = pr_id_list

    # リポジトリID-PRIDリスト辞書より取得したwIのPRリストと
    # GITREPOより取得したマージ済みのPRリストを比較し、
    # マージ状況をチェックする。
    for repo_id in repo_id_pr_id_list_dict:
        # WIのPRリスト
        wi_pr_id_list = repo_id_pr_id_list_dict[repo_id]
        # GITREPOのマージ済みPRリスト
        git_pr_id_list = git_repo.get_pr_id_list(repo_id, branch_name, 'completed')
    
        # マージ済みを取得
        pr_merged_set = set(wi_pr_id_list) & set(git_pr_id_list)
        # 未マージを取得
        pr_not_merged_set = set(wi_pr_id_list) - set(git_pr_id_list)

        if len(pr_not_merged_set)!=0:
            is_all_merged=False

        logger.info('■' + git_repo.get_repo_name(repo_id))
        logger.info('==PRマージ済み==')
        logger.info(list(pr_merged_set))
        logger.info('==PRマージ未了==')
        logger.info(list(pr_not_merged_set))

    return is_all_merged
