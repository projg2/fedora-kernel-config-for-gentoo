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
# (Uncomment the '#' and the first two spaces below to set buildid.)
# % define buildid .local
%define buildid .xendom0
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
%global baserelease 170
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 2.6.22-rc7-git1 starts with a 2.6.21 base,
# which yields a base_sublevel of 21.
%define base_sublevel 32

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 23
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
%define doc_build_fail false
%else
%define doc_build_fail true
%endif

%define rawhide_skip_docs 1
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
%define debugbuildsenabled 0

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
%define with_up 0
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

# only build kernel-kdump on ppc64
# (no relocatable kernel support upstream yet)
#FIXME: Temporarily disabled to speed up builds.
#ifnarch ppc64
%define with_kdump 0
#endif

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
%define with_firmware  %{?_without_firmware:  0} %{?!_without_firmware:  1}
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
# and we no longer build for 31bit S390. Same for 32bit sparc and arm.
%define nobuildarches i386 ppc ppc64 ia64 sparc sparc64 390 s390x alpha alphaev56 %{arm}

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
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3, xen < 3.4.3

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
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, kernel-firmware >= %{rpmversion}-%{pkg_release}, grubby >= 7.0.4-1
%if %{with_dracut}
%define initrd_prereq  dracut >= 002 xorg-x11-drv-ati-firmware
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
Provides: kernel-drm-nouveau = 15\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
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
ExclusiveArch: noarch %{all_x86} x86_64 ia64 sparc sparc64 s390x alpha alphaev56 %{arm}
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
BuildRequires: elfutils-libelf-devel zlib-devel binutils-devel
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

Patch141: linux-2.6-ps3-storage-alias.patch
Patch143: linux-2.6-g5-therm-shutdown.patch
Patch144: linux-2.6-vio-modalias.patch
Patch147: linux-2.6-imac-transparent-bridge.patch

Patch150: linux-2.6.29-sparc-IOC_TYPECHECK.patch

Patch160: linux-2.6-execshield.patch

Patch250: linux-2.6-debug-sizeof-structs.patch
Patch260: linux-2.6-debug-nmi-timeout.patch
Patch270: linux-2.6-debug-taint-vm.patch
Patch300: linux-2.6-driver-level-usb-autosuspend.diff
Patch303: linux-2.6-enable-btusb-autosuspend.patch
Patch304: linux-2.6-usb-uvc-autosuspend.diff
Patch305: linux-2.6-usb-wwan-update.patch

Patch310: linux-2.6-autoload-wmi.patch
# wmi autoload fixes
Patch311: wmi-check-find_guid-return-value-to-prevent-oops.patch
Patch312: wmi-survive-bios-with-duplicate-guids.patch

Patch340: linux-2.6-debug-vm-would-have-oomkilled.patch
Patch360: linux-2.6-debug-always-inline-kzalloc.patch
Patch380: linux-2.6-defaults-pci_no_msi.patch
Patch381: linux-2.6-pciehp-update.patch
Patch382: linux-2.6-defaults-pciehp.patch
Patch383: linux-2.6-defaults-aspm.patch
Patch384: pci-acpi-disable-aspm-if-no-osc.patch
Patch385: pci-aspm-dont-enable-too-early.patch

Patch390: linux-2.6-defaults-acpi-video.patch
Patch391: linux-2.6-acpi-video-dos.patch
Patch450: linux-2.6-input-kill-stupid-messages.patch
Patch451: linux-2.6-input-fix-toshiba-hotkeys.patch
Patch452: linux-2.6.30-no-pcspkr-modalias.patch
Patch454: linux-2.6-input-hid-quirk-egalax.patch
Patch455: thinkpad-acpi-add-x100e.patch
Patch456: thinkpad-acpi-fix-backlight.patch

Patch460: linux-2.6-serial-460800.patch

Patch470: die-floppy-die.patch

Patch510: linux-2.6-silence-noise.patch
Patch520: linux-2.6.30-hush-rom-warning.patch
Patch530: linux-2.6-silence-fbcon-logo.patch
Patch531: viafb-neuter-device-table.patch
Patch570: linux-2.6-selinux-mprotect-checks.patch
Patch580: linux-2.6-sparc-selinux-mprotect-checks.patch

Patch600: linux-2.6-defaults-alsa-hda-beep-off.patch
Patch610: hda_intel-prealloc-4mb-dmabuffer.patch

Patch670: linux-2.6-ata-quirk.patch

Patch701: sky2-optima-add-register-definitions.patch
Patch702: sky2-optima-support.patch
Patch703: sky2-optima-fix-tcp-offload.patch
Patch704: sky2-optima-print-chip-name.patch
Patch705: sky2-optima-add-missing-write-bits.patch

Patch800: linux-2.6-crash-driver.patch

Patch900: linux-2.6-pci-cacheline-sizing.patch

Patch1515: lirc-2.6.32.patch
Patch1517: hdpvr-ir-enable.patch
Patch1520: crystalhd-2.6.34-staging.patch

# virt + ksm patches
Patch1551: linux-2.6-ksm-kvm.patch

# fbdev multi-card fix
Patch1700: linux-2.6-x86-64-fbdev-primary.patch

# nouveau + drm fixes
Patch1810: drm-upgrayedd.patch
Patch1811: drm-upgrayed-fixes.patch
Patch1813: drm-radeon-pm.patch
#Patch1814: drm-nouveau.patch
Patch1818: drm-i915-resume-force-mode.patch
Patch1819: drm-intel-big-hammer.patch
Patch1820: drm-intel-no-tv-hotplug.patch
Patch1823: drm-intel-945gm-stability-fixes.patch
# intel drm is all merged upstream
Patch1824: drm-intel-next.patch
Patch1825: drm-intel-acpi-populate-didl.patch
Patch1826: drm-intel-make-lvds-work.patch
#Patch1827: linux-2.6-intel-agp-clear-gtt.patch
Patch1828: drm-nouveau-g80-ctxprog.patch
Patch1831: drm-nouveau-tvout-disable.patch
Patch1832: drm-nouveau-safetile-getparam.patch
Patch1844: drm-nouveau-kconfig.patch
Patch1845: drm-nouveau-mutex.patch
Patch1846: drm-nouveau-update.patch
Patch1847: drm-nouveau-d620.patch
Patch1848: drm-nouveau-nva3-noaccel.patch

# kludge to make ich9 e1000 work
Patch2000: linux-2.6-e1000-ich9.patch

Patch2100: linux-2.6-phylib-autoload.patch

# linux1394 git patches
Patch2200: linux-2.6-firewire-git-update.patch
Patch2201: linux-2.6-firewire-git-pending.patch

# Quiet boot fixes
# silence the ACPI blacklist code
Patch2802: linux-2.6-silence-acpi-blacklist.patch

Patch2899: linux-2.6-v4l-dvb-fixes.patch
Patch2900: linux-2.6-v4l-dvb-update.patch
Patch2901: linux-2.6-v4l-dvb-experimental.patch
Patch2903: linux-2.6-revert-dvb-net-kabi-change.patch
Patch2904: linux-2.6-v4l-dvb-rebase-gspca-to-latest.patch
Patch2905: linux-2.6-v4l-dvb-add-lgdt3304-support.patch
Patch2096: linux-2.6-v4l-dvb-add-kworld-a340-support.patch

# fs fixes

# ext4/quota

# NFSv4
Patch3050: linux-2.6-nfsd4-proots.patch
Patch3051: linux-2.6-nfs4-callback-hidden.patch

# btrfs
Patch3101: btrfs-prohibit-a-operation-of-changing-acls-mask-when-noacl-mount-option-is-used.patch

# XFS

# VIA Nano / VX8xx updates
Patch11010: via-hwmon-temp-sensor.patch

# patches headed upstream
Patch12010: linux-2.6-dell-laptop-rfkill-fix.patch
Patch12013: linux-2.6-rfkill-all.patch
Patch12020: linux-2.6-cantiga-iommu-gfx.patch

Patch12200: add-appleir-usb-driver.patch

# Patches for -stable

# ACPI EC bugfixes (not all upstream)
Patch12250: acpi-ec-add-delay-before-write.patch

Patch12311: fix-ima-null-ptr-deref.patch

Patch12315: fix-abrtd.patch

# rhbz#/566565
Patch12340: ice1712-fix-revo71-mixer-names.patch

# rhbz#572653
Patch12370: linux-2.6-b43_-Rewrite-DMA-Tx-status-handling-sanity-checks.patch

# backport iwlwifi fixes (thanks, sgruszka!) -- drop when stable catches-up
Patch12391: iwlwifi-reset-card-during-probe.patch

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

# iwlwifi: fix scan races
Patch12910: iwlwifi-fix-scan-races.patch
# iwlwifi: fix internal scan race
Patch12911: iwlwifi-fix-internal-scan-race.patch
# iwlwifi: recover_from_tx_stall
Patch12912: iwlwifi-recover_from_tx_stall.patch

Patch12921: iwlwifi-manage-QoS-by-mac-stack.patch
Patch12923: mac80211-explicitly-disable-enable-QoS.patch

# l2tp: fix oops in pppol2tp_xmit (#607054)
Patch13030: l2tp-fix-oops-in-pppol2tp_xmit.patch

Patch14050: crypto-add-async-hash-testing.patch

# Red Hat Bugzilla #610911
Patch14130: kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch

Patch14200: net-do-not-check-capable-if-kernel.patch

# Mitigate DOS with large argument lists
Patch14210: execve-improve-interactivity-with-large-arguments.patch
Patch14211: execve-make-responsive-to-sigkill-with-large-arguments.patch
Patch14212: setup_arg_pages-diagnose-excessive-argument-size.patch

Patch14220: xen-fix-typo-in-xen-irq-fix.patch

Patch19997: xen.pvops.pre.patch
Patch19998: xen.pvops.patch
Patch19999: xen.pvops.post.patch

# ==============================================================================
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

#ApplyPatch git-cpufreq.patch
#ApplyPatch git-bluetooth.patch

ApplyOptionalPatch linux-2.6-hotfixes.patch

# Roland's utrace ptrace replacement.
ApplyPatch linux-2.6-tracehook.patch
ApplyPatch linux-2.6-utrace.patch
ApplyPatch linux-2.6-utrace-ptrace.patch

# Architecture patches
# x86(-64)
ApplyPatch via-hwmon-temp-sensor.patch
ApplyPatch linux-2.6-dell-laptop-rfkill-fix.patch

#
# Intel IOMMU
#
ApplyPatch linux-2.6-cantiga-iommu-gfx.patch

#
# PowerPC
#
### NOT (YET) UPSTREAM:
# The storage alias patch is Fedora-local, and allows the old 'ps3_storage'
# module name to work on upgrades. Otherwise, I believe mkinitrd will fail
# to pull the module in,
ApplyPatch linux-2.6-ps3-storage-alias.patch
# Alleviate G5 thermal shutdown problems
ApplyPatch linux-2.6-g5-therm-shutdown.patch
# Provide modalias in sysfs for vio devices
ApplyPatch linux-2.6-vio-modalias.patch
# Work around PCIe bridge setup on iSight
ApplyPatch linux-2.6-imac-transparent-bridge.patch

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
ApplyPatch btrfs-prohibit-a-operation-of-changing-acls-mask-when-noacl-mount-option-is-used.patch

# eCryptfs

# NFSv4
ApplyPatch linux-2.6-nfsd4-proots.patch
ApplyPatch linux-2.6-nfs4-callback-hidden.patch

# USB
ApplyPatch linux-2.6-driver-level-usb-autosuspend.diff
ApplyPatch linux-2.6-enable-btusb-autosuspend.patch
ApplyPatch linux-2.6-usb-uvc-autosuspend.diff
ApplyPatch linux-2.6-usb-wwan-update.patch

# WMI
ApplyPatch linux-2.6-autoload-wmi.patch
# autoload fixes
ApplyPatch wmi-check-find_guid-return-value-to-prevent-oops.patch
ApplyPatch wmi-survive-bios-with-duplicate-guids.patch

# ACPI
ApplyPatch linux-2.6-defaults-acpi-video.patch
ApplyPatch linux-2.6-acpi-video-dos.patch

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
# disable aspm if acpi doesn't provide an _OSC method
ApplyPatch pci-acpi-disable-aspm-if-no-osc.patch
# allow drivers to disable aspm at load time
ApplyPatch pci-aspm-dont-enable-too-early.patch

#
# SCSI Bits.
#

# ALSA
# squelch hda_beep by default
ApplyPatch linux-2.6-defaults-alsa-hda-beep-off.patch
ApplyPatch hda_intel-prealloc-4mb-dmabuffer.patch

# Networking
ApplyPatch sky2-optima-add-register-definitions.patch
ApplyPatch sky2-optima-support.patch
ApplyPatch sky2-optima-fix-tcp-offload.patch
ApplyPatch sky2-optima-print-chip-name.patch
ApplyPatch sky2-optima-add-missing-write-bits.patch

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch linux-2.6-input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

# Get away from having to poll Toshibas
#ApplyPatch linux-2.6-input-fix-toshiba-hotkeys.patch

ApplyPatch linux-2.6.30-no-pcspkr-modalias.patch

ApplyPatch linux-2.6-input-hid-quirk-egalax.patch
ApplyPatch thinkpad-acpi-add-x100e.patch
ApplyPatch thinkpad-acpi-fix-backlight.patch

# Allow to use 480600 baud on 16C950 UARTs
ApplyPatch linux-2.6-serial-460800.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch linux-2.6-silence-noise.patch
ApplyPatch linux-2.6.30-hush-rom-warning.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch linux-2.6-silence-fbcon-logo.patch

# don't autoload viafb
ApplyPatch viafb-neuter-device-table.patch

# Fix the SELinux mprotect checks on executable mappings
# ApplyPatch linux-2.6-selinux-mprotect-checks.patch
# Fix SELinux for sparc
ApplyPatch linux-2.6-sparc-selinux-mprotect-checks.patch

# Changes to upstream defaults.


# ia64 ata quirk
ApplyPatch linux-2.6-ata-quirk.patch

# /dev/crash driver.
ApplyPatch linux-2.6-crash-driver.patch

# Determine cacheline sizes in a generic manner.
ApplyPatch linux-2.6-pci-cacheline-sizing.patch

# http://www.lirc.org/
ApplyPatch lirc-2.6.32.patch
# enable IR transceiver on Hauppauge HD PVR (v4l-dvb merge pending)
ApplyPatch hdpvr-ir-enable.patch
# Broadcom Crystal HD driver from 2.6.34 staging
ApplyPatch crystalhd-2.6.34-staging.patch

# Add kernel KSM support
# Optimize KVM for KSM support
#ApplyPatch linux-2.6-ksm-kvm.patch

# Assorted Virt Fixes

ApplyPatch linux-2.6-e1000-ich9.patch

ApplyPatch linux-2.6-phylib-autoload.patch

ApplyPatch linux-2.6-x86-64-fbdev-primary.patch
# Nouveau DRM + drm fixes
ApplyPatch drm-upgrayedd.patch
ApplyPatch drm-upgrayed-fixes.patch
#ApplyPatch drm-intel-big-hammer.patch
#ApplyPatch drm-intel-no-tv-hotplug.patch
ApplyOptionalPatch drm-intel-next.patch
ApplyPatch drm-intel-acpi-populate-didl.patch
ApplyPatch drm-intel-make-lvds-work.patch
# gm45 stability fixes
ApplyPatch drm-intel-945gm-stability-fixes.patch

ApplyPatch drm-nouveau-g80-ctxprog.patch
ApplyPatch drm-nouveau-tvout-disable.patch
ApplyPatch drm-nouveau-safetile-getparam.patch
ApplyPatch drm-nouveau-kconfig.patch
ApplyPatch drm-nouveau-update.patch
ApplyPatch drm-nouveau-d620.patch
ApplyPatch drm-nouveau-nva3-noaccel.patch

# linux1394 git patches
#ApplyPatch linux-2.6-firewire-git-update.patch
#ApplyOptionalPatch linux-2.6-firewire-git-pending.patch

# silence the ACPI blacklist code
ApplyPatch linux-2.6-silence-acpi-blacklist.patch

# V4L/DVB updates/fixes/experimental drivers
#ApplyPatch linux-2.6-v4l-dvb-fixes.patch
#ApplyPatch linux-2.6-v4l-dvb-update.patch
#ApplyPatch linux-2.6-v4l-dvb-experimental.patch
#ApplyPatch linux-2.6-revert-dvb-net-kabi-change.patch
ApplyPatch linux-2.6-v4l-dvb-rebase-gspca-to-latest.patch
ApplyPatch linux-2.6-v4l-dvb-add-lgdt3304-support.patch
ApplyPatch linux-2.6-v4l-dvb-add-kworld-a340-support.patch

# Patches headed upstream
ApplyPatch linux-2.6-rfkill-all.patch

ApplyPatch add-appleir-usb-driver.patch

# Patches for -stable

ApplyPatch fix-ima-null-ptr-deref.patch

ApplyPatch fix-abrtd.patch

# rhbz#566565
ApplyPatch ice1712-fix-revo71-mixer-names.patch

# rhbz#572653
ApplyPatch linux-2.6-b43_-Rewrite-DMA-Tx-status-handling-sanity-checks.patch

# backport iwlwifi fixes (thanks, sgruszka!) -- drop when stable catches-up
ApplyPatch iwlwifi-reset-card-during-probe.patch

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

# iwlwifi: fix scan races
ApplyPatch iwlwifi-fix-scan-races.patch
# iwlwifi: fix internal scan race
ApplyPatch iwlwifi-fix-internal-scan-race.patch
# iwlwifi: recover_from_tx_stall
ApplyPatch iwlwifi-recover_from_tx_stall.patch

# mac80211/iwlwifi fix connections to some APs (rhbz#558002)
ApplyPatch mac80211-explicitly-disable-enable-QoS.patch
ApplyPatch iwlwifi-manage-QoS-by-mac-stack.patch

# l2tp: fix oops in pppol2tp_xmit (#607054)
ApplyPatch l2tp-fix-oops-in-pppol2tp_xmit.patch

# add tests for crypto async hashing (#571577)
ApplyPatch crypto-add-async-hash-testing.patch

ApplyPatch kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch

# rhbz #598796
ApplyPatch net-do-not-check-capable-if-kernel.patch

# Mitigate DOS with large argument lists
ApplyPatch execve-improve-interactivity-with-large-arguments.patch
ApplyPatch execve-make-responsive-to-sigkill-with-large-arguments.patch
ApplyPatch setup_arg_pages-diagnose-excessive-argument-size.patch

# Fix typo in Xen patch from 2.6.22 that causes hang on boot.
ApplyPatch xen-fix-typo-in-xen-irq-fix.patch

ApplyPatch xen.pvops.pre.patch
ApplyPatch xen.pvops.patch
ApplyPatch xen.pvops.post.patch

# END OF PATCH APPLICATIONS ====================================================
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
    make -s V=1 %{?_smp_mflags} perf
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
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cd include
    cp -a acpi config crypto keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound trace video drm asm-generic xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    asmdir=$(readlink asm)
    cp -a $asmdir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    ln -s $asmdir asm
    popd
    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf
    cd ..

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
    			 'register_netdev|ieee80211_register_hw|usbnet_probe'
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
#make %{?_smp_mflags} htmldocs mandocs || %{doc_build_fail}
make -j1 htmldocs mandocs || %{doc_build_fail}

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
%if %{with_dracut}\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
%else\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --depmod --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
%endif}\
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
* Mon Sep 27 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.32.23-170
- Linux 2.6.32.23
- Drop merged patches:
  aio-check-for-multiplication-overflow-in-do_io_submit.patch
  inotify-fix-inotify-oneshot-support.patch
  inotify-send-IN_UNMOUNT-events.patch
  irda-correctly-clean-up-self-ias_obj-on-irda_bind-failure.patch
  keys-fix-bug-in-keyctl_session_to_parent-if-parent-has-no-session-keyring.patch
  keys-fix-rcu-no-lock-warning-in-keyctl_session_to_parent.patch
- Fix typo in Xen patch from 2.6.32.22.

* Mon Sep 20 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.32.22-169
- Linux 2.6.32.22
- Drop merged patches:
  01-compat-make-compat_alloc_user_space-incorporate-the-access_ok-check.patch
  02-compat-test-rax-for-the-system-call-number-not-eax.patch
  03-compat-retruncate-rax-after-ia32-syscall-entry-tracing.patch
  hid-01-usbhid-initialize-interface-pointers-early-enough.patch
  hid-02-fix-suspend-crash-by-moving-initializations-earlier.patch
  alsa-seq-oss-fix-double-free-at-error-path-of-snd_seq_oss_open.patch
  tracing-do-not-allow-llseek-to-set_ftrace_filter.patch

* Mon Sep 20 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.32.21-168
- Fix three CVEs:
  CVE-2010-3080: /dev/sequencer open failure is not handled correctly
  CVE-2010-2960: keyctl_session_to_parent NULL deref system crash
  CVE-2010-3079: ftrace NULL pointer dereference

* Tue Sep 14 2010 Chuck Ebbert <cebbert@redhat.com>
- Mitigate DOS with large argument lists.

* Tue Sep 14 2010 Kyle McMartin <kyle@redhat.com>
- x86_64: plug compat syscalls holes. (CVE-2010-3081, CVE-2010-3301)
  upgrading is highly recommended.
- aio: check for multiplication overflow in do_io_submit. (CVE-2010-3067)

* Mon Sep 06 2010 Kyle McMartin <kyle@redhat.com>
- Backport two fixes from Eric Paris to resolve #598796 which avoids a
  capability check if the request comes from the kernel.

* Fri Sep 03 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops to 2.6.32.21
- Set new dom0 related option CONFIG_NET_SCH_PLUG=m

* Thu Sep 02 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.21-167
- irda-correctly-clean-up-self-ias_obj-on-irda_bind-failure.patch (CVE-2010-2954)

* Fri Aug 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.21-166
- Linux 2.6.32.21

* Wed Aug 25 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.21-165.rc1
- Linux 2.6.32.21-rc1
- Drop merged patches:
    drm-i915-add-reclaimable-to-page-allocations.patch
    drm-i915-fix-hibernate-memory-corruption.patch
- Fix up execshield and DRM upgrade patches to apply after 2.6.32.21

* Sat Aug 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.20-164
- Linux 2.6.32.20
- Drop merged patches:
   mm-fix-page-table-unmap-for-stack-guard-page-properly.patch
   mm-fix-up-some-user-visible-effects-of-the-stack-guard-page.patch

* Wed Aug 18 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.19-163
- Bump version.

* Tue Aug 17 2010 Kyle McMartin <kyle@redhat.com>
- Touch .scmversion in the kernel top level to prevent scripts/setlocalversion
  from recursing into our fedpkg git tree and trying to decide whether the
  kernel git is modified (obviously not, since it's a tarball.) Fixes make
  local.

* Tue Aug 17 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.19-162
- Fix fallout from the stack guard page fixes.
  (mm-fix-page-table-unmap-for-stack-guard-page-properly.patch,
   mm-fix-up-some-user-visible-effects-of-the-stack-guard-page.patch)

* Sat Aug 14 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.19-161
- Linux 2.6.32.19

* Fri Aug 13 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.19-160.rc1
- Linux 2.6.32.19-rc1
- Comment out patches merged upstream:
    linux-2.6-btrfs-fix-acl.patch
    crypto-testmgr-add-null-test-for-aesni.patch
    ext4-make-sure-the-move_ext-ioctl-can-t-overwrite-append-only-files.patch
    ext4-fix-freeze-deadlock-under-io.patch
- Fix linux-2.6-usb-wwan-update.patch to apply after 2.6.32.19

* Tue Aug 10 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.18-159
- Linux 2.6.32.18
- Backport nouveau noaccel fix for nva3+ cards from f13.
- ext4-fix-freeze-deadlock-under-io.patch:
  Fix deadlock caused by patch in 2.6.32.17
  (0036-ext4-don-t-return-to-userspace-after-freezing-the-fs.patch)

* Tue Aug 10 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.18-158.rc1
- Bring back drm-upgrayed-fixes.patch, dropped in the
  2.6.32.16 update. (#620955)
- Revert upstream DRM stable fix we already have:
    drm-i915-give-up-on-8xx-lid-status.patch

* Sat Aug 07 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.32.18-rc1
- Revert DRM patches from -stable we already have:
    drm-i915-Fix-LVDS-presence-check
    drm-i915-parse-child-device-from-vbt.patch
- Comment out patches merged in -stable:
    xfs-prevent-swapext-from-operating-on-write-only-files.patch
    cifs-fix-dns-resolver.patch

* Fri Aug 06 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops to 2.6.32.17
- try removing patch that set CONFIG_XEN_XENBUS_FRONTEND=y

* Fri Aug 06 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.17-157
- Fix USB HID initialization (#592785)

* Mon Aug 02 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.17-156
- Linux 2.6.32.17
- Drop the patches commented out for -rc1 except ssb_check_for_sprom.patch

* Mon Aug 02 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.17-155.rc1
- Linux 2.6.32.17-rc1
- Comment out patches merged upstream:
    linux-2.6-ext4-quota-metadata-reservation.patch
    ext4-issue-discard-operation-before-releasing-blocks.patch
    mac80211-do-not-wipe-out-old-supported-rates.patch
    mac80211-fix-supported-rates-IE-if-AP-doesnt-give-us-its-rates.patch
    iwlwifi-cancel-scan-watchdog-in-iwl_bg_abort_scan.patch
    sched-fix-over-scheduling-bug.patch
    ethtool-fix-buffer-overflow.patch
    cifs-fix-malicious-redirect-problem-in-the-dns-lookup-code.patch
    usb-obey-the-sysfs-power-wakeup-setting.patch
- Revert -stable patches we already have:
    drm-i915-enable-low-power-render-writes-on-gen3-hardware.patch
    drm-i915-define-mi_arb_state-bits.patch
- Comment out due to conflicts with -stable:
    ssb_check_for_sprom.patch

* Tue Jul 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-154
- xfs-prevent-swapext-from-operating-on-write-only-files.patch:
  CVE-2010-2266

* Tue Jul 27 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.16-153
- kvm-mmu-fix-conflict-access-permissions-in-direct-sp.patch:
  Fix crash in guest Python programs (#610911)

* Tue Jul 27 2010 Michael Young <m.a.young@durham.ac.uk>
- remove some obsolete or unnecessary additions to config-generic
- try building XEN_BLKDEV_BACKEND XEN_NETDEV_BACKEND XEN_GNTDEV
  as modules and adding XEN_PCIDEV_FRONTEND XEN_PLATFORM_PCI as modules

* Mon Jul 26 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-152
- usb-obey-the-sysfs-power-wakeup-setting.patch:
  Restore ability of USB devices to wake the machine (F13#617559)

* Mon Jul 26 2010 Eric Sandeen <sandeen@redhat.com> 2.6.32.16-151
- Fix ext4 metadata vs. quota reservation bug (#608770)

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-150
- drm-intel-945gm-stability-fixes.patch
- Make doc build single-threaded to prevent build failures.

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-149
- drm-i915-fix-hibernate-memory-corruption.patch,
  drm-i915-add-reclaimable-to-page-allocations.patch:
  Fixes for hibernation memory corruption bugs introduced in 2.6.32.8

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-148
- ext4-make-sure-the-move_ext-ioctl-can-t-overwrite-append-only-files.patch
  (CVE-2010-2066)

* Thu Jul 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-147
- cifs-fix-malicious-redirect-problem-in-the-dns-lookup-code.patch:
  Fix a malicious redirect problem in the DNS lookup code (CVE-2010-2524)

* Wed Jul 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-146
- pci-acpi-disable-aspm-if-no-osc.patch, pci-aspm-dont-enable-too-early.patch
  PCI layer fixes for problems with hardware that doesn't support ASPM.

* Wed Jul 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-145
- crypto-add-async-hash-testing.patch: fix the rest of the errors
  reported during crypto testing (#571577)

* Wed Jul 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-144
- Fix inotify-oneshot-support patch so it builds.
- crypto-testmgr-add-null-test-for-aesni.patch:
  Add tests for aesni crypto module (#571577)

* Fri Jul 16 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-143
- inotify-fix-inotify-oneshot-support.patch,
  inotify-send-IN_UNMOUNT-events.patch:
  Fix broken oneshot support and missing umount events. (F13#607327)

* Wed Jul 14 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.32.16-142
- Drop Intel Moorestown support.

* Wed Jul 12 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops

* Wed Jul 07 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.16-141
- Really make hdpvr i2c IR part register this time, so something can
  actually be bound to it (like, say, lirc_zilog)

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.32.16-140
- ethtool-fix-buffer-overflow.patch: ethtool buffer overflow (CVE-2010-2478)
- sched-fix-over-scheduling-bug.patch: fix scheduler bug with CGROUPS

* Tue Jul 06 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-139
- Linux 2.6.32.16

* Fri Jul 02 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.16-138.rc1
- Linux 2.6.32.16-rc1
- Drop patches merged upstream:
    btrfs-should-add-permission-check-for-setfacl.patch
    linux-2.6-wireless_-report-reasonable-bitrate-for-MCS-rates-through-wext.patch
    drm-upgrayed-fixes.patch
    iwlwifi_-check-for-aggregation-frame-and-queue.patch
    iwlwifi-recalculate-average-tpt-if-not-current.patch
    iwlwifi-update-supported-PCI_ID-list-for-5xx0-series.patch
    keys-find-keyring-by-name-can-gain-access-to-the-freed-keyring.patch
- Fix up wireless patches and usb-wwan-update.patch to apply on 2.6.32.16

* Thu Jul 01 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.15-137
- Linux 2.6.32.15

* Mon Jun 28 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.14-136
- Drop unused ro-nx patches.
- Add support for sky2 Optima chip.

* Wed Jun 23 2010 Kyle McMartin <kyle@redhat.com>  2.6.32.14-135
- l2tp: fix oops in pppol2tp_xmit (rhbz#607054)

* Wed Jun 16 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops
- undo balloning patch as it is upstream in xen

* Tue Jun 15 2010 Kyle McMartin <kyle@redhat.com>  2.6.32.14-134
- Fix btrfs ACL fixes... commit 431547b3c4533b8c7fd150ab36980b9a3147797b
  changed them to take a struct dentry instead of struct inode after
  2.6.32.

* Tue Jun 15 2010 John W. Linville <linville@redhat.com> 2.6.32.14-133
- iwlwifi: cancel scan watchdog in iwl_bg_abort_scan (#604264)

* Mon Jun 14 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.14-132
- Add in ACL fixes to btrfs from CVE-2010-2071.

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.14-131
- mac80211/iwlwifi fix connections to some APs (rhbz#558002)
  patches from sgruszka@.

* Sat Jun  5 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops (only change is 2.6.32.14 -> 2.6.32.15)
- try a ballooning patch

* Wed Jun  2 2010 John W. Linville <linville@redhat.com>
- iwlwifi: update supported PCI_ID list for 5xx0 series (#599153)

* Sat May 29 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops

* Thu May 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.14-127
- CVE-2010-1437: keyrings: find_keyring_by_name() can gain the freed keyring

* Wed May 26 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.14-126
- Linux 2.6.32.14
- Drop merged patches:
    btrfs-check-for-read-permission-on-src-file-in-clone-ioctl.patch
    iwlwifi_-clear-all-the-stop_queue-flag-after-load-firmware.patch
    revert-ath9k_-fix-lockdep-warning-when-unloading-module.patch

* Mon May 24 2010 John W. Linville <linville@redhat.com>
- iwlwifi: recalculate average tpt if not current (#588021)

* Mon May 24 2010 John W. Linville <linville@redhat.com>
- iwlwifi: recover_from_tx_stall (#589777)
- iwlwifi: fix scan races (#592011)
- iwlwifi: fix internal scan race (#592011)

* Tue May 18 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops

* Tue May 18 2010 Kyle McMartin <kyle@redhat.com>
- btrfs: check for read permission on src file in the clone ioctl
  (rhbz#593226)

* Mon May 17 2010 Matthew Garrett <mjg@redhat.com>
- thinkpad-acpi-fix-backlight.patch: Fix backlight control on some recent
   Thinkpads

* Fri May 14 2010 Jarod Wilson <jarod@redhat.com>
- Update previous kworld patch w/the one that actually works
  correctly w/o constant rf tracking filter recalibration

* Thu May 13 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.13-120
- Restore patch to enable hauppauge hdpvr ir part
- Enable support for kworld ub435-q and 340u usb atsc tuners

* Wed May 12 2010 Chuck Ebbert <cebbert@redhat.com>
- Completely drop patches merged in 2.6.32.13

* Wed May 12 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.13-118
- Linux 2.6.32.13

* Wed May 12 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.13-117.rc1
- Linux 2.6.32.13-rc1
- Drop patches:
   libata-fix-accesses-at-LBA28-boundary.patch
   hugetlb-fix-infinite-loop-in-get-futex-key.patch
   reiserfs-fix-permissions-on-reiserfs-priv.patch
   libiscsi-regression-fix-header-digest-errors.patch

* Wed May 12 2010 Roland McGrath <roland@redhat.com> 2.6.32.12-116
- utrace update (#590954)

* Thu May 6 2010 Michael Young <m.a.young@durham.ac.uk>
- pvops update which adds XEN_PLATFORM_PCI support
- current pvops kernel won't build unless CONFIG_XEN_XENBUS_FRONTEND=y
  if XEN and PM_SLEEP are selected
- add a patch to ensure this as we can't set CONFIG_XEN_XENBUS_FRONTEND
  directly
- build problems with CONFIG_XEN_PLATFORM_PCI=m so unset it again

* Fri Apr 30 2010 John W. Linville <linville@redhat.com> 2.6.32.12-115
- Revert "ath9k: fix lockdep warning when unloading module"

* Wed Apr 28 2010 Michael Young <m.a.young@durham.ac.uk>
- another pvops update

* Tue Apr 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.12-114
- libiscsi-regression-fix-header-digest-errors.patch:
  fix iscsi header authentication broken in .32 (#583581)

* Tue Apr 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.12-113
- Fix possible data corruption with ext4 mounted with -o discard

* Tue Apr 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.12-112
- hugetlb-fix-infinite-loop-in-get-futex-key.patch (#552257)
- reiserfs-fix-permissions-on-reiserfs-priv.patch (CVE-2010-1146)

* Mon Apr 26 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.12-111
- Linux 2.6.32.12

* Fri Apr 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.12-110.rc2
- Linux 2.6.32.12-rc2
- Drop -rc1 workarounds

* Thu Apr 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.12-109.rc1
- Linux 2.6.32.12-rc1
- Drop patches merged upstream:
  xfs_swap_extents-needs-to-handle-dynamic-fork-offsets.patch
  acpi-ec-allow-multibyte-access-to-ec.patch
  acpi-ec-limit-burst-to-64-bit.patch
  vgaarb-fix-userspace-ptr-deref.patch
  linux-2.6-net-r8169-improved-rx-length-check-errors.patch
  tcp-fix-icmp-rto-war.patch
  iwlwifi-fix-nfreed--.patch
  mac80211_-tear-down-all-agg-queues-when-restart_reconfig-hw.patch
  iwlwifi_-clear-all-tx-queues-when-firmware-ready.patch
  iwlwifi_-fix-scan-race.patch
  b43_-Optimize-PIO-scratchbuffer-usage.patch
  b43_-Remove-reset-after-fatal-DMA-error.patch
  b43_-Allow-PIO-mode-to-be-selected-at-module-load.patch
  b43_-fall-back-gracefully-to-PIO-mode-after-fatal-DMA-errors.patch
  mac80211_-fix-deferred-hardware-scan-requests.patch
- Revert -rc1 patch: md-raid5-allow-for-more-than-2-31-chunks.patch
  ( ERROR: "__umoddi3" [drivers/md/raid456.ko] undefined! )
- Hotfix -rc1 lockdep patch with fix from LKML

* Wed Apr 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.11-108
- ACPI embedded controller fixes from Fedora 13 (#532161)

* Wed Apr 21 2010 Matthew Garrett <mjg@redhat.com>
- thinkpad-acpi-add-x100e.patch: Add EC path for Thinkpad X100

* Wed Apr 21 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.11-106
- libata-fix-accesses-at-LBA28-boundary.patch

* Tue Apr 20 2010 John W. Linville <linville@redhat.com> 2.6.32.11-105
- mac80211: fix deferred hardware scan requests

* Fri Apr 16 2010 John W. Linville <linville@redhat.com> 2.6.32.11-104
- b43: Optimize PIO scratchbuffer usage
- b43: Remove reset after fatal DMA error
- b43: Allow PIO mode to be selected at module load
- b43: fall back gracefully to PIO mode after fatal DMA errors

* Wed Apr 14 2010 David Woodhouse <David.Woodhouse@intel.com>
- Fix autoloading of phy modules (#525966)

* Mon Apr 12 2010 John W. Linville <linville@redhat.com> 2.6.32.11-102
- patches from Intel to address intermittent firmware failures with iwlagn

* Sat Apr 10 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops

* Tue Apr 07 2010 Chuck Ebbert <cebbert@redhat.com>
- Disable async RAID4/5/6 processing (#575402)

* Tue Apr 06 2010 Chuck Ebbert <cebbert@redhat.com>
- Build eeepc-laptop driver for x86_64 (F13#565582)
- Build all of the DVB frontend drivers (F13#578755)

* Mon Apr 05 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.11-99
- Fix oops in lirc_it87 driver (#579270)
- Support more imon 0xffdc key combinations

* Sat Apr 03 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.11-98
- Linux 2.6.32.11
- Reverted: we already have in our DRM:
    drm-edid-unify-detailed-block-parsing-between-base-and-extension-blocks.patch
    drm-i915-fix-gpio-register-detection-logic-for-bios-without-vbt.patch
- Reverted: already in linux-2.6-usb-wwan-update.patch:
    usb-qcserial-add-new-device-ids.patch
- Dropped patches merged upstream:
    linux-2.6-delalloc-quota-fixes.patch
    linux-2.6-efi-handover.fix
    coredump-uid-pipe-check.patch
    tg3-05-assign-flags-to-fixes-in-start_xmit_dma_bug.patch
    tg3-06-fix-5906-transmit-hangs.patch
    linux-2.6-tg3-netpoll.patch
    iwlwifi-silence-tfds-in-queue-message.patch
    iwlwifi-use-dma_alloc_coherent.patch
- Fixups:
    drm-upgrayedd.patch: lib/lcm.o was added
    fix-abrtd.patch: coredump-uid-pipe-check went upstream

* Thu Apr 01 2010 Eric Sandeen <sandeen@redhat.com>
- Fix quota WARN_ON for ext4 (#521914)

* Thu Apr 01 2010 Matthew Garrett <mjg@redhat.com>
- drm-intel-acpi-populate-didl.patch: Fix backlight hotkeys on some hardware
- drm-intel-make-lvds-work.patch: Fix screen not turning back on on lid open
- linux-2.6-usb-wwan-update.patch: Update wwan code and fix qcserial

* Wed Mar 31 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops (xen/stable-2.6.32.x branch) which introduces PAT support

* Tue Mar 30 2010 John W. Linville <linville@redhat.com> 2.6.32.10-94
- Avoid null pointer dereference introduced by 'ssb: check for sprom' (#577463)

* Mon Mar 29 2010 John W. Linville <linville@redhat.com> 2.6.32.10-93
- iwlwifi: fix nfreed--
- iwlwifi: reset card during probe (#557084)
- iwlwifi: use dma_alloc_coherent (#574146)

* Mon Mar 29 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.10-91
- nouveau: fix display issues on Dell D620 laptops

* Sun Mar 28 2010 Michael Young <m.a.young@durham.ac.uk>
- try turning STACKPROTECTOR back on
- add xen includes to -devel package

* Tue Mar 23 2010 Michael Young <m.a.young@durham.ac.uk>
- update pvops which should hopefully fix ix86
- Add in a conflicts xen < 3.4.3 rule

* Mon Mar 22 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.10-90
- A few more imon driver button additions
- Fix minor init issue w/topseed 0x0008 mceusb transceivers

* Mon Mar 22 2010 Neil Horman <nhorman@redhat.com>
- Fix tg3 poll controller to not oops (bz 574969)

* Fri Mar 19 2010 John W. Linville <linville@redhat.com> 2.6.32.10-88
- Revise "ssb: check for sprom" (#533746)

* Fri Mar 19 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.10-86
- Improve mouse button and pad handling on 0xffdc imon devices
- Add xmit support to topseed 0x0008 lirc_mceusb transceiver

* Fri Mar 19 2010 John W. Linville <linville@redhat.com> 2.6.32.10-85
- ssb: check for sprom (#533746)

* Thu Mar 18 2010 Neil Horman <nhorman@redhat.com>
- Remove TIPC from config (bz 574800)

* Wed Mar 17 2010 John W. Linville <linville@redhat.com> 2.6.32.10-83
- b43: Rewrite DMA Tx status handling sanity checks

* Tue Mar 16 2010 Jarod Wilson <jarod@redhat.com>
- Catch imon panel/knob events from older 0xffdc devices
- Add two more variants of imon mce mode star and pound keys

* Tue Mar 16 2010 Chuck Ebbert <cebbert@redhat.com>
- iwlwifi-silence-tfds-in-queue-message.patch:
  don't spam the log when the problem keeps happening

* Tue Mar 16 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.10-78
- Fix null ptr deref in lirc_imon (#545599)
- Fix lirc_zilog not loading on cx2341x devices

* Mon Mar 15 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.32.10

* Mon Mar 15 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.10-76.rc1
- Rebase lirc drivers to latest git tree
- Copious amounts of imon driver update

* Mon Mar 15 2010 Michael Young <m.a.young@durham.ac.uk>
- another pvops update
- try pvops with dracut

* Mon Mar 15 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.10-75.rc1
- Make the perf package require libdwarf; fix up description (#568309)

* Sun Mar 14 2010 Chuck Ebbert <cebbert@redhat.com>
- Fix regression in tg3 driver (#571638)

* Sat Mar 13 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.32.10-rc1
- Manually fix up drm-upgrayedd.patch to apply after this stable patch:
  drm-i915-use-a-dmi-quirk-to-skip-a-broken-sdvo-tv-output.patch
- Added stable patches to upstream-reverts; we have these in our backports:
  drm-ttm-handle-oom-in-ttm_tt_swapout.patch
  v4l-dvb-13991-gspca_mr973010a-fix-cif-type-1-cameras-not-streaming-on-uhci-controllers.patch
  drm-i915-disable-tv-hotplug-status-check.patch
  drm-i915-fix-get_core_clock_speed-for-g33-class-desktop-chips.patch
  drm-radeon-r6xx-r7xx-possible-security-issue-system-ram-access.patch
  drm-radeon-kms-r600-r700-don-t-test-ib-if-ib-initialization-fails.patch
  drm-radeon-kms-forbid-creation-of-framebuffer-with-no-valid-gem-object.patch
  acpi-i915-blacklist-clevo-m5x0n-bad_lid-state.patch
- Dropped merged upstream patches:
  fix-LOOKUP_FOLLOW-on-automount-symlinks.patch
  fs-exec.c-fix-initial-stack-reservation.patch
  kms-offb-handoff.patch
  linux-2.6-input-hid-quirk-hp-touchsmart.patch
  sparc-align-clone-and-signal-stacks-to-16-bytes.patch
  sparc-additional-pci-id-xvr-500.patch

* Thu Mar 11 2010 Dennis Gilmore <dennis@ausil.us>
- add add aditional pci-id for  xvr-500
- sparc stack alignment fix

* Wed Mar 10 2010 Tom "spot" Callaway <tcallawa@redhat.com>
- cleanup and re-enable sparc selinux mprotect fix

* Wed Mar 03 2010 Dave Airlie <airlied@redhat.com> 2.6.32.9-70
- drm-upgrayed-fixes: backport a bunch of fixes from upstream
- should fix AGP slowdowns + rv740 hw.
- linux-2.6-efi-handover.patch - fix efifb handover from upstream

* Tue Mar 02 2010 Chuck Ebbert <cebbert@redhat.com>
- Include examples.txt in the perf package (#569506)

* Mon Mar 01 2010 Michael Young <m.a.young@durham.ac.uk>
- another pvops update

* Mon Mar 01 2010 Dave Jones <davej@redhat.com>
- Don't own /usr/src/kernels any more, it's now owned by filesystem. (#569438)

* Sat Feb 27 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.9-67
- Fix lookup of automount symlinks (#567813)
- Fix stack expansion rlimit check broken by a patch in 2.6.32.9

* Thu Feb 25 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.9-66
- TCP: fix broken RTO calculation causing high CPU load (#567530)

* Thu Feb 25 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.9-65
- nouveau: DP fix for cards with version 0x20 DP tables

* Wed Feb 24 2010 Michael Young <m.a.young@durham.ac.uk>
- switch to xen/stable pvops branch

* Tue Feb 23 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.9-64
- Linux 2.6.32.9

* Tue Feb 23 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.9-63.rc1
- nouveau: fix pre-nv17 output detection regression, support for GF8 IGPs

* Mon Feb 22 2010 Kyle McMartin <kyle@redhat.com>
- coredump-uid-pipe-check.patch: ditto from F-13/

* Mon Feb 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.9-61.rc1
- Drop the PCI device table in the viafb driver -- it was added in
  2.6.32 and we don't want the driver to autoload.

* Mon Feb 22 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.9-60.rc1
- Linux 2.6.32.9-rc1
- Revert the 14 DRM patches from 2.6.32.9: we already have them
- Drop other patches merged upstream:
  wmi-check-wmi-get-event-data-return-value.patch
  wmi-free-the-allocated-acpi-objects.patch
  fix-conntrack-bug-with-namespaces.patch
  prevent-runtime-conntrack-changes.patch
  fix-crash-with-sys_move_pages.patch
  futex-handle-futex-value-corruption-gracefully.patch
  futex-handle-user-space-corruption-gracefully.patch
  futex_lock_pi-key-refcnt-fix.patch
  fix-race-in-tty_fasync-properly.patch

* Thu Feb 18 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-59
- ice1712-fix-revo71-mixer-names.patch: fix mixer names for
  monty. (rhbz#566565)

* Wed Feb 17 2010 Michael Young <m.a.young@durham.ac.uk>
- try another pvops update
- fix an incorrect git conflict merge in generating pvops patch

* Wed Feb 17 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.8-58
- fix-race-in-tty_fasync-properly.patch: fix for deadlock caused
  by original patch in 2.6.32.6

* Wed Feb 17 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.8-57
- CVE-2010-0623 kernel: local DoS via futex_lock_pi

* Wed Feb 17 2010 Chuck Ebbert <cebbert@redhat.com>
- CVE-2009-4537 kernel: r8169 issue reported at 26c3
  (fix taken from Red Hat/CentOS 5.4)

* Wed Feb 17 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.8.55
- drm-nouveau-mutex.patch: add fix that didn't quite make it to linus yet

* Wed Feb 17 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: rebase fedora patchset
- drm-nouveau-shared-fb.patch: drop
- drm-nouveau-update.patch: drop, included in previous drm update

* Wed Feb 17 2010 Dave Airlie <airlied@redhat.com>
- drm-upgrayedd.patch - update - needs nouveau patch rebase
- drop reverted upstream commits since rc8 - also drop other merged patches

* Tue Feb 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-51
- vgaarb-fix-userspace-ptr-deref.patch: fix a userspace ptr deref.
  (rhbz#564246) [and correct upstream diff]

* Tue Feb 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-50
- fix-abrtd.patch: backport of nhorman's call_usermode_helper changes
  from devel/ & linux-next.

* Mon Feb 15 2010 Michael Young <m.a.young@durham.ac.uk>
- more pvops updates and try with STACKPROTECTOR off

* Tue Feb 09 2010 Michael Young <m.a.young@durham.ac.uk>
- try pvops again with xen/next after some more updates

* Tue Feb 09 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-49
- Linux 2.6.32.8
- futex-handle-user-space-corruption-gracefully.patch: Fix oops in
  the PI futex code. (rhbz#563091)

* Sun Feb 07 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-48.rc2
- xfs: xfs_swap_extents needs to handle dynamic fork offsets (rhbz#510823)
  from sandeen.

* Sun Feb 07 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-47.rc2
- fix-ima-null-ptr-deref.patch: fix null ptr deref in IMA introduced
  in 2.6.32-rc5.

* Sat Feb 06 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.8-46.rc2
- fix-crash-with-sys_move_pages.patch: sys_move_pages doesn't bounds
  check the node properly.

* Fri Feb 05 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.8-45.rc2
- Linux 2.6.32.8-rc2
- Drop fix-net-restore-ip-source-validation.patch

* Fri Feb 05 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.8-44.rc1
- Fix networking bug in 2.6.32.8-rc1

* Thu Feb 04 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.8-43.rc1
- Linux 2.6.32.8-rc1
- Revert three DRM patches from 2.6.32.8:
  drm-i915-only-enable-hotplug-for-detected-outputs.patch : already in
  drm-i915-reload-hangcheck-timer-too-for-ironlake.patch : conflicts
  drm-i915-selectively-enable-self-reclaim.patch : already in
- Drop patches merged in -stable:
  linux-2.6-userspace_kvmclock_offset.patch
  block-fix-bugs-in-bio-integrity-mempool-usage.patch

* Wed Feb 03 2010 Kyle McMartin <kyle@redhat.com>
- Fix another conntrack issue pointed out by jcm.
- Fix utrace header. (rhbz#561536)

* Wed Feb 03 2010 Kyle McMartin <kyle@redhat.com>
- fix-conntrack-bug-with-namespaces.patch: Fix for issue identified by jcm,
  http://lkml.org/lkml/2010/2/3/112

* Tue Feb 02 2010 David Woodhouse <David.Woodhouse@intel.com> 2.6.32.7-40
- Disable graphics DMAR unit on Cantiga (#538163)

* Mon Feb 01 2010 Dave Airlie <airlied@redhat.com> 2.6.32.7-39
- Add two input quirks for HP and eGalax touchscreens.

* Sat Jan 31 2010 Michael Young <m.a.young@durham.ac.uk>
- switch pvops to xen/next branch for the moment
- update to 2.6.32
- orphaned comments
-* Wed Dec 23 2009 Michael Young <m.a.young@durham.ac.uk>
-- update to latest pvops patch
-* Wed Dec 09 2009 Michael Young <m.a.young@durham.ac.uk>
-- update to latest pvops patch
-* Fri Nov 13 2009 Michael Young <m.a.young@durham.ac.uk>
-- fix typo in drm-edid-retry.patch
-* Thu Nov 12 2009 Michael Young <m.a.young@durham.ac.uk>
-- XEN_NETCHANNEL2 depends on XEN_XENBUS_FRONTEND
-- Disable XEN_PCIDEV_FRONTEND for the moment (compile issues)
-* Mon Nov 09 2009 Michael Young <m.a.young@durham.ac.uk>
-- update pvops which adds XEN_NETCHANNEL2 and XEN_PCIDEV_FRONTEND
-* Fri Oct 16 2009 Michael Young <m.a.young@durham.ac.uk>
-- update pvops patch to 2.6.31.4
-- add configuration options for XEN_PCIDEV_BACKEND and XEN_PCIDEV_BE_DEBUG
-* Sat Oct 10 2009 Michael Young <m.a.young@durham.ac.uk>
-- update pvops patch
-- try putting DRM_RADEON and DRM_NOUVEAU back in
-* Sat Oct  3 2009 Michael Young <m.a.young@durham.ac.uk>
-- update pvops patch
-* Sat Sep 26 2009 Michael Young <m.a.young@durham.ac.uk>
-- disable DRM_RADEON  and DRM_NOUVEAU due to build problems
-* Thu Sep 24 2009 Michael Young <m.a.young@durham.ac.uk>
-- Try a dri fix in the latest xen/master
-* Sat Sep 19 2009 Michael Young <m.a.young@durham.ac.uk>
-- Switch pvops from rebase/master to xen/master branch
-* Tue Sep 15 2009 Michael Young <m.a.young@durham.ac.uk>
-- switch to the F-12 branch for the moment
-- try an NX related fix

* Sat Jan 30 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.7-38
- Fix possible oops in bio-integrity code.

* Thu Jan 28 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.7-37
- Linux 2.6.32.7

* Mon Jan 25 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.6-36
- fix gspca mismerge.

* Mon Jan 25 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.6-35
- stable update 2.6.32.6
- rebase gspca crud.

* Mon Jan 25 2010 Dave Jones <davej@redhat.com> 2.6.32.5-34
- Disable CONFIG_X86_CPU_DEBUG

* Sun Jan 24 2010 Hans de Goede <hdegoede@redhat.com> 2.6.32.5-33
- Rebase gspca usb webcam driver + sub drivers to latest upstream, this
  adds support for the following webcam bridge chipsets:
  benq, cpia1, ovfx2, sn9c2028, w996xCF, stv0680;
  and also includes many many bugfixes (hopefully also fixes 531234)

* Sat Jan 23 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.32.5-32
- Linux 2.6.32.5
- Revert commit c7c85101afd0cb8ce497456d12ee1cad4aad152f from
  upstream .32.5 because it conflicts with our DRM update.

* Sat Jan 23 2010 Dave Airlie <airlied@redhat.com> 2.6.32.4-31
- fix dracut depends

* Thu Jan 21 2010 John W. Linville <linville@redhat.com> 2.6.32.4-30
- Report meaningful values for MCS rates through wireless extensions

* Wed Jan 20 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.4-29
- add appleir usb driver

* Mon Jan 18 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.4-28
- Linux stable 2.6.32.4
- drm-upgrayedd: rebase for related changes in intel_display.c, i915_drv.h

* Mon Jan 18 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.3-27
- various nouveau fixes from upstream
- dropped drm-nouveau-bios-paranoia.patch, it's upstream now

* Thu Jan 14 2010 Adam Jackson <ajax@redhat.com> 2.6.32.3-26
- Don't generate i915 TV hotplug interrupts ever ever ever.

* Thu Jan 14 2010 Josef Bacik <josef@toxicpanda.com> 2.6.32.3-25
- fix null pointer dereference in btrfs acl code

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-24
- drm fixes from upstream - mostly printk stupids + integrate radeon s/r fix

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-23
- crystalhd fix build on powerpc

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-22
- bring back offb handoff patch - fixes G5 + nouveau

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-21
- fix regression in radeon s/r - hangs on suspend

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-20
- force depend ati firmware, better safe than sorry. I don't
  think dracut and dracut kernel are what I wanted to do.

* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-19
- update dracut requires to make sure we get -ati firmware
- add fbdev multi-card console fix patch

* Tue Jan 12 2010 Jarod Wilson <jarod@redhat.com> 2.6.32.3-18
- Add Broadcom Crystal HD driver from staging

* Tue Jan 12 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.3-17
- add nouveau to staging Kconfig

* Tue Jan 12 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.3-16
- nouveau: fix nvac noaccel patch, not sure what happened there!

* Tue Jan 12 2010 Ben Skeggs <bskeggs@redhat.com> 2.6.32.3-15
- nouveau: patches and firmware from F12 that aren't in upstream kernel

* Mon Jan 11 2010 Dave Airlie <airlied@redhat.com> 2.6.32.3-14
- drm-upgrayedd.patch: rebase to present 2.6.33 (drm-linus)
- nouveau TODO - comment out no-tv-hp for now, leave patch
- we can readd if all the upstream goodness didn't fix it

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.3-13
- drm-intel-no-tv-hotplug.patch: re-add lost patch from F-12
  2.6.31 (#522611, #544671)

* Mon Jan 11 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.3-12
- Re-enable ATM_HE (#545289)

* Fri Jan 08 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-11
- Add another symbol to look for when generating modules.block

* Thu Jan 07 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-10
- Turn off default powersave mode for AC97 and HDA audio devices
  due to continuing bug reports (can still be enabled in sysfs.)
- Remove some patches that are upstream:
  v4l-dvb-fix-cx25840-firmware-loading.patch
  fix-9p-fscache.patch
  ext4-fix-insufficient-checks-in-EXT4_IOC_MOVE_EXT.patch

* Thu Jan 07 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-9
- Change configs to build the acerhdf driver again, requires
  setting CONFIG_HWMON=y

* Wed Jan 06 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-8
- Linux 2.6.32.3

* Wed Jan 06 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-7.rc2
- Remove obsolete config options (generated .config files are
  unchanged.)

* Wed Jan 06 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-6.rc2
- Linux 2.6.32.3-rc2

* Tue Jan 05 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.3-5.rc1
- Linux 2.6.32.3-rc1
- Drop merged patches:
  linux-2.6-fix-btusb-autosuspend.patch
  drm-radeon-fix-crtc-vbl-update-for-r600.patch

* Tue Jan 05 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.2-4
- Fix WMI driver oopses and a memory leak.

* Tue Jan 05 2010 Chuck Ebbert <cebbert@redhat.com>  2.6.32.2-3
- Run 'make release', fix up tracing options to match what shipped
  in F-12, fix CPU count on x86-64.

* Mon Jan 04 2010 Dave Jones <davej@redhat.com>
- Drop some of the spinlock/vm taint patches. dump_stack() already does same.

* Fri Jan  1 2010 Kyle McMartin <kyle@redhat.com> 2.6.32.2-1
- Rebased F-12 to 2.6.32, still needs forward porting of patches.

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

* Thu Sep 10 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops and get to 2.6.31

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

* Sat Sep 04 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops which includes swiotlb updates and a network fix
- try a drm build fix
- therefore re-enable CONFIG_DRM_NOUVEAU and CONFIG_DRM_RADEON_KMS options

* Fri Sep 04 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.203.rc8.git2
- Fix kernel build errors when building firmware by removing the
  .config file before that step and restoring it afterward.

* Thu Sep 03 2009 Adam Jackson <ajax@redhat.com>
- drm-ddc-caching-bug.patch: Empty the connector's mode list when it's
  disconnected.

* Thu Sep 03 2009 Jarod Wilson <jarod@redhat.com>
- Update hdpvr and lirc_zilog drivers for 2.6.31 i2c

* Thu Sep 03 2009 Michael Young <m.a.young@durham.ac.uk>
- Update pvops patch to try stack protector on i686 again
- disable linux-2.6-xen-stack-protector-fix.patch as we already have it

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

* Wed Aug 26 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops again.

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

* Mon Aug 24 2009 Michael Young <m.a.young@durham.ac.uk>
- turn off stackprotector on i686 for a working build

* Mon Aug 24 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7-git1

* Sat Aug 22 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc7

* Thu Aug 20 2009 Michael Young <m.a.young@durham.ac.uk>
- test a i686 stackprotector patch

* Thu Aug 20 2009 Mark McLoughlin <markmc@redhat.com>
- Disable LZMA for xen (#515831)

* Thu Aug 20 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc6-git5
- Fix up drm-r600-kms.patch
- Drop fix-perf-make-man-failure.patch

* Wed Aug 19 2009 Michael Young <m.a.young@durham.ac.uk>
- update rebase/master to test i686 stackprotector issue

* Wed Aug 19 2009 Chuck Ebbert <cebbert@redhat.com>
- 2.6.31-rc6-git5
- Revert linux-2.6-debug-vm-would-have-oomkilled.patch to v1.2
  because upstream changes to oom-kill.c were all reverted.

* Tue Aug 18 2009 Kyle McMartin <kyle@redhat.com>
- Fix up perf so that it builds docs now that they are fixed.
- with_docs disables perf docs too. be warned. (logic is that the
  build deps are (mostly) the same, so if you don't want one, odds are...)

* Tue Aug 18 2009 Michael Young <m.a.young@durham.ac.uk>
- another rebase/master update
  - try upstream STACKPROTECTOR fixes
  - MCE/MCA support
- remove grubby dependency to make it more F11 friendly, it isn't needed
  until dracut is re-enabled

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

* Fri Aug 14 2009 Michael Young <m.a.young@durham.ac.uk>
- another rebase/master update
- make perf a Source file so the kernel builds

* Fri Aug 14 2009 Dave Jones <davej@redhat.com> 2.6.31-0.155.rc6
- 2.6.31-rc6

* Thu Aug 13 2009 Michael Young <m.a.young@durham.ac.uk>
- add another rebase/master update

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

* Tue Aug 11 2009 Michael Young <m.a.young@durham.ac.uk>
- CONFIG_CC_STACKPROTECTOR was probably innocent but leave it off
  a bit longer just in case
- add rebase/master update

* Tue Aug 11 2009 Ben Skeggs <bskeggs@redhat.com>
- nouveau: various cleanups and fixes + more sanity checking in dma paths

* Mon Aug 10 2009 Michael Young <m.a.young@durham.ac.uk>
- disable CONFIG_CC_STACKPROTECTOR for x86_64 again (the workaround
  needs revising)
- disable dracut until the issue with livecd is fixed

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

* Sat Aug 08 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops patch to latest rebase/master and current rawhide
- tell kernel.spec not to build non-PAE kernel for i686

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

* Wed Jul 15 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops patch x2

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

* Thu Jul 09 2009 Michael Young <m.a.young@durham.ac.uk>
- disable CONFIG_KERNEL_LZMA as xen doesn't like it

* Thu Jul 09 2009 Dave Jones <davej@redhat.com> 2.6.31-0.62.rc2.git4
- Use correct spinlock initialization in dma-debug

* Thu Jul 09 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.61.rc2.git4
- 2.6.31-rc2-git4

* Thu Jul 09 2009 Jarod Wilson <jarod@redhat.com>
- Enable IR receiver on the Hauppauge HD PVR
- Trim the changelog, axing everything before 2.6.29 (see cvs
  if you still really want to see that far back)

* Thu Jul 09 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops and see if CONFIG_KERNEL_LZMA=y is compatible with xen

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

* Tue Jun 30 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops from xen/rebase/master branch which should return disk
  and network support

* Tue Jun 30 2009 Ben Skeggs <bskeggs@redhat.com>
- drm-nouveau.patch: match upstream

* Mon Jun 29 2009 Chuck Ebbert <cebbert@redhat.com> 2.6.31-0.35.rc1.git5
- 2.6.31-rc1-git5
- CONFIG_LEDS_LP3944=m

* Mon Jun 29 2009 Chuck Ebbert <cebbert@redhat.com>
- Try to fix the dm overlay bug for real (#505121)

* Sat Jun 27 2009 Michael Young <m.a.young@durham.ac.uk>
- switch pvops to xen/rebase/master branch
- rebase pvops on 2.6.31-rc1-git2
- drivers/gpu/drm/ttm/ttm_agp_backend.c doesn't like 
  include/linux/swiotlb.h so disable the options CONFIG_DRM_RADEON_KMS
  and CONFIG_DRM_NOUVEAU that use it.

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

* Sat Jun 13 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops to 2.6.30

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

* Thu Jun 04 2009 Michael Young <m.a.young@durham.ac.uk>
- pvops update to 2.6.30-rc8

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

* Fri May 22 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops patch to latest xen-tip/next version
- pull in patch for !PERF_COUNTERS build failure
- That still doesn't work so enable PERF_COUNTERS for the moment

* Thu May 21 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops patch to latest xen-tip/next version

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

* Thu May 07 2009 Michael Young <m.a.young@durham.ac.uk>
- i686 CONFIG_CC_STACKPROTECTOR is still broken so disable it

* Wed May 06 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops patch from xen-tip/master - hopefully i686 will work again

* Wed May 06 2009 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.30-rc4-git3
- linux-2.6-cdrom-door-status.patch: merged upstream.
- linux-2.6-iwl3945-remove-useless-exports.patch: merged upstream.
- linux-2.6-utrace.patch: rebase against changes to fs/proc/array.c
- USB_NET_CDC_EEM=m

* Sat May 02 2009 Michael Young <m.a.young@durham.ac.uk>
- update pvops patch from xen-tip/master
- Try enabling CONFIG_XEN_GNTDEV and CONFIG_XEN_PCI_PASSTHROUGH
- test a patch to allow CONFIG_CC_STACKPROTECTOR to be enabled
- patch to allow kernel to build with XEN_PCI_PASSTHROUGH and current config

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

* Fri Apr 24 2009 Michael Young <m.a.young@durham.ac.uk>
- switch back to devel kernel branch
- switch pvops to xen-tip/next branch
- remove added config options now in main fedora configuration
- add in new config options required by new pvops patch
- relocate the below comment stranded by the devel switch
-* Tue Apr 14 2009 Michael Young <m.a.young@durham.ac.uk>
-- follow the 2.6.29.1 stable branch for the moment
-- reset a few config settings to Fedora defaults
-- drop the squashfs 3 patches as we can't build both
-- docs won't build, so don't build them

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

* Mon Mar 30 2009 Michael Young <m.a.young@durham.ac.uk>
- pvops update and merging of patches
- disable squashfs 3 again since we can't build both versions at the same time

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

* Sun Mar 29 2009 Michael Young <m.a.young@durham.ac.uk>
- try push2/xen/dom0/master branch rather than xen/dom0/hackery as it should
    be closer to the proposed 2.6.30 merge
- add squashfs 3 support from F-10 to make kernel more friendly to fc10
- Set CONFIG_HIGHPTE=n in config-x86-generic to avoid eventual crash problem
- comment out linux-2.6-net-fix-gro-bug.patch which is in push2/xen/dom0/master

* Sun Mar 29 2009 Michael Young <m.a.young@durham.ac.uk>
- drop dropwatch patch due to compile problems
- revert pvops patches bd4a7874716d1b1f69cacfef4adf9f94050ecd82 and
    cfb667260eb7f6dd26ceb6d49da818978396757d to get the kernel to boot

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

* Wed Mar 25 2009 Michael Young <m.a.young@durham.ac.uk>
- disable linux-2.6-utrace-ftrace.patch due to merge problems
- minor pvops update

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

* Tue Mar 24 2009 Michael Young <m.a.young@durham.ac.uk>
- Update pvops patch and fix package numbering for 2.6.29

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
