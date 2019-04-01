# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 0

# Sign modules on x86.  Make sure the config files match this setting if more
# architectures are added.
%ifarch %{ix86} x86_64
%global signkernel 1
%global signmodules 1
%global zipmodules 1
%else
%global signkernel 0
%global signmodules 1
%global zipmodules 1
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
%endif

# define buildid .local

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
%global baserelease 1
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 0

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
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
%global rcrev 3
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
# kernel PAE (only valid for i686 (PAE) and ARM (lpae))
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
%define with_cross_headers   %{?_without_cross_headers:   0} %{?!_without_cross_headers:   1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
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

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# Kernel headers are being split out into a separate package
%if 0%{?fedora}
%define with_headers 0
%define with_cross_headers 0
%endif

%if %{with_verbose}
%define make_opts V=1
%else
%define make_opts -s
%endif

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

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

%define make_target bzImage
%define image_install_path boot

%define KVERREL %{version}-%{release}.%{_target_cpu}
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

# kernel PAE is only built on ARMv7 in rawhide.
# Fedora 27 and earlier still support PAE, so change this on rebases.
# %ifnarch i686 armv7hl
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
%define with_pae 0
%endif
%define with_pae 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
%define use_vdso 1
%endif

# Overrides for generic default options

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_cross_headers 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# sparse blows up on ppc
%ifnarch %{power64}
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define pae PAE
%define all_arch_configs kernel-%{version}-i?86*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch %{power64}
%define asmarch powerpc
%define hdrarch powerpc
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%ifarch ppc64le
%define all_arch_configs kernel-%{version}-ppc64le*.config
%endif
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
%define pae lpae
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
%define listnewconfig_fail 0
%define configmismatch_fail 0
%else
%define listnewconfig_fail 1
%define configmismatch_fail 1
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386

%ifarch %nobuildarches
%define with_up 0
%define with_pae 0
%define with_debuginfo 0
%define with_debug 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs %{ix86} x86_64 %{power64} %{arm} aarch64

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
ExclusiveArch: %{all_x86} x86_64 s390x %{arm} aarch64 ppc64le
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
BuildRequires: net-tools, hostname, bc, elfutils-devel, gcc-plugin-devel
%if 0%{?fedora}
# Used to mangle unversioned shebangs to be Python 3
BuildRequires: /usr/bin/pathfix.py
%endif
%if %{with_sparse}
BuildRequires: sparse
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
BuildConflicts: rpm < 4.13.0.1-19
# Most of these should be enabled after more investigation
%undefine _include_minidebuginfo
%undefine _find_debuginfo_dwz_opts
%undefine _unique_build_ids
%undefine _unique_debug_names
%undefine _unique_debug_srcs
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%undefine _include_gdb_index
%global _find_debuginfo_opts -r
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%endif

%if %{signkernel}%{signmodules}
BuildRequires: openssl openssl-devel
%if %{signkernel}
BuildRequires: pesign >= 0.10-4
%endif
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%endif

Source0: https://www.kernel.org/pub/linux/kernel/v5.x/linux-%{kversion}.tar.xz

Source11: x509.genkey
Source12: remove-binary-diff.pl
Source15: merge.pl
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-sign.sh
Source90: filter-x86_64.sh
Source91: filter-armv7hl.sh
Source92: filter-i686.sh
Source93: filter-aarch64.sh
Source94: filter-ppc64le.sh
Source95: filter-s390x.sh
Source99: filter-modules.sh
%define modsign_cmd %{SOURCE18}

Source20: kernel-aarch64.config
Source21: kernel-aarch64-debug.config
Source22: kernel-armv7hl.config
Source23: kernel-armv7hl-debug.config
Source24: kernel-armv7hl-lpae.config
Source25: kernel-armv7hl-lpae-debug.config
Source26: kernel-i686.config
Source27: kernel-i686-debug.config
Source30: kernel-ppc64le.config
Source31: kernel-ppc64le-debug.config
Source32: kernel-s390x.config
Source33: kernel-s390x-debug.config
Source34: kernel-x86_64.config
Source35: kernel-x86_64-debug.config

Source40: generate_all_configs.sh
Source41: generate_debug_configs.sh

Source42: process_configs.sh
Source43: generate_bls_conf.sh

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

# Git trees.

# Standalone patches
# 100 - Generic long running patches

Patch110: lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

Patch111: input-kill-stupid-messages.patch

Patch112: die-floppy-die.patch

Patch113: no-pcspkr-modalias.patch

Patch115: Kbuild-Add-an-option-to-enable-GCC-VTA.patch

Patch116: crash-driver.patch

Patch117: lis3-improve-handling-of-null-rate.patch

Patch118: scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

Patch119: namespaces-no-expert.patch

Patch120: ath9k-rx-dma-stop-check.patch

Patch122: Input-synaptics-pin-3-touches-when-the-firmware-repo.patch

# This no longer applies, let's see if it needs to be updated
# Patch123: firmware-Drop-WARN-from-usermodehelper_read_trylock-.patch

# 200 - x86 / secureboot

Patch201: efi-lockdown.patch

Patch202: KEYS-Allow-unrestricted-boot-time-addition-of-keys-t.patch

# bz 1497559 - Make kernel MODSIGN code not error on missing variables
Patch207: 0001-Make-get_cert_list-not-complain-about-cert-lists-tha.patch
Patch208: 0002-Add-efi_status_to_str-and-rework-efi_status_to_err.patch
Patch209: 0003-Make-get_cert_list-use-efi_status_to_str-to-print-er.patch

Patch210: disable-i8042-check-on-apple-mac.patch

Patch211: drm-i915-hush-check-crtc-state.patch

Patch212: efi-secureboot.patch

# 300 - ARM patches
Patch300: arm64-Add-option-of-13-for-FORCE_MAX_ZONEORDER.patch

# http://www.spinics.net/lists/linux-tegra/msg26029.html
Patch301: usb-phy-tegra-Add-38.4MHz-clock-table-entry.patch
# http://patchwork.ozlabs.org/patch/587554/
Patch302: ARM-tegra-usb-no-reset.patch

# https://patchwork.kernel.org/patch/10351797/
Patch303: ACPI-scan-Fix-regression-related-to-X-Gene-UARTs.patch
# rhbz 1574718
Patch304: ACPI-irq-Workaround-firmware-issue-on-X-Gene-based-m400.patch

# https://patchwork.kernel.org/patch/9820417/
Patch305: qcom-msm89xx-fixes.patch

# https://patchwork.kernel.org/project/linux-mmc/list/?submitter=71861
Patch306: arm-sdhci-esdhc-imx-fixes.patch

Patch312: arm64-rock960-enable-tsadc.patch

Patch339: bcm2835-cpufreq-add-CPU-frequency-control-driver.patch

# Tegra bits
Patch340: arm64-tegra-jetson-tx1-fixes.patch

# https://patchwork.kernel.org/patch/10858639/
Patch341: arm64-tegra-Add-NVIDIA-Jetson-Nano-Developer-Kit-support.patch

# 400 - IBM (ppc/s390x) patches

# 500 - Temp fixes/CVEs etc

# rhbz 1431375
Patch501: input-rmi4-remove-the-need-for-artifical-IRQ.patch

# gcc9 fixes
Patch506: 0001-s390-jump_label-Correct-asm-contraint.patch
Patch507: 0001-Drop-that-for-now.patch

# rhbz 1688283
Patch512: v3-tpm-fix-an-invalid-condition-in-tpm_common_poll.patch

# https://patchwork.kernel.org/patch/10872997/
Patch513: Correct-zone-boundary-handling-when-resetting-pageblock-skip-hints.patch

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

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
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
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '/.*/%%{KVERREL}%{?1:[+]%{1}}/.*|/.*%%{KVERREL}%{?1:\+%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
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
%ifarch %{power64}\
Obsoletes: kernel-bootwrapper\
%endif\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%{nil}

# Now, each variant package.

%if %{with_pae}
%ifnarch armv7hl
%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package %{pae}
%description %{pae}-core
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.
%else
%define variant_summary The Linux kernel compiled for Cortex-A15
%kernel_variant_package %{pae}
%description %{pae}-core
This package includes a version of the Linux kernel with support for
Cortex-A15 devices with LPAE and HW virtualisation support
%endif


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package %{pae}debug
Obsoletes: kernel-PAE-debug
%description %{pae}debug-core
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.
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
    xzcat %{SOURCE5000} | ./remove-binary-diff.pl | patch -p1 -F1 -s
%if 0%{?gitrev}
    xzcat %{SOURCE5001} | ./remove-binary-diff.pl | patch -p1 -F1 -s
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    xzcat %{SOURCE5000} | ./remove-binary-diff.pl | patch -p1 -F1 -s
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
chmod +x tools/objtool/sync-check.sh
mv COPYING COPYING-%{version}

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# Deal with configs stuff
mkdir configs
cd configs

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-*.config .
cp %{SOURCE1000} .
cp %{SOURCE15} .
cp %{SOURCE40} .
cp %{SOURCE41} .
cp %{SOURCE43} .

%if !%{debugbuildsenabled}
# The normal build is a really debug build and the user has explicitly requested
# a release kernel. Change the config files into non-debug versions.
%if !%{with_release}
VERSION=%{version} ./generate_debug_configs.sh
%else
VERSION=%{version} ./generate_all_configs.sh
%endif

%else
VERSION=%{version} ./generate_all_configs.sh
%endif

# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE1000} $i.tmp > $i
  rm $i.tmp
done
%endif

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

%define make make %{?cross_opts}

CheckConfigs() {
     ./check_configs.awk $1 $2 > .mismatches
     if [ -s .mismatches ]
     then
	echo "Error: Mismatches found in configuration files"
	cat .mismatches
	exit 1
     fi
}

cp %{SOURCE42} .
OPTS=""
%if %{listnewconfig_fail}
	OPTS="$OPTS -n"
%endif
%if %{configmismatch_fail}
	OPTS="$OPTS -c"
%endif
./process_configs.sh $OPTS kernel %{rpmversion}

# end of kernel config
%endif

cd ..
# End of Configs stuff

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -delete >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -delete >/dev/null

%if 0%{?fedora}
# Mangle /usr/bin/python shebangs to /usr/bin/python3
# Mangle all Python shebangs to be Python 3 explicitly
# -p preserves timestamps
# -n prevents creating ~backup files
# -i specifies the interpreter for the shebang
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/diffconfig
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/bloat-o-meter
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/show_delta
%endif

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
%define build_hostldflags %{?build_ldflags} -Wl,--build-id=uuid
%endif

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$4
    DoVDSO=$3
    Flav=${Flavour:++${Flavour}}
    InstallName=${5:-vmlinuz}

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
    # Trim the release if this is a CI build, since KERNELVERSION is limited to 64 characters
    ShortRel=$(perl -e "print \"%{release}\" =~ s/\.pr\.[0-9A-Fa-f]{32}//r")
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -${ShortRel}.%{_target_cpu}${Flav}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make %{?make_opts} mrproper
    cp configs/$Config .config

    %if %{signkernel}%{signmodules}
    cp %{SOURCE11} certs/.
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make %{?make_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}" ARCH=$Arch olddefconfig

    # This ensures build-ids are unique to allow parallel debuginfo
    perl -p -i -e "s/^CONFIG_BUILD_SALT.*/CONFIG_BUILD_SALT=\"%{KVERREL}\"/" .config
    %{make} %{?make_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}" ARCH=$Arch %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    %{make} %{?make_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}" ARCH=$Arch %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif

%ifarch %{arm} aarch64
    %{make} %{?make_opts} ARCH=$Arch dtbs dtbs_install INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
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
    # Sign the image if we're using EFI
    %pesign -s -i $KernelImage -o vmlinuz.signed
    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $KernelImage
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

    # Override $(mod-fw) because we don't want it to install any firmware
    # we'll get it from the linux-firmware package and we don't want conflicts
    %{make} %{?make_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=

    # add an a noop %%defattr statement 'cause rpm doesn't like empty file list files
    echo '%%defattr(-,-,-)' > ../kernel${Flavour:+-${Flavour}}-ldsoconf.list
    if [ $DoVDSO -ne 0 ]; then
        %{make} %{?make_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
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
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi
    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
      # these are a few files associated with objtool
      cp -a --parents tools/build/Build.include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      cp -a --parents tools/build/Build $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      cp -a --parents tools/build/fixdep.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      cp -a --parents tools/scripts/utilities.mak $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      # also more than necessary but it's not that many more files
      cp -a --parents tools/objtool/* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      cp -a --parents tools/lib/str_error_r.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      cp -a --parents tools/lib/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
      cp -a --parents tools/lib/subcmd/* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
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
%ifarch %{power64}
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
%ifarch %{ix86} x86_64
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
    # Yes this is more includes than we probably need. Feel free to sort out
    # dependencies if you so choose.
    cp -a --parents tools/include/* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
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
    %{SOURCE17} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE16}

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # don't include anything going into k-m-e in the file lists
    rm -rf lib/modules/$KernelVer/extra

    # Find all the module files and filter them out into the core and modules
    # lists.  This actually removes anything going into -modules from the dir.
    find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
    cp $RPM_SOURCE_DIR/filter-*.sh .
    %{SOURCE99} modules.list %{_target_cpu}
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
    # Save the signing keys so we can sign the modules in __modsign_install_post
    cp certs/signing_key.pem certs/signing_key.pem.sign${Flav}
    cp certs/signing_key.x509 certs/signing_key.x509.sign${Flav}
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
    %{SOURCE43} "$KernelVer" "$RPM_BUILD_ROOT" "%{?variant}"
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

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image %{use_vdso} %{pae}debug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image %{use_vdso} %{pae}
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image %{_use_vdso}
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

%define __modsign_install_post \
  if [ "%{signmodules}" -eq "1" ]; then \
    if [ "%{with_pae}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+%{pae} certs/signing_key.x509.sign+%{pae} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}/ \
    fi \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+debug certs/signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_pae_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+%{pae}debug certs/signing_key.x509.sign+%{pae}debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign certs/signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
    fi \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs xz; \
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

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

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
mkdir -p $RPM_BUILD_ROOT/usr/tmp-headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr/tmp-headers headers_install_all

find $RPM_BUILD_ROOT/usr/tmp-headers/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

# Copy all the architectures we care about to their respective asm directories
for arch in arm arm64 powerpc s390 x86 ; do
mkdir -p $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include
mv $RPM_BUILD_ROOT/usr/tmp-headers/include/arch-${arch}/asm $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/
cp -a $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-generic $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/.
done

# Remove the rest of the architectures
rm -rf $RPM_BUILD_ROOT/usr/tmp-headers/include/arch*
rm -rf $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-*

# Copy the rest of the headers over
for arch in arm arm64 powerpc s390 x86 ; do
cp -a $RPM_BUILD_ROOT/usr/tmp-headers/include/* $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/.
done

rm -rf $RPM_BUILD_ROOT/usr/tmp-headers
%endif

###
### clean
###

###
### scripts
###

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
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
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%if %{with_pae}
%kernel_variant_preun %{pae}
%kernel_variant_post -v %{pae} -r (kernel|kernel-smp)

%kernel_variant_post -v %{pae}debug -r (kernel|kernel-smp)
%kernel_variant_preun %{pae}debug
%endif

%kernel_variant_preun debug
%kernel_variant_post -v debug

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

# empty meta-package
%files
# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{2}\
%{expand:%%files -f kernel-%{?3:%{3}-}core.list %{?1:-f kernel-%{?3:%{3}-}ldsoconf.list} %{?3:%{3}-}core}\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING-%{version}\
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
/lib/modules/%{KVERREL}%{?3:+%{3}}/config\
%ghost /boot/config-%{KVERREL}%{?3:+%{3}}\
%ghost /boot/initramfs-%{KVERREL}%{?3:+%{3}}.img\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}/kernel\
/lib/modules/%{KVERREL}%{?3:+%{3}}/build\
/lib/modules/%{KVERREL}%{?3:+%{3}}/source\
/lib/modules/%{KVERREL}%{?3:+%{3}}/updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/bls.conf\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f kernel-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%{expand:%%files %{?3:%{3}-}devel}\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files %{?3:%{3}-}modules-extra}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/extra\
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
%kernel_variant_files %{use_vdso} %{with_pae} %{pae}
%kernel_variant_files %{use_vdso} %{with_pae_debug} %{pae}debug

# plz don't put in a version string unless you're going to tag
# and build.
#
#
%changelog
* Mon Apr 01 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc3.git0.1
- Linux v5.1-rc3

* Mon Apr 01 2019 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Fri Mar 29 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc2.git4.1
- Linux v5.1-rc2-247-g9936328b41ce
- Pick up a mm fix causing hangs (rhbz 1693525)

* Thu Mar 28 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc2.git3.1
- Linux v5.1-rc2-243-g8c7ae38d1ce1

* Wed Mar 27 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc2.git2.1
- Linux v5.1-rc2-24-g14c741de9386

* Wed Mar 27 2019 Jeremy Cline <jeremy@jcline.org>
- Build iptable_filter as module

* Tue Mar 26 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc2.git1.1
- Linux v5.1-rc2-16-g65ae689329c5

* Tue Mar 26 2019 Jeremy Cline <jcline@redhat.com>
- Reenable debugging options.

* Tue Mar 26 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial NXP i.MX8 enablement

* Mon Mar 25 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc2.git0.1
- Linux v5.1-rc2

* Mon Mar 25 2019 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Sat Mar 23 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Fixes for Tegra Jetson TX series
- Initial support for NVIDIA Jetson Nano

* Fri Mar 22 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc1.git2.1
- Linux v5.1-rc1-66-gfd1f297b794c

* Wed Mar 20 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc1.git1.1
- Linux v5.1-rc1-15-gbabf09c3837f
- Reenable debugging options.

* Wed Mar 20 2019 Hans de Goede <hdegoede@redhat.com>
- Make the mainline vboxguest drv feature set match VirtualBox 6.0.x (#1689750)

* Mon Mar 18 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc1.git0.1
- Linux v5.1-rc1

* Mon Mar 18 2019 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Sun Mar 17 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Updates for Arm

* Fri Mar 15 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git9.1
- Linux v5.0-11520-gf261c4e529da

* Thu Mar 14 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git8.1
- Linux v5.0-11139-gfa3d493f7a57

* Wed Mar 13 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git7.1
- Linux v5.0-11053-gebc551f2b8f9

* Tue Mar 12 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git6.1
- Linux v5.0-10742-gea295481b6e3

* Tue Mar 12 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Arm config updates and fixes

* Mon Mar 11 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git5.1
- Linux v5.0-10360-g12ad143e1b80

* Fri Mar 08 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git4.1
- Linux v5.0-7001-g610cd4eadec4

* Thu Mar 07 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git3.1
- Linux v5.0-6399-gf90d64483ebd

* Wed Mar 06 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git2.1
- Linux v5.0-3452-g3717f613f48d

* Tue Mar 05 2019 Jeremy Cline <jcline@redhat.com> - 5.1.0-0.rc0.git1.1
- Linux v5.0-510-gcd2a3bf02625

* Tue Mar 05 2019 Jeremy Cline <jcline@redhat.com>
- Reenable debugging options.

* Mon Mar 04 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-1
- Linux v5.0.0

* Tue Feb 26 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc8.git1.1
- Linux v5.0-rc8-3-g7d762d69145a

* Tue Feb 26 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Feb 25 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc8.git0.1
- Linux v5.0-rc8
- Disable debugging options.

* Fri Feb 22 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc7.git3.1
- Linux v5.0-rc7-118-g8a61716ff2ab

* Wed Feb 20 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Improvements to 96boards Rock960

* Wed Feb 20 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc7.git2.1
- Linux v5.0-rc7-85-g2137397c92ae

* Tue Feb 19 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc7.git1.1
- Linux v5.0-rc7-11-gb5372fe5dc84

* Tue Feb 19 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Feb 18 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc7.git0.1
- Linux v5.0-rc7
- Disable debugging options.

* Wed Feb 13 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc6.git1.1
- Linux v5.0-rc6-42-g1f947a7a011f

* Wed Feb 13 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Wed Feb 13 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Wed Feb 13 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable NXP Freescale Layerscape platform

* Mon Feb 11 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc6.git0.1
- Linux v5.0-rc6
- Disable debugging options.
- Tweaks to gcc9 fixes

* Mon Feb 04 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc5.git0.1
- Linux v5.0-rc5
- Disable debugging options.

* Fri Feb 01 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git3.1
- Linux v5.0-rc4-106-g5b4746a03199

* Thu Jan 31 2019 Hans de Goede <hdegoede@redhat.com>
- Add patches from -next to enable i915.fastboot by default on Skylake+ for
  https://fedoraproject.org/wiki/Changes/FlickerFreeBoot

* Wed Jan 30 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git2.1
- Linux v5.0-rc4-59-g62967898789d

* Tue Jan 29 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git1.1
- Linux v5.0-rc4-1-g4aa9fc2a435a

* Tue Jan 29 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Jan 28 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git0.1
- Linux v5.0-rc4
- Disable debugging options.

* Wed Jan 23 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc3.git1.1
- Linux v5.0-rc3-53-g333478a7eb21

* Wed Jan 23 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Jan 21 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc3.git0.1
- Linux v5.0-rc3
- Disable debugging options.

* Fri Jan 18 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git4.1
- Linux v5.0-rc2-211-gd7393226d15a

* Thu Jan 17 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git3.1
- Linux v5.0-rc2-145-g7fbfee7c80de

* Wed Jan 16 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git2.1
- Linux v5.0-rc2-141-g47bfa6d9dc8c

* Tue Jan 15 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git1.1
- Linux v5.0-rc2-36-gfe76fc6aaf53

* Tue Jan 15 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Jan 14 2019 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_GPIO_LEDS and CONFIG_GPIO_PCA953X  (rhbz 1601623)

* Mon Jan 14 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git0.1
- Linux v5.0-rc2

* Mon Jan 14 2019 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Sun Jan 13 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Raspberry Pi updates
- Update AllWinner A64 timer errata workaround

* Fri Jan 11 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git4.1
- Linux v5.0-rc1-43-g1bdbe2274920

* Thu Jan 10 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git3.1
- Linux v5.0-rc1-26-g70c25259537c

* Wed Jan 09 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git2.1
- Linux v5.0-rc1-24-g4064e47c8281

* Wed Jan 09 2019 Justin M. Forbes <jforbes@fedoraproject.org>
- Fix CVE-2019-3701 (rhbz 1663729 1663730)

* Tue Jan 08 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git1.1
- Linux v5.0-rc1-2-g7b5585136713

* Tue Jan 08 2019 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Jan 07 2019 Justin M. Forbes <jforbes@fedoraproject.org>
- Updates for secure boot

* Mon Jan 07 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git0.1
- Linux v5.0-rc1

* Mon Jan 07 2019 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Fri Jan 04 2019 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git7.1
- Linux v4.20-10979-g96d4f267e40f

* Fri Jan  4 2019 Peter Robinson <pbrobinson@fedoraproject.org>
- Updates for Arm plaforms
- IoT related updates

* Thu Jan 03 2019 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git6.1
- Linux v4.20-10911-g645ff1e8e704

* Wed Jan 02 2019 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git5.1
- Linux v4.20-10595-g8e143b90e4d4

* Mon Dec 31 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git4.1
- Linux v4.20-9221-gf12e840c819b

* Sun Dec 30 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git3.1
- Linux v4.20-9163-g195303136f19

* Fri Dec 28 2018 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_BPF_LIRC_MODE2 (rhbz 1628151)
- Enable CONFIG_NET_SCH_CAKE (rhbz 1655155)

* Fri Dec 28 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git2.1
- Linux v4.20-6428-g00c569b567c7

* Thu Dec 27 2018 Hans de Goede <hdegoede@redhat.com>
- Set CONFIG_REALTEK_PHY=y to workaround realtek ethernet issues (rhbz 1650984)

* Wed Dec 26 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git1.1
- Linux v4.20-3117-ga5f2bd479f58

* Wed Dec 26 2018 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Dec 24 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-1
- Linux v4.20.0

* Mon Dec 24 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Another fix for issue affecting Raspberry Pi 3-series WiFi (rhbz 1652093)

* Fri Dec 21 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc7.git3.1
- Linux v4.20-rc7-214-g9097a058d49e

* Thu Dec 20 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc7.git2.1
- Linux v4.20-rc7-202-g1d51b4b1d3f2

* Wed Dec 19 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial support for Raspberry Pi model 3A+
- Stability fixes for Raspberry Pi MMC (sdcard) driver

* Tue Dec 18 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc7.git1.1
- Linux v4.20-rc7-6-gddfbab46539f
- Reenable debugging options.

* Mon Dec 17 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc7.git0.1
- Linux v4.20-rc7

* Mon Dec 17 2018 Justin M. Forbes <jforbes@fedoraproject.org>
- Disable debugging options.

* Fri Dec 14 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Enhancements for Raspberrp Pi Camera

* Thu Dec 13 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc6.git2.1
- Linux v4.20-rc6-82-g65e08c5e8631

* Wed Dec 12 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc6.git1.2
- Reenable debugging options.

* Tue Dec 11 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc6.git1.1
- Linux v4.20-rc6-25-gf5d582777bcb

* Tue Dec 11 2018 Hans de Goede <hdegoede@redhat.com>
- Really fix non functional hotkeys on Asus FX503VD (#1645070)

* Mon Dec 10 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc6.git0.1
- Linux v4.20-rc6

* Mon Dec 10 2018 Justin M. Forbes <jforbes@fedoraproject.org>
- Disable debugging options.

* Fri Dec 07 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc5.git3.1
- Linux v4.20-rc5-86-gb72f711a4efa

* Wed Dec 05 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc5.git2.1
- Linux v4.20-rc5-44-gd08970904582

* Wed Dec 05 2018 Jeremy Cline <jeremy@jcline.org>
- Fix corruption bug in direct dispatch for blk-mq

* Tue Dec 04 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc5.git1.1
- Linux v4.20-rc5-21-g0072a0c14d5b
- Reenable debugging options.

* Mon Dec 03 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc5.git0.1
- Linux v4.20-rc5

* Mon Dec 03 2018 Justin M. Forbes <jforbes@fedoraproject.org>
- Disable debugging options.

* Mon Dec  3 2018 Hans de Goede <hdegoede@redhat.com>
- Fix non functional hotkeys on Asus FX503VD (#1645070)

* Fri Nov 30 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc4.git2.1
- Linux v4.20-rc4-156-g94f371cb7394

* Wed Nov 28 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc4.git1.1
- Linux v4.20-rc4-35-g121b018f8c74
- Reenable debugging options.

* Mon Nov 26 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc4.git0.1
- Linux v4.20-rc4
- Disable debugging options.

* Tue Nov 20 2018 Jeremy Cline <jcline@redhat.com> - 4.20.0-0.rc3.git1.1
- Linux v4.20-rc3-83-g06e68fed3282

* Tue Nov 20 2018 Jeremy Cline <jcline@redhat.com>
- Reenable debugging options.

* Tue Nov 20 2018 Hans de Goede <hdegoede@redhat.com>
- Turn on CONFIG_PINCTRL_GEMINILAKE on x86_64 (rhbz#1639155)
- Add a patch fixing touchscreens on HP AMD based laptops (rhbz#1644013)
- Add a patch fixing KIOX010A accelerometers (rhbz#1526312)

* Mon Nov 19 2018 Jeremy Cline <jcline@redhat.com> - 4.20.0-0.rc3.git0.1
- Linux v4.20-rc3

* Mon Nov 19 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Sat Nov 17 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix WiFi on Raspberry Pi 3 on aarch64 (rhbz 1649344)
- Fixes for Raspberry Pi hwmon driver and firmware interface

* Fri Nov 16 2018 Hans de Goede <hdegoede@redhat.com>
- Enable a few modules needed for accelerometer and other sensor support
  on some HP X2 2-in-1s

* Thu Nov 15 2018 Justin M. Forbes <jforbes@redhat.com> - 4.20.0-0.rc2.git2.1
- Linux v4.20-rc2-52-g5929a1f0ff30

* Wed Nov 14 2018 Justin M. Forbes <jforbes@redhat.com> - 4.20.0-0.rc2.git1.1
- Linux v4.20-rc2-37-g3472f66013d1
- Reenable debugging options.

* Mon Nov 12 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Further updates for ARM
- More Qualcomm SD845 enablement
- FPGA Device Feature List (DFL) support
- Minor cleanups

* Sun Nov 11 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc2.git0.1
- Linux v4.20-rc2
- Disable debugging options.

* Fri Nov 09 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc1.git4.1
- Linux v4.20-rc1-145-gaa4330e15c26

* Thu Nov  8 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial Qualcomm SD845 enablement

* Thu Nov 08 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc1.git3.1
- Linux v4.20-rc1-98-gb00d209241ff

* Wed Nov 07 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc1.git2.1
- Linux v4.20-rc1-87-g85758777c2a2

* Wed Nov  7 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial Arm config updates for 4.20

* Tue Nov 06 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc1.git1.1
- Linux v4.20-rc1-62-g8053e5b93eca
- Reenable debugging options.

* Mon Nov 05 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc1.git0.1
- Linux v4.20-rc1

* Mon Nov 05 2018 Justin M. Forbes <jforbes@fedoraproject.org>
- Disable debugging options.

* Fri Nov 02 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git9.1
- Linux v4.19-12532-g8adcc59974b8

* Thu Nov 01 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git8.1
- Linux v4.19-12279-g5b7449810ae6

* Wed Oct 31 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git7.1
- Linux v4.19-11807-g310c7585e830

* Tue Oct 30 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git6.1
- Linux v4.19-11706-g11743c56785c

* Mon Oct 29 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git5.1
- Linux v4.19-9448-g673c790e7282

* Fri Oct 26 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git4.1
- Linux v4.19-6148-ge5f6d9afa341

* Thu Oct 25 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git3.1
- Linux v4.19-5646-g3acbd2de6bc3

* Wed Oct 24 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git2.1
- Linux v4.19-4345-g638820d8da8e

* Tue Oct 23 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git1.1
- Linux v4.19-1676-g0d1b82cd8ac2
- Reenable debugging options.

* Mon Oct 22 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-1
- Linux v4.19
- Disable debugging options.

* Sat Oct 20 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix network on some i.MX6 devices (rhbz 1628209)

* Fri Oct 19 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git4.1
- Linux v4.19-rc8-95-g91b15613ce7f
- Enable pinctrl-cannonlake (rhbz 1641057)

* Thu Oct 18 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git3.1
- Linux v4.19-rc8-27-gfa520c47eaa1

* Wed Oct 17 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git2.1
- Linux v4.19-rc8-16-gc343db455eb3

* Tue Oct 16 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Fixes to Rock960 series of devices, improves stability considerably
- Raspberry Pi graphics fix

* Tue Oct 16 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git1.1
- Linux v4.19-rc8-11-gb955a910d7fd
- Re-enable debugging options.

* Mon Oct 15 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git0.1
- Linux v4.19-rc8

* Mon Oct 15 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Fri Oct 12 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Rebase device specific NVRAM files on brcm WiFi devices to latest

* Fri Oct 12 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git4.1
- Linux v4.19-rc7-139-g6b3944e42e2e

* Thu Oct 11 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git3.1
- Linux v4.19-rc7-61-g9f203e2f2f06

* Wed Oct 10 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git2.1
- Linux v4.19-rc7-33-gbb2d8f2f6104

* Tue Oct 09 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git1.1
- Linux v4.19-rc7-15-g64c5e530ac2c
- Re-enable debugging options.

* Mon Oct 08 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git0.1
- Linux v4.19-rc7

* Mon Oct 08 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Fri Oct 05 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git4.1
- Linux v4.19-rc6-223-gbefad944e231

* Thu Oct 04 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git3.1
- Linux v4.19-rc6-177-gcec4de302c5f

* Wed Oct 03 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git2.1
- Linux v4.19-rc6-37-g6bebe37927f3

* Tue Oct 02 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git1.1
- Linux v4.19-rc6-29-g1d2ba7fee28b
- Re-enable debugging options.

* Mon Oct 01 2018 Laura Abbott <labbott@redhat.com>
- Disable CONFIG_CRYPTO_DEV_SP_PSP (rhbz 1608242)

* Mon Oct 01 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git0.1
- Linux v4.19-rc6

* Mon Oct 01 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Mon Oct  1 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Support loading device specific NVRAM files on brcm WiFi devices

* Fri Sep 28 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git3.1
- Linux v4.19-rc5-159-gad0371482b1e

* Wed Sep 26 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Add thermal trip to bcm283x (Raspberry Pi) cpufreq
- Add initial RockPro64 DT support

* Wed Sep 26 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git2.1
- Linux v4.19-rc5-143-gc307aaf3eb47

* Tue Sep 25 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git1.1
- Linux v4.19-rc5-99-g8c0f9f5b309d
- Re-enable debugging options.

* Mon Sep 24 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git0.1
- Linux v4.19-rc5

* Mon Sep 24 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Fri Sep 21 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git4.1
- Linux v4.19-rc4-176-g211b100a5ced

* Thu Sep 20 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git3.1
- Linux v4.19-rc4-137-gae596de1a0c8

* Wed Sep 19 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git2.1
- Linux v4.19-rc4-86-g4ca719a338d5

* Tue Sep 18 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git1.1
- Linux v4.19-rc4-78-g5211da9ca526
- Enable debugging options.

* Mon Sep 17 2018 Jeremy Cline <jeremy@jcline.org> - 4.19.0-0.rc4.git0.1
- Linux v4.19-rc4

* Mon Sep 17 2018 Jeremy Cline <jcline@redhat.com>
- Stop including the i686-PAE config in the sources
- Disable debugging options.

* Fri Sep 14 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git3.1
- Linux v4.19-rc3-247-gf3c0b8ce4840

* Thu Sep 13 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git2.1
- Linux v4.19-rc3-130-g54eda9df17f3

* Thu Sep 13 2018 Hans de Goede <hdegoede@redhat.com>
- Add patch silencing "EFI stub: UEFI Secure Boot is enabled." at boot

* Wed Sep 12 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git1.1
- Linux v4.19-rc3-21-g5e335542de83
- Re-enable debugging options.

* Mon Sep 10 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git0.1
- Linux v4.19-rc3

* Mon Sep 10 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Fri Sep 07 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git3.1
- Linux v4.19-rc2-205-ga49a9dcce802

* Thu Sep 06 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git2.1
- Linux v4.19-rc2-163-gb36fdc6853a3

* Wed Sep 05 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git1.1
- Linux v4.19-rc2-107-g28619527b8a7
- Re-enable debugging options

* Mon Sep  3 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable bcm283x VCHIQ, camera and analog audio drivers
- ARM config updates for 4.19

* Mon Sep 03 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git0.1
- Linux v4.19-rc2

* Mon Sep 03 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Fri Aug 31 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git4.1
- Linux v4.19-rc1-195-g4658aff6eeaa

* Thu Aug 30 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git3.1
- Linux v4.19-rc1-124-g58c3f14f86c9

* Wed Aug 29 2018 Jeremy Cline <jeremy@jcline.org>
- Enable the AFS module (rhbz 1616016)

* Wed Aug 29 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git2.1
- Linux v4.19-rc1-95-g3f16503b7d22

* Tue Aug 28 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git1.1
- Linux v4.19-rc1-88-g050cdc6c9501
- Re-enable debugging options

* Mon Aug 27 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git0.1
- Linux v4.19-rc1

* Mon Aug 27 2018 Jeremy Cline <jcline@redhat.com>
- Disable debugging options.

* Sat Aug 25 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git12.1
- Linux v4.18-12872-g051935978432

* Fri Aug 24 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git11.1
- Linux v4.18-12721-g33e17876ea4e

* Thu Aug 23 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git10.1
- Linux v4.18-11682-g815f0ddb346c

* Wed Aug 22 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git9.1
- Linux v4.18-11219-gad1d69735878

* Tue Aug 21 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git8.1
- Linux v4.18-10986-g778a33959a8a

* Mon Aug 20 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git7.1
- Linux v4.18-10721-g2ad0d5269970

* Sun Aug 19 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git6.1
- Linux v4.18-10568-g08b5fa819970

* Sat Aug 18 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git5.1
- Linux v4.18-8895-g1f7a4c73a739

* Fri Aug 17 2018 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_AF_KCM (rhbz 1613819)

* Fri Aug 17 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git4.1
- Linux v4.18-8108-g5c60a7389d79
- Re-enable AEGIS and MORUS ciphers (rhbz 1610180)

* Thu Aug 16 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git3.1
- Linux v4.18-7873-gf91e654474d4

* Wed Aug 15 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop PPC64 (Big Endian) configs

* Wed Aug 15 2018 Laura Abbott <labbott@redhat.com> - 4.19.0-0.rc0.git2.1
- Linux v4.18-2978-g1eb46908b35d

* Tue Aug 14 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git1.1
- Reenable debugging options.
- Linux v4.18-1283-g10f3e23f07cb

* Mon Aug 13 2018 Laura Abbott <labbott@redhat.com> - 4.18.0-1
- Linux v4.18
- Disable debugging options.
