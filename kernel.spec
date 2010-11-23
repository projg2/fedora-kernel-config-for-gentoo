# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

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
%global baserelease 62
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 2.6.22-rc7-git1 starts with a 2.6.21 base,
# which yields a base_sublevel of 21.
%define base_sublevel 34

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 7
# Is it a -stable RC?
%define stable_rc 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev .%{stable_update}
%define stable_base %{stable_update}
%if 0%{?stable_rc}
# stable RCs are incremental patches, so we need the previous stable patch
%define stable_base %(echo $((%{stable_update} - 1)))
%endif
%endif
%define rpmversion 2.6.%{base_sublevel}%{?stablerev}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 0
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 2.6.%{upstream_sublevel}
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
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-firmware
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
# tools/perf
%define with_perftool  %{?_without_perftool:  0} %{?!_without_perftool:  1}
# perf noarch subpkg
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%if 0%{?released_kernel}
%define doc_build_fail true
%else
%define doc_build_fail true
%endif

%define rawhide_skip_docs 0
%if 0%{?rawhide_skip_docs}
%define with_doc 0
%endif

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# should we do C=1 builds with sparse
%define with_sparse	%{?_with_sparse:      1} %{?!_with_sparse:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# Want to build a vanilla kernel build without any non-upstream patches?
# (well, almost none, we need nonintconfig for build purposes). Default to 0 (off).
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%if 0%{?stable_rc}
%define stable_rctag .rc%{stable_rc}
%endif
%define pkg_release %{fedora_build}%{?stable_rctag}%{?buildid}%{?dist}

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
%define pkg_release 0.%{fedora_build}%{?rctag}%{?gittag}%{?buildid}%{?dist}

%endif

# The kernel tarball/base version
%define kversion 2.6.%{base_sublevel}

%define make_target bzImage

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
%ifarch i686
%define with_pae 1
%else
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_smp 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%endif
%define with_smp 0
%define with_pae 0
%define with_perftool 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64
%endif

# Overrides for generic default options

# only ppc and alphav56 need separate smp kernels
%ifnarch ppc alphaev56
%define with_smp 0
%endif

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_perf 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define all_arch_configs kernel-%{version}-*.config
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
%endif

# bootwrapper is only on ppc
%ifnarch ppc ppc64
%define with_bootwrapper 0
%endif

# sparse blows up on ppc64 alpha and sparc64
%ifarch ppc64 ppc alpha sparc64
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

%ifarch ppc64
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
%endif

%ifarch sparc64
%define asmarch sparc
%define all_arch_configs kernel-%{version}-sparc64*.config
%define make_target image
%define kernel_image arch/sparc/boot/image
%define image_install_path boot
%define with_perftool 0
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

%ifarch ia64
%define all_arch_configs kernel-%{version}-ia64*.config
%define image_install_path boot/efi/EFI/redhat
%define make_target compressed
%define kernel_image vmlinux.gz
%endif

%ifarch alpha alphaev56
%define all_arch_configs kernel-%{version}-alpha*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define hdrarch arm
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%if %{nopatches}
# XXX temporary until last vdso patches are upstream
%define vdso_arches ppc ppc64
%endif

%if %{nopatches}%{using_upstream_branch}
# Ignore unknown options in our config-* files.
# Some options go with patches we're not applying.
%define oldconfig_target loose_nonint_oldconfig
%else
%define oldconfig_target nonint_oldconfig
%endif

# To temporarily exclude an architecture from being built, add it to
# %nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386 s390 sparc %{arm}

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_debuginfo 0
%define with_perftool 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

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
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.10-1
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
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
%if %{with_firmware}\
Requires(pre): kernel-firmware >= %{rpmversion}-%{pkg_release}\
%else\
Requires(pre): linux-firmware >= 20100806-2\
%if %{with_perftool}\
Requires(pre): elfutils-libs\
%endif\
%endif\
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
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 ppc ppc64 ia64 sparc sparc64 s390 s390x alpha alphaev56 %{arm}
ExclusiveOS: Linux

%kernel_reqprovconf
%ifarch x86_64 sparc64
Obsoletes: kernel-smp
%endif


#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
BuildRequires: net-tools
BuildRequires: xmlto, asciidoc
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perftool}
BuildRequires: elfutils-devel zlib-devel binutils-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

%define fancy_debuginfo 0
%if %{with_debuginfo}
%if 0%{?fedora} >= 8 || 0%{?rhel} >= 6
%define fancy_debuginfo 1
%endif
%endif

%if %{fancy_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8.
BuildRequires: rpm-build >= 4.4.2.1-4
%define debuginfo_args --strict-build-id
%endif

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/linux-%{kversion}.tar.bz2

Source11: genkey
Source14: find-provides
Source15: merge.pl

Source20: Makefile.config
Source21: config-debug
Source22: config-nodebug
Source23: config-generic
Source24: config-rhel-generic

Source30: config-x86-generic
Source31: config-i686-PAE

Source40: config-x86_64-generic

Source50: config-powerpc-generic
Source51: config-powerpc32-generic
Source52: config-powerpc32-smp
Source53: config-powerpc64

Source60: config-ia64-generic

Source70: config-s390x

Source90: config-sparc64-generic

Source100: config-arm

Source200: perf

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-2.6.%{base_sublevel}.%{stable_base}.bz2
Patch00: %{stable_patch_00}
%endif
%if 0%{?stable_rc}
%define    stable_patch_01  patch-2.6.%{base_sublevel}.%{stable_update}-rc%{stable_rc}.bz2
Patch01: %{stable_patch_01}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Patch00: patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
Patch01: patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Patch00: patch-2.6.%{base_sublevel}-git%{gitrev}.bz2
%endif
%endif
%endif

%if %{using_upstream_branch}
### BRANCH PATCH ###
%endif

Patch02: git-linus.diff

# we always need nonintconfig, even for -vanilla kernels
Patch03: linux-2.6-build-nonintconfig.patch

# we also need compile fixes for -vanilla
Patch04: linux-2.6-compile-fixes.patch

# build tweak for build ID magic, even for -vanilla
Patch05: linux-2.6-makefile-after_link.patch

%if !%{nopatches}

# revert upstream patches we get via other methods
Patch09: linux-2.6-upstream-reverts.patch
# Git trees.
Patch11: git-bluetooth.patch
Patch12: git-cpufreq.patch

# Standalone patches
Patch20: linux-2.6-hotfixes.patch

Patch21: linux-2.6-tracehook.patch
Patch22: linux-2.6-utrace.patch
Patch23: linux-2.6-utrace-ptrace.patch

Patch50: linux-2.6-x86-cfi_sections.patch

# CVE-2010-3301, CVE-2010-3081
Patch100: 01-compat-make-compat_alloc_user_space-incorporate-the-access_ok-check.patch
Patch101: 02-compat-test-rax-for-the-system-call-number-not-eax.patch
Patch102: 03-compat-retruncate-rax-after-ia32-syscall-entry-tracing.patch
# CVE-2010-3067
Patch103: aio-check-for-multiplication-overflow-in-do_io_submit.patch

Patch144: linux-2.6-vio-modalias.patch

Patch150: linux-2.6.29-sparc-IOC_TYPECHECK.patch

Patch160: linux-2.6-execshield.patch

Patch200: linux-2.6-debug-sizeof-structs.patch
Patch201: linux-2.6-debug-nmi-timeout.patch
Patch202: linux-2.6-debug-taint-vm.patch
Patch203: linux-2.6-debug-vm-would-have-oomkilled.patch
Patch204: linux-2.6-debug-always-inline-kzalloc.patch

Patch300: linux-2.6-driver-level-usb-autosuspend.diff
Patch303: linux-2.6-enable-btusb-autosuspend.patch
Patch304: linux-2.6-usb-uvc-autosuspend.diff
Patch305: linux-2.6-fix-btusb-autosuspend.patch

Patch310: linux-2.6-usb-wwan-update.patch

# disable new features in 2.6.34
Patch370: linux-2.6-defaults-acpi-pci_no_crs.patch
Patch371: linux-2.6-defaults-no-pm-async.patch

Patch380: linux-2.6-defaults-pci_no_msi.patch
# enable ASPM
Patch383: linux-2.6-defaults-aspm.patch
# fixes for ASPM
Patch384: pci-acpi-disable-aspm-if-no-osc.patch
Patch385: pci-aspm-dont-enable-too-early.patch

# 2.6.34 bugfixes
Patch387: pci-fall-back-to-original-bios-bar-addresses.patch

Patch390: linux-2.6-defaults-acpi-video.patch
Patch391: linux-2.6-acpi-video-dos.patch
Patch392: linux-2.6-acpi-video-export-edid.patch
Patch393: acpi-ec-add-delay-before-write.patch

Patch450: linux-2.6-input-kill-stupid-messages.patch
Patch452: linux-2.6.30-no-pcspkr-modalias.patch
Patch453: thinkpad-acpi-add-x100e.patch
Patch454: thinkpad-acpi-fix-backlight.patch

Patch460: linux-2.6-serial-460800.patch

Patch470: die-floppy-die.patch

Patch510: linux-2.6-silence-noise.patch
Patch520: pci-change-error-messages-to-kern-info.patch
Patch530: linux-2.6-silence-fbcon-logo.patch
Patch570: linux-2.6-selinux-mprotect-checks.patch
Patch580: linux-2.6-sparc-selinux-mprotect-checks.patch

Patch610: hda_intel-prealloc-4mb-dmabuffer.patch

Patch690: iwlwifi-add-internal-short-scan-support-for-3945.patch
Patch692: iwlwifi-move-plcp-check-to-separated-function.patch
Patch693: iwlwifi-Recover-TX-flow-failure.patch
Patch694: iwlwifi-code-cleanup-for-connectivity-recovery.patch
Patch695: iwlwifi-iwl_good_ack_health-only-apply-to-AGN-device.patch

Patch800: linux-2.6-crash-driver.patch

Patch900: linux-2.6-cantiga-iommu-gfx.patch

# crypto/
Patch1200: crypto-add-async-hash-testing.patch

Patch1515: lirc-2.6.33.patch
Patch1517: hdpvr-ir-enable.patch

# virt + ksm patches
Patch1550: virtqueue-wrappers.patch
Patch1554: virt_console-rollup.patch
Patch1555: fix_xen_guest_on_old_EC2.patch

# DRM
Patch1800: drm-next.patch
Patch1801: drm-revert-drm-fbdev-rework-output-polling-to-be-back-in-core.patch
Patch1802: revert-drm-kms-toggle-poll-around-switcheroo.patch
Patch1803: drm-encoder-disable.patch
# nouveau + drm fixes
Patch1815: drm-nouveau-updates.patch
Patch1816: drm-nouveau-race-fix.patch
Patch1817: drm-nouveau-nva3-noaccel.patch
Patch1818: drm-nouveau-nv50-crtc-update-delay.patch
Patch1819: drm-intel-big-hammer.patch
# intel drm is all merged upstream
Patch1820: drm-i915-fix-edp-panels.patch
Patch1821: i915-fix-crt-hotplug-regression.patch
Patch1824: drm-intel-next.patch
# make sure the lvds comes back on lid open
Patch1825: drm-intel-make-lvds-work.patch
Patch1826: drm-radeon-resume-fixes.patch
Patch1830: drm-i915-explosion-following-oom-in-do_execbuffer.patch
Patch1900: linux-2.6-intel-iommu-igfx.patch
Patch1901: drm-nouveau-acpi-edid-fix.patch
Patch1902: agp-intel-use-the-correct-mask-to-detect-i830-aperture-size.patch
Patch1903: drm-nouveau-pusher-intr.patch
Patch1904: drm-nouveau-ibdma-race.patch
# radeon

# linux1394 git patches
Patch2200: linux-2.6-firewire-git-update.patch
Patch2201: linux-2.6-firewire-git-pending.patch

Patch2400: linux-2.6-phylib-autoload.patch

# Quiet boot fixes
# silence the ACPI blacklist code
Patch2802: linux-2.6-silence-acpi-blacklist.patch

Patch2899: linux-2.6-v4l-dvb-fixes.patch
Patch2900: linux-2.6-v4l-dvb-update.patch
Patch2901: linux-2.6-v4l-dvb-experimental.patch
Patch2905: linux-2.6-v4l-dvb-gspca-fixes.patch
Patch2906: linux-2.6-v4l-dvb-uvcvideo-update.patch

Patch2910: linux-2.6-v4l-dvb-add-lgdt3304-support.patch
Patch2911: linux-2.6-v4l-dvb-add-kworld-a340-support.patch

# fs fixes

Patch3012: btrfs-prohibit-a-operation-of-changing-acls-mask-when-noacl-mount-option-is-used.patch


# NFSv4

# VIA Nano / VX8xx updates

# patches headed upstream
Patch12005: linux-2.6-input-hid-quirk-egalax.patch

Patch12015: add-appleir-usb-driver.patch
Patch12016: disable-i8042-check-on-apple-mac.patch

Patch12017: prevent-runtime-conntrack-changes.patch

Patch12018: neuter_intel_microcode_load.patch

Patch12019: linux-2.6-umh-refactor.patch

Patch12030: ssb_check_for_sprom.patch

Patch12035: quiet-prove_RCU-in-cgroups.patch

Patch12040: iwlwifi-manage-QoS-by-mac-stack.patch
Patch12042: mac80211-explicitly-disable-enable-QoS.patch

Patch12250: inotify-fix-inotify-oneshot-support.patch
Patch12260: inotify-send-IN_UNMOUNT-events.patch

Patch12270: kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch

Patch12400: input-synaptics-relax-capability-id-checks-on-new-hardware.patch

Patch12410: cifs-fix-dns-resolver.patch
Patch12430: cred-dont-resurrect-dead-credentials.patch

Patch12440: direct-io-move-aio_complete-into-end_io.patch
Patch12450: ext4-move-aio-completion-after-unwritten-extent-conversion.patch
Patch12460: xfs-move-aio-completion-after-unwritten-extent-conversion.patch

Patch12470: drivers-hwmon-coretemp-c-detect-the-thermal-sensors-by-cpuid.patch
Patch12480: kprobes-x86-fix-kprobes-to-skip-prefixes-correctly.patch

Patch12490: dell-wmi-add-support-for-eject-key.patch
Patch12500: irda-correctly-clean-up-self-ias_obj-on-irda_bind-failure.patch
Patch12510: wireless-extensions-fix-kernel-heap-content-leak.patch

Patch12517: flexcop-fix-xlate_proc_name-warning.patch

Patch12520: acpi-ec-pm-fix-race-between-ec-transactions-and-system-suspend.patch
Patch12521: nfs-fix-an-oops-in-the-nfsv4-atomic-open-code.patch
Patch12522: keys-fix-bug-in-keyctl-session-to-parent-if-parent-has-no-session-keyring.patch
Patch12523: keys-fix-rcu-no-lock-warning-in-keyctl-session-to-parent.patch

Patch12530: pci-msi-remove-unsafe-and-unnecessary-hardware-access.patch
Patch12531: pci-msi-restore-read_msi_msg_desc-add-get_cached_msi_msg_desc.patch

Patch12532: x86-tsc-sched-recompute-cyc2ns_offset-s-during-resume-from-sleep-states.patch
# fix bug caused by above patch
Patch12533: x86-tsc-fix-a-preemption-leak-in-restore_sched_clock_state.patch

# Mitigate DOS with large argument lists.
Patch12540: execve-improve-interactivity-with-large-arguments.patch
Patch12541: execve-make-responsive-to-sigkill-with-large-arguments.patch
Patch12542: setup_arg_pages-diagnose-excessive-argument-size.patch

# CVE-2010-3080
Patch12550: alsa-seq-oss-fix-double-free-at-error-path-of-snd_seq_oss_open.patch

# CVE-2010-3079
Patch12560: tracing-do-not-allow-llseek-to-set_ftrace_filter.patch

Patch12570: sched-00-fix-user-time-incorrectly-accounted-as-system-time-on-32-bit.patch

# bz 636534
Patch12580: xen-handle-events-as-edge-triggered.patch
Patch12581: xen-use-percpu-interrupts-for-ipis-and-virqs.patch

# CVE-2010-3432
Patch12590: sctp-do-not-reset-the-packet-during-sctp_packet_config.patch

#Bonding sysfs WARN_ON (bz 604630)
Patch12591: linux-2.6-bonding-sysfs-warning.patch

#twsock rcu warning fix (bz 642905)
Patch12592: linux-2.6-twsock-rcu-lockdep-warn.patch

Patch13635: r8169-fix-dma-allocations.patch
Patch13636: skge-quirk-to-4gb-dma.patch

Patch13637: dmar-disable-when-ricoh-multifunction.patch

Patch13640: mmc-SDHCI_INT_DATA_MASK-typo-error.patch
Patch13641: mmc-add-ricoh-e822-pci-id.patch
Patch13642: mmc-make-sdhci-work-with-ricoh-mmc-controller.patch
Patch13643: sdhci-8-bit-data-transfer-width-support.patch

Patch13645: depessimize-rds_copy_page_user.patch
Patch13646: tpm-autodetect-itpm-devices.patch

Patch13647: rt2x00-disable-auto-wakeup-before-waking-up-device.patch
Patch13648: rt2x00-fix-failed-SLEEP-AWAKE-and-AWAKE-SLEEP-transitions.patch

Patch13700: ipc-zero-struct-memory-for-compat-fns.patch
Patch13701: ipc-shm-fix-information-leak-to-user.patch

Patch13702: inet_diag-make-sure-we-run-the-same-bytecode-we-audited.patch

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
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package firmware
Summary: Firmware files used by the Linux kernel
Group: Development/System
# This is... complicated.
# Look at the WHENCE file.
License: GPL+ and GPLv2+ and MIT and Redistributable, no modification permitted
%if "x%{?variant}" != "x"
Provides: kernel-firmware = %{rpmversion}-%{pkg_release}
%endif
%description firmware
Kernel-firmware includes firmware files required for some devices to
operate.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package provides the supporting documentation for the perf tool
shipped in each kernel image subpackage.

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
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
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
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
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
  if ! egrep "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:10}" != "patch-2.6." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
%endif
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
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

# we don't want a .config file when building firmware: it just confuses the build system
%define build_firmware \
   mv .config .config.firmware_save \
   make INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware firmware_install \
   mv .config.firmware_save .config

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 2.6.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 2.6.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 2.6.%{base_sublevel}
%endif
%endif
%endif

# %{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%{kversion}%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-2.6.*' \
            | grep -x -v "$PWD"/kernel-%{kversion}%{?dist}) ||:

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
    ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
    ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    ApplyPatch patch-2.6.%{base_sublevel}-git%{gitrev}.bz2
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
if [ -d linux-%{kversion}.%{_target_cpu} ]; then
  # Just in case we ctrl-c'd a prep already
  rm -rf deleteme.%{_target_cpu}
  # Move away the stale away, and delete in background.
  mv linux-%{kversion}.%{_target_cpu} deleteme.%{_target_cpu}
  rm -rf deleteme.%{_target_cpu} &
fi

cp -rl vanilla-%{vanillaversion} linux-%{kversion}.%{_target_cpu}

cd linux-%{kversion}.%{_target_cpu}

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

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE20} VERSION=%{version} configs

#if a rhel kernel, apply the rhel config options
%if 0%{?rhel}
  for i in %{all_arch_configs}
  do
    mv $i $i.tmp
    ./merge.pl config-rhel-generic $i.tmp > $i
    rm $i.tmp
  done
%endif

ApplyOptionalPatch git-linus.diff

# This patch adds a "make nonint_oldconfig" which is non-interactive and
# also gives a list of missing options at the end. Useful for automated
# builds (as used in the buildsystem).
ApplyPatch linux-2.6-build-nonintconfig.patch

ApplyPatch linux-2.6-makefile-after_link.patch

#
# misc small stuff to make things compile
#
ApplyOptionalPatch linux-2.6-compile-fixes.patch

%if !%{nopatches}

# revert patches from upstream that conflict or that we get via other means
ApplyOptionalPatch linux-2.6-upstream-reverts.patch -R

ApplyOptionalPatch git-bluetooth.patch
ApplyOptionalPatch git-cpufreq.patch

ApplyPatch linux-2.6-hotfixes.patch

# Roland's utrace ptrace replacement.
ApplyPatch linux-2.6-tracehook.patch
ApplyPatch linux-2.6-utrace.patch
ApplyPatch linux-2.6-utrace-ptrace.patch

# Architecture patches
# x86(-64)
ApplyPatch linux-2.6-x86-cfi_sections.patch

# CVE-2010-3301, CVE-2010-3081
ApplyPatch 01-compat-make-compat_alloc_user_space-incorporate-the-access_ok-check.patch
ApplyPatch 02-compat-test-rax-for-the-system-call-number-not-eax.patch
ApplyPatch 03-compat-retruncate-rax-after-ia32-syscall-entry-tracing.patch

#
# Intel IOMMU
#

#
# PowerPC
#
# Provide modalias in sysfs for vio devices
ApplyPatch linux-2.6-vio-modalias.patch

#
# SPARC64
#
ApplyPatch linux-2.6.29-sparc-IOC_TYPECHECK.patch

#
# Exec shield
#
ApplyPatch linux-2.6-execshield.patch

#
# bugfixes to drivers and filesystems
#
ApplyPatch aio-check-for-multiplication-overflow-in-do_io_submit.patch

# ext4

# xfs

# btrfs
ApplyPatch btrfs-prohibit-a-operation-of-changing-acls-mask-when-noacl-mount-option-is-used.patch


# eCryptfs

# NFSv4

# USB
#ApplyPatch linux-2.6-driver-level-usb-autosuspend.diff
#ApplyPatch linux-2.6-enable-btusb-autosuspend.patch
#ApplyPatch linux-2.6-usb-uvc-autosuspend.diff
#ApplyPatch linux-2.6-fix-btusb-autosuspend.patch
ApplyPatch linux-2.6-usb-wwan-update.patch

# WMI

# ACPI
ApplyPatch linux-2.6-defaults-acpi-video.patch
ApplyPatch linux-2.6-acpi-video-dos.patch
ApplyPatch linux-2.6-acpi-video-export-edid.patch
ApplyPatch acpi-ec-add-delay-before-write.patch

# Various low-impact patches to aid debugging.
ApplyPatch linux-2.6-debug-sizeof-structs.patch
ApplyPatch linux-2.6-debug-nmi-timeout.patch
ApplyPatch linux-2.6-debug-taint-vm.patch
ApplyPatch linux-2.6-debug-vm-would-have-oomkilled.patch
ApplyPatch linux-2.6-debug-always-inline-kzalloc.patch

#
# PCI / PM
#

# new 2.6.34 options
# default to async suspend disabled
ApplyPatch linux-2.6-defaults-no-pm-async.patch
# default to pci=nocrs
ApplyPatch linux-2.6-defaults-acpi-pci_no_crs.patch

# make default state of PCI MSI a config option
ApplyPatch linux-2.6-defaults-pci_no_msi.patch

# enable ASPM by default on hardware we expect to work
ApplyPatch linux-2.6-defaults-aspm.patch
# disable aspm if acpi doesn't provide an _OSC method
ApplyPatch pci-acpi-disable-aspm-if-no-osc.patch
# allow drivers to disable aspm at load time
ApplyPatch pci-aspm-dont-enable-too-early.patch
# fall back to original BIOS address when reassignment fails (KORG#16263)
ApplyPatch pci-fall-back-to-original-bios-bar-addresses.patch

#
# SCSI Bits.
#

# ACPI

# ALSA
ApplyPatch hda_intel-prealloc-4mb-dmabuffer.patch

# Networking

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch linux-2.6-input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

ApplyPatch linux-2.6.30-no-pcspkr-modalias.patch

ApplyPatch linux-2.6-input-hid-quirk-egalax.patch
ApplyPatch thinkpad-acpi-add-x100e.patch
ApplyPatch thinkpad-acpi-fix-backlight.patch

# Allow to use 480600 baud on 16C950 UARTs
ApplyPatch linux-2.6-serial-460800.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch linux-2.6-silence-noise.patch
ApplyPatch pci-change-error-messages-to-kern-info.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch linux-2.6-silence-fbcon-logo.patch

# Fix the SELinux mprotect checks on executable mappings
#ApplyPatch linux-2.6-selinux-mprotect-checks.patch
# Fix SELinux for sparc
# FIXME: Can we drop this now? See updated linux-2.6-selinux-mprotect-checks.patch
#ApplyPatch linux-2.6-sparc-selinux-mprotect-checks.patch

# Changes to upstream defaults.

# /dev/crash driver.
ApplyPatch linux-2.6-crash-driver.patch

# Cantiga chipset b0rkage
ApplyPatch linux-2.6-cantiga-iommu-gfx.patch

# crypto/

# Add async hash testing (a8f1a05)
ApplyPatch crypto-add-async-hash-testing.patch

# http://www.lirc.org/
ApplyPatch lirc-2.6.33.patch
# enable IR receiver on Hauppauge HD PVR (v4l-dvb merge pending)
ApplyPatch hdpvr-ir-enable.patch

# Assorted Virt Fixes
ApplyPatch virtqueue-wrappers.patch
ApplyPatch virt_console-rollup.patch
ApplyPatch fix_xen_guest_on_old_EC2.patch

ApplyPatch drm-next.patch
ApplyPatch drm-revert-drm-fbdev-rework-output-polling-to-be-back-in-core.patch
ApplyPatch revert-drm-kms-toggle-poll-around-switcheroo.patch
ApplyPatch drm-i915-fix-edp-panels.patch
ApplyPatch i915-fix-crt-hotplug-regression.patch
ApplyPatch drm-encoder-disable.patch

# Nouveau DRM + drm fixes
ApplyPatch drm-nouveau-updates.patch
ApplyPatch drm-nouveau-race-fix.patch
ApplyPatch drm-nouveau-nva3-noaccel.patch
ApplyPatch drm-nouveau-nv50-crtc-update-delay.patch
ApplyPatch drm-nouveau-acpi-edid-fix.patch
ApplyPatch drm-nouveau-pusher-intr.patch
ApplyPatch drm-nouveau-ibdma-race.patch

ApplyPatch drm-intel-big-hammer.patch
ApplyOptionalPatch drm-intel-next.patch
ApplyPatch drm-intel-make-lvds-work.patch
ApplyPatch drm-i915-explosion-following-oom-in-do_execbuffer.patch
# broken in 2.6.35-rc2, fixed in 2.6.35, but our drm-next snapshot has the bug
ApplyPatch agp-intel-use-the-correct-mask-to-detect-i830-aperture-size.patch

ApplyPatch drm-radeon-resume-fixes.patch
ApplyPatch linux-2.6-intel-iommu-igfx.patch

# linux1394 git patches
ApplyOptionalPatch linux-2.6-firewire-git-update.patch
ApplyOptionalPatch linux-2.6-firewire-git-pending.patch

# silence the ACPI blacklist code
ApplyPatch linux-2.6-silence-acpi-blacklist.patch

# V4L/DVB updates/fixes/experimental drivers
#  apply if non-empty
ApplyOptionalPatch linux-2.6-v4l-dvb-fixes.patch
ApplyOptionalPatch linux-2.6-v4l-dvb-update.patch
ApplyOptionalPatch linux-2.6-v4l-dvb-experimental.patch

ApplyPatch linux-2.6-v4l-dvb-gspca-fixes.patch
ApplyPatch linux-2.6-v4l-dvb-uvcvideo-update.patch

ApplyPatch linux-2.6-v4l-dvb-add-lgdt3304-support.patch
ApplyPatch linux-2.6-v4l-dvb-add-kworld-a340-support.patch

ApplyPatch linux-2.6-phylib-autoload.patch

# Patches headed upstream
ApplyPatch add-appleir-usb-driver.patch
ApplyPatch disable-i8042-check-on-apple-mac.patch

ApplyPatch neuter_intel_microcode_load.patch

# Refactor UserModeHelper code & satisfy abrt recursion check request
ApplyPatch linux-2.6-umh-refactor.patch

# rhbz#533746
# awful, ugly conflicts between this patch and the 2.6.34.2 patch:
# ssb-handle-netbook-devices-where-the-sprom-address-is-changed.patch
#ApplyPatch ssb_check_for_sprom.patch

# iwlwifi fixes from F-13-2.6.33
ApplyPatch iwlwifi-add-internal-short-scan-support-for-3945.patch
ApplyPatch iwlwifi-move-plcp-check-to-separated-function.patch
ApplyPatch iwlwifi-Recover-TX-flow-failure.patch
ApplyPatch iwlwifi-code-cleanup-for-connectivity-recovery.patch
ApplyPatch iwlwifi-iwl_good_ack_health-only-apply-to-AGN-device.patch

# mac80211/iwlwifi fix connections to some APs (rhbz#558002)
ApplyPatch mac80211-explicitly-disable-enable-QoS.patch
ApplyPatch iwlwifi-manage-QoS-by-mac-stack.patch

ApplyPatch quiet-prove_RCU-in-cgroups.patch

# fix broken oneshot support and missing umount events (#607327)
ApplyPatch inotify-fix-inotify-oneshot-support.patch
ApplyPatch inotify-send-IN_UNMOUNT-events.patch

# 610911
ApplyPatch kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch

# fix newer synaptics touchpads not being recognized
ApplyPatch input-synaptics-relax-capability-id-checks-on-new-hardware.patch

# Remove __init and __exit attributes from resolver code
ApplyPatch cifs-fix-dns-resolver.patch

# RHBZ #591015
ApplyPatch cred-dont-resurrect-dead-credentials.patch

# RHBZ #617699
ApplyPatch direct-io-move-aio_complete-into-end_io.patch
ApplyPatch ext4-move-aio-completion-after-unwritten-extent-conversion.patch
ApplyPatch xfs-move-aio-completion-after-unwritten-extent-conversion.patch

# bz #625734
ApplyPatch drivers-hwmon-coretemp-c-detect-the-thermal-sensors-by-cpuid.patch

# bz #610941
ApplyPatch kprobes-x86-fix-kprobes-to-skip-prefixes-correctly.patch

# bz #513530
ApplyPatch dell-wmi-add-support-for-eject-key.patch

# cve-2010-2954
ApplyPatch irda-correctly-clean-up-self-ias_obj-on-irda_bind-failure.patch

# cve-2010-2955
ApplyPatch wireless-extensions-fix-kernel-heap-content-leak.patch

# bz #575873
ApplyPatch flexcop-fix-xlate_proc_name-warning.patch

# another fix for suspend/resume bugs
ApplyPatch acpi-ec-pm-fix-race-between-ec-transactions-and-system-suspend.patch

# this went in 2.6.35-stable
ApplyPatch nfs-fix-an-oops-in-the-nfsv4-atomic-open-code.patch

# CVE-2010-2960
ApplyPatch keys-fix-bug-in-keyctl-session-to-parent-if-parent-has-no-session-keyring.patch
ApplyPatch keys-fix-rcu-no-lock-warning-in-keyctl-session-to-parent.patch

# more suspend/resume fixes form 2.6.32 / 2.6.35 queue
# Fix unsafe access to MSI registers during suspend
ApplyPatch pci-msi-remove-unsafe-and-unnecessary-hardware-access.patch
ApplyPatch pci-msi-restore-read_msi_msg_desc-add-get_cached_msi_msg_desc.patch
# Fix scheduler load balancing after suspend/resume cycle
ApplyPatch x86-tsc-sched-recompute-cyc2ns_offset-s-during-resume-from-sleep-states.patch
# fix bug caused by above patch
ApplyPatch x86-tsc-fix-a-preemption-leak-in-restore_sched_clock_state.patch

# Mitigate DOS with large argument lists.
ApplyPatch execve-improve-interactivity-with-large-arguments.patch
ApplyPatch execve-make-responsive-to-sigkill-with-large-arguments.patch
ApplyPatch setup_arg_pages-diagnose-excessive-argument-size.patch

# CVE-2010-3080
ApplyPatch alsa-seq-oss-fix-double-free-at-error-path-of-snd_seq_oss_open.patch

# CVE-2010-3079
ApplyPatch tracing-do-not-allow-llseek-to-set_ftrace_filter.patch

# BZ 633037
ApplyPatch sched-00-fix-user-time-incorrectly-accounted-as-system-time-on-32-bit.patch

# BZ 636534
ApplyPatch xen-handle-events-as-edge-triggered.patch
ApplyPatch xen-use-percpu-interrupts-for-ipis-and-virqs.patch

# CVE-2010-3432
ApplyPatch sctp-do-not-reset-the-packet-during-sctp_packet_config.patch

# BZ 604630
ApplyPatch linux-2.6-bonding-sysfs-warning.patch

# BZ 642905
ApplyPatch linux-2.6-twsock-rcu-lockdep-warn.patch

# rhbz#629158
ApplyPatch r8169-fix-dma-allocations.patch
# rhbz#447489
ApplyPatch skge-quirk-to-4gb-dma.patch

# rhbz#605888
ApplyPatch dmar-disable-when-ricoh-multifunction.patch

ApplyPatch mmc-SDHCI_INT_DATA_MASK-typo-error.patch
ApplyPatch sdhci-8-bit-data-transfer-width-support.patch
ApplyPatch mmc-make-sdhci-work-with-ricoh-mmc-controller.patch
ApplyPatch mmc-add-ricoh-e822-pci-id.patch

ApplyPatch depessimize-rds_copy_page_user.patch
ApplyPatch tpm-autodetect-itpm-devices.patch

ApplyPatch rt2x00-disable-auto-wakeup-before-waking-up-device.patch
ApplyPatch rt2x00-fix-failed-SLEEP-AWAKE-and-AWAKE-SLEEP-transitions.patch

# rhbz#648658 (CVE-2010-4073)
ApplyPatch ipc-zero-struct-memory-for-compat-fns.patch

# rhbz#648656 (CVE-2010-4072)
ApplyPatch ipc-shm-fix-information-leak-to-user.patch

# rhbz#651264 (CVE-2010-3880)
ApplyPatch inet_diag-make-sure-we-run-the-same-bytecode-we-audited.patch

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

# Remove configs not for the buildarch
for cfg in kernel-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch %{oldconfig_target} > /dev/null
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{fancy_debuginfo}
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

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = %{?stablerev}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # if pre-rc1 devel kernel, must fix up SUBLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^SUBLEVEL.*/SUBLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch %{oldconfig_target} > /dev/null
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags}
    make -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

%if %{with_perftool}
    pushd tools/perf
# make sure the scripts are executable... won't be in tarball until 2.6.31 :/
    chmod +x util/generate-cmdlist.sh util/PERF-VERSION-GEN
    make -s V=1 NO_DEMANGLE=1 %{?_smp_mflags} perf
    mkdir -p $RPM_BUILD_ROOT/usr/libexec/
    install -m 755 perf $RPM_BUILD_ROOT/usr/libexec/perf.$KernelVer
    popd
%endif

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
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # We'll do that ourselves with 'make firmware_install'
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
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
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
%ifarch ppc
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** WARNING *** no vmlinux build ID! ***"
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    fgrep /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register'
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

    egrep -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot

cd linux-%{kversion}.%{_target_cpu}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image PAEdebug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image PAE
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_smp}
BuildKernel %make_target %kernel_image smp
%endif

%if %{with_doc}
# Make the HTML and man pages.
make %{?_smp_mflags} htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

%if %{with_perf}
pushd tools/perf
make %{?_smp_mflags} man || %{doc_build_fail}
popd
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{fancy_debuginfo}
%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

%if %{with_debuginfo}
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

cd linux-%{kversion}.%{_target_cpu}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

# perf docs
%if %{with_perf}
mandir=$RPM_BUILD_ROOT%{_datadir}/man
man1dir=$mandir/man1
pushd tools/perf/Documentation
make install-man mandir=$mandir
popd

pushd $man1dir
for d in *.1; do
 gzip $d;
done
popd
%endif # with_perf

# perf shell wrapper
%if %{with_perf}
mkdir -p $RPM_BUILD_ROOT/usr/sbin/
cp $RPM_SOURCE_DIR/perf $RPM_BUILD_ROOT/usr/sbin/perf
chmod 0755 $RPM_BUILD_ROOT/usr/sbin/perf
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/perf
%endif

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

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_firmware}
%{build_firmware}
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
#if [ -x /sbin/weak-modules ]\
#then\
#    /sbin/weak-modules --add-kernel %{KVERREL}%{?-v*} || exit $?\
#fi\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
#if [ -x /sbin/weak-modules ]\
#then\
#    /sbin/weak-modules --remove-kernel %{KVERREL}%{?1} || exit $?\
#fi\
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

%if %{with_firmware}
%files firmware
%defattr(-,root,root)
/lib/firmware/*
%doc linux-%{kversion}.%{_target_cpu}/firmware/WHENCE
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
%{_datadir}/doc/perf
/usr/sbin/perf
%{_datadir}/man/man1/*
%endif

# This is %{image_install_path} on an arch where that includes ELF files,
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
/boot/System.map-%{KVERREL}%{?2:.%{2}}\
%if %{with_perftool}\
/usr/libexec/perf.%{KVERREL}%{?2:.%{2}}\
%endif\
#/boot/symvers-%{KVERREL}%{?2:.%{2}}.gz\
/boot/config-%{KVERREL}%{?2:.%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:.%{2}}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:.%{2}}/build\
/lib/modules/%{KVERREL}%{?2:.%{2}}/source\
/lib/modules/%{KVERREL}%{?2:.%{2}}/extra\
/lib/modules/%{KVERREL}%{?2:.%{2}}/updates\
/lib/modules/%{KVERREL}%{?2:.%{2}}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
%verify(not mtime) /usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%if %{fancy_debuginfo}\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%else\
%{expand:%%files %{?2:%{2}-}debuginfo}\
%endif\
%defattr(-,root,root)\
%if !%{fancy_debuginfo}\
%if "%{elf_image_install_path}" != ""\
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}%{?2:.%{2}}.debug\
%endif\
%{debuginfodir}/lib/modules/%{KVERREL}%{?2:.%{2}}\
%{debuginfodir}/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%endif\
%endif\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_smp} smp
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} PAE
%kernel_variant_files %{with_pae_debug} PAEdebug


%changelog
* Tue Nov 23 2010 Kyle McMartin <kyle@redhat.com>
- zero struct memory in ipc compat (CVE-2010-4073) (#648658)
- zero struct memory in ipc shm (CVE-2010-4072) (#648656)
- fix logic error in INET_DIAG bytecode auditing (CVE-2010-3880) (#651264)

* Fri Oct 22 2010 Kyle McMartin <kyle@redhat.cmo> 2.6.34.7-62
- tpm-autodetect-itpm-devices.patch: Auto-fix TPM issues on various
  laptops which prevented suspend/resume.
- depessimize-rds_copy_page_user.patch: Fix CVE-2010-3904, local
  privilege escalation via RDS protocol.
- rt2x00: Backport fixes for #642031 from Stanislaw Gruszka.

* Mon Oct 18 2010 Kyle McMartin <kyle@redhat.com> 2.6.34.7-61
- Add Ricoh e822 support. (rhbz#596475) Thanks to sgruszka@ for
  sending the patches in.

* Mon Oct 18 2010 Kyle McMartin <kyle@redhat.com> 2.6.34.7-60
- Quirk to disable DMAR with Ricoh card reader/firewire. (rhbz#605888)

* Mon Oct 18 2010 Kyle McMartin <kyle@redhat.com>
- Two networking fixes (skge, r8169) from sgruska. (rhbz#447489,629158)

* Thu Oct 14 2010 Neil Horman <nhorman@redhat.com>
- Fix rcu warning in twsock_net (bz 642905)

* Wed Oct 06 2010 Neil Horman <nhorman@redhat.com>
- Fix WARN_ON when you try to create an exiting bond in bond_masters

* Thu Sep 30 2010 Chuck Ebbert <cebbert@redhat.com>
- CVE-2010-3432: sctp-do-not-reset-the-packet-during-sctp_packet_config.patch

* Thu Sep 30 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.7-59
- nouveau: fix theoretical race condition that could be responsible for
  certain random hangs that have been reported.

* Mon Sep 27 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.7-58
- nouveau: better handling of certain GPU errors

* Fri Sep 24 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix typo in previous Xen fix that causes boot failure.

* Wed Sep 22 2010 Chuck Ebbert <cebbert@redhat.com>
- Copy two Xen fixes from 2.6.35-stable for RHBZ#636534

* Tue Sep 21 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix RHBZ #633037, Process user time incorrectly accounted as system time

* Mon Sep 20 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix AGP aperture size detection on Intel G33/Q35 chipsets (#629203)

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.34.7-56
- Fix CVE-2010-3079: ftrace NULL pointer dereference

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix CVE-2010-3080: /dev/sequencer open failure is not handled correctly

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix bug added in 2.6.34.6-53

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com>
- Mitigate DOS with large argument lists.

* Tue Sep 14 2010 Kyle McMartin <kyle@redhat.com>
- x86_64: plug compat syscalls holes. (CVE-2010-3081, CVE-2010-3301)
  upgrading is highly recommended.
- aio: check for multiplication overflow in do_io_submit. (CVE-2010-3067)

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.34.7, should fix multiple USB HID device issues.

* Mon Sep 13 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.6-55
- nouveau: fix oops in acpi edid support (rhbz#613284)

* Thu Sep 09 2010 Kyle McMartin <kyle@redhat.com>
- Backport 6f772d7e to hopefully fix #629442,
  (drm/i915: Explosion following OOM in do_execbuffer.)

* Wed Sep 08 2010 Kyle McMartin <kyle@redhat.com>
- Enable GPIO_SYSFS. (#631958)

* Sun Sep 05 2010 Jarod Wilson <jarod@redhat.com> 2.6.34.6-54
- Restore lirc patch from 2.6.33.x F13 kernels, re-fixes multiple issues

* Sat Sep 04 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.34.6-53
- Disable asynchronous suspend, a new feature in 2.6.34
- Fix unsafe access to MSI registers during suspend
  (pci-msi-remove-unsafe-and-unnecessary-hardware-access.patch,
   pci-msi-restore-read_msi_msg_desc-add-get_cached_msi_msg_desc.patch)
- x86-tsc-sched-recompute-cyc2ns_offset-s-during-resume-from-sleep-states.patch
   Fix load balancing after suspend/resume cycle (taken from 2.6.32 stable queue)

* Fri Sep 03 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.34.6-52
- acpi-ec-pm-fix-race-between-ec-transactions-and-system-suspend.patch:
  another possible fix for suspend/resume problems.
- From 2.6.35.4: nfs-fix-an-oops-in-the-nfsv4-atomic-open-code.patch
- Add fix for CVE-2010-2960: keyctl_session_to_parent NULL deref system crash

* Fri Sep 03 2010 Kyle McMartin <kmcmartin@redhat.com>
- default to pci=nocrs
- flexcop: fix registering braindead stupid names (#575873)

* Fri Sep 03 2010 Kyle McMartin <kmcmartin@redhat.com> 2.6.34.6-51
- lirc_imon: move alloc before use (rhbz#629980)

* Fri Sep 03 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.6-50
- Re-enable I2O, but only for 32-bit x86 (#629676)
- Add support for eject key on Dell laptops (#513530)
- irda-correctly-clean-up-self-ias_obj-on-irda_bind-failure.patch (CVE-2010-2954)
- wireless-extensions-fix-kernel-heap-content-leak.patch (CVE-2010-2955)

* Thu Sep 02 2010 Dave Airlie <airlied@redhat.com> 2.6.34.6-49
- fix radeon suspend/resume issues and two other minor patches

* Wed Sep 01 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.6-48
- Revert commit 6a1a82df91fa0eb1cc76069a9efe5714d087eccd from 2.6.34.1;
  it breaks ftdi_sio (#613597)

* Fri Aug 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.6-47
- Linux 2.6.34.6
- drivers-hwmon-coretemp-c-detect-the-thermal-sensors-by-cpuid.patch (#625734)
- kprobes-x86-fix-kprobes-to-skip-prefixes-correctly.patch (#610941)

* Wed Aug 25 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.6-46.rc1
- Linux 2.6.34.6-rc1
- Drop merged patches:
    matroxfb-fix-font-corruption.patch

* Tue Aug 24 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.34.5-45
- Revert commit 3d61510f4ecacfe47c75c0eb51c0659dfa77fb1b from 2.6.34.2;
  it causes dropped keystrokes (#625758)

* Mon Aug 23 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.5-44
- nouveau: fix eDP panels that flip HPD during link training (rhbz#596562)

* Sat Aug 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.5-43
- Linux 2.6.34.5
- Drop merged patches:
   mm-fix-page-table-unmap-for-stack-guard-page-properly.patch
   mm-fix-up-some-user-visible-effects-of-the-stack-guard-page.patch

* Wed Aug 18 2010 Chuck Ebbert <cebbert@redhat.com>
- Restore linux-2.6-umh-refactor.patch, still needed in 2.6.34 (#625150)
- Drop coredump-uid-pipe-check.patch, now upstream.

* Wed Aug 18 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.4-42
- Revert "ata-piix: Detect spurious IRQs and clear them",
  should be fixed by commit 27943620c upstream.

* Wed Aug 18 2010 Jarod Wilson <jarod@redhat.com>
- make f13 lirc userspace happy with ioctl defs again (#623770)

* Wed Aug 18 2010 Dave Jones <davej@redhat.com>
- ata-piix: Detect spurious IRQs and clear them.

* Tue Aug 17 2010 Kyle McMartin <kyle@redhat.com>
- Touch .scmversion in the kernel top level to prevent scripts/setlocalversion
  from recursing into our fedpkg git tree and trying to decide whether the
  kernel git is modified (obviously not, since it's a tarball.) Fixes make
  local.

* Tue Aug 17 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.4-41
- Fix fallout from the stack guard page fixes.
  (mm-fix-page-table-unmap-for-stack-guard-page-properly.patch,
   mm-fix-up-some-user-visible-effects-of-the-stack-guard-page.patch)

* Tue Aug 17 2010 Ben Skeggs <bskeggs@redhat.com>  2.6.34.4-40
- drm-nouveau-nv50-crtc-update-delay.patch (rhbz#614452)

* Sun Aug 15 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.4-39
- Linux 2.6.34.4

* Fri Aug 13 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.4-38.rc1
- Linux 2.6.34.4-rc1
- Fix up drm-next patch to apply on top of 2.6.34.4

* Tue Aug 10 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.3-37
- Linux 2.6.34.3
- Disable AES-NI encryption until bugs can be sorted out (#622435)

* Tue Aug 10 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.3-36.rc1
- nouveau: disable accel on nva3/nva5/nva8 until it's fixed upstream
- rhbz#596330

* Sat Aug 07 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.3-35.rc1
- Linux 2.6.34.3-rc1

* Fri Aug 06 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.2-34
- nouveau: fix inter-engine race when under memory pressure (rhbz#602956)
- Disable CONFIG_MULTICORE_RAID456

* Tue Aug 03 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.2-33
- Linux 2.6.34.2
- Drop commented-out patches.
- Drop ancient linux-2.6-mac80211-age-scan-results-on-resume.patch
- Fix matroxfb font corruption (#617687)
- Don't resurrect dead task credentials (#591015)
- Fix "ext4 and xfs wrong data returned on read after write if
  file size was changed with ftruncate" (#617699)

* Sun Aug 01 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.2-32.rc1
- Linux 2.6.34.2-rc1
- Comment out upstream merged patches:
    pci-pm-do-not-use-native-pcie-pme-by-default.patch
    linux-2.6-acpi-sleep-live-sci-live.patch (slightly different upstream patch)
    drm-i915-make-G4X-style-PLL-search-more-permissive.patch
    drm-intel-945gm-stability-fixes.patch
    drm-radeon-fix-shared-ddc-handling.patch
    drm-i915-add-reclaimable-to-page-allocations.patch
    drm-i915-fix-hibernate-memory-corruption.patch
    iwlwifi-Recover-TX-flow-stall-due-to-stuck-queue.patch
    iwlwifi-recover_from_tx_stall.patch
    mac80211-do-not-wipe-out-old-supported-rates.patch
    mac80211-fix-supported-rates-IE-if-AP-doesnt-give-us-its-rates.patch
    iwlwifi-cancel-scan-watchdog-in-iwl_bg_abort_scan.patch
    ata-generic-handle-new-mbp-with-mcp89.patch
    ata-generic-implement-ata-gen-flags.patch
    x86-debug-send-sigtrap-for-user-icebp.patch
    ethtool-fix-buffer-overflow.patch
    sched-fix-over-scheduling-bug.patch
    kbuild-fix-modpost-segfault.patch
    acpica-00-linux-2.6.git-0f849d2cc6863c7874889ea60a871fb71399dd3f.patch
    acpica-01-linux-2.6.git-a997ab332832519c2e292db13f509e4360495a5a.patch
    acpica-02-linux-2.6.git-e4e9a735991c80fb0fc1bd4a13a93681c3c17ce0.patch
    acpica-03-linux-2.6.git-fd247447c1d94a79d5cfc647430784306b3a8323.patch
    acpica-04-linux-2.6.git-c9a8bbb7704cbf515c0fc68970abbe4e91d68521.patch
    acpica-05-linux-2.6.git-ce43ace02320a3fb9614ddb27edc3a8700d68b26.patch
    acpica-06-linux-2.6.git-9d3c752de65dbfa6e522f1d666deb0ac152ef367.patch
    acpi-pm-do-not-enable-gpes-for-system-wakeup-in-advance.patch
    cifs-fix-malicious-redirect-problem-in-the-dns-lookup-code.patch
    usb-obey-the-sysfs-power-wakeup-setting.patch
- Fix up virtqueue-wrappers.patch to apply after 2.6.34.2 due to:
    virtio_net-fix-oom-handling-on-tx.patch
- Revert -stable DRM patches already in our drm-next patch:
    amd64-agp-probe-unknown-agp-devices-the-right-way.patch
    i915-fix-lock-imbalance-on-error-path.patch
    drm-i915-hold-the-spinlock-whilst-resetting-unpin_work-along-error-path.patch
- Fix up drm-next.patch to apply after 2.6.34.2 due to:
    drm-i915-gen3-page-flipping-fixes.patch
    drm-i915-don-t-queue-flips-during-a-flip-pending-event.patch
- Drop patches now upstream from linux-2.6-v4l-dvb-uvcvideo-update.patch:
    V4L/DVB: uvcvideo: Add support for unbranded Arkmicro 18ec:3290 webcams
    V4L/DVB: uvcvideo: Add support for V4L2_PIX_FMT_Y16
- Temporarily comment out ssb_check_for_sprom.patch due to ugly conflicts with:
    ssb-handle-netbook-devices-where-the-sprom-address-is-changed.patch

* Sun Aug 01 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-31
- Backport initial dist-git fixes from master (377da6d08)
- Modify the prep stage so multiple trees can be prepped in a
  single shared git directory.

* Mon Jul 26 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-30
- usb-obey-the-sysfs-power-wakeup-setting.patch:
  Restore ability of USB devices to wake the machine (#617559)

* Thu Jul 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-29
- cifs-fix-malicious-redirect-problem-in-the-dns-lookup-code.patch:
  Fix a malicious redirect problem in the DNS lookup code (CVE-2010-2524)

* Thu Jul 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-28
- input-synaptics-relax-capability-id-checks-on-new-hardware.patch:
  Make mouse driver recognize newer synaptics hardware as touchpad.

* Thu Jul 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-27
- ACPI GPE enable/disable patches: fix system powering back on
  after shutdown (#613239) (and possibly #615858)

* Thu Jul 22 2010 Jerome Glisse <jglisse@redhat.com> 2.6.34.1-26
- radeon fix shared ddc handling (#593429)

* Thu Jul 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-25
- kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch:
  Fix crash in guest Python programs (#610911)

* Wed Jul 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-24
- Drop crypto-aesni-kill-module_alias.patch; bug #571577 should
  not be present in 2.6.34.

* Wed Jul 21 2010 Dave Airlie <airlied@redhat.com> 2.6.34.1-23
- drm-intel-945gm-stability-fixes.patch: fix 945GM stability issues

* Wed Jul 21 2010 Dave Airlie <airlied@redhat.com> 2.6.34.1-22
- double drop: its a revert on top of a revert.

* Tue Jul 20 2010 Dave Airlie <airlied@redhat.com> 2.6.34.1-21
- drop drm revert, that can't possible cause the bug, but is causing another one.

* Mon Jul 19 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-20
- pci-fall-back-to-original-bios-bar-addresses.patch:
  Fix 2.6.34 problems with assigning PCI addresses (KORG#16263)

* Mon Jul 19 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-19
- drm-i915-add-reclaimable-to-page-allocations.patch:
  Additional fix for hibernation memory corruption bugs.

* Sun Jul 18 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-18
- drm-i915-make-G4X-style-PLL-search-more-permissive.patch (#572799)

* Sun Jul 18 2010 Hans de Goede <hdegoede@redhat.com> 2.6.34.1-17
- Fix inotify-fix-inotify-oneshot-support.patch so that it compiles
- Various small updates / fixes to the uvcvideo driver:
  - Support dynamic menu controls (#576023)
  - Fix the apple iSight camera not working (#600998)

* Fri Jul 16 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-16
- inotify-fix-inotify-oneshot-support.patch,
  inotify-send-IN_UNMOUNT-events.patch:
  Fix broken oneshot support and missing umount events. (#607327)

* Fri Jul 16 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.1-15
- nouveau: fix lvds regression (#601002)
- nouveau: bring back acpi edid support, with fixes (#613284)
- nouveau: remove dcb1.5 quirk that breaks things (#595645)

* Wed Jul 14 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-14
- Truncate the obsolete git bluetooth and firewire patches, use
  ApplyOptionalPatch for bluetooth, cpufreq and firewire patches.

* Wed Jul 14 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-12
- pci-pm-do-not-use-native-pcie-pme-by-default.patch:
  fix PCIe hotplug interrupts firing continuously. (#613412)
- Update pci-acpi-disable-aspm-if-no-osc.patch so it works
  with the above patch.
- Drop linux-2.6-defaults-pciehp.patch: pciehp_passive mode
  does not exist anymore.

* Tue Jul 13 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.34.1-11
- nouveau: bring back patches lost from 2.6.34 update + add some more to
  fix at least rhbz#532711 and rhbz#593046
- remove patches relating to nouveau that are now unused

* Mon Jul 12 2010 Dave Jones <davej@redhat.com>
- Remove a bunch of x86 options from config files that get set
  automatically, and can't be overridden.

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-9
- crypto-aesni-kill-module_alias.patch: kill MODULE_ALIAS to prevent
  aesni-intel from autoloading.

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-8
- iwlwifi: cancel scan watchdog in iwl_bg_abort_scan (#590436)

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-7
- Restore PowerPC VIO modalias patch; use the upstream version.
- Drop Mac G5 thermal shutdown patch, now upstream.

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-6
- Fix modpost segfault when building kernels. (#595915)

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-5
- pci-change-error-messages-to-kern-info.patch:
  Use new upstream patch to silence more useless messages.

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-4
- sched-fix-over-scheduling-bug.patch: fix scheduler bug with CGROUPS

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-3
- ethtool-fix-buffer-overflow.patch (CVE-2010-2478)

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-2
- Copy fix for BZ#609548 from F-13 2.6.33 kernel.

* Fri Jul 09 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.34.1-1
- Initial commit of 2.6.34 for F-13
- Previous history is in the branch private-f14-2_6_34

* Wed Jul 07 2010 Chuck Ebbert <cebbert@redhat.com>
- pci-acpi-disable-aspm-if-no-osc.patch, pci-aspm-dont-enable-too-early.patch
  PCI layer fixes for problems with hardware that doesn't support ASPM.

* Wed Jul 07 2010 Chuck Ebbert <cebbert@redhat.com>
- attempt to fix hibernate on Intel GPUs (kernel.org #13811) (RHBZ#537494)

* Wed Jul 07 2010 Chuck Ebbert <cebbert@redhat.com>
- Let ata_generic handle SATA interface on new MacBook Pro (#608034)

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com>
- Re-enable options: DYNAMIC_FTRACE, FUNCTION_TRACER and STACK_TRACER

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.34.1

* Thu Jul 01 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.34.1-rc1
- Drop patches merged upstream:
    btrfs-should-add-permission-check-for-setfacl.patch (CVE-2010-2071)
    iwlwifi-recalculate-average-tpt-if-not-current.patch
    iwlwifi-fix-internal-scan-race.patch
- Revert DRM patches we already have:
    drm-i915-rebind-bo-if-currently-bound-with-incorrect-alignment.patch
    drm-radeon-fix-the-r100-r200-ums-block-0-page-fix.patch
    drm-radeon-r100-r200-ums-block-ability-for-userspace-app-to-trash-0-page-and-beyond.patch
    drm-radeon-kms-atom-fix-typo-in-lvds-panel-info-parsing.patch
    drm-radeon-kms-reset-ddc_bus-in-object-header-parsing.patch
    drm-edid-fix-1024x768-85hz.patch
    drm-i915-reject-bind_to_gtt-early-if-object-aperture.patch
    drm-i915-fix-82854-pci-id-and-treat-it-like-other-85x.patch
- Revert broken -stable patch:
    perf-fix-endianness-argument-compatibility-with-opt_boolean-and-introduce-opt_incr.patch

* Wed Jun 30 2010 Kyle McMartin <kyle@redhat.com>
- Disable MRST on x86 here as well.

* Tue Jun 29 2010 Kyle McMartin <kyle@redhat.com>
- i915-fix-crt-hotplug-regression.patch: copy from rawhide.

* Mon Jun 28 2010 Chuck Ebbert <cebbert@redhat.com>
- ppc64: enable active memory sharing and DLPAR memory remove (#607175)

* Mon Jun 28 2010 Chuck Ebbert <cebbert@redhat.com>
- Copy fix for BZ#220892 from F-13.

* Fri Jun 25 2010 Kyle McMartin <kyle@redhat.com>
- drm-i915-fix-edp-panels.patch: copy from rawhide.

* Mon Jun 21 2010 Dave Jones <davej@redhat.com>
- Disable workaround for obscure SMP pentium pro errata.
  I miss the 1990s too, but it's time to move on.
  If anyone actually needs this it would be better done using
  the apply_alternatives infrastructure.

* Mon Jun 21 2010 Kyle McMartin <kyle@redhat.com>
- drm-revert-drm-fbdev-rework-output-polling-to-be-back-in-core.patch
  Revert eb1f8e4f, bisected by Nicolas Kaiser. Thanks! (rhbz#599190)
  (If this works, will try to root-cause.)
- rebase previous patch on top of above reversion

* Mon Jun 21 2010 Kyle McMartin <kyle@redhat.com>
- revert-drm-kms-toggle-poll-around-switcheroo.patch (rhbz#599190)

* Thu Jun 17 2010 Kyle McMartin <kyle@redhat.com>
- Suck in patch from Dave Miller in 2.6.35 to add async hash testing,
  hopefully fixes error from previous commit. (But making it modular
  is still a good idea.)

* Thu Jun 17 2010 Kyle McMartin <kyle@redhat.com>
- make ghash-clmulni modular to get rid of early boot noise (rhbz#586954)
  (not a /fix/ but it should at least quiet boot down a bit if you have
   the cpu support)

* Wed Jun 16 2010 Kyle McMartin <kyle@redhat.com>
- Snag some more DRM commits into drm-next.patch that I missed the first
  time.
- Fix up radeon_pm toggle to work with the upstream code.

* Tue Jun 15 2010 Prarit Bhargava <prarit@redhat.com>
- Turn off CONFIG_I2O on x86.
  It is broken on 64-bit address spaces (i686/PAE, x86_64), and frankly, I'm
  having trouble finding anyone who actually uses it.

* Tue Jun 15 2010 Kyle McMartin <kyle@redhat.com>
- Fix build by nuking superfluous "%{expand" which was missing a
  trailing '}'. You may now reward me with an array of alcoholic
  beverages, I so richly deserve for spending roughly a full
  day staring at the diff of the spec.

* Mon Jun 14 2010 Kyle McMartin <kyle@redhat.com>
- btrfs ACL fixes from CVE-2010-2071.

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com>
- remunge and reapply hdpvr-ir-enable

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com>
- mac80211/iwlwifi fix connections to some APs (rhbz#558002)
  patches from sgruszka@.

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com>
- Provide a knob to enable radeon_pm to allow users to test
  that functionality. Add radeon.pm=1 to your kernel cmdline
  in order to enable it. (It still defaults to off though.)

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com>
- Update drm-next to include fixes since 2.6.35-rc1.

* Fri Jun 11 2010 Justin M. Forbes <jforbes@redhat.com>
- Disable xsave for so that kernel will boot on ancient EC2 hosts.

* Wed Jun 09 2010 John W. Linville <linville@redhat.com>
- Disable rt20xx and rt35xx chipset support in rt2800 drivers (#570869)

* Wed Jun 09 2010 David Woodhouse <David.Woodhouse@intel.com>
- Include PHY modules in modules.networking (#602155)


###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
