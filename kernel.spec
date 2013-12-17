# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

# Sign modules on x86.  Make sure the config files match this setting if more
# architectures are added.
%ifarch %{ix86} x86_64
%global signmodules 1
%else
%global signmodules 0
%endif

# Save original buildid for later if it's defined
%if 0%{?buildid:1}
%global orig_buildid %{buildid}
%undefine buildid
%endif

###################################################################
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456". This will be
# appended to the full kernel version.
#
# (Uncomment the '#' and both spaces below to set the buildid.)
#
# % define buildid .local
###################################################################

# The buildid can also be specified on the rpmbuild command line
# by adding --define="buildid .whatever". If both the specfile and
# the environment define a buildid they will be concatenated together.
%if 0%{?orig_buildid:1}
%if 0%{?buildid:1}
%global srpm_buildid %{buildid}
%define buildid %{srpm_buildid}%{orig_buildid}
%else
%define buildid %{orig_buildid}
%endif
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
%global baserelease 100
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 11

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 10
# Is it a -stable RC?
%define stable_rc 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%if 0%{?stable_rc}
# stable RCs are incremental patches, so we need the previous stable patch
%define stable_base %(echo $((%{stable_update} - 1)))
%endif
%endif
%define rpmversion 3.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 0
# The git snapshot level
%define gitrev 100
# Set rpm version accordingly
%define rpmversion 3.%{upstream_sublevel}.0
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
# kernel-smp (only valid for ppc 32-bit)
%define with_smp       %{?_without_smp:       0} %{?!_without_smp:       1}
# kernel-PAE (only valid for i686)
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# kernel-kirkwood (only valid for arm)
%define with_kirkwood       %{?_without_kirkwood:       0} %{?!_without_kirkwood:       1}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
#
# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}
#
# build a release kernel on rawhide
%define with_release   %{?_with_release:      1} %{?!_with_release:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%if 0%{?released_kernel}
%define doc_build_fail false
%else
%define doc_build_fail true
%endif

%define rawhide_skip_docs 0
%if 0%{?rawhide_skip_docs}
%define with_doc 0
%define doc_build_fail true
%endif

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%if 0%{?stable_rc}
%define stable_rctag .rc%{stable_rc}
%define pkg_release 0%{stable_rctag}.%{fedora_build}%{?buildid}%{?dist}
%else
%define pkg_release %{fedora_build}%{?buildid}%{?dist}
%endif

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
%define kversion 3.%{base_sublevel}

%define make_target bzImage

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{with_vanilla}
# Vanilla kernels before 3.7 don't contain modsign support.  Remove this when
# we rebase to 3.7
%define signmodules 0
%define nopatches 1
%endif

%if %{nopatches}
%define with_bootwrapper 0
%define variant -vanilla
%else
%define variant_fedora -fedora
%endif

%define using_upstream_branch 0
%if 0%{?upstream_branch:1}
%define stable_update 0
%define using_upstream_branch 1
%define variant -%{upstream_branch}%{?variant_fedora}
%define pkg_release 0.%{fedora_build}%{upstream_branch_tag}%{?buildid}%{?dist}
%endif

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# kernel-PAE is only built on i686.
%ifnarch i686
%define with_pae 0
%endif

# kernel-kirkwood is only built for armv5
%ifnarch armv5tel
%define with_kirkwood 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_smp 0
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_smp 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%define with_pae 0
%endif
%define with_smp 0
%define with_pae 0
%define with_tools 0
%define with_perf 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64 ppc64p7 s390 s390x
%endif

# Overrides for generic default options

# only ppc needs a separate smp kernel
%ifnarch ppc 
%define with_smp 0
%endif

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# bootwrapper is only on ppc
%ifnarch ppc ppc64 ppc64p7
%define with_bootwrapper 0
%endif

# sparse blows up on ppc64
%ifarch ppc64 ppc ppc64p7
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define all_arch_configs kernel-%{version}-i?86*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64 ppc64p7
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%define with_tools 0
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc{-,.}*config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define asmarch arm
%define hdrarch arm
%define make_target bzImage
%define kernel_image arch/arm/boot/zImage
# we only build headers/perf/tools on the base arm arches
# just like we used to only build them on i386 for x86
%ifarch armv5tel
%define with_up 0
%endif
%ifnarch armv5tel armv7hl
%define with_headers 0
%define with_perf 0
%define with_tools 0
%endif
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}%{using_upstream_branch}
%define listnewconfig_fail 0
%else
%define listnewconfig_fail 1
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386 s390

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs %{ix86} x86_64 ppc ppc64 ppc64p7 %{arm}

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.2.5-7.fc17, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools >= 3.16-4, initscripts >= 8.11.1-1, grubby >= 8.3-1
%define initrd_prereq  dracut >= 001-7

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
Provides: kernel-highbank\
Provides: kernel-highbank-uname-r = %{KVERREL}%{?1:.%{1}}\
Provides: kernel-omap\
Provides: kernel-omap-uname-r = %{KVERREL}%{?1:.%{1}}\
Provides: kernel-tegra\
Provides: kernel-tegra-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20130724-0.3.git31f6b30\
Requires(post): /sbin/new-kernel-pkg\
Requires(preun): /sbin/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2 and Redistributable, no modification permitted
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 ppc ppc64 ppc64p7 s390 s390x %{arm}
ExclusiveOS: Linux

%kernel_reqprovconf

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config, hmaccalc
BuildRequires: net-tools, hostname, bc
BuildRequires: xmlto, asciidoc
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed) bison audit-libs-devel
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8/RHEL 6.
# The -r flag to find-debuginfo.sh to invoke eu-strip --reloc-debug-sections
# reduces the number of relocations in kernel module .ko.debug files and was
# introduced with rpm 4.9 and elfutils 0.153.
BuildRequires: rpm-build >= 4.9.0-1, elfutils >= elfutils-0.153-1
%define debuginfo_args --strict-build-id -r
%endif

%if %{signmodules}
BuildRequires: openssl
BuildRequires: pesign >= 0.10-4
%endif

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v3.0/linux-%{kversion}.tar.xz

%if %{signmodules}
Source11: x509.genkey
%endif

Source15: merge.pl
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-extra-sign.sh

Source19: Makefile.release
Source20: Makefile.config
Source21: config-debug
Source22: config-nodebug
Source23: config-generic

Source30: config-x86-generic
Source31: config-i686-PAE
Source32: config-x86-32-generic

Source40: config-x86_64-generic

Source50: config-powerpc-generic
Source51: config-powerpc32-generic
Source52: config-powerpc32-smp
Source53: config-powerpc64
Source54: config-powerpc64p7

Source70: config-s390x

# Unified ARM kernels
Source100: config-arm-generic
Source101: config-armv7
Source102: config-armv7-generic

# Legacy ARM kernels
Source103: config-arm-kirkwood

# This file is intentionally left empty in the stock kernel. Its a nicety
# added for those wanting to do custom rebuilds with altered config opts.
Source1000: config-local

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-3.%{base_sublevel}.%{stable_base}.xz
Patch00: %{stable_patch_00}
%endif
%if 0%{?stable_rc}
%define    stable_patch_01  patch-3.%{base_sublevel}.%{stable_update}-rc%{stable_rc}.xz
Patch01: %{stable_patch_01}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Patch00: patch-3.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
Patch01: patch-3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Patch00: patch-3.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif
%endif

%if %{using_upstream_branch}
### BRANCH PATCH ###
%endif

# we also need compile fixes for -vanilla
Patch04: compile-fixes.patch

# build tweak for build ID magic, even for -vanilla
Patch05: makefile-after_link.patch

%if !%{nopatches}


# revert upstream patches we get via other methods
Patch09: upstream-reverts.patch
# Git trees.

# Standalone patches

Patch100: taint-vbox.patch

Patch110: vmbugon-warnon.patch

Patch390: defaults-acpi-video.patch

Patch394: acpi-debug-infinite-loop.patch

Patch450: input-kill-stupid-messages.patch
Patch452: no-pcspkr-modalias.patch

Patch460: serial-460800.patch

Patch470: die-floppy-die.patch

Patch510: silence-noise.patch
Patch530: silence-fbcon-logo.patch

Patch800: crash-driver.patch

# secure boot
Patch1000: devel-pekey-secure-boot-20130502.patch

# virt + ksm patches

# DRM
#atch1700: drm-edid-try-harder-to-fix-up-broken-headers.patch
#Patch1800: drm-vgem.patch

# nouveau + drm fixes
# intel drm is all merged upstream
Patch1824: drm-intel-next.patch
# mustard patch to shut abrt up. please drop (and notify ajax) whenever it
# fails to apply
Patch1826: drm-i915-tv-detect-hush.patch

# Quiet boot fixes
# silence the ACPI blacklist code
Patch2802: silence-acpi-blacklist.patch

# media patches
Patch2899: v4l-dvb-fixes.patch
Patch2900: v4l-dvb-update.patch
Patch2901: v4l-dvb-experimental.patch

# fs fixes

# NFSv4

# patches headed upstream
Patch10000: fs-proc-devtree-remove_proc_entry.patch

Patch12016: disable-i8042-check-on-apple-mac.patch

Patch14000: hibernate-freeze-filesystems.patch

Patch14010: lis3-improve-handling-of-null-rate.patch

Patch15000: nowatchdog-on-virt.patch

Patch20000: 0001-efifb-Skip-DMI-checks-if-the-bootloader-knows-what-i.patch
Patch20001: 0002-x86-EFI-Calculate-the-EFI-framebuffer-size-instead-o.patch

# ARM
Patch21000: arm-export-read_current_timer.patch

# lpae
Patch21001: arm-lpae-ax88796.patch

# ARM omap
Patch21003: arm-omap-load-tfp410.patch

# ARM tegra
Patch21005: arm-tegra-usb-no-reset-linux33.patch

#rhbz 754518
Patch21235: scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

Patch22000: weird-root-dentry-name-debug.patch

#rhbz 892811
Patch22247: ath9k_rx_dma_stop_check.patch

#rhbz 927469
Patch25007: fix-child-thread-introspection.patch

#rhbz 977040
Patch25056: iwl3945-better-skb-management-in-rx-path.patch
Patch25057: iwl4965-better-skb-management-in-rx-path.patch

#rhbz 963715
Patch25077: media-cx23885-Fix-TeVii-S471-regression-since-introduction-of-ts2020.patch

#rhbz 971893
Patch25106: bonding-driver-alb-learning.patch

#rhbz 985522
Patch25107: ntp-Make-periodic-RTC-update-more-reliable.patch

#rhbz 902012
Patch25114: elevator-Fix-a-race-in-elevator-switching-and-md.patch
Patch25115: elevator-acquire-q-sysfs_lock-in-elevator_change.patch

#rhbz 974072
Patch25117: rt2800-add-support-for-rf3070.patch

#rhbz 1015989
Patch25122: netfilter-nf_conntrack-use-RCU-safe-kfree-for-conntr.patch

#rhbz 982153
Patch25123: iommu-Remove-stack-trace-from-broken-irq-remapping-warning.patch

#rhbz 998732
Patch25125: vfio-iommu-Fixed-interaction-of-VFIO_IOMMU_MAP_DMA.patch

#rhbz 896695
Patch25126: 0001-iwlwifi-don-t-WARN-on-host-commands-sent-when-firmwa.patch
Patch25127: 0002-iwlwifi-don-t-WARN-on-bad-firmware-state.patch

#rhbz 993744
Patch25128: dm-cache-policy-mq_fix-large-scale-table-allocation-bug.patch

#rhbz 1000439
Patch25129: cpupower-Fix-segfault-due-to-incorrect-getopt_long-a.patch

#rhbz 1010679
Patch25130: fix-radeon-sound.patch
Patch25149: drm-radeon-24hz-audio-fixes.patch

#rhbz 984696
Patch25132: rt2800usb-slow-down-TX-status-polling.patch

#rhbz 1023413
Patch25135: alps-Support-for-Dell-XT2-model.patch

#rhbz 1011621
Patch25137: cifs-Allow-LANMAN-auth-for-unencapsulated-auth-methods.patch

#rhbz 1025769
Patch25142: iwlwifi-dvm-dont-override-mac80211-queue-setting.patch

Patch25143: drm-qxl-backport-fixes-for-Fedora.patch
Patch25160: drm-qxl-fix-memory-leak-in-release-list-handling.patch

Patch25144: Input-evdev-fall-back-to-vmalloc-for-client-event-buffer.patch

#CVE-2013-4563 rhbz 1030015 1030017
Patch25145: ipv6-fix-headroom-calculation-in-udp6_ufo_fragment.patch

#rhbz 1015905
Patch25146: 0001-ip6_output-fragment-outgoing-reassembled-skb-properl.patch
Patch25147: 0002-netfilter-push-reasm-skb-through-instead-of-original.patch

#rhbz 1011362
Patch25148: alx-Reset-phy-speed-after-resume.patch

#rhbz 1031086
Patch25150: slab_common-Do-not-check-for-duplicate-slab-names.patch

#rhbz 967652
Patch25151: KVM-x86-fix-emulation-of-movzbl-bpl-eax.patch

# Fix 15sec NFS mount delay
Patch25152: sunrpc-create-a-new-dummy-pipe-for-gssd-to-hold-open.patch
Patch25153: sunrpc-replace-gssd_running-with-more-reliable-check.patch
Patch25154: nfs-check-gssd-running-before-krb5i-auth.patch

#CVE-2013-6382 rhbz 1033603 1034670
Patch25157: xfs-underflow-bug-in-xfs_attrlist_by_handle.patch

#rhbz 1022733
Patch25158: via-velocity-fix-netif_receive_skb-use-in-irq-disable.patch

#rhbz 998342
Patch25159: usbnet-fix-status-interrupt-urb-handling.patch

#CVE-2013-6405 rhbz 1035875 1035887
Patch25161: inet-prevent-leakage-of-uninitialized-memory-to-user.patch
Patch25162: inet-fix-addr_len-msg_namelen-assignment-in-recv_error-and-rxpmtu-functions.patch

#rhbz 958826
Patch25164: dell-laptop.patch

#CVE-2013-XXXX rhbz 1039845 1039874
Patch25165: net-rework-recvmsg-handler-msg_name-and-msg_namelen-.patch

#rhbz 1030802
Patch25170: Input-elantech-add-support-for-newer-August-2013-dev.patch
Patch25171: elantech-Properly-differentiate-between-clickpads-an.patch

#CVE-2013-6367 rhbz 1032207 1042081
Patch25172: KVM-x86-Fix-potential-divide-by-0-in-lapic.patch

#CVE-2013-6368 rhbz 1032210 1042090
Patch25173: KVM-x86-Convert-vapic-synchronization-to-_cached-functions.patch

#CVE-2013-6376 rhbz 1033106 1042099
Patch25174: KVM-x86-fix-guest-initiated-crash-with-x2apic.patch

#CVE-2013-4587 rhbz 1030986 1042071
Patch25175: KVM-Improve-create-VCPU-parameter.patch

#rhbz 1025770
Patch25176: br-fix-use-of-rx_handler_data-in-code-executed-on-no.patch

# END OF PATCH DEFINITIONS

%endif

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


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
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}

%package -n python-perf
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf
The python-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
Group: Development/System
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

%endif # with_tools


#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:\.%{1}}/.*|/.*%%{KVERREL}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
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
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-modules-extra = %{version}-%{release}%{?1:.%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel-modules-extra-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
AutoReqProv: no\
%description -n kernel%{?variant}%{?1:-%{1}}-modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_modules_extra_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled for SMP machines
%kernel_variant_package -n SMP smp
%description smp
This package includes a SMP version of the Linux kernel. It is
required only on machines with two or more CPUs as well as machines with
hyperthreading technology.

Install the kernel-smp package if your machine uses two or more CPUs.


%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package PAE
%description PAE
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package PAEdebug
Obsoletes: kernel-PAE-debug
%description PAEdebug
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

%define variant_summary The Linux kernel compiled for marvell kirkwood boards
%kernel_variant_package kirkwood
%description kirkwood
This package includes a version of the Linux kernel with support for
marvell kirkwood based systems, i.e., guruplug, sheevaplug


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}%{with_pae}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if %{with_smponly}
%if !%{with_smp}
echo "Cannot build --with smponly, smp build is disabled"
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
%if !%{using_upstream_branch}
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
%endif
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
%define vanillaversion 3.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 3.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 3.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 3.%{base_sublevel}
%endif
%endif
%endif

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-3.*' \
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
      cp -rl $sharedir/vanilla-%{kversion} .
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

    cp -rl $sharedir/vanilla-%{vanillaversion} .

  else

    # Need to apply patches to the base vanilla version.
    cp -rl vanilla-%{kversion} vanilla-%{vanillaversion}
    cd vanilla-%{vanillaversion}

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    ApplyPatch patch-3.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
    ApplyPatch patch-3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    ApplyPatch patch-3.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif

    cd ..

  fi

%endif

else

  # We already have all vanilla dirs, just change to the top-level directory.
  cd kernel-%{kversion}%{?dist}

fi

# Now build the fedora kernel tree.
cp -rl vanilla-%{vanillaversion} linux-%{KVERREL}

cd linux-%{KVERREL}

# released_kernel with possible stable updates
%if 0%{?stable_base}
ApplyPatch %{stable_patch_00}
%endif
%if 0%{?stable_rc}
ApplyPatch %{stable_patch_01}
%endif

%if %{using_upstream_branch}
### BRANCH APPLY ###
%endif

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} .

%if !%{debugbuildsenabled}
%if %{with_release}
# The normal build is a really debug build and the user has explicitly requested
# a release kernel. Change the config files into non-debug versions.
make -f %{SOURCE19} config-release
%endif
%endif

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE20} VERSION=%{version} configs

# Merge in any user-provided local config option changes
for i in kernel-%{version}-*.config
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE1000} $i.tmp > $i
  rm $i.tmp
done

ApplyPatch makefile-after_link.patch

#
# misc small stuff to make things compile
#
ApplyOptionalPatch compile-fixes.patch

%if !%{nopatches}

# revert patches from upstream that conflict or that we get via other means
ApplyOptionalPatch upstream-reverts.patch -R


ApplyPatch taint-vbox.patch

ApplyPatch vmbugon-warnon.patch

# Architecture patches
# x86(-64)

#
# ARM
#
ApplyPatch arm-export-read_current_timer.patch
ApplyPatch arm-lpae-ax88796.patch
ApplyPatch arm-omap-load-tfp410.patch
ApplyPatch arm-tegra-usb-no-reset-linux33.patch

#
# bugfixes to drivers and filesystems
#

# ext4

# xfs

# btrfs

# eCryptfs

# NFSv4

# USB

# WMI

# ACPI
ApplyPatch defaults-acpi-video.patch
ApplyPatch acpi-debug-infinite-loop.patch

#
# PCI
#

#
# SCSI Bits.
#

# ACPI

# ALSA

# Networking

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

ApplyPatch no-pcspkr-modalias.patch

# Allow to use 480600 baud on 16C950 UARTs
ApplyPatch serial-460800.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch silence-noise.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch silence-fbcon-logo.patch

# Changes to upstream defaults.


# /dev/crash driver.
ApplyPatch crash-driver.patch

# secure boot
ApplyPatch devel-pekey-secure-boot-20130502.patch

# Assorted Virt Fixes

# DRM core
#ApplyPatch drm-edid-try-harder-to-fix-up-broken-headers.patch
#ApplyPatch drm-vgem.patch

# Nouveau DRM

# Intel DRM
ApplyOptionalPatch drm-intel-next.patch
ApplyPatch drm-i915-tv-detect-hush.patch

# silence the ACPI blacklist code
ApplyPatch silence-acpi-blacklist.patch

# V4L/DVB updates/fixes/experimental drivers
#  apply if non-empty
ApplyOptionalPatch v4l-dvb-fixes.patch
ApplyOptionalPatch v4l-dvb-update.patch
ApplyOptionalPatch v4l-dvb-experimental.patch

# Patches headed upstream
ApplyPatch fs-proc-devtree-remove_proc_entry.patch

ApplyPatch disable-i8042-check-on-apple-mac.patch

# FIXME: REBASE
#ApplyPatch hibernate-freeze-filesystems.patch

ApplyPatch lis3-improve-handling-of-null-rate.patch

# Disable watchdog on virtual machines.
ApplyPatch nowatchdog-on-virt.patch

#ApplyPatch 0001-efifb-Skip-DMI-checks-if-the-bootloader-knows-what-i.patch
#ApplyPatch 0002-x86-EFI-Calculate-the-EFI-framebuffer-size-instead-o.patch

#rhbz 754518
ApplyPatch scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

ApplyPatch weird-root-dentry-name-debug.patch

#rhbz 892811
ApplyPatch ath9k_rx_dma_stop_check.patch

#rhbz 927469
ApplyPatch fix-child-thread-introspection.patch

#rhbz 977040
ApplyPatch iwl3945-better-skb-management-in-rx-path.patch
ApplyPatch iwl4965-better-skb-management-in-rx-path.patch

#rhbz 963715
ApplyPatch media-cx23885-Fix-TeVii-S471-regression-since-introduction-of-ts2020.patch

#rhbz 985522
ApplyPatch ntp-Make-periodic-RTC-update-more-reliable.patch

#rhbz 971893
ApplyPatch bonding-driver-alb-learning.patch

#rhbz 902012
ApplyPatch elevator-Fix-a-race-in-elevator-switching-and-md.patch
ApplyPatch elevator-acquire-q-sysfs_lock-in-elevator_change.patch

#rhbz 974072
ApplyPatch rt2800-add-support-for-rf3070.patch

#rhbz 1015989
ApplyPatch netfilter-nf_conntrack-use-RCU-safe-kfree-for-conntr.patch

#rhbz 982153
ApplyPatch iommu-Remove-stack-trace-from-broken-irq-remapping-warning.patch

#rhbz 998732
ApplyPatch vfio-iommu-Fixed-interaction-of-VFIO_IOMMU_MAP_DMA.patch

#rhbz 896695
ApplyPatch 0001-iwlwifi-don-t-WARN-on-host-commands-sent-when-firmwa.patch
ApplyPatch 0002-iwlwifi-don-t-WARN-on-bad-firmware-state.patch

#rhbz 993744
ApplyPatch dm-cache-policy-mq_fix-large-scale-table-allocation-bug.patch

#rhbz 1000439
ApplyPatch cpupower-Fix-segfault-due-to-incorrect-getopt_long-a.patch

#rhbz 1010679
ApplyPatch fix-radeon-sound.patch
ApplyPatch drm-radeon-24hz-audio-fixes.patch

#rhbz 984696
ApplyPatch rt2800usb-slow-down-TX-status-polling.patch

#rhbz 1023413
ApplyPatch alps-Support-for-Dell-XT2-model.patch

#rhbz 1011621
ApplyPatch cifs-Allow-LANMAN-auth-for-unencapsulated-auth-methods.patch

#rhbz 1025769
ApplyPatch iwlwifi-dvm-dont-override-mac80211-queue-setting.patch

ApplyPatch drm-qxl-backport-fixes-for-Fedora.patch
ApplyPatch drm-qxl-fix-memory-leak-in-release-list-handling.patch

ApplyPatch Input-evdev-fall-back-to-vmalloc-for-client-event-buffer.patch

#CVE-2013-4563 rhbz 1030015 1030017
ApplyPatch ipv6-fix-headroom-calculation-in-udp6_ufo_fragment.patch

#rhbz 1015905
ApplyPatch 0001-ip6_output-fragment-outgoing-reassembled-skb-properl.patch
ApplyPatch 0002-netfilter-push-reasm-skb-through-instead-of-original.patch

#rhbz 1011362
ApplyPatch alx-Reset-phy-speed-after-resume.patch

#rhbz 1031086
ApplyPatch slab_common-Do-not-check-for-duplicate-slab-names.patch

#rhbz 967652
ApplyPatch KVM-x86-fix-emulation-of-movzbl-bpl-eax.patch

# Fix 15sec NFS mount delay
ApplyPatch sunrpc-create-a-new-dummy-pipe-for-gssd-to-hold-open.patch
ApplyPatch sunrpc-replace-gssd_running-with-more-reliable-check.patch
ApplyPatch nfs-check-gssd-running-before-krb5i-auth.patch

#CVE-2013-6382 rhbz 1033603 1034670
ApplyPatch xfs-underflow-bug-in-xfs_attrlist_by_handle.patch

#rhbz 1022733
ApplyPatch via-velocity-fix-netif_receive_skb-use-in-irq-disable.patch

#rhbz 998342
ApplyPatch usbnet-fix-status-interrupt-urb-handling.patch

#CVE-2013-6405 rhbz 1035875 1035887
ApplyPatch inet-prevent-leakage-of-uninitialized-memory-to-user.patch
ApplyPatch inet-fix-addr_len-msg_namelen-assignment-in-recv_error-and-rxpmtu-functions.patch

#rhbz 958826
ApplyPatch dell-laptop.patch

#CVE-2013-XXXX rhbz 1039845 1039874
ApplyPatch net-rework-recvmsg-handler-msg_name-and-msg_namelen-.patch

#rhbz 1030802
ApplyPatch Input-elantech-add-support-for-newer-August-2013-dev.patch
ApplyPatch elantech-Properly-differentiate-between-clickpads-an.patch

#CVE-2013-6367 rhbz 1032207 1042081
ApplyPatch KVM-x86-Fix-potential-divide-by-0-in-lapic.patch

#CVE-2013-6368 rhbz 1032210 1042090
ApplyPatch KVM-x86-Convert-vapic-synchronization-to-_cached-functions.patch

#CVE-2013-6376 rhbz 1033106 1042099
ApplyPatch KVM-x86-fix-guest-initiated-crash-with-x2apic.patch

#CVE-2013-4587 rhbz 1030986 1042071
ApplyPatch KVM-Improve-create-VCPU-parameter.patch

#rhbz 1025770
ApplyPatch br-fix-use-of-rx_handler_data-in-code-executed-on-no.patch

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif


# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make ARCH=$Arch oldnoconfig
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug \
    				-i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    %if 0%{?stable_update}
    # make sure SUBLEVEL is incremented on a stable release.  Sigh 3.x.
    perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{?stablerev}/" Makefile
    %endif

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    %if %{signmodules}
    cp %{SOURCE11} .
    chmod +x scripts/sign-file
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch oldnoconfig >/dev/null
%ifarch %{arm}
    # http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags} KALLSYMS_EXTRA_PASS=1

    make -s ARCH=$Arch V=1 dtbs
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    install -m 644 arch/arm/boot/dts/*.dtb $RPM_BUILD_ROOT/boot/dtb-$KernelVer/
    rm -f arch/arm/boot/dts/*.dtb
%else
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags}
%endif
    make -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
    %if %{signmodules}
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

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # we'll get it from the linux-firmware package and we don't want conflicts
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=

%ifarch %{vdso_arches}
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
        $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
%endif

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
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc ppc64 ppc64p7
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    # include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
    if [ -d arch/%{asmarch}/mach-${Flavour}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Flavour}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi

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
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler'
    collect_modules_list drm \
    			 'drm_open|drm_init'
    collect_modules_list modesetting \
    			 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # Call the modules-extra script to move things around
    %{SOURCE17} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE16}

%if %{signmodules}
    # Save off the .tmp_versions/ directory.  We'll use it in the 
    # __debug_install_post macro below to sign the right things
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp signing_key.priv signing_key.priv.sign${Flavour:+.${Flavour}}
    cp signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}
%endif

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap devname softdep
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir

    # This is going to create a broken link during the build, but we don't use
    # it after this point.  We need the link to actually point to something
    # when kernel-devel is installed, and a relative link doesn't work across
    # the F17 UsrMove feature.
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
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
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image PAEdebug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image PAE
%endif

%if %{with_kirkwood}
BuildKernel %make_target %kernel_image kirkwood
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_smp}
BuildKernel %make_target %kernel_image smp
%endif

%global perf_make \
  make %{?_smp_mflags} -C tools/perf -s V=1 WERROR=0 HAVE_CPLUS_DEMANGLE=1 prefix=%{_prefix}
%if %{with_perf}
# perf
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch %{ix86}
    cd tools/power/cpupower/debug/i386
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    cd -
%endif
%ifarch x86_64
    cd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    cd -
%endif
%ifarch %{ix86} x86_64
   cd tools/power/x86/x86_energy_perf_policy/
   make
   cd -
   cd tools/power/x86/turbostat
   make
   cd -
%endif #turbostat/x86_energy_perf_policy
%endif
%endif

%if %{with_doc}
# Make the HTML and man pages.
make htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke 'make modules_sign' and the mod-extra-sign.sh
# commands to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.

%if %{with_debuginfo}
%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
  if [ "%{signmodules}" == "1" ]; \
  then \
    if [ "%{with_pae}" != "0" ]; \
    then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}-PAE.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign.PAE .tmp_versions \
      mv signing_key.priv.sign.PAE signing_key.priv \
      mv signing_key.x509.sign.PAE signing_key.x509 \
      make -s ARCH=$Arch V=1 INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_sign KERNELRELEASE=%{KVERREL}.PAE \
      %{SOURCE18} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}.PAE/extra/ \
    fi \
    if [ "%{with_debug}" != "0" ]; \
    then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign.debug .tmp_versions \
      mv signing_key.priv.sign.debug signing_key.priv \
      mv signing_key.x509.sign.debug signing_key.x509 \
      make -s ARCH=$Arch V=1 INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_sign KERNELRELEASE=%{KVERREL}.debug \
      %{SOURCE18} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}.debug/extra/ \
    fi \
    if [ "%{with_pae_debug}" != "0" ]; \
    then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}-PAEdebug.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign.PAEdebug .tmp_versions \
      mv signing_key.priv.sign.PAEdebug signing_key.priv \
      mv signing_key.x509.sign.PAEdebug signing_key.x509 \
      make -s ARCH=$Arch V=1 INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_sign KERNELRELEASE=%{KVERREL}.PAEdebug \
      %{SOURCE18} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}.PAEdebug/extra/ \
    fi \
    if [ "%{with_up}" != "0" ]; \
    then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign .tmp_versions \
      mv signing_key.priv.sign signing_key.priv \
      mv signing_key.x509.sign signing_key.x509 \
      make -s ARCH=$Arch V=1 INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_sign KERNELRELEASE=%{KVERREL} \
      %{SOURCE18} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/extra/ \
    fi \
  fi \
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif
%endif

###
### install
###

%install

cd linux-%{KVERREL}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -h -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check \
     > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch %{ix86}
    cd tools/power/cpupower/debug/i386
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    cd -
%endif
%ifarch x86_64
    cd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    cd -
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   cd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   cd -
   cd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   cd -
%endif #turbostat/x86_energy_perf_policy
%endif

%if %{with_bootwrapper}
make DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif


###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n kernel-tools
/sbin/ldconfig

%postun -n kernel-tools
/sbin/ldconfig
%endif

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
    (cd /usr/src/kernels/%{KVERREL}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
     done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:.%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1}}\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVERREL}%{?-v:.%{-v*}} || exit $?\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*}}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%kernel_variant_preun smp
%kernel_variant_post -v smp

%kernel_variant_preun PAE
%kernel_variant_post -v PAE -r (kernel|kernel-smp)

%kernel_variant_preun debug
%kernel_variant_post -v debug

%kernel_variant_post -v PAEdebug -r (kernel|kernel-smp)
%kernel_variant_preun PAEdebug

%kernel_variant_preun kirkwood
%kernel_variant_post -v kirkwood

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt

%files -n python-perf
%defattr(-,root,root)
%{python_sitearch}

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)

%files -f python-perf-debuginfo.list -n python-perf-debuginfo
%defattr(-,root,root)
%endif
%endif # with_perf

%if %{with_tools}
%files -n kernel-tools -f cpupower.lang
%defattr(-,root,root)
%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%endif

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.0

%files -n kernel-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
%endif # with_perf

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files %{?2}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:.%{2}}\
/%{image_install_path}/.vmlinuz-%{KVERREL}%{?2:.%{2}}.hmac \
%ifarch %{arm}\
/%{image_install_path}/dtb-%{KVERREL}%{?2:.%{2}} \
%endif\
%attr(600,root,root) /boot/System.map-%{KVERREL}%{?2:.%{2}}\
/boot/config-%{KVERREL}%{?2:.%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:.%{2}}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:.%{2}}/build\
/lib/modules/%{KVERREL}%{?2:.%{2}}/source\
/lib/modules/%{KVERREL}%{?2:.%{2}}/updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%{expand:%%files %{?2:%{2}-}modules-extra}\
%defattr(-,root,root)\
/lib/modules/%{KVERREL}%{?2:.%{2}}/extra\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_smp} smp
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} PAE
%kernel_variant_files %{with_pae_debug} PAEdebug
%kernel_variant_files %{with_kirkwood} kirkwood

# plz don't put in a version string unless you're going to tag
# and build.

#  ___________________________________________________________
# / This branch is for Fedora 18. You probably want to commit \
# \ to the F-17 branch instead, or in addition to this one.   /
#  -----------------------------------------------------------
#         \   ^__^
#          \  (@@)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||
%changelog
* Mon Dec 16 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix host lockup in bridge code when starting from virt guest (rhbz 1025770)

* Thu Dec 12 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4587 kvm: out-of-bounds access (rhbz 1030986 1042071)
- CVE-2013-6376 kvm: BUG_ON in apic_cluster_id (rhbz 1033106 1042099)
- CVE-2013-6368 kvm: cross page vapic_addr access (rhbz 1032210 1042090)
- CVE-2013-6367 kvm: division by 0 in apic_get_tmcct (rhbz 1032207 1042081)

* Wed Dec 11 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to support ETPS/2 Elantech touchpads (rhbz 1030802)

* Tue Dec 10 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-XXXX net: memory leak in recvmsg (rhbz 1039845 1039874)

* Tue Dec 03 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to fix rfkill switch on Dell machines (rhbz 958826)

* Sat Nov 30 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-6405 net: leak of uninited mem to userspace via recv syscalls (rhbz 1035875 1035887)

* Fri Nov 29 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.10-100
- Linux v3.11.10
- Fix memory leak in qxl (from Dave Airlie)

* Tue Nov 26 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix usbnet URB handling (rhbz 998342)
- Fix crash in via-velocity driver (rhbz 1022733)
- CVE-2013-6382 xfs: missing check for ZERO_SIZE_PTR (rhbz 1033603 1034670)

* Mon Nov 25 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-6380 aacraid: invalid pointer dereference (rhbz 1033593 1034304)
- CVE-2013-6378 libertas: potential oops in debugfs (rhbz 1033578 1034183)

* Fri Nov 22 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches from Jeff Layton to fix 15sec NFS mount hang

* Wed Nov 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.9-100
- Linux v3.11.9

* Mon Nov 18 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix rhel5.9 KVM guests (rhbz 967652)
- Add patch to fix crash from slab when using md-raid mirrors (rhbz 1031086)
- Add patches from Pierre Ossman to fix 24Hz/24p radeon audio (rhbz 1010679)
- Add patch to fix ALX phy issues after resume (rhbz 1011362)
- Fix ipv6 sit panic with packet size > mtu (from Michele Baldessari) (rbhz 1015905)

* Thu Nov 14 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4563: net: large udp packet over IPv6 over UFO-enabled device with TBF qdisc panic (rhbz 1030015 1030017)

* Wed Nov 13 2013 Justin M. Forbes <jforbes@fedoraproject.org> - 3.11.8-100
- Linux v3.11.8

* Sat Nov 09 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Daniel Stone to avoid high order allocations in evdev
- Add qxl backport fixes from Dave Airlie

* Mon Nov 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.7-100
- Add patch to fix iwlwifi queue settings backtrace (rhbz 1025769)

* Mon Nov 04 2013 Justin M. Forbes <jforbes@fedoraproject.org>
- Linux v3.11.7

* Fri Nov 01 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.6-101
- Revert blocking patches causing systemd to crash on resume (rhbz 1010603)
- CVE-2013-4348 net: deadloop path in skb_flow_dissect (rhbz 1007939 1025647)

* Thu Oct 31 2013 Josh Boyer <jwboyer@fedoraprorject.org>
- Fix display regression on Dell XPS 13 machines (rhbz 995782)

* Tue Oct 29 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix plaintext auth regression in cifs (rhbz 1011621)

* Fri Oct 25 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4470 net: memory corruption with UDP_CORK and UFO (rhbz 1023477 1023495)
- Add touchpad support for Dell XT2 (rhbz 1023413)

* Tue Oct 22 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix warning in tcp_fastretrans_alert (rhbz 989251)

* Fri Oct 18 2013 Justin M. Forbes <jforbes@fedoraproject.org> - 3.11.6-100
- Linux v3.11.6

* Thu Oct 17 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix BusLogic error (rhbz 1015558)
- Fix rt2800usb polling timeouts and throughput issues (rhbz 984696)

* Wed Oct 16 2013 Josh Boyer <jwboyer@fedoraproject.org> 
- Fix btrfs balance/scrub issue (rhbz 1011714)

* Tue Oct 15 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix regression in radeon sound (rhbz 1010679)

* Mon Oct 14 2013 Kyle McMartin <kyle@redhat.com>
- Fix crash-driver.patch to properly use page_is_ram. 

* Mon Oct 14 2013 Justin M. Forbes <jforbes@fedoraproject.org> - 3.11.5-100
- Linux v3.11.5

* Fri Oct 11 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix segfault in cpupower set (rhbz 1000439)

* Thu Oct 10 2013 Justin M. Forbes <jforbes@fedoraproject.org> - 3.11.4-101
- Fix linux-firmware requirement

* Thu Oct 10 2013 Josh Boyer <jwboyer@fedoraproject.org>
- USB OHCI accept very late isochronous URBs (in 3.11.4) (rhbz 975158)
- Fix large order allocation in dm mq policy (rhbz 993744)

* Wed Oct 09 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Don't trigger a stack trace on crashing iwlwifi firmware (rhbz 896695)
- Add patch to fix VFIO IOMMU crash (rhbz 998732)

* Tue Oct 08 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix nouveau crash (rhbz 1015920)

* Tue Oct 08 2013 Justin M. Forbes <jforbes@fedoraproject.org>
- Linux v3.11.4
- Add missing 3.11 patches from F19

* Tue Oct 08 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Quiet irq remapping stack trace (rhbz 982153)
- Use RCU safe kfree for conntrack (rhbz 1015989)

* Fri Oct 4 2013 Justin M. Forbes <jforbes@fedoraproject.org> 3.10.14-100
- Linux v3.10.14

* Thu Oct 3 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4387 ipv6: panic when UFO=On for an interface (rhbz 1011927 1015166)

* Mon Sep 30 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Drop VC_MUTE patch (rhbz 859485)

* Fri Sep 27 2013 Justin M. Forbes <jforbes@fedoraproject.org> 3.10.13-101
- Bump and tag for build

* Fri Sep 27 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add HID revert patch to fix logitech unifying devices (rhbz 1013000)
- Add patches to fix soft lockup from elevator changes (rhbz 902012)

* Fri Sep 27 2013 Justin M. Forbes <jforbes@fedoraproject.org> 3.10.13-100
- Linux v3.10.13

* Mon Sep 23 2013 Neil Horman <nhorman@redhat.com>
- Add alb learning packet config knob (rhbz 971893)

* Fri Sep 20 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix multimedia keys on Genius GX keyboard (rhbz 928561)

* Tue Sep 17 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4345 ansi_cprng: off by one error in non-block size request (rhbz 1007690 1009136)

* Mon Sep 16 2013 Justin M. Forbes <jforbes@fedoraproject.org> 3.10.12-100
- Linux v3.10.12

* Fri Sep 13 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4350 net: sctp: ipv6 ipsec encryption bug in sctp_v6_xmit (rhbz 1007872 1007903)
- CVE-2013-4343 net: use-after-free TUNSETIFF (rhbz 1007733 1007741)

* Thu Sep 12 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Update HID CVE fixes to fix crash from lenovo-tpkbd driver (rhbz 1003998)

* Wed Sep 11 2013 Neil Horman <nhorman@redhat.com>
- Fix race in crypto larval lookup

* Mon Sep 09 2013 Josh Boyer <jwboyer@fedoraproject.org> 3.10.11-100
- Fix system freeze due to incorrect rt2800 initialization (rhbz 1000679)

* Mon Sep 09 2013 Justin M. Forbes <jforbes@fedoraproject.org>
- Linux v3.10.11

* Fri Aug 30 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix HID CVEs.  Absurd.
- CVE-2013-2888 rhbz 1000451 1002543 CVE-2013-2889 rhbz 999890 1002548
- CVE-2013-2891 rhbz 999960 1002555  CVE-2013-2892 rhbz 1000429 1002570
- CVE-2013-2893 rhbz 1000414 1002575 CVE-2013-2894 rhbz 1000137 1002579
- CVE-2013-2895 rhbz 1000360 1002581 CVE-2013-2896 rhbz 1000494 1002594
- CVE-2013-2897 rhbz 1000536 1002600 CVE-2013-2899 rhbz 1000373 1002604

* Thu Aug 29 2013 Justin M. Forbes <jforbes@fedoraproject.org> 3.10.10-100
- Linux v3.10.10

* Wed Aug 28 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add mei patches that fix various s/r issues (rhbz 994824 989373)

* Wed Aug 21 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix brcmsmac oops (rhbz 989269)
- CVE-2013-0343 handling of IPv6 temporary addresses (rhbz 914664 999380)

* Tue Aug 20 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.10.9

* Tue Aug 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.10.8-100
- Linux v3.10.8
- CVE-2013-4254 ARM: perf: NULL pointer dereference in validate_event (rhbz 998878 998881)

* Fri Aug 16 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Nathanael Noblet to fix mic on Gateway LT27 (rhbz 845699)

* Thu Aug 15 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.7-100
- Add patch to fix regression on TeVII S471 devices (rhbz 963715)
- Linux v3.10.7

* Mon Aug 12 2013 Justin M. Forbes <jforbes@redhat.com> 3.10.6-100
- Linux v3.10.6

* Wed Aug 07 2013 Justin M. Forbes <jforbes@redhat.com> 3.10.5-101
- Bump for rebuild after koji hiccup

* Wed Aug 07 2013 Josh Boyer <jwboyer@redhat.com>
- Add zero file length check to make sure pesign didn't fail (rhbz 991808)

* Tue Aug 06 2013 Justin M. Forbes <jforbes@redhat.com> 3.10.5-100
- update s390x config [Dan Horák]

* Mon Aug 05 2013 Justin M. Forbes <jforbes@redhat.com>
- Linux v3.10.5

* Thu Aug  1 2013 Peter Robinson <pbrobinson@fedoraproject.org> - 3.10.4-100
- Rebase ARM config

* Thu Aug 01 2013 Justin M. Forbes <jforbes@redhat.com>
- Update s390x config

* Thu Aug 01 2013 Justin M. Forbes <jforbes@redhat.com>
- Rebase to 3.10.4
  dropped:
   debug-bad-pte-dmi.patch
   debug-bad-pte-modules.patch
   VMX-x86-handle-host-TSC-calibration-failure.patch
   ipv6-ip6_sk_dst_check-must-not-assume-ipv6-dst.patch
   af_key-fix-info-leaks-in-notify-messages.patch
   arm-tegra-fixclk.patch
   vhost-net-fix-use-after-free-in-vhost_net_flush.patch
   0001-drivers-crypto-nx-fix-init-race-alignmasks-and-GCM-b.patch
   i7300_edac_single_mode_fixup.patch
   drivers-hwmon-nct6775.patch
   iwlwifi-pcie-fix-race-in-queue-unmapping.patch
   iwlwifi-pcie-wake-the-queue-if-stopped-when-being-unmapped.patch
   cve-2013-4125.patch
   iwlwifi-add-new-pci-id-for-6x35-series.patch
   ipv6-ip6_append_data_mtu-did-not-care-about-pmtudisc-and_frag_size.patch
   ipv6-call-udp_push_pending_frames-when-uncorking-a-socket-with-AF_INET-pending-data.patch

* Thu Aug 01 2013 Josh Boyer <jwboyer@redhat.com>
- Fix mac80211 connection issues (rhbz 981445)
- Fix firmware issues with iwl4965 and rfkill (rhbz 977053)

* Mon Jul 29 2013 Josh Boyer <jwboyer@redhat.com>
- Add support for elantech v7 devices (rhbz 969473)

* Fri Jul 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix NULL deref in iwlwifi (rhbz 979581)

* Wed Jul 24 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-4162 net: panic while pushing pending data out of a IPv6 socket with UDP_CORK enabled (rhbz 987627 987656)
- CVE-2013-4163 net: panic while appending data to a corked IPv6 socket in ip6_append_data_mtu (rhbz 987633 987639)

* Mon Jul 22 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.11-200
- Fix timer issue in bridge code (rhbz 980254)
- Add patch for iwlwifi 6x35 devices (rhbz 986538)
- Linux v3.9.11

* Fri Jul 19 2013 Dave Jones <davej@redhat.com>
- CVE-2013-4125  ipv6: BUG_ON in fib6_add_rt2node() (rhbz 984664)

* Sat Jul 13 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.10-200
- Linux v3.9.10

* Fri Jul 12 2013 Dave Jones <davej@redhat.com> - 3.9.9-203
- Disable LATENCYTOP/SCHEDSTATS in non-debug builds.

* Fri Jul 12 2013 Josh Boyer <jwboyer@redhat.com>
- Fix various overflow issues in ext4 (rhbz 976837)
- Add iwlwifi fix for connection issue (rhbz 885407)

* Fri Jul 05 2013 Josh Boyer <jwboyer@redhat.com>
- Add report fixup for Genius Gila mouse from Benjamin Tissoires (rhbz 959721)
- Add vhost-net use-after-free fix (rhbz 976789 980643)
- Add fix for timer issue in bridge code (rhbz 980254)
- CVE-2013-2232 ipv6: using ipv4 vs ipv6 structure during routing lookup in sendmsg (rhbz 981552 981564)

* Wed Jul 03 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.9-200
- CVE-2013-1059 libceph: Fix NULL pointer dereference in auth client code (rhbz 977356 980341)
- CVE-2013-2234 net: information leak in AF_KEY notify (rhbz 980995 981007)
- Linux v3.9.9

* Wed Jul 03 2013 Josh Boyer <jwboyer@redhat.com>
- Add patches to fix iwl skb managment (rhbz 977040)

* Thu Jun 27 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.8-200
- Linux v3.9.8

* Thu Jun 27 2013 Josh Boyer <jwboyer@redhat.com>
- Fix stack memory usage for DMA in ath3k (rhbz 977558)

* Wed Jun 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add two patches to fix bridge networking issues (rhbz 880035)

* Mon Jun 24 2013 Josh Boyer <jwboyer@redhat.com>
- Fix battery issue with bluetooth keyboards (rhbz 903741)

* Fri Jun 21 2013 Josh Boyer <jwboyer@redhat.com>
- Add two patches to fix iwlwifi issues in unmapping
- Add patch to fix carl9170 oops (rhbz 967271)

* Thu Jun 20 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.7-200
- Linux v3.9.7

* Wed Jun 19 2013 Mauro Carvalho Chehab
- Add and enable upstream kernel driver for nct6775 sensors

* Tue Jun 18 2013 Dave Jones <davej@redhat.com>
- Disable MTRR sanitizer by default.

* Thu Jun 13 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.6-200
- Linux v3.9.6

* Wed Jun 12 2013 Josh Boyer <jwboyer@redhat.com>
- Fix KVM divide by zero error (rhbz 969644)
- Add fix for rt5390/rt3290 regression (rhbz 950735)

* Tue Jun 11 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.5-201
- Add patches to fix MTRR issues in 3.9.5 (rhbz 973185)
- Add two patches to fix issues with vhost_net and macvlan (rhbz 954181)
- CVE-2013-2164 information leak in cdrom driver (rhbz 973100 973109)

* Mon Jun 10 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.5-200
- Linux v3.9.5

* Fri Jun 07 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2851 block: passing disk names as format strings (rhbz 969515 971662)
- CVE-2013-2852 b43: format string leaking into error msgs (rhbz 969518 971665)

* Thu Jun 06 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2148 fanotify: info leak in copy_event_to_user (rhbz 971258 971261)
- CVE-2013-2147 cpqarray/cciss: information leak via ioctl (rhbz 971242 971249)

* Wed Jun 05 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2140 xen: blkback: insufficient permission checks for BLKIF_OP_DISCARD (rhbz 971146 971148)

* Mon Jun 03 2013 Josh Boyer <jwboyer@redhat.com>
- Fix UEFI anti-bricking code (rhbz 964335)

* Fri May 31 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2850 iscsi-target: heap buffer overflow on large key error (rhbz 968036 969272)

* Fri May 24 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.4-200
- Linux v3.9.4

* Fri May 24 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to quiet irq remapping failures (rhbz 948262)

* Thu May 23 2013 Josh Boyer <jwboyer@redhat.com>
- Fix oops from incorrect rfkill set in hp-wmi (rhbz 964367)

* Wed May 22 2013 Josh Boyer <jwboyer@redhat.com>
- Fix memcmp error in iwlwifi

* Tue May 21 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.3-201
- Fix modules-extra signing with 3.9 kernels (rhbz 965181)

* Mon May 20 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.3-200
- Linux 3.9.3
- Update s390x config

* Thu May 16 2013 Josh Boyer <jwboyer@redhat.com>
- Fix config-local usage (rhbz 950841)

* Mon May 13 2013 Dave Jones <davej@redhat.com> - 3.9.2-200
- Linux 3.9.2

* Fri May 10 2013 Dave Jones <davej@redhat.com> - 3.9.2-0.rc1.200
- Linux 3.9.2-rc1

* Thu May 9 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable PL330 on ARM as it's broken on highbank

* Wed May  8 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add the ARM patches needed for 3.9 :-/

* Wed May 08 2013 Dave Jones <davej@redhat.com> - 3.9.1-200
- Linux 3.9.1

* Wed May 08 2013 Josh Boyer <jwboyer@redhat.com>
- Don't remove headers explicitly exported via UAPI (rhbz 959467)

* Tue May 07 2013 Josh Boyer <jwboyer@redhat.com>
- Fix dmesg_restrict patch to avoid regression (rhbz 952655)

* Mon May 06 2013 Dave Jones <davej@redhat.com> - 3.9.1-0.rc1.201
- Linux 3.9.1-rc1
  merged: wireless-regulatory-fix-channel-disabling-race-condition.patch
  merged: iwlwifi-fix-freeing-uninitialized-pointer.patch

* Mon May 06 2013 Josh Boyer <jwboyer@redhat.com>
- Rebase F18 secure-boot patchset to Linux v3.9

* Mon May  6 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial rebase of ARM to 3.9

* Mon May 06 2013 Dave Jones <davej@redhat.com> - 3.9.0-200
- Rebase to Linux 3.9
  merged: silence-empty-ipi-mask-warning.patch
  merged: quiet-apm.patch
  merged: Input-increase-struct-ps2dev-cmdbuf-to-8-bytes.patch
  merged: Input-add-support-for-Cypress-PS2-Trackpads.patch
  merged: Input-cypress_ps2-fix-trackpadi-found-in-Dell-XPS12.patch
  merged: alps-v2.patch
  merged: userns-avoid-recursion-in-put_user_ns.patch
  merged: amd64_edac_fix_rank_count.patch
  merged: team-net-next-update-20130307.patch
  merged: uvcvideo-suspend-fix.patch
  merged: cfg80211-mac80211-disconnect-on-suspend.patch
  merged: mac80211_fixes_for_ieee80211_do_stop_while_suspend_v3.8.patch
  merged: mac80211-Dont-restart-sta-timer-if-not-running.patch
  merged: 0001-bluetooth-Add-support-for-atheros-04ca-3004-device-t.patch
  TODO: secure-boot
  TODO: ARM configs.

* Wed May 01 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.11-200
- Linux v3.8.11

* Mon Apr 29 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.10-200
- Linux v3.8.10

* Fri Apr 26 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.9-200
- Linux v3.8.9

* Wed Apr 24 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.8-203
- CVE-2013-3228 irda: missing msg_namelen update in irda_recvmsg_dgram (rhbz 956069 956071)
- CVE-2013-3230 l2tp: info leak in l2tp_ip6_recvmsg (rhbz 956088 956089)
- CVE-2013-3231 llc: Fix missing msg_namelen update in llc_ui_recvmsg (rhbz 956094 956104)
- CVE-2013-3232 netrom: information leak via msg_name in nr_recvmsg (rhbz 956110 956113)
- CVE-2013-3233 NFC: llcp: info leaks via msg_name in llcp_sock_recvmsg (rhbz 956125 956129)
- CVE-2013-3234 rose: info leak via msg_name in rose_recvmsg (rhbz 956135 956139)
- CVE-2013-3076 crypto: algif suppress sending src addr info in recvmsg (rhbz 956162 956168)

* Tue Apr 23 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-3223 ax25: information leak via msg_name in ax25_recvmsg (rhbz 955662 955666)
- CVE-2013-3225 Bluetooth: RFCOMM missing msg_namelen update in rfcomm_sock_recvmsg (rhbz 955649 955658)
- CVE-2013-1979 net: incorrect SCM_CREDENTIALS passing (rhbz 955629 955647)
- CVE-2013-3224 Bluetooth: possible info leak in bt_sock_recvmsg (rhbz 955599 955607)

* Mon Apr 22 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-3222 atm: update msg_namelen in vcc_recvmsg (rhbz 955216 955228)

* Wed Apr 17 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.8-202
- Fix missing raid REQ_WRITE_SAME flag commit (rhbz 947539)

* Wed Apr 17 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.8-201
- Linux v3.8.8

* Tue Apr 16 2013 Josh Boyer <jwboyer@redhat.com>
- Fix uninitialized variable free in iwlwifi (rhbz 951241)
- Fix race in regulatory code (rhbz 919176)

* Mon Apr 15 2013 Josh Boyer <jwboyer@redhat.com>
- tracing: NULL pointer dereference (rhbz 952197 952217)
- Fix debug patches to build on s390x/ppc

* Fri Apr 12 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.7-201
- Linux v3.8.7
- Enable CONFIG_LDM_PARTITION (rhbz 948636)

* Thu Apr 11 2013 Dave Jones <davej@redhat.com>
- Print out some extra debug information when we hit bad page tables.

* Thu Apr 11 2013 Josh Boyer <jwboyer@redhat.com>
- Fix ALPS backport patch (rhbz 812111)

* Tue Apr 09 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.6-203
- Temporarily work around pci device assignment issues (rhbz 908888)
- CVE-2013-1929 tg3: len overflow in VPD firmware parsing (rhbz 949932 949946)
- Backport intel brightness quirk for emachines (rhbz 871932)

* Mon Apr  8 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable CMA on ARM tegra
- Minor tweeks to ARM OMAP

* Mon Apr 08 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch from Benjamin Tissoires to fix race in HID magicmouse (rhbz 908604)

* Fri Apr 05 2013 Justin M. Forbes <jforbes@redhat.com>
- Linux v3.8.6

* Wed Apr 03 2013 Dave Jones <davej@redhat.com>
- Enable MTD_CHAR/MTD_BLOCK (Needed for SFC)
  Enable 10gigE on 64-bit only.

* Tue Apr 02 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_FB_MATROX_G on powerpc
- Add support for Atheros 04ca:3004 bluetooth devices (again) (rhbz 844750)
- Enable CONFIG_SCSI_DMX3191D (rhbz 919874)

* Mon Apr 01 2013 Josh Boyer <jwboyer@redhat.com>
- Enable the rtl8192e driver (rhbz 913753)
- Enable CONFIG_MCE_INJECT (rhbz 927353)

* Thu Mar 28 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.5-201
- Linux v3.8.5

* Tue Mar 26 2013 Justin M. Forbes <jforbes@redhat.com>
- Fix child thread introspection of of /proc/self/exe (rhbz 927469)

* Tue Mar 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add quirk for Realtek card reader to avoid 10 sec boot delay (rhbz 806587)
- Add quirk for MSI keyboard backlight to avoid 10 sec boot delay (rhbz 907221)

* Mon Mar 25 2013 Justin M. Forbes <jforbes@redhat.com>
- enable CONFIG_DRM_VMWGFX_FBCON (rhbz 927022)
- disable whci-hcd since it doesnt seem to have users (rhbz 919289)

* Sat Mar 23 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable Marvell Dove support for the moment as it breaks other SoCs

* Thu Mar 21 2013 Josh Boyer <jwboyer@redhat.com>
- Fix workqueue crash in mac80211 (rhbz 920218)

* Thu Mar 21 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates

* Wed Mar 20 2013 Justin M. Forbes <jforbes@redhat.com> 3.8.4-201
- Linux v3.8.4
- CVE-2013-1873 information leaks via netlink interface (rhbz 923652 923662)

* Wed Mar 20 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-1796 kvm: buffer overflow in handling of MSR_KVM_SYSTEM_TIME
  (rhbz 917012 923966)
- CVE-2013-1797 kvm: after free issue with the handling of MSR_KVM_SYSTEM_TIME
  (rhbz 917013 923967)
- CVE-2013-1798 kvm: out-of-bounds access in ioapic indirect register reads
  (rhbz 917017 923968)

* Mon Mar 18 2013 Justin M. Forbes
- Revert rc6 ilk changes from 3.8.3 stable (rhbz 922304)

* Mon Mar 18 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable OMAP RNG and mvebu dove configs

* Fri Mar 15 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-1860 usb: cdc-wdm buf overflow triggered by dev (rhbz 921970 922004) 

* Thu Mar 14 2013 Justin M. Forbes <jforbes@redhat.com> 3.8.3-201
- Linux v3.8.3

* Thu Mar 14 2013 Josh Boyer <jwboyer@redhat.com>
- Fix divide by zero on host TSC calibration failure (rhbz 859282)

* Thu Mar 14 2013 Mauro Carvalho Chehab <mchehab@redhat.com>
- fix i7300_edac twice-mem-size-report via EDAC API (rhbz 921500)

* Tue Mar 12 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix ieee80211_do_stop (rhbz 892599)
- Add patches to fix cfg80211 issues with suspend (rhbz 856863)
- Add patch to fix Cypress trackpad on XPS 12 machines (rhbz 912166)
- CVE-2013-0913 drm/i915: head writing overflow (rhbz 920471 920529)
- CVE-2013-0914 sa_restorer information leak (rhbz 920499 920510)

* Mon Mar 11 2013 Mauro Carvalho Chehab <mchehab@redhat.com>
- fix amd64_edac twice-mem-size-report via EDAC API (rhbz 920586)

* Mon Mar 11 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix usb_submit_urb error in uvcvideo (rhbz 879462)
- Add patch to allow "8250." prefix to keep working (rhbz 911771)
- Add patch to fix w1_search oops (rhbz 857954)
- Add patch to fix broken tty handling (rhbz 904182)

* Fri Mar 08 2013 Josh Boyer <jwboyer@redhat.com>
- Add turbostat and x86_engery_perf_policy debuginfo to kernel-tools-debuginfo

* Fri Mar 08 2013 Justin M. Forbes <jforbes@redhat.com>
- Revert "write backlight harder" until better solution is found (rhbz 917353)
- Update team driver from net-next from Jiri Pirko

* Fri Mar 08 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-1828 sctp: SCTP_GET_ASSOC_STATS stack buffer overflow (rhbz 919315 919316)

* Fri Mar  8 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Have kernel provide kernel-highbank for upgrade to unified
- Update mvebu configs
- Drop unused ARM patches

* Thu Mar 07 2013 Josh Boyer <jwboyer@redhat.com>
- Fix DMI regression (rhbz 916444)
- Fix logitech-dj HID bug from Benjamin Tissoires (rhbz 840391)
- CVE-2013-1792 keys: race condition in install_user_keyrings (rhbz 916646 919021)

* Wed Mar 06 2013 Justin M. Forbes <jforbes@redhat.com>
- Remove Ricoh multifunction DMAR patch as it's no longer needed (rhbz 880051)
- Fix destroy_conntrack GPF (rhbz 859346)

* Wed Mar 06 2013 Josh Boyer <jwboyer@redhat.com>
- Fix regression in secure-boot acpi_rsdp patch (rhbz 906225)
- crypto: info leaks in report API (rhbz 918512 918521)

* Tue Mar  5 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix Beagle (omap), update vexpress

* Tue Mar 05 2013 Josh Boyer <jwboyer@redhat.com>
- Backport 4 fixes for efivarfs (rhbz 917984)
- Enable CONFIG_IP6_NF_TARGET_MASQUERADE

* Mon Mar 04 2013 Josh Boyer <jwboyer@redhat.com>
- Fix issues in nx crypto driver from Kent Yoder (rhbz 916544)

* Mon Mar 04 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.2-201
- Linux v3.8.2

* Mon Mar  4 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix DTB generation on ARM

* Fri Mar 01 2013 Dave Jones <davej@redhat.com>
- Silence "tty is NULL" trace.

* Fri Mar 01 2013 Josh Boyer <jwboyer@redhat.com>
- Add patches to fix sunrpc panic (rhbz 904870)

* Thu Feb 28 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM config for 3.8

* Thu Feb 28 2013 Dave Jones <davej@redhat.com>
- Remove no longer needed E1000 hack.

* Thu Feb 28 2013 Dave Jones <davej@redhat.com>
- Drop SPARC64 support.

* Thu Feb 28 2013 Dave Jones <davej@redhat.com>
- Linux 3.8.1
  Dropped (merged in 3.8.1)
  - drm-i915-lvds-reclock-fix.patch
  - usb-cypress-supertop.patch
  - perf-hists-Fix-period-symbol_conf.field_sep-display.patch
  - ipv6-dst-from-ptr-race.patch
  - sock_diag-Fix-out-of-bounds-access-to-sock_diag_handlers.patch
  - tmpfs-fix-use-after-free-of-mempolicy-object.patch

* Thu Feb 28 2013 Dave Jones <davej@redhat.com>
- Update usb-cypress-supertop.patch

* Wed Feb 27 2013 Dave Jones <davej@redhat.com>
- Update ALPS patch to what got merged in 3.9-rc

* Wed Feb 27 2013 Dave Jones <davej@redhat.com>
- 3.8.0
  Dropped (merged in 3.8)
  - arm-l2x0-only-set-set_debug-on-pl310-r3p0-and-earlier.patch
  - power-x86-destdir.patch
  - modsign-post-KS-jwb.patch
  - efivarfs-3.7.patch
  - handle-efi-roms.patch
  - drm-i915-Fix-up-mismerge-of-3490ea5d-in-3.7.y.patch
  - USB-report-submission-of-active-URBs.patch
  - exec-use-eloop-for-max-recursion-depth.patch
  - 8139cp-revert-set-ring-address-before-enabling-receiver.patch
  - 8139cp-set-ring-address-after-enabling-C-mode.patch
  - 8139cp-re-enable-interrupts-after-tx-timeout.patch
  - brcmsmac-updates-rhbz892428.patch
  - silence-brcmsmac-warning.patch
  - net-fix-infinite-loop-in-__skb_recv_datagram.patch
  - Bluetooth-Add-support-for-Foxconn-Hon-Hai-0489-e056.patch
  - 0001-bluetooth-Add-support-for-atheros-04ca-3004-device-t.patch
  Needs checking:
  - arm-tegra-nvec-kconfig.patch
  - arm-tegra-sdhci-module-fix.patch

* Tue Feb 26 2013 Justin M. Forbes <jforbes@redhat.com>
- Avoid recursion in put_user_ns, potential overflow

* Tue Feb 26 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-1767 tmpfs: fix use-after-free of mempolicy obj (rhbz 915592,915716)
- Fix vmalloc_fault oops during lazy MMU (rhbz 914737)

* Mon Feb 25 2013 Josh Boyer <jwboyer@redhat.com>
- Honor dmesg_restrict for /dev/kmsg (rhbz 903192)

* Sun Feb 24 2013 Josh Boyer <jwboyer@redhat.com> - 3.7.9-205
- CVE-2013-1763 sock_diag: out-of-bounds access to sock_diag_handlers (rhbz 915052,915057)

* Fri Feb 22 2013 Josh Boyer <jwboyer@redhat.com>
- Add support for bluetooth in Acer Aspire S7 (rhbz 879408)

* Thu Feb 21 2013 Neil Horman <nhorman@redhat.com>
- Fix crash from race in ipv6 dst entries (rhbz 892060)

* Wed Feb 20 2013 Josh Boyer <jwboyer@redhat.com>
- Fix perf report field separator issue (rhbz 906055)
- Fix oops from acpi_rsdp setup in secure-boot patchset (rhbz 906225)

* Tue Feb 19 2013 Josh Boyer <jwboyer@redhat.com>
- Add support for Atheros 04ca:3004 bluetooth devices (rhbz 844750)
- Backport support for newer ALPS touchpads (rhbz 812111)

* Tue Feb 19 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix OMAP thermal driver by building it in (seems it doesn't auto load when a module)

* Mon Feb 18 2013 Justin M. Forbes <jforbes@redhat.com> - 3.7.9-201
- Linux v3.7.9

* Mon Feb 18 2013 Adam Jackson <ajax@redhat.com
- i915: Fix a mismerge in 3.7.y that leads to divide-by-zero in i915_update_wm

* Fri Feb 15 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-0290 net: infinite loop in __skb_recv_datagram (rhbz 911479 911473)

* Thu Feb 14 2013 Justin M. Forbes <jforbes@redhat.com> - 3.7.8-201
- Linux v3.7.8

* Thu Feb 14 2013 Adam Jackson <ajax@redhat.com>
- i915: Hush asserts during TV detection, just useless noise
- i915: Fix LVDS downclock to not cripple performance (#901951)

* Thu Feb 14 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix corruption on newer M6116 SATA bridges (rhbz 909591)
- CVE-2013-0228 xen: xen_iret() invalid %ds local DoS (rhbz 910848 906309)

* Tue Feb 12 2013 Dave Jones <davej@redhat.com>
- Add networking queue for next stable release.

* Tue Feb 12 2013 Dave Jones <davej@redhat.com>
- mm: Check if PUD is large when validating a kernel address

* Tue Feb 12 2013 Dave Jones <davej@redhat.com>
- Silence brcmsmac warnings. (Fixed in 3.8, but not backporting to 3.7)

* Tue Feb 12 2013 Justin M. Forbes <jforbes@redhat.com>
- Linux v3.7.7

* Mon Feb 11 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch from Kees Cook to restrict MSR writting in secure boot mode
- Add patch to honor MokSBState (rhbz 907406)

* Thu Feb  7 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM build fixes

* Wed Feb 06 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix ath9k dma stop checks (rhbz 892811)

* Mon Feb 04 2013 Josh Boyer <jwboyer@redhat.com>
- Linux v3.7.6
- Update secure-boot patchset
- Fix rtlwifi scheduling while atomic from Larry Finger (rhbz 903881)

* Tue Jan 29 2013 Josh Boyer <jwboyer@redhat.com>
- Backport driver for Cypress PS/2 trackpad (rhbz 799564)

* Mon Jan 28 2013 Josh Boyer <jwboyer@redhat.com> - 3.7.5-201
- Linux v3.7.5
- Add patch to fix iwlwifi issues (rhbz 863424)

* Sun Jan 27 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Build and package dtbs on ARM
- Enable FB options for qemu vexpress on unified

* Fri Jan 25 2013 Justin M. Forbes <jforbes@redhat.com>
- Turn off THP for 32bit

* Wed Jan 23 2013 Justin M. Forbes <jforbes@redhat.com> - 3.7.4-204
- brcmsmac fixes from upstream (rhbz 892428)

* Wed Jan 23 2013 Dave Jones <davej@redhat.com>
- Remove warnings about empty IPI masks.

* Tue Jan 22 2013 Justin M. Forbes <jforbes@redhat.com> - 3.7.4-203
- Add i915 bugfix from airlied

* Tue Jan 22 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Apply ARM errata fix
- disable HVC_DCC and VIRTIO_CONSOLE on ARM

* Tue Jan 22 2013 Josh Boyer <jwboyer@redhat.com>
- Fix libata settings bug (rhbz 902523)

* Mon Jan 21 2013 Josh Boyer <jwboyer@redhat.com> - 3.7.4-201
- Linux v3.7.4

* Fri Jan 18 2013 Justin M. Forbes <jforbes@redhat.com> 3.7.3-201
- Linux v3.7.3

* Thu Jan 17 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Merge 3.7 ARM kernel including unified kernel
- Drop separate IMX and highbank kernels
- Disable ARM PL310 errata that crash highbank

* Wed Jan 16 2013 Josh Boyer <jwboyer@redhat.com>
- Fix power management sysfs on non-secure boot machines (rhbz 896243)

* Wed Jan 16 2013 Justin M. Forbes <jforbes@redhat.com>  3.7.2-204
- Fix for CVE-2013-0190 xen corruption with 32bit pvops (rhbz 896051 896038)

* Wed Jan 16 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch from Stanislaw Gruszka to fix iwlegacy IBSS cleanup (rhbz 886946)

* Tue Jan 15 2013 Justin M. Forbes <jforbes@redhat.com> 3.7.2-203
- Turn off Intel IOMMU by default
- Stable queue from 3.7.3 with many relevant fixes

* Tue Jan 15 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_DVB_USB_V2 (rhbz 895460)

* Mon Jan 14 2013 Josh Boyer <jwboyer@redhat.com>
- Enable Orinoco drivers in kernel-modules-extra (rhbz 894069)

* Fri Jan 11 2013 Justin M. Forbes <jforbes@redhat.com> 3.7.1-1
- Linux v3.7.2
- Enable Intel IOMMU by default

* Thu Jan 10 2013 Dave Jones <davej@redhat.com>
- Add audit-libs-devel to perf build-deps to enable trace command. (rhbz 892893)

* Tue Jan 08 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix shutdown on some machines (rhbz 890547)

* Mon Jan 07 2013 Josh Boyer <jwboyer@redhat.com>
- Patch to fix efivarfs underflow from Lingzhu Xiang (rhbz 888163)

* Sun Jan 06 2013 Josh Boyer <jwboyer@redhat.com>
- Fix version.h include due to UAPI change in 3.7 (rhbz 892373)

* Fri Jan 04 2013 Josh Boyer <jwboyer@redhat.com>
- Fix oops on aoe module removal (rhbz 853064)

* Thu Jan 03 2013 Josh Boyer <jwboyer@redhat.com> - 3.7.1-2
- Fixup secure boot patchset for 3.7 rebase
- Package bash completion script for perf

* Thu Jan 03 2013 Dave Jones <davej@redhat.com>
- Rebase to 3.7.1

* Wed Jan 02 2013 Josh Boyer <jwboyer@redhat.com>
- Fix autofs issue in 3.6 (rhbz 874372)
- BR the hostname package (rhbz 886113)

* Mon Dec 17 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.11-3
- Linux v3.6.11

* Mon Dec 17 2012 Dennis Gilmore <dennis@ausil.us>
- disable gpiolib on vexpress

* Mon Dec 17 2012 Josh Boyer <jwboyer@redhat.com>
- Fix oops in sony-laptop setup (rhbz 873107)

* Wed Dec 12 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.10-5
- Fix infinite loop in efi signature parser
- Don't error out if db doesn't exist

* Tue Dec 11 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.10-4
- Update secure boot patches to include MoK support
- Fix IBSS scanning in mac80211 (rhbz 883414)

* Tue Dec 11 2012 Justin M. Forbes <jforbes@redhat.com> 3.6.10-1
- Linux 3.6.10

* Wed Dec 05 2012 Dave Jones <davej@redhat.com>
- Team driver updates (Jiri Pirko)

* Mon Dec 03 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.9-2
- Backport 3 upstream fixes to resolve radeon schedule IB errors (rhbz 855275)

* Mon Dec 03 2012 Justin M. Forbes <jforbes@redhat.com> 3.6.9-1
- Linux 3.6.9

* Thu Nov 29 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Update some ARM GPIO and I2C configs

* Tue Nov 27 2012 Josh Boyer <jwboyer@redhat.com>
- Update patches for 8139cp issues from David Woodhouse (rhbz 851278)

* Mon Nov 26 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.8-1
- Linux v3.6.8

* Mon Nov 26 2012 Josh Boyer <jwboyer@redhat.com>
- Fix regression in 8139cp driver, debugged by William J. Eaton (rhbz 851278)
- Fix ACPI video after _DOD errors (rhbz 869383)
- Fix ata command timeout oops in mvsas (rhbz 869629)
- Enable CONFIG_UIO_PDRV on ppc64 (rhbz 878180)
- CVE-2012-4530: stack disclosure binfmt_script load_script (rhbz 868285 880147)

* Tue Nov 20 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.7-5
- CVE-2012-4461: kvm: invalid opcode oops on SET_SREGS with OSXSAVE bit set (rhbz 878518 862900)
- Add VC_MUTE ioctl (rhbz 859485)
- Add support for BCM20702A0 (rhbz 874791)

* Tue Nov 20 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Change the minimum mmap address back to 32768 on ARM systems (thanks to Jon Masters)

* Mon Nov 19 2012 Josh Boyer <jwboyer@redhat.com>
- Apply patches from Jeff Moyer to fix direct-io oops (rhbz 812129)

* Sat Nov 17 2012 Justin M. Forbes <jforbes@linuxtx.org> - 3.6.7-1
- linux 3.6.7

* Fri Nov 16 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.6-9
- Fix oops causing typo in keyspan driver (rhbz 870562)
- Don't WARN_ON empty queues in iwlwifi (rhbz 873001)

* Thu Nov 15 2012 Justin M. Forbes <jforbes@redhat.com>
- Fix panic in  panic in smp_irq_move_cleanup_interrupt (rhbz 869341)

* Wed Nov 14 2012 Josh Boyer <jwboyer@redhat.com>
- Fix module signing of kernel flavours

* Mon Nov 12 2012 Justin M. Forbes <jforbes@redhat.com>
- fix list_del corruption warning on USB audio with twinkle (rhbz 871078)

* Fri Nov 09 2012 Josh Boyer <jwboyer@redhat.com>
- Fix vanilla kernel builds (reported by Thorsten Leemhuis)

* Wed Nov 07 2012 Josh Boyer <jwboyer@redhat.com>
- Add patch to not break modules_install for external module builds

* Mon Nov 05 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.6-3
- Backport efivarfs from efi/next for moktools
- Fix build break without CONFIG_EFI set (reported by Peter W. Bowey)
- Linux v3.6.6

* Mon Nov 05 2012 David Woodhouse <David.Woodhouse@intel.com> - 3.6.5-3
- Fix EFI framebuffer handling

* Wed Oct 31 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.5-2
- Update modsign to what is currently in 3.7-rc2
- Update secure boot support for UEFI cert importing.

* Wed Oct 31 2012 Josh Boyer <jwboyer@redhat.com> - 3.6.5-1
- Linux v3.6.5
- CVE-2012-4565 net: divide by zero in tcp algorithm illinois (rhbz 871848 871923)

* Tue Oct 30 2012 Josh Boyer <jwboyer@redhat.com>
- Move power-x86-destdir.patch to apply on vanilla kernels (thanks knurd)

* Mon Oct 29 2012 Justin M. Forbes <jforbes@redhat.com>
- Uprobes backports from upstream

* Mon Oct 29 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM alignment patch to upstream

* Mon Oct 29 2012 Justin M. Forbes <jforbes@redhat.com> 3.6.4-1
- Linux 3.6.4

* Thu Oct 25 2012 Justin M. Forbes <jforbes@redhat.com>
- CVE-2012-4508: ext4: AIO vs fallocate stale data exposure (rhbz 869904 869909)

* Wed Oct 24 2012 Josh Boyer <jwboyer@redhat.com>
- Remove patch added for rhbz 856863
- Add patch to fix corrupted text with i915 (rhbz 852210)

* Tue Oct 23 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Update OMAP Video config options

* Mon Oct 22 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- VIFO fails on ARM at the moment so disable it for the time being

* Mon Oct 22 2012 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix CIFS oops from Jeff Layton (rhbz 867344)
- CVE-2012-0957: uts: stack memory leak in UNAME26 (rhbz 862877 864824)
- Fix rt2x00 usb reset resume (rhbz 856863)

* Mon Oct 22 2012 Justin M. Forbes <jforbes@linuxtx.org> - 3.6.3-1
- Linux 3.6.3

* Mon Oct 22 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Revert ARM misaligned access check to stop kernel OOPS
- Actually apply highbank sata patch

* Thu Oct 18 2012 Josh Boyer <jwboyer@redhat.com>
- Patch to have mac80211 connect with HT20 if HT40 is not allowed (rhbz 866013)
- Enable VFIO (rhbz 867152)
- Apply patch from Stanislaw Gruszka to fix mac80211 issue (rhbz 862168)
- Apply patch to fix iwlwifi crash (rhbz 770484)

* Tue Oct 16 2012 Mauro Carvalho Chehab <mchehab@redhat.com> - 3.6.2-2
- Fix i82975x_edac OOPS

* Tue Oct 16 2012 Justin M. Forbes <jforbes@redhat.com>
- Enable CONFIG_TCM_VHOST (rhbz 866981)

* Mon Oct 15 2012 Justin M. Forbes <jforbes@redhat.com> 3.6.2-1
- Linux 3.6.2

* Thu Oct 11 2012 Peter Robinson <pbrobinson@fedoraproject.org> 3.6.1-2
- Update ARM config for missing newoption items

* Tue Oct 09 2012 Josh Boyer <jwboyer@redhat.com>
- Drop unhandled irq polling patch

* Mon Oct 08 2012 Justin M. Forbes <jforbes@redhat.com> 3.6.1-1
- Linux 3.6.1

* Sat Oct 06 2012 Josh Boyer <jwboyer@redhat.com>
- secure boot modsign depends on CONFIG_MODULE_SIG not CONFIG_MODULES

* Fri Oct 05 2012 Josh Boyer <jwboyer@redhat.com>
- Adjust secure boot modsign patch

* Fri Oct  5 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Build MMC in on OMAP and Tegra until we work out why modules don't work

* Wed Oct 03 2012 Adam Jackson <ajax@redhat.com>
- Drop vgem patches, not doing anything yet.

* Wed Oct 03 2012 Josh Boyer <jwboyer@redhat.com>
- Make sure kernel-tools-libs-devel provides kernel-tools-devel

* Tue Oct 02 2012 Justin M. Forbes <jforbes@redhat.com> - 3.6.0-2
- Power: Fix VMX fix for memcpy case (rhbz 862420)

* Tue Oct 02 2012 Josh Boyer <jwboyer@redhat.com>
- Patch from David Howells to fix overflow on 32-bit X.509 certs (rhbz 861322)

* Tue Oct  2 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM configs for 3.6 final
- Add highbank SATA driver for stability
- Build in OMAP MMC and DMA drivers to fix borkage for now

* Mon Oct 01 2012 Justin M. Forbes <jforbes@redhat.com> - 3.6.0-1
- Linux 3.6.0
- Disable debugging options.

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
