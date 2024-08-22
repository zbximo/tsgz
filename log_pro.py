# -*- encoding: utf-8 -*-
# @ModuleName: log_pro
# @Author: ximo
# @Time: 2024/6/4 16:20

# -*- encoding: utf-8 -*-
# @ModuleName: log_req
# @Author: ximo
# @Time: 2023/12/15 11:29

import logging
logging.basicConfig(level=logging.INFO)
def log_with_name(name):
    logger1 = logging.getLogger('{}_logger'.format(name))
    # logger1.propagate = False
    logger1.setLevel(logging.INFO)
    if not logger1.handlers:
        test_log = logging.FileHandler('{}.log'.format(name), 'a', encoding='utf-8')

        test_log.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s -%(process)s')

        test_log.setFormatter(formatter)

        logger1.addHandler(test_log)
    return logger1


if __name__ == "__main__":
    logger = log_with_name("test")
    logger.debug('----调试信息 [debug]------')
    logger.info('[info]')
    logger.warning('警告信息[warning]')
    logger.error('错误信息[error]')
    logger.critical('严重错误信息[crtical]')
