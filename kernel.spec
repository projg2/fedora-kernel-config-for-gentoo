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

# buildid can also be specified on the rpmbuild command line
# by adding --define="buildid .whatever". If both kinds of buildid
# are specified they will be concatenated together.
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
%global baserelease 148
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 2.6.22-rc7-git1 starts with a 2.6.21 base,
# which yields a base_sublevel of 21.
%define base_sublevel 33

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
# kernel-kdump
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     1}
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
# Use dracut instead of mkinitrd for initrd image generation
%define with_dracut       %{?_without_dracut:       0} %{?!_without_dracut:       1}

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
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%endif
%define with_smp 0
%define with_pae 0
%define with_xen 0
%define with_kdump 0
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

%define with_kdump 0

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
%define all_arch_configs kernel-%{version}-s390x*.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%endif

%ifarch sparc
# We only build sparc headers since we dont support sparc32 hardware
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

# We don't build a kernel on i386; we only do kernel-headers there,
# and we no longer build for 31bit s390. Same for 32bit sparc and arm.
%define nobuildarches i386 s390 sparc %{arm}

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_kdump 0
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

#
# The ld.so.conf.d file we install uses syntax older ldconfig's don't grok.
#
%define kernel_xen_conflicts glibc < 2.3.5-1, xen < 3.0.1

%define kernel_PAE_obsoletes kernel-smp < 2.6.17, kernel-xen <= 2.6.27-0.2.rc0.git6.fc10
%define kernel_PAE_provides kernel-xen = %{rpmversion}-%{pkg_release}

%ifarch x86_64
%define kernel_obsoletes kernel-xen <= 2.6.27-0.2.rc0.git6.fc10
%define kernel_provides kernel-xen = %{rpmversion}-%{pkg_release}
%endif

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.10-1
%if %{with_dracut}
%define initrd_prereq  dracut >= 001-7
%else
%define initrd_prereq  mkinitrd >= 6.0.61-1
%endif

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
Requires(pre): linux-firmware\
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
BuildRequires: elfutils-libelf-devel zlib-devel binutils-devel libdwarf-devel
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
Patch10: git-cpufreq.patch
Patch11: git-bluetooth.patch

# Standalone patches
Patch20: linux-2.6-hotfixes.patch

Patch21: linux-2.6-tracehook.patch
Patch22: linux-2.6-utrace.patch
Patch23: linux-2.6-utrace-ptrace.patch

Patch143: linux-2.6-g5-therm-shutdown.patch
Patch144: linux-2.6-vio-modalias.patch

Patch150: linux-2.6.29-sparc-IOC_TYPECHECK.patch

Patch160: linux-2.6-execshield.patch

Patch250: linux-2.6-debug-sizeof-structs.patch
Patch260: linux-2.6-debug-nmi-timeout.patch
Patch270: linux-2.6-debug-taint-vm.patch
Patch300: linux-2.6-driver-level-usb-autosuspend.diff
Patch303: linux-2.6-enable-btusb-autosuspend.patch
Patch304: linux-2.6-usb-uvc-autosuspend.diff
Patch305: linux-2.6-fix-btusb-autosuspend.patch
Patch310: linux-2.6-usb-wwan-update.patch

Patch340: linux-2.6-debug-vm-would-have-oomkilled.patch
Patch360: linux-2.6-debug-always-inline-kzalloc.patch
Patch380: linux-2.6-defaults-pci_no_msi.patch
Patch381: linux-2.6-pciehp-update.patch
Patch382: linux-2.6-defaults-pciehp.patch
Patch383: linux-2.6-defaults-aspm.patch
Patch390: linux-2.6-defaults-acpi-video.patch
Patch391: linux-2.6-acpi-video-dos.patch
Patch392: linux-2.6-acpi-video-export-edid.patch
Patch450: linux-2.6-input-kill-stupid-messages.patch
Patch451: linux-2.6-input-fix-toshiba-hotkeys.patch
Patch452: linux-2.6.30-no-pcspkr-modalias.patch
Patch453: thinkpad-acpi-add-x100e.patch
Patch454: linux-2.6-input-hid-quirk-egalax.patch
Patch455: linux-2.6-input-clickpad-support.patch
Patch456: thinkpad-acpi-fix-backlight.patch
Patch457: ntrig-backport.patch

Patch460: linux-2.6-serial-460800.patch

Patch470: die-floppy-die.patch

Patch510: linux-2.6-silence-noise.patch
Patch520: linux-2.6.30-hush-rom-warning.patch
Patch530: linux-2.6-silence-fbcon-logo.patch
Patch570: linux-2.6-selinux-mprotect-checks.patch
Patch580: linux-2.6-sparc-selinux-mprotect-checks.patch
Patch581: linux-2.6-selinux-avtab-size.patch

Patch601: linux-2.6-acpi-indirect_fan_control.patch

Patch610: hda_intel-prealloc-4mb-dmabuffer.patch

Patch670: linux-2.6-ata-quirk.patch

Patch681: linux-2.6-mac80211-age-scan-results-on-resume.patch

Patch800: linux-2.6-crash-driver.patch

Patch1515: lirc-2.6.33.patch
Patch1517: hdpvr-ir-enable.patch
Patch1520: crystalhd-2.6.34-staging.patch

# virt + ksm patches
Patch1553: vhost_net-rollup.patch
Patch1554: virt_console-rollup.patch
Patch1555: virt_console-fix-race.patch
Patch1556: virt_console-fix-fix-race.patch
Patch1557: virt_console-rollup2.patch
Patch1558: vhost_net-rollup2.patch
# EC2 is running old xen hosts and wont upgrade so we have to work around it
Patch1559: fix_xen_guest_on_old_EC2.patch

# fbdev x86-64 primary fix
Patch1700: linux-2.6-x86-64-fbdev-primary.patch

Patch1800: drm-core-next.patch
# fix modeline for 1024x768@85
Patch1801: drm-1024x768-85.patch

# radeon kms backport
Patch1808: drm-radeon-evergreen.patch
Patch1809: drm-radeon-firemv-pciid.patch
Patch1810: drm-radeon-kms-fix-dual-link-dvi.patch
Patch1811: drm-radeon-fix-rs600-tlb.patch
Patch1812: drm-radeon-ss-fix.patch
# nouveau fixes
# - these not until 2.6.34
Patch1815: drm-nouveau-abi16.patch
Patch1816: drm-nouveau-updates.patch
# requires code that hasn't been merged upstream yet
Patch1817: drm-nouveau-acpi-edid-fallback.patch
Patch1818: drm-nouveau-drm-fixed-header.patch

# drm fixes
Patch1819: drm-intel-big-hammer.patch
# intel drm is all merged upstream
Patch1824: drm-intel-next.patch
# make sure the lvds comes back on lid open
Patch1825: drm-intel-make-lvds-work.patch
# disable iommu for gfx by default, just too broken
Patch1827: linux-2.6-intel-iommu-igfx.patch
# posted for upstream but not in an anholt tree yet
Patch1828: drm-intel-gen5-dither.patch
# thanks for the untested sdvo rework guys
Patch1829: drm-intel-sdvo-fix.patch
Patch1830: drm-intel-sdvo-fix-2.patch
# from 2.6.33.5
Patch1840: drm-i915-use-pipe_control-instruction-on-ironlake-and-sandy-bridge.patch
Patch1841: drm-i915-fix-non-ironlake-965-class-crashes.patch
Patch1842: drm-i915-fix-edp-panels.patch

Patch2100: linux-2.6-phylib-autoload.patch

# linux1394 git patches
Patch2200: linux-2.6-firewire-git-update.patch
Patch2201: linux-2.6-firewire-git-pending.patch

# Quiet boot fixes
# silence the ACPI blacklist code
Patch2802: linux-2.6-silence-acpi-blacklist.patch

# Upstream V4L updates
Patch2899: linux-2.6-v4l-dvb-fixes.patch
Patch2900: linux-2.6-v4l-dvb-update.patch
Patch2901: linux-2.6-v4l-dvb-experimental.patch

# Rebase gspca to what will be in 2.6.34
Patch2904: linux-2.6-v4l-dvb-rebase-gspca-to-latest.patch
# Some cherry picked fixes from v4l-dvb-next
Patch2905: linux-2.6-v4l-dvb-gspca-fixes.patch

# kworld ub435-q/340u usb atsc tuner support (still lingering
# in one of mkrufky's trees, pending push to v4l-dvb proper)
Patch2906: linux-2.6-v4l-dvb-add-lgdt3304-support.patch
Patch2907: linux-2.6-v4l-dvb-add-kworld-a340-support.patch

# fs fixes
Patch3000: linux-2.6-btrfs-update.patch
Patch3002: btrfs-prohibit-a-operation-of-changing-acls-mask-when-noacl-mount-option-is-used.patch

# NFSv4
Patch3051: linux-2.6-nfs4-callback-hidden.patch

Patch4000: linux-2.6-cpufreq-locking.patch

# VIA Nano / VX8xx updates

# patches headed upstream
Patch12010: linux-2.6-dell-laptop-rfkill-fix.patch
Patch12013: linux-2.6-rfkill-all.patch
Patch12014: linux-2.6-x86-cfi_sections.patch

Patch12015: add-appleir-driver.patch

Patch12017: prevent-runtime-conntrack-changes.patch

Patch12018: neuter_intel_microcode_load.patch

Patch12019: linux-2.6-umh-refactor.patch

# rhbz#533746
Patch12021: ssb_check_for_sprom.patch

# make p54pci usable on slower hardware
Patch12103: linux-2.6-p54pci.patch

Patch12200: acpi-ec-add-delay-before-write.patch

# patches from Intel to address intermittent firmware failures with iwlagn
Patch12404: iwlwifi_-add-function-to-reset_tune-radio-if-needed.patch
Patch12405: iwlwifi_-Logic-to-control-how-frequent-radio-should-be-reset-if-needed.patch
Patch12406: iwlwifi_-Tune-radio-to-prevent-unexpected-behavior.patch
Patch12407: iwlwifi_-multiple-force-reset-mode.patch
Patch12409: iwlwifi_-Adjusting-PLCP-error-threshold-for-1000-NIC.patch
Patch12410: iwlwifi_-separated-time-check-for-different-type-of-force-reset.patch
Patch12411: iwlwifi_-add-internal-short-scan-support-for-3945.patch
Patch12412: iwlwifi_-Recover-TX-flow-stall-due-to-stuck-queue.patch
Patch12413: iwlwifi_-move-plcp-check-to-separated-function.patch
Patch12414: iwlwifi_-Recover-TX-flow-failure.patch
Patch12415: iwlwifi_-code-cleanup-for-connectivity-recovery.patch
Patch12416: iwlwifi_-iwl_good_ack_health-only-apply-to-AGN-device.patch

Patch12500: alsa-usbmixer-add-possibility-to-remap-dB-values.patch

# fix possible corruption with ssd
Patch12700: ext4-issue-discard-operation-before-releasing-blocks.patch

Patch12820: ibmvscsi-fix-DMA-API-misuse.patch

Patch12830: disable-i8042-check-on-apple-mac.patch

Patch12850: crypto-aesni-kill-module_alias.patch

# automatically mount debugfs when perf needs it
Patch12851: perf-mount-debugfs-automatically.patch

# iwlwifi: fix scan races
Patch12910: iwlwifi-fix-scan-races.patch
# iwlwifi: fix internal scan race
Patch12911: iwlwifi-fix-internal-scan-race.patch
# iwlwifi: recover_from_tx_stall
Patch12912: iwlwifi-recover_from_tx_stall.patch

Patch12913: iwlwifi-manage-QoS-by-mac-stack.patch
Patch12915: mac80211-explicitly-disable-enable-QoS.patch

# Disable rt20xx and rt35xx chipset support in rt2800pci and rt2800usb
Patch13010: rt2x00-rt2800-Make-rt30xx-and-rt35xx-chipsets-configurable.patch

Patch13074: inotify-fix-inotify-oneshot-support.patch
Patch13076: inotify-send-IN_UNMOUNT-events.patch

Patch13080: kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch

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
Requires: libdwarf
%description -n perf
This package provides the perf shell script, supporting documentation and
required libraries for the perf tool shipped in each kernel image subpackage.

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


%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.


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
  # Move away the stale	 away, and delete in background.
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

#ApplyPatch git-cpufreq.patch
ApplyPatch git-bluetooth.patch

ApplyPatch linux-2.6-hotfixes.patch

# Roland's utrace ptrace replacement.
ApplyPatch linux-2.6-tracehook.patch
ApplyPatch linux-2.6-utrace.patch
ApplyPatch linux-2.6-utrace-ptrace.patch

# Architecture patches
# x86(-64)
ApplyPatch linux-2.6-dell-laptop-rfkill-fix.patch
ApplyPatch linux-2.6-x86-cfi_sections.patch

#
# Intel IOMMU
#

#
# PowerPC
#
### NOT (YET) UPSTREAM:
# Alleviate G5 thermal shutdown problems
ApplyPatch linux-2.6-g5-therm-shutdown.patch
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

# ext4

# xfs

# btrfs
ApplyPatch linux-2.6-btrfs-update.patch

ApplyPatch btrfs-prohibit-a-operation-of-changing-acls-mask-when-noacl-mount-option-is-used.patch

# eCryptfs

# NFSv4
ApplyPatch linux-2.6-nfs4-callback-hidden.patch

# CPUFREQ
ApplyPatch linux-2.6-cpufreq-locking.patch

# USB
ApplyPatch linux-2.6-driver-level-usb-autosuspend.diff
ApplyPatch linux-2.6-enable-btusb-autosuspend.patch
ApplyPatch linux-2.6-usb-uvc-autosuspend.diff
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
# PCI
#
# disable message signaled interrupts
ApplyPatch linux-2.6-defaults-pci_no_msi.patch
# update the pciehp driver
#ApplyPatch linux-2.6-pciehp-update.patch
# default to enabling passively listening for hotplug events
#ApplyPatch linux-2.6-defaults-pciehp.patch
# enable ASPM by default on hardware we expect to work
ApplyPatch linux-2.6-defaults-aspm.patch

#
# SCSI Bits.
#

# ACPI
ApplyPatch linux-2.6-acpi-indirect_fan_control.patch

# ALSA
ApplyPatch hda_intel-prealloc-4mb-dmabuffer.patch

# Networking

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch linux-2.6-input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

# Get away from having to poll Toshibas
#ApplyPatch linux-2.6-input-fix-toshiba-hotkeys.patch

ApplyPatch linux-2.6.30-no-pcspkr-modalias.patch

ApplyPatch linux-2.6-input-hid-quirk-egalax.patch
ApplyPatch linux-2.6-input-clickpad-support.patch
ApplyPatch thinkpad-acpi-add-x100e.patch
ApplyPatch thinkpad-acpi-fix-backlight.patch
ApplyPatch ntrig-backport.patch

# Allow to use 480600 baud on 16C950 UARTs
ApplyPatch linux-2.6-serial-460800.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch linux-2.6-silence-noise.patch
ApplyPatch linux-2.6.30-hush-rom-warning.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch linux-2.6-silence-fbcon-logo.patch

# Fix the SELinux mprotect checks on executable mappings
#ApplyPatch linux-2.6-selinux-mprotect-checks.patch
# Fix SELinux for sparc
#ApplyPatch linux-2.6-sparc-selinux-mprotect-checks.patch
# Shirk size of memory allocation required to load policy.  In 2.6.34
ApplyPatch linux-2.6-selinux-avtab-size.patch

# Changes to upstream defaults.


# ia64 ata quirk
ApplyPatch linux-2.6-ata-quirk.patch

# back-port scan result aging patches
#ApplyPatch linux-2.6-mac80211-age-scan-results-on-resume.patch

# /dev/crash driver.
ApplyPatch linux-2.6-crash-driver.patch

# http://www.lirc.org/
ApplyPatch lirc-2.6.33.patch
# enable IR receiver on Hauppauge HD PVR (v4l-dvb merge pending)
ApplyPatch hdpvr-ir-enable.patch
# Broadcom Crystal HD video decoder
ApplyPatch crystalhd-2.6.34-staging.patch

# Assorted Virt Fixes
ApplyPatch vhost_net-rollup.patch
ApplyPatch virt_console-rollup.patch
ApplyPatch virt_console-fix-race.patch
ApplyPatch virt_console-fix-fix-race.patch
ApplyPatch virt_console-rollup2.patch
ApplyPatch vhost_net-rollup2.patch
ApplyPatch fix_xen_guest_on_old_EC2.patch

# fix x86-64 fbdev primary GPU selection
ApplyPatch linux-2.6-x86-64-fbdev-primary.patch

ApplyPatch drm-core-next.patch
ApplyPatch drm-1024x768-85.patch

# Nouveau DRM + drm fixes
ApplyPatch drm-radeon-evergreen.patch
ApplyPatch drm-radeon-firemv-pciid.patch
ApplyPatch drm-radeon-kms-fix-dual-link-dvi.patch
ApplyPatch drm-radeon-fix-rs600-tlb.patch
ApplyPatch drm-radeon-ss-fix.patch
ApplyPatch drm-nouveau-abi16.patch
ApplyPatch drm-nouveau-updates.patch
ApplyPatch drm-nouveau-acpi-edid-fallback.patch
ApplyPatch drm-nouveau-drm-fixed-header.patch
# pm broken on my thinkpad t60p - airlied
ApplyPatch drm-intel-big-hammer.patch
ApplyOptionalPatch drm-intel-next.patch
ApplyPatch drm-intel-make-lvds-work.patch
ApplyPatch linux-2.6-intel-iommu-igfx.patch
ApplyPatch drm-intel-gen5-dither.patch
ApplyPatch drm-intel-sdvo-fix.patch
ApplyPatch drm-intel-sdvo-fix-2.patch
# from 2.6.33.5
ApplyPatch drm-i915-use-pipe_control-instruction-on-ironlake-and-sandy-bridge.patch
ApplyPatch drm-i915-fix-non-ironlake-965-class-crashes.patch
ApplyPatch drm-i915-fix-edp-panels.patch

ApplyPatch linux-2.6-phylib-autoload.patch

# linux1394 git patches
#ApplyPatch linux-2.6-firewire-git-update.patch
#ApplyOptionalPatch linux-2.6-firewire-git-pending.patch

# silence the ACPI blacklist code
ApplyPatch linux-2.6-silence-acpi-blacklist.patch

# V4L/DVB updates/fixes/experimental drivers
#  Upstream trees, applied only if non-empty
ApplyOptionalPatch linux-2.6-v4l-dvb-fixes.patch
ApplyOptionalPatch linux-2.6-v4l-dvb-update.patch
ApplyOptionalPatch linux-2.6-v4l-dvb-experimental.patch

ApplyPatch linux-2.6-v4l-dvb-rebase-gspca-to-latest.patch
ApplyPatch linux-2.6-v4l-dvb-gspca-fixes.patch

ApplyPatch linux-2.6-v4l-dvb-add-lgdt3304-support.patch
ApplyPatch linux-2.6-v4l-dvb-add-kworld-a340-support.patch

# Patches headed upstream
ApplyPatch linux-2.6-rfkill-all.patch

# appleir remote controller
ApplyPatch add-appleir-driver.patch

ApplyPatch neuter_intel_microcode_load.patch

# Refactor UserModeHelper code & satisfy abrt recursion check request
ApplyPatch linux-2.6-umh-refactor.patch

ApplyPatch alsa-usbmixer-add-possibility-to-remap-dB-values.patch

# rhbz#533746
ApplyPatch ssb_check_for_sprom.patch

# make p54pci usable on slower hardware
ApplyPatch linux-2.6-p54pci.patch

# patches from Intel to address intermittent firmware failures with iwlagn
ApplyPatch iwlwifi_-add-function-to-reset_tune-radio-if-needed.patch
ApplyPatch iwlwifi_-Logic-to-control-how-frequent-radio-should-be-reset-if-needed.patch
ApplyPatch iwlwifi_-Tune-radio-to-prevent-unexpected-behavior.patch
ApplyPatch iwlwifi_-multiple-force-reset-mode.patch
ApplyPatch iwlwifi_-Adjusting-PLCP-error-threshold-for-1000-NIC.patch
ApplyPatch iwlwifi_-separated-time-check-for-different-type-of-force-reset.patch
ApplyPatch iwlwifi_-add-internal-short-scan-support-for-3945.patch
ApplyPatch iwlwifi_-Recover-TX-flow-stall-due-to-stuck-queue.patch
ApplyPatch iwlwifi_-move-plcp-check-to-separated-function.patch
ApplyPatch iwlwifi_-Recover-TX-flow-failure.patch
ApplyPatch iwlwifi_-code-cleanup-for-connectivity-recovery.patch
ApplyPatch iwlwifi_-iwl_good_ack_health-only-apply-to-AGN-device.patch

# fix possible corruption with ssd
ApplyPatch ext4-issue-discard-operation-before-releasing-blocks.patch

ApplyPatch ibmvscsi-fix-DMA-API-misuse.patch

ApplyPatch disable-i8042-check-on-apple-mac.patch

ApplyPatch crypto-aesni-kill-module_alias.patch

# automagically mount debugfs for perf
ApplyPatch perf-mount-debugfs-automatically.patch

# iwlwifi: fix scan races
ApplyPatch iwlwifi-fix-scan-races.patch
# iwlwifi: fix internal scan race
ApplyPatch iwlwifi-fix-internal-scan-race.patch
# iwlwifi: recover_from_tx_stall
ApplyPatch iwlwifi-recover_from_tx_stall.patch

# mac80211/iwlwifi fix connections to some APs (rhbz#558002)
ApplyPatch mac80211-explicitly-disable-enable-QoS.patch
ApplyPatch iwlwifi-manage-QoS-by-mac-stack.patch

# Disable rt20xx and rt35xx chipset support in rt2800pci and rt2800usb
ApplyPatch rt2x00-rt2800-Make-rt30xx-and-rt35xx-chipsets-configurable.patch

# fix broken oneshot support and missing umount events (#607327)
ApplyPatch inotify-fix-inotify-oneshot-support.patch
ApplyPatch inotify-send-IN_UNMOUNT-events.patch

# RHBZ#610911
ApplyPatch kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

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
%if %{with_dracut}
    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20
%else
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initrd-$KernelVer.img bs=1M count=5
%endif
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
    if grep '^CONFIG_XEN=y$' .config >/dev/null; then
      echo > ldconfig-kernel.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 0 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 0 nosegneg"
    fi
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

%if %{with_kdump}
BuildKernel vmlinux vmlinux kdump vmlinux
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

%if %{with_perf}
# perf docs
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

# perf shell wrapper and examples
mkdir -p $RPM_BUILD_ROOT/usr/sbin/
cp $RPM_SOURCE_DIR/perf $RPM_BUILD_ROOT/usr/sbin/perf
chmod 0755 $RPM_BUILD_ROOT/usr/sbin/perf
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/perf
cp tools/perf/Documentation/examples.txt $RPM_BUILD_ROOT%{_datadir}/doc/perf
%endif # with_perf

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
%{expand:\
%if %{with_dracut}\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVERREL}%{?-v:.%{-v*}} || exit $?\
%else\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --depmod --update %{KVERREL}%{?-v:.%{-v*}} || exit $?\
%endif}\
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
%ifarch x86_64
%kernel_variant_post -r (kernel-smp|kernel-xen)
%else
%kernel_variant_post -r kernel-smp
%endif

%kernel_variant_preun smp
%kernel_variant_post -v smp

%kernel_variant_preun PAE
%kernel_variant_post -v PAE -r (kernel|kernel-smp|kernel-xen)

%kernel_variant_preun debug
%kernel_variant_post -v debug

%kernel_variant_post -v PAEdebug -r (kernel|kernel-smp|kernel-xen)
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
%if %{with_dracut}\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%else\
%ghost /boot/initrd-%{KVERREL}%{?2:.%{2}}.img\
%endif\
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
%kernel_variant_files -k vmlinux %{with_kdump} kdump


%changelog
* Sat Aug 14 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.7-148
- Update to kernel 2.6.33.7
- Drop patches merged in 2.6.33.7:
    drm-i915-add-reclaimable-to-page-allocations.patch
    drm-i915-fix-hibernate-memory-corruption.patch
    drm-radeon-fix-shared-ddc-handling.patch
    linux-2.6-acpi-sleep-live-sci-live.patch
    drm-i915-make-G4X-style-PLL-search-more-permissive.patch
    drm-intel-945gm-stability-fixes.patch
    mac80211-do-not-wipe-out-old-supported-rates.patch
    mac80211-fix-supported-rates-IE-if-AP-doesnt-give-us-its-rates.patch
    iwlwifi-cancel-scan-watchdog-in-iwl_bg_abort_scan.patch
    sched-fix-over-scheduling-bug.patch
    ethtool-fix-buffer-overflow.patch
    x86-debug-clear-reserved-bits-of-dr6.patch
    x86-debug-send-sigtrap-for-user-icebp.patch
    cifs-fix-malicious-redirect-problem-in-the-dns-lookup-code.patch
- Revert broken ssb patch from 2.6.33.7:
    ssb-handle-netbook-devices-where-the-sprom-address-is-changed.patch

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.6-147.2.4
- inotify-fix-inotify-oneshot-support.patch,
  inotify-send-IN_UNMOUNT-events.patch:
  Fix broken oneshot support and missing umount events. (#607327)

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.6-147.2.3
- drm-i915-add-reclaimable-to-page-allocations.patch:
  Additional fix for hibernation memory corruption bugs.
- drm-intel-945gm-stability-fixes.patch: fix 945GM stability issues
- drm-i915-make-G4X-style-PLL-search-more-permissive.patch (#572799)
- drm-radeon-fix-shared-ddc-handling.patch (#593429)

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.6-147.2.2
- kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch:
  Fix crash in guest Python programs (#610911)

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.6-147.2.1
- cifs-fix-malicious-redirect-problem-in-the-dns-lookup-code.patch:
  Fix a malicious redirect problem in the DNS lookup code (CVE-2010-2524)

* Tue Jul 06 2010 Jarod Wilson <jarod@redhat.com> 2.6.33.6-147
- Really make hdpvr i2c IR part register this time, so something can
  actually be bound to it (like, say, lirc_zilog)

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33.6-146
- x86-debug-send-sigtrap-for-user-icebp.patch,
  x86-debug-clear-reserved-bits-of-dr6.patch (#609548)

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33.6-145
- ethtool-fix-buffer-overflow.patch: ethtool buffer overflow (CVE-2010-2478)

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33.6-144
- sched-fix-over-scheduling-bug.patch: fix scheduler bug with CGROUPS

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33.6-143
- Linux 2.6.33.6

* Fri Jul 02 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33.6-142.rc1
- nouveau: fix connector ordering issues (rhbz#602492)

* Fri Jul 02 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33.6-141.rc1
- Linux 2.6.33.6-rc1
- Drop patches merged upstream:
    btrfs-should-add-permission-check-for-setfacl.patch (CVE-2010-2071)
    iwlwifi-reset-card-during-probe.patch
    iwlwifi-recalculate-average-tpt-if-not-current.patch
    keys-find-keyring-by-name-can-gain-access-to-the-freed-keyring.patch
    l2tp-fix-oops-in-pppol2tp_xmit.patch
- Revert DRM patches we already have:
    drm-edid-fix-1024x768-85hz.patch
    drm-i915-fix-82854-pci-id-and-treat-it-like-other-85x.patch
- Fix up usb-wwan-update.patch for upstream additions.

* Fri Jul 02 2010 Dave Airlie <airlied@redhat.com> 2.6.33.5-140
- attempt to fix hibernate on Intel GPUs (kernel.org #13811)

* Wed Jun 30 2010 Kyle McMartin <kyle@redhat.com>
- Disable MRST here too.

* Mon Jun 28 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33.5-138
- ppc64: enable active memory sharing and DLPAR memory remove (#607175)

* Mon Jun 28 2010 Dave Airlie <airlied@redhat.com> 2.6.33.5-137
- i915: fix edp panels betterer.

* Fri Jun 25 2010 Dave Airlie <airlied@redhat.com> 2.6.33.5-136
- i915: fix edp on a number of notebooks (including whot's one)

* Fri Jun 25 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33.5-135
- nouveau: backport important fixes from upstream
- Fixes unPOSTed detection + support nv4x multi-card (rhbz#607190)
- Various VBIOS parser fixes (potential culprit for many suspend bugs)
- Fixes memory detection on some GF8 IGPs, and boards with 4GiB VRAM
- Corrects various problems in the behaviour of GF8 dual-link TMDS

* Wed Jun 23 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-134
- l2tp: fix oops in pppol2tp_xmit (#607054)

* Fri Jun 18 2010 Roland McGrath <roland@redhat.com> 2.6.33.5-133
- make execshield respect PF_RANDOMIZE and ADDR_NO_RANDOMIZE (#220892)

* Thu Jun 17 2010 Kyle McMartin <kyle@redhat.com>
- make ghash-clmulni modular to get rid of early boot noise (rhbz#586954)
  (not a /fix/ but it should at least quiet boot down a bit if you have
   the cpu support)

* Tue Jun 15 2010 John W. Linville <linville@redhat.com> 2.6.33.5-131
- iwlwifi: cancel scan watchdog in iwl_bg_abort_scan (#590436)

* Mon Jun 14 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-129
- Add btrfs ACL fixes from CVE-2010-2071.

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-128
- mac80211/iwlwifi fix connections to some APs (rhbz#558002)
  patches from sgruszka@.

* Fri Jun 11 2010 Justin M. Forbes <jforbes@redhat.com> 2.6.33.5-127
- Disable xsave for so that kernel will boot on ancient EC2 hosts.

* Fri Jun 11 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-126
- ALSA: usbmixer - add possibility to remap dB values (rhbz#578131)

* Fri Jun 11 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-124
- Drop writeback patches, they appear to be able to cause oopses.

* Wed Jun 09 2010 John W. Linville <linville@redhat.com>
- Disable rt20xx and rt35xx chipset support in rt2800 drivers (#570869)

* Wed Jun 09 2010 David Woodhouse <David.Woodhouse@intel.com>
- Include PHY modules in modules.networking (#602155)

* Wed Jun 09 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-121
- doc_build_fail FAIL.

* Wed Jun 09 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.5-120
- backport ntrig hid driver from git head. (rhbz#584593)

* Mon Jun 07 2010 Matthew Garrett <mjg@redhat.com>
- linux-2.6-acpi-indirect_fan_control.patch: fix some ACPI fans (rh#531916)

* Mon Jun 07 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: fix iommu errors on GeForce 8 and newer chipsets (rh#561267)

* Thu Jun 03 2010 Kyle McMartin <kyle@redhat.com>
- But keep it for kernel-headers...

* Thu Jun 03 2010 Dave Jones <davej@redhat.com>
- remove the 31bit s390 support again.

* Tue Jun 01 2010 Jarod Wilson <jarod@redhat.com>
- Wire up all s390{,x} bits to match RHEL6 kernel spec

* Wed May 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.5-112
- CVE-2010-1437: keyrings: find_keyring_by_name() can gain the freed keyring

* Wed May 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.5-111
- Linux 2.6.33.5
- Drop patches merged in -stable:
    iwlwifi_-check-for-aggregation-frame-and-queue.patch
    iwlwifi_-clear-all-the-stop_queue-flag-after-load-firmware.patch
    revert-ath9k_-fix-lockdep-warning-when-unloading-module.patch
    btrfs-check-for-read-permission-on-src-file-in-clone-ioctl.patch
- Revert drm patch already in F-13: drm-i915-disable-fbc-on-915gm-and-945gm.patch
- Apply DRM patches from -stable on top of F-13 DRM updates:
    drm-i915-use-pipe_control-instruction-on-ironlake-and-sandy-bridge.patch
    drm-i915-fix-non-ironlake-965-class-crashes.patch

* Thu May 27 2010 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau-updates.patch: add nv50 gpio fix (rh#582621)

* Wed May 26 2010 Adam Jackson <ajax@redhat.com>
- linux-2.6-cantiga-iommu-gfx.patch: Drop, redundant.
- config-generic: Disable i830.ko, userspace will never load it.

* Mon May 24 2010 John W. Linville <linville@redhat.com>
- iwlwifi: recover_from_tx_stall (#589777)

* Thu May 20 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.4-106
- Remove "PatchNNNN" entries for dropped patches.
- More writeback fixes from block-2.6 tree (#593669)

* Thu May 20 2010 Kyle McMartin <kyle@redhat.com>
- kill some dead patches.

* Wed May 19 2010 John W. Linville <linville@redhat.com>
- iwlwifi: fix scan races
- iwlwifi: fix internal scan race

* Wed May 19 2010 Dave Airlie <airlied@redhat.com>
- disable vmwgfx at request of vmware

* Wed May 19 2010 Roland McGrath <roland@redhat.com>
- x86: put assembly CFI in .debug_frame

* Tue May 18 2010 Kyle McMartin <kyle@redhat.com>
- btrfs: check for read permission on src file in the clone ioctl
  (rhbz#593226)

* Mon May 17 2010 Matthew Garrett <mjg@redhat.com>
- thinkpad-acpi-fix-backlight.patch: Fix backlight control on some recent
   Thinkpads

* Mon May 17 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.4-97
- perf-mount-debugfs-automatically.patch (#570821)

* Mon May 17 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33.4-96
- drm: fix edid modeline for 1024x768@85Hz (#582472)

* Thu May 13 2010 Jarod Wilson <jarod@redhat.com> 2.6.33.4-95
- Enable support for kworld ub435-q and 340u usb atsc tuners

* Thu May 13 2010 Peter Hutterer <peter.hutterer@redhat.com>
- linux-2.6-input-clickpad-support.patch: add support for ClickPad
  touchpads (#590835)

* Wed May 12 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.4-93
- Linux 2.6.33.4
- Drop patches merged upstream:
    linux-2.6-pci-fixup-resume.patch
    linux-2.6-tun-orphan_an_skb_on_tx.patch
    libata-fix-accesses-at-LBA28-boundary.patch
    linux-2.6-creds_are_invalid-race.patch
    hugetlb-fix-infinite-loop-in-get-futex-key.patch
    reiserfs-fix-permissions-on-reiserfs-priv.patch
    ath9k-reorder-ieee80211_free_hw-behind-ath9k_uninit_.patch
- Revert -stable DRM patches we already have:
    drm-i915-add-initial-bits-for-vga-modesetting-bringup-on-sandybridge.patch
    drm-i915-fix-tiling-limits-for-i915-class-hw-v2.patch
- Fix up patches to apply on top of 2.6.33.4:
    linux-2.6-p54pci.patch
    vhost_net-rollup.patch

* Wed May 12 2010 Roland McGrath <roland@redhat.com>
- utrace update (#590954)

* Mon May 10 2010 Kyle McMartin <kyle@redhat.com>
- don't link binutils against perf. sigh. stupid gpl versions.

* Mon May 10 2010 Eric Paris <eparis@redhat.com>
- reduce size of selinux poliy memory allocation (rhbz#590363)

* Mon May 10 2010 Kyle McMartin <kyle@redhat.com>
- crypto-aesni-kill-module_alias.patch: kill MODULE_ALIAS to prevent
  aesni-intel from autoloading.

* Mon May 10 2010 Ben Skeggs <bskeggs@redhat.com>
- add linux-2.6-input-hid-quirk-egalax.patch, missed from F-12, requested
  by Peter Hutterer.

* Sun May 09 2010 Kyle McMartin <kyle@redhat.com>
- fs-explicitly-pass-in-whether-sb-is-pinned-or-not.patch (rhbz#588930)

* Sat May 08 2010 Kyle McMartin <kyle@redhat.com>
- Link perf against libbfd.a for name-demangling support. (rhbz#590289)

* Thu May 06 2010 Adam Jackson <ajax@redhat.com> 2.6.33.3-85
- drm-intel-next: Enable the display even harder (#587171)

* Wed May 5 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.3-84
- CONFIG_HWMON=y => CONFIG_THERMAL_HWMON. Kconfig is worse than rabies.

* Wed May 5 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.3-83
- disable-i8042-check-on-apple-mac.patch: fix build on ppc.

* Tue May 4 2010 John W. Linville <linville@redhat.com> 2.6.33.3-82
- iwlwifi: recalculate average tpt if not current (#588021)

* Tue May 4 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.3-81
- disable-i8042-check-on-apple-mac.patch: avoid long delay or hang booting
  on Intel Apple Macs.

* Tue May 4 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.3-80
- ibmvscsi-fix-DMA-API-misuse.patch (#579454)

* Mon May 3 2010 Kyle McMartin <kyle@redhat.com> 2.6.33.3-79
- disable aesni. (#571577)

* Fri Apr 30 2010 John W. Linville <linville@redhat.com> 2.6.33.3-78
- ath9k: reorder ieee80211_free_hw behind ath9k_uninit_hw to avoid
  oops (#586787)

* Fri Apr 30 2010 Kyle McMartin <kyle@redhat.com>
- add-appleir-driver.patch: update from hadess, split out some other patches.
- git-bluetooth.patch: and put them in git-bluetooth, along with other fixes.

* Thu Apr 29 2010 Adam Jackson <ajax@redhat.com>
- drm-intel-sdvo-fix-2.patch: Require that the A/D bit of EDID match the
  A/D-ness of the connector. (#584229)

* Thu Apr 29 2010 Kyle McMartin <kyle@redhat.com>
- add-appleir-usb-driver.patch: updates from hadess.

* Thu Apr 29 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33.3-73
- nouveau: initial eDP support + DP suspend/resume fixes
- nouveau: fix monitor detection on certain chipsets with DP support
- nouveau: better CRTC PLL calculation on latest chipsets
- nouveau: send hotplug events down to userspace

* Wed Apr 28 2010 John W. Linville <linville@redhat.com> 2.6.33.3-72
- Revert "ath9k: fix lockdep warning when unloading module"

* Tue Apr 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.3-71
- Linux 2.6.33.3
- Drop patches merged upstream:
   acpi-ec-allow-multibyte-access-to-ec.patch
   acpi-ec-limit-burst-to-64-bit.patch
   b43_-Allow-PIO-mode-to-be-selected-at-module-load.patch
   b43_-fall-back-gracefully-to-PIO-mode-after-fatal-DMA-errors.patch
   mac80211_-tear-down-all-agg-queues-when-restart_reconfig-hw.patch
   iwlwifi_-clear-all-tx-queues-when-firmware-ready.patch
   iwlwifi_-fix-scan-race.patch
- Revert DRM patches we already have:
   drm-radeon-kms-add-firemv-2400-pci-id.patch
   drm-radeon-kms-fix-rs600-tlb-flush.patch
   drm-edid-quirks-envision-en2028.patch
   drm-return-enodev-if-the-inode-mapping-changes.patch
   drm-remove-the-edid-blob-stored-in-the-edid-property-when-it-is-disconnected.patch
   drm-edid-allow-certain-bogus-edids-to-hit-a-fixup-path-rather-than-fail.patch
- Fix up drm-core-next to apply after 2.6.33.3

* Tue Apr 27 2010 Justin M. Forbes <jforbes@redhat.com>
- Orphan an skb on tx for tun/tap devices.

* Tue Apr 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.2-68
- Fix possible data corruption with ext4 mounted with -o discard

* Mon Apr 26 2010 Chuck Ebbert <cebbert@redhat.com>
- hugetlb-fix-infinite-loop-in-get-futex-key.patch (F12#552557)
- reiserfs-fix-permissions-on-reiserfs-priv.patch (CVE-2010-1146)

* Mon Apr 26 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.2-66
- Turn off debugging and enable debug kernel builds.

* Mon Apr 26 2010 Dave Jones <davej@redhat.com>
- Revert PCI changes from 2.6.33.2.
  Possibly causing networking problems with some drivers.

* Mon Apr 26 2010 Adam Jackson <ajax@redhat.com>
- drm-intel-sdvo-fix.patch: Fix DDC bus selection for SDVO (#584229)

* Thu Apr 22 2010 Hans de Goede <hdegoede@redhat.com>
- Make p54pci wlan work on slower computers (#583623)

* Thu Apr 22 2010 Matthew Garrett <mjg@redhat.com>
- linux-2.6-pci-fixup-resume.patch: Make sure we enable power resources on D0

* Wed Apr 21 2010 Justin M. Forbes <jforbes@redhat.com>
- vhost-net fixes from upstream

* Wed Apr 21 2010 Roland McGrath <roland@redhat.com> 2.6.33.2-60
- fix race crash from bogus cred.c debugging code (#583843)

* Wed Apr 21 2010 Matthew Garrett <mjg@redhat.com>
- thinkpad-acpi-add-x100e.patch: Add EC path for Thinkpad X100

* Tue Apr 20 2010 Dave Airlie <airlied@redhat.com> 2.6.33.2-57
- drm-radeon-ss-fix.patch: backport spread spectrum fix (#571874)

* Mon Apr 19 2010 Adam Jackson <ajax@redhat.com> 2.6.33.2-56
- drm-intel-next.patch: 2.6.34 as of today, plus anholt's for-linus tree as
  of today, plus most of drm-intel-next except for the AGP/GTT split and a
  broken TV detect fix. Tested on 945GM, GM45, and gen5.
- drm-intel-make-lvds-work.patch: Rebase to match.
- drm-intel-acpi-populate-didl.patch: Drop, merged in -intel-next
- drm-intel-gen5-dither.patch: Use better dither on gen5.

* Mon Apr 19 2010 Matthew Garrett <mjg@redhat.com>
- linux-2.6-acpi-sleep-live-sci-live.patch: Try harder to switch to ACPI mode

* Mon Apr 19 2010 Adam Jackson <ajax@redhat.com>
- linux-2.6-intel-iommu-igfx.patch: Disable IOMMU for GFX by default, just too
  broken.  intel_iommu=igfx_on to turn it on. (Adel Gadllah)

* Mon Apr 19 2010 Dave Airlie <airlied@redhat.com>
- radeon: add rs600 + firemv pciid + dual-link fix

* Fri Apr 16 2010 John W. Linville <linville@redhat.com>
- Patches from Intel to address intermittent firmware failures with iwlagn

* Fri Apr 16 2010 Adam Jackson <ajax@redhat.com>
- drm-core-next.patch: Update EDID and other core bits to airlied's tree
- drm-nouveau-abi16.patch: Rediff to match

* Fri Apr 16 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33.2-49
- nouveau: fix dereference-after-free bug (rh#575224)
- drm-nouveau-acpi-edid-fallback.patch: fix ppc build + potential crasher

* Thu Apr 15 2010 Eric Paris <eparis@redhat.com>
- enable CONFIG_INTEL_TXT on x86_64

* Wed Apr 14 2010 David Woodhouse <David.Woodhouse@intel.com>
- Fix autoloading of phy modules (#525966)

* Wed Apr 14 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.2-46
- libata-fix-accesses-at-LBA28-boundary.patch

* Tue Apr 13 2010 Justin M. Forbes <jforbes@redhat.com>
- virt_console: Fixes from upstream

* Tue Apr 13 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix ACPI errors on boot caused by EC burst mode patch (#581535)
- Re-enable ACPI EC delay patch (#579510)

* Tue Apr 13 2010 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau-acpi-edid-fallback.patch: fix oops on cards without _DSM method

* Mon Apr 12 2010 Matthew Garrett <mjg@redhat.com>
- linux-2.6-acpi-video-export-edid.patch:
  drm-nouveau-acpi-edid-fallback.patch: Let nouveau get an EDID from ACPI

* Fri Apr 09 2010 John W. Linville <linville@redhat.com> 2.6.33.2-41
- b43: Allow PIO mode to be selected at module load
- b43: fall back gracefully to PIO mode after fatal DMA errors

* Fri Apr 09 2010 Chuck Ebbert <cebbert@redhat.com>
- virt_console: fix a bug in the original race fix

* Fri Apr 09 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: fixes from upstream + NVA3 support

* Thu Apr 08 2010 Dave Airlie <airlied@redhat.com>
- Backport radeon r800 modesetting support

* Wed Apr 07 2010 Chuck Ebbert <cebbert@redhat.com>
- Disable async multicore RAID4/5/6 stripe processing (F12#575402)

* Tue Apr 06 2010 Hans de Goede <hdegoede@redhat.com>
- gspca-vc032x: Use YUYV output for OV7670 (#537332)

* Mon Apr 05 2010 Chuck Ebbert <cebbert@redhat.com>
- Build eeepc-laptop driver for x86_64 (#565582)

* Mon Apr 05 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.33.2
- Dropped patches merged upstream:
    coredump-uid-pipe-check.patch
    iwlwifi-use-dma_alloc_coherent.patch
    r8169-offical-fix-for-CVE-2009-4537.patch
- Dropped from drm-nouveau-updates.patch:
    "drm/nouveau: report unknown connector state if lid closed"
- New sparc64 config option:
    CONFIG_FB_XVR1000=y
- Reverted from upstream:
    usb-qcserial-add-new-device-ids.patch: Already in wwan-update patch

* Mon Apr 05 2010 Chuck Ebbert <cebbert@redhat.com>
- Comment out acpi-ec-add-delay-before-write.patch: breaks
  boot on some machines.

* Mon Apr 05 2010 Jarod Wilson <jarod@redhat.com> 2.6.33.1-32
- Fix oops in lirc_it87 driver (#579270)
- Support more imon 0xffdc key combinations

* Sat Apr 03 2010 Chuck Ebbert <cebbert@redhat.com>
- Build all of the DVB frontend drivers instead of just the automatically
  selected ones. (#578755)

* Thu Apr 01 2010 Matthew Garrett <mjg@redhat.com>
- drm-intel-acpi-populate-didl.patch: Fix brightness hotkeys on some machines
- linux-2.6-usb-wwan-update.patch: Update wwan code and fix qcserial

* Wed Mar 31 2010 Matthew Garrett <mjg@redhat.com>
- drm-intel-make-lvds-work.patch: Make sure LVDS gets turned back on

* Tue Mar 30 2010 Chuck Ebbert <cebbert@redhat.com>
- Allow setting buildid on both command line and in the SRPM.

* Tue Mar 30 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.33.1-26
- r8169-offical-fix-for-CVE-2009-4537.patch

* Tue Mar 30 2010 Chuck Ebbert <cebbert@redhat.com>
- ACPI EC fixes pending upstream:
   acpi-ec-add-delay-before-write.patch
   acpi-ec-allow-multibyte-access-to-ec.patch

* Tue Mar 30 2010 Dave Jones <davej@redhat.com>
- Fix broken locking in cpufreq.

* Tue Mar 30 2010 John W. Linville <linville@redhat.com> 2.6.33.1-24
- Avoid null pointer dereference introduced by 'ssb: check for sprom' (#577463)

* Mon Mar 29 2010 John W. Linville <linville@redhat.com> 2.6.33.1-23
- iwlwifi: reset card during probe (#557084)
- iwlwifi: use dma_alloc_coherent (#574146)

* Mon Mar 29 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33.1-22
- nouveau: sync with nouveau upstream

* Wed Mar 24 2010 Josef Bacik <josef@toxicpanda.com> 2.6.33.1-21
- Update btrfs so it includes the default subvolume stuff, for the rollback
  feature

* Mon Mar 22 2010 Jarod Wilson <jarod@redhat.com>
- A few more imon driver button additions
- Fix minor init issue w/topseed 0x0008 mceusb transceivers

* Fri Mar 19 2010 John W. Linville <linville@redhat.com> 2.6.33.1-19
- ssb: check for sprom (#533746)

* Fri Mar 19 2010 Jarod Wilson <jarod@redhat.com> 2.6.33.1-18
- Improve mouse button and pad handling on 0xffdc imon devices
- Add xmit support to topseed 0x0008 lirc_mceusb transceiver

* Fri Mar 19 2010 David Woodhouse <David.Woodhouse@intel.com>
- Apply fix for #538163 again (Cantiga shadow GTT chipset b0rkage).

* Fri Mar 19 2010 Hans de Goede <hdegoede@redhat.com>
- Cherry pick various webcam driver fixes
  (#571188, #572302, #572373)

* Thu Mar 18 2010 Neil Horman <nhorman@redhat.com>
- Disable TIPC protocol in config

* Wed Mar 17 2010 Jarod Wilson <jarod@redhat.com>
- lirc driver update:
  * fix lirc_i2c on cx2341x hauppauge cards (#573675)
  * fix null ptr deref in lirc_imon (#545599)
  * fix lirc_zilog on cx2341x hauppauge cards
  * adds a few new lirc_mceusb device ids
- imon input layer driver update, adds better support for 0xffdc
  devices and handles failed key lookups better

* Tue Mar 16 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.33.1

* Tue Mar 16 2010 Chuck Ebbert <cebbert@redhat.com>
- Add examples.txt to perf docs, require libdwarf with perf package.
  (#568309, #569506)

* Mon Mar 15 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.33.1-rc1
- Drop merged patch:
  x86-pci-prevent-mmconfig-memory-corruption.patch
- Revert V4l patch we already have:
  v4l-dvb-13991-gspca_mr973010a-fix-cif-type-1-cameras-not-streaming-on-uhci-controllers.patch

* Mon Mar 15 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: pull in more fixes from upstream

* Sat Mar 06 2010 Kyle McMartin <kyle@redhat.com>
- Add libdwarf dep if %with_perftool.

* Fri Mar 05 2010 Kyle McMartin <kyle@redhat.com>
- Fix race between hvc_close and hvc_remove. (rhbz#568621)

* Thu Mar 04 2010 Kyle McMartin <kyle@redhat.com>
- Enable CGROUP_DEBUG.

* Mon Mar 01 2010 Dave Jones <davej@redhat.com>
- Don't own /usr/src/kernels any more, it's now owned by filesystem. (#569438)

* Sat Feb 27 2010 Chuck Ebbert <cebbert@redhat.com>
- Add patch from the 2.6.33 stable queue to fix memory corruption
  in the PCI MMCONFIG code.

* Thu Feb 25 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: rebase to nouveau/linux-2.6 git

* Wed Feb 24 2010 Chuck Ebbert <cebbert@redhat.com>
- Drop/clear obsolete V4L patches, use ApplyOptionalPatch
- Fix two typos in config-generic probably caused by vi users

* Wed Feb 24 2010 Dave Jones <davej@redhat.com>
- Remove unnecessary redefinition of KEY_RFKILL from linux-2.6-rfkill-all.patch

* Wed Feb 24 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-1
- Linux 2.6.33

* Wed Feb 24 2010 Dave Jones <davej@redhat.com> 2.6.33-0.53.rc8.git9
- 2.6.33-rc8-git9
- dropped: drm-nouveau-old-vgaload.patch - merged upstream.
- dropped: drm-nouveau-gf8-igp.patch - merged upstream.

* Tue Feb 23 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33-0.52.rc8.git6
- nouveau: bring to latest upstream, reorganise patches to be more sensible

* Mon Feb 22 2010 Kyle McMartin <kyle@redhat.com>
- coredump-uid-pipe-check.patch: commit it to a useful branch.

* Mon Feb 22 2010 Dave Jones <davej@redhat.com> 2.6.33-0.50.rc8.git6
- 2.6.33-rc8-git6

* Sun Feb 21 2010 Hans de Goede <hdegoede@redhat.com>
- Rebase gspca usb webcam driver + sub drivers to latest upstream, this
  adds support for the following webcam bridge chipsets: benq, cpia1, sn9c2028;
  and support for new devices and many bugfixes in other gspca-subdrivers

* Fri Feb 19 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.48.rc8.git4
- 2.6.33-rc8-git4

* Wed Feb 17 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.33-0.47.rc8.git1
- nouveau: update to new kernel interface
- drm_nouveau_ucode.patch: drop, in linux-firmware now

* Tue Feb 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.46.rc8.git1
- 2.6.33-rc8-git1
- virt_console-rollup.patch: fixes from linux-next from Amit.

* Mon Feb 15 2010 Neil Horman <nhorman@redhat.com>
- Refactor usermodehelper code and change recursion check for abrt
  with linux-2.6-umh-refactor.patch from -mm
  fixes bz 557386

* Fri Feb 12 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33-0.44.rc8
- 2.6.33-rc8

* Fri Feb 12 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33-0.43.rc7.git6
- 2.6.33-rc7-git6

* Thu Feb 11 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33-0.42.rc7.git5
- 2.6.33-rc7-git5
- Drop merged patches:
  fix-conntrack-bug-with-namespaces.patch
  commit ad60a9154887bb6162e427b0969fefd2f34e94a6 from git-bluetooth.patch

* Mon Feb 08 2010 Josh Boyer <jwboyer@gmail.com>
- Drop ppc ps3_storage and imac-transparent bridge patches

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.40.rc7.git0
- Add libdwarf-devel to build deps so perf gets linked to it.

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com>
- virt_console-rollup.patch, for feature F13/VirtioSerial, patches
  are all targetted at 2.6.34 (and in linux-next.)

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com>
- git-bluetooth.patch: selection of backports from next for hadess.
  (rhbz#562245)

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.36.rc7.git0
- Linux 2.6.33-rc7 (oops, jumped the gun on -git6 I guess. :)

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com>
- 2.6.33-rc6-git6

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com>
- Hack around delay loading microcode.ko, on intel, we don't split out
  the firmware into cpuid specific versions (in fact, I don't know who does...)
  so just patch out the request_firmware calls in microcode_intel.c, and
  microcode_ctl.init will do the right thing. (fixes rhbz#560031)
  (side note: I'll fix microcode_ctl to do one better at some point.)

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com>
- Don't want linux-firmware if %with_firmware, yet. (Think F-11/F-12 2.6.33)

* Fri Feb 05 2010 Peter Jones <pjones@redhat.com>
- Move initrd creation to %%posttrans
  Resolves: rhbz#557922

* Fri Feb 05 2010 Kyle McMartin <kyle@redhat.com>
- If %with_firmware, continue with kernel-firmware, otherwise prereq on the
  separate linux-firmware pkg. Thanks to dzickus for noticing.

* Thu Feb 04 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.29.rc6.git4
- 2.6.33-rc6-git4

* Wed Feb 03 2010 Kyle McMartin <kyle@redhat.com>
- prevent-runtime-conntrack-changes.patch: fix another conntrack issue
  identified by jcm.

* Wed Feb 03 2010 Kyle McMartin <kyle@redhat.com>
- fix-conntrack-bug-with-namespaces.patch: Patch for issue identified
  by jcm. (Ref: http://lkml.org/lkml/2010/2/3/112)

* Mon Feb 02 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33-0.26.rc6.git1
- 2.6.33-rc6-git1

* Fri Jan 29 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.33-0.25.rc6.git0
- 2.6.33-rc6

* Wed Jan 27 2010 Roland McGrath <roland@redhat.com> 2.6.33-0.24.rc5.git1
- Fix include/ copying for kernel-devel.

* Mon Jan 25 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.23.rc5.git1
- 2.6.33-rc5-git1
- arm: MTD_PISMO is not set

* Mon Jan 25 2010 Dave Jones <davej@redhat.com>
- Disable CONFIG_X86_CPU_DEBUG

* Mon Jan 25 2010 Josh Boyer <jwboyer@gmail.com>
- Turn off CONFIG_USB_FHCI_HCD.  It doesn't build

* Fri Jan 22 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.20.rc5.git0
- 2.6.33-rc5

* Thu Jan 21 2010 Jarod Wilson <jarod@redhat.com>
- Merge crystalhd powerpc build fix from airlied

* Wed Jan 20 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.18.rc4.git7
- 2.6.32-rc4-git7
- dvb mantis drivers as modules

* Wed Jan 20 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.17.rc4.git6
- add appleir usb driver

* Mon Jan 18 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.16.rc4.git6
- 2.6.33-rc4-git6
- execshield: rebase for mm_types.h reject

* Mon Jan 18 2010 Kyle McMartin <kyle@redhat.com>
- vhost_net-rollup.patch: https://fedoraproject.org/wiki/Features/VHostNet
  from davem/net-next-2.6.git

* Sat Jan 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.14.rc4.git3
- DEBUG_STRICT_USER_COPY_CHECKS off for now, tickles issue in lirc_it87.c

* Sat Jan 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.13.rc4.git3
- 2.6.33-rc4-git3

* Thu Jan 14 2010 Steve Dickson <steved@redhat.com>
- Enabled the NFS4.1 (CONFIG_NFS_V4_1) kernel config

* Wed Jan 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.11.rc4
- Linux 2.6.33-rc4

* Wed Jan 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.33-0.10.rc3.git5
- 2.6.33-rc3-git5

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com>
- Add fbdev fix for multi-card primary console on x86-64
- clean up all the drm- patches

* Tue Jan 12 2010 Jarod Wilson <jarod@redhat.com>
- Update lirc patch for 2.6.33 kfifo changes
- Add Broadcom Crystal HD video decoder driver from staging

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com>
- include/asm is gone, kludge it for now.

* Mon Jan 11 2010 Dave Jones <davej@redhat.com>
- Rebase exec-shield.

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com>
- drop e1000 patch.

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com>
- lirc broken due to kfifo mess.

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com>
- drm-intel-big-hammer: fix IS_I855 macro.

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.33-rc3
- utrace: rebased from roland's people page.
- via-hwmon-temp-sensor.patch: upstream.
- linux-2.6-defaults-alsa-hda-beep-off.patch: new config option supercedes.
- readd nouveau ctxprogs as firmware/ like it should be.
- linux-2.6-pci-cacheline-sizing.patch: upstream.
- linux-2.6-intel-agp-clear-gtt.patch: upstream.
- linux-2.6-nfsd4-proots.patch: upstream?
- rebased the rest.

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.3-21
- Linux 2.6.32.3
- drm-intel-no-tv-hotplug.patch: re-add lost patch from F-12
  2.6.31 (#522611, #544671)

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.2-20
- Re-enable ATM_HE (#545289)

* Fri Jan 08 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.2-19
- Add another symbol to look for when generating modules.block

* Thu Jan 07 2010 David Woodhouse <David.Woodhouse@intel.com> 2.6.32.2-18
- Drop kernel-firmware package now that it's packaged separately.

* Mon Jan 04 2010 Dave Jones <davej@redhat.com>
- Drop some of the vm/spinlock taint patches. dump_stack() already does same.

* Thu Dec 24 2009 Kyle McMartin <kyle@redhat.com> 2.6.32.2-15
- Add patch from dri-devel to fix vblanks on r600.
  [http://marc.info/?l=dri-devel&m=126137027403059&w=2]

* Fri Dec 18 2009 Kyle McMartin <kyle@redhat.com> 2.6.32.2-14
- Linux 2.6.32.2
- dropped upstream patches.

* Fri Dec 18 2009 Roland McGrath <roland@redhat.com> - 2.6.32.1-13
- minor utrace update

* Thu Dec 17 2009 Matthew Garrett <mjg@redhat.com> 2.6.32.1-12
- linux-2.6-driver-level-usb-autosuspend.diff: fix so it works properly...
- linux-2.6-fix-btusb-autosuspend.patch: avoid bluetooth connection drops
- linux-2.6-enable-btusb-autosuspend.patch: and default it to on
- linux-2.6-autoload-wmi.patch: autoload WMI drivers

* Thu Dec 17 2009 Jarod Wilson <jarod@redhat.com> 2.6.32.1-11
- Split off onboard decode imon devices into pure input driver,
  leaving lirc_imon for the ancient imon devices only
- Fix NULL ptr deref in lirc_serial (#543886)
- Assorted lirc_mceusb fixups suggested by Mauro
- Dropped compat ioctls from lirc_dev, main ioctls should now be
  compatible between 32-bit and 64-bit (also at Mauro's suggestion)

* Wed Dec 16 2009 Roland McGrath <roland@redhat.com> 2.6.32.1-10
- utrace update, now testing the utrace-based ptrace!

* Mon Dec 14 2009 Kyle McMartin <kyle@redhat.com> 2.6.32.1-9
- 2.6.32.1
- ext4 patches and more...

* Wed Dec 09 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-8
- Add a patch off lkml from krh to fix perf when DEBUG_PERF_USE_VMALLOC
  (rhbz#542791)
- Re-enable CONFIG_DEBUG_PERF_USE_VMALLOC on debug kernels.

* Wed Dec 09 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-7
- ext4-fix-insufficient-checks-in-EXT4_IOC_MOVE_EXT.patch: CVE-2009-4131
  fix insufficient permission checking which could result in arbitrary
  data corruption by a local unprivileged user.

* Tue Dec 08 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.32-6
- Copy fix for #540580 from F-12.

* Tue Dec 08 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-5
- new rpm changes:
 - %{PACKAGE_VERSION} -> %{version}
 - %{PACKAGE_RELEASE} -> %{release}

* Tue Dec 08 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-4
- Disable CONFIG_DEBUG_PERF_USE_VMALLOC for now, causes issues
  on x86_64. (rhbz#542791)

* Mon Dec  7 2009 Justin M. Forbes <jforbes@redhat.com> 2.6.32-3
- Allow userspace to adjust kvmclock offset (#530389)

* Mon Dec  7 2009 Steve Dickson <steved@redhat.com> 2.6.32-2
- Updated the NFS4 pseudo root code to the latest release.

* Thu Dec 03 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-1
- Linux 2.6.32

* Wed Dec 02 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.65.rc8.git5
- 2.6.32-rc8-git5
- nuke 9p cachefiles fix, upstream.
- SLOW_WORK_PROC was renamed to SLOW_WORK_DEBUG, debugfs instead of procfs.

* Wed Dec 02 2009 John W. Linville <linville@redhat.com> 2.6.32-0.64.rc8.git2
- ath9k: add fixes suggested by upstream maintainer

* Wed Dec 02 2009 David Woodhouse <David.Woodhouse@intel.com> 2.6.32-0.63.rc8.git2
- forward port IOMMU fixes from F-12 for HP BIOS brokenness
- Fix oops with intel_iommu=igfx_off
- agp/intel: Clear full GTT at startup

* Wed Dec 02 2009 Dave Airlie <airlied@redhat.com> 2.6.32-0.62.rc8.git2
- forward port radeon fixes from F-12 + add radeon display port support

* Mon Nov 30 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.61.rc8.git2
- fix-9p-fscache.patch: fix build.

* Mon Nov 30 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.60.rc8.git2
- 2.6.32-rc8-git2 daily snapshot
- nuke include/generated nuke-age since the patch was reverted upstream
- config changes:
 - generic:
  +CONFIG_FSCACHE_OBJECT_LIST=y
  +CONFIG_SLOW_WORK_PROC=y

* Mon Nov 30 2009 Kyle McMartin <kyle@redhat.com>
- drm-i915-fix-sync-to-vbl-when-vga-is-off.patch: add, (rhbz#541670)

* Sun Nov 29 2009 Kyle McMartin <kyle@redhat.com>
- linux-2.6-sysrq-c.patch: drop, was made consistent upstream.

* Sat Nov 28 2009 Jarod Wilson <jarod@redhat.com> 2.6.32-0.55.rc8.git1
- add device name to lirc_zilog, fixes issues w/multiple target devices
- add lirc_imon pure input mode support for onboard decode devices

* Fri Nov 27 2009 Dave Airlie <airlied@redhat.com> 2.6.32-0.54.rc8.git1
- attempt to put nouveau back - same patch as F-12 should work

* Mon Nov 23 2009 Roland McGrath <roland@redhat.com>
- Install vmlinux.id file in kernel-devel rpm.

* Fri Nov 20 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.32-0.52.rc8.git1
- 2.6.32-rc8-git1
- Enable CONFIG_MEMORY_HOTPLUG (and HOTREMOVE) on x86_64

* Thu Nov 19 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.51.rc7.git2
- Oops, re-enable debug builds for rawhide... didn't mean to commit that.

* Thu Nov 19 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.50.rc7.git2
- Disable FUNCTION_TRACER and DYNAMIC_FTRACE in non-debug builds for
  Fedora 13. Some pondering required to see if it's actually worth doing
  though. Anecdotal evidence worth half as much as benchmarks.
  STACK_TRACER selects FUNCTION_TRACER, so it has to go off too, sadly,
  since it hooks every mcount to log the stack depth for the task.

* Thu Nov 19 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.49.rc7.git2
- 2.6.32-rc7-git2

* Mon Nov 16 2009 Dave Airlie <airlied@redhat.com> 2.6.32-0.48.rc7.git1
- backout gpg change now that koji is fixed

* Sun Nov 15 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.32-0.47.rc7.git1
- Buildrequire gpg

* Sun Nov 15 2009 Chuck Ebbert <cebbert@redhat.com>
- Fix oops in VIA Padlock driver.

* Sun Nov 15 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.32-rc7-git1

* Fri Nov 13 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.32-rc7

* Thu Nov 05 2009 Jarod Wilson <jarod@redhat.com>
- Add --with dbgonly rpmbuild option to build only debug kernels

* Wed Nov 04 2009 Kyle McMartin <kyle@redhat.com>
- Make JBD2_DEBUG a toggleable config option.

* Wed Nov 04 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.39.rc6.git0
- 2.6.32-rc6, fix for NULL ptr deref in cfg80211.

* Mon Nov 02 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.39.rc5.git6
- 2.6.32-rc5-git6 (with sandeen's reversion of "ext4: Remove journal_checksum
  mount option and enable it by default")

* Mon Nov 02 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.32-rc5-git5

* Tue Oct 27 2009 John W. Linville <linville@redhat.com>
- Disable build of prism54 module

* Tue Oct 27 2009 Dave Airlie <airlied@redhat.com>
- Get dd command line args correct.

* Mon Oct 26 2009 Dave Jones <davej@redhat.com>
- Make a 20MB initramfs file so rpm gets its diskspace calculations right. (#530778)

* Sat Oct 23 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.32-rc5-git3
- Drop merged patch:
  linux-2.6-virtio_blk-revert-QUEUE_FLAG_VIRT-addition.patch

* Sat Oct 17 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.32-0.33.rc5.git1
- 2.6.32-rc5-git1

* Fri Oct 16 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.32-rc5
- New config option: CONFIG_VMXNET3=m

* Wed Oct 14 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.32-rc4-git4

* Wed Oct 14 2009 Steve Dickson <steved@redhat.com>
- Updated the NFS v4 pseudo root patch so it will apply
- Fixed hang during NFS installs (bz 528537)

* Wed Oct 14 2009 Peter Jones <pjones@redhat.com>
- Add scsi_register_device_handler to modules.block's symbol list so
  we'll have scsi device handlers in installer images.

* Tue Oct 13 2009 Kyle McMartin <kyle@redhat.com>
- Always build perf docs, regardless of whether we build kernel-doc.
  Seems rather unfair to not ship the manpages half the time.
  Also, drop BuildRequires %if when not with_doc, the rules about %if
  there are f*!&^ing complicated.

* Tue Oct 13 2009 Kyle McMartin <kyle@redhat.com>
- Build perf manpages properly.

* Tue Oct 13 2009 Dave Airlie <airlied@redhat.com>
- cleanup some of drm vga arb bits that are upstream

* Mon Oct 12 2009 Jarod Wilson <jarod@redhat.com>
- Merge lirc compile fixes into lirc patch
- Refresh lirc patch with additional irq handling fixage
- Fix IR transmit on port 1 of 1st-gen mceusb transceiver
- Support another mouse button variant on imon devices

* Mon Oct 12 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.32-0.24.rc4.git0
- Last-minute USB fix from upstream.

* Sun Oct 11 2009 Chuck Ebbert <cebbert@redhat.com>
- Fix lirc build after header changes.
- Fix bug in lirc interrupt processing.

* Sun Oct 11 2009 Chuck Ebbert <cebbert@redhat.com>
- Fix up multiple definition of debug options
  (EXT4_DEBUG, DEBUG_FORCE_WEAK_PER_CPU)

* Sun Oct 11 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.32-rc4
- New config options:
  CONFIG_BE2ISCSI=m
  CONFIG_SCSI_BFA_FC=m
  CONFIG_USB_MUSB_HDRC is not set

* Sun Oct 11 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.32-rc3-git3

* Thu Oct 08 2009 Ben Skeggs <bskeggs@redhat.com>
- ppc: compile nvidiafb as a module only, nvidiafb+nouveau = bang! (rh#491308)

* Wed Oct 07 2009 Dave Jones <davej@redhat.com>
- Enable FUNCTION_GRAPH_TRACER on x86-64.

* Wed Oct 07 2009 Dave Jones <davej@redhat.com>
- Disable CONFIG_IRQSOFF_TRACER on srostedt's recommendation.
  (Adds unwanted overhead when not in use).

* Sun Oct 04 2009 Kyle McMartin <kyle@redhat.com> 2.6.32-0.17.rc3.git0
- 2.6.32-rc3 (bah, rebase script didn't catch it.)

* Sun Oct 04 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.32-rc1-git7
- [x86,x86_64] ACPI_PROCESSOR_AGGREGATOR=m

* Mon Sep 28 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.32-rc1
- rebased crash-driver patchset, ia64_ksyms.c conflicts. move x86 crash.h
  file to the right place.
- full changelog forthcoming & to fedora-kernel-list.

* Mon Sep 28 2009 Kyle McMartin <kyle@redhat.com>
- sick of rejects.

* Mon Sep 28 2009 Chuck Ebbert <cebbert@redhat.com>
- Fix up some items missing in make debug vs. make release,
  rearrange so the options are in the same order.
- Add new debug options:
  CONFIG_EXT4_DEBUG
  CONFIG_DEBUG_FORCE_WEAK_PER_CPU

* Sun Sep 27 2009 Kyle McMartin <kyle@redhat.com>
- Must now make mrproper after each config pass, due to Kbuild
  stashing away the $ARCH variable.

* Sun Sep 27 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.31-git18
- rebased:
 - hdpvr-ir-enable.patch
 - linux-2.6-build-nonintconfig.patch
 - linux-2.6-debug-sizeof-structs.patch
 - linux-2.6-debug-vm-would-have-oomkilled.patch
 - linux-2.6-execshield.patch
 - linux-2.6-makefile-after_link.patch
 - linux-2.6-serial-460800.patch
 - linux-2.6-utrace.patch
 - via-hwmon-temp-sensor.patch
- merged:
 - linux-2.6-tracehook.patch
 - linux-2.6-die-closed-source-bios-muppets-die.patch
 - linux-2.6-intel-iommu-updates.patch
 - linux-2.6-ksm.patch
 - linux-2.6-ksm-updates.patch
 - linux-2.6-ksm-fix-munlock.patch
 - linux-2.6-vga-arb.patch
 - v4l-dvb-fix-cx25840-firmware-loading.patch
 - linux-2.6-rtc-show-hctosys.patch

* Fri Sep 18 2009 Dave Jones <davej@redhat.com>
- %ghost the dracut initramfs file.

* Thu Sep 17 2009 Hans de Goede <hdegoede@redhat.com>
- Now that we have %%post generation of dracut images we do not need to
  Require dracut-kernel anymore

* Thu Sep 17 2009 Chuck Ebbert <cebbert@redhat.com>
- Disable drm-nouveau too -- it won't build without other
  drm updates.

* Wed Sep 16 2009 Roland McGrath <roland@redhat.com>
- Remove workaround for gcc bug #521991, now fixed.

* Tue Sep 15 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.31-git4
- rebased:
 - linux-2.6-execshield.patch: split paravirt_types.h
 - linux-2.6-buildnonintconfig.patch
- disabled:
 - ksm, drm.
- merged:
 - linux-2.6-kvm-pvmmu-do-not-batch-pte-updates-from-interrupt-context.patch
 - linux-2.6-kvm-vmx-check-cpl-before-emulating-debug-register-access.patch
 - linux-2.6-use-__pa_symbol-to-calculate-address-of-C-symbol.patch
 - linux-2.6-xen-stack-protector-fix.patch
 - linux-2.6-bluetooth-autosuspend.diff
 - hid-ignore-all-recent-imon-devices.patch
- config changes:
 - arm:
  - CONFIG_HIGHPTE off, seems safer this way.
 - generic:
  - RDS_RDMA/RDS_TCP=m
  - SCSI_PMCRAID=m
  - WLAN=y, CFG80211_DEFAULT_PS=y, NL80211_TESTMODE off.
  - WL12XX=m
  - B43_PHY_LP=y
  - BT_MRVL=m
  - new MISDN stuff modular.
 - sparc:
  - enable PERF_COUNTERS & EVENT_PROFILE
 - ppc:
  - XILINX_EMACSLITE=m

* Mon Sep 14 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-git2
- Drop merged patches:
  sched-introduce-SCHED_RESET_ON_FORK-scheduling-policy-flag.patch
  linux-2.6-nfs4-ver4opt.patch
  linux-2.6-alsa-improve-hda-powerdown.patch
  alsa-tell-user-that-stream-to-be-rewound-is-suspended.patch
  linux-2.6-ahci-export-capabilities.patch
- New s390 config option:
   CONFIG_SCLP_ASYNC=m
- New generic config options:
   CONFIG_ATA_VERBOSE_ERROR=y
   CONFIG_PATA_RDC=m
   CONFIG_SOUND_OSS_CORE_PRECLAIM=y
   CONFIG_SND_HDA_PATCH_LOADER=y
   CONFIG_SND_HDA_CODEC_CIRRUS=y
   CONFIG_OPROFILE_EVENT_MULTIPLEX=y
   CONFIG_CRYPTO_VMAC=m
   CONFIG_CRYPTO_GHASH=m
- New debug option:
   CONFIG_DEBUG_CREDENTIALS=y in debug kernels

* Mon Sep 14 2009 Steve Dickson <steved@redhat.com>
- Added support for -o v4 mount parsing

* Fri Sep 11 2009 Dave Jones <davej@redhat.com>
- Apply NX/RO to modules

* Fri Sep 11 2009 Dave Jones <davej@redhat.com>
- Mark kernel data section as NX

* Fri Sep 11 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: bring in Matthew Garret's initial switchable graphics support

* Fri Sep 11 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: fixed use of strap-based panel mode when required (rh#522649)
- nouveau: temporarily block accel on NVAC chipsets (rh#522361, rh#522575)

* Thu Sep 10 2009 Matthew Garrett <mjg@redhat.com>
- linux-2.6-ahci-export-capabilities.patch: Backport from upstream
- linux-2.6-rtc-show-hctosys.patch: Export the hctosys state of an rtc
- linux-2.6-rfkill-all.patch: Support for keys that toggle all rfkill state

* Thu Sep 10 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: add some scaler-only modes for LVDS, GEM/TTM fixes

* Wed Sep 09 2009 Dennis Gilmore <dennis@ausil.us> 2.6.31-2
- touch the dracut initrd file when using %%{with_dracut}

* Wed Sep 09 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-1
- Linux 2.6.31

* Wed Sep 09 2009 Chuck Ebbert <cebbert@redhat.com>
- Enable VXpocket and PDaudioCF PCMCIA sound drivers.

* Wed Sep 09 2009 Hans de Goede <hdegoede@redhat.com>
- Move to %%post generation of dracut initrd, because of GPL issues surrounding
  shipping a prebuild initrd
- Require grubby >= 7.0.4-1, for %%post generation

* Wed Sep  9 2009 Steve Dickson <steved@redhat.com>
- Updated the NFS4 pseudo root code to the latest release.

* Wed Sep 09 2009 Justin M. Forbes <jforbes@redhat.com>
- Revert virtio_blk to rotational mode. (#509383)

* Wed Sep 09 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.219.rc9.git
- uggh lost nouveau bits in page flip

* Wed Sep 09 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.218.rc9.git2
- fix r600 oops with page flip patch (#520766)

* Wed Sep 09 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: fix display resume on pre-G8x chips

* Wed Sep 09 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: add getparam to know using tile_flags is ok for scanout

* Wed Sep 09 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc9-git2

* Wed Sep  9 2009 Roland McGrath <roland@redhat.com> 2.6.31-0.214.rc9.git1
- compile with -fno-var-tracking-assignments, work around gcc bug #521991

* Wed Sep 09 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.213.rc9.git1
- fix two bugs in r600 kms, fencing + mobile lvds

* Tue Sep 08 2009 Ben Skeggs <bskeggs@redhat.com> 2.6.31-0.212.rc9.git1
- drm-nouveau.patch: fix ppc build

* Tue Sep 08 2009 Ben Skeggs <bskeggs@redhat.com> 2.6.31-0.211.rc9.git1
- drm-nouveau.patch: more misc fixes

* Tue Sep 08 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.210.rc9.git1
- drm-page-flip.patch: rebase again

* Tue Sep 08 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.209.rc9.git1
- drm-next.patch: fix r600 signal interruption return value

* Tue Sep 08 2009 Ben Skeggs <bskeggs@redhat.com> 2.6.31-0.208.rc9.git1
- drm-nouveau.patch: latest upstream + rebase onto drm-next

* Tue Sep 08 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.207.rc9.git1
- drm-vga-arb.patch: update to avoid lockdep + add r600 support

* Tue Sep 08 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.206.rc9.git1
- drm: rebase to drm-next - r600 accel + kms should start working now

* Mon Sep 07 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.205.rc9.git1
- 2.6.31-rc9-git1
- Temporarily hack the drm-next patch so it still applies; the result
  should still be safe to build.

* Sat Sep 05 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.204.rc9
- 2.6.31-rc9

* Fri Sep 04 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.203.rc8.git2
- Fix kernel build errors when building firmware by removing the
  .config file before that step and restoring it afterward.

* Thu Sep 03 2009 Adam Jackson <ajax@redhat.com>
- drm-ddc-caching-bug.patch: Empty the connector's mode list when it's
  disconnected.

* Thu Sep 03 2009 Jarod Wilson <jarod@redhat.com>
- Update hdpvr and lirc_zilog drivers for 2.6.31 i2c

* Thu Sep 03 2009 Justin M.Forbes <jforbes@redhat.com>
- Fix xen guest with stack protector. (#508120)
- Small kvm fixes.

* Wed Sep 02 2009 Adam Jackson <ajax@redhat.com> 2.6.31-0.199.rc8.git2
- drm-intel-pm.patch: Disable by default, too flickery on too many machines.
  Enable with i915.powersave=1.

* Wed Sep 02 2009 Dave Jones <davej@redhat.com>
- Add missing scriptlet dependancy. (#520788)

* Tue Sep 01 2009 Adam Jackson <ajax@redhat.com>
- Make DRM less chatty about EDID failures.  No one cares.

* Tue Sep 01 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc8-git2
- Blank out drm-intel-next: entire contents are now upstream.

* Tue Sep 01 2009 Dave Jones <davej@redhat.com>
- Make firmware buildarch noarch. (Suggested by drago01 on irc)

* Tue Sep 01 2009 Jarod Wilson <jarod@redhat.com>
- Fix up lirc_zilog to enable functional IR transmit and receive
  on the Hauppauge HD PVR
- Fix audio on PVR-500 when used in same system as HVR-1800 (#480728)

* Sun Aug 30 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc8-git1
- Drop linux-2.6-inotify-accounting.patch, merged upstream.

* Sun Aug 30 2009 Jarod Wilson <jarod@redhat.com>
- fix lirc_imon oops on older devices w/o tx ctrl ep (#520008)

* Fri Aug 28 2009 Eric Paris <eparis@redhat.com> 2.6.31-0.190.rc8
- fix inotify length accounting and send inotify events

* Fri Aug 28 2009 David Woodhouse <David.Woodhouse@intel.com>
- Enable Solos DSL driver

* Fri Aug 28 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc8

* Thu Aug 27 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.185.rc7.git6
- 2.6.31-rc7-git6
- Drop patch merged upstream:
  xen-fb-probe-fix.patch

* Thu Aug 27 2009 Adam Jackson <ajax@redhat.com>
- drm-rv710-ucode-fix.patch: Treat successful microcode load on RV710 as,
  you know, success. (#519718)

* Thu Aug 27 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7-git5
- Drop patch linux-2.6-ima-leak.patch, now merged upstream.

* Wed Aug 26 2009 Jarod Wilson <jarod@redhat.com>
- Fix up hdpvr ir enable patch for use w/modular i2c (David Engel)

* Wed Aug 26 2009 Eric Paris <eparis@redhat.com>
- fix iint_cache leak in IMA code
  drop the ima=0 patch

* Wed Aug 26 2009 Justin M. Forbes <jforbes@redhat.com>
- Fix munlock with KSM (#516909)
- Re-enable KSM

* Wed Aug 26 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7-git4
- Drop patches merged upstream:
  xen-x86-fix-stackprotect.patch
  xen-x86-no-stackprotect.patch

* Wed Aug 26 2009 Adam Jackson <ajax@redhat.com>
- drm-intel-next.patch: Update, various output setup fixes.

* Wed Aug 26 2009 David Woodhouse <David.Woodhouse@intel.com>
- Make WiMAX modular (#512070)

* Tue Aug 25 2009 Kyle McMartin <kyle@redhat.com>
- allow-disabling-ima.diff: debugging patch... adds ima=0 kernel
  param to disable initialization of IMA.

* Tue Aug 25 2009 Ben Skeggs <bskeggs@redhat.com> 2.6.31-0.174.rc7.git2
- drm-nouveau.patch: upstream update, pre-nv50 tv-out + misc fixes

* Tue Aug 25 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.173.rc7.git2
- Fix Xen boot (#508120)

* Tue Aug 25 2009 Dave Airlie <airlied@redhat.com>
- pull in drm-next tree + rebase around it

* Mon Aug 24 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7-git2

* Mon Aug 24 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7-git1

* Sat Aug 22 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7

* Thu Aug 20 2009 Mark McLoughlin <markmc@redhat.com>
- Disable LZMA for xen (#515831)

* Thu Aug 20 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc6-git5
- Fix up drm-r600-kms.patch
- Drop fix-perf-make-man-failure.patch

* Wed Aug 19 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc6-git5
- Revert linux-2.6-debug-vm-would-have-oomkilled.patch to v1.2
  because upstream changes to oom-kill.c were all reverted.

* Tue Aug 18 2009 Kyle McMartin <kyle@redhat.com>
- Fix up perf so that it builds docs now that they are fixed.
- with_docs disables perf docs too. be warned. (logic is that the
  build deps are (mostly) the same, so if you don't want one, odds are...)

* Tue Aug 18 2009 Dave Jones <davej@redhat.com>
- 2.6.31-rc6-git3

* Mon Aug 17 2009 Dave Jones <davej@redhat.com> 2.6.31-0.161.rc6.git2
- 2.6.31-rc6-git2

* Mon Aug 17 2009 Chuck Ebbert <cebbert@redhat.com>
- Stop generating the (unused) ppc64-kdump.config file.

* Mon Aug 17 2009 Jarod Wilson <jarod@redhat.com>
- Add new lirc driver for built-in ENE0100 device on some laptops

* Sun Aug 16 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.158.rc6
- Improve the perf script so it prints something helpful if the
  perf binary doesn't exist.

* Sat Aug 15 2009 Dave Jones <davej@redhat.com> 2.6.31-0.157.rc6
- Disable KSM patches on a hunch.  Chasing the "encrypted VGs don't work" bug.

* Fri Aug 14 2009 Dave Jones <davej@redhat.com> 2.6.31-0.155.rc6
- 2.6.31-rc6

* Wed Aug 12 2009 Kyle McMartin <kyle@redhat.com>
- fix perf.
- move perf to perf.$ver instead of perf-$ver...

* Wed Aug 12 2009 Dennis Gilmore <dennis@ausil.us>
- Obsolete kernel-smp on sparc64
- Require grubby >= 7.0.2-1 since thats what introduces the dracut options we use

* Wed Aug 12 2009 Kristian Høgsberg <krh@redhat.com>
- Fix drm-page-flip.patch to not break radeon kms and to not reset
  crtc offset into fb on flip.

* Wed Aug 12 2009 Adam Jackson <ajax@redhat.com>
- Update drm-intel-next patch

* Tue Aug 11 2009 Dennis Gilmore <dennis@ausil.us> - 2.6.31-0.149.rc5.git3
- disable building the -smp kernel on sparc64
- disable building kernel-perf on sparc64 syscalls not supported

* Tue Aug 11 2009 Eric Paris <eparis@redhat.com>
- Enable config IMA

* Tue Aug 11 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: various cleanups and fixes + more sanity checking in dma paths

* Mon Aug 10 2009 Jarod Wilson <jarod@redhat.com>
- Add new device ID to lirc_mceusb (#512483)
- Fix some lockdep false positives
- Add support for setting and enabling iMON clock via sysfs
- Add tunable pad threshold support to lirc_imon
- Add new pseudo-IR protocl to lirc_imon for universals w/o a pad
- Fix mouse device support on older iMON devices

* Mon Aug 10 2009 David Woodhouse <David.Woodhouse@intel.com> 2.6.31-0.145.rc5.git3
- Merge latest Intel IOMMU fixes and BIOS workarounds, re-enable by default.

* Sun Aug 09 2009 Kyle McMartin <kyle@redhat.com>
- btusb autosuspend: fix build on !CONFIG_PM by stubbing out
  suspend/resume methods.

* Sat Aug 08 2009 Dennis Gilmore <dennis@ausil.us> 2.6.31-0.141.rc5.git3
- disable kgdb on sparc64 uni-processor kernel
- set max cpus to 256 on sparc64
- enable AT keyboard on sparc64

* Fri Aug 07 2009 Justin M. Forbes <jforbes@redhat.com>
- Apply KSM updates from upstream

* Fri Aug 07 2009 Hans de Goede <hdegoede@redhat.com>
- When building a dracut generic initrd tell new-kernel-pkg to use that
  instead of running mkinitrd

* Fri Aug 07 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.139.rc5.git3
- drm-r600-kms.patch - update r600 KMS
- drm-radeon-fixes.patch - patches for queue to Linus

* Thu Aug 06 2009 Justin M. Forbes <jforbes@redhat.com> 2.6.31-0.138.rc5.git3
- Fix kvm virtio_blk errors (#514901)

* Thu Aug 06 2009 Adam Jackson <ajax@redhat.com>
- Hush DRM vblank warnings, they're constant (and harmless) under DRI2.

* Thu Aug 06 2009 Dave Airlie <airlied@redhat.com> 2.6.31.0.134.rc5.git3
- fixup vga arb warning at startup and handover between gpus

* Thu Aug 06 2009 Kyle McMartin <kyle@redhat.com> 2.6.31.0.133.rc5.git3
- die-floppy-die.patch: it's the 21st century, let's not rely on
  steam powered technology.

* Wed Aug 05 2009 Dave Airlie <airlied@redhat.com> 2.6.31.0.132.rc5.git3
- revert-ftrace-powerpc-snafu.patch - fix ppc build

* Wed Aug 05 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: respect nomodeset

* Wed Aug 05 2009 Chuck Ebbert <cebbert@redhat.com>
- Fix /usr/sbin/perf script. (#515494)

* Wed Aug 05 2009 Dave Jones <davej@redhat.com>
- Fix shift in pci cacheline size printk.

* Wed Aug 05 2009 Dave Airlie <airlied@redhat.com> 2.6.31.0.128.rc5.git3
- 2.6.31-rc5-git3
- drop cpufreq + set memory fixes

* Wed Aug 05 2009 Dave Airlie <airlied@redhat.com>
- Add Jeromes initial r600 kms work.
- rebase arb patch

* Tue Aug 04 2009 Kyle McMartin <kyle@redhat.com>
- alsa-tell-user-that-stream-to-be-rewound-is-suspended.patch: apply patch
  destined for 2.6.32, requested by Lennart.

* Tue Aug 04 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: more code share between nv50/<nv50 kms, bug fixes

* Tue Aug 04 2009 Dave Airlie <airlied@redhat.com>
- update VGA arb patches again

* Mon Aug 03 2009 Adam Jackson <ajax@redhat.com>
- Update intel drm from anholt's tree
- Rebase drm-intel-pm.patch to match
- Drop gen3 fb hack, merged
- Drop previous watermark setup change

* Mon Aug 03 2009 Dave Jones <davej@redhat.com> 2.6.31-0.122.rc5.git2
- 2.6.31-rc5-git2

* Mon Aug 03 2009 Adam Jackson <ajax@redhat.com>
- (Attempt to) fix watermark setup on Intel 9xx parts.

* Mon Aug 03 2009 Jarod Wilson <jarod@redhat.com>
- make usbhid driver ignore all recent SoundGraph iMON devices, so the
  lirc_imon driver can grab them instead

* Mon Aug 03 2009 Dave Airlie <airlied@redhat.com>
- update VGA arb patches

* Sat Aug 01 2009 David Woodhouse <David.Woodhouse@intel.com> 2.6.31-0.118.rc5
- Fix boot failures on ppc32 (#514010, #505071)

* Fri Jul 31 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.117.rc5
- Linux 2.6.31-rc5

* Fri Jul 31 2009 Matthew Garrett <mjg@redhat.com>
- linux-2.6-dell-laptop-rfkill-fix.patch: Fix up Dell rfkill

* Fri Jul 31 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: build against 2.6.31-rc4-git6, fix script parsing on some G8x chips

* Thu Jul 30 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.31-rc4-git6
  New config item: CONFIG_BATTERY_DS2782 is not set
- Add last-minute set_memory_wc() fix from LKML.

* Thu Jul 30 2009 Matthew Garrett <mjg@redhat.com>
- drm-intel-pm.patch: Don't reclock external outputs. Increase the reduced
   clock slightly to avoid upsetting some hardware. Disable renderclock
   adjustment for the moment - it's breaking on some hardware.

* Thu Jul 30 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: another DCB 1.5 entry, G80 corruption fixes, small <G80 KMS fix

* Thu Jul 30 2009 Dave Airlie <airlied@redhat.com>
- fix VGA ARB + kms

* Wed Jul 29 2009 Dave Jones <davej@redhat.com>
- Add support for dracut. (Harald Hoyer)

* Wed Jul 29 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: nv50/nva0 tiled scanout fixes, nv40 kms fixes

* Wed Jul 29 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.31-rc4-git3
- Drop linux-2.6-ecryptfs-overflow-fixes.patch, merged upstream now.

* Wed Jul 29 2009 Dave Airlie <airlied@redhat.com>
- update VGA arb patches

* Tue Jul 28 2009 Adam Jackson <ajax@redhat.com>
- Remove the pcspkr modalias.  If you're still living in 1994, load it
  by hand.

* Tue Jul 28 2009 Eric Sandeen <sandeen@redhat.com> 2.6.31-0.102.rc4.git2
- Fix eCryptfs overflow issues (CVE-2009-2406, CVE-2009-2407)

* Tue Jul 28 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.101.rc4.git2
- 2.6.31-rc4-git2
- rebase linux-2.6-fix-usb-serial-autosuspend.diff
- config changes:
 - USB_GSPCA_SN9C20X=m (_EVDEV=y)

* Tue Jul 28 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: cleanup userspace API, various bugfixes.
  Looks worse than it is, register macros got cleaned up, which
  touches pretty much everywhere..

* Mon Jul 27 2009 Adam Jackson <ajax@redhat.com>
- Warn quieter about not finding PCI bus parents for ROM BARs, they're
  not usually needed and there's nothing you can do about it anyway.

* Mon Jul 27 2009 Matthew Garrett <mjg@redhat.com>
- linux-2.6-alsa-improve-hda-powerdown.patch - attempt to reduce audio glitches
   caused by HDA powerdown
- disable CONFIG_DEBUG_KOBJECT again for now, since it produces huge dmesg spew

* Mon Jul 27 2009 Dave Airlie <airlied@redhat.com>
- update vga arb code

* Mon Jul 27 2009 Matthew Garrett <mjg@redhat.com>
- drm-intel-pm.patch - Add runtime PM for Intel graphics

* Fri Jul 24 2009 Kristian Høgsberg <krh@redhat.com>
- Add drm-page-flip.patch to support vsynced page flipping on intel
  chipsets.
- Really add patch.
- Fix patch to not break nouveau.

* Fri Jul 24 2009 Chuck Ebbert <cebbert@redhat.com>
- Enable CONFIG_DEBUG_KOBJECT in debug kernels. (#513606)

* Thu Jul 23 2009 Kyle McMartin <kyle@redhat.com>
- perf BuildRequires binutils-devel now.

* Thu Jul 23 2009 Justin M. Forbes <jforbes@redhat.com>
- Add KSM support

* Thu Jul 23 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.87.rc4
- Linux 2.6.31-rc4
- config changes:
 - USB_CDC_PHONET=m [all]
 - EVENT_PROFILE=y [i386, x86_64, powerpc, s390]

* Wed Jul 22 2009 Tom "spot" Callaway <tcallawa@redhat.com>
- We have to override the new %%install behavior because, well... the kernel is special.

* Wed Jul 22 2009 Dave Jones <davej@redhat.com>
- 2.6.31-rc3-git5

* Wed Jul 22 2009 Ben Skeggs <bskeggs@redhat.com> 2.6.31-0.82.rc3.git4
- Enable KMS for nouveau

* Wed Jul 22 2009 Ben Skeggs <bskeggs@redhat.com>
- Update nouveau from upstream (initial suspend/resume + misc bugfixes)

* Mon Jul 20 2009 Adam Jackson <ajax@redhat.com>
- Disable VGA arbiter patches for a moment

* Mon Jul 20 2009 Adam Jackson <ajax@redhat.com>
- Revive 4k framebuffers for intel gen3

* Mon Jul 20 2009 Dave Jones <davej@redhat.com> 2.6.31-0.78.rc3.git4
- Enable CONFIG_RTC_HCTOSYS (#489494)

* Mon Jul 20 2009 Dave Jones <davej@redhat.com> 2.6.31-0.77.rc3.git4
- Don't build 586 kernels any more.

* Sun Jul 19 2009 Dave Jones <davej@redhat.com> 2.6.31-0.75.rc3.git4
- build a 'full' package on i686 (Bill Nottingham)

* Sun Jul 19 2009 Dave Jones <davej@redhat.com> 2.6.31-0.74.rc3.git4
- 2.6.31-rc3-git4

* Sat Jul 18 2009 Matthew Garrett <mjg@redhat.com>
- linux-2.6-driver-level-usb-autosuspend.diff - allow drivers to enable autopm
- linux-2.6-fix-usb-serial-autosuspend.diff - fix generic usb-serial autopm
- linux-2.6-qcserial-autosuspend.diff - enable autopm by default on qcserial
- linux-2.6-bluetooth-autosuspend.diff - enable autopm by default on btusb
- linux-2.6-usb-uvc-autosuspend.diff - enable autopm by default on uvc

* Thu Jul 16 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc3-git3

* Thu Jul 16 2009 Matthew Garrett <mjg@redhat.com>
- linux-2.6-defaults-aspm.patch - default ASPM to on for PCIe >= 1.1 hardware

* Thu Jul 16 2009 Dave Airlie <airlied@redhat.com> 2.6.31-0.69.rc3
- linux-2.6-vga-arb.patch - add VGA arbiter.
- drm-vga-arb.patch - add VGA arbiter support to drm

* Tue Jul 14 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.68-rc3
- 2.6.31-rc3
- config changes:
 - RTL8192SU is not set, (staging)

* Mon Jul 13 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.67.rc2.git9
- 2.6.31-rc2-git9
- config changes:
 - BLK_DEV_OSD=m

* Mon Jul 13 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: update from upstream

* Fri Jul 10 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc2-git6
- Drop dmadebug-spinlock patch -- merged upstream.

* Fri Jul 10 2009 Dave Jones <davej@redhat.com> 2.6.31-0.64.rc2.git5
- Don't jump through hoops that ppc powerbooks have to on sensible systems
  in cpufreq_suspend.

* Fri Jul 10 2009 Dave Jones <davej@redhat.com>
- 2.6.31-rc2-git5

* Thu Jul 09 2009 Dave Jones <davej@redhat.com> 2.6.31-0.62.rc2.git4
- Use correct spinlock initialization in dma-debug

* Thu Jul 09 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.61.rc2.git4
- 2.6.31-rc2-git4

* Thu Jul 09 2009 Jarod Wilson <jarod@redhat.com>
- Enable IR receiver on the Hauppauge HD PVR
- Trim the changelog, axing everything before 2.6.29 (see cvs
  if you still really want to see that far back)

* Wed Jul 08 2009 Dave Jones <davej@redhat.com>
- Enable a bunch of debugging options that were missed somehow.

* Wed Jul 08 2009 Kyle McMartin <kyle@redhat.com>
- Bump NR_CPUS on x86_64 to 512.

* Wed Jul 08 2009 Adam Jackson <ajax@redhat.com>
- drm-no-gem-on-i8xx.patch: Drop, intel 2D driver requires GEM now. This
  should be entertaining.

* Wed Jul 08 2009 Kyle McMartin <kyle@redhat.com>
- First cut of /usr/sbin/perf wrapper script and 'perf'
  subpackage.

* Wed Jul 08 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.54.rc2.git2
- Rebase and re-apply all the Fedora-specific linux-2.6-debug-*
  patches.
- Cull a bunch of upstreamed patches from the spec.

* Wed Jul 08 2009 Steve Dickson <steved@redhat.com>
- Added NFSD v4 dynamic pseudo root patch which allows
  NFS v3 exports to be mounted by v4 clients.

* Tue Jul 07 2009 Jarod Wilson <jarod@redhat.com>
- See if we can't make lirc_streamzap behave better... (#508952)

* Tue Jul 07 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.47.rc2.git2
- 2.6.31-rc2-git2

* Tue Jul 07 2009 Jarod Wilson <jarod@redhat.com>
- Make lirc_i2c actually work with 2.6.31 i2c

* Mon Jul 06 2009 Chuck Ebbert <cebbert@redhat.com>
- Use LZMA for kernel compression on X86.

* Mon Jul 06 2009 Jarod Wilson <jarod@redhat.com>
- Hack up lirc_i2c and lirc_zilog to compile with 2.6.31 i2c
  changes. The drivers might not actually be functional now, but
  at least they compile again. Will fix later, if need be...

* Sat Jul 04 2009 Dave Jones <davej@redhat.com> 2.6.31-0.42.rc2
- 2.6.31-rc2

* Sat Jul 04 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc1-git11

* Fri Jul 03 2009 Hans de Goede <hdegoede@redhat.com>
- Disable v4l1 ov511 and quickcam_messenger drivers (obsoleted by
  v4l2 gspca subdrivers)

* Thu Jul 02 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.39.rc1.git9
- 2.6.31-rc1-git9
- linux-2.6-dm-fix-exstore-search.patch: similar patch merged upstream.

* Tue Jun 30 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.38.rc1.git7
- 2.6.31-rc1-git7

* Tue Jun 30 2009 Dave Jones <davej@redhat.com> 2.6.31-0.37.rc1.git5
- Disable kmemleak. Way too noisy, and not finding any real bugs.

* Tue Jun 30 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: match upstream

* Mon Jun 29 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.35.rc1.git5
- 2.6.31-rc1-git5
- CONFIG_LEDS_LP3944=m

* Mon Jun 29 2009 Chuck Ebbert <cebbert@redhat.com>
- Try to fix the dm overlay bug for real (#505121)

* Sat Jun 27 2009 Ben Skeggs <bskeggs@redhat.com> 2.6.31-0.33.rc1.git2
- drm-nouveau.patch: fix conflicts from 2.6.31-rc1-git2

* Fri Jun 26 2009 Dave Jones <davej@redhat.com> 2.6.31-0.31.rc1.git2
- Further improvements to kmemleak

* Fri Jun 26 2009 Dave Jones <davej@redhat.com> 2.6.31-0.30.rc1.git2
- 2.6.31-rc1-git2

* Fri Jun 26 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: latest upstream + reenable

* Thu Jun 25 2009 Dave Jones <davej@redhat.com> 2.6.31-0.29.rc1
- Make kmemleak scan process stacks by default.
  Should reduce false positives (which does also increase false negatives,
  but that's at least less noisy)

* Wed Jun 24 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.28.rc1
- 2.6.31-rc1
- linux-2.6-utrace.patch: rebase on kernel/Makefile changes
- config changes:
 - generic:
  - CONFIG_DM_LOG_USERSPACE=m
  - CONFIG_DM_MULTIPATH_QL=m
  - CONFIG_DM_MULTIPATH_ST=m
  - CONFIG_BATTERY_MAX17040=m
  - CONFIG_I2C_DESIGNWARE is off (depends on clk.h)

* Wed Jun 24 2009 Kyle McMartin <kyle@redhat.com>
- Move perf to /usr/libexec/perf-$KernelVer.

* Wed Jun 24 2009 Kyle McMartin <kyle@redhat.com>
- config changes:
 - generic:
  - CONFIG_SCSI_DEBUG=m (was off, requested by davidz)

* Wed Jun 24 2009 Dave Jones <davej@redhat.com> 2.6.31-0.22.rc0.git22
- 2.6.30-git22

* Tue Jun 23 2009 Dave Jones <davej@redhat.com> 2.6.31-0.22.rc0.git20
- 2.6.30-git20

* Mon Jun 22 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.24.rc0.git18
- Enable tools/perf, installed as /bin/perf-$KernelVer. Docs and a /bin/perf
  wrapper come next if this builds ok.

* Mon Jun 22 2009 Kyle McMartin <kyle@redhat.com>
- sched-introduce-SCHED_RESET_ON_FORK-scheduling-policy-flag.patch: pull in
  two fixes from Mike Galbraith from tip.git

* Sun Jun 21 2009 Dave Jones <davej@redhat.com> 2.6.31-0.21.rc0.git18
- Add patch to possibly fix the pktlen problem on via-velocity.

* Sun Jun 21 2009 Dave Jones <davej@redhat.com> 2.6.31-0.20.rc0.git18
- 2.6.30-git18
  VIA crypto & mmc patches now upstream.

* Sun Jun 21 2009 Dave Jones <davej@redhat.com>
- Determine cacheline sizes in a generic manner.

* Sun Jun 21 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.18.rc0.git17
- 2.6.30-git17
- Config changes:
  - powerpc32-generic
      CONFIG_PERF_COUNTERS=y
  - generic
      CONFIG_KEYBOARD_LM8323 is not set
      CONFIG_MOUSE_SYNAPTICS_I2C=m
      CONFIG_TOUCHSCREEN_EETI=m
      CONFIG_TOUCHSCREEN_W90X900=m
- Dropped agp-set_memory_ucwb.patch, all fixed upstream now.

* Sat Jun 20 2009 Kyle McMartin <kyle@redhat.com> 2.6.31.0.17.rc0.git15
- config changes:
 - ppc generic:
  - CONFIG_PPC_DISABLE_WERROR=y (switched... chrp fails otherwise, stack
    frame size.)

* Sat Jun 20 2009 Kyle McMartin <kyle@redhat.com> 2.6.31.0.16.rc0.git15
- 2.6.30-git15
- config changes:
 - generic:
  - CONFIG_LBDAF=y
 - staging:
  - CONFIG_USB_SERIAL_QUATECH2 is not set
  - CONFIG_VT6655 is not set
  - CONFIG_USB_CPC is not set
  - CONFIG_RDC_17F3101X is not set
  - CONFIG_FB_UDL is not set
 - ppc32:
  - CONFIG_KMETER1=y
 - ppc generic:
  - CONFIG_PPC_DISABLE_WERROR is not set
- lirc disabled due to i2c detach_client removal.

* Sat Jun 20 2009 Kyle McMartin <kyle@redhat.com>
- sched-introduce-SCHED_RESET_ON_FORK-scheduling-policy-flag.patch: add,
  queued in tip/sched/core (ca94c442535a44d508c99a77e54f21a59f4fc462)

* Fri Jun 19 2009 Kyle McMartin <kyle@redhat.com> 2.6.31.0.15.rc0.git14
- Fix up ptrace, hopefully. Builds on x86_64 at least.

* Fri Jun 19 2009 Chuck Ebbert <cebbert@redhat.com>
- linux-2.6-tip.git-203abd67b75f7714ce98ab0cdbd6cfd7ad79dec4.patch
  Fixes oops on boot with qemu (#507007)

* Fri Jun 19 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.13.rc0.git14
- 2.6.30-git14

* Fri Jun 19 2009 Chuck Ebbert <cebbert@redhat.com>
- Fix up the via-sdmmc and via-hwmon-temp-sensor patches.
- Drop VIA Padlock patches merged upstream:
    via-rng-enable-64bit.patch
    via-padlock-10-enable-64bit.patch
    via-padlock-20-add-x86-dependency.patch

* Thu Jun 18 2009 Kyle McMartin <kyle@redhat.com> 2.6.31-0.11.rc0.git13
- 2.6.30-git13
- config changes:
 - arm:
  - CONFIG_UACCESS_WITH_MEMCPY is not set
 - i686-PAE:
  - CONFIG_XEN_DEV_EVTCHN=m
  - CONFIG_XEN_SYS_HYPERVISOR=y
 - ia64:
  - CONFIG_RCU_FANOUT=64
 - nodebug:
  - CONFIG_DEBUG_KMEMLEAK is not set
  - CONFIG_DEBUG_KMEMLEAK_TEST=m
 - powerpc:
  - CONFIG_CAN_SJA1000_OF_PLATFORM=m
  - CONFIG_PPC_EMULATED_STATS=y
  - CONFIG_SWIOTLB=y
  - CONFIG_RDS is not set (broken on ppc32)
 - powerpc32:
  - CONFIG_RCU_FANOUT=32
 - powerpc64:
  - CONFIG_RCU_FANOUT=64
  - CONFIG_PERF_COUNTERS=y
 - s390x:
  - CONFIG_RCU_FANOUT=64
  - CONFIG_SECCOMP=y
  - CONFIG_PM=y
  - CONFIG_HIBERNATION=y
  - CONFIG_PM_STD_PARTITION="/dev/jokes"
 - sparc64:
  - CONFIG_RCU_FANOUT=64
 - x86:
  - CONFIG_RCU_FANOUT=32
  - CONFIG_IOMMU_STRESS is not set
  - CONFIG_PERF_COUNTERS=y
  - CONFIG_X86_OLD_MCE is not set
  - CONFIG_X86_MCE_INTEL=y
  - CONFIG_X86_MCE_AMD=y
  - CONFIG_X86_ANCIENT_MCE is not set
  - CONFIG_X86_MCE_INJECT is not set
 - x86_64:
  - CONFIG_EDAC_AMD64=m
  - CONFIG_EDAC_AMD64_ERROR_INJECTION is not set
  - CONFIG_XEN_DEV_EVTCHN=m
  - CONFIG_XEN_SYS_HYPERVISOR=y
  - CONFIG_RCU_FANOUT=64
  - CONFIG_IOMMU_STRESS is not set
  - CONFIG_PERF_COUNTERS=y
  - CONFIG_X86_MCE_INJECT is not set
 - generic:
  - CONFIG_RCU_FANOUT=32
  - CONFIG_MMC_SDHCI_PLTFM=m
  - CONFIG_MMC_CB710=m
  - CONFIG_CB710_CORE=m
  - CONFIG_CB710_DEBUG is not set
  - CONFIG_SCSI_MVSAS_DEBUG is not set
  - CONFIG_SCSI_BNX2_ISCSI=m
  - CONFIG_NETFILTER_XT_MATCH_OSF=m
  - CONFIG_RFKILL_INPUT=y (used to be =m, which was invalid)
  - CONFIG_DE2104X_DSL=0
  - CONFIG_KS8842 is not set
  - CONFIG_CFG80211_DEBUGFS=y
  - CONFIG_MAC80211_DEFAULT_PS=y
  - CONFIG_IWM=m
  - CONFIG_IWM_DEBUG is not set
  - CONFIG_RT2800USB=m
  - CONFIG_CAN_DEV=m
  - CONFIG_CAN_CALC_BITTIMING=y
  - CONFIG_CAN_SJA1000=m
  - CONFIG_CAN_SJA1000_PLATFORM=m
  - CONFIG_CAN_EMS_PCI=m
  - CONFIG_CAN_KVASER_PCI=m
  - CONFIG_EEPROM_MAX6875=m
  - CONFIG_SENSORS_TMP401=m
  - CONFIG_MEDIA_SUPPORT=m
  - CONFIG_SND_CTXFI=m
  - CONFIG_SND_LX6464ES=m
  - CONFIG_SND_HDA_CODEC_CA0110=y
  - CONFIG_USB_XHCI_HCD=m
  - CONFIG_USB_XHCI_HCD_DEBUGGING is not set
  - CONFIG_DRAGONRISE_FF=y (used to be =m)
  - CONFIG_GREENASIA_FF=y (used to be =m)
  - CONFIG_SMARTJOYPLUS_FF=y (used to be =m)
  - CONFIG_USB_NET_INT51X1=m
  - CONFIG_CUSE=m
  - CONFIG_FUNCTION_PROFILER=y
  - CONFIG_RING_BUFFER_BENCHMARK=m
  - CONFIG_REGULATOR_USERSPACE_CONSUMER=m
  - CONFIG_REGULATOR_MAX1586=m
  - CONFIG_REGULATOR_LP3971=m
  - CONFIG_RCU_FANOUT_EXACT is not set
  - CONFIG_DEFAULT_MMAP_MIN_ADDR=4096
  - CONFIG_FSNOTIFY=y
  - CONFIG_IEEE802154=m
  - CONFIG_IEEE802154_DRIVERS=m
  - CONFIG_IEEE802154_FAKEHARD=m
  - CONFIG_CNIC=m

* Wed Jun 17 2009 Jarod Wilson <jarod@redhat.com>
- New lirc_imon hotness, update 2:
  * support dual-interface devices with a single lirc device
  * directional pad functions as an input device mouse
  * touchscreen devices finally properly supported
  * support for using MCE/RC-6 protocol remotes
  * fix oops in RF remote association code (F10 bug #475496)
  * fix re-enabling case/panel buttons and/or knobs
- Add some misc additional lirc_mceusb2 transceiver IDs
- Add missing unregister_chrdev_region() call to lirc_dev exit
- Add it8720 support to lirc_it87

* Tue Jun 16 2009 Chuck Ebbert <cebbert@redhat.com>
- Update via-sdmmc driver

* Mon Jun 15 2009 Jarod Wilson <jarod@redhat.com>
- Update lirc patches w/new imon hotness

* Fri Jun 12 2009 Chuck Ebbert <cebbert@redhat.com>
- Update VIA temp sensor and mmc drivers.

* Fri Jun 12 2009 John W. Linville <linville@redhat.com> 2.6.30-6
- neigh: fix state transition INCOMPLETE->FAILED via Netlink request
- enable CONFIG_ARPD (used by OpenNHRP)

* Wed Jun 10 2009 Chuck Ebbert <cebbert@redhat.com>
- VIA Nano updates:
  Enable Padlock AES encryption and random number generator on x86-64
  Add via-sdmmc and via-cputemp drivers

* Wed Jun 10 2009 Kyle McMartin <kyle@redhat.com> 2.6.30-1
- Linux 2.6.30 rebase.

* Tue Jun 09 2009 John W. Linville <linville@tuxdriver.com>
- Clean-up some wireless bits in config-generic

* Tue Jun 09 2009 Chuck Ebbert <cebbert@redhat.com>
- Add support for ACPI P-states on VIA processors.
- Disable the e_powersaver driver.

* Tue Jun 09 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.30-rc8-git6

* Fri Jun 05 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.30-rc8-git1

* Wed Jun 03 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc8

* Tue Jun  2 2009 Roland McGrath <roland@redhat.com>
- utrace update (fixes stap PR10185)

* Tue Jun 02 2009 Dave Jones <davej@redhat.com>
- For reasons unknown, RT2X00 driver was being built-in.
  Make it modular.

* Tue Jun 02 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc7-git5

* Sat May 30 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc7-git4

* Thu May 28 2009 Dave Jones <davej@redhat.com
- 2.6.30-rc7-git3

* Wed May 27 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc7-git2

* Tue May 26 2009 Dave Jones <davej@redhat.com>
- Various cpufreq patches from git.

* Tue May 26 2009 Dave Jones <davej@redhat.com
- 2.6.30-rc7-git1

* Tue May 26 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc7-git1

* Mon May 25 2009 Kyle McMartin <kyle@redhat.com>
- rds-only-on-64-bit-or-x86.patch: drop patch, issue is fixed upstream.

* Sat May 23 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc7

* Thu May 21 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc6-git6

* Wed May 20 2009  Chuck Ebbert <cebbert@redhat.com>
- Enable Divas (formerly Eicon) ISDN drivers on x86_64. (#480837)

* Wed May 20 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc6-git5

* Mon May 18 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc6-git3

* Sun May 17 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc6-git2

* Sat May 16 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc6

* Mon May 11 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc5-git1

* Fri May 08 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc5

* Fri May 08 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc4-git4

* Wed May 06 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc4-git3
- linux-2.6-cdrom-door-status.patch: merged upstream.
- linux-2.6-iwl3945-remove-useless-exports.patch: merged upstream.
- linux-2.6-utrace.patch: rebase against changes to fs/proc/array.c
- USB_NET_CDC_EEM=m

* Fri May 01 2009 Eric Sandeen <sandeen@redhat.com>
- Fix ext4 corruption on partial write into prealloc block

* Thu Apr 30 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.30-rc4

* Wed Apr 29 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc3-git6

* Tue Apr 28 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc3-git4

* Tue Apr 28 2009 Chuck Ebbert <cebbert@redhat.com>
- Make the kernel-vanilla package buildable again.
- Allow building with older versions of RPM.

* Tue Apr 28 2009 Neil Horman <nhorman@redhat.com>
- Backport missing snmp stats (bz 492391)

* Tue Apr 28 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.30-0.72.rc3.git3
- Drop unused exports from the iwl3945 driver.

* Tue Apr 28 2009 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.30-rc3-git3

* Mon Apr 27 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc3-git2

* Sun Apr 26 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.30-0.68.rc3.git1
- Linux 2.6.30-rc3-git1

* Wed Apr 22 2009 Dave Jones <davej@redhat.com> 2.6.30-0.67.rc3
- Disable SYSFS_DEPRECATED on ia64

* Wed Apr 22 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc3
- PROC_VMCORE=y: Exports the dump image of crashed
  kernel in ELF format

* Wed Apr 22 2009 Neil Horman <nhorman@redhat.com>
- Enable RELOCATABLE and CRASH_DUMP for powerpc64
- With this we can remove the -kdump build variant
- for the ppc64 arch

* Tue Apr 21 2009 Chuck Ebbert <cebbert@redhat.com>
- Don't include the modules.*.bin files in the RPM package.

* Tue Apr 21 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc2-git7

* Mon Apr 20 2009 Dave Jones <davej@redhat.com>
- Various s390x config tweaks. (#496596, #496601, #496605, #496607)

* Mon Apr 20 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc2-git6

* Sat Apr 18 2009 Chuck Ebbert <cebbert@redhat.com>
- Set CONFIG_UEVENT_HELPER_PATH to the empty string (#496296)

* Fri Apr 17 2009 Dave Jones <davej@redhat.com>
- 2.6.30-rc2-git3

* Thu Apr 16 2009 Kyle McMartin <kyle@redhat.com> 2.6.30-0.58.rc2.git1
- 2.6.30-rc2-git1

* Wed Apr 15 2009 Kyle McMartin <kyle@redhat.com> 2.6.30-0.57.rc2
- 2.6.30-rc2

* Tue Apr 14 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.30-rc1-git7
- CONFIG_TOUCHSCREEN_AD7879_I2C=m
- CONFIG_STRIP_ASM_SYMS=y, off for -debug

* Mon Apr 13 2009 Kyle McMartin <kyle@redhat.com>
- ppc-fix-parport_pc.patch: add from linuxppc-dev@

* Mon Apr 13 2009 Kyle McMartin <kyle@redhat.com>
- execshield: fix build (load_user_cs_desc is 32-bit only in tlb.c)

* Sun Apr 12 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.30-rc1-git5
- revert-fix-modules_install-via-nfs.patch: reverted upstream

* Thu Apr 09 2009 Kyle McMartin <kyle@redhat.com>
- actually drop utrace-ftrace from srpm.

* Thu Apr 09 2009 Kyle McMartin <kyle@redhat.com>
- 2.6.30-rc1-git2
- CONFIG_IGBVF=m
- CONFIG_NETFILTER_XT_TARGET_LED=m

* Thu Apr 09 2009 Dave Jones <davej@redhat.com>
- Bring back the /dev/crash driver. (#492803)

* Wed Apr 08 2009 Dave Jones <davej@redhat.com>
- disable MMIOTRACE in non-debug builds (#494584)

* Wed Apr 08 2009 Kyle McMartin <kyle@redhat.com> 2.6.30-0.44.rc1
- 2.6.30-rc1
- linux-2.6-hwmon-atk0110.patch: drop
- CONFIG_DETECT_HUNG_TASK=y
- # CONFIG_BOOTPARAM_HUNG_TASK_PANIC is not set

* Tue Apr  7 2009 Roland McGrath <roland@redhat.com>
- utrace update, drop unfinished utrace-ftrace

* Tue Apr 07 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.29-git15
- EXT3_DEFAULTS_TO_ORDERED on for now.
- X86_X2APIC enabled.
- LEDS_LP5521, LEDS_BD2802 off... look not generally relevant.
- LIBFCOE on.

* Tue Apr 07 2009 Dave Jones <davej@redhat.com>
- Enable CONFIG_CIFS_STATS (#494545)

* Mon Apr 06 2009 Kyle McMartin <kyle@redhat.com>
- linux-2.6-execshield.patch: rebase for 2.6.30

* Mon Apr 06 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.29-git13
- drop patches merged upstream:
  - fix-ppc-debug_kmap_atomic.patch
  - fix-staging-at76.patch
  - linux-2.6-acpi-video-didl-intel-outputs.patch
  - linux-2.6-acpi-strict-resources.patch
  - linux-2.6-sony-laptop-rfkill.patch
  - linux-2.6-btrfs-fix-umount-hang.patch
  - linux-2.6-fiemap-header-install.patch
  - linux-2.6-debug-dma-api.patch
  - dma-api-debug-fixes.patch
  - linux-2.6-ext4-flush-on-close.patch
  - linux-2.6-relatime-by-default.patch
  - linux-2.6-pci-sysfs-remove-id.patch
  - linux-2.6-scsi-cpqarray-set-master.patch
  - alsa-rewrite-hw_ptr-updaters.patch
  - alsa-pcm-always-reset-invalid-position.patch
  - alsa-pcm-fix-delta-calc-at-overlap.patch
  - alsa-pcm-safer-boundary-checks.patch
  - linux-2.6-input-hid-extra-gamepad.patch
  - linux-2.6-ipw2x00-age-scan-results-on-resume.patch
  - linux-2.6-dropwatch-protocol.patch
  - linux-2.6-net-fix-gro-bug.patch
  - linux-2.6-net-fix-another-gro-bug.patch
  - linux-2.6-net-xfrm-fix-spin-unlock.patch
  - linux-2.6.29-pat-change-is_linear_pfn_mapping-to-not-use-vm_pgoff.patch
  - linux-2.6.29-pat-pci-change-prot-for-inherit.patch

* Thu Apr 02 2009 Josef Bacik <josef@toxicpanda.com>
- linux-2.6-btrfs-fix-umount-hang.patch: fix umount hang on btrfs

* Thu Apr 02 2009 Kyle McMartin <kyle@redhat.com>
- fix-ppc-debug_kmap_atomic.patch: fix build failures on ppc.

* Thu Apr 02 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.29-git9

* Tue Mar 31 2009 Kyle McMartin <kyle@redhat.com>
- rds-only-on-64-bit-or-x86.patch: add
- at76-netdev_ops.patch: add

* Tue Mar 31 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.29-git8
- linux-2.6-net-fix-another-gro-bug.patch: upstream.

* Tue Mar 31 2009 Eric Sandeen <sandeen@redhat.com>
- add fiemap.h to kernel-headers
- build ext4 (and jbd2 and crc16) into the kernel

* Tue Mar 31 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.29-git7
- fix-staging-at76.patch: pull patch from linux-wireless to fix...

* Mon Mar 30 2009 Kyle McMartin <kyle@redhat.com> 2.6.30-0.28.rc0.git6
- Linux 2.6.29-git6
- Bunch of stuff disabled, most merged, some needs rebasing.

* Mon Mar 30 2009 Chuck Ebbert <cebbert@redhat.com>
- Make the .shared-srctree file a list so more than two checkouts
  can share source files.

* Mon Mar 30 2009 Chuck Ebbert <cebbert@redhat.com>
- Separate PAT fixes that are headed for -stable from our out-of-tree ones.

* Mon Mar 30 2009 Dave Jones <davej@redhat.com>
- Make io schedulers selectable at boot time again. (#492817)

* Mon Mar 30 2009 Dave Jones <davej@redhat.com>
- Add a strict-devmem=0 boot argument (#492803)

* Mon Mar 30 2009 Adam Jackson <ajax@redhat.com>
- linux-2.6.29-pat-fixes.patch: Fix PAT/GTT interaction

* Mon Mar 30 2009 Mauro Carvalho Chehab <mchehab@redhat.com>
- some fixes of troubles caused by v4l2 subdev conversion

* Mon Mar 30 2009 Mark McLoughlin <markmc@redhat.com> 2.6.29-21
- Fix guest->remote network stall with virtio/GSO (#490266)

* Mon Mar 30 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch
  - rewrite nouveau PCI(E) GART functions, should fix rh#492492
  - kms: kernel option to allow dual-link dvi
  - modinfo descriptions for module parameters

* Sun Mar 29 2009 Mauro Carvalho Chehab <mchehab@redhat.com>
- more v4l/dvb updates: v4l subdev conversion and some driver improvements

* Sun Mar 29 2009 Chuck Ebbert <cebbert@redhat.com>
- More fixes for ALSA hardware pointer updating.

* Sat Mar 28 2009 Mauro Carvalho Chehab <mchehab@redhat.com>
- linux-2.6-revert-dvb-net-kabi-change.patch: attempt to fix dvb net breakage
- update v4l fixes patch to reflect what's ready for 2.6.30
- update v4l devel patch to reflect what will be kept on linux-next for a while

* Fri Mar 27 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.29-16
- Fix 2.6.29 networking lockups.
- Fix locking in net/xfrm/xfrm_state.c (#489764)

* Fri Mar 27 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: do nothing for dac_{prepare,commit}, it's useless
  and breaks some things in strange ways.

* Fri Mar 27 2009 Ben Skeggs <bskeggs@redhat.com>
- nv50: clear 0x1900/8 on init, possible fix for rh#492240
- forcibly disable GEM also if KMS requested where not supported
- inform the user if we disable KMS because of it not being supported

* Thu Mar 26 2009 Matthew Garrett <mjg@redhat.com>
- linux-2.6-relatime-by-default.patch: Backport relatime code from 2.6.30

* Thu Mar 26 2009 Dave Jones <davej@redhat.com>
- Check for modesetting enabled before forcing mode on 915. (#490336)

* Thu Mar 26 2009 Dave Jones <davej@redhat.com>
- Set kernel-PAE as default in grub. (#487578)

* Thu Mar 26 2009 Dave Jones <davej@redhat.com>
- Enable CONFIG_MOUSE_PS2_ELANTECH (#492163)

* Thu Mar 26 2009 Kyle McMartin <kyle@redhat.com>
- linux-2.6-v4l-pvrusb2-fixes.patch: fix build for uncle steve.

* Thu Mar 26 2009 Mauro Carvalho Chehab <mchehab@redhat.com>
- Move all 2.6.30 stuff into linux-2.6-v4l-dvb-fixes.patch, in
  preparation for upstream pull;
- Added two new drivers: gspca sq905c and DVB Intel ce6230
- Updated to the latest v4l-dvb drivers.

* Wed Mar 25 2009 Mauro Carvalho Chehab <mchehab@redhat.com>
- remove duplicated Cinergy T2 entry at config-generic

* Wed Mar 25 2009 Neil Horman <nhorman@redhat.com>
- Add dropmonitor/dropwatch protocol from 2.6.30

* Wed Mar 25 2009 Kyle McMartin <kyle@redhat.com>
- alsa-rewrite-hw_ptr-updaters.patch: snd_pcm_update_hw_ptr() tries to
  detect the unexpected hwptr jumps more strictly to avoid the position
  mess-up, which often results in the bad quality I/O with pulseaudio.

* Wed Mar 25 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: idle channels better before destroying them

* Tue Mar 24 2009 Kyle McMartin <kyle@redhat.com>
- Disable DMAR by default until suspend & resume is fixed.

* Tue Mar 24 2009 Josef Bacik <josef@toxicpanda.com>
- fsync replay fixes for btrfs

* Mon Mar 23 2009 Dave Jones <davej@redhat.com>
- 2.6.29

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
