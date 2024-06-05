# -*- encoding: utf-8 -*-
# @ModuleName: log_pro
# @Author: ximo
# @Time: 2024/6/4 16:20

# -*- encoding: utf-8 -*-
# @ModuleName: log_req
# @Author: ximo
# @Time: 2023/12/15 11:29

import logging


def log_with_name(name):
    logger = logging.getLogger('{}_logger'.format(name))

    logger.setLevel(logging.DEBUG)

    test_log = logging.FileHandler('{}.log'.format(name), 'a', encoding='utf-8')

    test_log.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s -%(process)s')

    test_log.setFormatter(formatter)

    logger.addHandler(test_log)
    return logger


if __name__ == "__main__":
    logger = log_with_name("test")
    logger.debug('----调试信息 [debug]------')
    logger.info('[info]')
    logger.warning('警告信息[warning]')
    logger.error('错误信息[error]')
    logger.critical('严重错误信息[crtical]')
