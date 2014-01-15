%define release_name Peach
%define dist_version 20
%define bug_version 20

Summary:        Korora release files
Name:           korora-release
Version:        20
Release:        2
License:        GPLv2
Group:          System Environment/Base
URL:            http://kororaproject.org
Source:         %{name}-%{version}.tar.gz
Obsoletes:      redhat-release
Provides:       redhat-release
Provides:       system-release = %{version}-%{release}
Obsoletes:      fedora-release-rawhide < %{version}-%{release}
BuildArch:      noarch
Obsoletes:      fedora-release
Provides:       fedora-release

%description
Korora release files such as yum configs and various /etc/ files that
define the release.

%package rawhide
Summary:    Rawhide repo definitions
Requires:   korora-release = %{version}-%{release}
Obsoletes:  fedora-release-rawhide
Provides:   fedora-release-rawhide

%description rawhide
This package provides the rawhide repo definitions.


%prep
%setup -q
sed -i 's|@@VERSION@@|%{dist_version}|g' Fedora-Legal-README.txt

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc
echo "Korora release %{version} (%{release_name})" > $RPM_BUILD_ROOT/etc/fedora-release
echo "cpe:/o:kororaproject:korora:%{version}" > $RPM_BUILD_ROOT/etc/system-release-cpe
cp -p $RPM_BUILD_ROOT/etc/fedora-release $RPM_BUILD_ROOT/etc/issue
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/etc/issue
cp -p $RPM_BUILD_ROOT/etc/issue $RPM_BUILD_ROOT/etc/issue.net
echo >> $RPM_BUILD_ROOT/etc/issue
ln -s fedora-release $RPM_BUILD_ROOT/etc/redhat-release
ln -s fedora-release $RPM_BUILD_ROOT/etc/system-release

cat << EOF >>$RPM_BUILD_ROOT/etc/os-release
NAME=Korora
VERSION="%{dist_version} (%{release_name})"
ID=korora
VERSION_ID=%{dist_version}
PRETTY_NAME="Korora %{dist_version} (%{release_name})"
ANSI_COLOR="0;34"
CPE_NAME="cpe:/o:kororaproject:korora:%{dist_version}"
HOME_URL="https://kororaproject.org/"
EOF

# Install the keys
install -d -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg
install -m 644 RPM-GPG-KEY* $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

# Link the primary/secondary keys to arch files, according to archmap.
# Ex: if there's a key named RPM-GPG-KEY-fedora-19-primary, and archmap
#     says "fedora-19-primary: i386 x86_64",
#     RPM-GPG-KEY-fedora-19-{i386,x86_64} will be symlinked to that key.
pushd $RPM_BUILD_ROOT/etc/pki/rpm-gpg/
for keyfile in RPM-GPG-KEY*; do
    key=${keyfile#RPM-GPG-KEY-} # e.g. 'fedora-20-primary'
    arches=$(sed -ne "s/^${key}://p" $RPM_BUILD_DIR/%{name}-%{version}/archmap) \
        || echo "WARNING: no archmap entry for $key"
    for arch in $arches; do
        # replace last part with $arch (fedora-20-primary -> fedora-20-$arch)
        ln -s $keyfile ${keyfile%%-*}-$arch # NOTE: RPM replaces %% with %
    done
done
# and add symlink for compat generic location
ln -s RPM-GPG-KEY-fedora-%{dist_version}-primary RPM-GPG-KEY-%{dist_version}-fedora
popd

install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d
for file in fedora*repo korora*repo ; do
  install -m 644 $file $RPM_BUILD_ROOT/etc/yum.repos.d
done

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT/etc/rpm
cat >> $RPM_BUILD_ROOT/etc/rpm/macros.dist << EOF
# dist macros.

%%fedora                %{dist_version}
%%dist                .fc%{dist_version}
%%fc%{dist_version}                1
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc GPL Fedora-Legal-README.txt README.pdf
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
* Tue Nov 04 2013 Chris Smart <csmart@kororaproject.org> - 20-0.8
- Bump upstream
- patch from Will Woods to use a archmap file for linking gpg keys
- add f21 keys
- add fields to /etc/os-release for rhbz#951119
- set skip_if_unavailable=False for rhbz#985354

* Tue Nov 04 2013 Chris Smart <csmart@kororaproject.org> - 20-0.7
- Update fedora repos to fix gpg key and mirror url, as per upstream

* Sun Oct 27 2013 Chris Smart <csmart@kororaproject.org> - 20-0.1
- Update to upstream release for Korora 20.

* Thu Aug 22 2013 Chris Smart <csmart@kororaproject.org> - 19-1
- Update to upstream release.

* Thu May 30 2013 Ian Firns <firnsy@kororaproject.org> - 19-0.3
- Fix gpgkey testing mirror lists paths in korora.repo.

* Sat May 25 2013 Ian Firns <firnsy@kororaproject.org> - 19-0.2
- Added Korora 19 signing keys.

* Sun Apr 28 2013 Ian Firns <firnsy@kororaproject.org> - 19-0.1
- Update to Korora 19 release

* Fri Jan 25 2013 Chris Smart <csmart@kororaproject.org> - 18-0.2
- Update to use new dl.kororaproject.org domain.

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
