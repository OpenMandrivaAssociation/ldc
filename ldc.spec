%bcond_without	bootstrap

Summary: LDC - the LLVM based D Compiler
Name:		ldc
Version:	1.36.0
Release:	3
License:	BSD-3-clause and GPL and LLVM and Boost
Group:		Development/Tools
URL:		https://github.com/ldc/ldc
Source0:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/ldc-%{version}-src.tar.gz
# Unfortunately all D compilers currently in existence require a
# D compiler to build -- so we have to start with downloading a
# prebuilt binary.
Source1:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/ldc2-%{version}-linux-x86_64.tar.xz
Source2:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/ldc2-%{version}-linux-aarch64.tar.xz
BuildRequires:	cmake ninja
BuildRequires:	cmake(LLVM)
%if %{without bootstrap}
BuildRequires:	ldc
%endif
BuildRequires:	llvm-static-devel
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(bash-completion)

Requires:	%{mklibname druntime-ldc-debug-shared} = %{EVRD}
Requires:	%{mklibname druntime-ldc-shared} = %{EVRD}
Requires:	%{mklibname phobos2-ldc-debug-shared} = %{EVRD}
Requires:	%{mklibname phobos2-ldc-shared} = %{EVRD}

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
%autosetup -p1 -n %{name}-%{version}-src

%build
# Unpack and initialize the bootstrap compiler -- we don't
# use ifarch and friends here so we can crosscompile (the
# interesting machine for selecting the bootstrap compiler
# is the build machine -- not necessarily the target)
%if %{with bootstrap}
case $(uname -m) in
x86_64)
	tar xf %{S:1}
	BOOTSTRAP_LDC="$(pwd)/ldc2-%{version}-$(uname -s |tr A-Z a-z)-x86_64"
	;;
aarch64)
	tar xf %{S:2}
	BOOTSTRAP_LDC="$(pwd)/ldc2-%{version}-$(uname -s |tr A-Z a-z)-aarch64"
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

%ninja_build

%install
%ninja_install -C build

