from logging import getLogger, config
import func

logger = getLogger(__name__)

def print_pr_dict():
    try: 
        pr_dict = func.get_pr_dict(3, 'master')
        for pr_id in pr_dict.keys():
            logger.info(pr_dict[pr_id].pr_id)
    except Exception as e:
        logger.error('異常終了します')
        exit(1)


logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print_pr_dict()
logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
func.print_changed_filepath_dict_by_pr(3, 'master')
logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
func.print_changed_filepath_dict_by_repo(3, 'master')
logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
logger.info('CheckResult: ' + str(func.check_merged(3, 'master')))

