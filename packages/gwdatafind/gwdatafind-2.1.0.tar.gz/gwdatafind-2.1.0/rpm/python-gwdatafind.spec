%global srcname gwdatafind
%global version 2.1.0
%global release 1

Name:      python-%{srcname}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   The client library for the GWDataFind service
Group:     Development/Libraries
License:   GPLv3+
Url:       https://gwdatafind.readthedocs.io/
Source0:   %pypi_source
Packager:  Duncan Macleod <duncan.macleod@ligo.org>

BuildArch: noarch
Prefix:    %{_prefix}

# build requirements
BuildRequires: python3-devel >= 3.6
BuildRequires: python3dist(pip)
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(wheel)

# man pages
BuildRequires: python3dist(argparse-manpage)
BuildRequires: python3dist(igwn-auth-utils) >= 0.3.1
BuildRequires: python3dist(igwn-segments)

# testing dependencies
BuildRequires: man-db
BuildRequires: python3dist(pytest) >= 3.1.0
BuildRequires: python3dist(requests-mock)

# -- src.rpm

%description
The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors. This is the source package for the
GWDataFind client API.

# -- gwdatafind

%package -n %{srcname}
Summary: %{summary}
Requires: python3-%{srcname} = %{version}-%{release}
Conflicts: glue < 1.61.0
Conflicts: python2-gwdatafind < 1.0.4-3
%description -n %{srcname}
The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors. This package provides the python interface
libraries.
%files -n %{srcname}
%license LICENSE
%doc README.md
%{_bindir}/gw_data_find
%{_mandir}/man1/gw_data_find.1*

# -- python3x-gwdatafind

%package -n python3-%{srcname}
Summary:  Python %{python3_version} library for the GWDataFind service
Requires: python3dist(igwn-auth-utils) >= 0.3.1
Requires: python3dist(igwn-segments)
%description -n python3-%{srcname}
The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors. This package provides the
Python %{python3_version} interface libraries.
%files -n python3-%{srcname}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- build steps

%prep
%autosetup -n %{srcname}-%{version}
# for RHEL < 9 hack together setup.{cfg,py} for old setuptools
%if 0%{?rhel} && 0%{?rhel} < 10
cat > setup.cfg << SETUP_CFG
[metadata]
name = %{srcname}
version = %{version}
author-email = %{packager}
description = %{summary}
license = %{license}
license_files = LICENSE
url = %{url}
[options]
packages = find:
python_requires = >=%{python3_version}
install_requires =
  igwn-auth-utils >= 0.3.1
  igwn-segments >= 2.0.0
[options.entry_points]
console_scripts =
  gw_data_find = gwdatafind.__main__:main
[build_manpages]
manpages =
  man/gw_data_find.1:prog=gwdatafind:function=command_line:module=gwdatafind.__main__
[tool:pytest]
minversion = 3.1.0
addopts = -r a
filterwarnings =
  error
  ignore:.*pkg_resources
  ignore:Support for identity-based X.509 credentials
SETUP_CFG
%endif
%if %{undefined pyproject_wheel}
cat > setup.py << SETUP_PY
from setuptools import setup
setup()
SETUP_PY
%endif

%build
%if %{defined pyproject_wheel}
%pyproject_wheel
%else
%py3_build_wheel
%endif
# generate manuals
%python3 -c "from setuptools import setup; setup()" \
  --command-packages=build_manpages \
  build_manpages \
;

%install
%if %{defined pyproject_install}
%pyproject_install
%else
%py3_install_wheel *.whl
%endif
%__mkdir -p -v %{buildroot}%{_mandir}/man1
%__install -m 644 -p -v man/*.1* %{buildroot}%{_mandir}/man1/

%check
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
# sanity checks
%{__python3} -m gwdatafind --help
%{buildroot}%{_bindir}/gw_data_find --help
# run test suite
%if 0%{?rhel} == 0 || 0%{?rhel} >= 9
%{pytest} --pyargs gwdatafind
%else
# pytest < 3.9 (EPEL8) can't handle 'tmp_path' fixture
%{pytest} --pyargs gwdatafind -k "not test_main["
%endif
# test man pages
env MANPATH="%{buildroot}%{_mandir}" man -P cat gw_data_find

# -- changelog

%changelog
* Thu Jul 24 2025 Duncan Macleod <duncan.macleod@ligo.org> 2.1.0-1
- update for 2.1.0
- update pytest warning filters

* Thu Apr 17 2025 Duncan Macleod <duncan.macleod@ligo.org> 2.0.0-1
- update for 2.0.0
- update macros for EL8+
- use pyproject macros for build, hack setup.cfg for distributions with old setuptools

* Sat Dec 16 2023 Duncan Macleod <duncan.macleod@ligo.org> 1.2.0-1
- update for 1.2.0
- add python3-devel to BuildRequires
- use argparse-manpage to build manuals, not help2man

* Mon Nov 21 2022 Duncan Macleod <duncan.macleod@ligo.org> 1.1.3-1
- update for 1.1.3

* Thu Sep 29 2022 Duncan Macleod <duncan.macleod@ligo.org> 1.1.2-1
- update for 1.1.2
- update igwn-auth-utils minimum version
- remove extra packages for igwn-auth-utils[requests]

* Mon May 09 2022 Duncan Macleod <duncan.macleod@ligo.org> 1.1.1-1
- update for 1.1.1

* Thu Apr 21 2022 Duncan Macleod <duncan.macleod@ligo.org> 1.1.0-1
- update for 1.1.0
- project now requires python3-igwn-auth-utils/requests

* Fri Jan 28 2022 Duncan Macleod <duncan.macleod@ligo.org> 1.0.5-1
- update for 1.0.5
- rename SRPM to not match any binary RPMs
- drop Python 2 packages
- update summary text to not reference LDR
- separate bindir into separate package

* Fri Jul 12 2019 Duncan Macleod <duncan.macleod@ligo.org> 1.0.4-2
- fixed incorrect installation of /usr/bin/gw_data_find
- use python-srpm-macros to provide python3 versions

* Fri Jan 11 2019 Duncan Macleod <duncan.macleod@ligo.org> 1.0.4-1
- include command-line client, requires matching glue release

* Fri Jan 04 2019 Duncan Macleod <duncan.macleod@ligo.org> 1.0.3-1
- added python3 packages

* Tue Aug 14 2018 Duncan Macleod <duncan.macleod@ligo.org> 1.0.2-1
- bug-fix release

* Tue Aug 14 2018 Duncan Macleod <duncan.macleod@ligo.org> 1.0.1-1
- bug-fix release

* Mon Jul 30 2018 Duncan Macleod <duncan.macleod@ligo.org> 1.0.0-1
- first build
