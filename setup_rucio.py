# Copyright 2012-2018 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Mario Lassnig <mario.lassnig@cern.ch>, 2012-2014
# - Vincent Garonne <vgaronne@gmail.com>, 2012-2018
# - Martin Barisits <martin.barisits@cern.ch>, 2012-2017
# - Wen Guan <wguan.icedew@gmail.com>, 2014
# - Thomas Beermann <thomas.beermann@cern.ch>, 2014

'''
Setup.py which moves kerberos modules in extra dependencies to be buildthedocs compliant.
'''

import glob
import os
import re
import subprocess
import sys

from distutils.command.sdist import sdist as _sdist

if sys.version_info < (2, 4):
    print('ERROR: Rucio requires at least Python 2.5 to run.')
    sys.exit(1)

sys.path.insert(0, os.path.abspath('lib/'))

from rucio import version  # noqa

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

name = 'rucio'
packages = find_packages('lib/')
description = "Rucio Package"
IsRelease = False
requirements_files = ['tools/pip-requires', 'tools/pip-requires-client']
data_files = [('rucio/etc/', glob.glob('etc/*.template')),
              ('rucio/etc/web', glob.glob('etc/web/*.template')),
              ('rucio/etc/schemas', glob.glob('etc/schemas/*.json')),
              ('rucio/tools/', ['tools/pip-requires', 'tools/pip-requires-client', 'tools/pip-requires-test',
                                'tools/bootstrap.py', 'tools/reset_database.py']),
              ('rucio/tools/probes/common/', ['tools/probes/common/graphite2nagios', ]),
              ('rucio/tools/probes/common/', glob.glob('tools/probes/common/check*')),
              ('rucio/etc/mail_templates/', glob.glob('etc/mail_templates/*.tmpl'))]

scripts = glob.glob('bin/rucio*')

copy_args = sys.argv[1:]
if '--release' in copy_args:
    IsRelease = True
    copy_args.remove('--release')

# Flags to know if the installation is done through pip and against git
using_pip = os.path.basename(os.path.dirname(__file__)).startswith('pip-')
using_git = os.path.isdir('.git')


def run_git_command(cmd):
    """
    Run a git command in path and return output"

    :param cmd: the git command.
    :return: Output of the git command.
    """
    output = subprocess.Popen(["/bin/sh", "-c", cmd], stdout=subprocess.PIPE)
    return output.communicate()[0].strip()


if using_pip and using_git:
    git_version_cmd = '''git describe --dirty=-dev`date +%s`'''
    pkg_version = run_git_command(git_version_cmd)
    branch_nick_cmd = 'git branch | grep -Ei "\* (.*)" | cut -f2 -d" "'
    branch_nick = run_git_command(branch_nick_cmd)
    revid_cmd = "git rev-parse HEAD"
    revid = run_git_command(revid_cmd)
    revno_cmd = "git --no-pager log --oneline | wc -l"
    revno = run_git_command(revno_cmd)
    version_file = open("lib/rucio/vcsversion.py", 'w')
    version_file.write("""'''\n"""
                       """This file is automatically generated by setup.py, So don't edit it. :)\n"""
                       """'''\n"""
                       """VERSION_INFO = {\n"""
                       """    'final': False,\n"""
                       """    'version': '%s',\n"""
                       """    'branch_nick': '%s',\n"""
                       """    'revision_id': '%s',\n"""
                       """    'revno': %s\n"""
                       """}""" % (pkg_version, branch_nick, revid, revno))
    version_file.close()
else:
    pkg_version = version.version_string()

cmdclass = {}

try:
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        def run(self):
            for builder in ['html']:   # 'man','latex'
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)
    cmdclass['build_sphinx'] = local_BuildDoc
except:
    pass


def get_reqs_from_file(requirements_file):
    if os.path.exists(requirements_file):
        return open(requirements_file, 'r').read().split('\n')
    return []


def parse_requirements(requirements_files):
    requirements = []
    for requirements_file in requirements_files:
        for line in get_reqs_from_file(requirements_file):
            if 'kerberos' in line:
                pass
            elif re.match(r'\s*-e\s+', line):
                requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
            elif re.match(r'\s*-f\s+', line):
                pass
            else:
                requirements.append(line)
    return requirements


def parse_dependency_links(requirements_files):
    dependency_links = []
    for requirements_file in requirements_files:
        for line in get_reqs_from_file(requirements_file):
            if re.match(r'(\s*#)|(\s*$)', line):
                continue
            if re.match(r'\s*-[ef]\s+', line):
                dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    return dependency_links


def write_requirements():
    venv = os.environ.get('VIRTUAL_ENV', None)
    if venv is not None:
        req_file = open("requirements.txt", "w")
        output = subprocess.Popen(["pip", "freeze", "-l"], stdout=subprocess.PIPE)
        requirements = output.communicate()[0].strip()
        req_file.write(requirements)
        req_file.close()


oracle_extras = ['cx_oracle>=5.1']
postgresql_extras = ['psycopg2>=2.4.2']
mysql_extras = ['PyMySQL']
kerberos_extras = ['kerberos>=1.3.0', 'pykerberos>=1.2.1', 'requests-kerberos>=0.12.0']
dev_extras = parse_requirements(requirements_files=['tools/pip-requires-test', ])
requires = parse_requirements(requirements_files=requirements_files)
extras_require = dict(oracle=oracle_extras,
                      postgresql=postgresql_extras,
                      mysql=mysql_extras,
                      kerberos=kerberos_extras,
                      dev=dev_extras)
depend_links = parse_dependency_links(requirements_files=requirements_files)


class CustomSdist(_sdist):

    user_options = [
        ('packaging=', None, "Some option to indicate what should be packaged")
    ] + _sdist.user_options

    def __init__(self, *args, **kwargs):
        _sdist.__init__(self, *args, **kwargs)
        self.packaging = "default value for this option"

    def get_file_list(self):
        print("Chosen packaging option: " + name)
        self.distribution.data_files = data_files
        _sdist.get_file_list(self)


cmdclass['sdist'] = CustomSdist

setup(
    name=name,
    version=pkg_version,
    packages=packages,
    package_dir={'': 'lib'},
    data_files=data_files,
    script_args=copy_args,
    cmdclass=cmdclass,
    include_package_data=True,
    scripts=scripts,
    # doc=cmdclass,
    author="Rucio",
    author_email="rucio-dev@cern.ch",
    description=description,
    license="Apache License, Version 2.0",
    url="http://rucio.cern.ch/",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)', ],
    install_requires=requires,
    extras_require=extras_require,
    dependency_links=depend_links,
    entry_points = {
    'console_scripts':
        ['rucio-reaper=rucio.clis.daemons.reaper.reaper:main',
         'rucio-dark-reaper=rucio.clis.daemons.reaper.dark:main',
         'rucio-light-reaper=rucio.clis.daemons.reaper.light:main'],
    },
)
