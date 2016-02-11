%define release_name Coral
%define dist_version 23
%define bug_version 23

Summary:        Korora release files
Name:           korora-release
Version:        23
Release:        2
License:        MIT
Group:          System Environment/Base
URL:            http://kororaproject.org
Source:         %{name}-%{version}.tar.gz
Obsoletes:      redhat-release
Provides:       redhat-release
Provides:       system-release
Provides:       system-release(%{version})

# Kill off the fedora-release-nonproduct package
Provides:       fedora-release-nonproduct = %{version}
Obsoletes:      fedora-release-nonproduct <= 23-0.3
Provides:       fedora-release-standard = 22-0.8
Obsoletes:      fedora-release-standard < 22-0.8

Requires:       korora-repos(%{version})
Obsoletes:      fedora-release
Provides:       fedora-release = %{version}-%{release}
BuildArch:      noarch

%description
Korora release files such as various /etc/ files that define the release.

%package cloud
Summary:        Base package for Korora Cloud-specific default configurations
Provides:       system-release-cloud
Provides:       system-release-cloud(%{version})
Provides:       system-release-product
Requires:       korora-release = %{version}-%{release}
# Replace fedora's packages
Provides:       fedora-release-cloud
Obsoletes:      fedora-release-cloud

%description cloud
Provides a base package for Korora Cloud-specific configuration files to
depend on.

%package server
Summary:        Base package for Korora Server-specific default configurations
Provides:       system-release-server
Provides:       system-release-server(%{version})
Provides:       system-release-product
Requires:       korora-release = %{version}-%{release}
Requires:       systemd
Requires:       cockpit
Requires:       rolekit
Requires(post):	sed
Requires(post):	systemd
# Replace fedora's packages
Provides:       fedora-release-server
Obsoletes:      fedora-release-server

%description server
Provides a base package for Korora Server-specific configuration files to
depend on.

%package workstation
Summary:        Base package for Korora Workstation-specific default configurations
Provides:       system-release-workstation
Provides:       system-release-workstation(%{version})
Provides:       system-release-product
Requires:       korora-release = %{version}-%{release}
# needed for captive portal support
Requires:       NetworkManager-config-connectivity-fedora
Requires(post): /usr/bin/glib-compile-schemas
Requires(postun): /usr/bin/glib-compile-schemas
# Replace fedora's packages
Provides:       fedora-release-workstation
Obsoletes:      fedora-release-workstation


%description workstation
Provides a base package for Korora Workstation-specific configuration files to
depend on.

%prep
%setup -q
sed -i 's|@@VERSION@@|%{dist_version}|g' Fedora-Legal-README.txt

%build

%install
install -d $RPM_BUILD_ROOT/etc
echo "Korora release %{version} (%{release_name})" > $RPM_BUILD_ROOT/etc/fedora-release
echo "cpe:/o:kororaproject:korora:%{version}" > $RPM_BUILD_ROOT/etc/system-release-cpe

# Symlink the -release files
ln -s fedora-release $RPM_BUILD_ROOT/etc/redhat-release
ln -s fedora-release $RPM_BUILD_ROOT/etc/system-release

# Create the common os-release file
install -d $RPM_BUILD_ROOT/usr/lib/os.release.d/
cat << EOF >>$RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora
NAME=Korora
VERSION="%{dist_version} (%{release_name})"
ID=fedora
VERSION_ID=%{dist_version}
PRETTY_NAME="Korora %{dist_version} (%{release_name})"
ANSI_COLOR="0;34"
CPE_NAME="cpe:/o:kororaproject:korora:%{dist_version}"
HOME_URL="https://kororaproject.org/"
EOF

# Create the common /etc/issue
echo "\S" > $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-fedora
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-fedora
echo >> $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-fedora

# Create /etc/issue.net
echo "\S" > $RPM_BUILD_ROOT/usr/lib/issue.net
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/usr/lib/issue.net
ln -s ../usr/lib/issue.net $RPM_BUILD_ROOT/etc/issue.net

# Create os-release and issue files for the different editions
# Cloud
cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud
echo "VARIANT=\"Cloud Edition\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud
echo "VARIANT_ID=cloud" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud
sed -i -e "s|(%{release_name})|(Cloud Edition)|g" $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud

# Server
cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server
echo "VARIANT=\"Server Edition\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server
echo "VARIANT_ID=server" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server
sed -i -e "s|(%{release_name})|(Server Edition)|g" $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server

cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-server
echo "Admin Console: https://\4:9090/ or https://[\6]:9090/" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-server
echo >> $RPM_BUILD_ROOT/usr/lib/os.release.d/issue-server

# Workstation
cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-workstation
echo "VARIANT=\"Workstation Edition\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-workstation
echo "VARIANT_ID=workstation" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-workstation

# Create the symlink for /etc/os-release
# This will be standard until %post when the
# release packages will link the appropriate one into
# /usr/lib/os-release
ln -s ../usr/lib/os-release $RPM_BUILD_ROOT/etc/os-release
ln -s os.release.d/os-release-fedora $RPM_BUILD_ROOT/usr/lib/os-release

# Create the symlink for /etc/issue
# This will be standard until %post when the
# release packages will link the appropriate one into
# /usr/lib/os-release
ln -s ../usr/lib/issue $RPM_BUILD_ROOT/etc/issue
ln -s os.release.d/issue-fedora $RPM_BUILD_ROOT/usr/lib/issue

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
cat >> $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.dist << EOF
# dist macros.

%%fedora                %{dist_version}
%%dist                .fc%{dist_version}
%%fc%{dist_version}                1
EOF

# Add presets
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/user-preset/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
# Default system wide
install -m 0644 85-display-manager.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -m 0644 90-default.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -m 0644 99-default-disable.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
# Fedora Server
install -m 0644 80-server.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
# Fedora Workstation
install -m 0644 80-workstation.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/

# Override the list of enabled gnome-shell extensions for Workstation
mkdir -p $RPM_BUILD_ROOT%{_datadir}/glib-2.0/schemas/
install -m 0644 org.gnome.shell.gschema.override $RPM_BUILD_ROOT%{_datadir}/glib-2.0/schemas/

%posttrans
# Only on installation
if [ $1 = 0 ]; then
    # If no fedora-release-$edition subpackage was installed,
    # make sure to link /etc/os-release to the standard version
    test -e /usr/lib/os-release || \
        ln -sf ./os-release.d/os-release-fedora /usr/lib/os-release
fi

%post cloud
# Run every time
    # If there is no link to os-release yet from some other
    # release package, create it
    test -e /usr/lib/os-release || \
        ln -sf ./os.release.d/os-release-cloud /usr/lib/os-release

    # If os-release isn't a link or it exists but it points to a
    # non-productized version, replace it with this one
    if [ \! -h /usr/lib/os-release -o "x$(readlink /usr/lib/os-release)" = "xos.release.d/os-release-fedora" ]; then
        ln -sf ./os.release.d/os-release-cloud /usr/lib/os-release || :
    fi

%postun cloud
# Uninstall
if [ $1 = 0 ]; then
    # If os-release is now a broken symlink or missing replace it
    # with a symlink to basic version
    test -e /usr/lib/os-release || \
        ln -sf ./os.release.d/os-release-fedora /usr/lib/os-release || :
fi


%post server
# Run every time
    # If there is no link to os-release yet from some other
    # release package, create it
    test -e /usr/lib/os-release || \
        ln -sf ./os.release.d/os-release-server /usr/lib/os-release

    # If os-release isn't a link or it exists but it points to a
    # non-productized version, replace it with this one
    if [ \! -h /usr/lib/os-release -o "x$(readlink /usr/lib/os-release)" = "xos.release.d/os-release-fedora" ]; then
        ln -sf ./os.release.d/os-release-server /usr/lib/os-release || :
    fi

    # If issue isn't a link or it exists but it points to a
    # non-productized version, replace it with this one
    if [ \! -h /usr/lib/issue -o "x$(readlink /usr/lib/issue)" = "xos.release.d/issue-fedora" ]; then
        ln -sf ./os.release.d/issue-server /usr/lib/issue || :
    fi

if [ $1 -eq 1 ] ; then
    # Initial installation

    # fix up after %%systemd_post in packages
    # possibly installed before our preset file was added
    units=$(sed -n 's/^enable//p' \
        < %{_prefix}/lib/systemd/system-preset/80-server.preset)
        /usr/bin/systemctl preset $units >/dev/null 2>&1 || :
fi

%postun server
# Uninstall
if [ $1 = 0 ]; then
    # If os-release is now a broken symlink or missing replace it
    # with a symlink to basic version
    test -e /usr/lib/os-release || \
        ln -sf ./os.release.d/os-release-fedora /usr/lib/os-release || :

    test -e /usr/lib/issue || \
        ln -sf ./os.release.d/issue-fedora /usr/lib/issue || :
fi

%post workstation
# Run every time
    # If there is no link to os-release yet from some other
    # release package, create it
    test -e /usr/lib/os-release || \
        ln -sf ./os.release.d/os-release-workstation /usr/lib/os-release

    # If os-release isn't a link or it exists but it points to a
    # non-productized version, replace it with this one
    if [ \! -h /usr/lib/os-release -o "x$(readlink /usr/lib/os-release)" = "xos.release.d/os-release-fedora" ]; then
        ln -sf ./os.release.d/os-release-workstation /usr/lib/os-release || :
    fi

if [ $1 -eq 1 ] ; then
    # Initial installation

    # fix up after %%systemd_post in packages
    # possibly installed before our preset file was added
    units=$(sed -n 's/^disable//p' \
        < %{_prefix}/lib/systemd/system-preset/80-workstation.preset)
    /usr/bin/systemctl preset $units >/dev/null 2>&1 || :
fi

%postun workstation
if [ $1 -eq 0 ] ; then
    glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :

    # If os-release is now a broken symlink or missing replace it
    # with a symlink to basic version
    test -e /usr/lib/os-release || \
        ln -sf ./os.release.d/os-release-fedora /usr/lib/os-release || :
fi

%posttrans workstation
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %doc}
%license LICENSE Fedora-Legal-README.txt
%dir /usr/lib/os.release.d
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-fedora
/usr/lib/os-release
/etc/os-release
%config %attr(0644,root,root) /etc/fedora-release
/etc/redhat-release
/etc/system-release
%config %attr(0644,root,root) /etc/system-release-cpe
%config %attr(0644,root,root) /usr/lib/os.release.d/issue-fedora
/usr/lib/issue
%config(noreplace) /etc/issue
%config %attr(0644,root,root) /usr/lib/issue.net
%config(noreplace) /etc/issue.net
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist
%dir /usr/lib/systemd/user-preset/
%dir %{_prefix}/lib/systemd/system-preset/
%{_prefix}/lib/systemd/system-preset/85-display-manager.preset
%{_prefix}/lib/systemd/system-preset/90-default.preset
%{_prefix}/lib/systemd/system-preset/99-default-disable.preset

%files cloud
%{!?_licensedir:%global license %doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-cloud


%files server
%{!?_licensedir:%global license %doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-server
%config %attr(0644,root,root) /usr/lib/os.release.d/issue-server
%{_prefix}/lib/systemd/system-preset/80-server.preset

%files workstation
%{!?_licensedir:%global license %doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-workstation
%{_datadir}/glib-2.0/schemas/org.gnome.shell.gschema.override
%{_prefix}/lib/systemd/system-preset/80-workstation.preset

%changelog
* Mon Nov 2 2015 Chris Smart <csmart@kororaproject.org> - 23-1
- setup for Korora 23 GA

* Tue Sep 15 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.19
- Do not clobber /etc/issue[.net] customizations

* Wed Sep 09 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.18
- Update preset file with FESCo decisions
- https://fedorahosted.org/fesco/ticket/1472

* Tue Sep 08 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.17
- Enclose IPv6 addresses in square brackets in /etc/issue
- rebuild to drop timesysncd enabled from server

* Mon Aug 24 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.16
- Make /etc/issue configurable per-edition
- Resolves: RHBZ#1239089

* Tue Jul 14 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.15
- setup for f23 branching

* Fri Jul 10 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.14
- Enable mlocate-updatedb.timer rhbz#1231745

* Wed May 20 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.13
- enable unbound-anchor.timer rhbz#1223199
- enable lvm2-lvmpolld.*  rhbz#1222495
- change PRIVACY_POLICY to PRIVACY_POLICY_URL in os-release

* Thu May 14 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.12
- install the default system wide presets rhbz#1221339

* Fri May 08 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.11
- make sure that the VARIANT is wrapped in ""

* Fri May 08 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.10
- use infor about the Edition instead of the release name in
- os-release for productised installs

* Tue May 05 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.9
- Follow systemd upstream guidelines for VARIANT and VARIANT_ID

* Thu Mar 19 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.8
- Handle os-release upgrades from existing productized installations

* Tue Mar 17 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.7
- make the os-release sysmlinks all relative

* Fri Mar 13 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.6
- Fix incorrect comparisons in fedora-release-* subpackages

* Fri Mar 13 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.4
- unbreak installs getting a broken symlink at /etc/os-release

* Fri Mar 13 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.4
- add preset file for workstation to disable sshd

* Thu Mar 12 2015 Stephen Gallagher <sgallagh@redhat.com> 23-0.3.1
- Generate os-release based on product subpackages
- Remove the -nonproduct subpackage
- Eliminate Conflicts between subpackages

* Tue Feb 24 2015 Dennis Gilmore <dennis@ausil.us> - 23-0.3
- make the /etc/os-release symlink relative rhbz#1192276 

* Tue Feb 10 2015 Dennis Gilmore <dennis@ausil.us> 23-0.2
- bump

* Tue Feb 10 2015 Peter Robinson <pbrobinson@fedoraproject.org> 23-0.1
- Setup for rawhide targetting f23
- Add PRIVACY_POLICY_URL to os-release (rhbz#1182635)
- Move os-release to /usr/lib and symlink to etc (rhbz#1149568)
