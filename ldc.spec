# FIXME This is needed because the bootstrap compiler
# is built against LLVM 15 and therefore can't read
# LLVM 16 bitcode files.
# We can enable LTO once we switch to an LLVM 16
# enabled bootstrap compiler.
#define _disable_lto 1

%bcond_with	bootstrap

%define beta beta1
%define snapshot 20231204
%define commit f4b15f2550fff7a252fab239f0fca03fd49ac582

Name: ldc
Version: 1.36.0
Release: %{?beta:0.%{beta}.}2
Source0: https://github.com/ldc-developers/ldc/releases/download/v%{version}%{?beta:-%{beta}}/ldc-%{version}%{?beta:-%{beta}}-src.tar.gz
#Source0: https://github.com/ldc-developers/ldc/archive/%{?snapshot:master}%{!?snapshot:v%{version}}/%{name}-%{?snapshot:master}%{!?snapshot:%{version}}-src.tar.gz
#Source0: https://github.com/JohanEngelen/ldc/archive/%{?snapshot:%{commit}}%{!?snapshot:v%{version}}/%{name}-%{?snapshot:%{commit}}%{!?snapshot:%{version}}-src.tar.gz
# Unfortunately all D compilers currently in existence require a
# D compiler to build -- so we have to start with downloading a
# prebuilt binary.
Source1: https://github.com/ldc-developers/ldc/releases/download/v%{version}%{?beta:-%{beta}}/ldc2-%{version}%{?beta:-%{beta}}-linux-x86_64.tar.xz
Source2: https://github.com/ldc-developers/ldc/releases/download/v%{version}%{?beta:-%{beta}}/ldc2-%{version}%{?beta:-%{beta}}-linux-aarch64.tar.xz
# LLVM 16 support
#Patch0: https://github.com/ldc-developers/ldc/pull/4411.patch
# LLVM 17 support
#Patch0:	ldc-1.35.0-port_to_llvm17.patch
# Link -lzstd, needed implicitly by LLVM libs
#Patch1: ldc-1.33-linkage.patch
Summary: LDC - the LLVM based D Compiler
URL: https://github.com/ldc/ldc
License: BSD-3-clause and GPL and LLVM and Boost
Group: Development/Tools
BuildRequires: cmake ninja
BuildRequires: cmake(LLVM)
BuildRequires: llvm-static-devel
BuildRequires: pkgconfig(libzstd)
BuildRequires: pkgconfig(bash-completion)
Requires: %{mklibname druntime-ldc-debug-shared} = %{EVRD}
Requires: %{mklibname druntime-ldc-shared} = %{EVRD}
Requires: %{mklibname phobos2-ldc-debug-shared} = %{EVRD}
Requires: %{mklibname phobos2-ldc-shared} = %{EVRD}

%libpackage druntime-ldc-debug-shared 106
%libpackage druntime-ldc-shared 106
%libpackage phobos2-ldc-debug-shared 106
%libpackage phobos2-ldc-shared 106

%description
An LLVM based compiler for the D programming language.

%files
%{_sysconfdir}/ldc2.conf
%{_bindir}/ldc-build-plugin
%{_bindir}/ldc-build-runtime
%{_bindir}/ldc-profdata
%{_bindir}/ldc-profgen
%{_bindir}/ldc-prune-cache
%{_bindir}/ldc2
%{_bindir}/ldmd2
%{_bindir}/timetrace2txt
%{_includedir}/d
%{_libdir}/ldc_rt.dso.o
%{_libdir}/libdruntime-ldc-debug-shared.so
%{_libdir}/libdruntime-ldc-shared.so
%{_libdir}/libphobos2-ldc-debug-shared.so
%{_libdir}/libphobos2-ldc-shared.so
%{_datadir}/bash-completion/completions/ldc2

#---------------------------------------------------------------------------

%prep
%autosetup -p1 -n %{name}-%{version}%{?beta:-%{beta}}-src
#autosetup -p1 -n %{name}-%{?snapshot:%{commit}}%{!?snapshot:%{version}}


%build
# Unpack and initialize the bootstrap compiler -- we don't
# use ifarch and friends here so we can crosscompile (the
# interesting machine for selecting the bootstrap compiler
# is the build machine -- not necessarily the target)
%if %{with bootstrap}
case $(uname -m) in
x86_64)
	tar xf %{S:1}
	BOOTSTRAP_LDC="$(pwd)/ldc2-%{version}%{?beta:-%{beta}}-$(uname -s |tr A-Z a-z)-x86_64"
	;;
aarch64)
	tar xf %{S:2}
	BOOTSTRAP_LDC="$(pwd)/ldc2-%{version}%{?beta:-%{beta}}-$(uname -s |tr A-Z a-z)-aarch64"
	;;
*)
	if which ldmd2; then
		echo "WARNING: Using system ldmd2 for bootstrapping"
		BOOTSTRAP_LDC=$(which ldmd2)
	else
		echo "There is no bootstrap compiler for this architecture."
		echo "Please crosscompile one."
		exit 1
	fi
	;;
esac
%endif

%cmake -Wno-dev \
	-DBUILD_LTO_LIBS:BOOL=OFF \
	-DLLVM_CONFIG:PATH=llvm-config \
%if %{with bootstrap}
	-DD_COMPILER=${BOOTSTRAP_LDC}/bin/ldmd2 \
%endif
	-G Ninja

#ninja_build -j1
ninja -j1

%install
%ninja_install -C build

