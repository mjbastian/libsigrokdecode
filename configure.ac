##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2010 Bert Vermeulen <bert@biot.com>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

# We require at least autoconf 2.63 (AC_INIT format changed there).
AC_PREREQ([2.63])

# libsigrokdecode package version number (NOT the same as shared lib version!).
m4_define([srd_package_version_major], [0])
m4_define([srd_package_version_minor], [2])
m4_define([srd_package_version_micro], [0])
m4_define([srd_package_version], [srd_package_version_major.srd_package_version_minor.srd_package_version_micro])

AC_INIT([libsigrokdecode], [srd_package_version],
	[sigrok-devel@lists.sourceforge.net], [libsigrokdecode],
	[http://www.sigrok.org])
AC_CONFIG_HEADER([config.h])
AC_CONFIG_MACRO_DIR([autostuff])
AC_CONFIG_AUX_DIR([autostuff])

# We require at least automake 1.11 (needed for 'silent rules').
AM_INIT_AUTOMAKE([1.11 -Wall -Werror check-news color-tests])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])
m4_ifdef([AM_PROG_AR], [AM_PROG_AR])

AH_TOP([#ifndef SRD_CONFIG_H
#define SRD_CONFIG_H    /* To stop multiple inclusions. */])
AH_BOTTOM([#endif /* SRD_CONFIG_H */])

# Enable more compiler warnings via -Wall and -Wextra. Add -fvisibility=hidden
# and enforce use of SRD_API to explicitly mark all public API functions.
CFLAGS="$CFLAGS -Wall -Wextra -Wmissing-prototypes -fvisibility=hidden"

# Checks for programs.
AC_PROG_CC
AC_PROG_CPP
AC_PROG_INSTALL
AC_PROG_LN_S

# Required for per-target flags or subdir-objects with C sources.
AM_PROG_CC_C_O

# Initialize libtool.
LT_INIT

# Initialize pkg-config.
# We require at least 0.22, as "Requires.private" behaviour changed there.
PKG_PROG_PKG_CONFIG([0.22])

# Library version for libsigrokdecode (NOT the same as the package version).
# Carefully read the libtool docs before updating these numbers!
# The algorithm for determining which number to change (and how) is nontrivial!
# http://www.gnu.org/software/libtool/manual/libtool.html#Updating-version-info
SRD_LIB_VERSION_CURRENT=1
SRD_LIB_VERSION_REVISION=0
SRD_LIB_VERSION_AGE=0
SRD_LIB_VERSION="$SRD_LIB_VERSION_CURRENT:$SRD_LIB_VERSION_REVISION:$SRD_LIB_VERSION_AGE"
SRD_LIB_LDFLAGS="-version-info $SRD_LIB_VERSION"
AC_SUBST(SRD_LIB_VERSION_CURRENT)
AC_SUBST(SRD_LIB_VERSION_REVISION)
AC_SUBST(SRD_LIB_VERSION_AGE)
AC_SUBST(SRD_LIB_VERSION)
AC_SUBST(SRD_LIB_LDFLAGS)

# assume we can build tests/runtc unless proven otherwise
build_runtc="yes"

# Checks for libraries.

# libglib-2.0 is always needed.
# Note: glib-2.0 is part of the libsigrokdecode API
# (hard pkg-config requirement).
AM_PATH_GLIB_2_0([2.24.0],
        [CFLAGS="$CFLAGS $GLIB_CFLAGS"; LIBS="$LIBS $GLIB_LIBS"])

# Python 3 is always needed.
# Note: We need to try a few different variants, since some systems have a
# python3.pc file, others have a python-3.3.pc file, and so on.
# See also: http://sigrok.org/wiki/Libsigrokdecode/Python
CPPFLAGS_PYTHON=""
LDFLAGS_PYTHON=""
PKG_CHECK_MODULES([python3], [python3 >= 3.0],
	[CPPFLAGS_PYTHON="$CPPFLAGS_PYTHON $python3_CFLAGS";
	LDFLAGS_PYTHON="$LDFLAGS_PYTHON $python3_LIBS"],
[PKG_CHECK_MODULES([python33], [python-3.3 >= 3.0],
	[CPPFLAGS_PYTHON="$CPPFLAGS_PYTHON $python33_CFLAGS";
	LDFLAGS_PYTHON="$LDFLAGS_PYTHON $python33_LIBS"],
[PKG_CHECK_MODULES([python32], [python-3.2 >= 3.0],
	[CPPFLAGS_PYTHON="$CPPFLAGS_PYTHON $python32_CFLAGS";
	LDFLAGS_PYTHON="$LDFLAGS_PYTHON $python32_LIBS"],
[PKG_CHECK_MODULES([python31], [python-3.1 >= 3.0],
	[CPPFLAGS_PYTHON="$CPPFLAGS_PYTHON $python31_CFLAGS";
	LDFLAGS_PYTHON="$LDFLAGS_PYTHON $python31_LIBS"],
[PKG_CHECK_MODULES([python30], [python-3.0 >= 3.0],
	[CPPFLAGS_PYTHON="$CPPFLAGS_PYTHON $python30_CFLAGS";
	LDFLAGS_PYTHON="$LDFLAGS_PYTHON $python30_LIBS"],
)])])])])
AC_SUBST(CPPFLAGS_PYTHON)
AC_SUBST(LDFLAGS_PYTHON)

# Link against libm, this is required (among other things) by Python.
AC_SEARCH_LIBS([pow], [m])

# The Check unit testing framework is optional. Disable if not found.
PKG_CHECK_MODULES([check], [check >= 0.9.4],
	[have_check="yes"; CFLAGS="$CFLAGS $check_CFLAGS";
	LIBS="$LIBS $check_LIBS"], [have_check="no"])
AM_CONDITIONAL(HAVE_CHECK, test x"$have_check" = "xyes")

# libsigrok is optional (only used for the protocol decoder test framework).
# Disable if not found.
PKG_CHECK_MODULES([libsigrok], [libsigrok >= 0.2.0],
	[LIBSIGROK_CFLAGS="$libsigrok_CFLAGS"; LIBSIGROK_LIBS="$libsigrok_LIBS"],
	[build_runtc="no"])
AC_SUBST([LIBSIGROK_CFLAGS])
AC_SUBST([LIBSIGROK_LIBS])

# Checks for header files.
# These are already checked: inttypes.h stdint.h stdlib.h string.h unistd.h.
AC_CHECK_HEADER([sys/resource.h], [], [build_runtc="no"])

AC_SUBST(DECODERS_DIR, "$datadir/libsigrokdecode/decoders")
AC_SUBST(MAKEFLAGS, '--no-print-directory')
AC_SUBST(AM_LIBTOOLFLAGS, '--silent')

SRD_PACKAGE_VERSION_MAJOR=srd_package_version_major
SRD_PACKAGE_VERSION_MINOR=srd_package_version_minor
SRD_PACKAGE_VERSION_MICRO=srd_package_version_micro
SRD_PACKAGE_VERSION=srd_package_version

AC_SUBST(SRD_PACKAGE_VERSION_MAJOR)
AC_SUBST(SRD_PACKAGE_VERSION_MINOR)
AC_SUBST(SRD_PACKAGE_VERSION_MICRO)
AC_SUBST(SRD_PACKAGE_VERSION)

AM_CONDITIONAL(BUILD_RUNTC, test x"$build_runtc" = "xyes")

AC_CONFIG_FILES([Makefile
		 version.h
		 libsigrokdecode.pc
		 contrib/Makefile
		 tests/Makefile
		])

AC_OUTPUT

echo
echo "libsigrokdecode configuration summary:"
echo
echo "  - Package version (major.minor.micro):    $SRD_PACKAGE_VERSION"
echo "  - Library version (current:revision:age): $SRD_LIB_VERSION"
echo "  - Prefix: $prefix"
echo "  - Building on: $build"
echo "  - Building for: $host"
echo "  - Building protocol decoder test framework: $build_runtc"
echo
echo "Detected libraries:"
echo

# Note: This only works for libs with pkg-config integration.
for lib in "glib-2.0 >= 2.24.0" "check >= 0.9.4" "libsigrok >= 0.2.0"; do
        if `$PKG_CONFIG --exists $lib`; then
                ver=`$PKG_CONFIG --modversion $lib`
                answer="yes ($ver)"
        else
                answer="no"
        fi
        echo "  - $lib: $answer"
done

echo
echo "Detected Python:"
echo
echo "  - Python CPPFLAGS: $CPPFLAGS_PYTHON"
echo "  - Python LDFLAGS: $LDFLAGS_PYTHON"
echo

