%define release_name Twenty Two
%define dist_version 22
%define bug_version 22

Summary:        Fedora release files
Name:           fedora-release
Version:        22
Release:        1
License:        MIT
Group:          System Environment/Base
URL:            http://fedoraproject.org
Source:         %{name}-%{version}.tar.bz2
Obsoletes:      redhat-release
Provides:       redhat-release
Provides:       system-release
Provides:       system-release(%{version})

# Kill off the fedora-release-nonproduct package
Provides:       fedora-release-nonproduct = %{version}
Obsoletes:      fedora-release-nonproduct <= 23-0.3
Provides:       fedora-release-standard = 22-0.8
Obsoletes:      fedora-release-standard < 22-0.8

Requires:       fedora-repos(%{version})
BuildArch:      noarch

%description
Fedora release files such as various /etc/ files that define the release.

%package cloud
Summary:        Base package for Fedora Cloud-specific default configurations
Provides:       system-release-cloud
Provides:       system-release-cloud(%{version})
Provides:       system-release-product
Requires:       fedora-release = %{version}-%{release}

%description cloud
Provides a base package for Fedora Cloud-specific configuration files to
depend on.

%package server
Summary:        Base package for Fedora Server-specific default configurations
Provides:       system-release-server
Provides:       system-release-server(%{version})
Provides:       system-release-product
Requires:       fedora-release = %{version}-%{release}
Requires:       systemd
Requires:       cockpit
Requires:       rolekit
Requires(post): sed
Requires(post): systemd

%description server
Provides a base package for Fedora Server-specific configuration files to
depend on.

%package workstation
Summary:        Base package for Fedora Workstation-specific default configurations
Provides:       system-release-workstation
Provides:       system-release-workstation(%{version})
Provides:       system-release-product
Requires:       fedora-release = %{version}-%{release}
# needed for captive portal support
Requires:       NetworkManager-config-connectivity-fedora
Requires(post): /usr/bin/glib-compile-schemas
Requires(postun): /usr/bin/glib-compile-schemas

%description workstation
Provides a base package for Fedora Workstation-specific configuration files to
depend on.

%prep
%setup -q
sed -i 's|@@VERSION@@|%{dist_version}|g' Fedora-Legal-README.txt

%build

%install
install -d $RPM_BUILD_ROOT/etc
echo "Fedora release %{version} (%{release_name})" > $RPM_BUILD_ROOT/etc/fedora-release
echo "cpe:/o:fedoraproject:fedora:%{version}" > $RPM_BUILD_ROOT/etc/system-release-cpe
cp -p $RPM_BUILD_ROOT/etc/fedora-release $RPM_BUILD_ROOT/etc/issue
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/etc/issue
cp -p $RPM_BUILD_ROOT/etc/issue $RPM_BUILD_ROOT/etc/issue.net
echo >> $RPM_BUILD_ROOT/etc/issue
ln -s fedora-release $RPM_BUILD_ROOT/etc/redhat-release
ln -s fedora-release $RPM_BUILD_ROOT/etc/system-release

# Create the common os-release file
install -d $RPM_BUILD_ROOT/usr/lib/os.release.d/
cat << EOF >>$RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora
NAME=Fedora
VERSION="%{dist_version} (%{release_name})"
ID=fedora
VERSION_ID=%{dist_version}
PRETTY_NAME="Fedora %{dist_version} (%{release_name})"
ANSI_COLOR="0;34"
CPE_NAME="cpe:/o:fedoraproject:fedora:%{dist_version}"
HOME_URL="https://fedoraproject.org/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=%{bug_version}
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=%{bug_version}
PRIVACY_POLICY_URL=https://fedoraproject.org/wiki/Legal:PrivacyPolicy
EOF

# Create os-release files for the different editions
# Cloud
cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud
echo "VARIANT=\"Cloud Edition\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud
echo "VARIANT_ID=cloud" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-cloud

# Server
cp -p $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-fedora \
      $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server
echo "VARIANT=\"Server Edition\"" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server
echo "VARIANT_ID=server" >> $RPM_BUILD_ROOT/usr/lib/os.release.d/os-release-server

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


# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
cat >> $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.dist << EOF
# dist macros.

%%fedora                %{dist_version}
%%dist                .fc%{dist_version}
%%fc%{dist_version}                1
EOF

# Add Product-specific presets
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset/
# Fedora Server
install -m 0644 80-server.preset %{buildroot}%{_prefix}/lib/systemd/system-preset/
# Fedora Workstation
install -m 0644 80-workstation.preset %{buildroot}%{_prefix}/lib/systemd/system-preset/

# Override the list of enabled gnome-shell extensions for Workstation
mkdir -p %{buildroot}%{_datadir}/glib-2.0/schemas/
install -m 0644 org.gnome.shell.gschema.override %{buildroot}%{_datadir}/glib-2.0/schemas/

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
%{!?_licensedir:%global license %%doc}
%license LICENSE Fedora-Legal-README.txt
%dir /usr/lib/os.release.d
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-fedora
/usr/lib/os-release
/etc/os-release
%config %attr(0644,root,root) /etc/fedora-release
/etc/redhat-release
/etc/system-release
%config %attr(0644,root,root) /etc/system-release-cpe
%config(noreplace) %attr(0644,root,root) /etc/issue
%config(noreplace) %attr(0644,root,root) /etc/issue.net
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist

%files cloud
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-cloud

%files server
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-server
%{_prefix}/lib/systemd/system-preset/80-server.preset

%files workstation
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %attr(0644,root,root) /usr/lib/os.release.d/os-release-workstation
%{_datadir}/glib-2.0/schemas/org.gnome.shell.gschema.override
%{_prefix}/lib/systemd/system-preset/80-workstation.preset

%changelog
* Thu May 14 2015 Dennis Gilmore <dennis@ausil.us> - 22-1
- prep for F22 Final release rhbz#1221726
- change POLICY_POLICY to POLICY_POLICY_URL rhbz#1182635

* Fri May 08 2015 Dennis Gilmore <dennis@ausil.us> - 22-0.17
- make sure that the VARIANT is wrapped in ""

* Tue May 05 2015 Stephen Gallagher <sgallagh@redhat.com> 22-0.16
- Follow systemd upstream guidelines for VARIANT and VARIANT_ID

* Thu Apr 23 2015 Stephen Gallagher <sgallagh@redhat.com> 22-0.15
- Handle os-release upgrades from existing productized installations

* Mon Mar 16 2015 Stephen Gallagher <sgallagh@redhat.com> 22-0.14
- Generate os-release based on product subpackages
- Remove the -nonproduct subpackage
- Eliminate Conflicts between subpackages
- Add preset file for workstation to disable sshd
- make the os-release sysmlinks all relative

* Tue Feb 24 2015 Dennis Gilmore <dennis@ausil.us> - 22-0.13
- make the /etc/os-release symlink relative rhbz#1192276

* Tue Feb 10 2015 Peter Robinson <pbrobinson@fedoraproject.org> 22-0.12
- bump

* Tue Feb 10 2015 Peter Robinson <pbrobinson@fedoraproject.org> 22-0.11
- Setup for f22 branch
- Add PRIVACY_POLICY_URL to os-release (rhbz#1182635)
- Move os-release to /usr/lib and symlink to etc (rhbz#1149568)

* Thu Nov 20 2014 Kalev Lember <kalevlember@gmail.com> - 22-0.10
- Ship an override file to enable the gnome-shell background logo extension
  in Workstation (#1161637)
- fix up handling of schema file from inccorect initail handling - dennis

* Tue Nov 18 2014 Dennis Gilmore <dennis@ausil.us> - 22-0.9
- drop Requires on system-release-product rhbz#1156198

* Mon Oct 06 2014 Ray Strode <rstrode@redhat.com> 22-0.8
- Rename fedora-release-standard to fedora-release-nonproduct
  following discussion on list and irc

* Fri Oct 03 2014 Stephen Gallagher <sgallagh@redhat.com> 22-0.7
- Add system-release-product virtual Provides and Requires

* Tue Sep 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 22-0.6
- Add requires for captive portal to Workstation

* Mon Aug 04 2014 Dennis Gilmore <dennis@ausil.us> - 22-0.5
- reapply presets after installing

* Wed Jul 23 2014 Dennis Gilmore <dennis@ausil.us> - 22-0.4
- add patch from https://fedorahosted.org/rel-eng/ticket/5947 for server

* Mon Jul 14 2014 Stephen Gallagher <sgallagh@redhat.com> 22-0.3
- Add systemd preset file for Fedora Server
- Add requirement on Cockpit

* Sat Jul 12 2014 Tom Callaway <spot@fedoraproject.org> 22-0.2
- fix license handling

* Tue Jul 08 2014 Dennis Gilmore <dennis@ausil.us> 22-0.1
- setup for rawhide targetiing f22

* Tue Jul 08 2014 Stephen Gallagher <sgallagh@redhat.com> 21-0.8
- Provide new release file metapackages for Fedora Products
- drop .repo files and gpg keys (dennis)
- Require fedora-repos

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 21-0.7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 10 2014 Dennis Gilmore <dennis@ausil.us> - 21-0.6
- update Fedora-Legal-README.txt with updates from legal rhbz#1096434
- Change license to MIT to reflect the change in the fedora compilation
- based on reccomendations from Red Hat Legal rhbz#1096434

* Wed Feb 17 2014 Dennis Gilmore <dennis@ausil.us> - 21-0.5
- provide system-release(%%version) rhbz#1047058

* Mon Jan 13 2014 Dennis Gilmore <dennis@ausil.us> - 21-0.4
- set metadata expiry to 12 hours as dnf defaults to something silly bz#1045678

* Sat Dec 28 2013 Ville Skyttä <ville.skytta@iki.fi> - 21-0.3
- Install macros.dist as non-%%config to %%{_rpmconfigdir}/macros.d (#846679).
- Fix bogus date in %%changelog.

* Wed Nov 13 2013 Dennis Gilmore <dennis@ausil.us> - 21-0.2
- remove f20 keys add f21
- patch from Will Woods to use a archmap file for linking gpg keys
- add fields to /etc/os-release for rhbz#951119
- set skip_if_unavailable=False for rhbz#985354

* Tue Aug 20 2013 Dennis Gilmore <dennis@ausil.us> - 21-0.1
- setup for f21 rawhide

* Wed Jul 31 2013 Dennis Gilmore <dennis@ausil.us> - 20-0.4
- link armhfp gpg key to primary since its now living there

* Mon Jul 08 2013 Dennis Gilmore <dennis@ausil.us> - 20-0.3
- fix up typo

* Wed Jun 19 2013 Dennis Gilmore <dennis@ausil.us> - 20-0.2
- add f20 keys
- switch mirrorlist= to metalink= bz#948788
- add bugzilla fields to os-release for brokeness in abrt bz#961477
- add releasever into gpgkey paths
- use consistent macros for dist_release value

* Tue Mar 12 2013 Dennis Gilmore <dennis@ausil.us> - 20-0.1
- setup for f20
- 64 bit arm arch is aarch64 not arm64
- drop sparc arches

* Wed Aug 08 2012 Dennis Gilmore <dennis@ausil.us> - 19-0.1
- setup for f19

* Mon Aug 06 2012 Dennis Gilmore <dennis@ausil.us> - 18-0.6
- sync up from dist-git
- replace the fedora 18 gpg keys
- bring the Fedora-Legal-README file into upstream

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 18-0.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Mar 29 2012 Tom Callaway <spot@fedoraproject.org> - 18-0.4
- add Fedora-Legal-README.txt

* Mon Feb 27 2012 Dennis Gilmore <dennis@ausil.us> - 18-0.3
 add CPE info to os-release file bz#790509

* Wed Feb 08 2012 Dennis Gilmore <dennis@ausil.us> - 18-0.2
- add /etc/os-release file for bz#733117

* Tue Jan 10 2012 Dennis Gilmore <dennis@ausil.us> - 18-0.1
- setup for fedora 18
- add the fedora 18 gpg keys

* Tue Jan 10 2012 Dennis Gilmore <dennis@ausil.us> - 17-0.4
- install the fedora 17 gpg keys

* Wed Dec 28 2011 Dennis Gilmore <dennis@ausil.us> - 17-0.3
- symlink the secondary arch key for the armhfp and arm64 basearch

* Tue Jul 26 2011 Dennis Gilmore <dennis@ausil.us> - 17-0.2
- set dist_version to 17

* Tue Jul 26 2011 Dennis Gilmore <dennis@ausil.us> - 17-0.1
- build for Fedora 17

* Thu Feb 10 2011 Dennis Gilmore <dennis@ausil.us> - 16-0.1
- Build for Fedora 16

* Wed Feb 09 2011 Dennis Gilmore <dennis@ausil.us> - 15-0.5
- Add the Fedora 15 key

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 15-0.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jul 29 2010 Jesse Keating <jkeating@redhat.com> - 15-0.1
- Build for Fedora 15

* Fri Jul 23 2010 Jesse Keating <jkeating@redhat.com> - 14-0.6
- Add the Fedora 14 key

* Thu May 06 2010 Dennis Gilmore <dennis@ausil.us> - 14-0.5
- link sparc key
- drop ppc ppc64 from primary arch list

* Tue Mar 02 2010 Jesse Keating <jkeating@redhat.com> - 14-0.4
- When in rawhide, require the -rawhide subpackage.

* Thu Feb 18 2010 Jesse Keating <jkeating@redhat.com> - 14-0.3
- Fix the key path in the updates-testing repo

* Thu Feb 18 2010 Jesse Keating <jkeating@redhat.com> - 14-0.2
- Fix the -rawhide requires
- Fix the -rawhide files
- Switch to bz2 source

* Mon Feb 15 2010 Jesse Keating <jkeating@redhat.com> - 14-0.1
- Update for Fedora 14
- Move the rawhide repo file to it's own subpackage

* Tue Jan 19 2010 Jesse Keating <jkeating@redhat.com> - 13-0.3
- Put the right key in the key file this time

* Tue Jan 19 2010 Jesse Keating <jkeating@redhat.com> - 13-0.2
- Add the key for Fedora 13

* Thu Aug 27 2009 Jesse Keating <jkeating@redhat.com> - 13-0.1
- Bump for Fedora 13's rawhide.
- Put the version at 13 from the start.

* Fri Aug 07 2009 Jesse Keating <jkeating@redhat.com> - 11.91-3
- Bump for new tarball

* Fri Aug 07 2009 Jesse Keating <jkeating@redhat.com> - 11.91-2
- Fix the gpg key file name

* Fri Aug 07 2009 Jesse Keating <jkeating@redhat.com> - 11.91-1
- Update for F12-Alpha
- Replace F11 key with F12
- Drop old keys and inactive secondary arch keys
- Fix metalink urls to be https
- Drop the compose stuff

* Mon Mar 30 2009 Jesse Keating <jkeating@redhat.com> - 11.90-1
- Build for F12 collection

* Mon Mar 09 2009 Jesse Keating <jkeating@redhat.com> - 10.92-1
- Bump for F11 Beta
- Add the (giant) F11 Test key

* Thu Mar 05 2009 Jesse Keating <jkeating@redhat.com> - 10.91-4
- Drop req on fedora-release-notes (#483018)

* Tue Mar 03 2009 Jesse Keating <jkeating@redhat.com> - 10.91-3
- Move metalink urls to mirrorlist for helping anaconda

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 04 2009 Jesse Keating <jkeating@redhat.com> - 10.91-1
- Use the correct CPE name (#481287)

* Wed Jan 21 2009 Jesse Keating <jkeating@redhat.com> - 10.91-1
- Update for Fedora 11 Alpha
- Use metalink urls to get mirror information

* Wed Oct 01 2008 Jesse Keating <jkeating@redhat.com> - 10.90-1
- Initial build for Fedora 11.

* Mon Sep 15 2008 Jesse Keating <jkeating@redhat.com> - 9.91-1
- Update for Fedora 10 beta
- Add the new keys for F10
- Remove F8/9 keys
- Update compose configs
- Clarify rawhide repo definition

* Wed Jun 11 2008 Jesse Keating <jkeating@redhat.com> - 9.90-2
- Package up the ia64 key as the first secondary arch
- Mark config files correctly
- Stop using download.fedora.redhat.com and use download.fedoraproject.org instead

* Mon Mar 31 2008 Jesse Keating <jkeating@redhat.com> - 9.90-1
- Update for Fedora 10 rawhide.

* Thu Mar 13 2008 Jesse Keating <jkeating@redhat.com> - 8.92-1
- Update for 9 Beta
- Update the compose files for 9 Beta
- Add system-release-cpe (from Mark Cox)
- Add terminal to issue (#436387)
- Rename development to rawhide where appropriate.

* Wed Oct 10 2007 Jesse Keating <jkeating@redhat.com> - 8.90-3
- Bump for cvs oopsie

* Wed Oct 10 2007 Jesse Keating <jkeating@redhat.com> - 8.90-2
- Add the gpg info to the devel repo

* Wed Oct 03 2007 Jesse Keating <jkeating@redhat.com> - 8.90-1
- First build for Fedora 9 development.

* Fri Sep 28 2007 Jesse Keating <jkeating@redhat.com> - 7.92-1
- Bump for F8 Test2.
- Package up the compose kickstart files

* Fri Sep 14 2007 Jesse Keating <jkeating@redhat.com> - 7.91-2
- Use failovermethod=priority in yum configs (243698)

* Thu Aug 30 2007 Jesse Keating <jkeating@redhat.com> - 7.91-1
- Provide system-release, useful for spinoffs.
- Also link system-release to fedora-release for file level checks
- Bump for F8 Test2
- Fix license tag

* Fri Jul 27 2007 Jesse Keating <jkeating@redhat.com> - 7.90-1
- Bump for F8 Test1

* Thu Jun 28 2007 Jesse Keating <jkeating@redhat.com> - 7.89-3
- Cleanups from review
- Don't (noreplace) the dist tag macro file

* Tue Jun 19 2007 Jesse Keating <jkeating@redhat.com> - 7.89-2
- Define the dist macros in this package since we define everyting else here

* Wed May 30 2007 Jesse Keating <jkeating@redhat.com> - 7.89-1
- And we're back to rawhide.  Re-enable devel repos

* Thu May 24 2007 Jesse Keating <jkeating@redhat.com> - 7-3
- We have a name!
- Require the newer release notes

* Mon May 21 2007 Jesse Keating <jkeating@redhat.com> - 7-2
- Use Everything in the non-mirror URL to the release tree

* Mon May 21 2007 Jesse Keating <jkeating@redhat.com> - 7-1
- First build for Fedora 7
- Remove Extras repos (YAY!)
- Remove references to "core" in repo files.
- Adjust repo files for new mirror structure
- Remove Legacy repo

* Fri Apr 20 2007 Jesse Keating <jkeating@redhat.com> - 6.93-1
- Bump for Test 4

* Mon Mar 19 2007 Jesse Keating <jkeating@redhat.com> - 6.92-1
- Bump for Test 3
- No more eula in fedora-release, moved to firstboot

* Fri Feb 23 2007 Jesse Keating <jkeating@redhat.com> - 6.91-1
- Bump for Test 2

* Tue Feb 13 2007 Jesse Keating <jkeating@redhat.com> - 6.90-4
- Specfile cleanups

* Mon Feb 05 2007 Jesse Keating <jkeating@redhat.com> - 6.90-3
- Drop the legacy repo file.

* Fri Jan 26 2007 Jesse Keating <jkeating@redhat.com> - 6.90-2
- Core?  What Core?

* Wed Jan 24 2007 Jeremy Katz <katzj@redhat.com> - 6.90-1
- Bump to 6.90.  Keep working with older release notes

* Mon Oct 16 2006 Jesse Keating <jkeating@redhat.com> - 6-89
- Keep version 6, bump release.  Saves from having to rebuild
  release notes all the time

* Sun Oct 15 2006 Jesse Keating <jkeating@redhat.com> - 6.89-1
- Rebuild for rawhide

* Thu Oct 12 2006 Jesse Keating <jkeating@redhat.com> - 6-3
- version has to stay the same, safe to use.

* Thu Oct  5 2006 Jesse Keating <jkeating@redhat.com> - 6-2
- replace old mirror files with new mirrorlist cgi system

* Thu Oct  5 2006 Jesse Keating <jkeating@redhat.com> - 6-1
- Rebuild for Fedora Core 6 release

* Tue Sep  5 2006 Jesse Keating <jkeating@redhat.com> - 5.92-1
- Bump for FC6 Test3

* Thu Jul 27 2006 Jesse Keating <jkeating@redhat.com> - 5.91.1-1
- Convert deprecated gtk calls. (#200242)
- Fix some of the versioning

* Sun Jul 23 2006 Jesse Keating <jkeating@redhat.com> - 5.91-4
- Bump for FC6 Test2
- Remove release-notes content, now standalone package
- Don't replace issue and issue.net if the end user has modified it
- Require fedora-release-notes
- Cleanups

* Mon Jun 19 2006 Jesse Keating <jkeating@redhat.com> - 5.90-3
- Cleanups

* Thu Jun 15 2006 Jesse Keating <jkeating@redhat.com> - 5.90-1
- Update for 5.90

* Wed May 24 2006 Jesse Keating <jkeating@redhat.com> - 5.89-rawhide.2
- Update to get new devel repo file
- merge minor changes from external cvs .spec file

* Wed Apr 19 2006 Jesse Keating <jkeating@redhat.com> - 5.89-rawhide.1
- Look, a changelog!
- Removed duplicate html/css content from doc dir.
- Add lynx as a buildreq

