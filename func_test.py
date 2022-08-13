from logging import getLogger
import func

logger = getLogger(__name__)

logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
pr_dict = func.get_pr_dict(3, 'master')
for pr_id in pr_dict.keys():
    logger.info(pr_dict[pr_id].pr_id)

logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
func.print_changed_filepath_dict_by_pr(3, 'master')

logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
func.print_changed_filepath_dict_by_repo_pr(3, 'master')

logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
func.print_changed_filepath_dict_by_repo_diff_branch(3, 'feature', 'master')

logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
logger.info('CheckResult: ' + str(func.check_merged(3, 'master')))

