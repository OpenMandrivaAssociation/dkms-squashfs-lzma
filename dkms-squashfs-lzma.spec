%define bmodule squashfs
%define module %{bmodule}-lzma
%define name dkms-%{module}
%define version 3.3
%define extraver -457-2
%define kver 2.6.24
%define release %mkrel 8

Summary: Squashfs compressed read-only filesystem (using LZMA)
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{bmodule}%{version}.tgz
Source1: http://www.squashfs-lzma.org/dl/sqlzma%{version}%{extraver}.tar.bz2
Patch0: squashfs3.3-2618.patch
# http://sourceforge.net/tracker/index.php?func=detail&aid=1912192&group_id=63835&atid=505341
Patch1: squashfs3.3-2625.patch
# http://sourceforge.net/mailarchive/forum.php?thread_name=Pine.LNX.4.64.0805291610580.3218%40vixen.sonytel.be&forum_name=squashfs-devel
Patch2: squashfs3.3-f_pos.patch
# http://squashfs.cvs.sourceforge.net/squashfs/squashfs/kernel/fs/squashfs/inode.c?r1=1.61&r2=1.61.4.1&view=patch&sortby=date&pathrev=devel-3_4
Patch3: squashfs3.3-2627.patch
# http://kerneltrap.org/index.php?q=mailarchive/linux-kernel/2008/11/17/4175304/thread
Patch4: squashfs-d_alloc_anon-removal.patch
License: GPL
Group: System/Kernel and hardware
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Url: http://squashfs.sourceforge.net/
BuildArch: noarch
Requires(post): dkms
Requires(preun): dkms
Requires(post): dkms-lzma

%description
Squashfs is a compressed read-only filesystem.
This module is build with support for the LZMA compression algorithm.

%package -n %{module}-kernel
Summary:	Virtual package requiring squashfs-lzma modules
Group:		System/Kernel and hardware
Requires:	kmod(squashfs-lzma)
Requires:	kmod(unlzma)

%description -n %{module}-kernel
This virtual package requires the squashfs-lzma modules and their
dependencies.

%prep
%setup -q -n %{bmodule}%{version} -a 1
mkdir -p dkms
pushd dkms
patch -t < ../kernel-patches/linux-%{kver}/%{bmodule}%{version}-patch || [ -f %{bmodule}.h ]
patch -t < ../sqlzma2k-%{version}.patch
perl -pi -e 's,^#include <linux/(%{bmodule}.*\.h)>$,#include "$1",' *.{c,h}
popd
%patch0 -p1 -b .2618
%patch1 -p1 -b .2625
%patch2 -p1 -b .f_pos
%patch3 -p1 -b .2627
%patch4 -p1 -b .d_anon

cp sqmagic.h dkms/

cat > dkms/build.sh <<EOF
cp -a /usr/src/lzma-*/ lzma
cd lzma
make -C "\$1" M=\`pwd\`
cd ..
cp lzma/sqlzma.h lzma/Module.symvers .
make -C "\$1" M=\`pwd\`
EOF
chmod +x dkms/build.sh

cat > dkms/dkms.conf <<EOF
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{version}-%{release}
MAKE[0]="./build.sh \$kernel_source_dir"
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

%files -n %{module}-kernel
