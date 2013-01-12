%define release_name Flo
%define dist_version 18
%define dist_release ""

Summary:    Korora release files
Name:       korora-release
Version:    18
Release:    0.1
License:    GPLv2
Group:      System Environment/Base
URL:        http://kororaproject.org
Source:     %{name}-%{version}.tar.gz
Obsoletes:  redhat-release
Obsoletes:  redhat-release-rawhide < %{version}-%{release}
Provides:   redhat-release
Provides:   system-release = %{version}-%{release}
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:  noarch
Obsoletes:  fedora-release kororaa-release
Provides:   fedora-release kororaa-release

%description
Korora release files such as yum configs and various /etc/ files that
define the release.

%package rawhide
Summary:  Rawhide repo definitions
Requires: korora-release = %{version}-%{release}
Obsoletes:  fedora-release-rawhide
Provides: fedora-release-rawhide

%description rawhide
This package provides the rawhide repo definitions.


%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc
echo "Korora release %{version}%{dist_release} (%{release_name})" > $RPM_BUILD_ROOT/etc/fedora-release
echo "cpe://o:korora:korora:%{version}" > $RPM_BUILD_ROOT/etc/system-release-cpe
cp -p $RPM_BUILD_ROOT/etc/fedora-release $RPM_BUILD_ROOT/etc/issue
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/etc/issue
cp -p $RPM_BUILD_ROOT/etc/issue $RPM_BUILD_ROOT/etc/issue.net
echo >> $RPM_BUILD_ROOT/etc/issue
ln -s fedora-release $RPM_BUILD_ROOT/etc/redhat-release
ln -s fedora-release $RPM_BUILD_ROOT/etc/system-release

cat << EOF >>$RPM_BUILD_ROOT/etc/os-release
NAME=Korora
VERSION="%{version} (%{release_name})"
ID=korora
VERSION_ID=%{version}
PRETTY_NAME="Korora %{version} (%{release_name})"
ANSI_COLOR=0;34
EOF

install -d -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg

install -m 644 RPM-GPG-KEY* $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

# Install all the keys, link the primary keys to primary arch files
# and to compat generic location
pushd $RPM_BUILD_ROOT/etc/pki/rpm-gpg/
for arch in i386 x86_64
  do
  ln -s RPM-GPG-KEY-fedora-%{dist_version}-primary RPM-GPG-KEY-fedora-$arch
done
ln -s RPM-GPG-KEY-fedora-%{dist_version}-primary RPM-GPG-KEY-fedora
for arch in arm armhfp arm64 ppc ppc64 s390 s390x sparc sparc64
  do
  ln -s RPM-GPG-KEY-fedora-%{dist_version}-secondary RPM-GPG-KEY-fedora-$arch
done
popd

install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d
for file in fedora*repo korora*repo ; do
  install -m 644 $file $RPM_BUILD_ROOT/etc/yum.repos.d
done

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT/etc/rpm
cat >> $RPM_BUILD_ROOT/etc/rpm/macros.dist << EOF
# dist macros.

%%fedora    %{dist_version}
%%dist    .fc%{dist_version}
%%fc%{dist_version}   1
EOF

%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc GPL README.pdf
%config %attr(0644,root,root) /etc/os-release
%config %attr(0644,root,root) /etc/fedora-release
/etc/redhat-release
/etc/system-release
%config %attr(0644,root,root) /etc/system-release-cpe
%dir /etc/yum.repos.d
%config(noreplace) /etc/yum.repos.d/fedora.repo
%config(noreplace) /etc/yum.repos.d/fedora-updates*.repo
%config(noreplace) /etc/yum.repos.d/korora*.repo
%config(noreplace) %attr(0644,root,root) /etc/issue
%config(noreplace) %attr(0644,root,root) /etc/issue.net
%config %attr(0644,root,root) /etc/rpm/macros.dist
%dir /etc/pki/rpm-gpg
/etc/pki/rpm-gpg/*

%files rawhide
%defattr(-,root,root,-)
%config(noreplace) /etc/yum.repos.d/fedora-rawhide.repo

%changelog
* Thu Oct 25 2012 Chris Smart <chris@kororaproject.org> - 18-0.1
- Update to Korora 18 release

* Sun May 13 2012 Chris Smart <chris@kororaa.org> - 17-0.1
- Update to Kororaa 17 release

* Sat Feb 11 2012 Chris Smart <chris@kororaa.org> - 16.1-1
- Update to Kororaa 16.1 release

* Thu Nov 10 2011 Chris Smart <chris@kororaa.org> - 16.0-1
- Update to Kororaa 16

* Sun Nov 1 2011 Chris Smart <chris@kororaa.org> - 15.2-4
- Update to Kororaa 15.2

* Sun Jul 10 2011 Chris Smart <chris@kororaa.org> - 15-2
- Update to Fedora 15

* Fri Mar 11 2011 Chris Smart <chris@kororaa.org> - 14.0.4
- add priorities to kororaa.repo

* Fri Mar 11 2011 Chris Smart <chris@kororaa.org> - 14.0.1
- update mirror list in Kororaa repo.

* Sat Feb 26 2011 Chris Smart <chris@kororaa.org> - 14.0
- initial pull in from Fedora.
