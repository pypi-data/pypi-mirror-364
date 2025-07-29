# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/7/18 20:30
# Description:

from logair import get_logger

if __name__ == '__main__':
    logger = get_logger("quda.update")

    logger.info("info")
    logger.warning("warn")
    logger.debug("debug")
    logger.error("error",)
    a = 1
    b = 0
    logger.info(a/b)