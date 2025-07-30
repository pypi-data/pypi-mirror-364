# -*- coding: utf-8 -*-
# 通联数据机密
# --------------------------------------------------------------------
# 通联数据股份公司版权所有 © 2013-2025
#
# 注意：本文所载所有信息均属于通联数据股份公司资产。本文所包含的知识和技术概念均属于
# 通联数据产权，并可能由中国、美国和其他国家专利或申请中的专利所覆盖，并受商业秘密或
# 版权法保护。
# 除非事先获得通联数据股份公司书面许可，严禁传播文中信息或复制本材料。
#
# DataYes CONFIDENTIAL
# --------------------------------------------------------------------
# Copyright © 2013-2025 DataYes, All Rights Reserved.
#
# NOTICE: All information contained herein is the property of DataYes
# Incorporated. The intellectual and technical concepts contained herein are
# proprietary to DataYes Incorporated, and may be covered by China, U.S. and
# Other Countries Patents, patents in process, and are protected by trade
# secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from DataYes.
import sys
import os
import requests
from pip._vendor.packaging import version as packaging_version
from pip._vendor import pkg_resources
try:
    from pip._vendor.six.moves.urllib import parse as urllib_parse
except ImportError:
    import urllib.parse as urllib_parse

WINDOWS = (sys.platform.startswith("win") or (sys.platform == 'cli' and os.name == 'nt'))


class Index(object):
    def __init__(self, url):
        self.url = url
        self.netloc = urllib_parse.urlsplit(url).netloc
        self.simple_url = self.url_to_path('simple')
        self.pypi_url = self.url_to_path('pypi')
        self.pip_json_url = self.url_to_path('pypi/pip/json')

    def url_to_path(self, path):
        return urllib_parse.urljoin(self.url, path)


PyPI = Index('https://pypi.org/')


def get_installed_version(dist_name, lookup_dirs=None):
    """Get the installed version of dist_name avoiding pkg_resources cache"""
    # Create a requirement that we'll look for inside of setuptools.
    req = pkg_resources.Requirement.parse(dist_name)

    # We want to avoid having this cached, so we need to construct a new
    # working set each time.
    if lookup_dirs is None:
        working_set = pkg_resources.WorkingSet()
    else:
        working_set = pkg_resources.WorkingSet(lookup_dirs)

    # Get the installed distribution from our working set
    dist = working_set.find(req)

    # Check to see if we got an installed distribution or not, if we did
    # we want to return it's version.
    return dist.version if dist else ""


def check_uqer_version():
    installed_version = get_installed_version('uqer')
    pip_version = packaging_version.parse(installed_version)
    try:
        resp = requests.get(
            PyPI.url_to_path('pypi/uqer/json'),
            headers={"Accept": "application/json"},
            timeout=5
        )
        resp.raise_for_status()
        pypi_version = [
            v for v in sorted(
                list(resp.json()["releases"]),
                key=packaging_version.parse,
            )
            if not packaging_version.parse(v).is_prerelease
        ][-1]
    except Exception:
        pass
    else:
        remote_version = packaging_version.parse(pypi_version)
        pip_main_version = int(pip_version.base_version.split('.')[0])
        remote_main_version = int(remote_version.base_version.split('.')[0])
        if pip_main_version < remote_main_version:
            pip_cmd = "python -m pip" if WINDOWS else "pip"
            raise Exception(
                "你使用的uqer版本是%s, 然而%s已经可以使用。\n"
                "你必须使用'%s install --upgrade uqer'命令进行升级。" % (pip_version, remote_version, pip_cmd)
                )