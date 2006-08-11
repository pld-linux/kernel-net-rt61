# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)

%define		_snap	2006081110
%define		_rel	1.%{_snap}.1
Summary:	Ralink RT61 802.11abg WLAN Driver
#Summary(pl):	-
Name:		kernel-net-rt61
Version:	1.1.0
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://rt2x00.serialmonkey.com/rt61-cvs-daily.tar.gz
# Source0-md5:	8c48c6c4f384a695c75528e32822382d
URL:		http://rt2x00.serialmonkey.com/
# NOTE: might also work with 2.4
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.308
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif
Requires:	%{name}-firmware
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ralink RT61 802.11abg WLAN Driver.

#%description -l pl

%package -n kernel-smp-net-rt61
Summary:	Ralink RT61 802.11abg WLAN Driver (SMP)
#Summary(pl):	
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif
Requires:	%{name}-firmware

%description -n kernel-smp-net-rt61
Ralink RT61 802.11abg WLAN Driver (SMP).

#%description -n kernel-smp-net-rt61 -l pl

%package firmware
Summary:	Firmware for Ralink RT61 802.11abg WLAN cards
Release:	%{_rel}
Group:		Base/Kernel
# XXX: make a circular dependency?

%description firmware
Firmware for Ralink RT61 802.11abg WLAN cards: rt2561.bin, rt2561s.bin, rt2661.bin.

%prep
%setup -q -n rt61-cvs-%{_snap}

%build
cd Module
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv rt61{,-$cfg}.ko
done

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/Wireless/RT61STA
install Module/*.bin Module/rt61sta.dat $RPM_BUILD_ROOT%{_sysconfdir}/Wireless/RT61STA

install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/drivers/net/wireless
install Module/rt61-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/drivers/net/wireless/rt61.ko
%if %{with smp} && %{with dist_kernel}
install Module/rt61-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/drivers/net/wireless/rt61.ko
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-rt61
%depmod %{_kernel_ver}

%postun	-n kernel-net-rt61
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-rt61
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-net-rt61
%depmod %{_kernel_ver}smp

%files -n kernel-net-rt61
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/drivers/net/wireless/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-rt61
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/drivers/net/wireless/*.ko*
%endif

%files firmware
%defattr(644,root,root,755)
%dir %{_sysconfdir}/Wireless
%dir %{_sysconfdir}/Wireless/RT61STA
%{_sysconfdir}/Wireless/RT61STA/*.bin
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/Wireless/RT61STA/*.dat
