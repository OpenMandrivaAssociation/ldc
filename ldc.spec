%bcond bootstrap	0

%global api 111

Summary:	LDC - the LLVM based D Compiler
Name:		ldc
Version:	1.41.0
Release:	3
# The DMD frontend in dmd/* GPL version 1 or artistic license
# The files gen/asmstmt.cpp and gen/asm-*.h GPL version 2+ or artistic license
License:	BSD and GPL+ and Boost
Group:		Development/Toolsc-developersc-developers
URL:		https://github.com/ldc/ldc
Source0:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/ldc-%{version}-src.tar.gz
# Unfortunately all D compilers currently in existence require a
# D compiler to build -- so we have to start with downloading a
# prebuilt binary.
Source1:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/ldc2-%{version}-linux-x86_64.tar.xz
Source2:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/ldc2-%{version}-linux-aarch64.tar.xz
Patch0:	ldc-1.41.0-linkage.patch
Patch1:	4950.patch
Patch2:	ldc-1.41.0-llvm-21.1.patch
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

%libpackage druntime-ldc-debug-shared %{api}
%libpackage druntime-ldc-shared %{api}
%libpackage phobos2-ldc-debug-shared %{api}
%libpackage phobos2-ldc-shared %{api}

%description
An LLVM based compiler for the D programming language.

%files
%license LICENSE
%doc README.md
%{_sysconfdir}/ldc2.conf
%{_bindir}/ldc-build-plugin
%{_bindir}/ldc-build-runtime
#{_bindir}/ldc-profdata
#{_bindir}/ldc-profgen
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
#{_libdir}/libldc-jit-rt.a
#{_libdir}/libldc-jit.so
#{_libdir}/libldc-jit.so.*
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

