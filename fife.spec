%define soname 0
%define libname %mklibname %{name} %{soname}
%define develname %mklibname -d %{name}
%define staticname %mklibname -d -s %{name}
# fife.ppc: W: devel-file-in-non-devel-package /usr/lib/libfife.so <- just a symlink, shouldn't be in -devel. It's used by the client(s).
%global minor_version r2

Name:		fife
Version:	0.3.2
Release:	%mkrel 1
Summary:	Cross platform game creation framework
Group:		System/Libraries
License:	LGPLv2+
URL:		http://www.fifengine.de
# https://sourceforge.net/projects/fife/files/active/src/fife-0.3.2.tar.gz/download
# removed ext/   -  removed for using system libs instead of shipped
# removed tests/   -  removed for legal issues
# removed tools/   -  removed for legal issues
Source0:	%{name}-%{version}%{?minor_version}.tar.gz
Patch0:		%{name}-0.3.2-soname.patch
# Fix the VFSDirectory code to work with known versions of boost
# SVN 3592
Patch2:		%{name}-0.3.2r2-svn3592-boost-fix.patch
# This should probably be fixed in swig.
Patch3:		%{name}-0.3.2r2-gcc46.patch
BuildRequires:	scons
BuildRequires:	SDL-devel
BuildRequires:	boost-devel
BuildRequires:	SDL_ttf-devel
BuildRequires:	SDL_image-devel
BuildRequires:	libvorbis-devel
BuildRequires:	openal-devel
BuildRequires:	swig
BuildRequires:	python-devel
BuildRequires:	zlib-devel
BuildRequires:	mesaglu-devel
BuildRequires:	guichan-devel
BuildRequires:	libpng-devel
BuildRequires:	graphviz
BuildRequires:	libxcursor-devel
BuildRequires:	chrpath
Provides:	%{name}-python = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}

%description
This package of Fife comes with game-engine only.
Unknown horizons is one of the clients that will use this engine.

%package -n %{libname}
Summary:	Shared libs for %{name}
Group:		System/Libraries
Requires:	%{name} = %{version}-%{release}

%description -n %{libname}
Shared libs for %{name}.

%package -n %develname
Summary:	Development package for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{name}-devel < %{version}-%{release}

%description -n %{develname}
Files for development with %{name}.

%package -n %{staticname}
Summary:	Static library for %{name} development
Group:		Development/C
Requires:	%{develname} = %{version}-%{release}
Provides:	%{name}-static-devel = %{version}-%{release}
Obsoletes:	%{name}-static < %{version}-%{release}

%description -n %{staticname}
The %{name}-static package includes static library needed to develop programs
that use the %{name} library.

%package doc
Summary:	Documentation for %{name}
Group:		Development/Other
BuildRequires:	doxygen
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}

%description doc
Doxygen generated documentation for %{name}. 

%prep
%setup -q -n %{name}-%{version}%{?minor_version}

# remove usage of ./ext/ (see line 16 for further informations)
# very dirrty, but it works
sed -i '21d' \
    build/linux2-config.py

# use libdir instead of lib (for 64bit systems)
for l in ./engine/SConscript ./build/linux2-config.py
do
 sed -i "s|'lib'|'%{_lib}'|g" $l
done 

# be utf-8 clean, dudes!
for f in ./AUTHORS ./CHANGES ./COPYING ./README
do
 iconv -f iso-8859-1 -t utf-8 $f |sed 's|\r||g' > $f.utf8
 touch -c -r $f $f.utf8
 mv $f.utf8 $f
done 

# correction of leaf
sed -i 's|i->leaf()|i->path().leaf()|g' \
    engine/core/vfs/vfsdirectory.cpp

# no soname? You can not be serious!
%patch0 -p1
sed -i "s|SONAME|%{soname}|g" \
    engine/SConscript

# Fix boost compile
%patch2 -p1

# Fix swig generated file to work with gcc 4.6
%patch3 -p1

%build
scons . \
      CXXFLAGS='%{optflags}' \
      --enable-debug \
      --enable-rend-grid \
      --enable-rend-camzone \
              fife-shared fife-static fife-python fife-swig

# Doxygen generated docs
doxygen ./doc/doxygen/doxyfile
rm -f ./doc/doxygen/html/installdox


%install
rm -rf %{buildroot}

scons . \
      CXXFLAGS='%{optflags}' \
      --enable-debug \
              install-all \
              install-dev \
                     DESTDIR=%{buildroot} \
                            --prefix=%{_prefix} \
                            --python-prefix=%{python_sitearch}

# rpath is evil, evil, evil
chrpath --delete %{buildroot}%{_libdir}/lib%{name}.so
chrpath --delete %{buildroot}%{python_sitearch}/%{name}/_%{name}.so

# playing a little bit with soname
mv %{buildroot}/%{_libdir}/lib%{name}.so %{buildroot}/%{_libdir}/lib%{name}.so.%{version}
pushd %{buildroot}%{_libdir}
ln -s lib%{name}.so.%{version} lib%{name}.so.%{soname}
ln -s lib%{name}.so.%{version} lib%{name}.so
popd

mkdir -p %{buildroot}/%{_bindir}/
cat > %{buildroot}/%{_bindir}/%{name}-documentation << EOF
#!/bin/sh
xdg-open file://%{_docdir}/%{name}-doc-%{version}/index.html
EOF
chmod +x %{buildroot}/%{_bindir}/%{name}-documentation

# fife.ppc: E: non-standard-executable-perm /usr/lib/libfife.so.0 0775
chmod 755 %{buildroot}/%{_libdir}/lib%{name}.so.%{soname}
# fife.ppc: E: non-standard-executable-perm /usr/lib/python2.6/site-packages/fife/_fife.so 0775
chmod 755 %{buildroot}/%{python_sitearch}/%{name}/_%{name}.so

%files
%defattr(-,root,root,-)
%doc AUTHORS CHANGES COPYING README
%{python_sitearch}/%{name}

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{soname}
%{_libdir}/lib%{name}.so.%{version}

%files -n %{develname}
%defattr(-,root,root,-)
%{_libdir}/lib%{name}.so
%{_includedir}/%{name}/

%files -n %{staticname}
%defattr(-,root,root,-)
%{_libdir}/lib%{name}.a

%files doc
%defattr(-,root,root,-)
%doc ./doc/doxygen/html/*
%{_bindir}/%{name}-documentation

