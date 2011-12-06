%define gtk2_version 2.6.0
%define pygtk2_version 2.15.0
%define gnome_python2_version 2.6.0-5

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%define sabayon_user_uid 86

Name:    sabayon
Version: 2.29.92
Release: 1%{?dist}
Summary: Tool to maintain user profiles in a GNOME desktop

Group:   Applications/System
License: GPLv2+
URL:     http://www.gnome.org/projects/sabayon
Source:  http://ftp.gnome.org/pub/GNOME/sources/sabayon/2.29/sabayon-%{version}.tar.bz2

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: %{name}-apply = %{version}-%{release}
Requires: libxml2-python
Requires: pygtk2 >= %{pygtk2_version}
Requires: usermode
Requires: gnome-python2-gconf >= %{gnome_python2_version}
Requires: pyxdg
Requires: pessulus

BuildRequires: pessulus
BuildRequires: python-devel
BuildRequires: pygtk2-devel
BuildRequires: gtk2-devel
BuildRequires: libX11-devel
BuildRequires: libXt-devel
BuildRequires: gettext
BuildRequires: desktop-file-utils
BuildRequires: usermode
BuildRequires: pyxdg
BuildRequires: xorg-x11-server-Xephyr
# Needed to pick up the right Xsession file
BuildRequires: xorg-x11-xinit

BuildRequires: intltool
BuildRequires: libtool

BuildRequires: gnome-doc-utils
# scrollkeeper replacement
BuildRequires: rarian-compat

Requires(post):  shadow-utils
Requires(preun): shadow-utils

Requires(post):   gtk2 >= %{gtk2_version}
Requires(postun): gtk2 >= %{gtk2_version}

%description
Sabayon is a tool to help sysadmins and user change and maintain the
default behavior of the GNOME desktop. This package contains the
graphical tools which a sysadmin use to manage Sabayon profiles.

%package  apply
Summary:  The parts of sabayon needed on the client systems
Group:    Applications/System

Requires: xorg-x11-server-Xephyr
Requires: shadow-utils
Requires: gamin-python
Requires: python-ldap
Requires: libxml2-python
Requires: libselinux-python
Requires: pyxdg
Requires: gnome-python2-gconf >= %{gnome_python2_version}


%description apply
Sabayon is a tool to help sysadmins and user change and maintain the
default behavior of the GNOME desktop. This package contains the files
that need to be installed on the client systems.

%prep
%setup -q -n %{name}-%{version}

# https://fedoraproject.org/wiki/Features/SystemPythonExecutablesUseSystemPython
# replace "/usr/bin/env python" with a "/usr/bin/python"
for i in lib/unittests.py admin-tool/sabayon admin-tool/sabayon-session admin-tool/sabayon-apply ; do
   sed -i.bak 's|^#!/usr/bin/env python|#!/usr/bin/python|g' $i
   touch -r ${i}.bak $i
   rm ${i}.bak
done


%build
%configure					\
	--enable-console-helper=yes		\
	--with-prototype-user=%{name}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}
gzip -9 ChangeLog

%install
rm -rf $RPM_BUILD_ROOT
export PAM_PREFIX=%{buildroot}%{_sysconfdir}
make DESTDIR=%{buildroot} install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2
echo 'include "$(HOME)/.gconf.path.defaults"'  > $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2/local-defaults.path
echo 'include "$(HOME)/.gconf.path.mandatory"' > $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2/local-mandatory.path

desktop-file-install --vendor gnome --delete-original		\
	--dir $RPM_BUILD_ROOT%{_datadir}/applications		\
	$RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop

# We don't want these
rm -f $RPM_BUILD_ROOT%{python_sitearch}/%{name}/xlib.la
rm -f $RPM_BUILD_ROOT%{python_sitearch}/%{name}/xlib.a

rm -f $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/icon-theme.cache

rm -f $RPM_BUILD_ROOT%{_bindir}/%{name}
ln -s consolehelper $RPM_BUILD_ROOT%{_bindir}/%{name}

%find_lang sabayon

%clean
rm -rf $RPM_BUILD_ROOT

%pre
/usr/sbin/groupadd -g %{sabayon_user_uid} -r %{name} &>/dev/null || :
/usr/sbin/useradd  -r -u %{sabayon_user_uid} -s /sbin/nologin -c "Sabayon user" -g %{name} %{name} &>/dev/null || :
# Delete the old sabayon-admin user
/usr/sbin/usermod -d "" %{name}-admin &>/dev/null || :

%post
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%postun
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

if [ $1 -eq 0 ]; then
  /usr/sbin/userdel  %{name} &>/dev/null || :
  /usr/sbin/groupdel %{name} &>/dev/null || :
fi


%files apply -f sabayon.lang
%defattr(-, root, root, 755)

%doc AUTHORS NEWS README TODO ISSUES

%config(noreplace) %{_sysconfdir}/gconf/2/local-defaults.path
%config(noreplace) %{_sysconfdir}/gconf/2/local-mandatory.path
%config(noreplace) %{_sysconfdir}/X11/xinit/xinitrc.d/%{name}*

%{_sysconfdir}/sabayon/profiles

%{_sbindir}/%{name}-apply

%dir %{python_sitearch}/%{name}/
# https://fedoraproject.org/wiki/Packaging/Python#Including_pyos
%{python_sitearch}/%{name}/__init__.py*
%{python_sitearch}/%{name}/config.py*
%{python_sitearch}/%{name}/cache.py*
%{python_sitearch}/%{name}/dirmonitor.py*
%{python_sitearch}/%{name}/mozilla_bookmarks.py*
%{python_sitearch}/%{name}/storage.py*
%{python_sitearch}/%{name}/systemdb.py*
%{python_sitearch}/%{name}/userprofile.py*
%{python_sitearch}/%{name}/util.py*
%{python_sitearch}/%{name}/debuglog.py*
%{python_sitearch}/%{name}/errors.py*

%dir %{python_sitearch}/%{name}/sources
%{python_sitearch}/%{name}/sources/*.py*

%files
%defattr(-, root, root, -)
%doc %{_datadir}/gnome/help/sabayon/*
%doc %{_datadir}/omf/sabayon/*

%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}

%{_bindir}/%{name}
%{_sbindir}/%{name}
%{_libexecdir}/%{name}*

%dir %{_datadir}/%{name}
%{_datadir}/applications/gnome-%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%{python_sitearch}/%{name}/xlib.so

%{python_sitearch}/%{name}/aboutdialog.py*
%{python_sitearch}/%{name}/changeswindow.py*
%{python_sitearch}/%{name}/editorwindow.py*
%{python_sitearch}/%{name}/fileviewer.py*
%{python_sitearch}/%{name}/gconfviewer.py*
%{python_sitearch}/%{name}/groupsdialog.py*
%{python_sitearch}/%{name}/profilesdialog.py*
%{python_sitearch}/%{name}/protosession.py*
%{python_sitearch}/%{name}/saveconfirm.py*
%{python_sitearch}/%{name}/sessionwidget.py*
%{python_sitearch}/%{name}/sessionwindow.py*
%{python_sitearch}/%{name}/usermod.py*
%{python_sitearch}/%{name}/usersdialog.py*
%{python_sitearch}/%{name}/lockdownappliersabayon.py*
%{_mandir}/man8/*
%{_datadir}/sabayon/ui/


%changelog
* Tue Feb 23 2010 Warren Togami <wtogami@redhat.com> - 2.29.92-1
- 2.29.92 with more bug fixes
  More permissions handling and crash fixes

* Mon Feb 22 2010 Warren Togami <wtogami@redhat.com> - 2.29.91-1
- 2.29.91 with important bug fixes
  Saves and Restores File Permissions
  Details pane is now less confusing
  Common Editor Crasher Fixed

* Thu Jan 28 2010 Warren Togami <wtogami@redhat.com> - 2.29.5-3
- Make consolehelper actually work

* Fri Jan 15 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.29.5-2
- Cleanup for package review

* Thu Jan 14 2010 Warren Togami <wtogami@redhat.com> - 2.29.5-1
- 2.29.5 (no code changes since rc2)

* Thu Dec 31 2009 Warren Togami <wtogami@redhat.com> - 2.29.5-0.1.rc2
- Update to 2.95.5-rc2
- glade removed, replaced by GNOME Builder 
- /etc/desktop-profile moved to /etc/sabayon/profiles
  Manual Migration:
  mv /etc/desktop-profiles/*.xml /etc/sabayon
  mv /etc/desktop-profiles/*.zip /etc/sabayon/profiles

* Wed Dec  9 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.29.2-1
- Update to 2.29.2

* Tue Oct 27 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.29.0-1
- Update to 2.29.0

* Fri Oct 23 2009 Dan Walsh <dwalsh@redhat.com> - 2.28.0-2
- Move errors to sabayon-apply package
- Only trap Exception on sabayon-apply error

* Tue Sep 22 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Wed Aug 19 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.27.91-1
- Update to 2.27.91

* Tue Aug 11 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.27.0-1
- Update to 2.27.0

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Apr 20 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.0-3
- Another, more complete fix for panel gconf save issues (gnome #542604)

* Fri Apr  3 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.0-2
- Fix some gconf crashes (gnome #576445)
- Temporarily switched back to Xnest to get working keyboard (gnome #576447)

* Fri Mar 20 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.25.0-1
- Update to 2.25.0

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.22.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.22.1-2
- Rebuild for Python 2.6

* Tue Sep 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Wed Sep 10 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.22.0-4
- Fix saving lockdown settings

* Tue Apr 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-3
- Actually apply the Xephyr patch

* Tue Apr 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-2
- Use Xephyr instead of Xnest

* Tue Mar 11 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Fri Feb 22 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.21.0-3
- sabayon-apply requires libxml2-python (#428351) and gnome-python2 stuff

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.21.0-2
- Autorebuild for GCC 4.3

* Sun Jan 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.0-1
- Update to 2.21.0

* Sun Dec  9 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-4
- Don't use gnomesu

* Fri Oct 12 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-3
- Be more robust when directories are missing (#329471)
- Work better with SELinux (#329501)
- Move debuglog.py to the -apply package (#330001)

* Thu Oct 11 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-2
- Require pyxdg (#327851)

* Wed Sep 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1

* Thu Aug 16 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-3
- Update the license field

* Wed Jul 25 2007 Jeremy Katz <katzj@redhat.com> - 2.19.1-2
- rebuild for toolchain bug

* Mon Jul 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-1
- Update to 2.19.1

* Wed Apr 11 2007 Alexander Larsson <alexl@redhat.com> - 2.18.1-1
- Update to 2.18.1
- Move gamin-python and python-ldap requires to sabayon-apply subpackage
- Own datadir subdirs (#233912)

* Tue Mar 13 2007 Alexander Larsson <alexl@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Mon Dec 11 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-8
- Add intltool buildreq

* Mon Dec 11 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-7
- Also add libtool buildreq

* Mon Dec 11 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-6
- Add aclocal call to build with automake 1.10

* Mon Dec 11 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-5
- rebuild for new python

* Thu Oct 05 2006 Christian Iseli <Christian.Iseli@licr.org> 2.12.4-4
 - rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Tue Sep 19 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-3
- Rebuild with new toolchain

* Thu Jul 27 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-2
- Fix multilib issues

* Thu Jul 27 2006 Alexander Larsson <alexl@redhat.com> - 2.12.4-1
- Update to 2.14.4
- Ghost .pyo files
- Use a more modern pam file
- Remove macros from changelog
- Add usermode dependency
- Made sabayon symlink relative
- Add dist tag

* Tue Jul 25 2006 Alexander Larsson <alexl@redhat.com> - 2.12.3-5
- Rename sabayon-admin user to sabayon (< 8 chars)
- Use registered uid/gid for user
- Rename sabayon-admin package to sabayon, sabayon becomes sabayon-apply
- Add workaround for Xnest crash in rawhide

* Mon Jul 24 2006  <markmc@localhost.localdomain> - 2.12.3-4
- Remove FC4 stuff
- Add BuildRequires for autoconf and perl-XML-Parser
- Remove python-abi Requires

* Thu Mar  9 2006 Alexander Larsson <alexl@redhat.com> - 2.12.3-3
- Add xorg-x11-xinit build-req so configure picks the
  right Xsession script

* Tue Mar  7 2006 Alexander Larsson <alexl@redhat.com> - 2.12.3-2
- Add libXt-devel buildreq

* Mon Mar  6 2006 Alexander Larsson <alexl@redhat.com> - 2.12.3-1
- update to 2.12.3
- Fix Xnest dependency with modular X
- Fix Xsession script being moved in FC5
- Remove sabayon.schema from doc, as it wasn't in this release

* Thu Nov 17 2005 Alexander Larsson <alexl@redhat.com> - 2.12.2-2
- Update to 2.12.2

* Fri Nov  4 2005 Alexander Larsson <alexl@redhat.com> - 2.12.1-1
- Update

* Sun Oct 16 2005 Daniel Veillard <veillard@redhat.com> - 2.12.0-1
- update to 2.12.0 release

* Mon May 23 2005 Mark McLoughlin <markmc@redhat.com> - 2.11.90-1
- Update to 2.11.90
- Don't ghost .pyo files, package them
- We're no longer a noarch package
- BuildRequire python-devel, pygtk2-devel, gtk2-devel and xorg-x11-devel
  for the xlib module
- Add sessionwindow.py, sessionwidget.py, changeswindow.py and
  xlib.so to files
- Remove sabayon-monitor and monitorwindow.py
- Icon is now installed in the icon theme; update the
  icon cache in post and postun
- Require pygtk 2.7.1 in FC5 for MessageDialog fix (gnome #311226)

* Wed May 18 2005 Mark McLoughlin <markmc@redhat.com> - 0.18-1
- Update to 0.18

* Fri Apr  1 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 0.17-2
- Add missing dir entries.

* Thu Mar 24 2005 Mark McLoughlin <markmc@redhat.com> - 0.17-1
- Update to 0.17
- Pass --with-prototype-user=sabayon-admin to configure

* Mon Mar 21 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-8
- Add BuildRequires: usermode and pass --enable-consolehelper=yes
  to configure

* Mon Mar 21 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-7
- Move Xnest and shadow-utils requires to sabayon-admin
- Require libxml2-python

* Mon Mar 21 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-6
- Make noarch

* Mon Mar 21 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-5
- Add dirmonitor.py to base package

* Sun Mar 20 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-4
- Split the package into sabayon and sabayon-admin
- BuildRequires: gettext instead of gettext-devel

* Sat Mar 19 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-3
- Remove period at the end of the summary
- Specify full URL for source
- BuildRequires: python 
- Use _sysconfdir everywhere
- Set the directory mode

* Fri Mar 18 2005 Mark McLoughlin <markmc@redhat.com> - 0.16-2
- BuildRequires: gettext-devel
- Add X-Fedora-Extra to .desktop file

* Wed Mar 16 2005 Mark McLoughlin <markmc@redhat.com>
- Various changes to bring in line with Fedora package guidelines

* Wed Feb  9 2005 Daniel Veillard <veillard@redhat.com>
- initial version
