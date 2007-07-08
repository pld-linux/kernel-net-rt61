# XXX: move firmware to /lib/firmware?
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	verbose		# verbose build (V=1)

%define		_beta	b2
%define		_rel	1.%{_beta}.1
Summary:	Ralink RT61 802.11abg WLAN Driver
Summary(pl.UTF-8):	Sterownik WLAN 802.11abg dla urządzeń Ralink RT61
Name:		kernel%{_alt_kernel}-net-rt61
Version:	1.1.0
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://rt2x00.serialmonkey.com/rt61-%{version}-%{_beta}.tar.gz
# Source0-md5:	91d2b6ff31751c3280f32822a3978bed
URL:		http://rt2x00.serialmonkey.com/
# NOTE: might also work with 2.4
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif
Requires:	%{name}-firmware
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	modules	rt61

%description
Ralink RT61 802.11abg WLAN Driver.

%description -l pl.UTF-8
Sterownik WLAN 802.11abg dla urządzeń Ralink RT61.

%package firmware
Summary:	Firmware for Ralink RT61 802.11abg WLAN cards
Summary(pl.UTF-8):	Firmware dla kart WLAN 802.11abg Ralink RT61
Release:	%{_rel}
Group:		Base/Kernel

%description firmware
Firmware for Ralink RT61 802.11abg WLAN cards: rt2561.bin,
rt2561s.bin, rt2661.bin.

%description firmware -l pl.UTF-8
Firmware dla kart WLAN 802.11abg Ralink RT61: rt2561.bin, rt2561s.bin,
rt2661.bin.

%prep
%setup -q -n rt61-%{version}-%{_beta}

%build
cd Module
%build_kernel_modules -m %{modules}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/Wireless/RT61STA
install Module/*.bin Module/rt61sta.dat $RPM_BUILD_ROOT%{_sysconfdir}/Wireless/RT61STA

cd Module
%install_kernel_modules -m %{modules} -d kernel/drivers/net/wireless

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-rt61
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-rt61
%depmod %{_kernel_ver}

%files -n kernel%{_alt_kernel}-net-rt61
%defattr(644,root,root,755)
%doc CHANGELOG FAQ TESTING THANKS Module/README Module/*.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*

%files firmware
%defattr(644,root,root,755)
%dir %{_sysconfdir}/Wireless
%dir %{_sysconfdir}/Wireless/RT61STA
%{_sysconfdir}/Wireless/RT61STA/*.bin
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/Wireless/RT61STA/*.dat
