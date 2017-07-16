#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Filters used by the OpenSSH roles
#
# Fabrizio Colonna <colofabrix@tin.it> - 31/05/2017
#

import re
import pwd
import getpass


def authfile_replace(value, getent_info):
    """
    Replace function for option AuthorizedKeysFiles
    """
    user = getent_info.keys()[0]
    user_home = getent_info[user][4]

    # Literal %
    value = value.replace("%%", "%")
    # Home directory of the user being authenticated
    value = value.replace("%h", user_home)
    # Username of that user
    value = value.replace("%u", user)
    # Home directory symbol
    value = value.replace("~", user_home)

    return value


def is_local_path(value):
    """
    Check if a path is absolute or depends on user or any other
    SSH variable
    """
    if re.findall(r'%[uh]', value):
        return True
    if re.findall(r'^/', value):
        return False
    return True


class FilterModule(object):
    """ Ansible core jinja2 filters """
    def filters(self):
        return {
            'authfile_replace': authfile_replace,
            'is_local_path': is_local_path
        }

# vim: ft=python:ts=4:sw=4