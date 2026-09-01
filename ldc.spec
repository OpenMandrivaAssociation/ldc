%bcond bootstrap	1

%global api 113

Summary:	LDC - the LLVM based D Compiler
Name:		ldc
Version:	1.43.0
%define realver %(echo %{version} | tr '_' '-')
Release:	1
# The DMD frontend in dmd/* GPL version 1 or artistic license
# The files gen/asmstmt.cpp and gen/asm-*.h GPL version 2+ or artistic license
License:	BSD and GPL+ and Boost
Group:		Development/Tools
URL:		https://github.com/ldc-developers/ldc
Source0:	https://github.com/ldc-developers/ldc/releases/download/v%{realver}/ldc-%{realver}-src.tar.gz
# Unfortunately all D compilers currently in existence require a
# D compiler to build -- so we have to start with downloading a
# prebuilt binary.
Source1:	https://github.com/ldc-developers/ldc/releases/download/v%{realver}/ldc2-%{realver}-linux-x86_64.tar.xz
Source2:	https://github.com/ldc-developers/ldc/releases/download/v%{realver}/ldc2-%{realver}-linux-aarch64.tar.xz
BuildRequires:	cmake ninja
BuildRequires:	cmake(LLVM)
%if %{without bootstrap}
BuildRequires:	ldc
%endif
BuildRequires:	llvm-static-devel
BuildRequires:	pkgconfig(libzstd)

Requires:	%{mklibname druntime-ldc-debug-shared} = %{EVRD}
Requires:	%{mklibname druntime-ldc-shared} = %{EVRD}
Requires:	%{mklibname phobos2-ldc-debug-shared} = %{EVRD}
Requires:	%{mklibname phobos2-ldc-shared} = %{EVRD}
# ldc-profdata / ldc-profgen are the system LLVM tools; 1.43 has no LLVM 23 copies
Requires:	llvm

%libpackage druntime-ldc-debug-shared %{api}
%libpackage druntime-ldc-shared %{api}
%libpackage phobos2-ldc-debug-shared %{api}
%libpackage phobos2-ldc-shared %{api}

%description
An LLVM based compiler for the D programming language.

%files
%license LICENSE
%doc README.md
%dir %{_sysconfdir}/ldc2.conf
%config(noreplace) %{_sysconfdir}/ldc2.conf/*
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
%autosetup -p1 -n ldc-%{realver}-src

%build
# Unpack and initialize the bootstrap compiler -- we don't
# use ifarch and friends here so we can crosscompile (the
# interesting machine for selecting the bootstrap compiler
# is the build machine -- not necessarily the target)
%if %{with bootstrap}
case $(uname -m) in
x86_64)
	tar xf %{S:1}
	BOOTSTRAP_LDC="$(pwd)/ldc2-%{realver}-$(uname -s |tr A-Z a-z)-x86_64"
	;;
aarch64)
	tar xf %{S:2}
	BOOTSTRAP_LDC="$(pwd)/ldc2-%{realver}-$(uname -s |tr A-Z a-z)-aarch64"
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
	-DLDC_BUNDLE_LLVM_TOOLS:BOOL=OFF \
	-DBASH_COMPLETION_COMPLETIONSDIR=%{_datadir}/bash-completion/completions \
	-DLLVM_CONFIG:PATH=llvm-config \
%if %{with bootstrap}
	-DD_COMPILER=${BOOTSTRAP_LDC}/bin/ldmd2 \
%endif
	-G Ninja

%ninja_build

%install
%ninja_install -C build
# 1.43 has no LLVM 23 copies of these tools; use the system LLVM ones
ln -s llvm-profdata %{buildroot}%{_bindir}/ldc-profdata
ln -s llvm-profgen %{buildroot}%{_bindir}/ldc-profgen
