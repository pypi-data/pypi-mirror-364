# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:# @Time   : 2023-09-09 23:17
# @Author : 毛鹏
import sys

from ..models._ui_model import ElementModel, ElementResultModel

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
__all__ = [
    'ElementModel',
    'ElementResultModel',
]
