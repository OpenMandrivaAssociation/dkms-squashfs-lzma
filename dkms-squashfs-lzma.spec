%define bmodule squashfs
%define module %{bmodule}-lzma
%define name dkms-%{module}
%define version 3.3
%define kver 2.6.24
%define release %mkrel 2

Summary: Squashfs compressed read-only filesystem (using LZMA)
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{bmodule}%{version}.tgz
Source1: http://www.squashfs-lzma.org/dl/sqlzma%{version}.tar.bz2
Patch0: squashfs3.3-2618.patch
# http://sourceforge.net/tracker/index.php?func=detail&aid=1912192&group_id=63835&atid=505341
Patch1: squashfs3.3-2625.patch
License: GPL
Group: System/Kernel and hardware
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Url: http://squashfs.sourceforge.net/
BuildArch: noarch
Requires(post): dkms
Requires(preun): dkms

%description
Squashfs is a compressed read-only filesystem.
This module is build with support for the LZMA compression algorithm.

%prep
%setup -q -n %{bmodule}%{version} -a 1
mkdir -p dkms
pushd dkms
patch -t < ../kernel-patches/linux-%{kver}/%{bmodule}%{version}-patch || [ -f %{bmodule}.h ]
patch -t < ../sqlzma2k-%{version}.patch
cp ../sqmagic.h ../sqlzma.h .
perl -pi -e 's,^#include <linux/(%{bmodule}.*\.h)>$,#include "$1",' *.{c,h}
popd
%patch0 -p1 -b .2618
%patch1 -p1 -b .2625

cat > dkms/dkms.conf <<EOF
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{version}-%{release}
DEST_MODULE_LOCATION[0]="/kernel/fs/%{bmodule}"
DEST_MODULE_NAME[0]="%{module}"
BUILT_MODULE_NAME[0]="%{bmodule}"
AUTOINSTALL=yes
EOF

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/src/%{module}-%{version}-%{release}/
tar c -C dkms . | tar x -C %{buildroot}/usr/src/%{module}-%{version}-%{release}/

%clean
rm -rf %{buildroot}

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{module} -v %{version}-%{release}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{module} -v %{version}-%{release}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{module} -v %{version}-%{release}
:

%preun
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{module} -v %{version}-%{release} --all
:

%files
%defattr(-,root,root)
/usr/src/%{module}-%{version}-%{release}
