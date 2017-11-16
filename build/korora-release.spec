%define release_name Marlin
%define dist_version 27
%define bug_version 27

Summary:        Korora release files
Name:           korora-release
Version:        27
Release:        0.2
License:        MIT
Group:          System Environment/Base
URL:            http://kororaproject.org
Source:         %{name}-%{version}.tar.gz
Source1:        convert-to-edition.lua
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


%package atomichost
Summary:        Base package for Fedora Atomic-specific default configurations
Provides:       system-release-atomichost
Provides:       system-release-atomichost(%{version})
Provides:       system-release-product
Requires:       fedora-release = %{version}-%{release}
# Replace fedora's packages
Provides:       fedora-release-atomichost
Obsoletes:      fedora-release-atomichost

%description atomichost
Provides a base package for Korora Atomic Host-specific configuration files to
depend on.

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
Requires:       fedora-release = %{version}-%{release}
Requires:       systemd
Requires:       cockpit-bridge
Requires:       cockpit-networkmanager
Requires:       cockpit-shell
Requires:       cockpit-storaged
Requires:       cockpit-ws
Requires:       openssh-server
Requires:       rolekit
Requires(post): sed
Requires(post): systemd
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
ID=korora
ID_LIKE=fedora
VERSION_ID=%{dist_version}
PRETTY_NAME="Korora %{dist_version} (%{release_name})"
ANSI_COLOR="0;34"
CPE_NAME="cpe:/o:kororaproject:korora:%{dist_version}"
HOME_URL="https://kororaproject.org/"
PRIVACY_POLICY_URL=https://fedoraproject.org/wiki/Legal:PrivacyPolicy
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

# Atomic Host - https://bugzilla.redhat.com/show_bug.cgi?id=1200122
cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-atomichost
echo "VARIANT=\"Atomic Host\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-atomichost
echo "VARIANT_ID=atomic.host" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-atomichost
sed -i -e "s|(%{release_name})|(Atomic Host)|g" $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-atomichost

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
#echo "VARIANT=\"\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-workstation
#echo "VARIANT_ID=\"\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-workstation
#sed -i -e "s|(%{release_name})|(Workstation Edition)|g" $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-workstation

# Create the symlink for /etc/os-release
# We don't create the /usr/lib/os-release symlink until %%post
# so that we can ensure that the right one is referenced.
ln -s ../usr/lib/os-release $RPM_BUILD_ROOT/etc/os-release

# Create the symlink for /etc/issue
# We don't create the /usr/lib/os-release symlink until %%post
# so that we can ensure that the right one is referenced.
ln -s ../usr/lib/issue $RPM_BUILD_ROOT/etc/issue

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
mkdir -p $RPM_BUILD_ROOT/usr/lib/os.release.d/presets

# Default system wide
install -m 0644 85-display-manager.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -m 0644 90-default.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -m 0644 99-default-disable.preset $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
# Fedora Server
install -m 0644 80-server.preset $RPM_BUILD_ROOT%{_prefix}/lib/os.release.d/presets/
# Fedora Workstation
install -m 0644 80-workstation.preset $RPM_BUILD_ROOT%{_prefix}/lib/os.release.d/presets/

# Override the list of enabled gnome-shell extensions for Workstation
mkdir -p $RPM_BUILD_ROOT%{_datadir}/glib-2.0/schemas/
install -m 0644 org.gnome.shell.gschema.override $RPM_BUILD_ROOT%{_datadir}/glib-2.0/schemas/

# Copy the make_edition script to /usr/sbin
mkdir -p $RPM_BUILD_ROOT/%{_prefix}/sbin/
install -m 0744 convert-to-edition $RPM_BUILD_ROOT/%{_prefix}/sbin/

%post -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
-- On initial installation, we'll at least temporarily put the non-product
-- symlinks in place. It will be overridden by fedora-release-$EDITION
-- %%post sections because we don't write the /usr/lib/variant file until
-- %%posttrans to avoid trumping the fedora-release-$EDITION packages.
-- This is necessary to avoid breaking systemctl scripts since they rely on
-- /usr/lib/os-release being valid. We can't wait until %%posttrans to default
-- to os-release-fedora.
if arg[2] == "0" then
    set_release(fedora)
    set_issue(fedora)
end

-- We also want to forcibly set these paths on upgrade if we are explicitly
-- set to "nonproduct"
if read_variant() == "nonproduct" then
    convert_to_edition("nonproduct", false)
end

%posttrans -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
-- If we get to %%posttrans and nothing created /usr/lib/variant, set it to
-- nonproduct.
install_edition("nonproduct")

%post atomichost -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
install_edition("atomichost")

%preun atomichost -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
uninstall_edition("atomichost")

%post cloud -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
install_edition("cloud")

%preun cloud -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
uninstall_edition("cloud")

%post server -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
install_edition("server")

%preun server -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
uninstall_edition("server")

%post workstation -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
install_edition("workstation")

%preun workstation -p <lua>
%include %{_sourcedir}/convert-to-edition.lua
uninstall_edition("workstation")

%postun workstation
if [ $1 -eq 0 ] ; then
    glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi

%posttrans workstation
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE Fedora-Legal-README.txt
%ghost /usr/lib/variant
%dir /usr/lib/os.release.d
%dir /usr/lib/os.release.d/presets
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-fedora
%ghost /usr/lib/os-release
/etc/os-release
%config %attr(0644,root,root) /etc/fedora-release
/etc/redhat-release
/etc/system-release
%config %attr(0644,root,root) /etc/system-release-cpe
%config %attr(0644,root,root) /usr/lib/os.release.d/issue-fedora
%ghost /usr/lib/issue
%config(noreplace) /etc/issue
%config %attr(0644,root,root) /usr/lib/issue.net
%config(noreplace) /etc/issue.net
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist
%dir /usr/lib/systemd/user-preset/
%dir %{_prefix}/lib/systemd/system-preset/
%{_prefix}/lib/systemd/system-preset/85-display-manager.preset
%{_prefix}/lib/systemd/system-preset/90-default.preset
%{_prefix}/lib/systemd/system-preset/99-default-disable.preset
/usr/sbin/convert-to-edition

%files atomichost
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-atomichost


%files cloud
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-cloud


%files server
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-server
%config %attr(0644,root,root) /usr/lib/os.release.d/issue-server
%ghost %{_prefix}/lib/systemd/system-preset/80-server.preset
%config %attr(0644,root,root) /usr/lib/os.release.d/presets/80-server.preset

%files workstation
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-workstation
%{_datadir}/glib-2.0/schemas/org.gnome.shell.gschema.override
%ghost %{_prefix}/lib/systemd/system-preset/80-workstation.preset
%config %attr(0644,root,root) /usr/lib/os.release.d/presets/80-workstation.preset


%changelog
* Wed Oct  9 2017 Ian Firns <firnsy@kororaproject.org> - 27-0.1
- Korora 27

* Wed Sep 13 2017 Ian Firns <firnsy@kororaproject.org> - 26-2
- Korora 26 release

* Sun May  1 2017 Ian Firns <firnsy@kororaproject.org> - 26-1
- Korora 26

* Thu Nov 24 2016 Chris Smart <csmart@kororaproject.org> - 25-2
- Korora 25 release

* Thu Sep 01 2016 Chris Smart <csmart@kororaproject.org> - 25-1
- Korora 25

* Thu May 12 2016 Chris Smart <csmart@kororaproject.org> - 24-1
- Korora 24

* Sat Feb 27 2016 Chris Smart <csmart@kororaproject.org> - 23-3
- Don't use workstation branding

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
