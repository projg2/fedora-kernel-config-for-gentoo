# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

# this should go away soon
%define _legacy_common_support 1

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
%global released_kernel 1

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

# baserelease defines which build revision of this kernel version we're
# building.  We used to call this fedora_build, but the magical name
# baserelease is matched by the rpmdev-bumpspec tool, which you should use.
#
# We used to have some extra magic weirdness to bump this automatically,
# but now we don't.  Just use: rpmdev-bumpspec -c 'comment for changelog'
# When changing base_sublevel below or going from rc to a final kernel,
# reset this by hand to 1 (or to 0 and then use rpmdev-bumpspec).
# scripts/rebase.sh should be made to do that for you, actually.
#
# NOTE: baserelease must be > 0 or bad things will happen if you switch
#       to a released kernel (released version will be < rc version)
#
# For non-released -rc kernels, this will be appended after the rcX and
# gitX tags, so a 3 here would become part of release "0.rcX.gitX.3"
#
%global baserelease 200
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 10

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 10
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 5.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%global rcrev 0
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 5.%{upstream_sublevel}.0
%endif
# Nb: The above rcrev and gitrev values automagically define Patch00 and Patch01 below.

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

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
# Want to build a the vsdo directories installed
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
%define debugbuildsenabled 1

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

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%define pkg_release %{fedora_build}%{?buildid}%{?dist}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define pkg_release 0%{?rctag}%{?gittag}.%{fedora_build}%{?buildid}%{?dist}

%endif

# The kernel tarball/base version
%define kversion 5.%{base_sublevel}


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

%if %{nopatches}
%define variant -vanilla
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
%if %{debugbuildsenabled}
%define with_up 0
%endif
%define with_pae 0
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
%define all_arch_configs kernel-%{version}-ppc64le*.config
%define kcflags -O3
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define kernel_image arch/s390/boot/bzImage
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

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%if 0%{?fedora}
%define nobuildarches i386
%else
%define nobuildarches i386 i686
%endif

%ifarch %nobuildarches
%define with_up 0
%define with_debug 0
%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_selftests 0
%define with_pae 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%if 0%{?fedora}
%define cpupowerarchs %{ix86} x86_64 ppc64le %{arm} aarch64
%else
%define cpupowerarchs i686 x86_64 ppc64le aarch64
%endif

%if %{use_vdso}

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


Name: kernel%{?variant}
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
Requires: kernel-core-uname-r = %{KVERREL}%{?variant}
Requires: kernel-modules-uname-r = %{KVERREL}%{?variant}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, tar, git-core
BuildRequires: bzip2, xz, findutils, gzip, m4, perl-interpreter, perl-Carp, perl-devel, perl-generators, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc, bison, flex
BuildRequires: net-tools, hostname, bc, elfutils-devel
%if 0%{?fedora}
BuildRequires: dwarves
%endif
# Used to mangle unversioned shebangs to be Python 3
BuildRequires: python3-devel
%if %{with_headers}
BuildRequires: rsync
%endif
%if %{with_doc}
BuildRequires: xmlto, asciidoc, python3-sphinx
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
%ifnarch s390x
BuildRequires: pciutils-devel
%endif
%endif
%if %{with_bpftool}
BuildRequires: python3-docutils
BuildRequires: zlib-devel binutils-devel
%endif
%if %{with_selftests}
%if 0%{?fedora}
BuildRequires: clang llvm
%else
BuildRequires: llvm-toolset
%endif
%ifnarch %{arm}
BuildRequires: numactl-devel
%endif
BuildRequires: libcap-devel libcap-ng-devel rsync
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
BuildConflicts: rpm < 4.13.0.1-19
%if 0%{?fedora}
BuildConflicts: dwarves < 1.13
%endif
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
%endif

# These below are required to build man pages
%if %{with_perf}
BuildRequires: xmlto
%endif
%if %{with_perf} || %{with_tools}
BuildRequires: asciidoc
%endif

Source0: https://www.kernel.org/pub/linux/kernel/v5.x/linux-%{kversion}.tar.xz

# Name of the packaged file containing signing key
%ifarch ppc64le
%define signing_key_filename kernel-signing-ppc.cer
%endif
%ifarch s390x
%define signing_key_filename kernel-signing-s390.cer
%endif

Source10: x509.genkey.rhel
Source11: x509.genkey.fedora
%if %{?released_kernel}

Source12: redhatsecurebootca5.cer
Source13: redhatsecurebootca1.cer
Source14: redhatsecureboot501.cer
Source15: redhatsecureboot301.cer
Source16: secureboot_s390.cer
Source17: secureboot_ppc.cer

%define secureboot_ca_1 %{SOURCE12}
%define secureboot_ca_0 %{SOURCE13}
%ifarch x86_64 aarch64
%define secureboot_key_1 %{SOURCE14}
%define pesign_name_1 redhatsecureboot501
%define secureboot_key_0 %{SOURCE15}
%define pesign_name_0 redhatsecureboot301
%endif
%ifarch s390x
%define secureboot_key_0 %{SOURCE16}
%define pesign_name_0 redhatsecureboot302
%endif
%ifarch ppc64le
%define secureboot_key_0 %{SOURCE17}
%define pesign_name_0 redhatsecureboot303
%endif

# released_kernel
%else

Source12: redhatsecurebootca4.cer
Source13: redhatsecurebootca2.cer
Source14: redhatsecureboot401.cer
Source15: redhatsecureboot003.cer

%define secureboot_ca_1 %{SOURCE12}
%define secureboot_ca_0 %{SOURCE13}
%define secureboot_key_1 %{SOURCE14}
%define pesign_name_1 redhatsecureboot401
%define secureboot_key_0 %{SOURCE15}
%define pesign_name_0 redhatsecureboot003

# released_kernel
%endif

Source22: mod-extra.list.rhel
Source23: mod-extra.list.fedora
Source24: mod-extra.sh
Source18: mod-sign.sh
Source19: mod-extra-blacklist.sh
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
Source55: merge.pl

Source200: check-kabi

Source201: Module.kabi_aarch64
Source202: Module.kabi_ppc64le
Source203: Module.kabi_s390x
Source204: Module.kabi_x86_64

Source210: Module.kabi_dup_aarch64
Source211: Module.kabi_dup_ppc64le
Source212: Module.kabi_dup_s390x
Source213: Module.kabi_dup_x86_64

# Source300: kernel-abi-whitelists-%{rpmversion}-%{distro_build}.tar.bz2
# Source301: kernel-kabi-dw-%{rpmversion}-%{distro_build}.tar.bz2

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

## Patches needed for building this package

# Patch1: patch-%{rpmversion}-redhat.patch

# empty final patch to facilitate testing of kernel patches
# Patch999999: linux-kernel-test.patch

# This file is intentionally left empty in the stock kernel. Its a nicety
# added for those wanting to do custom rebuilds with altered config opts.
Source1000: kernel-local

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-5.%{base_sublevel}.%{stable_base}.xz
Source5000: %{stable_patch_00}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Source5000: patch-5.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
Source5001: patch-5.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Source5000: patch-5.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif
%endif

## Patches needed for building this package

## compile fixes

%if !%{nopatches}

Patch6: 0001-ACPI-APEI-arm64-Ignore-broken-HPE-moonshot-APEI-supp.patch
Patch8: 0001-ACPI-irq-Workaround-firmware-issue-on-X-Gene-based-m.patch
Patch9: 0001-aarch64-acpi-scan-Fix-regression-related-to-X-Gene-U.patch
Patch11: 0001-kdump-round-up-the-total-memory-size-to-128M-for-cra.patch
Patch12: 0001-kdump-add-support-for-crashkernel-auto.patch
Patch15: 0001-kdump-fix-a-grammar-issue-in-a-kernel-message.patch
Patch19: 0001-Vulcan-AHCI-PCI-bar-fix-for-Broadcom-Vulcan-early-si.patch
Patch20: 0001-ahci-thunderx2-Fix-for-errata-that-affects-stop-engi.patch
Patch24: 0001-scsi-smartpqi-add-inspur-advantech-ids.patch
Patch26: 0001-ipmi-do-not-configure-ipmi-for-HPE-m400.patch
Patch28: 0001-iommu-arm-smmu-workaround-DMA-mode-issues.patch
Patch29: 0001-arm-aarch64-Drop-the-EXPERT-setting-from-ARM64_FORCE.patch
Patch31: 0001-Add-efi_status_to_str-and-rework-efi_status_to_err.patch
Patch32: 0001-Make-get_cert_list-use-efi_status_to_str-to-print-er.patch
Patch33: 0001-security-lockdown-expose-a-hook-to-lock-the-kernel-d.patch
Patch34: 0001-efi-Add-an-EFI_SECURE_BOOT-flag-to-indicate-secure-b.patch
Patch35: 0001-efi-Lock-down-the-kernel-if-booted-in-secure-boot-mo.patch
Patch36: 0001-s390-Lock-down-the-kernel-when-the-IPL-secure-flag-i.patch
Patch37: 0001-Add-option-of-13-for-FORCE_MAX_ZONEORDER.patch
Patch58: 0001-arm-make-CONFIG_HIGHPTE-optional-without-CONFIG_EXPE.patch
Patch59: 0001-ARM-tegra-usb-no-reset.patch
Patch61: 0001-Input-rmi4-remove-the-need-for-artificial-IRQ-in-cas.patch
Patch62: 0001-Drop-that-for-now.patch
Patch63: 0001-KEYS-Make-use-of-platform-keyring-for-module-signatu.patch
Patch64: 0001-mm-kmemleak-skip-late_init-if-not-skip-disable.patch
Patch65: 0001-ARM-fix-__get_user_check-in-case-uaccess_-calls-are-.patch
Patch66: 0001-dt-bindings-panel-add-binding-for-Xingbangda-XBD599-.patch
Patch67: 0001-drm-panel-add-Xingbangda-XBD599-panel.patch
Patch68: 0001-drm-sun4i-sun6i_mipi_dsi-fix-horizontal-timing-calcu.patch
Patch72: 0001-Work-around-for-gcc-bug-https-gcc.gnu.org-bugzilla-s.patch

# https://patchwork.kernel.org/patch/11796255/
Patch100: arm64-dts-rockchip-disable-USB-type-c-DisplayPort.patch

# Tegra fixes
Patch101: 0001-PCI-Add-MCFG-quirks-for-Tegra194-host-controllers.patch

# A patch to fix some undocumented things broke a bunch of Allwinner networks due to wrong assumptions
Patch102: 0001-update-phy-on-pine64-a64-devices.patch

# OMAP Pandaboard fix
Patch103: arm-pandaboard-fix-add-bluetooth.patch

# Fix for USB on some newer RPi4 / firmware combinations
Patch104: 0001-brcm-rpi4-fix-usb-numeration.patch

# Nouveau mDP detection fix
Patch107: 0001-drm-nouveau-kms-handle-mDP-connectors.patch

# END OF PATCH DEFINITIONS

%endif


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
Provides: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
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
%if "0%{?variant}"
Obsoletes: kernel-headers < %{rpmversion}-%{pkg_release}
Provides: kernel-headers = %{rpmversion}-%{pkg_release}
%endif
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
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|.*%%{_bindir}/lsgpio(\.debug)?|.*%%{_bindir}/gpio-hammer(\.debug)?|.*%%{_bindir}/gpio-event-mon(\.debug)?|.*%%{_bindir}/iio_event_monitor(\.debug)?|.*%%{_bindir}/iio_generic_buffer(\.debug)?|.*%%{_bindir}/lsiio(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

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
Provides: kernel-devel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl-interpreter\
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
Provides: kernel%{?1:-%{1}}-modules-internal-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
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
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
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
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Recommends: alsa-sof-firmware\
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
Requires: kernel-%{1}-core-uname-r = %{KVERREL}%{?variant}+%{1}\
Requires: kernel-%{1}-modules-uname-r = %{KVERREL}%{?variant}+%{1}\
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
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
%ifarch ppc64le\
Obsoletes: kernel-bootwrapper\
%endif\
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
%if !%{with_up}%{with_pae}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if "%{baserelease}" == "0"
echo "baserelease must be greater than zero"
exit 1
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
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
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

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 5.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 5.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 5.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 5.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 5.%{base_sublevel}
%endif
%endif
%endif

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-5.*' \
            | grep -x -v "$PWD"/kernel-%{kversion}%{?dist}) ||:

# Delete all old stale trees.
if [ -d kernel-%{kversion}%{?dist} ]; then
  cd kernel-%{kversion}%{?dist}
  for i in linux-*
  do
     if [ -d $i ]; then
       # Just in case we ctrl-c'd a prep already
       rm -rf deleteme.%{_target_cpu}
       # Move away the stale away, and delete in background.
       mv $i deleteme-$i
       rm -rf deleteme* &
     fi
  done
  cd ..
fi

# Generate new tree
if [ ! -d kernel-%{kversion}%{?dist}/vanilla-%{vanillaversion} ]; then

  if [ -d kernel-%{kversion}%{?dist}/vanilla-%{kversion} ]; then

    # The base vanilla version already exists.
    cd kernel-%{kversion}%{?dist}

    # Any vanilla-* directories other than the base one are stale.
    for dir in vanilla-*; do
      [ "$dir" = vanilla-%{kversion} ] || rm -rf $dir &
    done

  else

    rm -f pax_global_header
    # Look for an identical base vanilla dir that can be hardlinked.
    for sharedir in $sharedirs ; do
      if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
        break
      fi
    done
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
%setup -q -n kernel-%{kversion}%{?dist} -c -T
      cp -al $sharedir/vanilla-%{kversion} .
    else
%setup -q -n kernel-%{kversion}%{?dist} -c
      mv linux-%{kversion} vanilla-%{kversion}
    fi

  fi

%if "%{kversion}" != "%{vanillaversion}"

  for sharedir in $sharedirs ; do
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then
      break
    fi
  done
  if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then

    cp -al $sharedir/vanilla-%{vanillaversion} .

  else

    # Need to apply patches to the base vanilla version.
    cp -al vanilla-%{kversion} vanilla-%{vanillaversion}
    cd vanilla-%{vanillaversion}

cp %{SOURCE12} .

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    xzcat %{SOURCE5000} | patch -p1 -F1 -s
%if 0%{?gitrev}
    xzcat %{SOURCE5001} | patch -p1 -F1 -s
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    xzcat %{SOURCE5000} | patch -p1 -F1 -s
%endif
%endif
    git init
    git config user.email "kernel-team@fedoraproject.org"
    git config user.name "Fedora Kernel Team"
    git config gc.auto 0
    git add .
    git commit -a -q -m "baseline"

    cd ..

  fi

%endif

else

  # We already have all vanilla dirs, just change to the top-level directory.
  cd kernel-%{kversion}%{?dist}

fi

# Now build the fedora kernel tree.
cp -al vanilla-%{vanillaversion} linux-%{KVERREL}

cd linux-%{KVERREL}
if [ ! -d .git ]; then
    git init
    git config user.email "kernel-team@fedoraproject.org"
    git config user.name "Fedora Kernel Team"
    git config gc.auto 0
    git add .
    git commit -a -q -m "baseline"
fi


# released_kernel with possible stable updates
%if 0%{?stable_base}
# This is special because the kernel spec is hell and nothing is consistent
xzcat %{SOURCE5000} | patch -p1 -F1 -s
git commit -a -m "Stable update"
%endif

# Note: Even in the "nopatches" path some patches (build tweaks and compile
# fixes) will always get applied; see patch defition above for details

git am %{patches}

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
	tools/perf/tests/attr.py \
	tools/perf/scripts/python/stat-cpi.py \
	tools/perf/scripts/python/sched-migration.py \
	Documentation \
	scripts/clang-tools

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
fi
# Deal with configs stuff
mkdir configs
cd configs

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-*.config .
cp %{SOURCE1000} .
cp %{SOURCE55} .
cp %{SOURCE51} .
VERSION=%{version} ./generate_all_configs.sh %{primary_target} %{debugbuildsenabled}


# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE1000} $i.tmp > $i
  rm $i.tmp
done
%endif

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
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

# These are for host programs that get built as part of the kernel and
# are required to be packaged in kernel-devel for building external modules.
# Since they are userspace binaries, they are required to pickup the hardening
# flags defined in the macros. The --build-id=uuid is a trick to get around
# debuginfo limitations: Typically, find-debuginfo.sh will update the build
# id of all binaries to allow for parllel debuginfo installs. The kernel
# can't use this because it breaks debuginfo for the vDSO so we have to
# use a special mechanism for kernel and modules to be unique. Unfortunately,
# we still have userspace binaries which need unique debuginfo and because
# they come from the kernel package, we can't just use find-debuginfo.sh to
# rewrite only those binaries. The easiest option right now is just to have
# the build id be a uuid for the host programs.
#
# Note we need to disable these flags for cross builds because the flags
# from redhat-rpm-config assume that host == target so target arch
# flags cause issues with the host compiler.
%if !%{with_cross}
%define build_hostcflags  %{?build_cflags}
%define build_hostldflags %{?build_ldflags}
%endif

%define make make %{?cross_opts} %{?make_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}"

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$4
    DoVDSO=$3
    Flav=${Flavour:++${Flavour}}
    InstallName=${5:-vmlinuz}

    DoModules=1
    if [ "$Flavour" = "zfcpdump" ]; then
	    DoModules=0
    fi

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flav}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flav}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    %if 0%{?stable_update}
    # make sure SUBLEVEL is incremented on a stable release.  Sigh 3.x.
    perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{?stablerev}/" Makefile
    %endif

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flav}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    %{make} %{?_smp_mflags} mrproper
    cp configs/$Config .config

    %if %{signkernel}%{signmodules}
    cp $RPM_SOURCE_DIR/x509.genkey certs/.
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    KCFLAGS="%{?kcflags}"

    # add kpatch flags for base kernel
    if [ "$Flavour" == "" ]; then
        KCFLAGS="$KCFLAGS %{?kpatch_kcflags}"
    fi

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
    echo '%%defattr(-,-,-)' > ../kernel${Flavour:+-${Flavour}}-ldsoconf.list
    if [ $DoVDSO -ne 0 ]; then
        %{make} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
        if [ -s ldconfig-kernel.conf ]; then
             install -D -m 444 ldconfig-kernel.conf \
                $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
	     echo /etc/ld.so.conf.d/kernel-$KernelVer.conf >> ../kernel${Flavour:+-${Flavour}}-ldsoconf.list
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
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/internal
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
%if 0%{!?fedora:1}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
%endif
    # CONFIG_KERNEL_HEADER_TEST generates some extra files in the process of
    # testing so just delete
    find . -name *.h.s -delete
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
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
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        # for now, don't keep it around.
        rm $RPM_BUILD_ROOT/Module.kabi
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidupchk}
    echo "**** kABI DUP checking is enabled in kernel SPEC file. ****"
    if [ -e $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        # for now, don't keep it around.
        rm $RPM_BUILD_ROOT/Module.kabi
    else
        echo "**** NOTE: Cannot find DUP reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidw_base}
    # Don't build kabi base for debug kernels
    if [ "$Flavour" != "kdump" -a "$Flavour" != "debug" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf

        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/whitelists
        tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/whitelists

        echo "**** GENERATING DWARF-based kABI baseline dataset ****"
        chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
        $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
            "$RPM_BUILD_ROOT/kabi-dwarf/whitelists/kabi-current/kabi_whitelist_%{_target_cpu}" \
            "$(pwd)" \
            "$RPM_BUILD_ROOT/kabidw-base/%{_target_cpu}${Flavour:+.${Flavour}}" || :

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

%if %{with_kabidwchk}
    if [ "$Flavour" != "kdump" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf
        if [ -d "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}" ]; then
            mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/whitelists
            tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/whitelists

            echo "**** GENERATING DWARF-based kABI dataset ****"
            chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
                "$RPM_BUILD_ROOT/kabi-dwarf/whitelists/kabi-current/kabi_whitelist_%{_target_cpu}" \
                "$(pwd)" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}.tmp" || :

            echo "**** kABI DWARF-based comparison report ****"
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh compare \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}.tmp" || :
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

    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
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
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
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
    if [ -d arch/%{asmarch}/mach-${Flavour}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Flavour}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
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
    cp -a --parents tools/include/tools/le_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/setup-x86_64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/entry64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/ctype.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
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

    # Call the modules-extra script to move things around
    %{SOURCE24} $RPM_BUILD_ROOT/lib/modules/$KernelVer $RPM_SOURCE_DIR/mod-extra.list
    # Blacklist net autoloadable modules in modules-extra
    %{SOURCE19} $RPM_BUILD_ROOT lib/modules/$KernelVer
    # Call the modules-extra script for internal modules
    %{SOURCE24} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE54} internal

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # don't include anything going into k-m-e and k-m-i in the file lists
    rm -rf lib/modules/$KernelVer/{extra,internal}

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
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../kernel${Flavour:+-${Flavour}}-modules.list
    sed -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../kernel${Flavour:+-${Flavour}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../kernel${Flavour:+-${Flavour}}-core.list

    # Cleanup
    rm -f $RPM_BUILD_ROOT/k-d.list
    rm -f $RPM_BUILD_ROOT/modules.list
    rm -f $RPM_BUILD_ROOT/module-dirs.list

%if %{signmodules}
    if [ $DoModules -eq 1 ]; then
	# Save the signing keys so we can sign the modules in __modsign_install_post
	cp certs/signing_key.pem certs/signing_key.pem.sign${Flav}
	cp certs/signing_key.x509 certs/signing_key.x509.sign${Flav}
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
	    install -m 0644 certs/signing_key.x509.sign${Flav} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer
	    openssl x509 -in certs/signing_key.pem.sign${Flav} -outform der -out $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	    chmod 0644 $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/%{signing_key_filename}
	fi
    fi
    %endif

%if %{with_ipaclones}
    MAXPROCS=$(echo %{?_smp_mflags} | sed -n 's/-j\s*\([0-9]\+\)/\1/p')
    if [ -z "$MAXPROCS" ]; then
        MAXPROCS=1
    fi
    if [ "$Flavour" == "" ]; then
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

%global perf_make \
  make -s EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?cross_opts} -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 prefix=%{_prefix} PYTHON=%{__python3}
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
%{make}
popd
pushd tools/gpio/
%{make}
popd
%endif

%global bpftool_make \
  make EXTRA_CFLAGS="${RPM_OPT_FLAGS}" EXTRA_LDFLAGS="%{__global_ldflags}" DESTDIR=$RPM_BUILD_ROOT V=1
%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make}
popd
%endif

%if %{with_selftests}
%{make} -s ARCH=$Arch V=1 samples/bpf/
pushd tools/testing/selftests
# We need to install here because we need to call make with ARCH set which
# doesn't seem possible to do in the install section.
%{make} -s ARCH=$Arch V=1 TARGETS="bpf livepatch net" INSTALL_PATH=%{buildroot}%{_libexecdir}/kselftests install
popd
%endif

%if %{with_doc}
# Make the HTML pages.
make PYTHON=/usr/bin/python3 htmldocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Don't sign modules for the zfcpdump flavour as it is monolithic.

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
# Delete the debuginfo for for kernel-devel files
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
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

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
	make ARCH=${arch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr/tmp-headers/arch-${arch} headers_install
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
make DESTDIR=%{buildroot} install
popd
pushd tools/gpio
make DESTDIR=%{buildroot} install
popd
pushd tools/kvm/kvm_stat
make INSTALL_ROOT=%{buildroot} install-tools
make INSTALL_ROOT=%{buildroot} install-man
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
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink -a ! -e /run/ostree-booted ] \
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
%if 0%{!?fedora:1}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%endif\
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
%{_mandir}/man8/bpftool-map.8.gz
%{_mandir}/man8/bpftool-prog.8.gz
%{_mandir}/man8/bpftool-perf.8.gz
%{_mandir}/man8/bpftool.8.gz
%{_mandir}/man7/bpf-helpers.7.gz
%{_mandir}/man8/bpftool-net.8.gz
%{_mandir}/man8/bpftool-feature.8.gz
%{_mandir}/man8/bpftool-btf.8.gz

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
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage> <without_modules>
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
%if 0%{!?fedora:1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/weak-updates\
%endif\
%{_datadir}/doc/kernel-keys/%{KVERREL}%{?3:+%{3}}/kernel-signing-ca*.cer\
%ifarch s390x ppc64le\
%if 0%{!?4:1}\
%{_datadir}/doc/kernel-keys/%{KVERREL}%{?3:+%{3}}/%{signing_key_filename} \
%endif\
%endif\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f kernel-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%{expand:%%files %{?3:%{3}-}devel}\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files %{?3:%{3}-}modules-extra}\
%config(noreplace) /etc/modprobe.d/*-blacklist.conf\
/lib/modules/%{KVERREL}%{?3:+%{3}}/extra\
%{expand:%%files %{?3:%{3}-}modules-internal}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/internal\
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
%kernel_variant_files %{_use_vdso} %{with_zfcpdump} zfcpdump 1

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
* Sun Jan 24 11:28:41 CST 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.10.10-200
- Linux v5.10.10
- Fixes CVE-2021-3178 (rhbz 1918179 1918181)

* Wed Jan 20 2021 Peter Robinson <pbrobinson@fedoraproject.org> - 5.10.9-201
- Fix for ARMv7 builder pause issue

* Tue Jan 19 15:00:17 CST 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.10.9-200
- Linux v5.10.9

* Sun Jan 17 13:09:31 CST 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.10.8-200
- Linux v5.10.8

* Tue Jan 12 13:41:35 CST 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.10.7-200
- Linux v5.10.7

* Mon Jan 11 06:51:13 CST 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.10.6-200
- Linux v5.10.6 rebase
- Fix bluetooth controller initialization (rhbz 1898495)
- Fix CVE-2020-36158 (rhbz 1913348 1913349)

* Mon Dec 21 07:41:08 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.16-200
- Linux v5.9.16

* Wed Dec 16 08:06:21 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.15-200
- Linux v5.9.15

* Fri Dec 11 07:14:10 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.14-200
- Linux v5.9.14
- Fixes CVE-2020-29660 (rhbz 1906522 1906523)
- Fixes CVE-2020-29661 (rhbz 1906525 1906526)

* Tue Dec  8 08:04:29 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.13-200
- Linux v5.9.13

* Wed Dec  2 07:55:34 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.12-200
- Linux v5.9.12

* Tue Nov 24 11:22:38 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.11-200
- Linux v5.9.11

* Mon Nov 23 09:58:15 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.10-200
- Linux v5.9.10
- Fix CVE-2020-28941 (rhbz 1899985 1899986)
- Fix CVE-2020-4788 (rhbz 1888433 1900437)

* Thu Nov 19 07:09:26 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.9-200
- Linux v5.9.9
- Enable NANDSIM (rhbz 1898638)

* Thu Nov 12 2020 Justin M. Forbes <jforbes@fedoraproject.org>
- Fix bluetooth device disconnect issues. (rhbz 1897038)

* Tue Nov 10 15:34:25 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.9.8-200
- Linux v5.9.8
- Fixes CVE-2020-8694 (rhbz 1828580 1896525)

* Tue Nov 10 2020 <jforbes@fedoraproject.org> - 5.9.7-200
- Linux v5.9.7 rebase
- Fixes CVE-2020-25668 (rhbz 1893287 1893288)
- Fixes CVE-2020-27673 (rhbz 1891110 1891112)
- Fixes CVE-2020-25704 (rhbz 1895951 1895963)

* Mon Nov  2 10:50:39 CST 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.18-300
- Linux v5.8.18

* Thu Oct 29 07:55:15 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.17-300
- Linux v5.8.17
- Fix CVE-2020-27675 (rhbz 1891114 1891115)

* Wed Oct 28 2020 Peter Robinson <pbrobinson@fedoraproject.org>
- Fixes for AllWinner wired network issues due to Realtek PHY driver change (rhbz 1889090)

* Mon Oct 19 07:15:01 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.16-300
- Linux v5.8.16

* Fri Oct 16 2020 Hans de Goede <hdegoede@redhat.com>
- Fix Micrsoft Surface Go series boot regression (rhbz 1886249)

* Thu Oct 15 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.15-301
- Fix BleedingTooth CVE-2020-12351 CVE-2020-12352 (rhbz 1886521 1888439 1886529 1888440)

* Wed Oct 14 11:29:34 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.15-300
- Linux v5.8.15
- Fix CVE-2020-16119 (rhbz 1886374 1888083)

* Wed Oct  7 07:21:34 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.14-300
- Linux v5.8.14

* Wed Oct  7 2020 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix aarch64 boot crash on BTI capable systems
- Fix boot crash on aarch64 Ampere eMAG systems (rhbz #1874117)

* Thu Oct  1 12:09:16 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.13-300
- Linux v5.8.13

* Mon Sep 28 06:48:48 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.12-300
- Linux v5.8.12

* Wed Sep 23 06:58:55 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.11-300
- Linux v5.8.11
- Fix (rhbz 1821946)

* Thu Sep 17 08:47:40 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.10-300
- Linux v5.8.10
- Fix (rhbz 1873720 1876997)

* Mon Sep 14 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.9-301
- Fix error code in bdev_del_part (rhbz 1878858)

* Mon Sep 14 08:51:55 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.9-300
- Linux v5.8.9

* Sat Sep 12 2020 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix for SDIO speed issue
- Fix for certain mSD cards on Raspberry Pi 4
- Fix for older brcm sdio WiFi modules

* Thu Sep 10 2020 Justin M. Forbes <jforbes@fedoraproject.org>
- Fix CVE-2020-25211 (rhbz 1877571 1877572)

* Wed Sep  9 13:39:47 CDT 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.8-300
- Linux v5.8.8

* Mon Sep 07 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.7-300
- Linux v5.8.7
- Fix CVE-2020-14386 (rhbz 1875699 1876349)

* Thu Sep 03 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.6-301
- Linux v5.8.6
- Fix CVE-2020-14385 (rhbz 1874800 1874811)
- Move CONFIG_USB_XHCI_PCI_RENESAS to inline (rhbz 1874300)

* Thu Aug 27 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.5-300
- Linux v5.8.5

* Wed Aug 26 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.4-300
- Linux v5.8.4

* Fri Aug 21 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.3-300
- Linux v5.8.3

* Wed Aug 19 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.2-300.rpi1
- Linux v5.8.2

* Wed Aug 12 2020 Justin M. Forbes <jforbes@fedoraproject.org> - 5.8.0-1.1
- Linux v5.8.1

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
