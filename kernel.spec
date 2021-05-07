# All Global changes to build and install go here.
# Per the below section about __spec_install_pre, any rpm
# environment changes that affect %%install need to go
# here before the %%install macro is pre-built.

# Disable LTO in userspace packages.
%global _lto_cflags %{nil}

# Option to enable compiling with clang instead of gcc.
%bcond_with toolchain_clang

%if %{with toolchain_clang}
%global toolchain clang
%endif

# Cross compile on copr for arm
# See https://bugzilla.redhat.com/1879599
%if 0%{?_with_cross_arm:1}
%global _target_cpu armv7hl
%global _arch arm
%global _build_arch arm
%global _with_cross    1
%endif

# The kernel's %%install section is special
# Normally the %%install section starts by cleaning up the BUILD_ROOT
# like so:
#
# %%__spec_install_pre %%{___build_pre}\
#     [ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "${RPM_BUILD_ROOT}"\
#     mkdir -p `dirname "$RPM_BUILD_ROOT"`\
#     mkdir "$RPM_BUILD_ROOT"\
# %%{nil}
#
# But because of kernel variants, the %%build section, specifically
# BuildKernel(), moves each variant to its final destination as the
# variant is built.  This violates the expectation of the %%install
# section.  As a result we snapshot the current env variables and
# purposely leave out the removal section.  All global wide changes
# should be added above this line otherwise the %%install section
# will not see them.
%global __spec_install_pre %{___build_pre}

# At the time of this writing (2019-03), RHEL8 packages use w2.xzdio
# compression for rpms (xz, level 2).
# Kernel has several large (hundreds of mbytes) rpms, they take ~5 mins
# to compress by single-threaded xz. Switch to threaded compression,
# and from level 2 to 3 to keep compressed sizes close to "w2" results.
#
# NB: if default compression in /usr/lib/rpm/redhat/macros ever changes,
# this one might need tweaking (e.g. if default changes to w3.xzdio,
# change below to w4T.xzdio):
#
# This is disabled on i686 as it triggers oom errors

%ifnarch i686
%define _binary_payload w3T.xzdio
%endif

Summary: The Linux kernel

# For a kernel released for public testing, released_kernel should be 1.
# For internal testing builds during development, it should be 0.
# For rawhide and/or a kernel built from an rc or git snapshot,
# released_kernel should be 0.
# For a stable, released kernel, released_kernel should be 1.
%global released_kernel 0

%global distro_build 0.rc0.20210507gita48b0872e694.10

%if 0%{?fedora}
%define secure_boot_arch x86_64
%else
%define secure_boot_arch x86_64 aarch64 s390x ppc64le
%endif

# Signing for secure boot authentication
%ifarch %{secure_boot_arch}
%global signkernel 1
%else
%global signkernel 0
%endif

# Sign modules on all arches
%global signmodules 1

# Compress modules only for architectures that build modules
%ifarch noarch
%global zipmodules 0
%else
%global zipmodules 1
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
# for parallel xz processes, replace with 1 to go back to single process
%global zcpu `nproc --all`
%endif

# define buildid .local


%if 0%{?fedora}
%define primary_target fedora
%else
%define primary_target rhel
%endif

%define rpmversion 5.13.0
%define pkgrelease 0.rc0.20210507gita48b0872e694.10

# This is needed to do merge window version magic
%define patchlevel 13

# allow pkg_release to have configurable %%{?dist} tag
%define specrelease 0.rc0.20210507gita48b0872e694.10%{?buildid}%{?dist}

%define pkg_release %{specrelease}

# What parts do we want to build? These are the kernels that are built IF the
# architecture allows it. All should default to 1 (enabled) and be flipped to
# 0 (disabled) by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel PAE (only valid for ARM (lpae))
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
%define with_cross_headers   %{?_without_cross_headers:   0} %{?!_without_cross_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# bpf tool
%define with_bpftool   %{?_without_bpftool:   0} %{?!_without_bpftool:   1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# Control whether to install the vdso directories.
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# kernel-zfcpdump (s390 specific kernel for zfcpdump)
%define with_zfcpdump  %{?_without_zfcpdump:  0} %{?!_without_zfcpdump:  1}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_without_kernel_abi_whitelists: 0} %{?!_without_kernel_abi_whitelists: 1}
# internal samples and selftests
%define with_selftests %{?_without_selftests: 0} %{?!_without_selftests: 1}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}
# Temporarily disable kabi checks until RC.
%define with_kabichk 0
# Control whether we perform a compat. check against DUP ABI.
%define with_kabidupchk %{?_with_kabidupchk:  1} %{?!_with_kabidupchk:   0}
#
# Control whether to run an extensive DWARF based kABI check.
# Note that this option needs to have baseline setup in SOURCE300.
%define with_kabidwchk %{?_without_kabidwchk: 0} %{?!_without_kabidwchk: 1}
%define with_kabidw_base %{?_with_kabidw_base: 1} %{?!_with_kabidw_base: 0}
#
# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}
#
# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}
#
# build a release kernel on rawhide
%define with_release   %{?_with_release:      1} %{?!_with_release:      0}

# verbose build, i.e. no silent rules and V=1
%define with_verbose %{?_with_verbose:        1} %{?!_with_verbose:      0}

#
# check for mismatched config options
%define with_configchecks %{?_without_configchecks:        0} %{?!_without_configchecks:        1}

#
# gcov support
%define with_gcov %{?_with_gcov:1}%{?!_with_gcov:0}

#
# ipa_clone support
%define with_ipaclones %{?_without_ipaclones: 0} %{?!_without_ipaclones: 1}

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 0

# The kernel tarball/base version
%define kversion 5.13

%if 0%{?fedora}
# Kernel headers are being split out into a separate package
%define with_headers 0
%define with_cross_headers 0
# no selftests for now
%define with_selftests 0
# no ipa_clone for now
%define with_ipaclones 0
# no whitelist
%define with_kernel_abi_whitelists 0
# Fedora builds these separately
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%endif

%if %{with_verbose}
%define make_opts V=1
%else
%define make_opts -s
%endif

%if %{with toolchain_clang}
%global make_opts %{make_opts} HOSTCC=clang CC=clang
# clang does not support the -fdump-ipa-clones option
%global with_ipaclones 0
%endif

# turn off debug kernel and kabichk for gcov builds
%if %{with_gcov}
%define with_debug 0
%define with_kabichk 0
%define with_kabidupchk 0
%define with_kabidwchk 0
%endif

# turn off kABI DWARF-based check if we're generating the base dataset
%if %{with_kabidw_base}
%define with_kabidwchk 0
%endif

# kpatch_kcflags are extra compiler flags applied to base kernel
# -fdump-ipa-clones is enabled only for base kernels on selected arches
%if %{with_ipaclones}
%ifarch x86_64 ppc64le
%define kpatch_kcflags -fdump-ipa-clones
%else
%define with_ipaclones 0
%endif
%endif

%define make_target bzImage
%define image_install_path boot

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define KVERREL_RE %(echo %KVERREL | sed 's/+/[+]/g')
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{with_vanilla}
%define nopatches 1
%endif

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug
# Needed because we override almost everything involving build-ids
# and debuginfo generation. Currently we rely on the old alldebug setting.
%global _build_id_links alldebug

# kernel PAE is only built on ARMv7
%ifnarch armv7hl
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_up 0
%define with_tools 0
%define with_perf 0
%define with_bpftool 0
%endif

# turn off kABI DUP check and DWARF-based check if kABI check is disabled
%if !%{with_kabichk}
%define with_kabidupchk 0
%define with_kabidwchk 0
%endif

%if %{with_vdso_install}
%define use_vdso 1
%endif


%ifnarch noarch
%define with_kernel_abi_whitelists 0
%endif

# Overrides for generic default options

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define doc_build_fail true
%endif

%if 0%{?fedora}
# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_cross_headers 0
%define with_tools 0
%define with_perf 0
%define with_bpftool 0
%define with_selftests 0
%define with_debug 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# sparse blows up on ppc
%ifnarch ppc64le
%define with_sparse 0
%endif

# zfcpdump mechanism is s390 only
%ifnarch s390x
%define with_zfcpdump 0
%endif

%if 0%{?fedora}
# This is not for Fedora
%define with_zfcpdump 0
%endif

# Per-arch tweaks

%ifarch i686
%define asmarch x86
%define hdrarch i386
%define all_arch_configs kernel-%{version}-i?86*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define use_vdso 0
%define all_arch_configs kernel-%{version}-ppc64le*.config
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define kernel_image arch/s390/boot/bzImage
%define vmlinux_decompressor arch/s390/boot/compressed/vmlinux
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define skip_nonpae_vdso 1
%define asmarch arm
%define hdrarch arm
%define make_target bzImage
%define kernel_image arch/arm/boot/zImage
# http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
%define kernel_mflags KALLSYMS_EXTRA_PASS=1
# we only build headers/perf/tools on the base arm arches
# just like we used to only build them on i386 for x86
%ifnarch armv7hl
%define with_headers 0
%define with_cross_headers 0
%endif
# These currently don't compile on armv7
%define with_selftests 0
%endif

%ifarch aarch64
%define all_arch_configs kernel-%{version}-aarch64*.config
%define asmarch arm64
%define hdrarch arm64
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}
%define with_configchecks 0
%endif

# Setting the compiler to clang enables some different config options
# than what is expected, so disable this check for now.
# TODO: What's the best way to fix this?  Do wee need a different set of
# configs for clang?
%if %{with toolchain_clang}
%define with_configchecks 0
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%if 0%{?fedora}
%define nobuildarches i386
%else
%define nobuildarches i386 i686 %{arm}
%endif

%ifarch %nobuildarches
# disable BuildKernel commands
%define with_up 0
%define with_debug 0
%define with_pae 0
%define with_zfcpdump 0

%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_selftests 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%if 0%{?fedora}
%define cpupowerarchs %{ix86} x86_64 ppc64le %{arm} aarch64
%else
%define cpupowerarchs i686 x86_64 ppc64le aarch64
%endif

%if 0%{?use_vdso}

%if 0%{?skip_nonpae_vdso}
%define _use_vdso 0
%else
%define _use_vdso 1
%endif

%else
%define _use_vdso 0
%endif

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  coreutils, systemd >= 203-2, /usr/bin/kernel-install
%define initrd_prereq  dracut >= 027


Name: kernel
License: GPLv2 and Redistributable, no modification permitted
URL: https://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
%if 0%{?fedora}
ExclusiveArch: x86_64 s390x %{arm} aarch64 ppc64le
%else
ExclusiveArch: noarch i386 i686 x86_64 s390x %{arm} aarch64 ppc64le
%endif
ExclusiveOS: Linux
%ifnarch %{nobuildarches}
Requires: kernel-core-uname-r = %{KVERREL}
Requires: kernel-modules-uname-r = %{KVERREL}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, tar, git-core
BuildRequires: bzip2, xz, findutils, gzip, m4, perl-interpreter, perl-Carp, perl-devel, perl-generators, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc, bison, flex, gcc-c++
BuildRequires: net-tools, hostname, bc, elfutils-devel
BuildRequires: dwarves
BuildRequires: python3-devel
BuildRequires: gcc-plugin-devel
%if %{with_headers}
BuildRequires: rsync
%endif
%if %{with_doc}
BuildRequires: xmlto, asciidoc, python3-sphinx, python3-sphinx_rtd_theme
%endif
%if %{with_sparse}
BuildRequires: sparse
%endif
%if %{with_perf}
BuildRequires: zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison flex xz-devel
BuildRequires: audit-libs-devel
BuildRequires: java-devel
%ifnarch %{arm} s390x
BuildRequires: numactl-devel
%endif
%endif
%if %{with_tools}
BuildRequires: gettext ncurses-devel
BuildRequires: libcap-devel libcap-ng-devel
%ifnarch s390x
BuildRequires: pciutils-devel
%endif
%endif
%if %{with_bpftool}
BuildRequires: python3-docutils
BuildRequires: zlib-devel binutils-devel
%endif
%if %{with_selftests}
BuildRequires: clang llvm
%ifnarch %{arm}
BuildRequires: numactl-devel
%endif
BuildRequires: libcap-devel libcap-ng-devel rsync
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
BuildConflicts: rpm < 4.13.0.1-19
BuildConflicts: dwarves < 1.13
# Most of these should be enabled after more investigation
%undefine _include_minidebuginfo
%undefine _find_debuginfo_dwz_opts
%undefine _unique_build_ids
%undefine _unique_debug_names
%undefine _unique_debug_srcs
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%global _find_debuginfo_opts -r
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%endif
%if %{with_kabidwchk} || %{with_kabidw_base}
BuildRequires: kabi-dw
%endif

%if %{signkernel}%{signmodules}
BuildRequires: openssl openssl-devel
%if %{signkernel}
%ifarch x86_64 aarch64
BuildRequires: nss-tools
BuildRequires: pesign >= 0.10-4
%endif
%endif
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%define __strip %{_build_arch}-linux-gnu-strip
%endif

# These below are required to build man pages
%if %{with_perf}
BuildRequires: xmlto
%endif
%if %{with_perf} || %{with_tools}
BuildRequires: asciidoc
%endif

%if %{with toolchain_clang}
BuildRequires: clang
%endif

# Because this is the kernel, it's hard to get a single upstream URL
# to represent the base without needing to do a bunch of patching. This
# tarball is generated from a src-git tree. If you want to see the
# exact git commit you can run
#
# xzcat -qq ${TARBALL} | git get-tar-commit-id
Source0: linux-5.12-14712-ga48b0872e694.tar.xz

Source1: Makefile.rhelver


# Name of the packaged file containing signing key
%ifarch ppc64le
%define signing_key_filename kernel-signing-ppc.cer
%endif
%ifarch s390x
%define signing_key_filename kernel-signing-s390.cer
%endif

Source8: x509.genkey.rhel
Source9: x509.genkey.fedora

%if %{?released_kernel}

Source10: redhatsecurebootca5.cer
Source11: redhatsecurebootca1.cer
Source12: redhatsecureboot501.cer
Source13: redhatsecureboot301.cer
Source14: secureboot_s390.cer
Source15: secureboot_ppc.cer

%define secureboot_ca_1 %{SOURCE10}
%define secureboot_ca_0 %{SOURCE11}
%ifarch x86_64 aarch64
%define secureboot_key_1 %{SOURCE12}
%define pesign_name_1 redhatsecureboot501
%define secureboot_key_0 %{SOURCE13}
%define pesign_name_0 redhatsecureboot301
%endif
%ifarch s390x
%define secureboot_key_0 %{SOURCE14}
%define pesign_name_0 redhatsecureboot302
%endif
%ifarch ppc64le
%define secureboot_key_0 %{SOURCE15}
%define pesign_name_0 redhatsecureboot303
%endif

# released_kernel
%else

Source10: redhatsecurebootca4.cer
Source11: redhatsecurebootca2.cer
Source12: redhatsecureboot401.cer
Source13: redhatsecureboot003.cer

%define secureboot_ca_1 %{SOURCE10}
%define secureboot_ca_0 %{SOURCE11}
%define secureboot_key_1 %{SOURCE12}
%define pesign_name_1 redhatsecureboot401
%define secureboot_key_0 %{SOURCE13}
%define pesign_name_0 redhatsecureboot003

# released_kernel
%endif

Source22: mod-extra.list.rhel
Source16: mod-extra.list.fedora
Source17: mod-blacklist.sh
Source18: mod-sign.sh
Source79: parallel_xz.sh

Source80: filter-x86_64.sh.fedora
Source81: filter-armv7hl.sh.fedora
Source82: filter-i686.sh.fedora
Source83: filter-aarch64.sh.fedora
Source86: filter-ppc64le.sh.fedora
Source87: filter-s390x.sh.fedora
Source89: filter-modules.sh.fedora

Source90: filter-x86_64.sh.rhel
Source91: filter-armv7hl.sh.rhel
Source92: filter-i686.sh.rhel
Source93: filter-aarch64.sh.rhel
Source96: filter-ppc64le.sh.rhel
Source97: filter-s390x.sh.rhel
Source99: filter-modules.sh.rhel
%define modsign_cmd %{SOURCE18}

Source20: kernel-aarch64-rhel.config
Source21: kernel-aarch64-debug-rhel.config
Source30: kernel-ppc64le-rhel.config
Source31: kernel-ppc64le-debug-rhel.config
Source32: kernel-s390x-rhel.config
Source33: kernel-s390x-debug-rhel.config
Source34: kernel-s390x-zfcpdump-rhel.config
Source35: kernel-x86_64-rhel.config
Source36: kernel-x86_64-debug-rhel.config

Source37: kernel-aarch64-fedora.config
Source38: kernel-aarch64-debug-fedora.config
Source39: kernel-armv7hl-fedora.config
Source40: kernel-armv7hl-debug-fedora.config
Source41: kernel-armv7hl-lpae-fedora.config
Source42: kernel-armv7hl-lpae-debug-fedora.config
Source43: kernel-i686-fedora.config
Source44: kernel-i686-debug-fedora.config
Source45: kernel-ppc64le-fedora.config
Source46: kernel-ppc64le-debug-fedora.config
Source47: kernel-s390x-fedora.config
Source48: kernel-s390x-debug-fedora.config
Source49: kernel-x86_64-fedora.config
Source50: kernel-x86_64-debug-fedora.config



Source51: generate_all_configs.sh

Source52: process_configs.sh
Source53: generate_bls_conf.sh
Source56: update_scripts.sh

Source54: mod-internal.list

Source100: rheldup3.x509
Source101: rhelkpatch1.x509

Source200: check-kabi

Source201: Module.kabi_aarch64
Source202: Module.kabi_ppc64le
Source203: Module.kabi_s390x
Source204: Module.kabi_x86_64

Source210: Module.kabi_dup_aarch64
Source211: Module.kabi_dup_ppc64le
Source212: Module.kabi_dup_s390x
Source213: Module.kabi_dup_x86_64

Source300: kernel-abi-whitelists-%{rpmversion}-%{distro_build}.tar.bz2
Source301: kernel-kabi-dw-%{rpmversion}-%{distro_build}.tar.bz2

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

# Some people enjoy building customized kernels from the dist-git in Fedora and
# use this to override configuration options. One day they may all use the
# source tree, but in the mean time we carry this to support the legacy workflow
Source3000: merge.pl
Source3001: kernel-local
Source3003: Patchlist.changelog

Source4000: README.rst

## Patches needed for building this package

%if !%{nopatches}

Patch1: patch-%{rpmversion}-redhat.patch
%endif

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

# END OF PATCH DEFINITIONS

%description
The kernel meta package

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:+%{1}}\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20150904-56.git6ebf5d57\
Requires(preun): systemd >= 200\
Conflicts: xfsprogs < 4.3.0-1\
Conflicts: xorg-x11-drv-vmmouse < 13.0.99\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc
%description cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.


%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Provides: installonlypkg(kernel)
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Requires: bzip2
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|.*%%{_libdir}/traceevent/plugins/.*|.*%%{_libdir}/libperf-jvmti.so(\.debug)?|XXX' -o perf-debuginfo.list}

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events
%description -n python3-perf
The python3-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%package -n python3-perf-debuginfo
Summary: Debug information for package perf python bindings
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python3-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{python3_sitearch}/perf.*so(\.debug)?|XXX' -o python3-perf-debuginfo.list}

# with_perf
%endif

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
License: GPLv2
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%endif
%define __requires_exclude ^%{_bindir}/python
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
%endif
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|.*%%{_bindir}/lsgpio(\.debug)?|.*%%{_bindir}/gpio-hammer(\.debug)?|.*%%{_bindir}/gpio-event-mon(\.debug)?|.*%%{_bindir}/gpio-watch(\.debug)?|.*%%{_bindir}/iio_event_monitor(\.debug)?|.*%%{_bindir}/iio_generic_buffer(\.debug)?|.*%%{_bindir}/lsiio(\.debug)?|.*%%{_bindir}/intel-speed-select(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

# with_tools
%endif

%if %{with_bpftool}

%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps
License: GPLv2
%description -n bpftool
This package contains the bpftool, which allows inspection and simple
manipulation of eBPF programs and maps.

%package -n bpftool-debuginfo
Summary: Debug information for package bpftool
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n bpftool-debuginfo
This package provides debug information for the bpftool package.

%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_sbindir}/bpftool(\.debug)?|XXX' -o bpftool-debuginfo.list}

# with_bpftool
%endif

%if %{with_selftests}

%package selftests-internal
Summary: Kernel samples and selftests
License: GPLv2
Requires: binutils, bpftool, iproute-tc, nmap-ncat
Requires: kernel-modules-internal = %{version}-%{release}
%description selftests-internal
Kernel sample programs and selftests.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_libexecdir}/(ksamples|kselftests)/.*|XXX' -o selftests-debuginfo.list}

# with_selftests
%endif

%if %{with_gcov}
%package gcov
Summary: gcov graph and source files for coverage data collection.
%description gcov
kernel-gcov includes the gcov graph and source files for gcov coverage collection.
%endif

%package -n kernel-abi-whitelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol whitelists
AutoReqProv: no
%description -n kernel-abi-whitelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

%if %{with_kabidw_base}
%package kabidw-base
Summary: The baseline dataset for kABI verification using DWARF data
Group: System Environment/Kernel
AutoReqProv: no
%description kabidw-base
The kabidw-base package contains data describing the current ABI of the Red Hat
Enterprise Linux kernel, suitable for the kabi-dw tool.
%endif

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
# Explanation of the find_debuginfo_opts: We build multiple kernels (debug
# pae etc.) so the regex filters those kernels appropriately. We also
# have to package several binaries as part of kernel-devel but getting
# unique build-ids is tricky for these userspace binaries. We don't really
# care about debugging those so we just filter those out and remove it.
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
%description %{?1:%{1}-}debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*\/usr\/src\/kernels/.*|XXX' -o ignored-debuginfo.list -p '/.*/%%{KVERREL_RE}%{?1:[+]%{1}}/.*|/.*%%{KVERREL_RE}%{?1:\+%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl-interpreter\
Requires: openssl-devel\
Requires: elfutils-libelf-devel\
Requires: bison\
Requires: flex\
Requires: make\
Requires: gcc\
%description %{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# kernel-<variant>-ipaclones-internal package
#
%define kernel_ipaclones_package() \
%package %{?1:%{1}-}ipaclones-internal\
Summary: *.ipa-clones files generated by -fdump-ipa-clones for kernel%{?1:-%{1}}\
Group: System Environment/Kernel\
AutoReqProv: no\
%description %{?1:%{1}-}ipaclones-internal\
This package provides *.ipa-clones files.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-internal package.
#	%%kernel_modules_internal_package <subpackage> <pretty-name>
#
%define kernel_modules_internal_package() \
%package %{?1:%{1}-}modules-internal\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-internal-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-internal-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-internal = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-internal-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-internal\
This package provides kernel modules for the %{?2:%{2} }kernel package for Red Hat internal usage.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-extra package.
#	%%kernel_modules_extra_package <subpackage> <pretty-name>
#
%define kernel_modules_extra_package() \
%package %{?1:%{1}-}modules-extra\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules package.
#	%%kernel_modules_package <subpackage> <pretty-name>
#
%define kernel_modules_package() \
%package %{?1:%{1}-}modules\
Summary: kernel modules to match the %{?2:%{2}-}core kernel\
Provides: kernel%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules\
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.\
%{nil}

#
# this macro creates a kernel-<subpackage> meta package.
#	%%kernel_meta_package <subpackage>
#
%define kernel_meta_package() \
%package %{1}\
summary: kernel meta-package for the %{1} kernel\
Requires: kernel-%{1}-core-uname-r = %{KVERREL}+%{1}\
Requires: kernel-%{1}-modules-uname-r = %{KVERREL}+%{1}\
Provides: installonlypkg(kernel)\
%description %{1}\
The meta-package for the %{1} kernel\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}\
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_internal_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%{nil}

# Now, each variant package.

%if %{with_pae}
%define variant_summary The Linux kernel compiled for Cortex-A15
%kernel_variant_package lpae
%description lpae-core
This package includes a version of the Linux kernel with support for
Cortex-A15 devices with LPAE and HW virtualisation support
%endif

%if %{with_zfcpdump}
%define variant_summary The Linux kernel compiled for zfcpdump usage
%kernel_variant_package zfcpdump
%description zfcpdump-core
The kernel package contains the Linux kernel (vmlinuz) for use by the
zfcpdump infrastructure.
# with_zfcpdump
%endif

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug-core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

# And finally the main -core package

%define variant_summary The Linux kernel
%kernel_variant_package
%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.

%if %{with_ipaclones}
%kernel_ipaclones_package
%endif

%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME}.spec ; then
    if [ "${patch:0:8}" != "patch-5." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz)  gunzip  < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.xz)  unxz    < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

%setup -q -n kernel-5.12-14712-ga48b0872e694 -c
mv linux-5.12-14712-ga48b0872e694 linux-%{KVERREL}

cd linux-%{KVERREL}
cp -a %{SOURCE1} .

%if !%{nopatches}

ApplyOptionalPatch patch-%{rpmversion}-redhat.patch
%endif

ApplyOptionalPatch linux-kernel-test.patch

# END OF PATCH APPLICATIONS

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl
mv COPYING COPYING-%{version}-%{release}

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# Mangle /usr/bin/python shebangs to /usr/bin/python3
# Mangle all Python shebangs to be Python 3 explicitly
# -p preserves timestamps
# -n prevents creating ~backup files
# -i specifies the interpreter for the shebang
# This fixes errors such as
# *** ERROR: ambiguous python shebang in /usr/bin/kvm_stat: #!/usr/bin/python. Change it to python3 (or python2) explicitly.
# We patch all sources below for which we got a report/error.
pathfix.py -i "%{__python3} %{py3_shbang_opts}" -p -n \
	tools/kvm/kvm_stat/kvm_stat \
	scripts/show_delta \
	scripts/diffconfig \
	scripts/bloat-o-meter \
	scripts/jobserver-exec \
	tools \
	Documentation \
	scripts/clang-tools

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
fi
mkdir configs
cd configs

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-*.config .
cp %{SOURCE51} .
# merge.pl
cp %{SOURCE3000} .
# kernel-local
cp %{SOURCE3001} .
VERSION=%{version} ./generate_all_configs.sh %{primary_target} %{debugbuildsenabled}

# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE3001} $i.tmp > $i
  rm $i.tmp
done
%endif

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
%endif

# Add DUP and kpatch certificates to system trusted keys for RHEL
%if 0%{?rhel}
%if %{signkernel}%{signmodules}
openssl x509 -inform der -in %{SOURCE100} -out rheldup3.pem
openssl x509 -inform der -in %{SOURCE101} -out rhelkpatch1.pem
cat rheldup3.pem rhelkpatch1.pem > ../certs/rhel.pem
for i in *.config; do
  sed -i 's@CONFIG_SYSTEM_TRUSTED_KEYS=""@CONFIG_SYSTEM_TRUSTED_KEYS="certs/rhel.pem"@' $i
done
%endif
%endif

cp %{SOURCE52} .
OPTS=""
%if %{with_configchecks}
	OPTS="$OPTS -w -n -c"
%endif
./process_configs.sh $OPTS kernel %{rpmversion}

cp %{SOURCE56} .
RPM_SOURCE_DIR=$RPM_SOURCE_DIR ./update_scripts.sh %{primary_target}

# end of kernel config
%endif

cd ..
# # End of Configs stuff

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -delete >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -delete >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

# Note we need to disable these flags for cross builds because the flags
# from redhat-rpm-config assume that host == target so target arch
# flags cause issues with the host compiler.
%if !%{with_cross}
%define build_hostcflags  %{?build_cflags}
%define build_hostldflags %{?build_ldflags}
%endif

%define make %{__make} %{?cross_opts} %{?make_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}"

InitBuildVars() {
    # Initialize the kernel .config file and create some variables that are
    # needed for the actual build process.

    Variant=$1

    # Pick the right kernel config file
    Config=kernel-%{version}-%{_target_cpu}${Variant:+-${Variant}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Variant:++${Variant}}

    KernelVer=%{version}-%{release}.%{_target_cpu}${Variant:++${Variant}}

    # make sure EXTRAVERSION says what we want it to say
    # Trim the release if this is a CI build, since KERNELVERSION is limited to 64 characters
    ShortRel=$(perl -e "print \"%{release}\" =~ s/\.pr\.[0-9A-Fa-f]{32}//r")
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -${ShortRel}.%{_target_cpu}${Variant:++${Variant}}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    # if we are post rc1 this should match anyway so this won't matter
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{patchlevel}/' Makefile

    %{make} %{?_smp_mflags} mrproper
    cp configs/$Config .config

    %if %{signkernel}%{signmodules}
    cp $RPM_SOURCE_DIR/x509.genkey certs/.
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    KCFLAGS="%{?kcflags}"

    # add kpatch flags for base kernel
    if [ "$Variant" == "" ]; then
        KCFLAGS="$KCFLAGS %{?kpatch_kcflags}"
    fi
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    DoVDSO=$3
    Variant=$4
    InstallName=${5:-vmlinuz}

    DoModules=1
    if [ "$Variant" = "zfcpdump" ]; then
	    DoModules=0
    fi

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    InitBuildVars $Variant

    echo BUILDING A KERNEL FOR ${Variant} %{_target_cpu}...

    %{make} ARCH=$Arch olddefconfig >/dev/null

    # This ensures build-ids are unique to allow parallel debuginfo
    perl -p -i -e "s/^CONFIG_BUILD_SALT.*/CONFIG_BUILD_SALT=\"%{KVERREL}\"/" .config
    %{make} ARCH=$Arch KCFLAGS="$KCFLAGS" WITH_GCOV="%{?with_gcov}" %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    if [ $DoModules -eq 1 ]; then
	%{make} ARCH=$Arch KCFLAGS="$KCFLAGS" WITH_GCOV="%{?with_gcov}" %{?_smp_mflags} modules %{?sparse_mflags} || exit 1
    fi

    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif

%ifarch %{arm} aarch64
    %{make} ARCH=$Arch dtbs INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    %{make} ARCH=$Arch dtbs_install INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    cp -r $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/dtb
    find arch/$Arch/boot/dts -name '*.dtb' -type f -delete
%endif

    # Start installing the results
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/config
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/System.map

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/lib/modules/$KernelVer/zImage.stub-$KernelVer || :
    fi

    %if %{signkernel}
    if [ "$KernelImage" = vmlinux ]; then
        # We can't strip and sign $KernelImage in place, because
        # we need to preserve original vmlinux for debuginfo.
        # Use a copy for signing.
        $CopyKernel $KernelImage $KernelImage.tosign
        KernelImage=$KernelImage.tosign
        CopyKernel=cp
    fi

    # Sign the image if we're using EFI
    # aarch64 kernels are gziped EFI images
    KernelExtension=${KernelImage##*.}
    if [ "$KernelExtension" == "gz" ]; then
        SignImage=${KernelImage%.*}
    else
        SignImage=$KernelImage
    fi

    %ifarch x86_64 aarch64
    %pesign -s -i $SignImage -o vmlinuz.tmp -a %{secureboot_ca_0} -c %{secureboot_key_0} -n %{pesign_name_0}
    %pesign -s -i vmlinuz.tmp -o vmlinuz.signed -a %{secureboot_ca_1} -c %{secureboot_key_1} -n %{pesign_name_1}
    rm vmlinuz.tmp
    %endif
    %ifarch s390x ppc64le
    if [ -x /usr/bin/rpm-sign ]; then
	rpm-sign --key "%{pesign_name_0}" --lkmsign $SignImage --output vmlinuz.signed
    elif [ $DoModules -eq 1 ]; then
	chmod +x scripts/sign-file
	./scripts/sign-file -p sha256 certs/signing_key.pem certs/signing_key.x509 $SignImage vmlinuz.signed
    else
	mv $SignImage vmlinuz.signed
    fi
    %endif

    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $SignImage
    if [ "$KernelExtension" == "gz" ]; then
        gzip -f9 $SignImage
    fi
    # signkernel
    %endif

    $CopyKernel $KernelImage \
                $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    cp $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/$InstallName

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;
    cp $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac $RPM_BUILD_ROOT/lib/modules/$KernelVer/.vmlinuz.hmac

    if [ $DoModules -eq 1 ]; then
	# Override $(mod-fw) because we don't want it to install any firmware
	# we'll get it from the linux-firmware package and we don't want conflicts
	%{make} %{?_smp_mflags} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT %{?_smp_mflags} modules_install KERNELRELEASE=$KernelVer mod-fw=
    fi

%if %{with_gcov}
    # install gcov-needed files to $BUILDROOT/$BUILD/...:
    #   gcov_info->filename is absolute path
    #   gcno references to sources can use absolute paths (e.g. in out-of-tree builds)
    #   sysfs symlink targets (set up at compile time) use absolute paths to BUILD dir
    find . \( -name '*.gcno' -o -name '*.[chS]' \) -exec install -D '{}' "$RPM_BUILD_ROOT/$(pwd)/{}" \;
%endif

    # add an a noop %%defattr statement 'cause rpm doesn't like empty file list files
    echo '%%defattr(-,-,-)' > ../kernel${Variant:+-${Variant}}-ldsoconf.list
    if [ $DoVDSO -ne 0 ]; then
        %{make} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
        if [ -s ldconfig-kernel.conf ]; then
             install -D -m 444 ldconfig-kernel.conf \
                $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
	     echo /etc/ld.so.conf.d/kernel-$KernelVer.conf >> ../kernel${Variant:+-${Variant}}-ldsoconf.list
        fi

        rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
    fi

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # CONFIG_KERNEL_HEADER_TEST generates some extra files in the process of
    # testing so just delete
    find . -name *.h.s -delete
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ ! -e Module.symvers ]; then
        touch Module.symvers
    fi
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    cp $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz $RPM_BUILD_ROOT/lib/modules/$KernelVer/symvers.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Variant ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Variant $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        # for now, don't keep it around.
        rm $RPM_BUILD_ROOT/Module.kabi
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidupchk}
    echo "**** kABI DUP checking is enabled in kernel SPEC file. ****"
    if [ -e $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Variant ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Variant $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        # for now, don't keep it around.
        rm $RPM_BUILD_ROOT/Module.kabi
    else
        echo "**** NOTE: Cannot find DUP reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidw_base}
    # Don't build kabi base for debug kernels
    if [ "$Variant" != "kdump" -a "$Variant" != "debug" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf

        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/whitelists
        tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/whitelists

        echo "**** GENERATING DWARF-based kABI baseline dataset ****"
        chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
        $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
            "$RPM_BUILD_ROOT/kabi-dwarf/whitelists/kabi-current/kabi_whitelist_%{_target_cpu}" \
            "$(pwd)" \
            "$RPM_BUILD_ROOT/kabidw-base/%{_target_cpu}${Variant:+.${Variant}}" || :

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

%if %{with_kabidwchk}
    if [ "$Variant" != "kdump" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf
        if [ -d "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}" ]; then
            mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/whitelists
            tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/whitelists

            echo "**** GENERATING DWARF-based kABI dataset ****"
            chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
                "$RPM_BUILD_ROOT/kabi-dwarf/whitelists/kabi-current/kabi_whitelist_%{_target_cpu}" \
                "$(pwd)" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}.tmp" || :

            echo "**** kABI DWARF-based comparison report ****"
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh compare \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Variant:+.${Variant}}.tmp" || :
            echo "**** End of kABI DWARF-based comparison report ****"
        else
            echo "**** Baseline dataset for kABI DWARF-BASED comparison report not found ****"
        fi

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/tracing
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/spdxcheck.py

    # Files for 'make scripts' to succeed with kernel-devel.
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/security/selinux/include
    cp -a --parents security/selinux/include/classmap.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents security/selinux/include/initial_sid_to_string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/include/tools
    cp -a --parents tools/include/tools/be_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/tools/le_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # Files for 'make prepare' to succeed with kernel-devel.
    cp -a --parents tools/include/linux/compiler* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/linux/types.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/build/Build.include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/build/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/build/fixdep.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/sync-check.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/bpf/resolve_btfids $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    cp --parents security/selinux/include/policycap_names.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents security/selinux/include/policycap.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    cp -a --parents tools/include/asm-generic $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/linux $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/uapi/asm $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/uapi/asm-generic $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/uapi/linux $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/include/vdso $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/scripts/utilities.mak $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/lib/subcmd $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/lib/*.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/*.[ch] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/objtool/include/objtool/*.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/lib/bpf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp --parents tools/lib/bpf/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    if [ -f tools/objtool/fixdep ]; then
      cp -a tools/objtool/fixdep $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    if [ -f arch/%{asmarch}/kernel/module.lds ]; then
      cp -a --parents arch/%{asmarch}/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    find $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
%ifarch ppc64le
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # arch/arm64/include/asm/xen references arch/arm
    cp -a --parents arch/arm/include/asm/xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    # arch/arm64/include/asm/opcodes.h references arch/arm
    cp -a --parents arch/arm/include/asm/opcodes.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    # include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
    if [ -d arch/%{asmarch}/mach-${Variant}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Variant}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    # include a few files for 'make prepare'
    cp -a --parents arch/arm/tools/gen-mach-types $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/arm/tools/mach-types $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
%ifarch i686 x86_64
    # files for 'make prepare' to succeed with kernel-devel
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscalltbl.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscallhdr.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_32.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_64.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_common.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/setup-x86_64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/entry64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/ctype.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

    cp -a --parents tools/arch/x86/include/asm $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/arch/x86/include/uapi/asm $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/objtool/arch/x86/lib $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/arch/x86/lib/ $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a --parents tools/objtool/arch/x86/ $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

%endif
    # Clean up intermediate tools files
    find $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    eu-readelf -n vmlinux | grep "Build ID" | awk '{print $NF}' > vmlinux.id
    cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    if [ -n "%{vmlinux_decompressor}" ]; then
	    eu-readelf -n  %{vmlinux_decompressor} | grep "Build ID" | awk '{print $NF}' > vmlinux.decompressor.id
	    # Without build-id the build will fail. But for s390 the build-id
	    # wasn't added before 5.11. In case it is missing prefer not
	    # packaging the debuginfo over a build failure.
	    if [ -s vmlinux.decompressor.id ]; then
		    cp vmlinux.decompressor.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.decompressor.id
		    cp %{vmlinux_decompressor} $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer/vmlinux.decompressor
	    fi
    fi
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
        LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking \
      'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
      'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm \
      'drm_open|drm_init'
    collect_modules_list modesetting \
      'drm_crtc_init'

    # detect missing or incorrect license tags
    ( find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' | xargs /sbin/modinfo -l | \
        grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1

    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    # Identify modules in the kernel-modules-extras package
    %{SOURCE17} $RPM_BUILD_ROOT lib/modules/$KernelVer $RPM_SOURCE_DIR/mod-extra.list
    # Identify modules in the kernel-modules-extras package
    %{SOURCE17} $RPM_BUILD_ROOT lib/modules/$KernelVer %{SOURCE54} internal

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # don't include anything going into kernel-modules-extra in the file lists
    xargs rm -rf < mod-extra.list
    # don't include anything going int kernel-modules-internal in the file lists
    xargs rm -rf < mod-internal.list

    if [ $DoModules -eq 1 ]; then
	# Find all the module files and filter them out into the core and
	# modules lists.  This actually removes anything going into -modules
	# from the dir.
	find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
	cp $RPM_SOURCE_DIR/filter-*.sh .
	./filter-modules.sh modules.list %{_target_cpu}
	rm filter-*.sh

	# Run depmod on the resulting module tree and make sure it isn't broken
	depmod -b . -aeF ./System.map $KernelVer &> depmod.out
	if [ -s depmod.out ]; then
	    echo "Depmod failure"
	    cat depmod.out
	    exit 1
	else
	    rm depmod.out
	fi
    else
	# Ensure important files/directories exist to let the packaging succeed
	echo '%%defattr(-,-,-)' > modules.list
	echo '%%defattr(-,-,-)' > k-d.list
	mkdir -p lib/modules/$KernelVer/kernel
	# Add files usually created by make modules, needed to prevent errors
	# thrown by depmod during package installation
	touch lib/modules/$KernelVer/modules.order
	touch lib/modules/$KernelVer/modules.builtin
    fi

    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    # Go back and find all of the various directories in the tree.  We use this
    # for the dir lists in kernel-core
    find lib/modules/$KernelVer/kernel -mindepth 1 -type d | sort -n > module-dirs.list

    # Cleanup
    rm System.map
    cp -r restore/* lib/modules/$KernelVer/.
    rm -rf restore
    popd

    # Make sure the files lists start with absolute paths or rpmbuild fails.
    # Also add in the dir entries
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../kernel${Variant:+-${Variant}}-modules.list
    sed -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../kernel${Variant:+-${Variant}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../kernel${Variant:+-${Variant}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/mod-extra.list >> ../kernel${Variant:+-${Variant}}-modules-extra.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/mod-internal.list >> ../kernel${Variant:+-${Variant}}-modules-internal.list

    # Cleanup
    rm -f $RPM_BUILD_ROOT/k-d.list
    rm -f $RPM_BUILD_ROOT/modules.list
    rm -f $RPM_BUILD_ROOT/module-dirs.list
    rm -f $RPM_BUILD_ROOT/mod-extra.list
    rm -f $RPM_BUILD_ROOT/mod-internal.list

%if %{signmodules}
    if [ $DoModules -eq 1 ]; then
	# Save the signing keys so we can sign the modules in __modsign_install_post
	cp certs/signing_key.pem certs/signing_key.pem.sign${Variant:++${Variant}}
	cp certs/signing_key.x509 certs/signing_key.x509.sign${Variant:++${Variant}}
    fi
%endif

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir

    # This is going to create a broken link during the build, but we don't use
    # it after this point.  We need the link to actually point to something
    # when kernel-devel is installed, and a relative link doesn't work across
    # the F17 UsrMove feature.
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -delete

    # build a BLS config for this kernel
    %{SOURCE53} "$KernelVer" "$RPM_BUILD_ROOT" "%{?variant}"

    # Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer
    %ifarch x86_64 aarch64
       install -m 0644 %{secureboot_ca_0} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca-20200609.cer
       install -m 0644 %{secureboot_ca_1} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca-20140212.cer
       ln -s kernel-signing-ca-20200609.cer $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
    %else
       install -m 0644 %{secureboot_ca_0} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
    %endif
    %ifarch s390x ppc64le
    if [ $DoModules -eq 1 ]; then
	if [ -x /usr/bin/rpm-sign ]; then
	    install -m 0644 %{secureboot_key_0} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	else
	    install -m 0644 certs/signing_key.x509.sign${Variant:++${Variant}} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
	    openssl x509 -in certs/signing_key.pem.sign${Variant:++${Variant}} -outform der -out $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	    chmod 0644 $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	fi
    fi
    %endif

%if %{with_ipaclones}
    MAXPROCS=$(echo %{?_smp_mflags} | sed -n 's/-j\s*\([0-9]\+\)/\1/p')
    if [ -z "$MAXPROCS" ]; then
        MAXPROCS=1
    fi
    if [ "$Variant" == "" ]; then
        mkdir -p $RPM_BUILD_ROOT/$DevelDir-ipaclones
        find . -name '*.ipa-clones' | xargs -i{} -r -n 1 -P $MAXPROCS install -m 644 -D "{}" "$RPM_BUILD_ROOT/$DevelDir-ipaclones/{}"
    fi
%endif

}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVERREL}


%if %{with_debug}
BuildKernel %make_target %kernel_image %{_use_vdso} debug
%endif

%if %{with_zfcpdump}
BuildKernel %make_target %kernel_image %{_use_vdso} zfcpdump
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image %{use_vdso} lpae
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image %{_use_vdso}
%endif

%ifnarch noarch i686
%if !%{with_debug} && !%{with_zfcpdump} && !%{with_up}
# If only building the user space tools, then initialize the build environment
# and some variables so that the various userspace tools can be built.
InitBuildVars
%endif
%endif

%global perf_make \
  %{__make} -s EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?cross_opts} -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 prefix=%{_prefix} PYTHON=%{__python3}
%if %{with_perf}
# perf
# make sure check-headers.sh is executable
chmod +x tools/perf/check-headers.sh
%{perf_make} DESTDIR=$RPM_BUILD_ROOT all
%endif

%global tools_make \
  %{make} CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" V=1

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%{tools_make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{tools_make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   %{tools_make}
   popd
   pushd tools/power/x86/turbostat
   %{tools_make}
   popd
   pushd tools/power/x86/intel-speed-select
   %{make}
   popd
%endif
%endif
pushd tools/thermal/tmon/
%{tools_make}
popd
pushd tools/iio/
# Needs to be fixed to pick up CFLAGS
%{__make}
popd
pushd tools/gpio/
# Needs to be fixed to pick up CFLAGS
%{__make}
popd
%endif

%global bpftool_make \
  %{__make} EXTRA_CFLAGS="${RPM_OPT_FLAGS}" EXTRA_LDFLAGS="%{__global_ldflags}" DESTDIR=$RPM_BUILD_ROOT V=1
%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make}
popd
%endif

%if %{with_selftests}
%{make} -s %{?_smp_mflags} ARCH=$Arch V=1 samples/bpf/
pushd tools/testing/selftests
# We need to install here because we need to call make with ARCH set which
# doesn't seem possible to do in the install section.
%{make} -s %{?_smp_mflags} ARCH=$Arch V=1 TARGETS="bpf livepatch net" INSTALL_PATH=%{buildroot}%{_libexecdir}/kselftests install
popd
%endif

%if %{with_doc}
# Make the HTML pages.
%{__make} PYTHON=/usr/bin/python3 htmldocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "variant" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that variant.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Don't sign modules for the zfcpdump variant as it is monolithic.

%define __modsign_install_post \
  if [ "%{signmodules}" -eq "1" ]; then \
    if [ "%{with_pae}" -ne "0" ]; then \
       %{modsign_cmd} certs/signing_key.pem.sign+lpae certs/signing_key.x509.sign+lpae $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+lpae/ \
    fi \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+debug certs/signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign certs/signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
    fi \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs -P%{zcpu} xz; \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%endif

%endif

# We don't want to package debuginfo for self-tests and samples but
# we have to delete them to avoid an error messages about unpackaged
# files.
# Delete the debuginfo for kernel-devel files
%define __remove_unwanted_dbginfo_install_post \
  if [ "%{with_selftests}" -ne "0" ]; then \
    rm -rf $RPM_BUILD_ROOT/usr/lib/debug/usr/libexec/ksamples; \
    rm -rf $RPM_BUILD_ROOT/usr/lib/debug/usr/libexec/kselftests; \
  fi \
  rm -rf $RPM_BUILD_ROOT/usr/lib/debug/usr/src; \
%{nil}

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__remove_unwanted_dbginfo_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}

# copy the source over
mkdir -p $docdir
tar -h -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# with_doc
%endif

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
%{__make} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

%endif

%if %{with_cross_headers}
%if 0%{?fedora}
HDR_ARCH_LIST='arm arm64 powerpc s390 x86'
%else
HDR_ARCH_LIST='arm64 powerpc s390 x86'
%endif
mkdir -p $RPM_BUILD_ROOT/usr/tmp-headers

for arch in $HDR_ARCH_LIST; do
	mkdir $RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch}
	%{__make} ARCH=${arch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch} headers_install
done

find $RPM_BUILD_ROOT/usr/tmp-headers \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

# Copy all the architectures we care about to their respective asm directories
for arch in $HDR_ARCH_LIST ; do
	mkdir -p $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include
	mv $RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch}/include/* $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/
done

rm -rf $RPM_BUILD_ROOT/usr/tmp-headers
%endif

%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE300} -C $INSTALL_KABI_PATH
# with_kernel_abi_whitelists
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-bin install-traceevent-plugins
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# For both of the below, yes, this should be using a macro but right now
# it's hard coded and we don't actually want it anyway right now.
# Whoever wants examples can fix it up!

# remove examples
rm -rf %{buildroot}/usr/lib/perf/examples
# remove the stray files that somehow got packaged
rm -rf %{buildroot}/usr/lib/perf/include/bpf/bpf.h
rm -rf %{buildroot}/usr/lib/perf/include/bpf/stdio.h
rm -rf %{buildroot}/usr/lib/perf/include/bpf/linux/socket.h
rm -rf %{buildroot}/usr/lib/perf/include/bpf/pid_filter.h
rm -rf %{buildroot}/usr/lib/perf/include/bpf/unistd.h

# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
mkdir -p %{buildroot}/%{_mandir}/man1
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
%{make} -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif
%ifarch x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   %{tools_make} DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   %{tools_make} DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/intel-speed-select
   %{tools_make} CFLAGS+="-D_GNU_SOURCE -Iinclude" DESTDIR=%{buildroot} install
   popd
%endif
pushd tools/thermal/tmon
%{tools_make} INSTALL_ROOT=%{buildroot} install
popd
pushd tools/iio
%{__make} DESTDIR=%{buildroot} install
popd
pushd tools/gpio
%{__make} DESTDIR=%{buildroot} install
popd
pushd tools/kvm/kvm_stat
%{__make} INSTALL_ROOT=%{buildroot} install-tools
%{__make} INSTALL_ROOT=%{buildroot} install-man
popd
%endif

%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install doc-install
popd
%endif

%if %{with_selftests}
pushd samples
install -d %{buildroot}%{_libexecdir}/ksamples
# install bpf samples
pushd bpf
install -d %{buildroot}%{_libexecdir}/ksamples/bpf
find -type f -executable -exec install -m755 {} %{buildroot}%{_libexecdir}/ksamples/bpf \;
install -m755 *.sh %{buildroot}%{_libexecdir}/ksamples/bpf
# test_lwt_bpf.sh compiles test_lwt_bpf.c when run; this works only from the
# kernel tree. Just remove it.
rm %{buildroot}%{_libexecdir}/ksamples/bpf/test_lwt_bpf.sh
install -m644 tcp_bpf.readme %{buildroot}%{_libexecdir}/ksamples/bpf
popd
# install pktgen samples
pushd pktgen
install -d %{buildroot}%{_libexecdir}/ksamples/pktgen
find . -type f -executable -exec install -m755 {} %{buildroot}%{_libexecdir}/ksamples/pktgen/{} \;
find . -type f ! -executable -exec install -m644 {} %{buildroot}%{_libexecdir}/ksamples/pktgen/{} \;
popd
popd
# install drivers/net/mlxsw selftests
pushd tools/testing/selftests/drivers/net/mlxsw
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/drivers/net/mlxsw/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/drivers/net/mlxsw/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/drivers/net/mlxsw/{} \;
popd
# install net/forwarding selftests
pushd tools/testing/selftests/net/forwarding
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/net/forwarding/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/net/forwarding/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/net/forwarding/{} \;
popd
# install tc-testing selftests
pushd tools/testing/selftests/tc-testing
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/tc-testing/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/tc-testing/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/tc-testing/{} \;
popd
# install livepatch selftests
pushd tools/testing/selftests/livepatch
find -type d -exec install -d %{buildroot}%{_libexecdir}/kselftests/livepatch/{} \;
find -type f -executable -exec install -D -m755 {} %{buildroot}%{_libexecdir}/kselftests/livepatch/{} \;
find -type f ! -executable -exec install -D -m644 {} %{buildroot}%{_libexecdir}/kselftests/livepatch/{} \;
popd
%endif

# We have to do the headers checksum calculation after the tools install because
# these might end up installing their own set of headers on top of kernel's
%if %{with_headers}
# compute a content hash to export as Provides: kernel-headers-checksum
HEADERS_CHKSUM=$(export LC_ALL=C; find $RPM_BUILD_ROOT/usr/include -type f -name "*.h" \
			! -path $RPM_BUILD_ROOT/usr/include/linux/version.h | \
		 sort | xargs cat | sha1sum - | cut -f 1 -d ' ');
# export the checksum via usr/include/linux/version.h, so the dynamic
# find-provides can grab the hash to update it accordingly
echo "#define KERNEL_HEADERS_CHECKSUM \"$HEADERS_CHKSUM\"" >> $RPM_BUILD_ROOT/usr/include/linux/version.h
%endif

###
### clean
###

###
### scripts
###

%if %{with_tools}
%post -n kernel-tools-libs
/sbin/ldconfig

%postun -n kernel-tools-libs
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
# Note we don't run hardlink if ostree is in use, as ostree is
# a far more sophisticated hardlink implementation.
# https://github.com/projectatomic/rpm-ostree/commit/58a79056a889be8814aa51f507b2c7a4dccee526
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ] \
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f\
     done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-internal package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_internal_post [<subpackage>]
#
%define kernel_modules_internal_post() \
%{expand:%%post %{?1:%{1}-}modules-internal}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-internal}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_post [<subpackage>]
#
%define kernel_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
%if 0%{!?fedora:1}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%endif\
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%{expand:%%kernel_modules_internal_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%if %{with_pae}
%kernel_variant_preun lpae
%kernel_variant_post -v lpae -r (kernel|kernel-smp)
%endif

%kernel_variant_preun debug
%kernel_variant_post -v debug

%if %{with_zfcpdump}
%kernel_variant_preun zfcpdump
%kernel_variant_post -v zfcpdump
%endif

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
/usr/include/*
%endif

%if %{with_cross_headers}
%files cross-headers
/usr/*-linux-gnu/include/*
%endif

%if %{with_kernel_abi_whitelists}
%files -n kernel-abi-whitelists
/lib/modules/kabi-*
%endif

%if %{with_kabidw_base}
%ifarch x86_64 s390x ppc64 ppc64le aarch64
%files kabidw-base
%defattr(-,root,root)
/kabidw-base/%{_target_cpu}/*
%endif
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%endif

%if %{with_perf}
%files -n perf
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_datadir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt
%{_docdir}/perf-tip/tips.txt

%files -n python3-perf
%{python3_sitearch}/*

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo

%files -f python3-perf-debuginfo.list -n python3-perf-debuginfo
%endif
# with_perf
%endif

%if %{with_tools}
%ifnarch %{cpupowerarchs}
%files -n kernel-tools
%else
%files -n kernel-tools -f cpupower.lang
%{_bindir}/cpupower
%{_datadir}/bash-completion/completions/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%{_bindir}/intel-speed-select
%endif
# cpupowerarchs
%endif
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_bindir}/gpio-watch
%{_mandir}/man1/kvm_stat*
%{_bindir}/kvm_stat

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n kernel-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
# with_tools
%endif

%if %{with_bpftool}
%files -n bpftool
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man8/bpftool-cgroup.8.gz
%{_mandir}/man8/bpftool-gen.8.gz
%{_mandir}/man8/bpftool-iter.8.gz
%{_mandir}/man8/bpftool-link.8.gz
%{_mandir}/man8/bpftool-map.8.gz
%{_mandir}/man8/bpftool-prog.8.gz
%{_mandir}/man8/bpftool-perf.8.gz
%{_mandir}/man8/bpftool.8.gz
%{_mandir}/man8/bpftool-net.8.gz
%{_mandir}/man8/bpftool-feature.8.gz
%{_mandir}/man8/bpftool-btf.8.gz
%{_mandir}/man8/bpftool-struct_ops.8.gz

%if %{with_debuginfo}
%files -f bpftool-debuginfo.list -n bpftool-debuginfo
%defattr(-,root,root)
%endif
%endif

%if %{with_selftests}
%files selftests-internal
%{_libexecdir}/ksamples
%{_libexecdir}/kselftests
%endif

# empty meta-package
%ifnarch %nobuildarches noarch
%files
%endif

%if %{with_gcov}
%ifarch x86_64 s390x ppc64le aarch64
%files gcov
%{_builddir}
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <use_vdso> <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{2}\
%{expand:%%files -f kernel-%{?3:%{3}-}core.list %{?1:-f kernel-%{?3:%{3}-}ldsoconf.list} %{?3:%{3}-}core}\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING-%{version}-%{release}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/%{?-k:%{-k*}}%{!?-k:vmlinuz}\
%ghost /%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/.vmlinuz.hmac \
%ghost /%{image_install_path}/.vmlinuz-%{KVERREL}%{?3:+%{3}}.hmac \
%ifarch %{arm} aarch64\
/lib/modules/%{KVERREL}%{?3:+%{3}}/dtb \
%ghost /%{image_install_path}/dtb-%{KVERREL}%{?3:+%{3}} \
%endif\
%attr(600,root,root) /lib/modules/%{KVERREL}%{?3:+%{3}}/System.map\
%ghost /boot/System.map-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/symvers.gz\
/lib/modules/%{KVERREL}%{?3:+%{3}}/config\
%ghost /boot/symvers-%{KVERREL}%{?3:+%{3}}.gz\
%ghost /boot/config-%{KVERREL}%{?3:+%{3}}\
%ghost /boot/initramfs-%{KVERREL}%{?3:+%{3}}.img\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}/kernel\
/lib/modules/%{KVERREL}%{?3:+%{3}}/build\
/lib/modules/%{KVERREL}%{?3:+%{3}}/source\
/lib/modules/%{KVERREL}%{?3:+%{3}}/updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/bls.conf\
/lib/modules/%{KVERREL}%{?3:+%{3}}/weak-updates\
%{_datadir}/doc/kernel-keys/%{KVERREL}%{?3:+%{3}}\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f kernel-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%{expand:%%files %{?3:%{3}-}devel}\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files -f kernel-%{?3:%{3}-}modules-extra.list %{?3:%{3}-}modules-extra}\
%config(noreplace) /etc/modprobe.d/*-blacklist.conf\
%{expand:%%files -f kernel-%{?3:%{3}-}modules-internal.list %{?3:%{3}-}modules-internal}\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?3}.list %{?3:%{3}-}debuginfo}\
%endif\
%endif\
%if %{?3:1} %{!?3:0}\
%{expand:%%files %{3}}\
%endif\
%endif\
%{nil}

%kernel_variant_files %{_use_vdso} %{with_up}
%kernel_variant_files %{_use_vdso} %{with_debug} debug
%kernel_variant_files %{use_vdso} %{with_pae} lpae
%kernel_variant_files %{_use_vdso} %{with_zfcpdump} zfcpdump

%define kernel_variant_ipaclones(k:) \
%if %{1}\
%if %{with_ipaclones}\
%{expand:%%files %{?2:%{2}-}ipaclones-internal}\
%defattr(-,root,root)\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?2:+%{2}}-ipaclones\
%endif\
%endif\
%{nil}

%kernel_variant_ipaclones %{with_up}

# plz don't put in a version string unless you're going to tag
# and build.
#
#
%changelog
* Fri May 07 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210507gita48b0872e694.10]
- Keep sctp and l2tp modules in modules-extra (Don Zickus)
- Fix ppc64le cross build packaging (Don Zickus)
- Fedora: Make amd_pinctrl module builtin (Hans de Goede)

* Thu May 06 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210506git8404c9fbc84b.9]
- Keep CONFIG_KASAN_HW_TAGS off for aarch64 debug configs (Justin M. Forbes)
- New configs in drivers/bus (Fedora Kernel Team)
- RHEL: Don't build KVM PR module on ppc64 (David Gibson) [1930649]

* Wed May 05 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210505gitd665ea6ea86c.8]
- Flip CONFIG_USB_ROLE_SWITCH from m to y (Justin M. Forbes)
- Set valid options for CONFIG_FW_LOADER_USER_HELPER (Justin M. Forbes)
- Clean up CONFIG_FB_MODE_HELPERS (Justin M. Forbes)
- Turn off CONFIG_VFIO for the s390x zfcpdump kernel (Justin M. Forbes)
- Delete unused CONFIG_SND_SOC_MAX98390 pending-common (Justin M. Forbes)
- Update pending-common configs, preparing to set correctly (Justin M. Forbes)
- Update fedora filters for surface (Justin M. Forbes)
- Build CONFIG_CRYPTO_ECDSA inline for s390x zfcpdump (Justin M. Forbes)

* Tue May 04 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210504git5e321ded302d.7]
- Fix branch creation for releases based on tags (Jeremy Cline)
- Replace "flavour" where "variant" is meant instead (David Ward)
- Drop the %%{variant} macro and fix --with-vanilla (David Ward)
- Fix syntax of %%kernel_variant_files (David Ward)
- Change description of --without-vdso-install to fix typo (David Ward)
- Config updates to work around mismatches (Justin M. Forbes)
- CONFIG_SND_SOC_FSL_ASOC_CARD selects CONFIG_MFD_WM8994 now (Justin M. Forbes)
- wireguard: disable in FIPS mode (Hangbin Liu) [1940794]
- Enable mtdram for fedora (rhbz 1955916) (Justin M. Forbes)

* Mon May 03 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210503git9ccce092fc64.6]
- Remove reference to bpf-helpers man page (Justin M. Forbes)
- Fedora: enable more modules for surface devices (Dave Olsthoorn)

* Sat May 01 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210501git9f67672a817e.4]
- Fix Fedora config mismatch for CONFIG_FSL_ENETC_IERB (Justin M. Forbes)

* Fri Apr 30 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210430git8ca5297e7e38.3]
- hardlink is in /usr/bin/ now (Justin M. Forbes)
- Ensure CONFIG_KVM_BOOK3S_64_PR stays on in Fedora, even if it is turned off in RHEL (Justin M. Forbes)
- Set date in package release from repository commit, not system clock (David Ward)
- Use a better upstream tarball filename for snapshots (David Ward)
- Don't create empty pending-common files on pending-fedora commits (Don Zickus)
- nvme: multipath: Change default of kernel NVMe multipath to be disabled (Mike Snitzer)
- nvme: decouple basic ANA log page re-read support from native multipathing (Mike Snitzer)
- nvme: allow local retry and proper failover for REQ_FAILFAST_TRANSPORT (Mike Snitzer)
- nvme: Return BLK_STS_TARGET if the DNR bit is set (Mike Snitzer)
- Add redhat/configs/pending-common/generic/s390x/zfcpdump/CONFIG_NETFS_SUPPORT (Justin M. Forbes)

* Wed Apr 28 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.13.0-0.rc0.20210428gitacd3d2859453.2]
- Reset the counter as we start the 5.13 merge window (Justin M. Forbes)
- Create ark-latest branch last for CI scripts (Don Zickus)
- Replace /usr/libexec/platform-python with /usr/bin/python3 (David Ward)
- Turn off ADI_AXI_ADC and AD9467 which now require CONFIG_OF (Justin M. Forbes)
- Export ark infrastructure files (Don Zickus)
- docs: Update docs to reflect newer workflow. (Don Zickus)
- Use upstream/master for merge-base with fallback to master (Don Zickus)
- Fedora: Turn off the SND_INTEL_BYT_PREFER_SOF option (Hans de Goede)
- filter-modules.sh.fedora: clean up "netprots" (Paul Bolle)
- filter-modules.sh.fedora: clean up "scsidrvs" (Paul Bolle)
- filter-*.sh.fedora: clean up "ethdrvs" (Paul Bolle)
- filter-*.sh.fedora: clean up "driverdirs" (Paul Bolle)
- filter-*.sh.fedora: remove incorrect entries (Paul Bolle)
- filter-*.sh.fedora: clean up "singlemods" (Paul Bolle)
- filter-modules.sh.fedora: drop unused list "iiodrvs" (Paul Bolle)
- Update mod-internal to fix depmod issue (Nico Pache)
- Turn on CONFIG_VDPA_SIM_NET (rhbz 1942343) (Justin M. Forbes)
- New configs in drivers/power (Fedora Kernel Team)
- Turn on CONFIG_NOUVEAU_DEBUG_PUSH for debug configs (Justin M. Forbes)
- Turn off KFENCE sampling by default for Fedora (Justin M. Forbes)
- Fedora config updates round 2 (Justin M. Forbes)
- New configs in drivers/soc (Jeremy Cline)
- filter-modules.sh: Fix copy/paste error 'input' (Paul Bolle)
- Update module filtering for 5.12 kernels (Justin M. Forbes)
- Fix genlog.py to ensure that comments retain "%%" characters. (Mark Mielke)
- New configs in drivers/leds (Fedora Kernel Team)
- Limit CONFIG_USB_CDNS_SUPPORT to x86_64 and arm in Fedora (David Ward)
- Fedora: Enable CHARGER_GPIO on aarch64 too (Peter Robinson)
- Fedora config updates (Justin M. Forbes)
- wireguard: mark as Tech Preview (Hangbin Liu) [1613522]
- configs: enable CONFIG_WIREGUARD in ARK (Hangbin Liu) [1613522]
- Remove duplicate configs acroos fedora, ark and common (Don Zickus)
- Combine duplicate configs across ark and fedora into common (Don Zickus)
- common/ark: cleanup and unify the parport configs (Peter Robinson)
- iommu/vt-d: enable INTEL_IDXD_SVM for both fedora and rhel (Jerry Snitselaar)
- REDHAT: coresight: etm4x: Disable coresight on HPE Apollo 70 (Jeremy Linton)
- configs/common/generic: disable CONFIG_SLAB_MERGE_DEFAULT (Rafael Aquini)
- Remove _legacy_common_support (Justin M. Forbes)
- redhat/mod-blacklist.sh: Fix floppy blacklisting (Hans de Goede)
- New configs in fs/pstore (CKI@GitLab)
- New configs in arch/powerpc (Fedora Kernel Team)
- configs: enable BPF LSM on Fedora and ARK (Ondrej Mosnacek)
- configs: clean up LSM configs (Ondrej Mosnacek)
- New configs in drivers/platform (CKI@GitLab)
- New configs in drivers/firmware (CKI@GitLab)
- New configs in drivers/mailbox (Fedora Kernel Team)
- New configs in drivers/net/phy (Justin M. Forbes)
- Update CONFIG_DM_MULTIPATH_IOA (Augusto Caringi)
- New configs in mm/Kconfig (CKI@GitLab)
- New configs in arch/powerpc (Jeremy Cline)
- New configs in arch/powerpc (Jeremy Cline)
- New configs in drivers/input (Fedora Kernel Team)
- New configs in net/bluetooth (Justin M. Forbes)
- New configs in drivers/clk (Fedora Kernel Team)
- New configs in init/Kconfig (Jeremy Cline)
- redhat: allow running fedora-configs and rh-configs targets outside of redhat/ (Herton R. Krzesinski)
- all: unify the disable of goldfish (android emulation platform) (Peter Robinson)
- common: minor cleanup/de-dupe of dma/dmabuf debug configs (Peter Robinson)
- common/ark: these drivers/arches were removed in 5.12 (Peter Robinson)
- common: unset serial mouse for general config (Peter Robinson)
- Correct kernel-devel make prepare build for 5.12. (Paulo E. Castro)
- redhat: add initial support for centos stream dist-git sync on Makefiles (Herton R. Krzesinski)
- redhat/configs: Enable CONFIG_SCHED_STACK_END_CHECK for Fedora and ARK (Josh Poimboeuf) [1856174]
- CONFIG_VFIO now selects IOMMU_API instead of depending on it, causing several config mismatches for the zfcpdump kernel (Justin M. Forbes)
- Turn off weak-modules for Fedora (Justin M. Forbes)
- redhat: enable CONFIG_FW_LOADER_COMPRESS for ARK (Herton R. Krzesinski) [1939095]
- Fedora: filters: update to move dfl-emif to modules (Peter Robinson)
- drop duplicate DEVFREQ_GOV_SIMPLE_ONDEMAND config (Peter Robinson)
- efi: The EFI_VARS is legacy and now x86 only (Peter Robinson)
- common: enable RTC_SYSTOHC to supplement update_persistent_clock64 (Peter Robinson)
- generic: arm: enable SCMI for all options (Peter Robinson)
- fedora: the PCH_CAN driver is x86-32 only (Peter Robinson)
- common: disable legacy CAN device support (Peter Robinson)
- common: Enable Microchip MCP251x/MCP251xFD CAN controllers (Peter Robinson)
- common: Bosch MCAN support for Intel Elkhart Lake (Peter Robinson)
- common: enable CAN_PEAK_PCIEFD PCI-E driver (Peter Robinson)
- common: disable CAN_PEAK_PCIEC PCAN-ExpressCard (Peter Robinson)
- common: enable common CAN layer 2 protocols (Peter Robinson)
- ark: disable CAN_LEDS option (Peter Robinson)
- Fedora: Turn on SND_SOC_INTEL_SKYLAKE_HDAUDIO_CODEC option (Hans de Goede)
- Fedora: enable modules for surface devices (Dave Olsthoorn)
- Turn on SND_SOC_INTEL_SOUNDWIRE_SOF_MACH for Fedora again (Justin M. Forbes)
- common: fix WM8804 codec dependencies (Peter Robinson)
- Build SERIO_SERPORT as a module (Peter Robinson)
- input: touchscreen: move ELO and Wacom serial touchscreens to x86 (Peter Robinson)
- Sync serio touchscreens for non x86 architectures to the same as ARK (Peter Robinson)
- Only enable SERIO_LIBPS2 on x86 (Peter Robinson)
- Only enable PC keyboard controller and associated keyboard on x86 (Peter Robinson)
- Generic: Mouse: Tweak generic serial mouse options (Peter Robinson)
- Only enable PS2 Mouse options on x86 (Peter Robinson)
- Disable bluetooth highspeed by default (Peter Robinson)
- Fedora: A few more general updates for 5.12 window (Peter Robinson)
- Fedora: Updates for 5.12 merge window (Peter Robinson)
- Fedora: remove dead options that were removed upstream (Peter Robinson)
- Revert "mm/kmemleak: skip late_init if not skip disable" (Herton R. Krzesinski)
- Revert "ARM: fix __get_user_check() in case uaccess_* calls are not inlined" (Herton R. Krzesinski)
- Revert "dt-bindings: panel: add binding for Xingbangda XBD599 panel" (Herton R. Krzesinski)
- redhat: remove CONFIG_DRM_PANEL_XINGBANGDA_XBD599 (Herton R. Krzesinski)
- Revert "drm: panel: add Xingbangda XBD599 panel" (Herton R. Krzesinski)
- Revert "drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation" (Herton R. Krzesinski)
- New configs in arch/powerpc (Fedora Kernel Team)
- Fix merge issue (Justin M. Forbes)
- Revert pending so that MR works (Justin M. Forbes)
- Change the pending config for CONFIG_PPC_QUEUED_SPINLOCKS as it is now default upstream for 64-bit server CPUs (Justin M. Forbes)
- Turn on CONFIG_PPC_QUEUED_SPINLOCKS as it is default upstream now (Justin M. Forbes)
- Update pending-common configs to address new upstream config deps (Justin M. Forbes)
- rpmspec: ship gpio-watch.debug in the proper debuginfo package (Herton R. Krzesinski)
- Removed description text as a comment confuses the config generation (Justin M. Forbes)
- New configs in drivers/dma-buf (Jeremy Cline)
- Fedora: ARMv7: build for 16 CPUs. (Peter Robinson)
- Fedora: only enable DEBUG_HIGHMEM on debug kernels (Peter Robinson)
- process_configs.sh: fix find/xargs data flow (Ondrej Mosnacek)
- Fedora config update (Justin M. Forbes)
- fedora: minor arm sound config updates (Peter Robinson)
- Fix trailing white space in redhat/configs/fedora/generic/CONFIG_SND_INTEL_BYT_PREFER_SOF (Justin M. Forbes)
- Add a redhat/rebase-notes.txt file (Hans de Goede)
- Turn on SND_INTEL_BYT_PREFER_SOF for Fedora (Hans de Goede)
- ALSA: hda: intel-dsp-config: Add SND_INTEL_BYT_PREFER_SOF Kconfig option (Hans de Goede) [1924101]
- CI: Drop MR ID from the name variable (Veronika Kabatova)
- redhat: add DUP and kpatch certificates to system trusted keys for RHEL build (Herton R. Krzesinski)
- The comments in CONFIG_USB_RTL8153_ECM actually turn off CONFIG_USB_RTL8152 (Justin M. Forbes)
- Update CKI pipeline project (Veronika Kabatova)
- Turn off additional KASAN options for Fedora (Justin M. Forbes)
- Rename the master branch to rawhide for Fedora (Justin M. Forbes)
- Makefile targets for packit integration (Ben Crocker)
- Turn off KASAN for rawhide debug builds (Justin M. Forbes)
- New configs in arch/arm64 (Justin Forbes)
- Remove deprecated Intel MIC config options (Peter Robinson)
- redhat: replace inline awk script with genlog.py call (Herton R. Krzesinski)
- redhat: add genlog.py script (Herton R. Krzesinski)
- kernel.spec.template - fix use_vdso usage (Ben Crocker)
- redhat: remove remaining references of CONFIG_RH_DISABLE_DEPRECATED (Herton R. Krzesinski)
- .gitignore: fix previous mismerge with "HEAD line" (Herton R. Krzesinski)
- Turn off vdso_install for ppc (Justin M. Forbes)
- Remove bpf-helpers.7 from bpftool package (Jiri Olsa)
- New configs in lib/Kconfig.debug (Fedora Kernel Team)
- Turn off CONFIG_VIRTIO_CONSOLE for s390x zfcpdump (Justin M. Forbes)
- New configs in drivers/clk (Justin M. Forbes)
- Keep VIRTIO_CONSOLE on s390x available. (Jakub Čajka)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- Fedora 5.11 config updates part 4 (Justin M. Forbes)
- Fedora 5.11 config updates part 3 (Justin M. Forbes)
- Fedora 5.11 config updates part 2 (Justin M. Forbes)
- Update internal (test) module list from RHEL-8 (Joe Lawrence) [1915073]
- Fix USB_XHCI_PCI regression (Justin M. Forbes)
- fedora: fixes for ARMv7 build issue by disabling HIGHPTE (Peter Robinson)
- all: s390x: Increase CONFIG_PCI_NR_FUNCTIONS to 512 (#1888735) (Dan Horák)
- Fedora 5.11 configs pt 1 (Justin M. Forbes)
- redhat: avoid conflict with mod-blacklist.sh and released_kernel defined (Herton R. Krzesinski)
- redhat: handle certificate files conditionally as done for src.rpm (Herton R. Krzesinski)
- specfile: add %%{?_smp_mflags} to "make headers_install" in tools/testing/selftests (Denys Vlasenko)
- specfile: add %%{?_smp_mflags} to "make samples/bpf/" (Denys Vlasenko)
- Run MR testing in CKI pipeline (Veronika Kabatova)
- Reword comment (Nicolas Chauvet)
- Add with_cross_arm conditional (Nicolas Chauvet)
- Redefines __strip if with_cross (Nicolas Chauvet)
- fedora: only enable ACPI_CONFIGFS, ACPI_CUSTOM_METHOD in debug kernels (Peter Robinson)
- fedora: User the same EFI_CUSTOM_SSDT_OVERLAYS as ARK (Peter Robinson)
- all: all arches/kernels enable the same DMI options (Peter Robinson)
- all: move SENSORS_ACPI_POWER to common/generic (Peter Robinson)
- fedora: PCIE_HISI_ERR is already in common (Peter Robinson)
- all: all ACPI platforms enable ATA_ACPI so move it to common (Peter Robinson)
- all: x86: move shared x86 acpi config options to generic (Peter Robinson)
- All: x86: Move ACPI_VIDEO to common/x86 (Peter Robinson)
- All: x86: Enable ACPI_DPTF (Intel DPTF) (Peter Robinson)
- All: enable ACPI_BGRT for all ACPI platforms. (Peter Robinson)
- All: Only build ACPI_EC_DEBUGFS for debug kernels (Peter Robinson)
- All: Disable Intel Classmate PC ACPI_CMPC option (Peter Robinson)
- cleanup: ACPI_PROCFS_POWER was removed upstream (Peter Robinson)
- All: ACPI: De-dupe the ACPI options that are the same across ark/fedora on x86/arm (Peter Robinson)
- Enable the vkms module in Fedora (Jeremy Cline)
- Revert "Merge branch 'revert-29a48502' into 'os-build'" (Justin Forbes)
- Fedora: arm updates for 5.11 and general cross Fedora cleanups (Peter Robinson)
- Add gcc-c++ to BuildRequires (Justin M. Forbes)
- gcc-plugins: fix gcc 11 indigestion with plugins... (Valdis Klētnieks)
- Update CONFIG_KASAN_HW_TAGS (Justin M. Forbes)
- fedora: arm: move generic power off/reset to all arm (Peter Robinson)
- fedora: ARMv7: build in DEVFREQ_GOV_SIMPLE_ONDEMAND until I work out why it's changed (Peter Robinson)
- fedora: cleanup joystick_adc (Peter Robinson)
- fedora: update some display options (Peter Robinson)
- fedora: arm: enable TI PRU options (Peter Robinson)
- fedora: arm: minor exynos plaform updates (Peter Robinson)
- arm: SoC: disable Toshiba Visconti SoC (Peter Robinson)
- common: disable ARCH_BCM4908 (NFC) (Peter Robinson)
- fedora: minor arm config updates (Peter Robinson)
- fedora: enable Tegra 234 SoC (Peter Robinson)
- fedora: arm: enable new Hikey 3xx options (Peter Robinson)
- Fedora: USB updates (Peter Robinson)
- fedora: enable the GNSS receiver subsystem (Peter Robinson)
- Remove POWER_AVS as no longer upstream (Peter Robinson)
- Cleanup RESET_RASPBERRYPI (Peter Robinson)
- Cleanup GPIO_CDEV_V1 options. (Peter Robinson)
- fedora: arm crypto updates (Peter Robinson)
- Revert "Merge branch 'ark-enable-structleak' into 'os-build'" (Justin Forbes)
- CONFIG_KASAN_HW_TAGS for aarch64 (Justin M. Forbes)
- Fix up bad merge with efi: generalize efi_get_secureboot (Justin M. Forbes)
- Fedora: cleanup PCMCIA configs, move to x86 (Peter Robinson)
- New configs in drivers/rtc (Fedora Kernel Team)
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK_BYREF_ALL (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_GCC_PLUGINS on ARK (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_KASAN on Fedora (Josh Poimboeuf) [1856176]
- New configs in init/Kconfig (Fedora Kernel Team)
- build_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- genspec.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- mod-blacklist.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Enable Speakup accessibility driver (Justin M. Forbes)
- New configs in init/Kconfig (Fedora Kernel Team)
- Fix fedora config mismatch due to dep changes (Justin M. Forbes)
- New configs in drivers/crypto (Jeremy Cline)
- Remove duplicate ENERGY_MODEL configs (Peter Robinson)
- This is selected by PCIE_QCOM so must match (Justin M. Forbes)
- drop unused BACKLIGHT_GENERIC (Peter Robinson)
- Remove cp instruction already handled in instruction below. (Paulo E. Castro)
- Add all the dependencies gleaned from running `make prepare` on a bloated devel kernel. (Paulo E. Castro)
- Add tools to path mangling script. (Paulo E. Castro)
- Remove duplicate cp statement which is also not specific to x86. (Paulo E. Castro)
- Correct orc_types failure whilst running `make prepare` https://bugzilla.redhat.com/show_bug.cgi?id=1882854 (Paulo E. Castro)
- redhat: ark: enable CONFIG_IKHEADERS (Jiri Olsa)
- Add missing '$' sign to (GIT) in redhat/Makefile (Augusto Caringi)
- Remove filterdiff and use native git instead (Don Zickus)
- New configs in net/sched (Justin M. Forbes)
- New configs in drivers/mfd (CKI@GitLab)
- New configs in drivers/mfd (Fedora Kernel Team)
- New configs in drivers/firmware (Fedora Kernel Team)
- Temporarily backout parallel xz script (Justin M. Forbes)
- redhat: explicitly disable CONFIG_IMA_APPRAISE_SIGNED_INIT (Bruno Meneguele)
- redhat: enable CONFIG_EVM_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM_ATTR_FSUUID on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM in all arches and flavors (Bruno Meneguele)
- redhat: enable CONFIG_IMA_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: set CONFIG_IMA_DEFAULT_HASH to SHA256 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT (Bruno Meneguele)
- redhat: enable CONFIG_IMA_READ_POLICY on ARK (Bruno Meneguele)
- redhat: set default IMA template for all ARK arches (Bruno Meneguele)
- redhat: enable CONFIG_IMA_DEFAULT_HASH_SHA256 for all flavors (Bruno Meneguele)
- redhat: disable CONFIG_IMA_DEFAULT_HASH_SHA1 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_ARCH_POLICY for ppc and x86 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_MODSIG (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_BOOTPARAM (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE (Bruno Meneguele)
- redhat: enable CONFIG_INTEGRITY for aarch64 (Bruno Meneguele)
- kernel: Update some missing KASAN/KCSAN options (Jeremy Linton)
- kernel: Enable coresight on aarch64 (Jeremy Linton)
- Update CONFIG_INET6_ESPINTCP (Justin Forbes)
- New configs in net/ipv6 (Justin M. Forbes)
- fedora: move CONFIG_RTC_NVMEM options from ark to common (Peter Robinson)
- configs: Enable CONFIG_DEBUG_INFO_BTF (Don Zickus)
- fedora: some minor arm audio config tweaks (Peter Robinson)
- Ship xpad with default modules on Fedora and RHEL (Bastien Nocera)
- Fedora: Only enable legacy serial/game port joysticks on x86 (Peter Robinson)
- Fedora: Enable the options required for the Librem 5 Phone (Peter Robinson)
- Fedora config update (Justin M. Forbes)
- Fedora config change because CONFIG_FSL_DPAA2_ETH now selects CONFIG_FSL_XGMAC_MDIO (Justin M. Forbes)
- redhat: generic  enable CONFIG_INET_MPTCP_DIAG (Davide Caratti)
- Fedora config update (Justin M. Forbes)
- Enable NANDSIM for Fedora (Justin M. Forbes)
- Re-enable CONFIG_ACPI_TABLE_UPGRADE for Fedora since upstream disables this if secureboot is active (Justin M. Forbes)
- Ath11k related config updates (Justin M. Forbes)
- Fedora config updates for ath11k (Justin M. Forbes)
- Turn on ATH11K for Fedora (Justin M. Forbes)
- redhat: enable CONFIG_INTEL_IOMMU_SVM (Jerry Snitselaar)
- More Fedora config fixes (Justin M. Forbes)
- Fedora 5.10 config updates (Justin M. Forbes)
- Fedora 5.10 configs round 1 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Allow kernel-tools to build without selftests (Don Zickus)
- Allow building of kernel-tools standalone (Don Zickus)
- redhat: ark: disable CONFIG_NET_ACT_CTINFO (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_TEQL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_SFB (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_QFQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PLUG (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PIE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_MULTIQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_HHF (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DSMARK (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DRR (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CODEL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CHOKE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CBQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_ATM (Davide Caratti)
- redhat: ark: disable CONFIG_NET_EMATCH and sub-targets (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_TCINDEX (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP6 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_ROUTE4 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_BASIC (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SKBMOD (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SIMP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_NAT (Davide Caratti)
- arm64/defconfig: Enable CONFIG_KEXEC_FILE (Bhupesh Sharma) [1821565]
- redhat/configs: Cleanup CONFIG_CRYPTO_SHA512 (Prarit Bhargava)
- New configs in drivers/mfd (Fedora Kernel Team)
- Fix LTO issues with kernel-tools (Don Zickus)
- Point pathfix to the new location for gen_compile_commands.py (Justin M. Forbes)
- Filter out LTO build options from the perl ccopts (Justin M. Forbes)
- configs: Disable CONFIG_SECURITY_SELINUX_DISABLE (Ondrej Mosnacek)
- Fix up a merge issue with rxe.c (Justin M. Forbes)
- [Automatic] Handle config dependency changes (Don Zickus)
- configs/iommu: Add config comment to empty CONFIG_SUN50I_IOMMU file (Jerry Snitselaar)
- New configs in kernel/trace (Fedora Kernel Team)
- Fix Fedora config locations (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- configs: enable CONFIG_CRYPTO_CTS=y so cts(cbc(aes)) is available in FIPS mode (Vladis Dronov) [1855161]
- Partial revert: Add master merge check (Don Zickus)
- Update Maintainers doc to reflect workflow changes (Don Zickus)
- WIP: redhat/docs: Update documentation for single branch workflow (Prarit Bhargava)
- Add CONFIG_ARM64_MTE which is not picked up by the config scripts for some reason (Justin M. Forbes)
- Disable Speakup synth DECEXT (Justin M. Forbes)
- Enable Speakup for Fedora since it is out of staging (Justin M. Forbes)
- Modify patchlist changelog output (Don Zickus)
- process_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- generate_all_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- redhat/self-test: Initial commit (Ben Crocker)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Fixes "acpi: prefer booting with ACPI over DTS" to be RHEL only (Peter Robinson)
- arch/x86: Remove vendor specific CPU ID checks (Prarit Bhargava)
- redhat: Replace hardware.redhat.com link in Unsupported message (Prarit Bhargava) [1810301]
- x86: Fix compile issues with rh_check_supported() (Don Zickus)
- e1000e: bump up timeout to wait when ME un-configure ULP mode (Aaron Ma)
- drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation (Icenowy Zheng)
- drm: panel: add Xingbangda XBD599 panel (Icenowy Zheng)
- dt-bindings: panel: add binding for Xingbangda XBD599 panel (Icenowy Zheng)
- ARM: fix __get_user_check() in case uaccess_* calls are not inlined (Masahiro Yamada)
- mm/kmemleak: skip late_init if not skip disable (Murphy Zhou)
- KEYS: Make use of platform keyring for module signature verify (Robert Holmes)
- Drop that for now (Laura Abbott)
- Input: rmi4 - remove the need for artificial IRQ in case of HID (Benjamin Tissoires)
- ARM: tegra: usb no reset (Peter Robinson)
- arm: make CONFIG_HIGHPTE optional without CONFIG_EXPERT (Jon Masters)
- redhat: rh_kabi: deduplication friendly structs (Jiri Benc)
- redhat: rh_kabi add a comment with warning about RH_KABI_EXCLUDE usage (Jiri Benc)
- redhat: rh_kabi: introduce RH_KABI_EXTEND_WITH_SIZE (Jiri Benc)
- redhat: rh_kabi: Indirect EXTEND macros so nesting of other macros will resolve. (Don Dutile)
- redhat: rh_kabi: Fix RH_KABI_SET_SIZE to use dereference operator (Tony Camuso)
- redhat: rh_kabi: Add macros to size and extend structs (Prarit Bhargava)
- Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy)
- mptsas: pci-id table changes (Laura Abbott)
- mptsas: Taint kernel if mptsas is loaded (Laura Abbott)
- mptspi: pci-id table changes (Laura Abbott)
- qla2xxx: Remove PCI IDs of deprecated adapter (Jeremy Cline)
- be2iscsi: remove unsupported device IDs (Chris Leech)
- mptspi: Taint kernel if mptspi is loaded (Laura Abbott)
- hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek)
- qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis)
- aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta)
- megaraid_sas: remove deprecated pci-ids (Tomas Henzl)
- mpt*: remove certain deprecated pci-ids (Jeremy Cline)
- kernel: add SUPPORT_REMOVED kernel taint (Tomas Henzl)
- Rename RH_DISABLE_DEPRECATED to RHEL_DIFFERENCES (Don Zickus)
- Add option of 13 for FORCE_MAX_ZONEORDER (Peter Robinson)
- s390: Lock down the kernel when the IPL secure flag is set (Jeremy Cline)
- efi: Lock down the kernel if booted in secure boot mode (David Howells)
- efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (David Howells)
- security: lockdown: expose a hook to lock the kernel down (Jeremy Cline)
- Make get_cert_list() use efi_status_to_str() to print error messages. (Peter Jones)
- Add efi_status_to_str() and rework efi_status_to_err(). (Peter Jones)
- Add support for deprecating processors (Laura Abbott) [1565717 1595918 1609604 1610493]
- arm: aarch64: Drop the EXPERT setting from ARM64_FORCE_52BIT (Jeremy Cline)
- iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- rh_kabi: introduce RH_KABI_EXCLUDE (Jakub Racek)
- ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [1670017]
- IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- scsi: smartpqi: add inspur advantech ids (Don Brace)
- ice: mark driver as tech-preview (Jonathan Toppins)
- kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- add pci_hw_vendor_status() (Maurizio Lombardi)
- ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter)
- Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter)
- bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- tags.sh: Ignore redhat/rpm (Jeremy Cline)
- put RHEL info into generated headers (Laura Abbott) [1663728]
- kdump: add support for crashkernel=auto (Jeremy Cline)
- kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- modules: add rhelversion MODULE_INFO tag (Laura Abbott)
- ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- Add Red Hat tainting (Laura Abbott) [1565704]
- Introduce CONFIG_RH_DISABLE_DEPRECATED (Laura Abbott)
- Stop merging ark-patches for release (Don Zickus)
- Fix path location for ark-update-configs.sh (Don Zickus)
- Combine Red Hat patches into single patch (Don Zickus)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- New configs in drivers/misc (Jeremy Cline)
- New configs in drivers/net/wireless (Justin M. Forbes)
- New configs in drivers/phy (Fedora Kernel Team)
- New configs in drivers/tty (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)
- Updated changelog for the release based on 22fbc037cd32 (Fedora Kernel Team)
- Updated changelog for the release based on d3d45f8220d6 (Fedora Kernel Team)
- Updated changelog for the release based on 472e5b056f00 (Fedora Kernel Team)
- Set SquashFS decompression options for all flavors to match RHEL (Bohdan Khomutskyi)
- Updated changelog for the release based on 60e720931556 (Fedora Kernel Team)
- configs: Enable CONFIG_ENERGY_MODEL (Phil Auld)
- New configs in drivers/pinctrl (Fedora Kernel Team)
- Update CONFIG_THERMAL_NETLINK (Justin Forbes)
- Updated changelog for the release based on 02de58b24d2e (Fedora Kernel Team)
- Updated changelog for the release based on fb0155a09b02 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)
- Separate merge-upstream and release stages (Don Zickus)
- Re-enable CONFIG_IR_SERIAL on Fedora (Prarit Bhargava)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)
- Updated changelog for the release based on a1bffa48745a (Fedora Kernel Team)
- Create Patchlist.changelog file (Don Zickus)
- Updated changelog for the release based on 7c7ec3226f5f (Fedora Kernel Team)
- Filter out upstream commits from changelog (Don Zickus)
- Merge Upstream script fixes (Don Zickus)
- Updated changelog for the release based on 171d4ff79f96 (Fedora Kernel Team)
- Updated changelog for the release based on c9c9e6a49f89 (Fedora Kernel Team)
- Updated changelog for the release based on 805c6d3c1921 (Fedora Kernel Team)
- Updated changelog for the release based on 98477740630f (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc6 (Fedora Kernel Team)
- kernel.spec: Remove kernel-keys directory on rpm erase (Prarit Bhargava)
- Add mlx5_vdpa to module filter for Fedora (Justin M. Forbes)
- Add python3-sphinx_rtd_theme buildreq for docs (Justin M. Forbes)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on fc4f28bb3daf (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc5 (Fedora Kernel Team)
- Updated changelog for the release based on ef2e9a563b0c (Fedora Kernel Team)
- Updated changelog for the release based on 729e3d091984 (Fedora Kernel Team)
- dist-merge-upstream: Checkout known branch for ci scripts (Don Zickus)
- Updated changelog for the release based on 581cb3a26baf (Fedora Kernel Team)
- kernel.spec: don't override upstream compiler flags for ppc64le (Dan Horák)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on v5.9-rc4 (Fedora Kernel Team)
- Updated changelog for the release based on dd9fb9bb3340 (Fedora Kernel Team)
- Updated changelog for the release based on c70672d8d316 (Fedora Kernel Team)
- Fedora confi gupdate (Justin M. Forbes)
- Updated changelog for the release based on 59126901f200 (Fedora Kernel Team)
- mod-sign.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Swap how ark-latest is built (Don Zickus)
- Add extra version bump to os-build branch (Don Zickus)
- dist-release: Avoid needless version bump. (Don Zickus)
- Add dist-fedora-release target (Don Zickus)
- Remove redundant code in dist-release (Don Zickus)
- Makefile.common rename TAG to _TAG (Don Zickus)
- Updated changelog for the release based on fc3abb53250a (Fedora Kernel Team)
- Fedora config change (Justin M. Forbes)
- Updated changelog for the release based on 9c7d619be5a0 (Fedora Kernel Team)
- Updated changelog for the release based on b51594df17d0 (Fedora Kernel Team)
- Fedora filter update (Justin M. Forbes)
- Config update for Fedora (Justin M. Forbes)
- Updated changelog for the release based on v5.9-rc3 (Fedora Kernel Team)
- Updated changelog for the release based on 1127b219ce94 (Fedora Kernel Team)
- Updated changelog for the release based on 4d41ead6ead9 (Fedora Kernel Team)
- Updated changelog for the release based on 15bc20c6af4c (Fedora Kernel Team)
- Updated changelog for the release based on 2ac69819ba9e (Fedora Kernel Team)
- Updated changelog for the release based on 6a9dc5fd6170 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc2 (Fedora Kernel Team)
- Updated changelog for the release based on c3d8f220d012 (Fedora Kernel Team)
- Updated changelog for the release based on f873db9acd3c (Fedora Kernel Team)
- Updated changelog for the release based on da2968ff879b (Fedora Kernel Team)
- enable PROTECTED_VIRTUALIZATION_GUEST for all s390x kernels (Dan Horák)
- Updated changelog for the release based on 18445bf405cb (Fedora Kernel Team)
- redhat: ark: enable CONFIG_NET_SCH_TAPRIO (Davide Caratti)
- redhat: ark: enable CONFIG_NET_SCH_ETF (Davide Caratti)
- More Fedora config updates (Justin M. Forbes)
- New config deps (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on 06a4ec1d9dc6 (Fedora Kernel Team)
- First half of config updates for Fedora (Justin M. Forbes)
- Updates for Fedora arm architectures for the 5.9 window (Peter Robinson)
- Add config options that only show up when we prep on arm (Justin M. Forbes)
- Config updates for Fedora (Justin M. Forbes)
- fedora: enable enery model (Peter Robinson)
- Use the configs/generic config for SND_HDA_INTEL everywhere (Peter Robinson)
- Enable ZSTD compression algorithm on all kernels (Peter Robinson)
- Enable ARM_SMCCC_SOC_ID on all aarch64 kernels (Peter Robinson)
- iio: enable LTR-559 light and proximity sensor (Peter Robinson)
- iio: chemical: enable some popular chemical and partical sensors (Peter Robinson)
- More mismatches (Justin M. Forbes)
- Fedora config change due to deps (Justin M. Forbes)
- CONFIG_SND_SOC_MAX98390 is now selected by SND_SOC_INTEL_DA7219_MAX98357A_GENERIC (Justin M. Forbes)
- Config change required for build part 2 (Justin M. Forbes)
- Config change required for build (Justin M. Forbes)
- Revert "Merge branch 'make_configs_fix' into 'os-build'" (Justin Forbes)
- Fedora config update (Justin M. Forbes)
- Add ability to sync upstream through Makefile (Don Zickus)
- Add master merge check (Don Zickus)
- Replace hardcoded values 'os-build' and project id with variables (Don Zickus)
- redhat/Makefile.common: Fix MARKER (Prarit Bhargava)
- gitattributes: Remove unnecesary export restrictions (Prarit Bhargava)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on v5.8 (Fedora Kernel Team)
- Updated changelog for the release based on ac3a0c847296 (Fedora Kernel Team)
- Updated changelog for the release based on 7dc6fd0f3b84 (Fedora Kernel Team)
- Updated changelog for the release based on 417385c47ef7 (Fedora Kernel Team)
- Add new certs for dual signing with boothole (Justin M. Forbes)
- Update secureboot signing for dual keys (Justin M. Forbes)
- Updated changelog for the release based on d3590ebf6f91 (Fedora Kernel Team)
- Updated changelog for the release based on 6ba1b005ffc3 (Fedora Kernel Team)
- fedora: enable LEDS_SGM3140 for arm configs (Peter Robinson)
- Updated changelog for the release based on v5.8-rc7 (Fedora Kernel Team)
- Updated changelog for the release based on 04300d66f0a0 (Fedora Kernel Team)
- Updated changelog for the release based on 23ee3e4e5bd2 (Fedora Kernel Team)
- Enable CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG (Justin M. Forbes)
- Updated changelog for the release based on f37e99aca03f (Fedora Kernel Team)
- redhat/configs: Fix common CONFIGs (Prarit Bhargava)
- redhat/configs: General CONFIG cleanups (Prarit Bhargava)
- redhat/configs: Update & generalize evaluate_configs (Prarit Bhargava)
- Updated changelog for the release based on d15be546031c (Fedora Kernel Team)
- fedora: arm: Update some meson config options (Peter Robinson)
- Updated changelog for the release based on 4fa640dc5230 (Fedora Kernel Team)
- redhat/docs: Add Fedora RPM tagging date (Prarit Bhargava)
- Updated changelog for the release based on 5714ee50bb43 (Fedora Kernel Team)
- Updated changelog for the release based on f932d58abc38 (Fedora Kernel Team)
- Updated changelog for the release based on 6a70f89cc58f (Fedora Kernel Team)
- Updated changelog for the release based on 07a56bb875af (Fedora Kernel Team)
- Updated changelog for the release based on e9919e11e219 (Fedora Kernel Team)
- Update config for renamed panel driver. (Peter Robinson)
- Enable SERIAL_SC16IS7XX for SPI interfaces (Peter Robinson)
- Updated changelog for the release based on dcde237b9b0e (Fedora Kernel Team)
- Updated changelog for the release based on v5.8-rc4 (Fedora Kernel Team)
- s390x-zfcpdump: Handle missing Module.symvers file (Don Zickus)
- Updated changelog for the release based on cd77006e01b3 (Fedora Kernel Team)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on v5.8-rc3 (Fedora Kernel Team)
- Updated changelog for the release based on 8be3a53e18e0 (Fedora Kernel Team)
- redhat/configs: Add .tmp files to .gitignore (Prarit Bhargava)
- disable uncommon TCP congestion control algorithms (Davide Caratti)
- Updated changelog for the release based on dd0d718152e4 (Fedora Kernel Team)
- Add new bpf man pages (Justin M. Forbes)
- Add default option for CONFIG_ARM64_BTI_KERNEL to pending-common so that eln kernels build (Justin M. Forbes)
- redhat/Makefile: Add fedora-configs and rh-configs make targets (Prarit Bhargava)
- Updated changelog for the release based on 625d3449788f (Fedora Kernel Team)
- Updated changelog for the release based on 1b5044021070 (Fedora Kernel Team)
- redhat/configs: Use SHA512 for module signing (Prarit Bhargava)
- genspec.sh: 'touch' empty Patchlist file for single tarball (Don Zickus)
- Updated changelog for the release based on 69119673bd50 (Fedora Kernel Team)
- Updated changelog for the release based on a5dc8300df75 (Fedora Kernel Team)
- Fedora config update for rc1 (Justin M. Forbes)
- Updated changelog for the release based on v5.8-rc1 (Fedora Kernel Team)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on df2fbf5bfa0e (Fedora Kernel Team)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on b791d1bdf921 (Fedora Kernel Team)
- redhat/Makefile.common: fix RPMKSUBLEVEL condition (Ondrej Mosnacek)
- redhat/Makefile: silence KABI tar output (Ondrej Mosnacek)
- One more Fedora config update (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix PATCHLEVEL for merge window (Justin M. Forbes)
- Change ark CONFIG_COMMON_CLK to yes, it is selected already by other options (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- More module filtering for Fedora (Justin M. Forbes)
- Update filters for rnbd in Fedora (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix up module filtering for 5.8 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- More Fedora config work (Justin M. Forbes)
- RTW88BE and CE have been extracted to their own modules (Justin M. Forbes)
- Set CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK for Fedora (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Arm64 Use Branch Target Identification for kernel (Justin M. Forbes)
- Change value of CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix configs for Fedora (Justin M. Forbes)
- Add zero-commit to format-patch options (Justin M. Forbes)
- Copy Makefile.rhelver as a source file rather than a patch (Jeremy Cline)
- Move the sed to clear the patch templating outside of conditionals (Justin M. Forbes)
- Match template format in kernel.spec.template (Justin M. Forbes)
- Break out the Patches into individual files for dist-git (Justin M. Forbes)
- Break the Red Hat patch into individual commits (Jeremy Cline)
- Fix update_scripts.sh unselective pattern sub (David Howells)
- Add cec to the filter overrides (Justin M. Forbes)
- Add overrides to filter-modules.sh (Justin M. Forbes)
- redhat/configs: Enable CONFIG_SMC91X and disable CONFIG_SMC911X (Prarit Bhargava) [1722136]
- Include bpftool-struct_ops man page in the bpftool package (Jeremy Cline)
- Add sharedbuffer_configuration.py to the pathfix.py script (Jeremy Cline)
- Use __make macro instead of make (Tom Stellard)
- Sign off generated configuration patches (Jeremy Cline)
- Drop the static path configuration for the Sphinx docs (Jeremy Cline)
- Updated changelog for the release based on b0c3ba31be3e (CKI@GitLab)
- Updated changelog for the release based on 444fc5cde643 (CKI@GitLab)
- redhat: Add dummy-module kernel module (Prarit Bhargava)
- redhat: enable CONFIG_LWTUNNEL_BPF (Jiri Benc)
- Remove typoed config file aarch64CONFIG_SM_GCC_8150 (Justin M. Forbes)
- Updated changelog for the release based on v5.7-rc7 (CKI@GitLab)
- Updated changelog for the release based on caffb99b6929 (CKI@GitLab)
- Updated changelog for the release based on 444565650a5f (CKI@GitLab)
- Add Documentation back to kernel-devel as it has Kconfig now (Justin M. Forbes)
- Copy distro files rather than moving them (Jeremy Cline)
- kernel.spec: fix 'make scripts' for kernel-devel package (Brian Masney)
- Makefile: correct help text for dist-cross-<arch>-rpms (Brian Masney)
- redhat/Makefile: Fix RHEL8 python warning (Prarit Bhargava)
- redhat: Change Makefile target names to dist- (Prarit Bhargava)
- configs: Disable Serial IR driver (Prarit Bhargava)
- Updated changelog for the release based on 642b151f45dd (CKI@GitLab)
- Updated changelog for the release based on v5.7-rc6 (CKI@GitLab)
- Updated changelog for the release based on 3d1c1e5931ce (CKI@GitLab)
- Updated changelog for the release based on 12bf0b632ed0 (CKI@GitLab)
- Updated changelog for the release based on 1ae7efb38854 (CKI@GitLab)
- Updated changelog for the release based on 24085f70a6e1 (CKI@GitLab)
- Updated changelog for the release based on 152036d1379f (CKI@GitLab)
- Fix "multiple %%files for package kernel-tools" (Pablo Greco)
- Updated changelog for the release based on v5.7-rc5 (CKI@GitLab)
- Updated changelog for the release based on e99332e7b4cd (CKI@GitLab)
- Updated changelog for the release based on d5eeab8d7e26 (CKI@GitLab)
- Introduce a Sphinx documentation project (Jeremy Cline)
- Updated changelog for the release based on 79dede78c057 (CKI@GitLab)
- Build ARK against ELN (Don Zickus)
- Updated changelog for the release based on a811c1fa0a02 (CKI@GitLab)
- Updated changelog for the release based on dc56c5acd850 (CKI@GitLab)
- Updated changelog for the release based on 47cf1b422e60 (CKI@GitLab)
- Updated changelog for the release based on v5.7-rc4 (CKI@GitLab)
- Updated changelog for the release based on f66ed1ebbfde (CKI@GitLab)
- Updated changelog for the release based on 690e2aba7beb (CKI@GitLab)
- Drop the requirement to have a remote called linus (Jeremy Cline)
- Rename 'internal' branch to 'os-build' (Don Zickus)
- Updated changelog for the release based on c45e8bccecaf (CKI@GitLab)
- Updated changelog for the release based on 1d2cc5ac6f66 (CKI@GitLab)
- Only include open merge requests with "Include in Releases" label (Jeremy Cline)
- Package gpio-watch in kernel-tools (Jeremy Cline)
- Exit non-zero if the tag already exists for a release (Jeremy Cline)
- Adjust the changelog update script to not push anything (Jeremy Cline)
- Drop --target noarch from the rh-rpms make target (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- Add a script to generate release tags and branches (Jeremy Cline)
- Set CONFIG_VDPA for fedora (Justin M. Forbes)
- Add a README to the dist-git repository (Jeremy Cline)
- Provide defaults in ark-rebase-patches.sh (Jeremy Cline)
- Default ark-rebase-patches.sh to not report issues (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- Drop DIST from release commits and tags (Jeremy Cline)
- Place the buildid before the dist in the release (Jeremy Cline)
- Sync up with Fedora arm configuration prior to merging (Jeremy Cline)
- Disable CONFIG_PROTECTED_VIRTUALIZATION_GUEST for zfcpdump (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Add RHMAINTAINERS file and supporting conf (Don Zickus)
- Add a script to test if all commits are signed off (Jeremy Cline)
- Fix make rh-configs-arch (Don Zickus)
- Drop RH_FEDORA in favor of the now-merged RHEL_DIFFERENCES (Jeremy Cline)
- Sync up Fedora configs from the first week of the merge window (Jeremy Cline)
- Migrate blacklisting floppy.ko to mod-blacklist.sh (Don Zickus)
- kernel packaging: Combine mod-blacklist.sh and mod-extra-blacklist.sh (Don Zickus)
- kernel packaging: Fix extra namespace collision (Don Zickus)
- mod-extra.sh: Rename to mod-blacklist.sh (Don Zickus)
- mod-extra.sh: Make file generic (Don Zickus)
- Fix a painfully obvious YAML syntax error in .gitlab-ci.yml (Jeremy Cline)
- Add in armv7hl kernel header support (Don Zickus)
- Disable all BuildKernel commands when only building headers (Don Zickus)
- Updated changelog (CKI@GitLab)
- Drop any gitlab-ci patches from ark-patches (Jeremy Cline)
- Build the srpm for internal branch CI using the vanilla tree (Jeremy Cline)
- Pull in the latest ARM configurations for Fedora (Jeremy Cline)
- Fix xz memory usage issue (Neil Horman)
- Use ark-latest instead of master for update script (Jeremy Cline)
- Move the CI jobs back into the ARK repository (Jeremy Cline)
- Revert "[redhat] Apply a second patch set in Fedora build roots" (Jeremy Cline)
- Sync up ARK's Fedora config with the dist-git repository (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Pull in the latest configuration changes from Fedora (Jeremy Cline)
- configs: enable CONFIG_NET_SCH_CBS (Marcelo Ricardo Leitner)
- Updated changelog (CKI@GitLab)
- Drop configuration options in fedora/ that no longer exist (Jeremy Cline)
- Set RH_FEDORA for ARK and Fedora (Jeremy Cline)
- redhat/kernel.spec: Include the release in the kernel COPYING file (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- redhat/kernel.spec: add scripts/jobserver-exec to py3_shbang_opts list (Jeremy Cline)
- redhat/kernel.spec: package bpftool-gen man page (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- distgit-changelog: handle multiple y-stream BZ numbers (Bruno Meneguele)
- redhat/kernel.spec: remove all inline comments (Bruno Meneguele)
- redhat/genspec: awk unknown whitespace regex pattern (Bruno Meneguele)
- Improve the readability of gen_config_patches.sh (Jeremy Cline)
- Fix some awkward edge cases in gen_config_patches.sh (Jeremy Cline)
- Updated changelog (Jeremy Cline)
- Update the CI environment to use Fedora 31 (Jeremy Cline)
- Revert "Turn off CONFIG_AX25" (Laura Abbott)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- redhat: drop whitespace from with_gcov macro (Jan Stancek)
- configs: Enable CONFIG_KEY_DH_OPERATIONS on ARK (Ondrej Mosnacek)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- configs: Adjust CONFIG_MPLS_ROUTING and CONFIG_MPLS_IPTUNNEL (Laura Abbott)
- New configs in lib/crypto (Jeremy Cline)
- New configs in drivers/char (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Turn on BLAKE2B for Fedora (Jeremy Cline)
- kernel.spec.template: Clean up stray *.h.s files (Laura Abbott)
- Build the SRPM in the CI job (Jeremy Cline)
- New configs in net/tls (Jeremy Cline)
- New configs in net/tipc (Jeremy Cline)
- New configs in lib/kunit (Jeremy Cline)
- Fix up released_kernel case (Laura Abbott)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- New configs in drivers/ptp (Jeremy Cline)
- New configs in drivers/nvme (Jeremy Cline)
- New configs in drivers/net/phy (Jeremy Cline)
- New configs in arch/arm64 (Jeremy Cline)
- New configs in drivers/crypto (Jeremy Cline)
- New configs in crypto/Kconfig (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Add label so the Gitlab to email bridge ignores the changelog (Jeremy Cline)
- Temporarily switch TUNE_DEFAULT to y (Jeremy Cline)
- Run config test for merge requests and internal (Jeremy Cline)
- Turn off CONFIG_AX25 (Laura Abbott)
- Add missing licensedir line (Laura Abbott)
- Updated changelog (CKI@GitLab)
- redhat/scripts: Remove redhat/scripts/rh_get_maintainer.pl (Prarit Bhargava)
- configs: Take CONFIG_DEFAULT_MMAP_MIN_ADDR from Fedra (Laura Abbott)
- configs: Turn off ISDN (Laura Abbott)
- Add a script to generate configuration patches (Laura Abbott)
- Introduce rh-configs-commit (Laura Abbott)
- kernel-packaging: Remove kernel files from kernel-modules-extra package (Prarit Bhargava)
- Updated changelog (CKI@GitLab)
- configs: Enable CONFIG_DEBUG_WX (Laura Abbott)
- configs: Disable wireless USB (Laura Abbott)
- Clean up some temporary config files (Laura Abbott)
- configs: New config in drivers/gpu for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/powerpc for v5.4-rc1 (Jeremy Cline)
- configs: New config in crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/usb for v5.4-rc1 (Jeremy Cline)
- AUTOMATIC: New configs (Jeremy Cline)
- Skip ksamples for bpf, they are broken (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- configs: New config in fs/erofs for v5.4-rc1 (Jeremy Cline)
- configs: New config in mm for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/md for v5.4-rc1 (Jeremy Cline)
- configs: New config in init for v5.4-rc1 (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- configs: New config in fs/fuse for v5.4-rc1 (Jeremy Cline)
- merge.pl: Avoid comments but do not skip them (Don Zickus)
- configs: New config in drivers/net/ethernet/pensando for v5.4-rc1 (Jeremy Cline)
- Update a comment about what released kernel means (Laura Abbott)
- Provide both Fedora and RHEL files in the SRPM (Laura Abbott)
- kernel.spec.template: Trim EXTRAVERSION in the Makefile (Laura Abbott)
- kernel.spec.template: Add macros for building with nopatches (Laura Abbott)
- kernel.spec.template: Add some macros for Fedora differences (Laura Abbott)
- kernel.spec.template: Consolodate the options (Laura Abbott)
- configs: Add pending direcory to Fedora (Laura Abbott)
- kernel.spec.template: Don't run hardlink if rpm-ostree is in use (Laura Abbott)
- configs: New config in net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/phy for v5.4-rc1 (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- configs: Increase x86_64 NR_UARTS to 64 (Prarit Bhargava) [1730649]
- configs: turn on ARM64_FORCE_52BIT for debug builds (Jeremy Cline)
- kernel.spec.template: Tweak the python3 mangling (Laura Abbott)
- kernel.spec.template: Add --with verbose option (Laura Abbott)
- kernel.spec.template: Switch to using %%install instead of %%__install (Laura Abbott)
- kernel.spec.template: Make the kernel.org URL https (Laura Abbott)
- kernel.spec.template: Update message about secure boot signing (Laura Abbott)
- kernel.spec.template: Move some with flags definitions up (Laura Abbott)
- kernel.spec.template: Update some BuildRequires (Laura Abbott)
- kernel.spec.template: Get rid of %%clean (Laura Abbott)
- configs: New config in drivers/char for v5.4-rc1 (Jeremy Cline)
- configs: New config in net/sched for v5.4-rc1 (Jeremy Cline)
- configs: New config in lib for v5.4-rc1 (Jeremy Cline)
- configs: New config in fs/verity for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/aarch64 for v5.4-rc4 (Jeremy Cline)
- configs: New config in arch/arm64 for v5.4-rc1 (Jeremy Cline)
- Flip off CONFIG_ARM64_VA_BITS_52 so the bundle that turns it on applies (Jeremy Cline)
- Update changelog (Laura Abbott)
- New configuration options for v5.4-rc4 (Jeremy Cline)
- Correctly name tarball for single tarball builds (Laura Abbott)
- configs: New config in drivers/pci for v5.4-rc1 (Jeremy Cline)
- Allow overriding the dist tag on the command line (Laura Abbott)
- Allow scratch branch target to be overridden (Laura Abbott)
- Remove long dead BUILD_DEFAULT_TARGET (Laura Abbott)
- Amend the changelog when rebasing (Laura Abbott)
- configs: New config in drivers/platform for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/pinctrl for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/wireless for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/ethernet/mellanox for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hid for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/dma-buf for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in block for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/cpuidle for v5.4-rc1 (Jeremy Cline)
- redhat: configs: Split CONFIG_CRYPTO_SHA512 (Laura Abbott)
- redhat: Set Fedora options (Laura Abbott)
- Set CRYPTO_SHA3_*_S390 to builtin on zfcpdump (Jeremy Cline)
- configs: New config in drivers/edac for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/firmware for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hwmon for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/iio for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/mmc for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/tty for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/bus for v5.4-rc1 (Jeremy Cline)
- Add option to allow mismatched configs on the command line (Laura Abbott)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/pci for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/soc for v5.4-rc1 (Jeremy Cline)
- gitlab: Add CI job for packaging scripts (Major Hayden)
- Speed up CI with CKI image (Major Hayden)
- Disable e1000 driver in ARK (Neil Horman)
- configs: Fix the pending default for CONFIG_ARM64_VA_BITS_52 (Jeremy Cline)
- configs: Turn on OPTIMIZE_INLINING for everything (Jeremy Cline)
- configs: Set valid pending defaults for CRYPTO_ESSIV (Jeremy Cline)
- Add an initial CI configuration for the internal branch (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- Pull the RHEL version defines out of the Makefile (Jeremy Cline)
- Sync up the ARK build scripts (Jeremy Cline)
- Sync up the Fedora Rawhide configs (Jeremy Cline)
- Sync up the ARK config files (Jeremy Cline)
- configs: Adjust CONFIG_FORCE_MAX_ZONEORDER for Fedora (Laura Abbott)
- configs: Add README for some other arches (Laura Abbott)
- configs: Sync up Fedora configs (Laura Abbott)
- [initial commit] Add structure for building with git (Laura Abbott)
- [initial commit] Add Red Hat variables in the top level makefile (Laura Abbott)
- [initial commit] Red Hat gitignore and attributes (Laura Abbott)
- [initial commit] Add changelog (Laura Abbott)
- [initial commit] Add makefile (Laura Abbott)
- [initial commit] Add files for generating the kernel.spec (Laura Abbott)
- [initial commit] Add rpm directory (Laura Abbott)
- [initial commit] Add files for packaging (Laura Abbott)
- [initial commit] Add kabi files (Laura Abbott)
- [initial commit] Add scripts (Laura Abbott)
- [initial commit] Add configs (Laura Abbott)
- [initial commit] Add Makefiles (Laura Abbott)

* Tue Apr 27 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-1]
- Reset the counter as we start the 5.13 merge window (Justin M. Forbes)

* Mon Apr 26 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-197]
- Create ark-latest branch last for CI scripts (Don Zickus)

* Wed Apr 21 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc8.20210421git7af08140979a.193]
- Replace /usr/libexec/platform-python with /usr/bin/python3 (David Ward)

* Tue Apr 20 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc8.20210420git7af08140979a.192]
- Turn off ADI_AXI_ADC and AD9467 which now require CONFIG_OF (Justin M. Forbes)
- Export ark infrastructure files (Don Zickus)
- docs: Update docs to reflect newer workflow. (Don Zickus)
- Use upstream/master for merge-base with fallback to master (Don Zickus)
- Fedora: Turn off the SND_INTEL_BYT_PREFER_SOF option (Hans de Goede)

* Mon Apr 19 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc8.191]
- filter-modules.sh.fedora: clean up "netprots" (Paul Bolle)
- filter-modules.sh.fedora: clean up "scsidrvs" (Paul Bolle)
- filter-*.sh.fedora: clean up "ethdrvs" (Paul Bolle)
- filter-*.sh.fedora: clean up "driverdirs" (Paul Bolle)
- filter-*.sh.fedora: remove incorrect entries (Paul Bolle)
- filter-*.sh.fedora: clean up "singlemods" (Paul Bolle)
- filter-modules.sh.fedora: drop unused list "iiodrvs" (Paul Bolle)

* Fri Apr 16 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc7.20210416git7e25f40eab52.190]
- Update mod-internal to fix depmod issue (Nico Pache)
- Turn on CONFIG_VDPA_SIM_NET (rhbz 1942343) (Justin M. Forbes)
- New configs in drivers/power (Fedora Kernel Team)
- Turn on CONFIG_NOUVEAU_DEBUG_PUSH for debug configs (Justin M. Forbes)
- Turn off KFENCE sampling by default for Fedora (Justin M. Forbes)
- Fedora config updates round 2 (Justin M. Forbes)
- New configs in drivers/soc (Jeremy Cline)
- filter-modules.sh: Fix copy/paste error 'input' (Paul Bolle)
- Update module filtering for 5.12 kernels (Justin M. Forbes)
- Fix genlog.py to ensure that comments retain "%%" characters. (Mark Mielke)
- New configs in drivers/leds (Fedora Kernel Team)
- Limit CONFIG_USB_CDNS_SUPPORT to x86_64 and arm in Fedora (David Ward)

* Sat Apr 10 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc6.20210410gitd4961772226d.187]
- Fedora: Enable CHARGER_GPIO on aarch64 too (Peter Robinson)
- Fedora config updates (Justin M. Forbes)
- wireguard: mark as Tech Preview (Hangbin Liu) [1613522]
- configs: enable CONFIG_WIREGUARD in ARK (Hangbin Liu) [1613522]
- Remove duplicate configs acroos fedora, ark and common (Don Zickus)
- Combine duplicate configs across ark and fedora into common (Don Zickus)

* Wed Apr 07 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc6.20210407git2d743660786e.185]
- common/ark: cleanup and unify the parport configs (Peter Robinson)
- iommu/vt-d: enable INTEL_IDXD_SVM for both fedora and rhel (Jerry Snitselaar)
- REDHAT: coresight: etm4x: Disable coresight on HPE Apollo 70 (Jeremy Linton)

* Wed Mar 31 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc5.20210331git2bb25b3a748a.181]
- configs/common/generic: disable CONFIG_SLAB_MERGE_DEFAULT (Rafael Aquini)
- Remove _legacy_common_support (Justin M. Forbes)
- redhat/mod-blacklist.sh: Fix floppy blacklisting (Hans de Goede)

* Fri Mar 26 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc4.20210326gitdb24726bfefa.178]
- New configs in fs/pstore (CKI@GitLab)

* Thu Mar 25 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc4.20210325gite138138003eb.177]
- New configs in arch/powerpc (Fedora Kernel Team)
- configs: enable BPF LSM on Fedora and ARK (Ondrej Mosnacek)
- configs: clean up LSM configs (Ondrej Mosnacek)

* Wed Mar 24 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc4.20210324git7acac4b3196c.176]
- New configs in drivers/platform (CKI@GitLab)
- New configs in drivers/firmware (CKI@GitLab)
- New configs in drivers/mailbox (Fedora Kernel Team)
- New configs in drivers/net/phy (Justin M. Forbes)
- Update CONFIG_DM_MULTIPATH_IOA (Augusto Caringi)
- New configs in mm/Kconfig (CKI@GitLab)
- New configs in arch/powerpc (Jeremy Cline)
- New configs in arch/powerpc (Jeremy Cline)
- New configs in drivers/input (Fedora Kernel Team)
- New configs in net/bluetooth (Justin M. Forbes)
- New configs in drivers/clk (Fedora Kernel Team)
- New configs in init/Kconfig (Jeremy Cline)
- redhat: allow running fedora-configs and rh-configs targets outside of redhat/ (Herton R. Krzesinski)
- all: unify the disable of goldfish (android emulation platform) (Peter Robinson)
- common: minor cleanup/de-dupe of dma/dmabuf debug configs (Peter Robinson)
- common/ark: these drivers/arches were removed in 5.12 (Peter Robinson)
- common: unset serial mouse for general config (Peter Robinson)
- Correct kernel-devel make prepare build for 5.12. (Paulo E. Castro)
- redhat: add initial support for centos stream dist-git sync on Makefiles (Herton R. Krzesinski)
- redhat/configs: Enable CONFIG_SCHED_STACK_END_CHECK for Fedora and ARK (Josh Poimboeuf) [1856174]

* Sat Mar 20 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc3.20210320git1c273e10bc0c.173]
- CONFIG_VFIO now selects IOMMU_API instead of depending on it, causing several config mismatches for the zfcpdump kernel (Justin M. Forbes)

* Thu Mar 18 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc3.20210318git6417f03132a6.171]
- Turn off weak-modules for Fedora (Justin M. Forbes)
- redhat: enable CONFIG_FW_LOADER_COMPRESS for ARK (Herton R. Krzesinski) [1939095]

* Mon Mar 15 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc3.170]
- Fedora: filters: update to move dfl-emif to modules (Peter Robinson)
- drop duplicate DEVFREQ_GOV_SIMPLE_ONDEMAND config (Peter Robinson)
- efi: The EFI_VARS is legacy and now x86 only (Peter Robinson)
- common: enable RTC_SYSTOHC to supplement update_persistent_clock64 (Peter Robinson)
- generic: arm: enable SCMI for all options (Peter Robinson)
- fedora: the PCH_CAN driver is x86-32 only (Peter Robinson)
- common: disable legacy CAN device support (Peter Robinson)
- common: Enable Microchip MCP251x/MCP251xFD CAN controllers (Peter Robinson)
- common: Bosch MCAN support for Intel Elkhart Lake (Peter Robinson)
- common: enable CAN_PEAK_PCIEFD PCI-E driver (Peter Robinson)
- common: disable CAN_PEAK_PCIEC PCAN-ExpressCard (Peter Robinson)
- common: enable common CAN layer 2 protocols (Peter Robinson)
- ark: disable CAN_LEDS option (Peter Robinson)

* Wed Mar 10 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc2.20210310git05a59d79793d.167]
- Fedora: Turn on SND_SOC_INTEL_SKYLAKE_HDAUDIO_CODEC option (Hans de Goede)
- Fedora: enable modules for surface devices (Dave Olsthoorn)
- Turn on SND_SOC_INTEL_SOUNDWIRE_SOF_MACH for Fedora again (Justin M. Forbes)
- common: fix WM8804 codec dependencies (Peter Robinson)
- Build SERIO_SERPORT as a module (Peter Robinson)
- input: touchscreen: move ELO and Wacom serial touchscreens to x86 (Peter Robinson)
- Sync serio touchscreens for non x86 architectures to the same as ARK (Peter Robinson)
- Only enable SERIO_LIBPS2 on x86 (Peter Robinson)
- Only enable PC keyboard controller and associated keyboard on x86 (Peter Robinson)
- Generic: Mouse: Tweak generic serial mouse options (Peter Robinson)
- Only enable PS2 Mouse options on x86 (Peter Robinson)
- Disable bluetooth highspeed by default (Peter Robinson)
- Fedora: A few more general updates for 5.12 window (Peter Robinson)
- Fedora: Updates for 5.12 merge window (Peter Robinson)
- Fedora: remove dead options that were removed upstream (Peter Robinson)
- Revert "mm/kmemleak: skip late_init if not skip disable" (Herton R. Krzesinski)

* Fri Mar 05 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc1.20210305git280d542f6ffa.164]
- Revert "ARM: fix __get_user_check() in case uaccess_* calls are not inlined" (Herton R. Krzesinski)

* Thu Mar 04 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc1.20210304gitf69d02e37a85.163]
- Revert "dt-bindings: panel: add binding for Xingbangda XBD599 panel" (Herton R. Krzesinski)
- redhat: remove CONFIG_DRM_PANEL_XINGBANGDA_XBD599 (Herton R. Krzesinski)
- Revert "drm: panel: add Xingbangda XBD599 panel" (Herton R. Krzesinski)
- Revert "drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation" (Herton R. Krzesinski)
- New configs in arch/powerpc (Fedora Kernel Team)
- Fix merge issue (Justin M. Forbes)
- Revert pending so that MR works (Justin M. Forbes)

* Sat Feb 27 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc0.20210227gitc03c21ba6f4e.161]
- Change the pending config for CONFIG_PPC_QUEUED_SPINLOCKS as it is now default upstream for 64-bit server CPUs (Justin M. Forbes)
- Turn on CONFIG_PPC_QUEUED_SPINLOCKS as it is default upstream now (Justin M. Forbes)

* Tue Feb 23 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc0.20210223git3b9cdafb5358.159]
- Update pending-common configs to address new upstream config deps (Justin M. Forbes)
- rpmspec: ship gpio-watch.debug in the proper debuginfo package (Herton R. Krzesinski)

* Mon Feb 22 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.12.0-0.rc0.20210222git31caf8b2a847.158]
- Removed description text as a comment confuses the config generation (Justin M. Forbes)
- New configs in drivers/dma-buf (Jeremy Cline)
- Fedora: ARMv7: build for 16 CPUs. (Peter Robinson)
- Fedora: only enable DEBUG_HIGHMEM on debug kernels (Peter Robinson)
- process_configs.sh: fix find/xargs data flow (Ondrej Mosnacek)
- Fedora config update (Justin M. Forbes)
- fedora: minor arm sound config updates (Peter Robinson)
- Fix trailing white space in redhat/configs/fedora/generic/CONFIG_SND_INTEL_BYT_PREFER_SOF (Justin M. Forbes)
- Add a redhat/rebase-notes.txt file (Hans de Goede)
- Turn on SND_INTEL_BYT_PREFER_SOF for Fedora (Hans de Goede)
- ALSA: hda: intel-dsp-config: Add SND_INTEL_BYT_PREFER_SOF Kconfig option (Hans de Goede) [1924101]
- CI: Drop MR ID from the name variable (Veronika Kabatova)
- redhat: add DUP and kpatch certificates to system trusted keys for RHEL build (Herton R. Krzesinski)
- The comments in CONFIG_USB_RTL8153_ECM actually turn off CONFIG_USB_RTL8152 (Justin M. Forbes)
- Update CKI pipeline project (Veronika Kabatova)
- Turn off additional KASAN options for Fedora (Justin M. Forbes)
- Rename the master branch to rawhide for Fedora (Justin M. Forbes)
- Makefile targets for packit integration (Ben Crocker)
- Turn off KASAN for rawhide debug builds (Justin M. Forbes)
- New configs in arch/arm64 (Justin Forbes)
- Remove deprecated Intel MIC config options (Peter Robinson)
- redhat: replace inline awk script with genlog.py call (Herton R. Krzesinski)
- redhat: add genlog.py script (Herton R. Krzesinski)
- kernel.spec.template - fix use_vdso usage (Ben Crocker)
- redhat: remove remaining references of CONFIG_RH_DISABLE_DEPRECATED (Herton R. Krzesinski)
- .gitignore: fix previous mismerge with "HEAD line" (Herton R. Krzesinski)
- Turn off vdso_install for ppc (Justin M. Forbes)
- Remove bpf-helpers.7 from bpftool package (Jiri Olsa)
- New configs in lib/Kconfig.debug (Fedora Kernel Team)
- Turn off CONFIG_VIRTIO_CONSOLE for s390x zfcpdump (Justin M. Forbes)
- New configs in drivers/clk (Justin M. Forbes)
- Keep VIRTIO_CONSOLE on s390x available. (Jakub Čajka)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- Fedora 5.11 config updates part 4 (Justin M. Forbes)
- Fedora 5.11 config updates part 3 (Justin M. Forbes)
- Fedora 5.11 config updates part 2 (Justin M. Forbes)
- Update internal (test) module list from RHEL-8 (Joe Lawrence) [1915073]
- Fix USB_XHCI_PCI regression (Justin M. Forbes)
- fedora: fixes for ARMv7 build issue by disabling HIGHPTE (Peter Robinson)
- all: s390x: Increase CONFIG_PCI_NR_FUNCTIONS to 512 (#1888735) (Dan Horák)
- Fedora 5.11 configs pt 1 (Justin M. Forbes)
- redhat: avoid conflict with mod-blacklist.sh and released_kernel defined (Herton R. Krzesinski)
- redhat: handle certificate files conditionally as done for src.rpm (Herton R. Krzesinski)
- specfile: add {?_smp_mflags} to "make headers_install" in tools/testing/selftests (Denys Vlasenko)
- specfile: add {?_smp_mflags} to "make samples/bpf/" (Denys Vlasenko)
- Run MR testing in CKI pipeline (Veronika Kabatova)
- Reword comment (Nicolas Chauvet)
- Add with_cross_arm conditional (Nicolas Chauvet)
- Redefines __strip if with_cross (Nicolas Chauvet)
- fedora: only enable ACPI_CONFIGFS, ACPI_CUSTOM_METHOD in debug kernels (Peter Robinson)
- fedora: User the same EFI_CUSTOM_SSDT_OVERLAYS as ARK (Peter Robinson)
- all: all arches/kernels enable the same DMI options (Peter Robinson)
- all: move SENSORS_ACPI_POWER to common/generic (Peter Robinson)
- fedora: PCIE_HISI_ERR is already in common (Peter Robinson)
- all: all ACPI platforms enable ATA_ACPI so move it to common (Peter Robinson)
- all: x86: move shared x86 acpi config options to generic (Peter Robinson)
- All: x86: Move ACPI_VIDEO to common/x86 (Peter Robinson)
- All: x86: Enable ACPI_DPTF (Intel DPTF) (Peter Robinson)
- All: enable ACPI_BGRT for all ACPI platforms. (Peter Robinson)
- All: Only build ACPI_EC_DEBUGFS for debug kernels (Peter Robinson)
- All: Disable Intel Classmate PC ACPI_CMPC option (Peter Robinson)
- cleanup: ACPI_PROCFS_POWER was removed upstream (Peter Robinson)
- All: ACPI: De-dupe the ACPI options that are the same across ark/fedora on x86/arm (Peter Robinson)
- Enable the vkms module in Fedora (Jeremy Cline)
- Revert "Merge branch 'revert-29a48502' into 'os-build'" (Justin Forbes)
- Fedora: arm updates for 5.11 and general cross Fedora cleanups (Peter Robinson)
- Add gcc-c++ to BuildRequires (Justin M. Forbes)
- gcc-plugins: fix gcc 11 indigestion with plugins... (Valdis Klētnieks)
- Update CONFIG_KASAN_HW_TAGS (Justin M. Forbes)
- fedora: arm: move generic power off/reset to all arm (Peter Robinson)
- fedora: ARMv7: build in DEVFREQ_GOV_SIMPLE_ONDEMAND until I work out why it's changed (Peter Robinson)
- fedora: cleanup joystick_adc (Peter Robinson)
- fedora: update some display options (Peter Robinson)
- fedora: arm: enable TI PRU options (Peter Robinson)
- fedora: arm: minor exynos plaform updates (Peter Robinson)
- arm: SoC: disable Toshiba Visconti SoC (Peter Robinson)
- common: disable ARCH_BCM4908 (NFC) (Peter Robinson)
- fedora: minor arm config updates (Peter Robinson)
- fedora: enable Tegra 234 SoC (Peter Robinson)
- fedora: arm: enable new Hikey 3xx options (Peter Robinson)
- Fedora: USB updates (Peter Robinson)
- fedora: enable the GNSS receiver subsystem (Peter Robinson)
- Remove POWER_AVS as no longer upstream (Peter Robinson)
- Cleanup RESET_RASPBERRYPI (Peter Robinson)
- Cleanup GPIO_CDEV_V1 options. (Peter Robinson)
- fedora: arm crypto updates (Peter Robinson)
- Revert "Merge branch 'ark-enable-structleak' into 'os-build'" (Justin Forbes)
- CONFIG_KASAN_HW_TAGS for aarch64 (Justin M. Forbes)
- Fix up bad merge with efi: generalize efi_get_secureboot (Justin M. Forbes)
- Fedora: cleanup PCMCIA configs, move to x86 (Peter Robinson)
- New configs in drivers/rtc (Fedora Kernel Team)
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK_BYREF_ALL (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_GCC_PLUGINS on ARK (Josh Poimboeuf) [1856176]
- redhat/configs: Enable CONFIG_KASAN on Fedora (Josh Poimboeuf) [1856176]
- New configs in init/Kconfig (Fedora Kernel Team)
- build_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- genspec.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- mod-blacklist.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Enable Speakup accessibility driver (Justin M. Forbes)
- New configs in init/Kconfig (Fedora Kernel Team)
- Fix fedora config mismatch due to dep changes (Justin M. Forbes)
- New configs in drivers/crypto (Jeremy Cline)
- Remove duplicate ENERGY_MODEL configs (Peter Robinson)
- This is selected by PCIE_QCOM so must match (Justin M. Forbes)
- drop unused BACKLIGHT_GENERIC (Peter Robinson)
- Remove cp instruction already handled in instruction below. (Paulo E. Castro)
- Add all the dependencies gleaned from running `make prepare` on a bloated devel kernel. (Paulo E. Castro)
- Add tools to path mangling script. (Paulo E. Castro)
- Remove duplicate cp statement which is also not specific to x86. (Paulo E. Castro)
- Correct orc_types failure whilst running `make prepare` https://bugzilla.redhat.com/show_bug.cgi?id=1882854 (Paulo E. Castro)
- redhat: ark: enable CONFIG_IKHEADERS (Jiri Olsa)
- Add missing '$' sign to (GIT) in redhat/Makefile (Augusto Caringi)
- Remove filterdiff and use native git instead (Don Zickus)
- New configs in net/sched (Justin M. Forbes)
- New configs in drivers/mfd (CKI@GitLab)
- New configs in drivers/mfd (Fedora Kernel Team)
- New configs in drivers/firmware (Fedora Kernel Team)
- Temporarily backout parallel xz script (Justin M. Forbes)
- redhat: explicitly disable CONFIG_IMA_APPRAISE_SIGNED_INIT (Bruno Meneguele)
- redhat: enable CONFIG_EVM_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM_ATTR_FSUUID on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM in all arches and flavors (Bruno Meneguele)
- redhat: enable CONFIG_IMA_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: set CONFIG_IMA_DEFAULT_HASH to SHA256 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT (Bruno Meneguele)
- redhat: enable CONFIG_IMA_READ_POLICY on ARK (Bruno Meneguele)
- redhat: set default IMA template for all ARK arches (Bruno Meneguele)
- redhat: enable CONFIG_IMA_DEFAULT_HASH_SHA256 for all flavors (Bruno Meneguele)
- redhat: disable CONFIG_IMA_DEFAULT_HASH_SHA1 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_ARCH_POLICY for ppc and x86 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_MODSIG (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_BOOTPARAM (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE (Bruno Meneguele)
- redhat: enable CONFIG_INTEGRITY for aarch64 (Bruno Meneguele)
- kernel: Update some missing KASAN/KCSAN options (Jeremy Linton)
- kernel: Enable coresight on aarch64 (Jeremy Linton)
- Update CONFIG_INET6_ESPINTCP (Justin Forbes)
- New configs in net/ipv6 (Justin M. Forbes)
- fedora: move CONFIG_RTC_NVMEM options from ark to common (Peter Robinson)
- configs: Enable CONFIG_DEBUG_INFO_BTF (Don Zickus)
- fedora: some minor arm audio config tweaks (Peter Robinson)
- Ship xpad with default modules on Fedora and RHEL (Bastien Nocera)
- Fedora: Only enable legacy serial/game port joysticks on x86 (Peter Robinson)
- Fedora: Enable the options required for the Librem 5 Phone (Peter Robinson)
- Fedora config update (Justin M. Forbes)
- Fedora config change because CONFIG_FSL_DPAA2_ETH now selects CONFIG_FSL_XGMAC_MDIO (Justin M. Forbes)
- redhat: generic  enable CONFIG_INET_MPTCP_DIAG (Davide Caratti)
- Fedora config update (Justin M. Forbes)
- Enable NANDSIM for Fedora (Justin M. Forbes)
- Re-enable CONFIG_ACPI_TABLE_UPGRADE for Fedora since upstream disables this if secureboot is active (Justin M. Forbes)
- Ath11k related config updates (Justin M. Forbes)
- Fedora config updates for ath11k (Justin M. Forbes)
- Turn on ATH11K for Fedora (Justin M. Forbes)
- redhat: enable CONFIG_INTEL_IOMMU_SVM (Jerry Snitselaar)
- More Fedora config fixes (Justin M. Forbes)
- Fedora 5.10 config updates (Justin M. Forbes)
- Fedora 5.10 configs round 1 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Allow kernel-tools to build without selftests (Don Zickus)
- Allow building of kernel-tools standalone (Don Zickus)
- redhat: ark: disable CONFIG_NET_ACT_CTINFO (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_TEQL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_SFB (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_QFQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PLUG (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PIE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_MULTIQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_HHF (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DSMARK (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DRR (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CODEL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CHOKE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CBQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_ATM (Davide Caratti)
- redhat: ark: disable CONFIG_NET_EMATCH and sub-targets (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_TCINDEX (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP6 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_ROUTE4 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_BASIC (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SKBMOD (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SIMP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_NAT (Davide Caratti)
- arm64/defconfig: Enable CONFIG_KEXEC_FILE (Bhupesh Sharma) [1821565]
- redhat/configs: Cleanup CONFIG_CRYPTO_SHA512 (Prarit Bhargava)
- New configs in drivers/mfd (Fedora Kernel Team)
- Fix LTO issues with kernel-tools (Don Zickus)
- Point pathfix to the new location for gen_compile_commands.py (Justin M. Forbes)
- Filter out LTO build options from the perl ccopts (Justin M. Forbes)
- configs: Disable CONFIG_SECURITY_SELINUX_DISABLE (Ondrej Mosnacek)
- Fix up a merge issue with rxe.c (Justin M. Forbes)
- [Automatic] Handle config dependency changes (Don Zickus)
- configs/iommu: Add config comment to empty CONFIG_SUN50I_IOMMU file (Jerry Snitselaar)
- New configs in kernel/trace (Fedora Kernel Team)
- Fix Fedora config locations (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- configs: enable CONFIG_CRYPTO_CTS=y so cts(cbc(aes)) is available in FIPS mode (Vladis Dronov) [1855161]
- Partial revert: Add master merge check (Don Zickus)
- Update Maintainers doc to reflect workflow changes (Don Zickus)
- WIP: redhat/docs: Update documentation for single branch workflow (Prarit Bhargava)
- Add CONFIG_ARM64_MTE which is not picked up by the config scripts for some reason (Justin M. Forbes)
- Disable Speakup synth DECEXT (Justin M. Forbes)
- Enable Speakup for Fedora since it is out of staging (Justin M. Forbes)
- Modify patchlist changelog output (Don Zickus)
- process_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- generate_all_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- redhat/self-test: Initial commit (Ben Crocker)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Fixes "acpi: prefer booting with ACPI over DTS" to be RHEL only (Peter Robinson)
- arch/x86: Remove vendor specific CPU ID checks (Prarit Bhargava)
- redhat: Replace hardware.redhat.com link in Unsupported message (Prarit Bhargava) [1810301]
- x86: Fix compile issues with rh_check_supported() (Don Zickus)
- e1000e: bump up timeout to wait when ME un-configure ULP mode (Aaron Ma)
- drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation (Icenowy Zheng)
- drm: panel: add Xingbangda XBD599 panel (Icenowy Zheng)
- dt-bindings: panel: add binding for Xingbangda XBD599 panel (Icenowy Zheng)
- ARM: fix __get_user_check() in case uaccess_* calls are not inlined (Masahiro Yamada)
- mm/kmemleak: skip late_init if not skip disable (Murphy Zhou)
- KEYS: Make use of platform keyring for module signature verify (Robert Holmes)
- Drop that for now (Laura Abbott)
- Input: rmi4 - remove the need for artificial IRQ in case of HID (Benjamin Tissoires)
- ARM: tegra: usb no reset (Peter Robinson)
- arm: make CONFIG_HIGHPTE optional without CONFIG_EXPERT (Jon Masters)
- redhat: rh_kabi: deduplication friendly structs (Jiri Benc)
- redhat: rh_kabi add a comment with warning about RH_KABI_EXCLUDE usage (Jiri Benc)
- redhat: rh_kabi: introduce RH_KABI_EXTEND_WITH_SIZE (Jiri Benc)
- redhat: rh_kabi: Indirect EXTEND macros so nesting of other macros will resolve. (Don Dutile)
- redhat: rh_kabi: Fix RH_KABI_SET_SIZE to use dereference operator (Tony Camuso)
- redhat: rh_kabi: Add macros to size and extend structs (Prarit Bhargava)
- Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy)
- mptsas: pci-id table changes (Laura Abbott)
- mptsas: Taint kernel if mptsas is loaded (Laura Abbott)
- mptspi: pci-id table changes (Laura Abbott)
- qla2xxx: Remove PCI IDs of deprecated adapter (Jeremy Cline)
- be2iscsi: remove unsupported device IDs (Chris Leech)
- mptspi: Taint kernel if mptspi is loaded (Laura Abbott)
- hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek)
- qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis)
- aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta)
- megaraid_sas: remove deprecated pci-ids (Tomas Henzl)
- mpt*: remove certain deprecated pci-ids (Jeremy Cline)
- kernel: add SUPPORT_REMOVED kernel taint (Tomas Henzl)
- Rename RH_DISABLE_DEPRECATED to RHEL_DIFFERENCES (Don Zickus)
- Add option of 13 for FORCE_MAX_ZONEORDER (Peter Robinson)
- s390: Lock down the kernel when the IPL secure flag is set (Jeremy Cline)
- efi: Lock down the kernel if booted in secure boot mode (David Howells)
- efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (David Howells)
- security: lockdown: expose a hook to lock the kernel down (Jeremy Cline)
- Make get_cert_list() use efi_status_to_str() to print error messages. (Peter Jones)
- Add efi_status_to_str() and rework efi_status_to_err(). (Peter Jones)
- Add support for deprecating processors (Laura Abbott) [1565717 1595918 1609604 1610493]
- arm: aarch64: Drop the EXPERT setting from ARM64_FORCE_52BIT (Jeremy Cline)
- iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- rh_kabi: introduce RH_KABI_EXCLUDE (Jakub Racek)
- ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [1670017]
- IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- scsi: smartpqi: add inspur advantech ids (Don Brace)
- ice: mark driver as tech-preview (Jonathan Toppins)
- kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- add pci_hw_vendor_status() (Maurizio Lombardi)
- ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter)
- Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter)
- bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- tags.sh: Ignore redhat/rpm (Jeremy Cline)
- put RHEL info into generated headers (Laura Abbott) [1663728]
- kdump: add support for crashkernel=auto (Jeremy Cline)
- kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- modules: add rhelversion MODULE_INFO tag (Laura Abbott)
- ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- Add Red Hat tainting (Laura Abbott) [1565704]
- Introduce CONFIG_RH_DISABLE_DEPRECATED (Laura Abbott)
- Stop merging ark-patches for release (Don Zickus)
- Fix path location for ark-update-configs.sh (Don Zickus)
- Combine Red Hat patches into single patch (Don Zickus)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- New configs in drivers/misc (Jeremy Cline)
- New configs in drivers/net/wireless (Justin M. Forbes)
- New configs in drivers/phy (Fedora Kernel Team)
- New configs in drivers/tty (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)
- Updated changelog for the release based on 22fbc037cd32 (Fedora Kernel Team)
- Updated changelog for the release based on d3d45f8220d6 (Fedora Kernel Team)
- Updated changelog for the release based on 472e5b056f00 (Fedora Kernel Team)
- Set SquashFS decompression options for all flavors to match RHEL (Bohdan Khomutskyi)
- Updated changelog for the release based on 60e720931556 (Fedora Kernel Team)
- configs: Enable CONFIG_ENERGY_MODEL (Phil Auld)
- New configs in drivers/pinctrl (Fedora Kernel Team)
- Update CONFIG_THERMAL_NETLINK (Justin Forbes)
- Updated changelog for the release based on 02de58b24d2e (Fedora Kernel Team)
- Updated changelog for the release based on fb0155a09b02 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)
- Separate merge-upstream and release stages (Don Zickus)
- Re-enable CONFIG_IR_SERIAL on Fedora (Prarit Bhargava)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)
- Updated changelog for the release based on a1bffa48745a (Fedora Kernel Team)
- Create Patchlist.changelog file (Don Zickus)
- Updated changelog for the release based on 7c7ec3226f5f (Fedora Kernel Team)
- Filter out upstream commits from changelog (Don Zickus)
- Merge Upstream script fixes (Don Zickus)
- Updated changelog for the release based on 171d4ff79f96 (Fedora Kernel Team)
- Updated changelog for the release based on c9c9e6a49f89 (Fedora Kernel Team)
- Updated changelog for the release based on 805c6d3c1921 (Fedora Kernel Team)
- Updated changelog for the release based on 98477740630f (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc6 (Fedora Kernel Team)
- kernel.spec: Remove kernel-keys directory on rpm erase (Prarit Bhargava)
- Add mlx5_vdpa to module filter for Fedora (Justin M. Forbes)
- Add python3-sphinx_rtd_theme buildreq for docs (Justin M. Forbes)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on fc4f28bb3daf (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc5 (Fedora Kernel Team)
- Updated changelog for the release based on ef2e9a563b0c (Fedora Kernel Team)
- Updated changelog for the release based on 729e3d091984 (Fedora Kernel Team)
- dist-merge-upstream: Checkout known branch for ci scripts (Don Zickus)
- Updated changelog for the release based on 581cb3a26baf (Fedora Kernel Team)
- kernel.spec: don't override upstream compiler flags for ppc64le (Dan Horák)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on v5.9-rc4 (Fedora Kernel Team)
- Updated changelog for the release based on dd9fb9bb3340 (Fedora Kernel Team)
- Updated changelog for the release based on c70672d8d316 (Fedora Kernel Team)
- Fedora confi gupdate (Justin M. Forbes)
- Updated changelog for the release based on 59126901f200 (Fedora Kernel Team)
- mod-sign.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Swap how ark-latest is built (Don Zickus)
- Add extra version bump to os-build branch (Don Zickus)
- dist-release: Avoid needless version bump. (Don Zickus)
- Add dist-fedora-release target (Don Zickus)
- Remove redundant code in dist-release (Don Zickus)
- Makefile.common rename TAG to _TAG (Don Zickus)
- Updated changelog for the release based on fc3abb53250a (Fedora Kernel Team)
- Fedora config change (Justin M. Forbes)
- Updated changelog for the release based on 9c7d619be5a0 (Fedora Kernel Team)
- Updated changelog for the release based on b51594df17d0 (Fedora Kernel Team)
- Fedora filter update (Justin M. Forbes)
- Config update for Fedora (Justin M. Forbes)
- Updated changelog for the release based on v5.9-rc3 (Fedora Kernel Team)
- Updated changelog for the release based on 1127b219ce94 (Fedora Kernel Team)
- Updated changelog for the release based on 4d41ead6ead9 (Fedora Kernel Team)
- Updated changelog for the release based on 15bc20c6af4c (Fedora Kernel Team)
- Updated changelog for the release based on 2ac69819ba9e (Fedora Kernel Team)
- Updated changelog for the release based on 6a9dc5fd6170 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc2 (Fedora Kernel Team)
- Updated changelog for the release based on c3d8f220d012 (Fedora Kernel Team)
- Updated changelog for the release based on f873db9acd3c (Fedora Kernel Team)
- Updated changelog for the release based on da2968ff879b (Fedora Kernel Team)
- enable PROTECTED_VIRTUALIZATION_GUEST for all s390x kernels (Dan Horák)
- Updated changelog for the release based on 18445bf405cb (Fedora Kernel Team)
- redhat: ark: enable CONFIG_NET_SCH_TAPRIO (Davide Caratti)
- redhat: ark: enable CONFIG_NET_SCH_ETF (Davide Caratti)
- More Fedora config updates (Justin M. Forbes)
- New config deps (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on 06a4ec1d9dc6 (Fedora Kernel Team)
- First half of config updates for Fedora (Justin M. Forbes)
- Updates for Fedora arm architectures for the 5.9 window (Peter Robinson)
- Add config options that only show up when we prep on arm (Justin M. Forbes)
- Config updates for Fedora (Justin M. Forbes)
- fedora: enable enery model (Peter Robinson)
- Use the configs/generic config for SND_HDA_INTEL everywhere (Peter Robinson)
- Enable ZSTD compression algorithm on all kernels (Peter Robinson)
- Enable ARM_SMCCC_SOC_ID on all aarch64 kernels (Peter Robinson)
- iio: enable LTR-559 light and proximity sensor (Peter Robinson)
- iio: chemical: enable some popular chemical and partical sensors (Peter Robinson)
- More mismatches (Justin M. Forbes)
- Fedora config change due to deps (Justin M. Forbes)
- CONFIG_SND_SOC_MAX98390 is now selected by SND_SOC_INTEL_DA7219_MAX98357A_GENERIC (Justin M. Forbes)
- Config change required for build part 2 (Justin M. Forbes)
- Config change required for build (Justin M. Forbes)
- Revert "Merge branch 'make_configs_fix' into 'os-build'" (Justin Forbes)
- Fedora config update (Justin M. Forbes)
- Add ability to sync upstream through Makefile (Don Zickus)
- Add master merge check (Don Zickus)
- Replace hardcoded values 'os-build' and project id with variables (Don Zickus)
- redhat/Makefile.common: Fix MARKER (Prarit Bhargava)
- gitattributes: Remove unnecesary export restrictions (Prarit Bhargava)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on v5.8 (Fedora Kernel Team)
- Updated changelog for the release based on ac3a0c847296 (Fedora Kernel Team)
- Updated changelog for the release based on 7dc6fd0f3b84 (Fedora Kernel Team)
- Updated changelog for the release based on 417385c47ef7 (Fedora Kernel Team)
- Add new certs for dual signing with boothole (Justin M. Forbes)
- Update secureboot signing for dual keys (Justin M. Forbes)
- Updated changelog for the release based on d3590ebf6f91 (Fedora Kernel Team)
- Updated changelog for the release based on 6ba1b005ffc3 (Fedora Kernel Team)
- fedora: enable LEDS_SGM3140 for arm configs (Peter Robinson)
- Updated changelog for the release based on v5.8-rc7 (Fedora Kernel Team)
- Updated changelog for the release based on 04300d66f0a0 (Fedora Kernel Team)
- Updated changelog for the release based on 23ee3e4e5bd2 (Fedora Kernel Team)
- Enable CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG (Justin M. Forbes)
- Updated changelog for the release based on f37e99aca03f (Fedora Kernel Team)
- redhat/configs: Fix common CONFIGs (Prarit Bhargava)
- redhat/configs: General CONFIG cleanups (Prarit Bhargava)
- redhat/configs: Update & generalize evaluate_configs (Prarit Bhargava)
- Updated changelog for the release based on d15be546031c (Fedora Kernel Team)
- fedora: arm: Update some meson config options (Peter Robinson)
- Updated changelog for the release based on 4fa640dc5230 (Fedora Kernel Team)
- redhat/docs: Add Fedora RPM tagging date (Prarit Bhargava)
- Updated changelog for the release based on 5714ee50bb43 (Fedora Kernel Team)
- Updated changelog for the release based on f932d58abc38 (Fedora Kernel Team)
- Updated changelog for the release based on 6a70f89cc58f (Fedora Kernel Team)
- Updated changelog for the release based on 07a56bb875af (Fedora Kernel Team)
- Updated changelog for the release based on e9919e11e219 (Fedora Kernel Team)
- Update config for renamed panel driver. (Peter Robinson)
- Enable SERIAL_SC16IS7XX for SPI interfaces (Peter Robinson)
- Updated changelog for the release based on dcde237b9b0e (Fedora Kernel Team)
- Updated changelog for the release based on v5.8-rc4 (Fedora Kernel Team)
- s390x-zfcpdump: Handle missing Module.symvers file (Don Zickus)
- Updated changelog for the release based on cd77006e01b3 (Fedora Kernel Team)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on v5.8-rc3 (Fedora Kernel Team)
- Updated changelog for the release based on 8be3a53e18e0 (Fedora Kernel Team)
- redhat/configs: Add .tmp files to .gitignore (Prarit Bhargava)
- disable uncommon TCP congestion control algorithms (Davide Caratti)
- Updated changelog for the release based on dd0d718152e4 (Fedora Kernel Team)
- Add new bpf man pages (Justin M. Forbes)
- Add default option for CONFIG_ARM64_BTI_KERNEL to pending-common so that eln kernels build (Justin M. Forbes)
- redhat/Makefile: Add fedora-configs and rh-configs make targets (Prarit Bhargava)
- Updated changelog for the release based on 625d3449788f (Fedora Kernel Team)
- Updated changelog for the release based on 1b5044021070 (Fedora Kernel Team)
- redhat/configs: Use SHA512 for module signing (Prarit Bhargava)
- genspec.sh: 'touch' empty Patchlist file for single tarball (Don Zickus)
- Updated changelog for the release based on 69119673bd50 (Fedora Kernel Team)
- Updated changelog for the release based on a5dc8300df75 (Fedora Kernel Team)
- Fedora config update for rc1 (Justin M. Forbes)
- Updated changelog for the release based on v5.8-rc1 (Fedora Kernel Team)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on df2fbf5bfa0e (Fedora Kernel Team)
- Fedora config updates (Justin M. Forbes)
- Updated changelog for the release based on b791d1bdf921 (Fedora Kernel Team)
- redhat/Makefile.common: fix RPMKSUBLEVEL condition (Ondrej Mosnacek)
- redhat/Makefile: silence KABI tar output (Ondrej Mosnacek)
- One more Fedora config update (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix PATCHLEVEL for merge window (Justin M. Forbes)
- Change ark CONFIG_COMMON_CLK to yes, it is selected already by other options (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- More module filtering for Fedora (Justin M. Forbes)
- Update filters for rnbd in Fedora (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix up module filtering for 5.8 (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- More Fedora config work (Justin M. Forbes)
- RTW88BE and CE have been extracted to their own modules (Justin M. Forbes)
- Set CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK for Fedora (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Arm64 Use Branch Target Identification for kernel (Justin M. Forbes)
- Change value of CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE (Justin M. Forbes)
- Fedora config updates (Justin M. Forbes)
- Fix configs for Fedora (Justin M. Forbes)
- Add zero-commit to format-patch options (Justin M. Forbes)
- Copy Makefile.rhelver as a source file rather than a patch (Jeremy Cline)
- Move the sed to clear the patch templating outside of conditionals (Justin M. Forbes)
- Match template format in kernel.spec.template (Justin M. Forbes)
- Break out the Patches into individual files for dist-git (Justin M. Forbes)
- Break the Red Hat patch into individual commits (Jeremy Cline)
- Fix update_scripts.sh unselective pattern sub (David Howells)
- Add cec to the filter overrides (Justin M. Forbes)
- Add overrides to filter-modules.sh (Justin M. Forbes)
- redhat/configs: Enable CONFIG_SMC91X and disable CONFIG_SMC911X (Prarit Bhargava) [1722136]
- Include bpftool-struct_ops man page in the bpftool package (Jeremy Cline)
- Add sharedbuffer_configuration.py to the pathfix.py script (Jeremy Cline)
- Use __make macro instead of make (Tom Stellard)
- Sign off generated configuration patches (Jeremy Cline)
- Drop the static path configuration for the Sphinx docs (Jeremy Cline)
- Updated changelog for the release based on b0c3ba31be3e (CKI@GitLab)
- Updated changelog for the release based on 444fc5cde643 (CKI@GitLab)
- redhat: Add dummy-module kernel module (Prarit Bhargava)
- redhat: enable CONFIG_LWTUNNEL_BPF (Jiri Benc)
- Remove typoed config file aarch64CONFIG_SM_GCC_8150 (Justin M. Forbes)
- Updated changelog for the release based on v5.7-rc7 (CKI@GitLab)
- Updated changelog for the release based on caffb99b6929 (CKI@GitLab)
- Updated changelog for the release based on 444565650a5f (CKI@GitLab)
- Add Documentation back to kernel-devel as it has Kconfig now (Justin M. Forbes)
- Copy distro files rather than moving them (Jeremy Cline)
- kernel.spec: fix 'make scripts' for kernel-devel package (Brian Masney)
- Makefile: correct help text for dist-cross-<arch>-rpms (Brian Masney)
- redhat/Makefile: Fix RHEL8 python warning (Prarit Bhargava)
- redhat: Change Makefile target names to dist- (Prarit Bhargava)
- configs: Disable Serial IR driver (Prarit Bhargava)
- Updated changelog for the release based on 642b151f45dd (CKI@GitLab)
- Updated changelog for the release based on v5.7-rc6 (CKI@GitLab)
- Updated changelog for the release based on 3d1c1e5931ce (CKI@GitLab)
- Updated changelog for the release based on 12bf0b632ed0 (CKI@GitLab)
- Updated changelog for the release based on 1ae7efb38854 (CKI@GitLab)
- Updated changelog for the release based on 24085f70a6e1 (CKI@GitLab)
- Updated changelog for the release based on 152036d1379f (CKI@GitLab)
- Fix "multiple files for package kernel-tools" (Pablo Greco)
- Updated changelog for the release based on v5.7-rc5 (CKI@GitLab)
- Updated changelog for the release based on e99332e7b4cd (CKI@GitLab)
- Updated changelog for the release based on d5eeab8d7e26 (CKI@GitLab)
- Introduce a Sphinx documentation project (Jeremy Cline)
- Updated changelog for the release based on 79dede78c057 (CKI@GitLab)
- Build ARK against ELN (Don Zickus)
- Updated changelog for the release based on a811c1fa0a02 (CKI@GitLab)
- Updated changelog for the release based on dc56c5acd850 (CKI@GitLab)
- Updated changelog for the release based on 47cf1b422e60 (CKI@GitLab)
- Updated changelog for the release based on v5.7-rc4 (CKI@GitLab)
- Updated changelog for the release based on f66ed1ebbfde (CKI@GitLab)
- Updated changelog for the release based on 690e2aba7beb (CKI@GitLab)
- Drop the requirement to have a remote called linus (Jeremy Cline)
- Rename 'internal' branch to 'os-build' (Don Zickus)
- Updated changelog for the release based on c45e8bccecaf (CKI@GitLab)
- Updated changelog for the release based on 1d2cc5ac6f66 (CKI@GitLab)
- Only include open merge requests with "Include in Releases" label (Jeremy Cline)
- Package gpio-watch in kernel-tools (Jeremy Cline)
- Exit non-zero if the tag already exists for a release (Jeremy Cline)
- Adjust the changelog update script to not push anything (Jeremy Cline)
- Drop --target noarch from the rh-rpms make target (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- Add a script to generate release tags and branches (Jeremy Cline)
- Set CONFIG_VDPA for fedora (Justin M. Forbes)
- Add a README to the dist-git repository (Jeremy Cline)
- Provide defaults in ark-rebase-patches.sh (Jeremy Cline)
- Default ark-rebase-patches.sh to not report issues (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- Drop DIST from release commits and tags (Jeremy Cline)
- Place the buildid before the dist in the release (Jeremy Cline)
- Sync up with Fedora arm configuration prior to merging (Jeremy Cline)
- Disable CONFIG_PROTECTED_VIRTUALIZATION_GUEST for zfcpdump (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Add RHMAINTAINERS file and supporting conf (Don Zickus)
- Add a script to test if all commits are signed off (Jeremy Cline)
- Fix make rh-configs-arch (Don Zickus)
- Drop RH_FEDORA in favor of the now-merged RHEL_DIFFERENCES (Jeremy Cline)
- Sync up Fedora configs from the first week of the merge window (Jeremy Cline)
- Migrate blacklisting floppy.ko to mod-blacklist.sh (Don Zickus)
- kernel packaging: Combine mod-blacklist.sh and mod-extra-blacklist.sh (Don Zickus)
- kernel packaging: Fix extra namespace collision (Don Zickus)
- mod-extra.sh: Rename to mod-blacklist.sh (Don Zickus)
- mod-extra.sh: Make file generic (Don Zickus)
- Fix a painfully obvious YAML syntax error in .gitlab-ci.yml (Jeremy Cline)
- Add in armv7hl kernel header support (Don Zickus)
- Disable all BuildKernel commands when only building headers (Don Zickus)
- Updated changelog (CKI@GitLab)
- Drop any gitlab-ci patches from ark-patches (Jeremy Cline)
- Build the srpm for internal branch CI using the vanilla tree (Jeremy Cline)
- Pull in the latest ARM configurations for Fedora (Jeremy Cline)
- Fix xz memory usage issue (Neil Horman)
- Use ark-latest instead of master for update script (Jeremy Cline)
- Move the CI jobs back into the ARK repository (Jeremy Cline)
- Revert "[redhat] Apply a second patch set in Fedora build roots" (Jeremy Cline)
- Sync up ARK's Fedora config with the dist-git repository (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Pull in the latest configuration changes from Fedora (Jeremy Cline)
- configs: enable CONFIG_NET_SCH_CBS (Marcelo Ricardo Leitner)
- Updated changelog (CKI@GitLab)
- Drop configuration options in fedora/ that no longer exist (Jeremy Cline)
- Set RH_FEDORA for ARK and Fedora (Jeremy Cline)
- redhat/kernel.spec: Include the release in the kernel COPYING file (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- redhat/kernel.spec: add scripts/jobserver-exec to py3_shbang_opts list (Jeremy Cline)
- redhat/kernel.spec: package bpftool-gen man page (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- distgit-changelog: handle multiple y-stream BZ numbers (Bruno Meneguele)
- redhat/kernel.spec: remove all inline comments (Bruno Meneguele)
- redhat/genspec: awk unknown whitespace regex pattern (Bruno Meneguele)
- Improve the readability of gen_config_patches.sh (Jeremy Cline)
- Fix some awkward edge cases in gen_config_patches.sh (Jeremy Cline)
- Updated changelog (Jeremy Cline)
- Update the CI environment to use Fedora 31 (Jeremy Cline)
- Revert "Turn off CONFIG_AX25" (Laura Abbott)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- redhat: drop whitespace from with_gcov macro (Jan Stancek)
- configs: Enable CONFIG_KEY_DH_OPERATIONS on ARK (Ondrej Mosnacek)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- Updated changelog (CKI@GitLab)
- configs: Adjust CONFIG_MPLS_ROUTING and CONFIG_MPLS_IPTUNNEL (Laura Abbott)
- New configs in lib/crypto (Jeremy Cline)
- New configs in drivers/char (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Turn on BLAKE2B for Fedora (Jeremy Cline)
- kernel.spec.template: Clean up stray *.h.s files (Laura Abbott)
- Build the SRPM in the CI job (Jeremy Cline)
- New configs in net/tls (Jeremy Cline)
- New configs in net/tipc (Jeremy Cline)
- New configs in lib/kunit (Jeremy Cline)
- Fix up released_kernel case (Laura Abbott)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- New configs in drivers/ptp (Jeremy Cline)
- New configs in drivers/nvme (Jeremy Cline)
- New configs in drivers/net/phy (Jeremy Cline)
- New configs in arch/arm64 (Jeremy Cline)
- New configs in drivers/crypto (Jeremy Cline)
- New configs in crypto/Kconfig (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- Add label so the Gitlab to email bridge ignores the changelog (Jeremy Cline)
- Temporarily switch TUNE_DEFAULT to y (Jeremy Cline)
- Run config test for merge requests and internal (Jeremy Cline)
- Turn off CONFIG_AX25 (Laura Abbott)
- Add missing licensedir line (Laura Abbott)
- Updated changelog (CKI@GitLab)
- redhat/scripts: Remove redhat/scripts/rh_get_maintainer.pl (Prarit Bhargava)
- configs: Take CONFIG_DEFAULT_MMAP_MIN_ADDR from Fedra (Laura Abbott)
- configs: Turn off ISDN (Laura Abbott)
- Add a script to generate configuration patches (Laura Abbott)
- Introduce rh-configs-commit (Laura Abbott)
- kernel-packaging: Remove kernel files from kernel-modules-extra package (Prarit Bhargava)
- Updated changelog (CKI@GitLab)
- configs: Enable CONFIG_DEBUG_WX (Laura Abbott)
- configs: Disable wireless USB (Laura Abbott)
- Clean up some temporary config files (Laura Abbott)
- configs: New config in drivers/gpu for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/powerpc for v5.4-rc1 (Jeremy Cline)
- configs: New config in crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/usb for v5.4-rc1 (Jeremy Cline)
- AUTOMATIC: New configs (Jeremy Cline)
- Skip ksamples for bpf, they are broken (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- configs: New config in fs/erofs for v5.4-rc1 (Jeremy Cline)
- configs: New config in mm for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/md for v5.4-rc1 (Jeremy Cline)
- configs: New config in init for v5.4-rc1 (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- configs: New config in fs/fuse for v5.4-rc1 (Jeremy Cline)
- merge.pl: Avoid comments but do not skip them (Don Zickus)
- configs: New config in drivers/net/ethernet/pensando for v5.4-rc1 (Jeremy Cline)
- Update a comment about what released kernel means (Laura Abbott)
- Provide both Fedora and RHEL files in the SRPM (Laura Abbott)
- kernel.spec.template: Trim EXTRAVERSION in the Makefile (Laura Abbott)
- kernel.spec.template: Add macros for building with nopatches (Laura Abbott)
- kernel.spec.template: Add some macros for Fedora differences (Laura Abbott)
- kernel.spec.template: Consolodate the options (Laura Abbott)
- configs: Add pending direcory to Fedora (Laura Abbott)
- kernel.spec.template: Don't run hardlink if rpm-ostree is in use (Laura Abbott)
- configs: New config in net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/phy for v5.4-rc1 (Jeremy Cline)
- Updated changelog (CKI@GitLab)
- configs: Increase x86_64 NR_UARTS to 64 (Prarit Bhargava) [1730649]
- configs: turn on ARM64_FORCE_52BIT for debug builds (Jeremy Cline)
- kernel.spec.template: Tweak the python3 mangling (Laura Abbott)
- kernel.spec.template: Add --with verbose option (Laura Abbott)
- kernel.spec.template: Switch to using install instead of __install (Laura Abbott)
- kernel.spec.template: Make the kernel.org URL https (Laura Abbott)
- kernel.spec.template: Update message about secure boot signing (Laura Abbott)
- kernel.spec.template: Move some with flags definitions up (Laura Abbott)
- kernel.spec.template: Update some BuildRequires (Laura Abbott)
- kernel.spec.template: Get rid of clean (Laura Abbott)
- configs: New config in drivers/char for v5.4-rc1 (Jeremy Cline)
- configs: New config in net/sched for v5.4-rc1 (Jeremy Cline)
- configs: New config in lib for v5.4-rc1 (Jeremy Cline)
- configs: New config in fs/verity for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/aarch64 for v5.4-rc4 (Jeremy Cline)
- configs: New config in arch/arm64 for v5.4-rc1 (Jeremy Cline)
- Flip off CONFIG_ARM64_VA_BITS_52 so the bundle that turns it on applies (Jeremy Cline)
- Update changelog (Laura Abbott)
- New configuration options for v5.4-rc4 (Jeremy Cline)
- Correctly name tarball for single tarball builds (Laura Abbott)
- configs: New config in drivers/pci for v5.4-rc1 (Jeremy Cline)
- Allow overriding the dist tag on the command line (Laura Abbott)
- Allow scratch branch target to be overridden (Laura Abbott)
- Remove long dead BUILD_DEFAULT_TARGET (Laura Abbott)
- Amend the changelog when rebasing (Laura Abbott)
- configs: New config in drivers/platform for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/pinctrl for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/wireless for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/ethernet/mellanox for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hid for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/dma-buf for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in block for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/cpuidle for v5.4-rc1 (Jeremy Cline)
- redhat: configs: Split CONFIG_CRYPTO_SHA512 (Laura Abbott)
- redhat: Set Fedora options (Laura Abbott)
- Set CRYPTO_SHA3_*_S390 to builtin on zfcpdump (Jeremy Cline)
- configs: New config in drivers/edac for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/firmware for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hwmon for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/iio for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/mmc for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/tty for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/bus for v5.4-rc1 (Jeremy Cline)
- Add option to allow mismatched configs on the command line (Laura Abbott)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/pci for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/soc for v5.4-rc1 (Jeremy Cline)
- gitlab: Add CI job for packaging scripts (Major Hayden)
- Speed up CI with CKI image (Major Hayden)
- Disable e1000 driver in ARK (Neil Horman)
- configs: Fix the pending default for CONFIG_ARM64_VA_BITS_52 (Jeremy Cline)
- configs: Turn on OPTIMIZE_INLINING for everything (Jeremy Cline)
- configs: Set valid pending defaults for CRYPTO_ESSIV (Jeremy Cline)
- Add an initial CI configuration for the internal branch (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- Pull the RHEL version defines out of the Makefile (Jeremy Cline)
- Sync up the ARK build scripts (Jeremy Cline)
- Sync up the Fedora Rawhide configs (Jeremy Cline)
- Sync up the ARK config files (Jeremy Cline)
- configs: Adjust CONFIG_FORCE_MAX_ZONEORDER for Fedora (Laura Abbott)
- configs: Add README for some other arches (Laura Abbott)
- configs: Sync up Fedora configs (Laura Abbott)
- [initial commit] Add structure for building with git (Laura Abbott)
- [initial commit] Add Red Hat variables in the top level makefile (Laura Abbott)
- [initial commit] Red Hat gitignore and attributes (Laura Abbott)
- [initial commit] Add changelog (Laura Abbott)
- [initial commit] Add makefile (Laura Abbott)
- [initial commit] Add files for generating the kernel.spec (Laura Abbott)
- [initial commit] Add rpm directory (Laura Abbott)
- [initial commit] Add files for packaging (Laura Abbott)
- [initial commit] Add kabi files (Laura Abbott)
- [initial commit] Add scripts (Laura Abbott)
- [initial commit] Add configs (Laura Abbott)
- [initial commit] Add Makefiles (Laura Abbott)

* Sat Feb 20 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-157]
- Removed description text as a comment confuses the config generation (Justin M. Forbes)

* Fri Feb 19 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-156]
- New configs in drivers/dma-buf (Jeremy Cline)

* Thu Feb 18 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-155]
- Fedora: ARMv7: build for 16 CPUs. (Peter Robinson)
- Fedora: only enable DEBUG_HIGHMEM on debug kernels (Peter Robinson)

* Mon Feb 15 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-154]
- process_configs.sh: fix find/xargs data flow (Ondrej Mosnacek)

* Sat Feb 13 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc7.20210213gitdcc0b49040c7.151]
- Fedora config update (Justin M. Forbes)

* Fri Feb 12 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc7.20210212git291009f656e8.150]
- fedora: minor arm sound config updates (Peter Robinson)

* Wed Feb 10 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc7.20210210gite0756cfc7d7c.149]
- Fix trailing white space in redhat/configs/fedora/generic/CONFIG_SND_INTEL_BYT_PREFER_SOF (Justin M. Forbes)
- Add a redhat/rebase-notes.txt file (Hans de Goede)
- Turn on SND_INTEL_BYT_PREFER_SOF for Fedora (Hans de Goede)
- ALSA: hda: intel-dsp-config: Add SND_INTEL_BYT_PREFER_SOF Kconfig option (Hans de Goede) [1924101]
- CI: Drop MR ID from the name variable (Veronika Kabatova)

* Mon Feb 08 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc7.148]
- redhat: add DUP and kpatch certificates to system trusted keys for RHEL build (Herton R. Krzesinski)

* Mon Feb 08 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc6.20210208git825b5991a46e.147]
- The comments in CONFIG_USB_RTL8153_ECM actually turn off CONFIG_USB_RTL8152 (Justin M. Forbes)

* Sat Feb 06 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc6.20210206git17fbcdf9f163.145]
- Update CKI pipeline project (Veronika Kabatova)

* Fri Feb 05 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc6.20210205gitdd86e7fa07a3.144]
- Turn off additional KASAN options for Fedora (Justin M. Forbes)
- Rename the master branch to rawhide for Fedora (Justin M. Forbes)

* Thu Feb 04 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc6.20210204git61556703b610.143]
- Makefile targets for packit integration (Ben Crocker)
- Turn off KASAN for rawhide debug builds (Justin M. Forbes)
- New configs in arch/arm64 (Justin Forbes)
- Remove deprecated Intel MIC config options (Peter Robinson)

* Wed Feb 03 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc6.20210203git3aaf0a27ffc2.142]
- redhat: replace inline awk script with genlog.py call (Herton R. Krzesinski)
- redhat: add genlog.py script (Herton R. Krzesinski)
- kernel.spec.template - fix use_vdso usage (Ben Crocker)

* Tue Feb 02 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc6.20210202git88bb507a74ea.141]
- redhat: remove remaining references of CONFIG_RH_DISABLE_DEPRECATED ("Herton R. Krzesinski")
- .gitignore: fix previous mismerge with "HEAD line" ("Herton R. Krzesinski")
- Turn off vdso_install for ppc ("Justin M. Forbes")

* Sun Jan 31 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc5.20210131git0e9bcda5d286.139]
- Remove bpf-helpers.7 from bpftool package (Jiri Olsa)

* Sat Jan 30 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc5.20210130git0e9bcda5d286.138]
- New configs in lib/Kconfig.debug (Fedora Kernel Team)

* Fri Jan 29 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc5.20210129gitbec4c2968fce.137]
- Turn off CONFIG_VIRTIO_CONSOLE for s390x zfcpdump ("Justin M. Forbes")

* Thu Jan 28 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc5.20210128git76c057c84d28.136]
- Keep VIRTIO_CONSOLE on s390x available. (=?UTF-8?q?Jakub=20=C4=8Cajka?=)
- New configs in drivers/clk ("Justin M. Forbes")

* Wed Jan 27 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc5.20210127git2ab38c17aac1.135]
- New configs in lib/Kconfig.debug (Jeremy Cline)

* Mon Jan 25 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc5.133]
- Fedora 5.11 config updates part 4 ("Justin M. Forbes")
- Fedora 5.11 config updates part 3 ("Justin M. Forbes")
- Fedora 5.11 config updates part 2 ("Justin M. Forbes")
- Update internal (test) module list from RHEL-8 (Joe Lawrence) [https://bugzilla.redhat.com/show_bug.cgi?id=1915073]

* Thu Jan 21 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc4.20210121git9791581c049c.131]
- Fix USB_XHCI_PCI regression ("Justin M. Forbes")
- fedora: fixes for ARMv7 build issue by disabling HIGHPTE (Peter Robinson)

* Tue Jan 19 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc4.20210119git1e2a199f6ccd.129]
- all: s390x: Increase CONFIG_PCI_NR_FUNCTIONS to 512 (#1888735) (=?UTF-8?q?Dan=20Hor=C3=A1k?=)

* Sat Jan 16 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc3.20210116git1d94330a437a.126]
- Fedora 5.11 configs pt 1 ("Justin M. Forbes")

* Fri Jan 15 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc3.20210115git5ee88057889b.125]
- redhat: avoid conflict with mod-blacklist.sh and released_kernel defined ("Herton R. Krzesinski")
- redhat: handle certificate files conditionally as done for src.rpm ("Herton R. Krzesinski")
- Run MR testing in CKI pipeline (Veronika Kabatova)
- specfile: add {?_smp_mflags} to "make headers_install" in tools/testing/selftests (Denys Vlasenko)
- specfile: add {?_smp_mflags} to "make samples/bpf/" (Denys Vlasenko)

* Thu Jan 14 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc3.20210114git65f0d2414b70.124]
- Reword comment (Nicolas Chauvet)
- Add with_cross_arm conditional (Nicolas Chauvet)
- Redefines __strip if with_cross (Nicolas Chauvet)

* Wed Jan 13 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc3.20210113gite609571b5ffa.123]
- fedora: only enable ACPI_CONFIGFS, ACPI_CUSTOM_METHOD in debug kernels (Peter Robinson)
- fedora: User the same EFI_CUSTOM_SSDT_OVERLAYS as ARK (Peter Robinson)
- all: all arches/kernels enable the same DMI options (Peter Robinson)
- all: move SENSORS_ACPI_POWER to common/generic (Peter Robinson)
- fedora: PCIE_HISI_ERR is already in common (Peter Robinson)
- all: all ACPI platforms enable ATA_ACPI so move it to common (Peter Robinson)
- all: x86: move shared x86 acpi config options to generic (Peter Robinson)
- All: x86: Move ACPI_VIDEO to common/x86 (Peter Robinson)
- All: x86: Enable ACPI_DPTF (Intel DPTF) (Peter Robinson)
- All: enable ACPI_BGRT for all ACPI platforms. (Peter Robinson)
- All: Only build ACPI_EC_DEBUGFS for debug kernels (Peter Robinson)
- All: Disable Intel Classmate PC ACPI_CMPC option (Peter Robinson)
- cleanup: ACPI_PROCFS_POWER was removed upstream (Peter Robinson)
- All: ACPI: De-dupe the ACPI options that are the same across ark/fedora on x86/arm (Peter Robinson)

* Tue Jan 12 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc3.20210112gita0d54b4f5b21.122]
- Enable the vkms module in Fedora (Jeremy Cline)

* Sat Jan 09 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc2.20210109git996e435fd401.119]
- Revert "Merge branch 'revert-29a48502' into 'os-build'" (Justin Forbes)

* Fri Jan 08 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc2.20210108gitf5e6c330254a.118]
- Fedora: arm updates for 5.11 and general cross Fedora cleanups (Peter Robinson)

* Thu Jan 07 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc2.20210107git71c061d24438.117]
- Add gcc-c++ to BuildRequires ("Justin M. Forbes")

* Wed Jan 06 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc2.20210106git36bbbd0e234d.116]
- Update CONFIG_KASAN_HW_TAGS ("Justin M. Forbes")
- gcc-plugins: fix gcc 11 indigestion with plugins... (=?UTF-8?q?Valdis=20Kl=C4=93tnieks?=)
- fedora: arm: move generic power off/reset to all arm (Peter Robinson)
- fedora: ARMv7: build in DEVFREQ_GOV_SIMPLE_ONDEMAND until I work out why it's changed (Peter Robinson)
- fedora: cleanup joystick_adc (Peter Robinson)
- fedora: update some display options (Peter Robinson)
- fedora: arm: enable TI PRU options (Peter Robinson)
- fedora: arm: minor exynos plaform updates (Peter Robinson)
- arm: SoC: disable Toshiba Visconti SoC (Peter Robinson)
- common: disable ARCH_BCM4908 (NFC) (Peter Robinson)
- fedora: minor arm config updates (Peter Robinson)
- fedora: enable Tegra 234 SoC (Peter Robinson)
- fedora: arm: enable new Hikey 3xx options (Peter Robinson)
- Fedora: USB updates (Peter Robinson)
- fedora: enable the GNSS receiver subsystem (Peter Robinson)
- Remove POWER_AVS as no longer upstream (Peter Robinson)
- Cleanup RESET_RASPBERRYPI (Peter Robinson)
- Cleanup GPIO_CDEV_V1 options. (Peter Robinson)
- fedora: arm crypto updates (Peter Robinson)

* Tue Jan 05 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc2.20210105git36bbbd0e234d.115]
- Revert "Merge branch 'ark-enable-structleak' into 'os-build'" (Justin Forbes)
- CONFIG_KASAN_HW_TAGS for aarch64 ("Justin M. Forbes")
- Fix up bad merge with efi: generalize efi_get_secureboot ("Justin M. Forbes")

* Sun Jan 03 2021 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc1.20210103giteda809aef534.113]
- Fedora: cleanup PCMCIA configs, move to x86 (Peter Robinson)

* Wed Dec 23 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc0.20201223git614cb5894306.107]
- New configs in drivers/rtc (Fedora Kernel Team)
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK_BYREF_ALL (Josh Poimboeuf)
- redhat/configs: Enable CONFIG_GCC_PLUGIN_STRUCTLEAK (Josh Poimboeuf)
- redhat/configs: Enable CONFIG_GCC_PLUGINS on ARK (Josh Poimboeuf)
- redhat/configs: Enable CONFIG_KASAN on Fedora (Josh Poimboeuf)
- build_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- genspec.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- mod-blacklist.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Enable Speakup accessibility driver ("Justin M. Forbes")
- New configs in init/Kconfig (Fedora Kernel Team)
- New configs in init/Kconfig (Fedora Kernel Team)

* Mon Dec 21 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc0.20201221git8653b778e454.106]
- Fix fedora config mismatch due to dep changes ("Justin M. Forbes")
- Remove duplicate ENERGY_MODEL configs (Peter Robinson)
- New configs in drivers/crypto (Jeremy Cline)

* Fri Dec 18 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc0.20201218gita409ed156a90.102]
- This is selected by PCIE_QCOM so must match ("Justin M. Forbes")

* Wed Dec 16 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc0.20201216gite994cc240a3b.101]
- drop unused BACKLIGHT_GENERIC (Peter Robinson)

* Tue Dec 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.11.0-0.rc0.20201215git148842c98a24.100]
- Add missing '$' sign to (GIT) in redhat/Makefile (Augusto Caringi)
- Remove filterdiff and use native git instead (Don Zickus)
- kernel: Update some missing KASAN/KCSAN options (Jeremy Linton)
- kernel: Enable coresight on aarch64 (Jeremy Linton)
- redhat: ark: enable CONFIG_IKHEADERS (Jiri Olsa)
- fedora: some minor arm audio config tweaks (Peter Robinson)
- fedora: move CONFIG_RTC_NVMEM options from ark to common (Peter Robinson)
- redhat: explicitly disable CONFIG_IMA_APPRAISE_SIGNED_INIT (Bruno Meneguele)
- redhat: enable CONFIG_EVM_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM_ATTR_FSUUID on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM in all arches and flavors (Bruno Meneguele)
- redhat: enable CONFIG_IMA_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: set CONFIG_IMA_DEFAULT_HASH to SHA256 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT (Bruno Meneguele)
- redhat: enable CONFIG_IMA_READ_POLICY on ARK (Bruno Meneguele)
- redhat: set default IMA template for all ARK arches (Bruno Meneguele)
- redhat: enable CONFIG_IMA_DEFAULT_HASH_SHA256 for all flavors (Bruno Meneguele)
- redhat: disable CONFIG_IMA_DEFAULT_HASH_SHA1 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_ARCH_POLICY for ppc and x86 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_MODSIG (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_BOOTPARAM (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE (Bruno Meneguele)
- redhat: enable CONFIG_INTEGRITY for aarch64 (Bruno Meneguele)
- Ship xpad with default modules on Fedora and RHEL (Bastien Nocera)
- configs: Enable CONFIG_DEBUG_INFO_BTF (Don Zickus)
- Remove cp instruction already handled in instruction below. ("Paulo E. Castro")
- Add all the dependencies gleaned from running `make prepare` on a bloated devel kernel. ("Paulo E. Castro")
- Add tools to path mangling script. ("Paulo E. Castro")
- Remove duplicate cp statement which is also not specific to x86. ("Paulo E. Castro")
- Correct orc_types failure whilst running `make prepare` https://bugzilla.redhat.com/show_bug.cgi?id=1882854 ("Paulo E. Castro")
- Fedora config update ("Justin M. Forbes")
- Fedora config change because CONFIG_FSL_DPAA2_ETH now selects CONFIG_FSL_XGMAC_MDIO ("Justin M. Forbes")
- Fedora: Only enable legacy serial/game port joysticks on x86 (Peter Robinson)
- Fedora: Enable the options required for the Librem 5 Phone (Peter Robinson)
- Temporarily backout parallel xz script ("Justin M. Forbes")
- Fedora config update ("Justin M. Forbes")
- Enable NANDSIM for Fedora ("Justin M. Forbes")
- Re-enable CONFIG_ACPI_TABLE_UPGRADE for Fedora since upstream disables this if secureboot is active ("Justin M. Forbes")
- Ath11k related config updates ("Justin M. Forbes")
- Fedora config updates for ath11k ("Justin M. Forbes")
- Turn on ATH11K for Fedora ("Justin M. Forbes")
- redhat: generic  enable CONFIG_INET_MPTCP_DIAG (Davide Caratti)
- More Fedora config fixes ("Justin M. Forbes")
- Fedora 5.10 config updates ("Justin M. Forbes")
- Fedora 5.10 configs round 1 ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- redhat: enable CONFIG_INTEL_IOMMU_SVM (Jerry Snitselaar)
- Update CONFIG_INET6_ESPINTCP (Justin Forbes)
- Fix LTO issues with kernel-tools (Don Zickus)
- Allow building of kernel-tools standalone (Don Zickus)
- Allow kernel-tools to build without selftests (Don Zickus)
- Fix up a merge issue with rxe.c ("Justin M. Forbes")
- Point pathfix to the new location for gen_compile_commands.py ("Justin M. Forbes")
- [Automatic] Handle config dependency changes (Don Zickus)
- New configs in drivers/mfd (Fedora Kernel Team)
- New configs in drivers/mfd ("CKI@GitLab")
- New configs in drivers/mfd (Fedora Kernel Team)
- New configs in drivers/firmware (Fedora Kernel Team)
- arm64/defconfig: Enable CONFIG_KEXEC_FILE (Bhupesh Sharma) [https://bugzilla.redhat.com/show_bug.cgi?id=1821565]
- Fix Fedora config locations ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Partial revert: Add master merge check (Don Zickus)
- Add CONFIG_ARM64_MTE which is not picked up by the config scripts for some reason ("Justin M. Forbes")
- configs: enable CONFIG_CRYPTO_CTS=y so cts(cbc(aes)) is available in FIPS mode (Vladis Dronov)
- Disable Speakup synth DECEXT ("Justin M. Forbes")
- Enable Speakup for Fedora since it is out of staging ("Justin M. Forbes")
- WIP: redhat/docs: Update documentation for single branch workflow (Prarit Bhargava)
- Update Maintainers doc to reflect workflow changes (Don Zickus)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Modify patchlist changelog output (Don Zickus)
- configs: Disable CONFIG_SECURITY_SELINUX_DISABLE (Ondrej Mosnacek)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Fix path location for ark-update-configs.sh (Don Zickus)
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)
- Stop merging ark-patches for release (Don Zickus)
- Combine Red Hat patches into single patch (Don Zickus)
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)
- Updated changelog for the release based on 22fbc037cd32 (Fedora Kernel Team)
- Updated changelog for the release based on d3d45f8220d6 (Fedora Kernel Team)
- Updated changelog for the release based on 472e5b056f00 (Fedora Kernel Team)
- Set SquashFS decompression options for all flavors to match RHEL (Bohdan Khomutskyi)
- Updated changelog for the release based on 60e720931556 (Fedora Kernel Team)
- New configs in drivers/pinctrl (Fedora Kernel Team)
- Updated changelog for the release based on 02de58b24d2e (Fedora Kernel Team)
- New configs in drivers/misc (Jeremy Cline)
- New configs in net/sched ("Justin M. Forbes")
- New configs in net/ipv6 ("Justin M. Forbes")
- New configs in drivers/net/wireless ("Justin M. Forbes")
- Update CONFIG_THERMAL_NETLINK (Justin Forbes)
- New configs in kernel/trace (Fedora Kernel Team)
- configs/iommu: Add config comment to empty CONFIG_SUN50I_IOMMU file (Jerry Snitselaar)
- New configs in drivers/phy (Fedora Kernel Team)
- New configs in drivers/tty (Fedora Kernel Team)
- Updated changelog for the release based on fb0155a09b02 (Fedora Kernel Team)
- redhat/self-test: Initial commit (Ben Crocker)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)
- Separate merge-upstream and release stages (Don Zickus)
- redhat/configs: Cleanup CONFIG_CRYPTO_SHA512 (Prarit Bhargava)
- Re-enable CONFIG_IR_SERIAL on Fedora (Prarit Bhargava)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)
- Updated changelog for the release based on a1bffa48745a (Fedora Kernel Team)
- Updated changelog for the release based on 7c7ec3226f5f (Fedora Kernel Team)
- Create Patchlist.changelog file (Don Zickus)
- Filter out upstream commits from changelog (Don Zickus)
- Merge Upstream script fixes (Don Zickus)
- Updated changelog for the release based on 171d4ff79f96 (Fedora Kernel Team)
- generate_all_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- process_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Updated changelog for the release based on c9c9e6a49f89 (Fedora Kernel Team)
- Updated changelog for the release based on 805c6d3c1921 (Fedora Kernel Team)
- Updated changelog for the release based on 98477740630f (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc6 (Fedora Kernel Team)
- Updated changelog for the release based on fc4f28bb3daf (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc5 (Fedora Kernel Team)
- Updated changelog for the release based on ef2e9a563b0c (Fedora Kernel Team)
- Updated changelog for the release based on 729e3d091984 (Fedora Kernel Team)
- dist-merge-upstream: Checkout known branch for ci scripts (Don Zickus)
- Updated changelog for the release based on 581cb3a26baf (Fedora Kernel Team)
- Filter out LTO build options from the perl ccopts ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- kernel.spec: don't override upstream compiler flags for ppc64le (=?UTF-8?q?Dan=20Hor=C3=A1k?=)
- Updated changelog for the release based on v5.9-rc4 (Fedora Kernel Team)
- Updated changelog for the release based on dd9fb9bb3340 (Fedora Kernel Team)
- Updated changelog for the release based on c70672d8d316 (Fedora Kernel Team)
- Fedora confi gupdate ("Justin M. Forbes")
- Updated changelog for the release based on 59126901f200 (Fedora Kernel Team)
- Updated changelog for the release based on fc3abb53250a (Fedora Kernel Team)
- Fedora config change ("Justin M. Forbes")
- Updated changelog for the release based on 9c7d619be5a0 (Fedora Kernel Team)
- Updated changelog for the release based on b51594df17d0 (Fedora Kernel Team)
- Fedora filter update ("Justin M. Forbes")
- Config update for Fedora ("Justin M. Forbes")
- Updated changelog for the release based on v5.9-rc3 (Fedora Kernel Team)
- Updated changelog for the release based on 1127b219ce94 (Fedora Kernel Team)
- Updated changelog for the release based on 4d41ead6ead9 (Fedora Kernel Team)
- mod-sign.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Updated changelog for the release based on 15bc20c6af4c (Fedora Kernel Team)
- Updated changelog for the release based on 2ac69819ba9e (Fedora Kernel Team)
- Updated changelog for the release based on 6a9dc5fd6170 (Fedora Kernel Team)
- Updated changelog for the release based on v5.9-rc2 (Fedora Kernel Team)
- Updated changelog for the release based on c3d8f220d012 (Fedora Kernel Team)
- Updated changelog for the release based on f873db9acd3c (Fedora Kernel Team)
- Swap how ark-latest is built (Don Zickus)
- Add extra version bump to os-build branch (Don Zickus)
- dist-release: Avoid needless version bump. (Don Zickus)
- Add dist-fedora-release target (Don Zickus)
- Remove redundant code in dist-release (Don Zickus)
- Makefile.common rename TAG to _TAG (Don Zickus)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on da2968ff879b (Fedora Kernel Team)
- Updated changelog for the release based on 18445bf405cb (Fedora Kernel Team)
- Add mlx5_vdpa to module filter for Fedora ("Justin M. Forbes")
- Add python3-sphinx_rtd_theme buildreq for docs ("Justin M. Forbes")
- More Fedora config updates ("Justin M. Forbes")
- New config deps ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Updated changelog for the release based on 06a4ec1d9dc6 (Fedora Kernel Team)
- First half of config updates for Fedora ("Justin M. Forbes")
- Add config options that only show up when we prep on arm ("Justin M. Forbes")
- Config updates for Fedora ("Justin M. Forbes")
- fedora: enable enery model (Peter Robinson)
- iio: enable LTR-559 light and proximity sensor (Peter Robinson)
- iio: chemical: enable some popular chemical and partical sensors (Peter Robinson)
- More mismatches ("Justin M. Forbes")
- Fedora config change due to deps ("Justin M. Forbes")
- CONFIG_SND_SOC_MAX98390 is now selected by SND_SOC_INTEL_DA7219_MAX98357A_GENERIC ("Justin M. Forbes")
- Config change required for build part 2 ("Justin M. Forbes")
- Config change required for build ("Justin M. Forbes")
- Fixes "acpi: prefer booting with ACPI over DTS" to be RHEL only (Peter Robinson)
- arch/x86: Remove vendor specific CPU ID checks (Prarit Bhargava)
- redhat: Replace hardware.redhat.com link in Unsupported message (Prarit Bhargava)
- x86: Fix compile issues with rh_check_supported() (Don Zickus)
- e1000e: bump up timeout to wait when ME un-configure ULP mode (Aaron Ma)
- drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation (Icenowy Zheng)
- drm: panel: add Xingbangda XBD599 panel (Icenowy Zheng)
- dt-bindings: panel: add binding for Xingbangda XBD599 panel (Icenowy Zheng)
- ARM: fix __get_user_check() in case uaccess_* calls are not inlined (Masahiro Yamada)
- mm/kmemleak: skip late_init if not skip disable (Murphy Zhou)
- KEYS: Make use of platform keyring for module signature verify (Robert Holmes)
- Drop that for now (Laura Abbott)
- Input: rmi4 - remove the need for artificial IRQ in case of HID (Benjamin Tissoires)
- ARM: tegra: usb no reset (Peter Robinson)
- arm: make CONFIG_HIGHPTE optional without CONFIG_EXPERT (Jon Masters)
- redhat: rh_kabi: deduplication friendly structs (Jiri Benc)
- redhat: rh_kabi add a comment with warning about RH_KABI_EXCLUDE usage (Jiri Benc)
- redhat: rh_kabi: introduce RH_KABI_EXTEND_WITH_SIZE (Jiri Benc)
- redhat: rh_kabi: Indirect EXTEND macros so nesting of other macros will resolve. (Don Dutile)
- redhat: rh_kabi: Fix RH_KABI_SET_SIZE to use dereference operator (Tony Camuso)
- redhat: rh_kabi: Add macros to size and extend structs (Prarit Bhargava)
- Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy) [1572321]
- mptsas: pci-id table changes (Laura Abbott)
- mptsas: Taint kernel if mptsas is loaded (Laura Abbott)
- mptspi: pci-id table changes (Laura Abbott)
- qla2xxx: Remove PCI IDs of deprecated adapter (Jeremy Cline)
- be2iscsi: remove unsupported device IDs (Chris Leech) [1574502]
- mptspi: Taint kernel if mptspi is loaded (Laura Abbott)
- hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek) [1471185]
- qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis) [1518874]
- aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta) [1495307]
- megaraid_sas: remove deprecated pci-ids (Tomas Henzl) [1509329]
- mpt*: remove certain deprecated pci-ids (Jeremy Cline)
- kernel: add SUPPORT_REMOVED kernel taint (Tomas Henzl) [1602033]
- Rename RH_DISABLE_DEPRECATED to RHEL_DIFFERENCES (Don Zickus)
- Add option of 13 for FORCE_MAX_ZONEORDER (Peter Robinson)
- s390: Lock down the kernel when the IPL secure flag is set (Jeremy Cline)
- efi: Lock down the kernel if booted in secure boot mode (David Howells)
- efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (David Howells)
- security: lockdown: expose a hook to lock the kernel down (Jeremy Cline)
- Make get_cert_list() use efi_status_to_str() to print error messages. (Peter Jones)
- Add efi_status_to_str() and rework efi_status_to_err(). (Peter Jones)
- Add support for deprecating processors (Laura Abbott)
- arm: aarch64: Drop the EXPERT setting from ARM64_FORCE_52BIT (Jeremy Cline)
- iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- rh_kabi: introduce RH_KABI_EXCLUDE (Jakub Racek) [1652256]
- ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1670017]
- IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- scsi: smartpqi: add inspur advantech ids (Don Brace) [1503736]
- ice: mark driver as tech-preview (Jonathan Toppins) [1495347]
- kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- add pci_hw_vendor_status() (Maurizio Lombardi) [1590829]
- ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1563590]
- Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1563590]
- bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- tags.sh: Ignore redhat/rpm (Jeremy Cline)
- put RHEL info into generated headers (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1663728]
- kdump: add support for crashkernel=auto (Jeremy Cline)
- kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- modules: add rhelversion MODULE_INFO tag (Laura Abbott)
- ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- Add Red Hat tainting (Laura Abbott)
- Introduce CONFIG_RH_DISABLE_DEPRECATED (Laura Abbott)
- Updates for Fedora arm architectures for the 5.9 window (Peter Robinson)
- Enable ARM_SMCCC_SOC_ID on all aarch64 kernels (Peter Robinson)
- Enable ZSTD compression algorithm on all kernels (Peter Robinson)
- Fedora config update ("Justin M. Forbes")
- Revert "Merge branch 'make_configs_fix' into 'os-build'" (Justin Forbes)
- Use the configs/generic config for SND_HDA_INTEL everywhere (Peter Robinson)
- enable PROTECTED_VIRTUALIZATION_GUEST for all s390x kernels (=?UTF-8?q?Dan=20Hor=C3=A1k?=)
- kernel.spec: Remove kernel-keys directory on rpm erase (Prarit Bhargava)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on v5.8 (Fedora Kernel Team)
- Updated changelog for the release based on ac3a0c847296 (Fedora Kernel Team)
- Updated changelog for the release based on 7dc6fd0f3b84 (Fedora Kernel Team)
- redhat: ark: enable CONFIG_NET_SCH_TAPRIO (Davide Caratti)
- redhat: ark: enable CONFIG_NET_SCH_ETF (Davide Caratti)
- Add ability to sync upstream through Makefile (Don Zickus)
- Add master merge check (Don Zickus)
- Replace hardcoded values 'os-build' and project id with variables (Don Zickus)
- Updated changelog for the release based on 417385c47ef7 (Fedora Kernel Team)
- gitattributes: Remove unnecesary export restrictions (Prarit Bhargava)
- redhat/Makefile.common: Fix MARKER (Prarit Bhargava)
- Add new certs for dual signing with boothole ("Justin M. Forbes")
- Update secureboot signing for dual keys ("Justin M. Forbes")
- Updated changelog for the release based on d3590ebf6f91 (Fedora Kernel Team)
- Updated changelog for the release based on 6ba1b005ffc3 (Fedora Kernel Team)
- redhat: ark: disable CONFIG_NET_ACT_CTINFO (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_TEQL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_SFB (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_QFQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PLUG (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PIE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_MULTIQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_HHF (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DSMARK (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DRR (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CODEL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CHOKE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CBQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_ATM (Davide Caratti)
- redhat: ark: disable CONFIG_NET_EMATCH and sub-targets (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_TCINDEX (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP6 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_ROUTE4 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_BASIC (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SKBMOD (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SIMP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_NAT (Davide Caratti)
- fedora: enable LEDS_SGM3140 for arm configs (Peter Robinson)
- Updated changelog for the release based on v5.8-rc7 (Fedora Kernel Team)
- Updated changelog for the release based on 04300d66f0a0 (Fedora Kernel Team)
- Updated changelog for the release based on 23ee3e4e5bd2 (Fedora Kernel Team)
- configs: Enable CONFIG_ENERGY_MODEL (Phil Auld)
- Enable CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG ("Justin M. Forbes")
- Updated changelog for the release based on f37e99aca03f (Fedora Kernel Team)
- Updated changelog for the release based on d15be546031c (Fedora Kernel Team)
- fedora: arm: Update some meson config options (Peter Robinson)
- redhat/configs: Fix common CONFIGs (Prarit Bhargava)
- redhat/configs: General CONFIG cleanups (Prarit Bhargava)
- redhat/configs: Update & generalize evaluate_configs (Prarit Bhargava)
- Updated changelog for the release based on 4fa640dc5230 (Fedora Kernel Team)
- Updated changelog for the release based on 5714ee50bb43 (Fedora Kernel Team)
- Updated changelog for the release based on f932d58abc38 (Fedora Kernel Team)
- Updated changelog for the release based on 6a70f89cc58f (Fedora Kernel Team)
- Updated changelog for the release based on 07a56bb875af (Fedora Kernel Team)
- redhat/docs: Add Fedora RPM tagging date (Prarit Bhargava)
- Updated changelog for the release based on e9919e11e219 (Fedora Kernel Team)
- Update config for renamed panel driver. (Peter Robinson)
- Enable SERIAL_SC16IS7XX for SPI interfaces (Peter Robinson)
- Updated changelog for the release based on dcde237b9b0e (Fedora Kernel Team)
- Updated changelog for the release based on v5.8-rc4 (Fedora Kernel Team)
- Updated changelog for the release based on cd77006e01b3 (Fedora Kernel Team)
- Fedora config updates ("Justin M. Forbes")
- Updated changelog for the release based on v5.8-rc3 (Fedora Kernel Team)
- s390x-zfcpdump: Handle missing Module.symvers file (Don Zickus)
- Updated changelog for the release based on 8be3a53e18e0 (Fedora Kernel Team)
- redhat/configs: Add .tmp files to .gitignore (Prarit Bhargava)
- disable uncommon TCP congestion control algorithms (Davide Caratti)
- Updated changelog for the release based on dd0d718152e4 (Fedora Kernel Team)
- Add new bpf man pages ("Justin M. Forbes")
- Add default option for CONFIG_ARM64_BTI_KERNEL to pending-common so that eln kernels build ("Justin M. Forbes")
- Updated changelog for the release based on 625d3449788f (Fedora Kernel Team)
- Updated changelog for the release based on 1b5044021070 (Fedora Kernel Team)
- redhat/Makefile: Add fedora-configs and rh-configs make targets (Prarit Bhargava)
- Updated changelog for the release based on 69119673bd50 (Fedora Kernel Team)
- redhat/configs: Use SHA512 for module signing (Prarit Bhargava)
- Updated changelog for the release based on a5dc8300df75 (Fedora Kernel Team)
- genspec.sh: 'touch' empty Patchlist file for single tarball (Don Zickus)
- Fedora config update for rc1 ("Justin M. Forbes")
- Updated changelog for the release based on v5.8-rc1 (Fedora Kernel Team)
- Fedora config updates ("Justin M. Forbes")
- Updated changelog for the release based on df2fbf5bfa0e (Fedora Kernel Team)
- Fedora config updates ("Justin M. Forbes")
- Updated changelog for the release based on b791d1bdf921 (Fedora Kernel Team)
- One more Fedora config update ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Change ark CONFIG_COMMON_CLK to yes, it is selected already by other options ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Fix PATCHLEVEL for merge window ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- More module filtering for Fedora ("Justin M. Forbes")
- Update filters for rnbd in Fedora ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- redhat/Makefile.common: fix RPMKSUBLEVEL condition (Ondrej Mosnacek)
- redhat/Makefile: silence KABI tar output (Ondrej Mosnacek)
- Fix up module filtering for 5.8 ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- More Fedora config work ("Justin M. Forbes")
- RTW88BE and CE have been extracted to their own modules ("Justin M. Forbes")
- Set CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK for Fedora ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Arm64 Use Branch Target Identification for kernel ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Change value of CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE ("Justin M. Forbes")
- Fix configs for Fedora ("Justin M. Forbes")
- Fix update_scripts.sh unselective pattern sub (David Howells)
- Updated changelog for the release based on b0c3ba31be3e ("CKI@GitLab")
- Updated changelog for the release based on 444fc5cde643 ("CKI@GitLab")
- Remove typoed config file aarch64CONFIG_SM_GCC_8150 ("Justin M. Forbes")
- Updated changelog for the release based on v5.7-rc7 ("CKI@GitLab")
- Updated changelog for the release based on caffb99b6929 ("CKI@GitLab")
- Updated changelog for the release based on 444565650a5f ("CKI@GitLab")
- redhat/Makefile: Fix RHEL8 python warning (Prarit Bhargava)
- redhat: Add dummy-module kernel module (Prarit Bhargava)
- kernel.spec: fix 'make scripts' for kernel-devel package (Brian Masney)
- Makefile: correct help text for dist-cross-<arch>-rpms (Brian Masney)
- Add Documentation back to kernel-devel as it has Kconfig now ("Justin M. Forbes")
- Updated changelog for the release based on 642b151f45dd ("CKI@GitLab")
- Drop the static path configuration for the Sphinx docs (Jeremy Cline)
- Updated changelog for the release based on v5.7-rc6 ("CKI@GitLab")
- Updated changelog for the release based on 3d1c1e5931ce ("CKI@GitLab")
- Updated changelog for the release based on 12bf0b632ed0 ("CKI@GitLab")
- Updated changelog for the release based on 1ae7efb38854 ("CKI@GitLab")
- redhat: Change Makefile target names to dist- (Prarit Bhargava)
- configs: Disable Serial IR driver (Prarit Bhargava)
- Updated changelog for the release based on 24085f70a6e1 ("CKI@GitLab")
- Updated changelog for the release based on 152036d1379f ("CKI@GitLab")
- Updated changelog for the release based on v5.7-rc5 ("CKI@GitLab")
- Updated changelog for the release based on e99332e7b4cd ("CKI@GitLab")
- Fix "multiple files for package kernel-tools" (Pablo Greco)
- Updated changelog for the release based on d5eeab8d7e26 ("CKI@GitLab")
- Add zero-commit to format-patch options ("Justin M. Forbes")
- Updated changelog for the release based on 79dede78c057 ("CKI@GitLab")
- Introduce a Sphinx documentation project (Jeremy Cline)
- Updated changelog for the release based on a811c1fa0a02 ("CKI@GitLab")
- Sign off generated configuration patches (Jeremy Cline)
- Updated changelog for the release based on dc56c5acd850 ("CKI@GitLab")
- Use __make macro instead of make (Tom Stellard)
- Build ARK against ELN (Don Zickus)
- Updated changelog for the release based on 47cf1b422e60 ("CKI@GitLab")
- Updated changelog for the release based on v5.7-rc4 ("CKI@GitLab")
- Updated changelog for the release based on f66ed1ebbfde ("CKI@GitLab")
- Updated changelog for the release based on 690e2aba7beb ("CKI@GitLab")
- redhat/configs: Enable CONFIG_SMC91X and disable CONFIG_SMC911X (Prarit Bhargava) [http://bugzilla.redhat.com/1722136]
- Updated changelog for the release based on c45e8bccecaf ("CKI@GitLab")
- Drop the requirement to have a remote called linus (Jeremy Cline)
- Rename 'internal' branch to 'os-build' (Don Zickus)
- Updated changelog for the release based on 1d2cc5ac6f66 ("CKI@GitLab")
- Only include open merge requests with "Include in Releases" label (Jeremy Cline)
- Copy Makefile.rhelver as a source file rather than a patch (Jeremy Cline)
- Exit non-zero if the tag already exists for a release (Jeremy Cline)
- Move the sed to clear the patch templating outside of conditionals ("Justin M. Forbes")
- Add cec to the filter overrides ("Justin M. Forbes")
- Add overrides to filter-modules.sh ("Justin M. Forbes")
- Adjust the changelog update script to not push anything (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- Updated changelog ("CKI@GitLab")
- Match template format in kernel.spec.template ("Justin M. Forbes")
- Break out the Patches into individual files for dist-git ("Justin M. Forbes")
- Break the Red Hat patch into individual commits (Jeremy Cline)
- Add a script to generate release tags and branches (Jeremy Cline)
- Set CONFIG_VDPA for fedora ("Justin M. Forbes")
- Drop --target noarch from the rh-rpms make target (Jeremy Cline)
- Provide defaults in ark-rebase-patches.sh (Jeremy Cline)
- Default ark-rebase-patches.sh to not report issues (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- Package gpio-watch in kernel-tools (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- Add a README to the dist-git repository (Jeremy Cline)
- Drop DIST from release commits and tags (Jeremy Cline)
- Copy distro files rather than moving them (Jeremy Cline)
- Place the buildid before the dist in the release (Jeremy Cline)
- Sync up with Fedora arm configuration prior to merging (Jeremy Cline)
- Disable CONFIG_PROTECTED_VIRTUALIZATION_GUEST for zfcpdump (Jeremy Cline)
- Include bpftool-struct_ops man page in the bpftool package (Jeremy Cline)
- Add sharedbuffer_configuration.py to the pathfix.py script (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- Drop RH_FEDORA in favor of the now-merged RHEL_DIFFERENCES (Jeremy Cline)
- Sync up Fedora configs from the first week of the merge window (Jeremy Cline)
- Add a script to test if all commits are signed off (Jeremy Cline)
- Fix a painfully obvious YAML syntax error in .gitlab-ci.yml (Jeremy Cline)
- Migrate blacklisting floppy.ko to mod-blacklist.sh (Don Zickus)
- kernel packaging: Combine mod-blacklist.sh and mod-extra-blacklist.sh (Don Zickus)
- kernel packaging: Fix extra namespace collision (Don Zickus)
- mod-extra.sh: Rename to mod-blacklist.sh (Don Zickus)
- mod-extra.sh: Make file generic (Don Zickus)
- Fix make rh-configs-arch (Don Zickus)
- Add in armv7hl kernel header support (Don Zickus)
- Disable all BuildKernel commands when only building headers (Don Zickus)
- Updated changelog ("CKI@GitLab")
- Add RHMAINTAINERS file and supporting conf (Don Zickus)
- Drop any gitlab-ci patches from ark-patches (Jeremy Cline)
- Build the srpm for internal branch CI using the vanilla tree (Jeremy Cline)
- Pull in the latest ARM configurations for Fedora (Jeremy Cline)
- Fix xz memory usage issue (Neil Horman)
- Use ark-latest instead of master for update script (Jeremy Cline)
- Move the CI jobs back into the ARK repository (Jeremy Cline)
- Revert "[redhat] Apply a second patch set in Fedora build roots" (Jeremy Cline)
- Sync up ARK's Fedora config with the dist-git repository (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- Pull in the latest configuration changes from Fedora (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- configs: enable CONFIG_NET_SCH_CBS (Marcelo Ricardo Leitner)
- Drop configuration options in fedora/ that no longer exist (Jeremy Cline)
- Set RH_FEDORA for ARK and Fedora (Jeremy Cline)
- redhat: enable CONFIG_LWTUNNEL_BPF (Jiri Benc)
- redhat/kernel.spec: Include the release in the kernel COPYING file (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- redhat/kernel.spec: add scripts/jobserver-exec to py3_shbang_opts list (Jeremy Cline)
- redhat/kernel.spec: package bpftool-gen man page (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- distgit-changelog: handle multiple y-stream BZ numbers (Bruno Meneguele)
- redhat/kernel.spec: remove all inline comments (Bruno Meneguele)
- redhat/genspec: awk unknown whitespace regex pattern (Bruno Meneguele)
- Improve the readability of gen_config_patches.sh (Jeremy Cline)
- Fix some awkward edge cases in gen_config_patches.sh (Jeremy Cline)
- Updated changelog (Jeremy Cline)
- Update the CI environment to use Fedora 31 (Jeremy Cline)
- Revert "Turn off CONFIG_AX25" (Laura Abbott)
- Updated changelog ("CKI@GitLab")
- Updated changelog ("CKI@GitLab")
- configs: Enable CONFIG_KEY_DH_OPERATIONS on ARK (Ondrej Mosnacek)
- redhat: drop whitespace from with_gcov macro (Jan Stancek) [INTERNAL]
- Updated changelog ("CKI@GitLab")
- Updated changelog ("CKI@GitLab")
- Updated changelog ("CKI@GitLab")
- Updated changelog ("CKI@GitLab")
- Turn on BLAKE2B for Fedora (Jeremy Cline)
- kernel.spec.template: Clean up stray *.h.s files (Laura Abbott)
- configs: Adjust CONFIG_MPLS_ROUTING and CONFIG_MPLS_IPTUNNEL (Laura Abbott)
- New configs in lib/crypto (Jeremy Cline)
- Build the SRPM in the CI job (Jeremy Cline)
- Fix up released_kernel case (Laura Abbott)
- New configs in drivers/char (Jeremy Cline)
- Add label so the Gitlab to email bridge ignores the changelog (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- Temporarily switch TUNE_DEFAULT to y (Jeremy Cline)
- Run config test for merge requests and internal (Jeremy Cline)
- Turn off CONFIG_AX25 (Laura Abbott)
- Add missing licensedir line (Laura Abbott)
- New configs in net/tls (Jeremy Cline)
- New configs in net/tipc (Jeremy Cline)
- New configs in lib/kunit (Jeremy Cline)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- New configs in drivers/ptp (Jeremy Cline)
- New configs in drivers/nvme (Jeremy Cline)
- New configs in drivers/net/phy (Jeremy Cline)
- New configs in drivers/crypto (Jeremy Cline)
- New configs in crypto/Kconfig (Jeremy Cline)
- New configs in arch/arm64 (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- redhat/scripts: Remove redhat/scripts/rh_get_maintainer.pl (Prarit Bhargava)
- configs: Take CONFIG_DEFAULT_MMAP_MIN_ADDR from Fedra (Laura Abbott)
- configs: Turn off ISDN (Laura Abbott)
- kernel-packaging: Remove kernel files from kernel-modules-extra package (Prarit Bhargava)
- Add a script to generate configuration patches (Laura Abbott)
- Introduce rh-configs-commit (Laura Abbott)
- Updated changelog ("CKI@GitLab")
- configs: Enable CONFIG_DEBUG_WX (Laura Abbott)
- configs: Disable wireless USB (Laura Abbott)
- Clean up some temporary config files (Laura Abbott)
- configs: New config in drivers/gpu for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/powerpc for v5.4-rc1 (Jeremy Cline)
- configs: New config in crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/usb for v5.4-rc1 (Jeremy Cline)
- AUTOMATIC: New configs (Jeremy Cline)
- Skip ksamples for bpf, they are broken (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- configs: New config in fs/erofs for v5.4-rc1 (Jeremy Cline)
- configs: New config in mm for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/md for v5.4-rc1 (Jeremy Cline)
- configs: New config in init for v5.4-rc1 (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- configs: New config in fs/fuse for v5.4-rc1 (Jeremy Cline)
- merge.pl: Avoid comments but do not skip them (Don Zickus)
- configs: New config in drivers/net/ethernet/pensando for v5.4-rc1 (Jeremy Cline)
- Update a comment about what released kernel means (Laura Abbott)
- Provide both Fedora and RHEL files in the SRPM (Laura Abbott)
- kernel.spec.template: Trim EXTRAVERSION in the Makefile (Laura Abbott)
- kernel.spec.template: Add macros for building with nopatches (Laura Abbott)
- kernel.spec.template: Add some macros for Fedora differences (Laura Abbott)
- kernel.spec.template: Consolodate the options (Laura Abbott)
- configs: Add pending direcory to Fedora (Laura Abbott)
- kernel.spec.template: Don't run hardlink if rpm-ostree is in use (Laura Abbott)
- configs: New config in net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/phy for v5.4-rc1 (Jeremy Cline)
- Updated changelog ("CKI@GitLab")
- configs: turn on ARM64_FORCE_52BIT for debug builds (Jeremy Cline)
- kernel.spec.template: Tweak the python3 mangling (Laura Abbott)
- kernel.spec.template: Add --with verbose option (Laura Abbott)
- kernel.spec.template: Switch to using install instead of __install (Laura Abbott)
- kernel.spec.template: Make the kernel.org URL https (Laura Abbott)
- kernel.spec.template: Update message about secure boot signing (Laura Abbott)
- kernel.spec.template: Move some with flags definitions up (Laura Abbott)
- kernel.spec.template: Update some BuildRequires (Laura Abbott)
- kernel.spec.template: Get rid of clean (Laura Abbott)
- configs: New config in drivers/char for v5.4-rc1 (Jeremy Cline)
- configs: New config in net/sched for v5.4-rc1 (Jeremy Cline)
- configs: New config in lib for v5.4-rc1 (Jeremy Cline)
- configs: New config in fs/verity for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/aarch64 for v5.4-rc4 (Jeremy Cline)
- configs: New config in arch/arm64 for v5.4-rc1 (Jeremy Cline)
- Flip off CONFIG_ARM64_VA_BITS_52 so the bundle that turns it on applies (Jeremy Cline)
- configs: Increase x86_64 NR_UARTS to 64 (Prarit Bhargava) [http://bugzilla.redhat.com/1730649]
- Update changelog (Laura Abbott)
- New configuration options for v5.4-rc4 (Jeremy Cline)
- Correctly name tarball for single tarball builds (Laura Abbott)
- configs: New config in drivers/pci for v5.4-rc1 (Jeremy Cline)
- Allow overriding the dist tag on the command line (Laura Abbott)
- Allow scratch branch target to be overridden (Laura Abbott)
- Remove long dead BUILD_DEFAULT_TARGET (Laura Abbott)
- Amend the changelog when rebasing (Laura Abbott)
- configs: New config in drivers/platform for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/pinctrl for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/wireless for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/ethernet/mellanox for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hid for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/dma-buf for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in block for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/cpuidle for v5.4-rc1 (Jeremy Cline)
- redhat: configs: Split CONFIG_CRYPTO_SHA512 (Laura Abbott)
- redhat: Set Fedora options (Laura Abbott)
- gitlab: Add CI job for packaging scripts (Major Hayden)
- Set CRYPTO_SHA3_*_S390 to builtin on zfcpdump (Jeremy Cline)
- configs: New config in drivers/edac for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/firmware for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hwmon for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/iio for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/mmc for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/tty for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/bus for v5.4-rc1 (Jeremy Cline)
- Add option to allow mismatched configs on the command line (Laura Abbott)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/pci for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/soc for v5.4-rc1 (Jeremy Cline)
- Speed up CI with CKI image (Major Hayden)
- configs: Fix the pending default for CONFIG_ARM64_VA_BITS_52 (Jeremy Cline)
- configs: Turn on OPTIMIZE_INLINING for everything (Jeremy Cline)
- configs: Set valid pending defaults for CRYPTO_ESSIV (Jeremy Cline)
- Add an initial CI configuration for the internal branch (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- Disable e1000 driver in ARK (Neil Horman)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- configs: Adjust CONFIG_FORCE_MAX_ZONEORDER for Fedora (Laura Abbott)
- configs: Add README for some other arches (Laura Abbott)
- configs: Sync up Fedora configs (Laura Abbott)
- Pull the RHEL version defines out of the Makefile (Jeremy Cline)
- Sync up the ARK build scripts (Jeremy Cline)
- Sync up the Fedora Rawhide configs (Jeremy Cline)
- Sync up the ARK config files (Jeremy Cline)
- [initial commit] Add structure for building with git (Laura Abbott)
- [initial commit] Add Red Hat variables in the top level makefile (Laura Abbott)
- [initial commit] Red Hat gitignore and attributes (Laura Abbott)
- [initial commit] Add changelog (Laura Abbott)
- [initial commit] Add makefile (Laura Abbott)
- [initial commit] Add files for generating the kernel.spec (Laura Abbott)
- [initial commit] Add rpm directory (Laura Abbott)
- [initial commit] Add files for packaging (Laura Abbott)
- [initial commit] Add kabi files (Laura Abbott)
- [initial commit] Add scripts (Laura Abbott)
- [initial commit] Add configs (Laura Abbott)
- [initial commit] Add Makefiles (Laura Abbott)

* Tue Dec 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-99]
- Add missing '$' sign to (GIT) in redhat/Makefile (Augusto Caringi)
- redhat: ark: enable CONFIG_IKHEADERS (Jiri Olsa)

* Sat Dec 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc7.20201212git7f376f1917d7.97]
- Remove filterdiff and use native git instead (Don Zickus)
- New configs in net/sched ("Justin M. Forbes")

* Fri Dec 11 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc7.20201211git33dc9614dc20.96]
- redhat: explicitly disable CONFIG_IMA_APPRAISE_SIGNED_INIT (Bruno Meneguele)
- redhat: enable CONFIG_EVM_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM_ATTR_FSUUID on ARK (Bruno Meneguele)
- redhat: enable CONFIG_EVM in all arches and flavors (Bruno Meneguele)
- redhat: enable CONFIG_IMA_LOAD_X509 on ARK (Bruno Meneguele)
- redhat: set CONFIG_IMA_DEFAULT_HASH to SHA256 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_SECURE_AND_OR_TRUSTED_BOOT (Bruno Meneguele)
- redhat: enable CONFIG_IMA_READ_POLICY on ARK (Bruno Meneguele)
- redhat: set default IMA template for all ARK arches (Bruno Meneguele)
- redhat: enable CONFIG_IMA_DEFAULT_HASH_SHA256 for all flavors (Bruno Meneguele)
- redhat: disable CONFIG_IMA_DEFAULT_HASH_SHA1 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_ARCH_POLICY for ppc and x86 (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_MODSIG (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE_BOOTPARAM (Bruno Meneguele)
- redhat: enable CONFIG_IMA_APPRAISE (Bruno Meneguele)
- redhat: enable CONFIG_INTEGRITY for aarch64 (Bruno Meneguele)
- Temporarily backout parallel xz script ("Justin M. Forbes")
- New configs in drivers/mfd (Fedora Kernel Team)
- New configs in drivers/mfd ("CKI@GitLab")
- New configs in drivers/firmware (Fedora Kernel Team)

* Thu Dec 10 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc7.20201210gita2f5ea9e314b.95]
- kernel: Update some missing KASAN/KCSAN options (Jeremy Linton)
- kernel: Enable coresight on aarch64 (Jeremy Linton)

* Wed Dec 09 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc7.20201209gita68a0262abda.94]
- Update CONFIG_INET6_ESPINTCP (Justin Forbes)
- New configs in net/ipv6 ("Justin M. Forbes")

* Tue Dec 08 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc7.93]
- fedora: move CONFIG_RTC_NVMEM options from ark to common (Peter Robinson)

* Mon Dec 07 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc7.92]
- configs: Enable CONFIG_DEBUG_INFO_BTF (Don Zickus)

* Thu Dec 03 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc6.20201203git34816d20f173.91]
- fedora: some minor arm audio config tweaks (Peter Robinson)
- Ship xpad with default modules on Fedora and RHEL (Bastien Nocera)

* Wed Dec 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc6.20201202git509a15421674.90]
- Fedora config update ("Justin M. Forbes")
- Fedora config change because CONFIG_FSL_DPAA2_ETH now selects CONFIG_FSL_XGMAC_MDIO ("Justin M. Forbes")
- Fedora: Only enable legacy serial/game port joysticks on x86 (Peter Robinson)
- Fedora: Enable the options required for the Librem 5 Phone (Peter Robinson)

* Fri Nov 20 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc4.20201120git4d02da974ea8.81]
- Fedora config update ("Justin M. Forbes")
- redhat: generic  enable CONFIG_INET_MPTCP_DIAG (Davide Caratti)

* Thu Nov 19 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc4.20201119gitc2e7554e1b85.79.test]
- c2e7554e1b85 rebase
- Enable NANDSIM for Fedora ("Justin M. Forbes")
- Re-enable CONFIG_ACPI_TABLE_UPGRADE for Fedora since upstream disables this if secureboot is active ("Justin M. Forbes")

* Wed Nov 18 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc4.20201118git0fa8ee0d9ab9.78.test]
- 0fa8ee0d9ab9 rebase

* Tue Nov 17 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc4.20201117git9c87c9f41245.77.test]
- 9c87c9f41245 rebase

* Mon Nov 16 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc4.76.test]
- v5.10-rc4 rebase
- Ath11k related config updates ("Justin M. Forbes")
- Fedora config updates for ath11k ("Justin M. Forbes")

* Sun Nov 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.20201115gite28c0d7c92c8.74.test]
- e28c0d7c92c8 rebase

* Sat Nov 14 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.20201114gitf01c30de86f1.73.test]
- f01c30de86f1 rebase
- Turn on ATH11K for Fedora ("Justin M. Forbes")

* Fri Nov 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.20201113git585e5b17b92d.72.test]
- 585e5b17b92d rebase

* Thu Nov 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.20201112git3d5e28bff7ad.71.test]
- 3d5e28bff7ad rebase

* Wed Nov 11 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.20201111giteccc87672492.68.test]
- eccc87672492 rebase
- redhat: enable CONFIG_INTEL_IOMMU_SVM (Jerry Snitselaar)

* Tue Nov 10 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.67.test]
- More Fedora config fixes ("Justin M. Forbes")
- Fedora 5.10 config updates ("Justin M. Forbes")

* Mon Nov 09 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc3.66.test]
- v5.10-rc3 rebase

* Sun Nov 08 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc2.20201108git4429f14aeea9.65.test]
- 4429f14aeea9 rebase

* Sat Nov 07 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc2.20201107git659caaf65dc9.64.test]
- 659caaf65dc9 rebase

* Fri Nov 06 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc2.20201106git521b619acdc8.63.test]
- 521b619acdc8 rebase
- Fedora 5.10 configs round 1 ("Justin M. Forbes")

* Wed Nov 04 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc2.20201104git4ef8451b3326.62.test]
- 4ef8451b3326 rebase

* Mon Nov 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc2.61.test]
- v5.10-rc2 rebase

* Sun Nov 01 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.20201101gitc2dc4c073fb7.60.test]
- c2dc4c073fb7 rebase

* Sat Oct 31 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.20201031git5fc6b075e165.59.test]
- 5fc6b075e165 rebase
- Allow building of kernel-tools standalone (Don Zickus)
- Allow kernel-tools to build without selftests (Don Zickus)

* Fri Oct 30 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.20201030git07e088730245.58.test]
- 07e088730245 rebase
- Fix LTO issues with kernel-tools (Don Zickus)
- New configs in drivers/mfd (Fedora Kernel Team)
- arm64/defconfig: Enable CONFIG_KEXEC_FILE (Bhupesh Sharma) [https://bugzilla.redhat.com/show_bug.cgi?id=1821565]
- redhat/configs: Cleanup CONFIG_CRYPTO_SHA512 (Prarit Bhargava)
- redhat: ark: disable CONFIG_NET_ACT_CTINFO (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_TEQL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_SFB (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_QFQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PLUG (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_PIE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_MULTIQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_HHF (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DSMARK (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_DRR (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CODEL (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CHOKE (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_CBQ (Davide Caratti)
- redhat: ark: disable CONFIG_NET_SCH_ATM (Davide Caratti)
- redhat: ark: disable CONFIG_NET_EMATCH and sub-targets (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_TCINDEX (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP6 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_RSVP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_ROUTE4 (Davide Caratti)
- redhat: ark: disable CONFIG_NET_CLS_BASIC (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SKBMOD (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_SIMP (Davide Caratti)
- redhat: ark: disable CONFIG_NET_ACT_NAT (Davide Caratti)

* Thu Oct 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.20201029git23859ae44402.57.test]
- 23859ae44402 rebase

* Thu Oct 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.20201029gited8780e3f2ec.56.test]
- Point pathfix to the new location for gen_compile_commands.py ("Justin M. Forbes")
- Filter out LTO build options from the perl ccopts ("Justin M. Forbes")

* Wed Oct 28 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.20201028gited8780e3f2ec.55.test]
- ed8780e3f2ec rebase
- Fix up a merge issue with rxe.c ("Justin M. Forbes")
- configs: Disable CONFIG_SECURITY_SELINUX_DISABLE (Ondrej Mosnacek)

* Mon Oct 26 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc1.54.test]
- v5.10-rc1 rebase

* Sat Oct 24 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201024git96485e446260.51.test]
- [Automatic] Handle config dependency changes (Don Zickus)

* Thu Oct 22 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201022git96485e446260.49.test]
- 96485e446260 rebase

* Thu Oct 22 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201022gitf804b3159482.48.test]
- f804b3159482 rebase
- New configs in kernel/trace (Fedora Kernel Team)
- configs/iommu: Add config comment to empty CONFIG_SUN50I_IOMMU file (Jerry Snitselaar)

* Tue Oct 20 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201020git071a0578b0ce.47.test]
- Fix Fedora config locations ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")

* Sat Oct 17 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201017git071a0578b0ce.44.test]
- 071a0578b0ce rebase
- configs: enable CONFIG_CRYPTO_CTS=y so cts(cbc(aes)) is available in FIPS mode (Vladis Dronov)

* Fri Oct 16 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201016git9ff9b0d392ea.43.test]
- 9ff9b0d392ea rebase
- Partial revert: Add master merge check (Don Zickus)

* Fri Oct 16 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201016git578a7155c5a1.42.test]
- 578a7155c5a1 rebase
- Update Maintainers doc to reflect workflow changes (Don Zickus)

* Thu Oct 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201015git3e4fb4346c78.41.test]
- 3e4fb4346c78 rebase
- WIP: redhat/docs: Update documentation for single branch workflow (Prarit Bhargava)

* Thu Oct 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201015gitb5fc7a89e58b.40.test]
- Add CONFIG_ARM64_MTE which is not picked up by the config scripts for some reason ("Justin M. Forbes")

* Wed Oct 14 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201014gitb5fc7a89e58b.39.test]
- b5fc7a89e58b rebase

* Tue Oct 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201013gitc4439713e82a.38.test]
- c4439713e82a rebase

* Tue Oct 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.10.0-0.rc0.20201013git865c50e1d279.37.test]
- 865c50e1d279 rebase

* Tue Oct 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-35.test]
- Disable Speakup synth DECEXT ("Justin M. Forbes")
- Enable Speakup for Fedora since it is out of staging ("Justin M. Forbes")

* Mon Oct 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-34.test]
- v5.9 rebase

* Mon Oct 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201012gitda690031a5d6.33.test]
- da690031a5d6 rebase

* Sun Oct 11 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201011git6f2f486d57c4.32.test]
- 6f2f486d57c4 rebase

* Sat Oct 10 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201010git583090b1b823.31.test]
- 583090b1b823 rebase
- redhat/self-test: Initial commit (Ben Crocker)
- generate_all_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- process_configs.sh: Fix syntax flagged by shellcheck (Ben Crocker)

* Fri Oct 09 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201009git7575fdda569b.31]
- Modify patchlist changelog output (Don Zickus)
- Filter out LTO build options from the perl ccopts ("Justin M. Forbes")
- Temporarily remove cdomain from sphinx documentation ("Justin M. Forbes")
- Work around for gcc bug https://gcc.gnu.org/bugzilla/show_bug.cgi?id=96377 ("Justin M. Forbes")

* Fri Oct 09 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201009git7575fdda569b.30.test]
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)
- Fix path location for ark-update-configs.sh (Don Zickus)
- Stop merging ark-patches for release (Don Zickus)
- Combine Red Hat patches into single patch (Don Zickus)
- Fixes "acpi: prefer booting with ACPI over DTS" to be RHEL only (Peter Robinson)
- arch/x86: Remove vendor specific CPU ID checks (Prarit Bhargava)
- redhat: Replace hardware.redhat.com link in Unsupported message (Prarit Bhargava)
- x86: Fix compile issues with rh_check_supported() (Don Zickus)
- e1000e: bump up timeout to wait when ME un-configure ULP mode (Aaron Ma)
- drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation (Icenowy Zheng)
- drm: panel: add Xingbangda XBD599 panel (Icenowy Zheng)
- dt-bindings: panel: add binding for Xingbangda XBD599 panel (Icenowy Zheng)
- ARM: fix __get_user_check() in case uaccess_* calls are not inlined (Masahiro Yamada)
- mm/kmemleak: skip late_init if not skip disable (Murphy Zhou)
- KEYS: Make use of platform keyring for module signature verify (Robert Holmes)
- Drop that for now (Laura Abbott)
- Input: rmi4 - remove the need for artificial IRQ in case of HID (Benjamin Tissoires)
- ARM: tegra: usb no reset (Peter Robinson)
- arm: make CONFIG_HIGHPTE optional without CONFIG_EXPERT (Jon Masters)
- redhat: rh_kabi: deduplication friendly structs (Jiri Benc)
- redhat: rh_kabi add a comment with warning about RH_KABI_EXCLUDE usage (Jiri Benc)
- redhat: rh_kabi: introduce RH_KABI_EXTEND_WITH_SIZE (Jiri Benc)
- redhat: rh_kabi: Indirect EXTEND macros so nesting of other macros will resolve. (Don Dutile)
- redhat: rh_kabi: Fix RH_KABI_SET_SIZE to use dereference operator (Tony Camuso)
- redhat: rh_kabi: Add macros to size and extend structs (Prarit Bhargava)
- Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy) [1572321]
- mptsas: pci-id table changes (Laura Abbott)
- mptsas: Taint kernel if mptsas is loaded (Laura Abbott)
- mptspi: pci-id table changes (Laura Abbott)
- qla2xxx: Remove PCI IDs of deprecated adapter (Jeremy Cline)
- be2iscsi: remove unsupported device IDs (Chris Leech) [1574502]
- mptspi: Taint kernel if mptspi is loaded (Laura Abbott)
- hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek) [1471185]
- qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis) [1518874]
- aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta) [1495307]
- megaraid_sas: remove deprecated pci-ids (Tomas Henzl) [1509329]
- mpt*: remove certain deprecated pci-ids (Jeremy Cline)
- kernel: add SUPPORT_REMOVED kernel taint (Tomas Henzl) [1602033]
- Rename RH_DISABLE_DEPRECATED to RHEL_DIFFERENCES (Don Zickus)
- Add option of 13 for FORCE_MAX_ZONEORDER (Peter Robinson)
- s390: Lock down the kernel when the IPL secure flag is set (Jeremy Cline)
- efi: Lock down the kernel if booted in secure boot mode (David Howells)
- efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (David Howells)
- security: lockdown: expose a hook to lock the kernel down (Jeremy Cline)
- Make get_cert_list() use efi_status_to_str() to print error messages. (Peter Jones)
- Add efi_status_to_str() and rework efi_status_to_err(). (Peter Jones)
- Add support for deprecating processors (Laura Abbott)
- arm: aarch64: Drop the EXPERT setting from ARM64_FORCE_52BIT (Jeremy Cline)
- iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- rh_kabi: introduce RH_KABI_EXCLUDE (Jakub Racek) [1652256]
- ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1670017]
- IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- scsi: smartpqi: add inspur advantech ids (Don Brace) [1503736]
- ice: mark driver as tech-preview (Jonathan Toppins) [1495347]
- kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- add pci_hw_vendor_status() (Maurizio Lombardi) [1590829]
- ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1563590]
- Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1563590]
- bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- tags.sh: Ignore redhat/rpm (Jeremy Cline)
- put RHEL info into generated headers (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1663728]
- kdump: add support for crashkernel=auto (Jeremy Cline)
- kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- modules: add rhelversion MODULE_INFO tag (Laura Abbott)
- ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- Add Red Hat tainting (Laura Abbott)
- Introduce CONFIG_RH_DISABLE_DEPRECATED (Laura Abbott)

* Thu Oct 08 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201008git7575fdda569b.30]
- Merge ark-patches

* Thu Oct 08 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201008git7575fdda569b.29.test]
- Updated changelog for the release based on 7575fdda569b (Fedora Kernel Team)

* Wed Oct 07 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201007git7575fdda569b.29]
- Merge ark-patches

* Wed Oct 07 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.20201007git7575fdda569b.28.test]
- 7575fdda569b rebase
- New configs in drivers/misc (Jeremy Cline)
- New configs in drivers/net/wireless ("Justin M. Forbes")
- New configs in drivers/phy (Fedora Kernel Team)
- New configs in drivers/tty (Fedora Kernel Team)

* Tue Oct 06 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.28]
- Merge ark-patches

* Tue Oct 06 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.27.test]
- Updated changelog for the release based on v5.9-rc8 (Fedora Kernel Team)

* Mon Oct 05 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.27]
- Merge ark-patches

* Mon Oct 05 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc8.26.test]
- v5.9-rc8 rebase
- Updated changelog for the release based on 22fbc037cd32 (Fedora Kernel Team)

* Mon Oct 05 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201005git22fbc037cd32.26]
- Merge ark-patches

* Mon Oct 05 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201005git22fbc037cd32.25.test]
- 22fbc037cd32 rebase
- Updated changelog for the release based on d3d45f8220d6 (Fedora Kernel Team)

* Sun Oct 04 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201004gitd3d45f8220d6.25]
- Merge ark-patches

* Sun Oct 04 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201004gitd3d45f8220d6.24.test]
- d3d45f8220d6 rebase
- Updated changelog for the release based on 472e5b056f00 (Fedora Kernel Team)

* Sat Oct 03 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201003git472e5b056f00.24]
- Merge ark-patches

* Sat Oct 03 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201003git472e5b056f00.23.test]
- 472e5b056f00 rebase
- Set SquashFS decompression options for all flavors to match RHEL (Bohdan Khomutskyi)
- Updated changelog for the release based on 60e720931556 (Fedora Kernel Team)

* Fri Oct 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201002git60e720931556.23]
- Merge ark-patches

* Fri Oct 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201002git60e720931556.22.test]
- 60e720931556 rebase
- New configs in drivers/pinctrl (Fedora Kernel Team)
- Updated changelog for the release based on 02de58b24d2e (Fedora Kernel Team)
- Update CONFIG_THERMAL_NETLINK (Justin Forbes)
- configs: Enable CONFIG_ENERGY_MODEL (Phil Auld)

* Thu Oct 01 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201001git02de58b24d2e.22]
- Merge ark-patches

* Thu Oct 01 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20201001git02de58b24d2e.21.test]
- 02de58b24d2e rebase
- Updated changelog for the release based on fb0155a09b02 (Fedora Kernel Team)

* Wed Sep 30 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20200930gitfb0155a09b02.21]
- Merge ark-patches

* Wed Sep 30 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20200930gitfb0155a09b02.20.test]
- fb0155a09b02 rebase

* Tue Sep 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.20]
- Merge ark-patches

* Tue Sep 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.19.test]
- Separate merge-upstream and release stages (Don Zickus)
- Re-enable CONFIG_IR_SERIAL on Fedora (Prarit Bhargava)
- Updated changelog for the release based on v5.9-rc7 (Fedora Kernel Team)

* Mon Sep 28 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.19]
- Merge ark-patches

* Mon Sep 28 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc7.18.test]
- v5.9-rc7 rebase
- Updated changelog for the release based on a1bffa48745a (Fedora Kernel Team)

* Sun Sep 27 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200927gita1bffa48745a.18]
- Merge ark-patches

* Sun Sep 27 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200927gita1bffa48745a.17.test]
- a1bffa48745a rebase
- Updated changelog for the release based on 7c7ec3226f5f (Fedora Kernel Team)
- Create Patchlist.changelog file (Don Zickus)

* Sat Sep 26 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200926git7c7ec3226f5f.17]
- Merge ark-patches

* Sat Sep 26 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200926git7c7ec3226f5f.16.test]
- 7c7ec3226f5f rebase
- Filter out upstream commits from changelog (Don Zickus)
- Merge Upstream script fixes (Don Zickus)
- Updated changelog for the release based on 171d4ff79f96 (Fedora Kernel Team)

* Fri Sep 25 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200925git171d4ff79f96.16]
- Merge ark-patches

* Fri Sep 25 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200925git171d4ff79f96.15.test]
- 171d4ff79f96 rebase
- mm: fix misplaced unlock_page in do_wp_page() (Linus Torvalds)
- Updated changelog for the release based on c9c9e6a49f89 (Fedora Kernel Team)
- Revert "ALSA: usb-audio: Disable Lenovo P620 Rear line-in volume control" (Kai-Heng Feng)
- media: dt-bindings: media: imx274: Convert to json-schema (Jacopo Mondi)
- Revert "ALSA: hda - Fix silent audio output and corrupted input on MSI X570-A PRO" (Takashi Iwai)
- ALSA: usb-audio: Add delay quirk for H570e USB headsets (Joakim Tjernlund)
- ALSA: hda/realtek: Enable front panel headset LED on Lenovo ThinkStation P520 (Kai-Heng Feng)
- ALSA: hda/realtek - Couldn't detect Mic if booting with headset plugged (Hui Wang)
- ALSA: asihpi: fix iounmap in error handler (Tom Rix)
- media: media/v4l2: remove V4L2_FLAG_MEMORY_NON_CONSISTENT flag (Sergey Senozhatsky)
- mmc: mmc_spi: Fix mmc_spi_dma_alloc() return type for !HAS_DMA (Geert Uytterhoeven)
- media: cec-adap.c: don't use flush_scheduled_work() (Hans Verkuil)

* Thu Sep 24 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200924gitc9c9e6a49f89.15]
- Merge ark-patches

* Thu Sep 24 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200924gitc9c9e6a49f89.14.test]
- c9c9e6a49f89 rebase
- mm: move the copy_one_pte() pte_present check into the caller (Linus Torvalds)
- mm: split out the non-present case from copy_one_pte() (Linus Torvalds)
- Updated changelog for the release based on 805c6d3c1921 (Fedora Kernel Team)
- dm crypt: document encrypted keyring key option (Milan Broz)
- dm crypt: document new no_workqueue flags (Milan Broz)
- btrfs: fix put of uninitialized kobject after seed device delete (Anand Jain)
- tools/bootconfig: Add testcase for tailing space (Masami Hiramatsu)
- tools/bootconfig: Add testcases for repeated key with brace (Masami Hiramatsu)
- lib/bootconfig: Fix to remove tailing spaces after value (Masami Hiramatsu)
- lib/bootconfig: Fix a bug of breaking existing tree nodes (Masami Hiramatsu)
- dm: fix comment in dm_process_bio() (Mike Snitzer)
- dm: fix bio splitting and its bio completion order for regular IO (Mike Snitzer)
- btrfs: fix overflow when copying corrupt csums for a message (Johannes Thumshirn)

* Wed Sep 23 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200923git805c6d3c1921.14]
- Merge ark-patches

* Wed Sep 23 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200923git805c6d3c1921.13.test]
- 805c6d3c1921 rebase
- Updated changelog for the release based on 98477740630f (Fedora Kernel Team)
- net: mscc: ocelot: fix some key offsets for IP4_TCP_UDP VCAP IS2 entries (Vladimir Oltean)
- net: dsa: seville: fix some key offsets for IP4_TCP_UDP VCAP IS2 entries (Vladimir Oltean)
- net: dsa: felix: fix some key offsets for IP4_TCP_UDP VCAP IS2 entries (Xiaoliang Yang)
- inet_diag: validate INET_DIAG_REQ_PROTOCOL attribute (Eric Dumazet)
- net: bridge: br_vlan_get_pvid_rcu() should dereference the VLAN group under RCU (Vladimir Oltean)
- net: Update MAINTAINERS for MediaTek switch driver (Sean Wang)
- net/mlx5e: mlx5e_fec_in_caps() returns a boolean (Saeed Mahameed)
- net/mlx5e: kTLS, Avoid kzalloc(GFP_KERNEL) under spinlock (Saeed Mahameed)
- net/mlx5e: kTLS, Fix leak on resync error flow (Saeed Mahameed)
- net/mlx5e: kTLS, Add missing dma_unmap in RX resync (Saeed Mahameed)
- net/mlx5e: kTLS, Fix napi sync and possible use-after-free (Tariq Toukan)
- net/mlx5e: TLS, Do not expose FPGA TLS counter if not supported (Tariq Toukan)
- net/mlx5e: Fix using wrong stats_grps in mlx5e_update_ndo_stats() (Alaa Hleihel)
- net/mlx5e: Fix multicast counter not up-to-date in "ip -s" (Ron Diskin)
- net/mlx5e: Fix endianness when calculating pedit mask first bit (Maor Dickman)
- net/mlx5e: Enable adding peer miss rules only if merged eswitch is supported (Maor Dickman)
- net/mlx5e: CT: Fix freeing ct_label mapping (Roi Dayan)
- net/mlx5e: Fix memory leak of tunnel info when rule under multipath not ready (Jianbo Liu)
- net/mlx5e: Use synchronize_rcu to sync with NAPI (Maxim Mikityanskiy)
- net/mlx5e: Use RCU to protect rq->xdp_prog (Maxim Mikityanskiy)
- net/mlx5: Fix FTE cleanup (Maor Gottlieb)
- ipv6: route: convert comma to semicolon (Xu Wang)
- sfc: Fix error code in probe (Dan Carpenter)
- io_uring: fix openat/openat2 unified prep handling (Jens Axboe)
- io_uring: mark statx/files_update/epoll_ctl as non-SQPOLL (Jens Axboe)
- tools/io_uring: fix compile breakage (Douglas Gilbert)
- io_uring: don't use retry based buffered reads for non-async bdev (Jens Axboe)
- io_uring: don't re-setup vecs/iter in io_resumit_prep() is already there (Jens Axboe)
- bnxt_en: Fix wrong flag value passed to HWRM_PORT_QSTATS_EXT fw call. (Michael Chan)
- bnxt_en: Fix HWRM_FUNC_QSTATS_EXT firmware call. (Michael Chan)
- bnxt_en: Return -EOPNOTSUPP for ETHTOOL_GREGS on VFs. (Vasundhara Volam)
- bnxt_en: Protect bnxt_set_eee() and bnxt_set_pauseparam() with mutex. (Michael Chan)
- bnxt_en: return proper error codes in bnxt_show_temp (Edwin Peer)
- bnxt_en: Use memcpy to copy VPD field info. (Vasundhara Volam)
- net: sctp: Fix IPv6 ancestor_size calc in sctp_copy_descendant (Henry Ptasinski)
- net: mvneta: recycle the page in case of out-of-order (Lorenzo Bianconi)
- rhashtable: fix indentation of a continue statement (Colin Ian King)
- bootconfig: init: make xbc_namebuf static (Jason Yan)
- MAINTAINERS: Update ibmveth maintainer (Cristobal Forno)
- net: ipv6: fix kconfig dependency warning for IPV6_SEG6_HMAC (Necip Fazil Yildiran)
- dpaa2-eth: fix a build warning in dpmac.c (Yangbo Lu)
- hinic: fix sending pkts from core while self testing (Luo bin)
- net: mscc: ocelot: deinitialize only initialized ports (Vladimir Oltean)
- net: mscc: ocelot: unregister net devices on unbind (Vladimir Oltean)
- net: mscc: ocelot: refactor ports parsing code into a dedicated function (Vladimir Oltean)
- net: mscc: ocelot: error checking when calling ocelot_init() (Vladimir Oltean)
- net: mscc: ocelot: check for errors on memory allocation of ports (Vladimir Oltean)
- net: dsa: seville: fix buffer size of the queue system (Vladimir Oltean)
- net: mscc: ocelot: add locking for the port TX timestamp ID (Vladimir Oltean)
- net: mscc: ocelot: fix race condition with TX timestamping (Vladimir Oltean)
- kprobes: tracing/kprobes: Fix to kill kprobes on initmem after boot (Masami Hiramatsu)
- tracing: fix double free (Tom Rix)
- ftrace: Let ftrace_enable_sysctl take a kernel pointer buffer (Tobias Klauser)
- tracing: Make the space reserved for the pid wider (Sebastian Andrzej Siewior)
- ftrace: Fix missing synchronize_rcu() removing trampoline from kallsyms (Adrian Hunter)
- ftrace: Free the trampoline when ftrace_startup() fails (Miroslav Benes)
- kprobes: Fix to check probe enabled before disarm_kprobe_ftrace() (Masami Hiramatsu)
- mac80211: fix 80 MHz association to 160/80+80 AP on 6 GHz (John Crispin)
- mac80211: do not allow bigger VHT MPDUs than the hardware supports (Felix Fietkau)
- cfg80211: fix 6 GHz channel conversion (Johannes Berg)
- mac80211: do not disable HE if HT is missing on 2.4 GHz (Wen Gong)
- mac80211: Fix radiotap header channel flag for 6GHz band (Aloka Dixit)
- lib80211: fix unmet direct dependendices config warning when !CRYPTO (Necip Fazil Yildiran)
- mac80211: add AQL support for VHT160 tx rates (Felix Fietkau)
- mac80211: extend AQL aggregation estimation to HE and fix unit mismatch (Felix Fietkau)
- nfp: use correct define to return NONE fec (Jakub Kicinski)
- hinic: fix potential resource leak (Wei Li)
- net: phy: Do not warn in phy_stop() on PHY_DOWN (Florian Fainelli)
- net: phy: Avoid NPD upon phy_detach() when driver is unbound (Florian Fainelli)
- ethtool: add and use message type for tunnel info reply (Michal Kubecek)
- drivers/net/wan/hdlc: Set skb->protocol before transmitting (Xie He)
- drivers/net/wan/lapbether: Make skb->protocol consistent with the header (Xie He)
- cxgb4: fix memory leak during module unload (Raju Rangoju)
- hv_netvsc: Add validation for untrusted Hyper-V values (Andres Beltran)
- fuse: fix the ->direct_IO() treatment of iov_iter (Al Viro)
- nvmet: get transport reference for passthru ctrl (Christoph Hellwig)
- nvme-core: get/put ctrl and transport module in nvme_dev_open/release() (Chaitanya Kulkarni)
- net: dsa: microchip: ksz8795: really set the correct number of ports (Matthias Schiffer)
- geneve: add transport ports in route lookup for geneve (Mark Gray)
- net: hns: kerneldoc fixes (Lu Wei)
- fs: fix cast in fsparam_u32hex() macro (Alexey Dobriyan)
- bpf: Fix a rcu warning for bpffs map pretty-print (Yonghong Song)
- bpf: Bpf_skc_to_* casting helpers require a NULL check on sk (Martin KaFai Lau)
- ipv4: Update exception handling for multipath routes via same device (David Ahern)
- net: tipc: kerneldoc fixes (Lu Wei)
- ibmvnic: update MAINTAINERS (Dany Madden)
- batman-adv: mcast: fix duplicate mcast packets from BLA backbone to mesh (=?UTF-8?q?Linus=20L=C3=BCssing?=)
- batman-adv: mcast: fix duplicate mcast packets in BLA backbone from mesh (=?UTF-8?q?Linus=20L=C3=BCssing?=)
- batman-adv: mcast: fix duplicate mcast packets in BLA backbone from LAN (=?UTF-8?q?Linus=20L=C3=BCssing?=)
- nvme-tcp: fix kconfig dependency warning when !CRYPTO (Necip Fazil Yildiran)
- nvme-pci: disable the write zeros command for Intel 600P/P3100 (David Milburn)
- docs/bpf: Remove source code links (Andrii Nakryiko)
- s390/dasd: Fix zero write for FBA devices (=?UTF-8?q?Jan=20H=C3=B6ppner?=)
- xsk: Fix number of pinned pages/umem size discrepancy (=?UTF-8?q?Bj=C3=B6rn=20T=C3=B6pel?=)
- net: sched: initialize with 0 before setting erspan md->u (Xin Long)
- lwtunnel: only keep the available bits when setting vxlan md->gbp (Xin Long)
- net: sched: only keep the available bits when setting vxlan md->gbp (Xin Long)
- tipc: use skb_unshare() instead in tipc_buf_append() (Xin Long)
- tipc: Fix memory leak in tipc_group_create_member() (Peilin Ye)
- ipv4: Initialize flowi4_multipath_hash in data path (David Ahern)
- net: lantiq: Disable IRQs only if NAPI gets scheduled (Hauke Mehrtens)
- net: lantiq: Use napi_complete_done() (Hauke Mehrtens)
- net: lantiq: use netif_tx_napi_add() for TX NAPI (Hauke Mehrtens)
- net: lantiq: Wake TX queue again (Hauke Mehrtens)
- rndis_host: increase sleep time in the query-response loop (Olympia Giannou)
- batman-adv: Add missing include for in_interrupt() (Sven Eckelmann)
- io_uring: don't run task work on an exiting task (Jens Axboe)
- io_uring: drop 'ctx' ref on task work cancelation (Jens Axboe)
- io_uring: grab any needed state during defer prep (Jens Axboe)
- net: ethernet: ti: cpsw_new: fix suspend/resume (Grygorii Strashko)
- net: ipa: fix u32_replace_bits by u32p_xxx version (Vadym Kochan)
- hinic: fix rewaking txq after netif_tx_disable (Luo bin)
- taprio: Fix allowing too small intervals (Vinicius Costa Gomes)
- enetc: Fix mdio bus removal on PF probe bailout (Claudiu Manoil)
- docs/bpf: Fix ringbuf documentation (Andrii Nakryiko)
- net: dec: de2104x: Increase receive ring size for Tulip (Lucy Yan)
- netlink: fix doc about nlmsg_parse/nla_validate (Nicolas Dichtel)
- net: DCB: Validate DCB_ATTR_DCB_BUFFER argument (Petr Machata)
- selftests: rtnetlink: Test bridge enslavement with different parent IDs (Ido Schimmel)
- net: Fix bridge enslavement failure (Ido Schimmel)
- net: mvneta: fix possible use-after-free in mvneta_xdp_put_buff (Lorenzo Bianconi)
- s390/qeth: delay draining the TX buffers (Julian Wiedmann)
- net: Fix broken NETIF_F_CSUM_MASK spell in netdev_features.h (Miaohe Lin)
- net: Correct the comment of dst_dev_put() (Miaohe Lin)
- hdlc_ppp: add range checks in ppp_cp_parse_cr() (Dan Carpenter)
- net: phy: call phy_disable_interrupts() in phy_attach_direct() instead (Yoshihiro Shimoda)
- hv_netvsc: Cache the current data path to avoid duplicate call and message (Dexuan Cui)
- hv_netvsc: Switch the data path at the right time during hibernation (Dexuan Cui)
- net: sch_generic: aviod concurrent reset and enqueue op for lockless qdisc (Yunsheng Lin)
- net: dsa: microchip: look for phy-mode in port nodes (Helmut Grohne)
- mptcp: fix kmalloc flag in mptcp_pm_nl_get_local_id (Geliang Tang)
- mptcp: fix subflow's remote_id issues (Geliang Tang)
- mptcp: fix subflow's local_id issues (Geliang Tang)
- tipc: fix shutdown() of connection oriented socket (Tetsuo Handa)
- connector: Move maintainence under networking drivers umbrella. ("David S. Miller")
- igc: Fix not considering the TX delay for timestamps (Vinicius Costa Gomes)
- igc: Fix wrong timestamp latency numbers (Vinicius Costa Gomes)
- i40e: always propagate error value in i40e_set_vsi_promisc() (Stefan Assmann)
- i40e: fix return of uninitialized aq_ret in i40e_set_vsi_promisc (Stefan Assmann)
- net: qed: RDMA personality shouldn't fail VF load (Dmitry Bogdanov)
- net: qede: Disable aRFS for NPAR and 100G (Dmitry Bogdanov)
- net: qed: Disable aRFS for NPAR and 100G (Dmitry Bogdanov)
- wireguard: peerlookup: take lock before checking hash in replace operation ("Jason A. Donenfeld")
- wireguard: noise: take lock when removing handshake entry from table ("Jason A. Donenfeld")
- hsr: avoid newline at end of message in NL_SET_ERR_MSG_MOD (Ye Bin)
- net: add __must_check to skb_put_padto() (Eric Dumazet)
- net: qrtr: check skb_put_padto() return value (Eric Dumazet)
- ip: fix tos reflection in ack and reset packets (Wei Wang)
- MAINTAINERS: remove John Allen from ibmvnic (Jakub Kicinski)
- fib: fix fib_rule_ops indirect call wrappers when CONFIG_IPV6=m (Brian Vazquez)
- ipv6: avoid lockdep issue in fib6_del() (Eric Dumazet)
- net: dsa: link interfaces with the DSA master to get rid of lockdep warnings (Vladimir Oltean)
- tools/libbpf: Avoid counting local symbols in ABI check (Tony Ambardar)
- bpf: Fix clobbering of r2 in bpf_gen_ld_abs (Daniel Borkmann)
- mac802154: tx: fix use-after-free (Eric Dumazet)
- netfilter: nft_meta: use socket user_ns to retrieve skuid and skgid (Pablo Neira Ayuso)
- netfilter: conntrack: nf_conncount_init is failing with IPv6 disabled (Eelco Chaudron)
- netfilter: ctnetlink: fix mark based dump filtering regression (Martin Willi)
- netfilter: nf_tables: coalesce multiple notifications into one skbuff (Pablo Neira Ayuso)
- netfilter: ctnetlink: add a range check for l3/l4 protonum (Will McVicker)
- hv_netvsc: Fix hibernation for mlx5 VF driver (Dexuan Cui)
- Revert "netns: don't disable BHs when locking "nsid_lock"" (Taehee Yoo)
- ibmvnic: add missing parenthesis in do_reset() (Jakub Kicinski)
- netdevice.h: fix xdp_state kernel-doc warning (Randy Dunlap)
- netdevice.h: fix proto_down_reason kernel-doc warning (Randy Dunlap)
- bnxt_en: Fix NULL ptr dereference crash in bnxt_fw_reset_task() (Vasundhara Volam)
- bnxt_en: Avoid sending firmware messages when AER error is detected. (Vasundhara Volam)
- Revert "wlcore: Adding suppoprt for IGTK key in wlcore driver" (Mauro Carvalho Chehab)
- net: dsa: rtl8366: Properly clear member config (Linus Walleij)
- net: macb: fix for pause frame receive enable bit (Parshuram Thombare)
- cxgb4: Fix offset when clearing filter byte counters (Ganji Aravind)
- hinic: bump up the timeout of UPDATE_FW cmd (Luo bin)
- hinic: bump up the timeout of SET_FUNC_STATE cmd (Luo bin)
- batman-adv: mcast/TT: fix wrongly dropped or rerouted packets (=?UTF-8?q?Linus=20L=C3=BCssing?=)
- act_ife: load meta modules before tcf_idr_check_alloc() (Cong Wang)
- atm: eni: fix the missed pci_disable_device() for eni_init_one() (Jing Xiangfeng)
- drivers/net/wan/hdlc_fr: Add needed_headroom for PVC devices (Xie He)
- selftests/bpf: Add bpf_{update, delete}_map_elem in hashmap iter program (Yonghong Song)
- bpf: Do not use bucket_lock for hashmap iterator (Yonghong Song)
- libbpf: Remove arch-specific include path in Makefile ("Naveen N. Rao")
- tools/bpf: build: Make sure resolve_btfids cleans up after itself (=?UTF-8?q?Toke=20H=C3=B8iland-J=C3=B8rgensen?=)
- libbpf: Fix build failure from uninitialized variable warning (Tony Ambardar)
- batman-adv: bla: fix type misuse for backbone_gw hash indexing (=?UTF-8?q?Linus=20L=C3=BCssing?=)
- mwifiex: Increase AES key storage size to 256 bits (Maximilian Luz)
- mt76: mt7915: use ieee80211_free_txskb to free tx skbs (Felix Fietkau)
- mt76: mt7615: use v1 MCU API on MT7615 to fix issues with adding/removing stations (Felix Fietkau)
- vboxsf: Fix the check for the old binary mount-arguments struct (Hans de Goede)
- brcmfmac: reserve tx credit only when txctl is ready to send (Wright Feng)
- ieee802154/adf7242: check status of adf7242_read_reg (Tom Rix)
- ieee802154: fix one possible memleak in ca8210_dev_com_init (Liu Jian)

* Tue Sep 22 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200922git98477740630f.13]
- Merge ark-patches

* Tue Sep 22 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.20200922git98477740630f.12.test]
- 98477740630f rebase
- dax: Fix compilation for CONFIG_DAX && !CONFIG_FS_DAX (Jan Kara)
- Updated changelog for the release based on v5.9-rc6 (Fedora Kernel Team)
- Revert "KVM: Check the allocation of pv cpu mask" (Vitaly Kuznetsov)
- KVM: arm64: Remove S1PTW check from kvm_vcpu_dabt_iswrite() (Marc Zyngier)
- KVM: arm64: Assume write fault on S1PTW permission fault on instruction fetch (Marc Zyngier)
- rcu-tasks: Prevent complaints of unused show_rcu_tasks_classic_gp_kthread() ("Paul E. McKenney")
- docs: kvm: add documentation for KVM_CAP_S390_DIAG318 (Collin Walling)

* Mon Sep 21 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.12]
- Merge ark-patches

* Mon Sep 21 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc6.11.test]
- v5.9-rc6 rebase
- Linux 5.9-rc6 (Linus Torvalds)
- mm: fix wake_page_function() comment typos (Linus Torvalds)
- dax: Fix stack overflow when mounting fsdax pmem device (Adrian Huang)
- dm: Call proper helper to determine dax support (Jan Kara)
- dm/dax: Fix table reference counts (Dan Williams)
- kconfig: qconf: revive help message in the info view (Masahiro Yamada)
- kconfig: qconf: fix incomplete type 'struct gstr' warning (Masahiro Yamada)
- RISC-V: Resurrect the MMIO timer implementation for M-mode systems (Palmer Dabbelt)
- riscv: Fix Kendryte K210 device tree (Damien Le Moal)
- riscv: Add sfence.vma after early page table changes (Greentime Hu)
- kcsan: kconfig: move to menu 'Generic Kernel Debugging Instruments' (Changbin Du)
- fs/fs-writeback.c: adjust dirtytime_interval_handler definition to match prototype (Tobias Klauser)
- stackleak: let stack_erasing_sysctl take a kernel pointer buffer (Tobias Klauser)
- ftrace: let ftrace_enable_sysctl take a kernel pointer buffer (Tobias Klauser)
- mm/memory_hotplug: drain per-cpu pages again during memory offline (Pavel Tatashin)
- selftests/vm: fix display of page size in map_hugetlb (Christophe Leroy)
- mm/thp: fix __split_huge_pmd_locked() for migration PMD (Ralph Campbell)
- kprobes: fix kill kprobe which has been marked as gone (Muchun Song)
- tmpfs: restore functionality of nr_inodes=0 (Byron Stanoszek)
- mlock: fix unevictable_pgs event counts on THP (Hugh Dickins)
- mm: fix check_move_unevictable_pages() on THP (Hugh Dickins)
- mm: migration of hugetlbfs page skip memcg (Hugh Dickins)
- ksm: reinstate memcg charge on copied pages (Hugh Dickins)
- mailmap: add older email addresses for Kees Cook (Kees Cook)
- i2c: mxs: use MXS_DMA_CTRL_WAIT4END instead of DMA_CTRL_ACK (Matthias Schiffer)
- i2c: mediatek: Send i2c master code at more than 1MHz (Qii Wang)
- i2c: mediatek: Fix generic definitions for bus frequency (Qii Wang)
- objtool: Fix noreturn detection for ignored functions (Josh Poimboeuf)
- kconfig: qconf: use delete[] instead of delete to free array (again) (Masahiro Yamada)
- iommu/amd: Restore IRTE.RemapEn bit for amd_iommu_activate_guest_mode (Suravee Suthikulpanit)
- iommu/amd: Fix potential @entry null deref (Joao Martins)
- x86/unwind/fp: Fix FP unwinding in ret_from_fork (Josh Poimboeuf)
- i2c: core: Call i2c_acpi_install_space_handler() before i2c_acpi_register_devices() (Hans de Goede)
- percpu: fix first chunk size calculation for populated bitmap (Sunghyun Jin)
- mm: allow a controlled amount of unfairness in the page lock (Linus Torvalds)
- arm64: paravirt: Initialize steal time when cpu is online (Andrew Jones)
- usblp: fix race between disconnect() and read() (Oliver Neukum)
- arm64: bpf: Fix branch offset in JIT (Ilias Apalodimas)
- ehci-hcd: Move include to keep CRC stable (Quentin Perret)
- drm/amd/display: Don't log hdcp module warnings in dmesg (Bhawanpreet Lakha)
- drm/amdgpu: declare ta firmware for navy_flounder (Jiansong Chen)
- drm/mediatek: Add missing put_device() call in mtk_hdmi_dt_parse_pdata() (Yu Kuai)
- drm/mediatek: Add missing put_device() call in mtk_drm_kms_init() (Yu Kuai)
- drm/mediatek: Add exception handing in mtk_drm_probe() if component init fail (Yu Kuai)
- drm/mediatek: Add missing put_device() call in mtk_ddp_comp_init() (Yu Kuai)
- drm/mediatek: Use CPU when fail to get cmdq event (Chun-Kuang Hu)
- drm/mediatek: Remove duplicated include (Wang Hai)
- MIPS: SNI: Fix spurious interrupts (Thomas Bogendoerfer)
- MAINTAINERS: Fix Max's and Shravan's emails (Leon Romanovsky)
- ACPI: processor: Take over RCU-idle for C3-BM idle (Peter Zijlstra)
- cpuidle: Allow cpuidle drivers to take over RCU-idle (Peter Zijlstra)
- ACPI: processor: Use CPUIDLE_FLAG_TLB_FLUSHED (Peter Zijlstra)
- ACPI: processor: Use CPUIDLE_FLAG_TIMER_STOP (Peter Zijlstra)
- locking/percpu-rwsem: Use this_cpu_{inc,dec}() for read_count (Hou Tao)
- perf stat: Fix the ratio comments of miss-events (Qi Liu)
- fbcon: Fix user font detection test at fbcon_resize(). (Tetsuo Handa)
- powercap: RAPL: Add support for Lakefield (Ricardo Neri)
- serial: 8250_pci: Add Realtek 816a and 816b (Tobias Diedrich)
- serial: core: fix console port-lock regression (Johan Hovold)
- serial: core: fix port-lock initialisation (Johan Hovold)
- usb: typec: intel_pmc_mux: Handle SCU IPC error conditions (Madhusudanarao Amara)
- USB: quirks: Add USB_QUIRK_IGNORE_REMOTE_WAKEUP quirk for BYD zhaoxin notebook (Penghao)
- USB: UAS: fix disconnect by unplugging a hub (Oliver Neukum)
- usb: typec: ucsi: Prevent mode overrun (Heikki Krogerus)
- usb: typec: ucsi: acpi: Increase command completion timeout value (Heikki Krogerus)
- drm/i915: Filter wake_flags passed to default_wake_function (Chris Wilson)
- drm/i915: Be wary of data races when reading the active execlists (Chris Wilson)
- drm/i915/gem: Reduce context termination list iteration guard to RCU (Chris Wilson)
- drm/i915/gem: Delay tracking the GEM context until it is registered (Chris Wilson)
- drm/amdgpu/dc: Require primary plane to be enabled whenever the CRTC is (=?UTF-8?q?Michel=20D=C3=A4nzer?=)
- drm/radeon: revert "Prefer lower feedback dividers" (=?UTF-8?q?Christian=20K=C3=B6nig?=)
- drm/amdgpu: Include sienna_cichlid in USBC PD FW support. (Andrey Grodzovsky)
- drm/amd/display: update nv1x stutter latencies (Jun Lei)
- drm/amd/display: Don't use DRM_ERROR() for DTM add topology (Bhawanpreet Lakha)
- drm/amd/pm: support runtime pptable update for sienna_cichlid etc. (Jiansong Chen)
- drm/amdkfd: fix a memory leak issue (Dennis Li)
- drm/kfd: fix a system crash issue during GPU recovery (Dennis Li)
- efi: efibc: check for efivars write capability (Ard Biesheuvel)
- perf test: Free formats for perf pmu parse test (Namhyung Kim)
- perf metric: Do not free metric when failed to resolve (Namhyung Kim)
- perf metric: Free metric when it failed to resolve (Namhyung Kim)
- perf metric: Release expr_parse_ctx after testing (Namhyung Kim)
- perf test: Fix memory leaks in parse-metric test (Namhyung Kim)
- perf parse-event: Fix memory leak in evsel->unit (Namhyung Kim)
- perf evlist: Fix cpu/thread map leak (Namhyung Kim)
- perf metric: Fix some memory leaks - part 2 (Namhyung Kim)
- perf metric: Fix some memory leaks (Namhyung Kim)
- perf test: Free aliases for PMU event map aliases test (Namhyung Kim)
- perf vendor events amd: Remove trailing commas (Henry Burns)
- MIPS: SNI: Fix MIPS_L1_CACHE_SHIFT (Thomas Bogendoerfer)
- EDAC/ghes: Check whether the driver is on the safe list correctly (Borislav Petkov)
- EDAC/ghes: Clear scanned data on unload (Borislav Petkov)
- Updated changelog for the release based on fc4f28bb3daf (Fedora Kernel Team)
- perf test: Leader sampling shouldn't clear sample period (Ian Rogers)
- perf record: Don't clear event's period if set by a term (Ian Rogers)
- tools headers UAPI: update linux/in.h copy (Arnaldo Carvalho de Melo)
- tools headers UAPI: Sync kvm.h headers with the kernel sources (Arnaldo Carvalho de Melo)
- perf record: Prevent override of attr->sample_period for libpfm4 events (Stephane Eranian)
- perf record: Set PERF_RECORD_PERIOD if attr->freq is set. (David Sharp)
- perf bench: Fix 2 memory sanitizer warnings (Ian Rogers)
- perf test: Fix the "signal" test inline assembly (Jiri Olsa)
- core/entry: Report syscall correctly for trace and audit (Kees Cook)
- Input: trackpoint - add new trackpoint variant IDs (Vincent Huang)
- Revert "mtd: spi-nor: Add capability to disable flash quad mode" (Yicong Yang)
- Revert "mtd: spi-nor: Disable the flash quad mode in spi_nor_restore()" (Yicong Yang)
- Drivers: hv: vmbus: Add timeout to vmbus_wait_for_unload (Michael Kelley)
- x86/boot/compressed: Disable relocation relaxation (Arvind Sankar)
- s390: add 3f program exception handler (Janosch Frank)
- lockdep: fix order in trace_hardirqs_off_caller() (Sven Schnelle)
- s390/pci: fix leak of DMA tables on hard unplug (Niklas Schnelle)
- s390/init: add missing __init annotations (Ilya Leoshkevich)
- s390/zcrypt: fix kmalloc 256k failure (Harald Freudenberger)
- s390/idle: fix suspicious RCU usage (Peter Zijlstra)
- i2c: i801: Simplify the suspend callback (Jean Delvare)
- i2c: i801: Fix resume bug (=?UTF-8?q?Volker=20R=C3=BCmelin?=)
- i2c: aspeed: Mask IRQ status to relevant bits (Eddie James)
- sh: fix syscall tracing (Rich Felker)
- sh: remove spurious circular inclusion from asm/smp.h (Rich Felker)
- arm64: Allow CPUs unffected by ARM erratum 1418040 to come in late (Marc Zyngier)
- RISC-V: Take text_mutex in ftrace_init_nop() (Palmer Dabbelt)
- clk: qcom: lpass: Correct goto target in lpass_core_sc7180_probe() (Jing Xiangfeng)
- clk: versatile: Add of_node_put() before return statement (Sumera Priyadarsini)
- clk: bcm: dvp: Select the reset framework (Maxime Ripard)
- scsi: libsas: Fix error path in sas_notify_lldd_dev_found() (Dan Carpenter)
- Drivers: hv: vmbus: hibernation: do not hang forever in vmbus_bus_resume() (Dexuan Cui)
- thunderbolt: Retry DROM read once if parsing fails (Mika Westerberg)
- ALSA: hda/realtek - The Mic on a RedmiBook doesn't work (Hui Wang)
- x86/defconfigs: Explicitly unset CONFIG_64BIT in i386_defconfig (=?UTF-8?q?Daniel=20D=C3=ADaz?=)
- powerpc/papr_scm: Limit the readability of 'perf_stats' sysfs attribute (Vaibhav Jain)
- Input: i8042 - add Entroware Proteus EL07R4 to nomux and reset lists (Hans de Goede)
- ASoC: tlv320adcx140: Wake up codec before accessing register (Camel Guo)
- cpuidle: pseries: Fix CEDE latency conversion from tb to us ("Gautham R. Shenoy")
- powerpc/dma: Fix dma_map_ops::get_required_mask (Alexey Kardashevskiy)
- ASoC: core: Do not cleanup uninitialized dais on soc_pcm_open failure (Cezary Rojewski)
- ALSA: hda: fixup headset for ASUS GX502 laptop (Luke D Jones)
- locking/lockdep: Fix "USED" <- "IN-NMI" inversions ("peterz@infradead.org")
- Revert "powerpc/build: vdso linker warning for orphan sections" (Michael Ellerman)
- ASoC: Intel: bytcr_rt5640: Add quirk for MPMAN Converter9 2-in-1 (Hans de Goede)
- powerpc/mm: Remove DEBUG_VM_PGTABLE support on powerpc ("Aneesh Kumar K.V")
- ASoC: Intel: haswell: Fix power transition refactor (Cezary Rojewski)
- ASoC: tlv320adcx140: Fix accessing uninitialized adcx140->dev (Camel Guo)
- selftests/powerpc: Skip PROT_SAO test in guests/LPARS (Michael Ellerman)
- ASoC: wm8994: Ensure the device is resumed in wm89xx_mic_detect functions (Sylwester Nawrocki)
- ASoC: wm8994: Skip setting of the WM8994_MICBIAS register for WM1811 (Sylwester Nawrocki)
- ASoC: meson: axg-toddr: fix channel order on g12 platforms (Jerome Brunet)
- ASoC: soc-core: add snd_soc_find_dai_with_mutex() (Kuninori Morimoto)
- powerpc/book3s64/radix: Fix boot failure with large amount of guest memory ("Aneesh Kumar K.V")
- drm/mediatek: dsi: Fix scrolling of panel with small hfp or hbp (Jitao Shi)
- ASoC: qcom: common: Fix refcount imbalance on error (Dinghao Liu)
- ASoC: rt700: Fix return check for devm_regmap_init_sdw() (Vinod Koul)
- ASoC: rt715: Fix return check for devm_regmap_init_sdw() (Vinod Koul)
- ASoC: rt711: Fix return check for devm_regmap_init_sdw() (Vinod Koul)
- ASoC: rt1308-sdw: Fix return check for devm_regmap_init_sdw() (Vinod Koul)
- ASoC: max98373: Fix return check for devm_regmap_init_sdw() (Vinod Koul)
- ASoC: ti: fixup ams_delta_mute() function name (Kuninori Morimoto)
- ASoC: pcm3168a: ignore 0 Hz settings (Kuninori Morimoto)
- ASoC: Intel: tgl_max98373: fix a runtime pm issue in multi-thread case (Rander Wang)
- ASoC: qcom: Set card->owner to avoid warnings (Stephan Gerhold)
- ASoC: intel: atom: Add period size constraint (Brent Lu)
- device_cgroup: Fix RCU list debugging warning (Amol Grover)
- ASoC: Intel: skl_hda_dsp_generic: Fix NULLptr dereference in autosuspend delay (Mateusz Gorski)
- clk: rockchip: Fix initialization of mux_pll_src_4plls_p (Nathan Chancellor)
- clk: davinci: Use the correct size when allocating memory (Christophe JAILLET)

* Tue Sep 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc5.20200915gitfc4f28bb3daf.11]
- Merge ark-patches

* Tue Sep 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc5.20200915gitfc4f28bb3daf.10.test]
- fc4f28bb3daf rebase
- vgacon: remove software scrollback support (Linus Torvalds)
- fbcon: remove now unusued 'softback_lines' cursor() argument (Linus Torvalds)
- fbcon: remove soft scrollback code (Linus Torvalds)
- btrfs: fix wrong address when faulting in pages in the search ioctl (Filipe Manana)
- Updated changelog for the release based on v5.9-rc5 (Fedora Kernel Team)

* Mon Sep 14 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc5.10]
- Merge ark-patches

* Mon Sep 14 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc5.9.test]
- v5.9-rc5 rebase
- Linux 5.9-rc5 (Linus Torvalds)
- Updated changelog for the release based on ef2e9a563b0c (Fedora Kernel Team)
- KVM: emulator: more strict rsm checks. (Maxim Levitsky)
- KVM: nSVM: more strict SMM checks when returning to nested guest (Maxim Levitsky)
- SVM: nSVM: setup nested msr permission bitmap on nested state load (Maxim Levitsky)
- SVM: nSVM: correctly restore GIF on vmexit from nesting after migration (Maxim Levitsky)
- openrisc: Fix issue with get_user for 64-bit values (Stafford Horne)
- x86/kvm: don't forget to ACK async PF IRQ (Vitaly Kuznetsov)
- x86/kvm: properly use DEFINE_IDTENTRY_SYSVEC() macro (Vitaly Kuznetsov)
- KVM: VMX: Don't freeze guest when event delivery causes an APIC-access exit (Wanpeng Li)
- KVM: SVM: avoid emulation with stale next_rip (Wanpeng Li)
- KVM: x86: always allow writing '0' to MSR_KVM_ASYNC_PF_EN (Vitaly Kuznetsov)
- KVM: SVM: Periodically schedule when unregistering regions on destroy (David Rientjes)
- KVM: MIPS: Change the definition of kvm type (Huacai Chen)
- kvm x86/mmu: use KVM_REQ_MMU_SYNC to sync when needed (Lai Jiangshan)
- KVM: nVMX: Fix the update value of nested load IA32_PERF_GLOBAL_CTRL control (Chenyi Qiang)
- KVM: fix memory leak in kvm_io_bus_unregister_dev() (Rustam Kovhaev)
- KVM: Check the allocation of pv cpu mask (Haiwei Li)
- KVM: nVMX: Update VMCS02 when L2 PAE PDPTE updates detected (Peter Shier)
- Revert "dyndbg: accept query terms like file=bar and module=foo" (Greg Kroah-Hartman)
- Revert "dyndbg: fix problem parsing format="foo bar"" (Greg Kroah-Hartman)
- test_firmware: Test platform fw loading on non-EFI systems (Kees Cook)
- arm64: dts: ns2: Fixed QSPI compatible string (Florian Fainelli)
- ARM: dts: BCM5301X: Fixed QSPI compatible string (Florian Fainelli)
- ARM: dts: NSP: Fixed QSPI compatible string (Florian Fainelli)
- ARM: dts: bcm: HR2: Fixed QSPI compatible string (Florian Fainelli)
- dt-bindings: spi: Fix spi-bcm-qspi compatible ordering (Florian Fainelli)
- usb: typec: intel_pmc_mux: Do not configure SBU and HSL Orientation in Alternate modes (Utkarsh Patel)
- usb: typec: intel_pmc_mux: Do not configure Altmode HPD High (Utkarsh Patel)
- scripts/tags.sh: exclude tools directory from tags generation (Rustam Kovhaev)
- openrisc: Fix cache API compile issue when not inlining (Stafford Horne)
- openrisc: Reserve memblock for initrd (Stafford Horne)
- kobject: Drop unneeded conditional in __kobject_del() (Andy Shevchenko)
- ARM: dts: imx6sx: fix the pad QSPI1B_SCLK mux mode for uart3 (Fugang Duan)
- arm64: dts: imx8mp: correct sdma1 clk setting (Robin Gong)
- driver core: Fix device_pm_lock() locking for device links (Saravana Kannan)
- MAINTAINERS: Add the security document to SECURITY CONTACT (Krzysztof Kozlowski)
- driver code: print symbolic error code (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- debugfs: Fix module state check condition (Vladis Dronov)
- video: fbdev: fix OOB read in vga_8planes_imageblit() (Tetsuo Handa)
- dyndbg: fix problem parsing format="foo bar" (Jim Cromie)
- dyndbg: refine export, rename to dynamic_debug_exec_queries() (Jim Cromie)
- dyndbg: give 3u width in pr-format, cosmetic only (Jim Cromie)
- usb: core: fix slab-out-of-bounds Read in read_descriptors (Zeng Tao)
- Revert "usb: dwc3: meson-g12a: fix shared reset control use" (Amjad Ouled-Ameur)
- usb: typec: ucsi: acpi: Check the _DEP dependencies (Heikki Krogerus)
- usb: typec: intel_pmc_mux: Un-register the USB role switch (Madhusudanarao Amara)
- usb: Fix out of sync data toggle if a configured device is reconfigured (Mathias Nyman)
- KVM: arm64: Update page shift if stage 2 block mapping not supported (Alexandru Elisei)
- KVM: arm64: Fix address truncation in traces (Marc Zyngier)
- KVM: arm64: Do not try to map PUDs when they are folded into PMD (Marc Zyngier)
- interconnect: qcom: Fix small BW votes being truncated to zero (Mike Tipton)
- soundwire: fix double free of dangling pointer (Tom Rix)
- interconnect: Show bandwidth for disabled paths as zero in debugfs (Matthias Kaehlcke)
- iio: adc: mcp3422: fix locking on error path (Angelo Compagnucci)
- habanalabs: fix report of RAZWI initiator coordinates (Ofir Bitton)
- habanalabs: prevent user buff overflow (Moti Haimovski)
- iio: adc: mcp3422: fix locking scope (Angelo Compagnucci)
- iio: adc: meson-saradc: Use the parent device to look up the calib data (Martin Blumenstingl)
- iio:adc:max1118 Fix alignment of timestamp and data leak issues (Jonathan Cameron)
- iio:adc:ina2xx Fix timestamp alignment issue. (Jonathan Cameron)
- iio:adc:ti-adc084s021 Fix alignment and data leak issues. (Jonathan Cameron)
- iio:adc:ti-adc081c Fix alignment and data leak issues (Jonathan Cameron)
- phy: omap-usb2-phy: disable PHY charger detect (Roger Quadros)
- USB: serial: option: support dynamic Quectel USB compositions (=?UTF-8?q?Bj=C3=B8rn=20Mork?=)
- USB: serial: option: add support for SIM7070/SIM7080/SIM7090 modules (Aleksander Morgado)
- arm64: dts: imx8mq: Fix TMU interrupt property (Krzysztof Kozlowski)
- kobject: Restore old behaviour of kobject_del(NULL) (Andy Shevchenko)
- firmware_loader: fix memory leak for paged buffer (Prateek Sood)
- thunderbolt: Use maximum USB3 link rate when reclaiming if link is not up (Mika Westerberg)
- thunderbolt: Disable ports that are not implemented ("Nikunj A. Dadhania")
- ARM: dts: imx7d-zii-rmu2: fix rgmii phy-mode for ksz9031 phy (Chris Healy)
- USB: serial: ftdi_sio: add IDs for Xsens Mti USB converter (Patrick Riphagen)
- phy: qcom-qmp: Use correct values for ipq8074 PCIe Gen2 PHY init (Sivaprakash Murugesan)
- ARM: dts: vfxxx: Add syscon compatible with OCOTP (Chris Healy)
- ARM: dts: imx6q-logicpd: Fix broken PWM (Adam Ford)
- arm64: dts: imx: Add missing imx8mm-beacon-kit.dtb to build (Rob Herring)
- ARM: dts: imx6q-prtwd2: Remove unneeded i2c unit name (Fabio Estevam)
- ARM: dts: imx6qdl-gw51xx: Remove unneeded #address-cells/#size-cells (Fabio Estevam)
- ARM: dts: imx7ulp: Correct gpio ranges (Anson Huang)
- iio:magnetometer:ak8975 Fix alignment and data leak issues. (Jonathan Cameron)
- iio:light:ltr501 Fix timestamp alignment issue. (Jonathan Cameron)
- iio:light:max44000 Fix timestamp alignment and prevent data leak. (Jonathan Cameron)
- iio:chemical:ccs811: Fix timestamp alignment and prevent data leak. (Jonathan Cameron)
- iio:proximity:mb1232: Fix timestamp alignment and prevent data leak. (Jonathan Cameron)
- iio:accel:mma7455: Fix timestamp alignment and prevent data leak. (Jonathan Cameron)
- iio:accel:bmc150-accel: Fix timestamp alignment and prevent data leak. (Jonathan Cameron)
- iio:accel:mma8452: Fix timestamp alignment and prevent data leak. (Jonathan Cameron)
- iio: accel: kxsd9: Fix alignment of local buffer. (Jonathan Cameron)
- iio: adc: rockchip_saradc: select IIO_TRIGGERED_BUFFER (Michael Walle)
- iio: adc: ti-ads1015: fix conversion when CONFIG_PM is not set (Maxim Kochetkov)
- counter: microchip-tcb-capture: check the correct variable (Dan Carpenter)
- iio: cros_ec: Set Gyroscope default frequency to 25Hz (Gwendal Grignou)
- ARM: dts: ls1021a: fix QuadSPI-memory reg range (Matthias Schiffer)
- arm64/x86: KVM: Introduce steal-time cap (Andrew Jones)
- KVM: Documentation: Minor fixups (Andrew Jones)
- KVM: arm64: pvtime: Fix stolen time accounting across migration (Andrew Jones)
- KVM: arm64: Drop type input from kvm_put_guest (Andrew Jones)
- KVM: arm64: pvtime: Fix potential loss of stolen time (Andrew Jones)
- KVM: arm64: pvtime: steal-time is only supported when configured (Andrew Jones)
- arm64: defconfig: Enable ptn5150 extcon driver (Krzysztof Kozlowski)
- arm64: defconfig: Enable USB gadget with configfs (Krzysztof Kozlowski)
- ARM: configs: Update Integrator defconfig (Linus Walleij)
- soundwire: bus: fix typo in comment on INTSTAT registers (Pierre-Louis Bossart)
- ARM: dts: omap5: Fix DSI base address and clocks (David Shah)
- staging: greybus: audio: fix uninitialized value issue (Vaibhav Agarwal)
- staging: wlan-ng: fix out of bounds read in prism2sta_probe_usb() (Rustam Kovhaev)
- staging: greybus: audio: Uninitialized variable in gbaudio_remove_controls() (Dan Carpenter)
- ARM: dts: socfpga: fix register entry for timer3 on Arria10 (Dinh Nguyen)
- ARM: dts: logicpd-som-lv-baseboard: Fix missing video (Adam Ford)
- ARM: dts: logicpd-som-lv-baseboard: Fix broken audio (Adam Ford)
- ARM: dts: logicpd-torpedo-baseboard: Fix broken audio (Adam Ford)
- ARM: OMAP2+: Fix an IS_ERR() vs NULL check in _get_pwrdm() (Jing Xiangfeng)
- arm64: dts: xilinx: Align IOMMU nodename with dtschema (Krzysztof Kozlowski)
- arm64: dts: zynqmp: Add GTR transceivers (Laurent Pinchart)
- phy: qualcomm: fix return value check in qcom_ipq806x_usb_phy_probe() (Wei Yongjun)
- phy: qualcomm: fix platform_no_drv_owner.cocci warnings (YueHaibing)

* Sun Sep 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200913gitef2e9a563b0c.9]
- Merge ark-patches

* Sun Sep 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200913gitef2e9a563b0c.8.test]
- ef2e9a563b0c rebase
- Updated changelog for the release based on 729e3d091984 (Fedora Kernel Team)
- seccomp: don't leave dangling ->notif if file allocation fails (Tycho Andersen)
- mailmap, MAINTAINERS: move to tycho.pizza (Tycho Andersen)
- seccomp: don't leak memory when filter install races (Tycho Andersen)
- btrfs: fix NULL pointer dereference after failure to create snapshot (Filipe Manana)
- btrfs: free data reloc tree on failed mount (Josef Bacik)
- btrfs: require only sector size alignment for parent eb bytenr (Qu Wenruo)
- btrfs: fix lockdep splat in add_missing_dev (Josef Bacik)
- cifs: fix DFS mount with cifsacl/modefromsid (Ronnie Sahlberg)
- dax: fix detection of dax support for non-persistent memory block devices (Coly Li)

* Sat Sep 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200912git729e3d091984.8]
- Merge ark-patches

* Sat Sep 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200912git729e3d091984.7.test]
- 729e3d091984 rebase
- dist-merge-upstream: Checkout known branch for ci scripts (Don Zickus)
- gcov: add support for GCC 10.1 (Peter Oberparleiter)
- Updated changelog for the release based on 581cb3a26baf (Fedora Kernel Team)
- powercap: make documentation reflect code (Amit Kucheria)
- PM: <linux/device.h>: fix @em_pd kernel-doc warning (Randy Dunlap)
- powercap/intel_rapl: add support for AlderLake (Zhang Rui)
- powercap/intel_rapl: add support for RocketLake (Zhang Rui)
- powercap/intel_rapl: add support for TigerLake Desktop (Zhang Rui)
- IB/isert: Fix unaligned immediate-data handling (Sagi Grimberg)
- RDMA/rtrs-srv: Set .release function for rtrs srv device during device init (Md Haris Iqbal)
- RDMA/bnxt_re: Remove set but not used variable 'qplib_ctx' (YueHaibing)
- block: Set same_page to false in __bio_try_merge_page if ret is false (Ritesh Harjani)
- spi: stm32: fix pm_runtime_get_sync() error checking (Dan Carpenter)
- spi: Fix memory leak on splited transfers (Gustav Wiklander)
- i2c: algo: pca: Reapply i2c bus settings after reset (Evan Nimmo)
- nvme-fabrics: allow to queue requests for live queues (Sagi Grimberg)
- block: only call sched requeue_request() for scheduled requests (Omar Sandoval)
- nvme-tcp: cancel async events before freeing event struct (David Milburn)
- nvme-rdma: cancel async events before freeing event struct (David Milburn)
- nvme-fc: cancel async events before freeing event struct (David Milburn)
- nvme: Revert: Fix controller creation races with teardown flow (James Smart)
- spi: spi-cadence-quadspi: Fix mapping of buffers for DMA reads (Vignesh Raghavendra)
- block: restore a specific error code in bdev_del_partition (Christoph Hellwig)
- drm/i915: fix regression leading to display audio probe failure on GLK (Kai Vehmanen)
- i2c: npcm7xx: Fix timeout calculation (Tali Perry)
- spi: stm32: Rate-limit the 'Communication suspended' message (Marek Vasut)
- rbd: require global CAP_SYS_ADMIN for mapping and unmapping (Ilya Dryomov)
- mmc: sdio: Use mmc_pre_req() / mmc_post_req() (Adrian Hunter)
- mmc: sdhci-of-esdhc: Don't walk device-tree on every interrupt (Chris Packham)
- mmc: mmc_spi: Allow the driver to be built when CONFIG_HAS_DMA is unset (Ulf Hansson)
- mmc: sdhci-msm: Add retries when all tuning phases are found valid (Douglas Anderson)
- mmc: sdhci-acpi: Clear amd_sdhci_host on reset (Raul E Rangel)
- drm: xlnx: dpsub: Fix DMADEVICES Kconfig dependency (Laurent Pinchart)
- rapidio: Replace 'select' DMAENGINES 'with depends on' (Laurent Pinchart)
- drm/virtio: drop virtio_gpu_output->enabled (Gerd Hoffmann)
- drm/sun4i: backend: Disable alpha on the lowest plane on the A20 (Maxime Ripard)
- drm/sun4i: backend: Support alpha property on lowest plane (Maxime Ripard)
- drm/sun4i: Fix DE2 YVU handling (Jernej Skrabec)
- drm/tve200: Stabilize enable/disable (Linus Walleij)
- dma-buf: fence-chain: Document missing dma_fence_chain_init() parameter in kerneldoc (Krzysztof Kozlowski)
- dma-buf: Fix kerneldoc of dma_buf_set_name() (Krzysztof Kozlowski)
- RDMA/core: Fix reported speed and width (Kamal Heib)
- RDMA/core: Fix unsafe linked list traversal after failing to allocate CQ (Xi Wang)
- spi: spi-loopback-test: Fix out-of-bounds read (Vincent Whitchurch)
- regulator: pwm: Fix machine constraints application (Vincent Whitchurch)
- drm/virtio: fix unblank (Gerd Hoffmann)
- regulator: core: Fix slab-out-of-bounds in regulator_unlock_recursive() (Dmitry Osipenko)
- Documentation: fix dma-buf.rst underline length warning (Randy Dunlap)
- misc: eeprom: at24: register nvmem only after eeprom is ready to use (Vadym Kochan)
- drm/sun4i: Fix dsi dcs long write function (Ondrej Jirman)
- drm/ingenic: Fix driver not probing when IPU port is missing (Paul Cercueil)
- drm/ingenic: Fix leak of device_node pointer (Paul Cercueil)
- drm/sun4i: add missing put_device() call in sun8i_r40_tcon_tv_set_mux() (Yu Kuai)
- RDMA/bnxt_re: Remove the qp from list only if the qp destroy succeeds (Selvin Xavier)
- RDMA/bnxt_re: Fix driver crash on unaligned PSN entry address (Naresh Kumar PBS)
- RDMA/bnxt_re: Restrict the max_gids to 256 (Naresh Kumar PBS)
- RDMA/bnxt_re: Static NQ depth allocation (Naresh Kumar PBS)
- RDMA/bnxt_re: Fix the qp table indexing (Selvin Xavier)
- RDMA/bnxt_re: Do not report transparent vlan from QP1 (Selvin Xavier)
- RDMA/mlx4: Read pkey table length instead of hardcoded value (Mark Bloch)
- RDMA/rxe: Fix panic when calling kmem_cache_create() (Kamal Heib)
- RDMA/rxe: Fix memleak in rxe_mem_init_user (Dinghao Liu)
- drm/virtio: Revert "drm/virtio: Call the right shmem helpers" (Gurchetan Singh)
- spi: spi-cadence-quadspi: Populate get_name() interface (Vignesh Raghavendra)
- RDMA/rxe: Fix the parent sysfs read when the interface has 15 chars (Yi Zhang)
- RDMA/rtrs-srv: Replace device_register with device_initialize and device_add (Md Haris Iqbal)
- MAINTAINERS: add myself as maintainer for spi-fsl-dspi driver (Vladimir Oltean)
- regulator: remove superfluous lock in regulator_resolve_coupling() (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: cleanup regulator_ena_gpio_free() (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: plug of_node leak in regulator_register()'s error path (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: push allocation in set_consumer_device_supply() out of lock (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: push allocations in create_regulator() outside of lock (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: push allocation in regulator_ena_gpio_request() out of lock (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: push allocation in regulator_init_coupling() outside of lock (=?UTF-8?q?Micha=C5=82=20Miros=C5=82aw?=)
- regulator: fix spelling mistake "Cant" -> "Can't" (Colin Ian King)
- regulator: cros-ec-regulator: Add NULL test for devm_kmemdup call (Axel Lin)

* Fri Sep 11 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200911git581cb3a26baf.7]
- Merge ark-patches

* Fri Sep 11 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200911git581cb3a26baf.6.test]
- 581cb3a26baf rebase
- f2fs: Return EOF on unaligned end of file DIO read (Gabriel Krisman Bertazi)
- f2fs: fix indefinite loop scanning for free nid (Sahitya Tummala)
- f2fs: Fix type of section block count variables (Shin'ichiro Kawasaki)

* Thu Sep 10 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200910git7fe10096c150.5.test]
- 7fe10096c150 rebase
- kernel.spec: don't override upstream compiler flags for ppc64le (=?UTF-8?q?Dan=20Hor=C3=A1k?=)
- SUNRPC: stop printk reading past end of string ("J. Bruce Fields")
- NFS: Zero-stateid SETATTR should first return delegation (Chuck Lever)
- padata: fix possible padata_works_lock deadlock (Daniel Jordan)
- NFSv4.1 handle ERR_DELAY error reclaiming locking state on delegation recall (Olga Kornievskaia)
- xprtrdma: Release in-flight MRs on disconnect (Chuck Lever)

* Wed Sep 09 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.20200909git34d4ddd359db.4.test]
- 34d4ddd359db rebase
- Revert "drm/i915/gem: Delete unused code" (Dave Airlie)
- Revert "drm/i915/gem: Async GPU relocations only" (Dave Airlie)
- Revert "drm/i915: Remove i915_gem_object_get_dirty_page()" (Dave Airlie)
- Updated changelog for the release based on v5.9-rc4 (Fedora Kernel Team)
- drm/msm: Disable the RPTR shadow (Jordan Crouse)
- drm/msm: Disable preemption on all 5xx targets (Jordan Crouse)
- drm/msm: Enable expanded apriv support for a650 (Jordan Crouse)
- drm/msm: Split the a5xx preemption record (Jordan Crouse)
- Revert "kbuild: use -flive-patching when CONFIG_LIVEPATCH is enabled" (Josh Poimboeuf)
- scsi: mpt3sas: Don't call disable_irq from IRQ poll handler (Tomas Henzl)
- scsi: megaraid_sas: Don't call disable_irq from process IRQ poll (Tomas Henzl)
- scsi: target: iscsi: Fix hang in iscsit_access_np() when getting tpg->np_login_sem (Hou Pu)
- scsi: libsas: Set data_dir as DMA_NONE if libata marks qc as NODATA (Luo Jiaxing)
- scsi: target: iscsi: Fix data digest calculation (Varun Prakash)
- scsi: lpfc: Update lpfc version to 12.8.0.4 (James Smart)
- scsi: lpfc: Extend the RDF FPIN Registration descriptor for additional events (James Smart)
- scsi: lpfc: Fix FLOGI/PLOGI receive race condition in pt2pt discovery (James Smart)
- scsi: lpfc: Fix setting IRQ affinity with an empty CPU mask (James Smart)
- scsi: qla2xxx: Fix regression on sparc64 (=?UTF-8?q?Ren=C3=A9=20Rebe?=)
- scsi: libfc: Fix for double free() (Javed Hasan)
- scsi: pm8001: Fix memleak in pm8001_exec_internal_task_abort (Dinghao Liu)
- selftests/timers: Turn off timeout setting (Po-Hsu Lin)

* Mon Sep 07 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.4]
- Merge ark-patches

* Mon Sep 07 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc4.3.test]
- v5.9-rc4 rebase
- Linux 5.9-rc4 (Linus Torvalds)
- Updated changelog for the release based on dd9fb9bb3340 (Fedora Kernel Team)
- io_uring: fix linked deferred ->files cancellation (Pavel Begunkov)
- io_uring: fix cancel of deferred reqs with ->files (Pavel Begunkov)
- io_uring: fix explicit async read/write mapping for large segments (Jens Axboe)
- x86/entry: Unbreak 32bit fast syscall (Thomas Gleixner)
- x86/debug: Allow a single level of #DB recursion (Andy Lutomirski)
- x86/entry: Fix AC assertion (Peter Zijlstra)
- tracing/kprobes, x86/ptrace: Fix regs argument order for i386 (Vamshi K Sthambamkadi)
- iommu/vt-d: Handle 36bit addressing for x86-32 (Chris Wilson)
- iommu/amd: Do not use IOMMUv2 functionality when SME is active (Joerg Roedel)
- iommu/amd: Do not force direct mapping when SME is active (Joerg Roedel)
- iommu/amd: Use cmpxchg_double() when updating 128-bit IRTE (Suravee Suthikulpanit)
- iommu/amd: Restore IRTE.RemapEn bit after programming IRTE (Suravee Suthikulpanit)
- iommu/vt-d: Fix NULL pointer dereference in dev_iommu_priv_set() (Lu Baolu)
- iommu/vt-d: Serialize IOMMU GCMD register modifications (Lu Baolu)
- MAINTAINERS: Update QUALCOMM IOMMU after Arm SMMU drivers move (Lukas Bulwahn)
- xen: add helpers to allocate unpopulated memory (Roger Pau Monne)
- memremap: rename MEMORY_DEVICE_DEVDAX to MEMORY_DEVICE_GENERIC (Roger Pau Monne)
- xen/balloon: add header guard (Roger Pau Monne)
- x86, fakenuma: Fix invalid starting node ID (Huang Ying)
- x86/mm/32: Bring back vmalloc faulting on x86_32 (Joerg Roedel)
- x86/cmdline: Disable jump tables for cmdline.c (Arvind Sankar)

* Sun Sep 06 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200906gitdd9fb9bb3340.3]
- Merge ark-patches

* Sun Sep 06 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200906gitdd9fb9bb3340.2.test]
- dd9fb9bb3340 rebase
- include/linux/log2.h: add missing () around n in roundup_pow_of_two() (Jason Gunthorpe)
- mm/khugepaged.c: fix khugepaged's request size in collapse_file (David Howells)
- mm/hugetlb: fix a race between hugetlb sysctl handlers (Muchun Song)
- mm/hugetlb: try preferred node first when alloc gigantic page from cma (Li Xinhai)
- mm/migrate: preserve soft dirty in remove_migration_pte() (Ralph Campbell)
- mm/migrate: remove unnecessary is_zone_device_page() check (Ralph Campbell)
- mm/rmap: fixup copying of soft dirty and uffd ptes (Alistair Popple)
- mm/migrate: fixup setting UFFD_WP flag (Alistair Popple)
- mm: madvise: fix vma user-after-free (Yang Shi)
- checkpatch: fix the usage of capture group ( ... ) (Mrinal Pandey)
- fork: adjust sysctl_max_threads definition to match prototype (Tobias Klauser)
- ipc: adjust proc_ipc_sem_dointvec definition to match prototype (Tobias Klauser)
- mm: track page table modifications in __apply_to_page_range() (Joerg Roedel)
- MAINTAINERS: IA64: mark Status as Odd Fixes only (Randy Dunlap)
- MAINTAINERS: add LLVM maintainers (Nick Desaulniers)
- MAINTAINERS: update Cavium/Marvell entries (Robert Richter)
- mm: slub: fix conversion of freelist_corrupted() (Eugeniu Rosca)
- mm: memcg: fix memcg reclaim soft lockup (Xunlei Pang)
- memcg: fix use-after-free in uncharge_batch (Michal Hocko)
- xfs: don't update mtime on COW faults (Mikulas Patocka)
- ext2: don't update mtime on COW faults (Mikulas Patocka)
- Updated changelog for the release based on c70672d8d316 (Fedora Kernel Team)
- xfs: fix xfs_bmap_validate_extent_raw when checking attr fork of rt files ("Darrick J. Wong")
- ARC: [plat-hsdk]: Switch ethernet phy-mode to rgmii-id (Evgeniy Didin)
- arc: fix memory initialization for systems with two memory banks (Mike Rapoport)
- clang-format: Update with the latest for_each macro list (Miguel Ojeda)
- sparse: use static inline for __chk_{user,io}_ptr() (Luc Van Oostenryck)
- irqchip/eznps: Fix build error for !ARC700 builds (Vineet Gupta)
- ARC: show_regs: fix r12 printing and simplify (Vineet Gupta)
- Compiler Attributes: fix comment concerning GCC 4.6 (Luc Van Oostenryck)
- Compiler Attributes: remove comment about sparse not supporting __has_attribute (Luc Van Oostenryck)
- ARC: HSDK: wireup perf irq (Vineet Gupta)
- ARC: perf: don't bail setup if pct irq missing in device-tree (Vineet Gupta)
- ARC: pgalloc.h: delete a duplicated word + other fixes (Randy Dunlap)
- auxdisplay: Replace HTTP links with HTTPS ones ("Alexander A. Klimov")

* Sat Sep 05 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200905gitc70672d8d316.2]
- Merge ark-patches

* Sat Sep 05 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200905gitc70672d8d316.1.test]
- c70672d8d316 rebase
- Fedora confi gupdate ("Justin M. Forbes")
- net/packet: fix overflow in tpacket_rcv (Or Cohen)
- mm: Add PGREUSE counter (Peter Xu)
- mm/gup: Remove enfornced COW mechanism (Peter Xu)
- mm/ksm: Remove reuse_ksm_page() (Peter Xu)
- mm: do_wp_page() simplification (Linus Torvalds)
- gcov: Disable gcov build with GCC 10 (Leon Romanovsky)
- init: fix error check in clean_path() (Barret Rhoden)
- thermal: core: Fix use-after-free in thermal_zone_device_unregister() (Dmitry Osipenko)
- thermal: qcom-spmi-temp-alarm: Don't suppress negative temp (Veera Vegivada)
- thermal: ti-soc-thermal: Fix bogus thermal shutdowns for omap4430 (Tony Lindgren)
- Updated changelog for the release based on 59126901f200 (Fedora Kernel Team)
- ALSA: hda/realtek - Improved routing for Thinkpad X1 7th/8th Gen (Takashi Iwai)
- MIPS: SNI: Fix SCSI interrupt (Thomas Bogendoerfer)
- MIPS: add missing MSACSR and upper MSA initialization (Huang Pei)
- dmaengine: ti: k3-udma: Update rchan_oes_offset for am654 SYSFW ABI 3.0 (Peter Ujfalusi)
- drm/nouveau/kms/nv50-gp1xx: add WAR for EVO push buffer HW bug (Ben Skeggs)
- drm/nouveau/kms/nv50-gp1xx: disable notifies again after core update (Ben Skeggs)
- drm/nouveau/kms/nv50-: add some whitespace before debug message (Ben Skeggs)
- drm/nouveau/kms/gv100-: Include correct push header in crcc37d.c (Lyude Paul)
- drm/radeon: Prefer lower feedback dividers (Kai-Heng Feng)
- drm/amdgpu: Fix bug in reporting voltage for CIK (Sandeep Raghuraman)
- drm/amdgpu: Specify get_argument function for ci_smu_funcs (Sandeep Raghuraman)
- drm/amd/pm: enable MP0 DPM for sienna_cichlid (Jiansong Chen)
- drm/amd/pm: avoid false alarm due to confusing softwareshutdowntemp setting (Evan Quan)
- drm/amd/pm: fix is_dpm_running() run error on 32bit system (Kevin Wang)
- kconfig: remove redundant assignment prompt = prompt (Denis Efremov)
- kbuild: Documentation: clean up makefiles.rst (Randy Dunlap)
- kconfig: streamline_config.pl: check defined(ENV variable) before using it (Randy Dunlap)
- block: allow for_each_bvec to support zero len bvec (Ming Lei)
- ALSA: hda: use consistent HDAudio spelling in comments/docs (Pierre-Louis Bossart)
- libata: implement ATA_HORKAGE_MAX_TRIM_128M and apply to Sandisks (Tejun Heo)
- ALSA: hda: add dev_dbg log when driver is not selected (Pierre-Louis Bossart)
- ALSA: hda: fix a runtime pm issue in SOF when integrated GPU is disabled (Rander Wang)
- ALSA: hda: hdmi - add Rocketlake support (Rander Wang)
- io_uring: no read/write-retry on -EAGAIN error and O_NONBLOCK marked file (Jens Axboe)
- io_uring: set table->files[i] to NULL when io_sqe_file_register failed (Jiufei Xue)
- ALSA: ua101: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ALSA: usb-audio: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ASoC: txx9: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ASoC: siu: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ASoC: fsl_esai: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ALSA: hdsp: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ALSA: riptide: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ALSA: pci/asihpi: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ALSA: firewire: convert tasklets to use new tasklet_setup() API (Allen Pais)
- ALSA: core: convert tasklets to use new tasklet_setup() API (Allen Pais)
- s390: update defconfigs (Heiko Carstens)
- s390: fix GENERIC_LOCKBREAK dependency typo in Kconfig (Eric Farman)
- drm/i915: Clear the repeater bit on HDCP disable (Sean Paul)
- drm/i915: Fix sha_text population code (Sean Paul)
- drm/i915/display: Ensure that ret is always initialized in icl_combo_phy_verify_state (Nathan Chancellor)
- arm64/module: set trampoline section flags regardless of CONFIG_DYNAMIC_FTRACE (Jessica Yu)
- arm64: Remove exporting cpu_logical_map symbol (Sudeep Holla)
- blk-stat: make q->stats->lock irqsafe (Tejun Heo)
- blk-iocost: ioc_pd_free() shouldn't assume irq disabled (Tejun Heo)
- cpufreq: intel_pstate: Fix intel_pstate_get_hwp_max() for turbo disabled (Francisco Jerez)
- cpufreq: intel_pstate: Free memory only when turning off ("Rafael J. Wysocki")
- cpufreq: intel_pstate: Add ->offline and ->online callbacks ("Rafael J. Wysocki")
- cpufreq: intel_pstate: Tweak the EPP sysfs interface ("Rafael J. Wysocki")
- cpufreq: intel_pstate: Update cached EPP in the active mode ("Rafael J. Wysocki")
- cpufreq: intel_pstate: Refuse to turn off with HWP enabled ("Rafael J. Wysocki")
- block: fix locking in bdev_del_partition (Christoph Hellwig)
- block: release disk reference in hd_struct_free_work (Ming Lei)
- io_uring: fix removing the wrong file in __io_sqe_files_update() (Jiufei Xue)
- block: ensure bdi->io_pages is always initialized (Jens Axboe)
- ALSA: pcm: oss: Remove superfluous WARN_ON() for mulaw sanity check (Takashi Iwai)
- MIPS: perf: Fix wrong check condition of Loongson event IDs (Tiezhu Yang)
- Documentation/llvm: Improve formatting of commands, variables, and arguments (Nathan Chancellor)
- opp: Don't drop reference for an OPP table that was never parsed (Viresh Kumar)
- ALSA: hda - Fix silent audio output and corrupted input on MSI X570-A PRO (Dan Crawford)
- nvme-pci: cancel nvme device request before disabling (Tong Zhang)
- nvme: only use power of two io boundaries (Keith Busch)
- nvme: fix controller instance leak (Keith Busch)
- nvmet-fc: Fix a missed _irqsave version of spin_lock in 'nvmet_fc_fod_op_done()' (Christophe JAILLET)
- nvme: Fix NULL dereference for pci nvme controllers (Sagi Grimberg)
- nvme-rdma: fix reset hang if controller died in the middle of a reset (Sagi Grimberg)
- nvme-rdma: fix timeout handler (Sagi Grimberg)
- nvme-rdma: serialize controller teardown sequences (Sagi Grimberg)
- nvme-tcp: fix reset hang if controller died in the middle of a reset (Sagi Grimberg)
- nvme-tcp: fix timeout handler (Sagi Grimberg)
- nvme-tcp: serialize controller teardown sequences (Sagi Grimberg)
- nvme: have nvme_wait_freeze_timeout return if it timed out (Sagi Grimberg)
- nvme-fabrics: don't check state NVME_CTRL_NEW for request acceptance (Sagi Grimberg)
- nvmet-tcp: Fix NULL dereference when a connect data comes in h2cdata pdu (Ziye Yang)
- ALSA: hda/hdmi: always check pin power status in i915 pin fixup (Kai Vehmanen)
- ALSA: hda/realtek: Add quirk for Samsung Galaxy Book Ion NT950XCJ-X716A (Adrien Crivelli)
- ALSA: usb-audio: Add basic capture support for Pioneer DJ DJM-250MK2 (=?UTF-8?q?Franti=C5=A1ek=20Ku=C4=8Dera?=)
- ALSA: usb-audio: Add implicit feedback quirk for UR22C (Joshua Sivec)
- drivers/dma/dma-jz4780: Fix race condition between probe and irq handler (Madhuparna Bhowmik)
- dmaengine: dw-edma: Fix scatter-gather address calculation (Gustavo Pimentel)
- dmaengine: ti: k3-udma: Fix the TR initialization for prep_slave_sg (Peter Ujfalusi)
- dmaengine: pl330: Fix burst length if burst size is smaller than bus width (Marek Szyprowski)
- Revert "ALSA: hda: Add support for Loongson 7A1000 controller" (Tiezhu Yang)
- ALSA: hda/tegra: Program WAKEEN register for Tegra (Mohan Kumar)
- ALSA: hda: Fix 2 channel swapping for Tegra (Mohan Kumar)
- ALSA: ca0106: fix error code handling (Tong Zhang)
- Documentation: sound/cards: fix heading underline lengths for https: changes (Randy Dunlap)
- ALSA: usb-audio: Disable autosuspend for Lenovo ThinkStation P620 (Kai-Heng Feng)
- ALSA: firewire-digi00x: exclude Avid Adrenaline from detection (Takashi Sakamoto)
- ALSA; firewire-tascam: exclude Tascam FE-8 from detection (Takashi Sakamoto)
- mips/oprofile: Fix fallthrough placement (He Zhe)
- MIPS: Loongson64: Remove unnecessary inclusion of boot_param.h (WANG Xuerui)
- MIPS: BMIPS: Also call bmips_cpu_setup() for secondary cores (Florian Fainelli)
- MIPS: mm: BMIPS5000 has inclusive physical caches (Florian Fainelli)
- dmaengine: at_hdmac: add missing kfree() call in at_dma_xlate() (Yu Kuai)
- dmaengine: at_hdmac: add missing put_device() call in at_dma_xlate() (Yu Kuai)
- dmaengine: at_hdmac: check return value of of_find_device_by_node() in at_dma_xlate() (Yu Kuai)
- MIPS: Loongson64: Do not override watch and ejtag feature (Jiaxun Yang)
- dmaengine: of-dma: Fix of_dma_router_xlate's of_dma_xlate handling (Peter Ujfalusi)
- dmaengine: idxd: reset states after device disable or reset (Dave Jiang)
- dmaengine: acpi: Put the CSRT table after using it (Hanjun Guo)
- ata: ahci: use ata_link_info() instead of ata_link_printk() (Xu Wang)

* Fri Sep 04 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200904git59126901f200.1]
- Merge ark-patches

* Fri Sep 04 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200904git59126901f200.0.test]
- 59126901f200 rebase
- Updated changelog for the release based on fc3abb53250a (Fedora Kernel Team)
- Swap how ark-latest is built (Don Zickus)
- Add extra version bump to os-build branch (Don Zickus)
- dist-release: Avoid needless version bump. (Don Zickus)
- Add dist-fedora-release target (Don Zickus)
- Remove redundant code in dist-release (Don Zickus)
- Makefile.common rename TAG to _TAG (Don Zickus)

* Thu Sep 03 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200903gitfc3abb53250a.1]
- fc3abb53250a rebase
- Fedora config change ("Justin M. Forbes")
- Updated changelog for the release based on 9c7d619be5a0 (Fedora Kernel Team)

* Wed Sep 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200902git9c7d619be5a0.1]
- 9c7d619be5a0 rebase
- Updated changelog for the release based on b51594df17d0 (Fedora Kernel Team)

* Tue Sep 01 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.20200901gitb51594df17d0.1]
- b51594df17d0 rebase
- Fedora filter update ("Justin M. Forbes")
- Config update for Fedora ("Justin M. Forbes")
- Updated changelog for the release based on v5.9-rc3 (Fedora Kernel Team)

* Mon Aug 31 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc3.1]
- v5.9-rc3 rebase
- Updated changelog for the release based on 1127b219ce94 (Fedora Kernel Team)

* Sun Aug 30 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc2.20200830git1127b219ce94.1]
- 1127b219ce94 rebase
- Updated changelog for the release based on 4d41ead6ead9 (Fedora Kernel Team)

* Sat Aug 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc2.20200829git4d41ead6ead9.1]
- 4d41ead6ead9 rebase
- mod-sign.sh: Fix syntax flagged by shellcheck (Ben Crocker)
- Updated changelog for the release based on 15bc20c6af4c (Fedora Kernel Team)

* Thu Aug 27 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc2.20200827git15bc20c6af4c.1]
- 15bc20c6af4c rebase
- Updated changelog for the release based on 2ac69819ba9e (Fedora Kernel Team)

* Wed Aug 26 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc2.20200826git2ac69819ba9e.1]
- 2ac69819ba9e rebase
- Updated changelog for the release based on 6a9dc5fd6170 (Fedora Kernel Team)

* Tue Aug 25 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc2.20200825git6a9dc5fd6170.1]
- 6a9dc5fd6170 rebase
- Updated changelog for the release based on v5.9-rc2 (Fedora Kernel Team)

* Mon Aug 24 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc2.1]
- v5.9-rc2 rebase
- Updated changelog for the release based on c3d8f220d012 (Fedora Kernel Team)

* Sun Aug 23 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc1.20200823gitc3d8f220d012.1]
- c3d8f220d012 rebase
- Updated changelog for the release based on f873db9acd3c (Fedora Kernel Team)

* Sat Aug 22 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc1.20200822gitf873db9acd3c.1]
- f873db9acd3c rebase
- Updated changelog for the release based on da2968ff879b (Fedora Kernel Team)

* Fri Aug 21 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc1.20200821gitda2968ff879b.1]
- da2968ff879b rebase
- Temporarily remove cdomain from sphinx documentation ("Justin M. Forbes")
- Work around for gcc bug https://gcc.gnu.org/bugzilla/show_bug.cgi?id=96377 ("Justin M. Forbes")
- Updated changelog for the release based on 18445bf405cb (Fedora Kernel Team)
- enable PROTECTED_VIRTUALIZATION_GUEST for all s390x kernels (=?UTF-8?q?Dan=20Hor=C3=A1k?=)

* Wed Aug 19 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc1.20200819git18445bf405cb.1]
- 18445bf405cb rebase
- Add mlx5_vdpa to module filter for Fedora ("Justin M. Forbes")
- Add python3-sphinx_rtd_theme buildreq for docs ("Justin M. Forbes")
- kernel.spec: Remove kernel-keys directory on rpm erase (Prarit Bhargava)
- More Fedora config updates ("Justin M. Forbes")
- New config deps ("Justin M. Forbes")
- Updated changelog for the release based on 06a4ec1d9dc6 (Fedora Kernel Team)
- redhat: ark: enable CONFIG_NET_SCH_TAPRIO (Davide Caratti)
- redhat: ark: enable CONFIG_NET_SCH_ETF (Davide Caratti)

* Tue Aug 18 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.9.0-0.rc1.20200818git06a4ec1d9dc6.1]
- 06a4ec1d9dc6 rebase
- First half of config updates for Fedora ("Justin M. Forbes")
- Add config options that only show up when we prep on arm ("Justin M. Forbes")
- Config updates for Fedora ("Justin M. Forbes")
- fedora: enable enery model (Peter Robinson)
- iio: enable LTR-559 light and proximity sensor (Peter Robinson)
- iio: chemical: enable some popular chemical and partical sensors (Peter Robinson)
- More mismatches ("Justin M. Forbes")
- Fedora config change due to deps ("Justin M. Forbes")
- CONFIG_SND_SOC_MAX98390 is now selected by SND_SOC_INTEL_DA7219_MAX98357A_GENERIC ("Justin M. Forbes")
- Config change required for build part 2 ("Justin M. Forbes")
- Config change required for build ("Justin M. Forbes")
- Updates for Fedora arm architectures for the 5.9 window (Peter Robinson)
- Enable ARM_SMCCC_SOC_ID on all aarch64 kernels (Peter Robinson)
- Enable ZSTD compression algorithm on all kernels (Peter Robinson)
- Fedora config update ("Justin M. Forbes")
- Revert "Merge branch 'make_configs_fix' into 'os-build'" (Justin Forbes)
- Use the configs/generic config for SND_HDA_INTEL everywhere (Peter Robinson)
- redhat/configs/process_configs.sh: Remove *.config.orig files (Prarit Bhargava)
- redhat/configs/process_configs.sh: Add process_configs_known_broken flag (Prarit Bhargava)
- redhat/Makefile: Fix '*-configs' targets (Prarit Bhargava)
- Updated changelog for the release based on v5.8 (Fedora Kernel Team)
- Add ability to sync upstream through Makefile (Don Zickus)
- Add master merge check (Don Zickus)
- Replace hardcoded values 'os-build' and project id with variables (Don Zickus)
- gitattributes: Remove unnecesary export restrictions (Prarit Bhargava)
- redhat/Makefile.common: Fix MARKER (Prarit Bhargava)

* Mon Aug 03 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-1]
- v5.8 rebase
- Updated changelog for the release based on ac3a0c847296 (Fedora Kernel Team)

* Sun Aug 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc7.20200802gitac3a0c847296.1]
- ac3a0c847296 rebase
- Updated changelog for the release based on 7dc6fd0f3b84 (Fedora Kernel Team)

* Sat Aug 01 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc7.20200801git7dc6fd0f3b84.1]
- 7dc6fd0f3b84 rebase
- Updated changelog for the release based on 417385c47ef7 (Fedora Kernel Team)

* Fri Jul 31 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc7.20200731git417385c47ef7.1]
- 417385c47ef7 rebase
- Add new certs for dual signing with boothole ("Justin M. Forbes")
- Update secureboot signing for dual keys ("Justin M. Forbes")
- Updated changelog for the release based on d3590ebf6f91 (Fedora Kernel Team)

* Thu Jul 30 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc7.20200730gitd3590ebf6f91.1]
- d3590ebf6f91 rebase
- Updated changelog for the release based on 6ba1b005ffc3 (Fedora Kernel Team)

* Wed Jul 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc7.20200729git6ba1b005ffc3.1]
- 6ba1b005ffc3 rebase
- Revert "dt-bindings: Add doc for Pine64 Pinebook Pro" (Peter Robinson)
- fedora: enable LEDS_SGM3140 for arm configs (Peter Robinson)
- Updated changelog for the release based on v5.8-rc7 (Fedora Kernel Team)

* Mon Jul 27 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc7.1]
- v5.8-rc7 rebase
- Updated changelog for the release based on 04300d66f0a0 (Fedora Kernel Team)

* Sun Jul 26 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc6.20200726git04300d66f0a0.1]
- 04300d66f0a0 rebase
- Updated changelog for the release based on 23ee3e4e5bd2 (Fedora Kernel Team)

* Sat Jul 25 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc6.20200725git23ee3e4e5bd2.1]
- 23ee3e4e5bd2 rebase
- Enable CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG ("Justin M. Forbes")
- Updated changelog for the release based on f37e99aca03f (Fedora Kernel Team)

* Fri Jul 24 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc6.20200724gitf37e99aca03f.1]
- f37e99aca03f rebase
- Updated changelog for the release based on d15be546031c (Fedora Kernel Team)

* Thu Jul 23 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc6.20200723gitd15be546031c.1]
- d15be546031c rebase
- fedora: arm: Update some meson config options (Peter Robinson)
- Updated changelog for the release based on 4fa640dc5230 (Fedora Kernel Team)

* Tue Jul 21 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc6.20200721git4fa640dc5230.1]
- 4fa640dc5230 rebase
- Updated changelog for the release based on 5714ee50bb43 (Fedora Kernel Team)
- redhat/docs: Add Fedora RPM tagging date (Prarit Bhargava)

* Mon Jul 20 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc6.20200720git5714ee50bb43.1]
- 5714ee50bb43 rebase
- Updated changelog for the release based on f932d58abc38 (Fedora Kernel Team)

* Sun Jul 19 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc5.20200719gitf932d58abc38.1]
- f932d58abc38 rebase
- Updated changelog for the release based on 6a70f89cc58f (Fedora Kernel Team)

* Sat Jul 18 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc5.20200718git6a70f89cc58f.1]
- 6a70f89cc58f rebase
- Updated changelog for the release based on 07a56bb875af (Fedora Kernel Team)

* Fri Jul 17 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc5.20200717git07a56bb875af.1]
- 07a56bb875af rebase
- redhat/configs: Fix common CONFIGs (Prarit Bhargava)
- redhat/configs: General CONFIG cleanups (Prarit Bhargava)
- redhat/configs: Update & generalize evaluate_configs (Prarit Bhargava)
- arch/x86: Remove vendor specific CPU ID checks (Prarit Bhargava)
- Updated changelog for the release based on e9919e11e219 (Fedora Kernel Team)

* Wed Jul 15 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc5.20200715gite9919e11e219.1]
- e9919e11e219 rebase
- arm64: dts: sun50i-a64-pinephone: Add touchscreen support (Ondrej Jirman)
- arm64: dts: sun50i-a64-pinephone: Enable LCD support on PinePhone (Icenowy Zheng)
- drm/panel: st7703: Assert reset prior to powering down the regulators (Ondrej Jirman)
- drm/panel: st7703: Enter sleep after display off (Ondrej Jirman)
- drm/panel: st7703: Add support for Xingbangda XBD599 (Ondrej Jirman)
- drm/panel: st7703: Move generic part of init sequence to enable callback (Ondrej Jirman)
- drm/panel: st7703: Move code specific to jh057n closer together (Ondrej Jirman)
- drm/panel: st7703: Prepare for supporting multiple panels (Ondrej Jirman)
- drm/panel: st7703: Rename functions from jh057n prefix to st7703 (Ondrej Jirman)
- drm/panel: rocktech-jh057n00900: Rename the driver to st7703 (Ondrej Jirman)
- dt-bindings: panel: Add compatible for Xingbangda XBD599 panel (Ondrej Jirman)
- dt-bindings: panel: Convert rocktech, jh057n00900 to yaml (Ondrej Jirman)
- dt-bindings: vendor-prefixes: Add Xingbangda (Icenowy Zheng)
- Revert "arm64: allwinner: dts: a64: add LCD-related device nodes for PinePhone" (Peter Robinson)
- Revert "drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation" (Peter Robinson)
- Revert "drm: panel: add Xingbangda XBD599 panel" (Peter Robinson)
- Revert "dt-bindings: panel: add binding for Xingbangda XBD599 panel" (Peter Robinson)
- selinux: allow reading labels before policy is loaded (Jonathan Lebon)
- Fixes "acpi: prefer booting with ACPI over DTS" to be RHEL only (Peter Robinson)
- Update config for renamed panel driver. (Peter Robinson)
- Enable SERIAL_SC16IS7XX for SPI interfaces (Peter Robinson)
- Updated changelog for the release based on dcde237b9b0e (Fedora Kernel Team)

* Wed Jul 08 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc4.20200708gitdcde237b9b0e.1]
- dcde237b9b0e rebase
- Updated changelog for the release based on v5.8-rc4 (Fedora Kernel Team)

* Mon Jul 06 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc4.1]
- v5.8-rc4 rebase
- Updated changelog for the release based on cd77006e01b3 (Fedora Kernel Team)

* Thu Jul 02 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc3.20200702gitcd77006e01b3.1]
- cd77006e01b3 rebase
- Updated changelog for the release based on v5.8-rc3 (Fedora Kernel Team)

* Mon Jun 29 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc3.1]
- v5.8-rc3 rebase
- s390x-zfcpdump: Handle missing Module.symvers file (Don Zickus)
- Updated changelog for the release based on 8be3a53e18e0 (Fedora Kernel Team)

* Thu Jun 25 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc2.20200625git8be3a53e18e0.1]
- 8be3a53e18e0 rebase
- redhat: Replace hardware.redhat.com link in Unsupported message (Prarit Bhargava)
- redhat/configs: Add .tmp files to .gitignore (Prarit Bhargava)
- disable uncommon TCP congestion control algorithms (Davide Caratti)
- Updated changelog for the release based on dd0d718152e4 (Fedora Kernel Team)

* Tue Jun 23 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc2.20200623gitdd0d718152e4.1]
- dd0d718152e4 rebase
- Add new bpf man pages ("Justin M. Forbes")
- Add default option for CONFIG_ARM64_BTI_KERNEL to pending-common so that eln kernels build ("Justin M. Forbes")
- Updated changelog for the release based on 625d3449788f (Fedora Kernel Team)

* Mon Jun 22 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc2.20200622git625d3449788f.1]
- 625d3449788f rebase
- Updated changelog for the release based on 1b5044021070 (Fedora Kernel Team)

* Thu Jun 18 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc1.20200618git1b5044021070.1]
- 1b5044021070 rebase
- redhat/Makefile: Add fedora-configs and rh-configs make targets (Prarit Bhargava)
- Updated changelog for the release based on 69119673bd50 (Fedora Kernel Team)
- redhat/configs: Use SHA512 for module signing (Prarit Bhargava)
- genspec.sh: 'touch' empty Patchlist file for single tarball (Don Zickus)

* Wed Jun 17 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc1.20200617git69119673bd50.1]
- 69119673bd50 rebase
- Updated changelog for the release based on a5dc8300df75 (Fedora Kernel Team)

* Tue Jun 16 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc1.20200616gita5dc8300df75.1]
- a5dc8300df75 rebase
- Fedora config update for rc1 ("Justin M. Forbes")
- Updated changelog for the release based on v5.8-rc1 (Fedora Kernel Team)

* Sun Jun 14 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc1.1]
- v5.8-rc1 rebase
- Updated changelog for the release based on df2fbf5bfa0e (Fedora Kernel Team)

* Sat Jun 13 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc0.20200613gitdf2fbf5bfa0e.1]
- df2fbf5bfa0e rebase
- Updated changelog for the release based on b791d1bdf921 (Fedora Kernel Team)

* Fri Jun 12 2020 Fedora Kernel Team <kernel-team@fedoraproject.org> [5.8.0-0.rc0.20200612gitb791d1bdf921.1]
- b791d1bdf921 rebase
- PCI: tegra: Revert raw_violation_fixup for tegra124 (Nicolas Chauvet)
- One more Fedora config update ("Justin M. Forbes")
- Change ark CONFIG_COMMON_CLK to yes, it is selected already by other options ("Justin M. Forbes")
- Fix PATCHLEVEL for merge window ("Justin M. Forbes")
- More module filtering for Fedora ("Justin M. Forbes")
- Update filters for rnbd in Fedora ("Justin M. Forbes")
- redhat/Makefile.common: fix RPMKSUBLEVEL condition (Ondrej Mosnacek)
- redhat/Makefile: silence KABI tar output (Ondrej Mosnacek)
- Fix up module filtering for 5.8 ("Justin M. Forbes")
- More Fedora config work ("Justin M. Forbes")
- RTW88BE and CE have been extracted to their own modules ("Justin M. Forbes")
- Set CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK for Fedora ("Justin M. Forbes")
- Arm64 Use Branch Target Identification for kernel ("Justin M. Forbes")
- Fedora config updates ("Justin M. Forbes")
- Change value of CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE ("Justin M. Forbes")
- Fix configs for Fedora ("Justin M. Forbes")
- Fix update_scripts.sh unselective pattern sub (David Howells)
- Updated changelog for the release based on b0c3ba31be3e ("CKI@GitLab")
- Drop the static path configuration for the Sphinx docs (Jeremy Cline)
- Sign off generated configuration patches (Jeremy Cline)
- Use __make macro instead of make (Tom Stellard)
- redhat/configs: Enable CONFIG_SMC91X and disable CONFIG_SMC911X (Prarit Bhargava) [http://bugzilla.redhat.com/1722136]

* Thu May 28 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc7.20200528gitb0c3ba31be3e.1]
- b0c3ba31be3e rebase
- Updated changelog for the release based on 444fc5cde643 ("CKI@GitLab")

* Wed May 27 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc7.20200527git444fc5cde643.1]
- 444fc5cde643 rebase
- platform/x86: sony-laptop: SNC calls should handle BUFFER types (Mattia Dongili)
- virt: vbox: Log unknown ioctl requests as error (Hans de Goede)
- virt: vbox: Add a few new vmmdev request types to the userspace whitelist (Hans de Goede)
- virt: vbox: Add support for the new VBG_IOCTL_ACQUIRE_GUEST_CAPABILITIES ioctl (Hans de Goede)
- virt: vbox: Add vbg_set_host_capabilities() helper function (Hans de Goede)
- virt: vbox: Rename guest_caps struct members to set_guest_caps (Hans de Goede)
- virt: vbox: Fix guest capabilities mask check (Hans de Goede)
- virt: vbox: Fix VBGL_IOCTL_VMMDEV_REQUEST_BIG and _LOG req numbers to match upstream (Hans de Goede)
- kms/nv50-: Share DP SST mode_valid() handling with MST (Lyude Paul)
- kms/nv50-: Move 8BPC limit for MST into nv50_mstc_get_modes() (Lyude Paul)
- kms/gv100-: Add support for interlaced modes (Lyude Paul)
- kms/nv50-: Probe SOR and PIOR caps for DP interlacing support (Lyude Paul)
- kms/nv50-: Initialize core channel in nouveau_display_create() (Lyude Paul)
- disp/hda/gv100-: NV_PDISP_SF_AUDIO_CNTRL0 register moved (Ben Skeggs)
- disp/hda/gf119-: select HDA device entry based on bound head (Ben Skeggs)
- disp/hda/gf119-: add HAL for programming device entry in SF (Ben Skeggs)
- disp/hda/gt215-: pass head to nvkm_ior.hda.eld() (Ben Skeggs)
- disp/nv50-: increase timeout on pio channel free() polling (Ben Skeggs)
- kms: Fix regression by audio component transition (Takashi Iwai)
- device: use regular PRI accessors in chipset detection (Ben Skeggs)
- device: detect vGPUs (Karol Herbst)
- device: detect if changing endianness failed (Karol Herbst)
- device: rework mmio mapping code to get rid of second map (Karol Herbst)
- mmu: Remove unneeded semicolon (Zheng Bin)
- drm: Use generic helper to check _PR3 presence (Kai-Heng Feng)
- acr: Use kmemdup instead of kmalloc and memcpy (Zou Wei)
- core/memory: remove redundant assignments to variable ret (Colin Ian King)
- disp/gv100-: expose capabilities class (Ben Skeggs)
- Remove typoed config file aarch64CONFIG_SM_GCC_8150 ("Justin M. Forbes")
- Updated changelog for the release based on v5.7-rc7 ("CKI@GitLab")
- redhat: Add dummy-module kernel module (Prarit Bhargava)
- redhat: enable CONFIG_LWTUNNEL_BPF (Jiri Benc)

* Mon May 25 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc7.1]
- v5.7-rc7 rebase
- Updated changelog for the release based on caffb99b6929 ("CKI@GitLab")

* Sun May 24 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc6.20200524gitcaffb99b6929.1]
- caffb99b6929 rebase
- Updated changelog for the release based on 444565650a5f ("CKI@GitLab")

* Sat May 23 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc6.20200523git444565650a5f.1]
- 444565650a5f rebase
- x86: Fix compile issues with rh_check_supported() (Don Zickus)
- redhat/Makefile: Fix RHEL8 python warning (Prarit Bhargava)
- kernel.spec: fix 'make scripts' for kernel-devel package (Brian Masney)
- Makefile: correct help text for dist-cross-<arch>-rpms (Brian Masney)
- Add Documentation back to kernel-devel as it has Kconfig now ("Justin M. Forbes")
- Updated changelog for the release based on 642b151f45dd ("CKI@GitLab")
- redhat: Change Makefile target names to dist- (Prarit Bhargava)
- configs: Disable Serial IR driver (Prarit Bhargava)

* Tue May 19 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc6.20200519git642b151f45dd.1]
- 642b151f45dd rebase
- pwm: lpss: Fix get_state runtime-pm reference handling (Hans de Goede)
- Updated changelog for the release based on v5.7-rc6 ("CKI@GitLab")

* Mon May 18 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc6.1]
- v5.7-rc6 rebase
- Updated changelog for the release based on 3d1c1e5931ce ("CKI@GitLab")

* Sun May 17 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc5.20200517git3d1c1e5931ce.1]
- 3d1c1e5931ce rebase
- Updated changelog for the release based on 12bf0b632ed0 ("CKI@GitLab")

* Sat May 16 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc5.20200516git12bf0b632ed0.1]
- 12bf0b632ed0 rebase
- Updated changelog for the release based on 1ae7efb38854 ("CKI@GitLab")

* Fri May 15 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc5.20200515git1ae7efb38854.1]
- 1ae7efb38854 rebase
- Updated changelog for the release based on 24085f70a6e1 ("CKI@GitLab")

* Wed May 13 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc5.20200513git24085f70a6e1.1]
- 24085f70a6e1 rebase
- Updated changelog for the release based on 152036d1379f ("CKI@GitLab")

* Tue May 12 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc5.20200512git152036d1379f.1]
- 152036d1379f rebase
- Updated changelog for the release based on v5.7-rc5 ("CKI@GitLab")
- Fix "multiple files for package kernel-tools" (Pablo Greco)

* Mon May 11 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc5.1]
- v5.7-rc5 rebase
- Updated changelog for the release based on e99332e7b4cd ("CKI@GitLab")

* Sun May 10 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.20200510gite99332e7b4cd.1]
- e99332e7b4cd rebase
- Updated changelog for the release based on d5eeab8d7e26 ("CKI@GitLab")

* Sat May 09 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.20200509gitd5eeab8d7e26.1]
- d5eeab8d7e26 rebase
- Add zero-commit to format-patch options ("Justin M. Forbes")
- Updated changelog for the release based on 79dede78c057 ("CKI@GitLab")
- Introduce a Sphinx documentation project (Jeremy Cline)

* Fri May 08 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.20200508git79dede78c057.1]
- 79dede78c057 rebase
- Updated changelog for the release based on a811c1fa0a02 ("CKI@GitLab")

* Thu May 07 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.20200507gita811c1fa0a02.1]
- a811c1fa0a02 rebase
- perf cs-etm: Move defined of traceid_list (Leo Yan)
- Updated changelog for the release based on dc56c5acd850 ("CKI@GitLab")

* Wed May 06 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.20200506gitdc56c5acd850.1]
- dc56c5acd850 rebase
- Updated changelog for the release based on 47cf1b422e60 ("CKI@GitLab")

* Tue May 05 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.20200505git47cf1b422e60.1]
- 47cf1b422e60 rebase
- Build ARK against ELN (Don Zickus)
- Updated changelog for the release based on v5.7-rc4 ("CKI@GitLab")

* Mon May 04 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc4.1]
- v5.7-rc4 rebase
- Updated changelog for the release based on f66ed1ebbfde ("CKI@GitLab")

* Sun May 03 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc3.20200503gitf66ed1ebbfde.1]
- f66ed1ebbfde rebase
- Updated changelog for the release based on 690e2aba7beb ("CKI@GitLab")

* Sat May 02 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc3.20200502git690e2aba7beb.1]
- 690e2aba7beb rebase
- Updated changelog for the release based on c45e8bccecaf ("CKI@GitLab")
- Drop the requirement to have a remote called linus (Jeremy Cline)
- Rename 'internal' branch to 'os-build' (Don Zickus)

* Fri May 01 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc3.20200501gitc45e8bccecaf.1]
- c45e8bccecaf rebase
- Updated changelog for the release based on 1d2cc5ac6f66 ("CKI@GitLab")

* Wed Apr 29 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc3.20200429git1d2cc5ac6f66.1]
- 1d2cc5ac6f66 rebase
- Add cec to the filter overrides ("Justin M. Forbes")
- Add overrides to filter-modules.sh ("Justin M. Forbes")
- Copy Makefile.rhelver as a source file rather than a patch (Jeremy Cline)
- Move the sed to clear the patch templating outside of conditionals ("Justin M. Forbes")
- Only include open merge requests with "Include in Releases" label (Jeremy Cline)
- Exit non-zero if the tag already exists for a release (Jeremy Cline)
- Adjust the changelog update script to not push anything (Jeremy Cline)
- Drop --target noarch from the rh-rpms make target (Jeremy Cline)

* Fri Apr 24 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc2.20200424gitb4f633221f0a.1]
- b4f633221f0a rebase

* Thu Apr 23 2020 CKI@GitLab <cki-project@redhat.com> [5.7.0-0.rc2.20200423git7adc4b399952.1]
- 7adc4b399952 rebase
- Match template format in kernel.spec.template ("Justin M. Forbes")
- Break out the Patches into individual files for dist-git ("Justin M. Forbes")
- Break the Red Hat patch into individual commits (Jeremy Cline)
- Adjust module filtering so CONFIG_DRM_DP_CEC can be set (Jeremy Cline)
- Add a script to generate release tags and branches (Jeremy Cline)
- Set CONFIG_VDPA for fedora ("Justin M. Forbes")
- Provide defaults in ark-rebase-patches.sh (Jeremy Cline)
- Default ark-rebase-patches.sh to not report issues (Jeremy Cline)

* Mon Apr 20 2020 Jeremy Cline <jcline@redhat.com> [5.7.0-0.rc2.2]
- Package gpio-watch in kernel-tools (Jeremy Cline)

* Mon Apr 20 2020 Jeremy Cline <jcline@redhat.com> [5.7.0-0.rc2.1]
- v5.7-rc2 rebase
- Add a README to the dist-git repository (Jeremy Cline)
- Copy distro files rather than moving them (Jeremy Cline)
- Drop DIST from release commits and tags (Jeremy Cline)
- Place the buildid before the dist in the release (Jeremy Cline)
- Sync up with Fedora arm configuration prior to merging (Jeremy Cline)
- Disable CONFIG_PROTECTED_VIRTUALIZATION_GUEST for zfcpdump (Jeremy Cline)

* Tue Apr 14 2020 Jeremy Cline <jcline@redhat.com> [5.7.0-0.rc1.3.fc33]
- Include bpftool-struct_ops man page in the bpftool package (Jeremy Cline)

* Mon Apr 13 2020 Jeremy Cline <jcline@redhat.com> [5.7.0-0.rc1.2.fc33]
- Add sharedbuffer_configuration.py to the pathfix.py script (Jeremy Cline)

* Mon Apr 13 2020 Jeremy Cline <jcline@redhat.com> [5.7.0-0.rc1.1.fc33]
- v5.7-rc1 rebase
- tty/sysrq: Export sysrq_mask() (Dmitry Safonov)
- e1000e: bump up timeout to wait when ME un-configure ULP mode (Aaron Ma)
- Drop RH_FEDORA in favor of the now-merged RHEL_DIFFERENCES (Jeremy Cline)
- Sync up Fedora configs from the first week of the merge window (Jeremy Cline)
- Add a script to test if all commits are signed off (Jeremy Cline)
- Fix a painfully obvious YAML syntax error in .gitlab-ci.yml (Jeremy Cline)
- Migrate blacklisting floppy.ko to mod-blacklist.sh (Don Zickus)
- kernel packaging: Combine mod-blacklist.sh and mod-extra-blacklist.sh (Don Zickus)
- kernel packaging: Fix extra namespace collision (Don Zickus)
- mod-extra.sh: Rename to mod-blacklist.sh (Don Zickus)
- mod-extra.sh: Make file generic (Don Zickus)
- Fix make rh-configs-arch (Don Zickus)
- Add in armv7hl kernel header support (Don Zickus)
- Disable all BuildKernel commands when only building headers (Don Zickus)
- Add RHMAINTAINERS file and supporting conf (Don Zickus)

* Mon Mar 30 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc7.1.elrdy]
- v5.6-rc7 rebase
- Drop any gitlab-ci patches from ark-patches (Jeremy Cline)
- Build the srpm for internal branch CI using the vanilla tree (Jeremy Cline)
- arm64: allwinner: dts: a64: add LCD-related device nodes for PinePhone (Icenowy Zheng)
- drm/sun4i: sun6i_mipi_dsi: fix horizontal timing calculation (Icenowy Zheng)
- drm: panel: add Xingbangda XBD599 panel (Icenowy Zheng)
- dt-bindings: panel: add binding for Xingbangda XBD599 panel (Icenowy Zheng)
- Pull in the latest ARM configurations for Fedora (Jeremy Cline)
- USB: pci-quirks: Add Raspberry Pi 4 quirk (Nicolas Saenz Julienne)
- PCI: brcmstb: Wait for Raspberry Pi's firmware when present (Nicolas Saenz Julienne)
- firmware: raspberrypi: Introduce vl805 init routine (Nicolas Saenz Julienne)
- soc: bcm2835: Sync xHCI reset firmware property with downstream (Nicolas Saenz Julienne)
- drm/i915: Force DPCD backlight mode for some Dell CML 2020 panels (Lyude Paul)
- drm/i915: Force DPCD backlight mode on X1 Extreme 2nd Gen 4K AMOLED panel (Lyude Paul)
- drm/dp: Introduce EDID-based quirks (Lyude Paul)
- drm/i915: Auto detect DPCD backlight support by default (Lyude Paul)
- drm/i915: Fix DPCD register order in intel_dp_aux_enable_backlight() (Lyude Paul)
- drm/i915: Assume 100 brightness when not in DPCD control mode (Lyude Paul)
- drm/i915: Fix eDP DPCD aux max backlight calculations (Lyude Paul)
- drm/dp_mst: Fix drm_dp_check_mstb_guid() return code (Lyude Paul)
- drm/dp_mst: Make drm_dp_mst_dpcd_write() consistent with drm_dp_dpcd_write() (Lyude Paul)
- drm/dp_mst: Fix W=1 warnings (Benjamin Gaignard)
- ARM: fix __get_user_check() in case uaccess_* calls are not inlined (Masahiro Yamada)
- mm/kmemleak: skip late_init if not skip disable (Murphy Zhou)
- KEYS: Make use of platform keyring for module signature verify (Robert Holmes)
- Drop that for now (Laura Abbott)
- Input: rmi4 - remove the need for artificial IRQ in case of HID (Benjamin Tissoires)
- arm64: dts: rockchip: Add initial support for Pinebook Pro (Tobias Schramm)
- dt-bindings: Add doc for Pine64 Pinebook Pro (Emmanuel Vadot)
- arm64: dts: allwinner: Add initial support for Pine64 PinePhone (Ondrej Jirman)
- dt-bindings: arm: sunxi: Add PinePhone 1.0 and 1.1 bindings (Ondrej Jirman)
- arm64: dts: sun50i-a64: Add i2c2 pins (Ondrej Jirman)
- arm64: dts: allwinner: a64: add support for PineTab (Icenowy Zheng)
- dt-bindings: arm: sunxi: add binding for PineTab tablet (Icenowy Zheng)
- arm64: allwinner: a64: enable LCD-related hardware for Pinebook (Icenowy Zheng)
- drm/panel: simple: Add NewEast Optoelectronics CO., LTD WJFH116008A panel support (Vasily Khoruzhick)
- dt-bindings: display: simple: Add NewEast Optoelectronics WJFH116008A compatible (Vasily Khoruzhick)
- dt-bindings: Add Guangdong Neweast Optoelectronics CO. LTD vendor prefix (Vasily Khoruzhick)
- drm/bridge: anx6345: don't print error message if regulator is not ready (Vasily Khoruzhick)
- drm/bridge: anx6345: Fix getting anx6345 regulators (Samuel Holland)
- arm64: dts: allwinner: a64: Add MBUS controller node (Jernej Skrabec)
- dt-bindings: interconnect: sunxi: Add A64 MBUS compatible (Jernej Skrabec)
- arm64: dts: allwinner: pinebook: Remove unused AXP803 regulators (Samuel Holland)
- arm64: dts: allwinner: pinebook: Fix 5v0 boost regulator (Samuel Holland)
- arm64: dts: allwinner: pinebook: Fix backlight regulator (Samuel Holland)
- arm64: dts: allwinner: pinebook: Add GPIO port regulators (Samuel Holland)
- arm64: dts: allwinner: pinebook: Document MMC0 CD pin name (Samuel Holland)
- arm64: dts: allwinner: pinebook: Make simplefb more consistent (Samuel Holland)
- arm64: dts: allwinner: pinebook: Sort device tree nodes (Samuel Holland)
- arm64: dts: allwinner: pinebook: Remove unused vcc3v3 regulator (Samuel Holland)
- arm64: dts: imx8mq-phanbell: Add support for ethernet (Alifer Moraes)
- backlight: lp855x: Ensure regulators are disabled on probe failure (Jon Hunter)
- regulator: pwm: Don't warn on probe deferral (Jon Hunter)
- ARM64: tegra: Fix Tegra194 PCIe compatible string ("Signed-off-by: Jon Hunter")
- serial: 8250_tegra: Create Tegra specific 8250 driver (Jeff Brasen)
- ARM64: tegra: Populate LP8557 backlight regulator (Jon Hunter)
- ARM64: tegra: Fix Tegra186 SOR supply (Jon Hunter)
- ARM64: tegra: Add EEPROM supplies (Jon Hunter)
- ARM64: Tegra: Enable I2C controller for EEPROM (Jon Hunter)
- ARM: dts: bcm2711: Move emmc2 into its own bus (Nicolas Saenz Julienne)
- irqchip/bcm2835: Quiesce IRQs left enabled by bootloader (Lukas Wunner)
- ARM: dts: bcm2711-rpi-4-b: Add SoC GPIO labels (Stefan Wahren)
- pinctrl: bcm2835: Add support for all GPIOs on BCM2711 (Stefan Wahren)
- pinctrl: bcm2835: Refactor platform data (Stefan Wahren)
- pinctrl: bcm2835: Drop unused define (Stefan Wahren)
- ARM: tegra: usb no reset (Peter Robinson)
- arm: make CONFIG_HIGHPTE optional without CONFIG_EXPERT (Jon Masters)
- Revert "Add a SysRq option to lift kernel lockdown" (Jeremy Cline)
- Fix xz memory usage issue (Neil Horman)
- Use ark-latest instead of master for update script (Jeremy Cline)
- Move the CI jobs back into the ARK repository (Jeremy Cline)
- Revert "[redhat] Apply a second patch set in Fedora build roots" (Jeremy Cline)
- Sync up ARK's Fedora config with the dist-git repository (Jeremy Cline)

* Mon Mar 09 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc5.1.elrdy]
- v5.6-rc5 rebase
- Pull in the latest configuration changes from Fedora (Jeremy Cline)
- configs: enable CONFIG_NET_SCH_CBS (Marcelo Ricardo Leitner)

* Fri Mar 06 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc4.2.elrdy]
- Disable CONFIG_DRM_DP_CEC temporarily (Jeremy Cline)

* Fri Mar 06 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc4.1.elrdy]
- v5.6-rc4 rebase
- redhat: rh_kabi: deduplication friendly structs (Jiri Benc)
- redhat: rh_kabi add a comment with warning about RH_KABI_EXCLUDE usage (Jiri Benc)
- redhat: rh_kabi: introduce RH_KABI_EXTEND_WITH_SIZE (Jiri Benc)
- redhat: rh_kabi: Indirect EXTEND macros so nesting of other macros will resolve. (Don Dutile)
- redhat: rh_kabi: Fix RH_KABI_SET_SIZE to use dereference operator (Tony Camuso)
- redhat: rh_kabi: Add macros to size and extend structs (Prarit Bhargava)
- mptsas: pci-id table changes (Laura Abbott)
- mptsas: Taint kernel if mptsas is loaded (Laura Abbott)
- mptspi: pci-id table changes (Laura Abbott)
- mptspi: Taint kernel if mptspi is loaded (Laura Abbott)
- kernel: add SUPPORT_REMOVED kernel taint (Tomas Henzl) [1602033]
- Rename RH_DISABLE_DEPRECATED to RHEL_DIFFERENCES (Don Zickus)
- Revert "Drop references to SCSI PCI IDs we remove" (Don Zickus)
- Revert "mpt*: remove certain deprecated pci-ids" (Don Zickus)
- Revert "megaraid_sas: remove deprecated pci-ids" (Don Zickus)
- Revert "aacraid: Remove depreciated device and vendor PCI id's" (Don Zickus)
- Revert "qla4xxx: Remove deprecated PCI IDs from RHEL 8" (Don Zickus)
- Revert "hpsa: remove old cciss-based smartarray pci ids" (Don Zickus)
- Revert "hpsa: modify hpsa driver version" (Don Zickus)
- Revert "Removing Obsolete hba pci-ids from rhel8" (Don Zickus)
- Revert "be2iscsi: remove unsupported device IDs" (Don Zickus)
- Revert "be2iscsi: remove BE3 family support" (Don Zickus)
- Revert "qla2xxx: Remove PCI IDs of deprecated adapter" (Don Zickus)
- Drop configuration options in fedora/ that no longer exist (Jeremy Cline)
- Set RH_FEDORA for ARK and Fedora (Jeremy Cline)
- Add option of 13 for FORCE_MAX_ZONEORDER (Peter Robinson)
- Introduce RH_FEDORA config for Fedora-specific patches (Jeremy Cline)
- redhat/kernel.spec: Include the release in the kernel COPYING file (Jeremy Cline)

* Mon Feb 17 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc2.2.elrdy]
- Disable CONFIG_DRM_DP_CEC temporarily (Jeremy Cline)
- Drop references to SCSI PCI IDs we remove (Jeremy Cline)

* Mon Feb 17 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc2.1.elrdy]
- v5.6-rc2 rebase
- redhat/kernel.spec: add scripts/jobserver-exec to py3_shbang_opts list (Jeremy Cline)
- redhat/kernel.spec: package bpftool-gen man page (Jeremy Cline)

* Thu Feb 13 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc1.4.elrdy]
- Package bpftool-gen man page (Jeremy Cline)

* Thu Feb 13 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc1.3.elrdy]
- Used Python 3 for scripts/jobserver-exec (Jeremy Cline)

* Wed Feb 12 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc1.2.elrdy]
- Disable CONFIG_DRM_DP_CEC temporarily (Jeremy Cline)

* Wed Feb 12 2020 Jeremy Cline <jcline@redhat.com> [5.6.0-0.rc1.1.elrdy]
- v5.6-rc1 rebase
- Fix up the EFI secureboot rebase (Jeremy Cline)
- distgit-changelog: handle multiple y-stream BZ numbers (Bruno Meneguele)
- redhat/kernel.spec: remove all inline comments (Bruno Meneguele)
- redhat/genspec: awk unknown whitespace regex pattern (Bruno Meneguele)
- Improve the readability of gen_config_patches.sh (Jeremy Cline)
- Fix some awkward edge cases in gen_config_patches.sh (Jeremy Cline)
- Updated changelog (Jeremy Cline)
- Update the CI environment to use Fedora 31 (Jeremy Cline)

* Tue Jan 28 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-1.elrdy]
- v5.5 rebase
- Revert "Turn off CONFIG_AX25" (Laura Abbott)

* Thu Jan 23 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc7.1.elrdy]
- v5.5-rc7 rebase

* Wed Jan 15 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc6.1.elrdy]
- v5.5-rc6 rebase
- s390: Lock down the kernel when the IPL secure flag is set (Jeremy Cline)
- configs: Enable CONFIG_KEY_DH_OPERATIONS on ARK (Ondrej Mosnacek)
- redhat: drop whitespace from with_gcov macro (Jan Stancek) [INTERNAL]

* Mon Jan 06 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc5.1.elrdy]
- v5.5-rc5 rebase

* Mon Jan 06 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc4.1.elrdy]
- v5.5-rc4 rebase

* Fri Jan 03 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc3.1.elrdy]
- v5.5-rc3 rebase
- Turn on BLAKE2B for Fedora (Jeremy Cline)
- configs: Adjust CONFIG_MPLS_ROUTING and CONFIG_MPLS_IPTUNNEL (Laura Abbott)
- New configs in lib/crypto (Jeremy Cline)
- New configs in drivers/char (Jeremy Cline)

* Fri Jan 03 2020 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc2.1.elrdy]
- v5.5-rc2 rebase
- Convert pr_warning to pr_warn in secureboot.c (Jeremy Cline)
- Enable CRYPTO_BLAKE2B as its being selected automatically (Jeremy Cline)
- kernel.spec.template: Clean up stray *.h.s files (Laura Abbott)
- Build the SRPM in the CI job (Jeremy Cline)
- Fix up released_kernel case (Laura Abbott)
- Add label so the Gitlab to email bridge ignores the changelog (Jeremy Cline)
- New configs in net/tls (Jeremy Cline)
- New configs in net/tipc (Jeremy Cline)
- New configs in lib/kunit (Jeremy Cline)
- New configs in lib/Kconfig.debug (Jeremy Cline)
- New configs in drivers/ptp (Jeremy Cline)
- New configs in drivers/nvme (Jeremy Cline)
- New configs in drivers/net/phy (Jeremy Cline)
- New configs in drivers/crypto (Jeremy Cline)
- New configs in crypto/Kconfig (Jeremy Cline)
- New configs in arch/arm64 (Jeremy Cline)

* Fri Dec 13 2019 Jeremy Cline <jcline@redhat.com> [5.5.0-0.rc1.1.elrdy]
- v5.5-rc1 rebase
- Used Python 3 for scripts/jobserver-exec (Jeremy Cline)
- Drop references to SCSI PCI IDs we remove (Jeremy Cline)
- Disable documentation build, it is broken. (Jeremy Cline)
- Temporarily switch TUNE_DEFAULT to y (Jeremy Cline)
- Run config test for merge requests and internal (Jeremy Cline)
- Turn off CONFIG_AX25 (Laura Abbott)
- Add missing licensedir line (Laura Abbott)

* Tue Nov 26 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-1.elrdy]
- v5.4 rebase
- redhat/scripts: Remove redhat/scripts/rh_get_maintainer.pl (Prarit Bhargava)
- configs: Take CONFIG_DEFAULT_MMAP_MIN_ADDR from Fedra (Laura Abbott)
- configs: Turn off ISDN (Laura Abbott)
- kernel-packaging: Remove kernel files from kernel-modules-extra package (Prarit Bhargava)
- Add a script to generate configuration patches (Laura Abbott)
- Introduce rh-configs-commit (Laura Abbott)

* Fri Nov 22 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-0.rc8.1.elrdy]
- v5.4-rc8 rebase
- kconfig: Add option to get the full help text with listnewconfig (Laura Abbott)
- configs: Enable CONFIG_DEBUG_WX (Laura Abbott)
- configs: Disable wireless USB (Laura Abbott)
- Clean up some temporary config files (Laura Abbott)
- configs: New config in drivers/gpu for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/powerpc for v5.4-rc1 (Jeremy Cline)
- configs: New config in crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/usb for v5.4-rc1 (Jeremy Cline)
- AUTOMATIC: New configs (Jeremy Cline)

* Wed Nov 13 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-0.rc7.1.elrdy]
- v5.4-rc7 rebase
- Temporarily add VBOXSF_FS config (Jeremy Cline)
- Add support for deprecating processors (Laura Abbott)
- Add Red Hat tainting (Laura Abbott)
- Introduce CONFIG_RH_DISABLE_DEPRECATED (Laura Abbott)
- configs: New config in fs/erofs for v5.4-rc1 (Jeremy Cline)
- configs: New config in mm for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/md for v5.4-rc1 (Jeremy Cline)
- configs: New config in init for v5.4-rc1 (Jeremy Cline)

* Wed Nov 06 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-0.rc6.2.elrdy]
- v5.4-rc6 rebase
- iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- rh_taint: correct loaddable module support dependencies (Philipp Rudo) [1652266]
- rh_kabi: introduce RH_KABI_EXCLUDE (Jakub Racek) [1652256]
- mark intel knights landing and knights mill unsupported (David Arcari) [1610493]
- mark whiskey-lake processor supported (David Arcari) [1609604]
- ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1670017]
- IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- scsi: smartpqi: add inspur advantech ids (Don Brace) [1503736]
- ice: mark driver as tech-preview (Jonathan Toppins) [1495347]
- be2iscsi: remove BE3 family support (Maurizio Lombardi) [1598366]
- update rh_check_supported processor list (David Arcari) [1595918]
- kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- add pci_hw_vendor_status() (Maurizio Lombardi) [1590829]
- ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1563590]
- Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1563590]
- bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- tags.sh: Ignore redhat/rpm (Jeremy Cline)
- put RHEL info into generated headers (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1663728]
- kdump: add support for crashkernel=auto (Jeremy Cline)
- kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- add rh_check_supported (David Arcari) [1565717]
- qla2xxx: Remove PCI IDs of deprecated adapter (Jeremy Cline)
- be2iscsi: remove unsupported device IDs (Chris Leech) [1574502]
- Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy) [1572321]
- hpsa: modify hpsa driver version (Jeremy Cline)
- hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek) [1471185]
- rh_taint: add support for marking driver as unsupported (Jonathan Toppins) [1565704]
- rh_taint: add support (David Arcari) [1565704]
- qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis) [1518874]
- aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta) [1495307]
- megaraid_sas: remove deprecated pci-ids (Tomas Henzl) [1509329]
- mpt*: remove certain deprecated pci-ids (Jeremy Cline)
- modules: add rhelversion MODULE_INFO tag (Laura Abbott)
- ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- configs: New config in fs/fuse for v5.4-rc1 (Jeremy Cline)
- merge.pl: Avoid comments but do not skip them (Don Zickus)
- configs: New config in drivers/net/ethernet/pensando for v5.4-rc1 (Jeremy Cline)
- Update a comment about what released kernel means (Laura Abbott)
- Provide both Fedora and RHEL files in the SRPM (Laura Abbott)
- kernel.spec.template: Trim EXTRAVERSION in the Makefile (Laura Abbott)
- kernel.spec.template: Add macros for building with nopatches (Laura Abbott)
- kernel.spec.template: Add some macros for Fedora differences (Laura Abbott)
- kernel.spec.template: Consolodate the options (Laura Abbott)
- configs: Add pending direcory to Fedora (Laura Abbott)
- kernel.spec.template: Don't run hardlink if rpm-ostree is in use (Laura Abbott)
- configs: New config in net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/phy for v5.4-rc1 (Jeremy Cline)
- Updated changelog ("CKI@GitLab")

* Mon Oct 28 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-0.rc5.1.elrdy]
- v5.4-rc5 rebase
- arm: aarch64: Drop the EXPERT setting from ARM64_FORCE_52BIT (Jeremy Cline)
- configs: turn on ARM64_FORCE_52BIT for debug builds (Jeremy Cline)
- kernel.spec.template: Tweak the python3 mangling (Laura Abbott)
- kernel.spec.template: Add --with verbose option (Laura Abbott)
- kernel.spec.template: Switch to using install instead of __install (Laura Abbott)
- kernel.spec.template: Make the kernel.org URL https (Laura Abbott)
- kernel.spec.template: Update message about secure boot signing (Laura Abbott)
- kernel.spec.template: Move some with flags definitions up (Laura Abbott)
- kernel.spec.template: Update some BuildRequires (Laura Abbott)
- kernel.spec.template: Get rid of clean (Laura Abbott)
- configs: New config in drivers/char for v5.4-rc1 (Jeremy Cline)
- configs: New config in net/sched for v5.4-rc1 (Jeremy Cline)
- configs: New config in lib for v5.4-rc1 (Jeremy Cline)
- configs: New config in fs/verity for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/aarch64 for v5.4-rc4 (Jeremy Cline)
- configs: New config in arch/arm64 for v5.4-rc1 (Jeremy Cline)
- Flip off CONFIG_ARM64_VA_BITS_52 so the bundle that turns it on applies (Jeremy Cline)
- configs: Increase x86_64 NR_UARTS to 64 (Prarit Bhargava) [http://bugzilla.redhat.com/1730649]
- Update changelog (Laura Abbott)
- New configuration options for v5.4-rc4 (Jeremy Cline)
- Correctly name tarball for single tarball builds (Laura Abbott)
- configs: New config in drivers/pci for v5.4-rc1 (Jeremy Cline)
- Allow overriding the dist tag on the command line (Laura Abbott)
- Allow scratch branch target to be overridden (Laura Abbott)
- Remove long dead BUILD_DEFAULT_TARGET (Laura Abbott)

* Thu Oct 17 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-0.rc3.1.elrdy]
- v5.4-rc3 rebase
- Amend the changelog when rebasing (Laura Abbott)
- configs: New config in drivers/platform for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/pinctrl for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/wireless for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/ethernet/mellanox for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/net/can for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hid for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/dma-buf for v5.4-rc1 (Jeremy Cline)
- configs: New config in block for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/cpuidle for v5.4-rc1 (Jeremy Cline)
- redhat: configs: Split CONFIG_CRYPTO_SHA512 (Laura Abbott)
- redhat: Set Fedora options (Laura Abbott)

* Wed Oct 09 2019 Jeremy Cline <jcline@redhat.com> [5.4.0-0.rc2.1.elrdy]
- Skip ksamples for bpf, they are broken (Jeremy Cline)
- Add a SysRq option to lift kernel lockdown (Kyle McMartin)
- efi: Lock down the kernel if booted in secure boot mode (David Howells)
- efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (David Howells)
- security: lockdown: expose a hook to lock the kernel down (Jeremy Cline)
- Make get_cert_list() use efi_status_to_str() to print error messages. (Peter Jones)
- Add efi_status_to_str() and rework efi_status_to_err(). (Peter Jones)
- Make get_cert_list() not complain about cert lists that aren't present. (Peter Jones)
- [iommu] iommu/arm-smmu: workaround DMA mode issues (Laura Abbott)
- [kernel] rh_taint: correct loaddable module support dependencies (Philipp Rudo) [1652266]
- [kernel] rh_kabi: introduce RH_KABI_EXCLUDE (Jakub Racek) [1652256]
- [x86] mark intel knights landing and knights mill unsupported (David Arcari) [1610493]
- [x86] mark whiskey-lake processor supported (David Arcari) [1609604]
- [char] ipmi: do not configure ipmi for HPE m400 (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1670017]
- [infiniband] IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- [scsi] scsi: smartpqi: add inspur advantech ids (Don Brace) [1503736]
- [netdrv] ice: mark driver as tech-preview (Jonathan Toppins) [1495347]
- [scsi] be2iscsi: remove BE3 family support (Maurizio Lombardi) [1598366]
- [x86] update rh_check_supported processor list (David Arcari) [1595918]
- [kernel] kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- [pci] add pci_hw_vendor_status() (Maurizio Lombardi) [1590829]
- [ata] ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1563590]
- [pci] Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1563590]
- [kernel] bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- [kernel] bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- [kernel] add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- [kernel] kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- [scripts] tags.sh: Ignore redhat/rpm (Jeremy Cline)
- [kernel] put RHEL info into generated headers (Laura Abbott) [https://bugzilla.redhat.com/show_bug.cgi?id=1663728]
- [kernel] kdump: add support for crashkernel=auto (Jeremy Cline)
- [kernel] kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- [arm64] acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- [acpi] aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- [acpi] ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- [x86] add rh_check_supported (David Arcari) [1565717]
- [scsi] qla2xxx: Remove PCI IDs of deprecated adapter (Jeremy Cline)
- [scsi] be2iscsi: remove unsupported device IDs (Chris Leech) [1574502]
- [scsi] Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy) [1572321]
- [scsi] hpsa: modify hpsa driver version (Jeremy Cline)
- [scsi] hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek) [1471185]
- [kernel] rh_taint: add support for marking driver as unsupported (Jonathan Toppins) [1565704]
- [kernel] rh_taint: add support (David Arcari) [1565704]
- [scsi] qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis) [1518874]
- [scsi] aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta) [1495307]
- [scsi] megaraid_sas: remove deprecated pci-ids (Tomas Henzl) [1509329]
- [scsi] mpt*: remove certain deprecated pci-ids (Jeremy Cline)
- [kernel] modules: add rhelversion MODULE_INFO tag (Laura Abbott)
- [acpi] ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- gitlab: Add CI job for packaging scripts (Major Hayden)
- Set CRYPTO_SHA3_*_S390 to builtin on zfcpdump (Jeremy Cline)
- configs: New config in drivers/edac for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/firmware for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/hwmon for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/iio for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/mmc for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/tty for v5.4-rc1 (Jeremy Cline)
- configs: New config in arch/s390 for v5.4-rc1 (Jeremy Cline)
- configs: New config in drivers/bus for v5.4-rc1 (Jeremy Cline)
- Add option to allow mismatched configs on the command line (Laura Abbott)
- configs: New config in drivers/crypto for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/pci for v5.4-rc1 (Jeremy Cline)
- configs: New config in sound/soc for v5.4-rc1 (Jeremy Cline)
- Speed up CI with CKI image (Major Hayden)
- configs: Fix the pending default for CONFIG_ARM64_VA_BITS_52 (Jeremy Cline)
- configs: Turn on OPTIMIZE_INLINING for everything (Jeremy Cline)
- configs: Set valid pending defaults for CRYPTO_ESSIV (Jeremy Cline)
- Add an initial CI configuration for the internal branch (Jeremy Cline)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- Disable e1000 driver in ARK (Neil Horman)
- New drop of configuration options for v5.4-rc1 (Jeremy Cline)
- configs: Adjust CONFIG_FORCE_MAX_ZONEORDER for Fedora (Laura Abbott)
- configs: Add README for some other arches (Laura Abbott)
- configs: Sync up Fedora configs (Laura Abbott)
- Pull the RHEL version defines out of the Makefile (Jeremy Cline)
- Sync up the ARK build scripts (Jeremy Cline)
- Sync up the Fedora Rawhide configs (Jeremy Cline)
- Sync up the ARK config files (Jeremy Cline)
- [initial commit] Add structure for building with git (Laura Abbott)
- [initial commit] Add Red Hat variables in the top level makefile (Laura Abbott)
- [initial commit] Red Hat gitignore and attributes (Laura Abbott)
- [initial commit] Add changelog (Laura Abbott)
- [initial commit] Add makefile (Laura Abbott)
- [initial commit] Add files for generating the kernel.spec (Laura Abbott)
- [initial commit] Add rpm directory (Laura Abbott)
- [initial commit] Add files for packaging (Laura Abbott)
- [initial commit] Add kabi files (Laura Abbott)
- [initial commit] Add scripts (Laura Abbott)
- [initial commit] Add configs (Laura Abbott)
- [initial commit] Add Makefiles (Laura Abbott)

# The following bit is important for automation so please do not remove
# END OF CHANGELOG

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
