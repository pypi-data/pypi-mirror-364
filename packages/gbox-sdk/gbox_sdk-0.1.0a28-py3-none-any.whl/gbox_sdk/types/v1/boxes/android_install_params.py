# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ...._types import FileTypes
from ...._utils import PropertyInfo

__all__ = ["AndroidInstallParams", "InstallAndroidPkgByFile", "InstallAndroidPkgByURL"]


class InstallAndroidPkgByFile(TypedDict, total=False):
    apk: Required[FileTypes]
    """APK file or ZIP archive to install (max file size: 512MB).

    **Single APK mode (installMultiple: false):**

    - Upload a single APK file (e.g., app.apk)

    **Install-Multiple mode (installMultiple: true):**

    - Upload a ZIP archive containing multiple APK files
    - ZIP filename example: com.reddit.frontpage-gplay.zip
    - ZIP contents example:

    com.reddit.frontpage-gplay.zip └── com.reddit.frontpage-gplay/ (folder) ├──
    reddit-base.apk (base APK) ├── reddit-arm64.apk (architecture-specific) ├──
    reddit-en.apk (language pack) └── reddit-mdpi.apk (density-specific resources)

    This is commonly used for split APKs where different components are separated by
    architecture, language, or screen density.
    """

    install_multiple: Annotated[bool, PropertyInfo(alias="installMultiple")]
    """Whether to use 'adb install-multiple' command for installation.

    When true, uses install-multiple which is useful for split APKs or when
    installing multiple related packages. When false, uses standard 'adb install'
    command. Split APKs are commonly used for apps with different architecture
    variants, language packs, or modular components.
    """

    open: bool
    """Whether to open the app after installation.

    Will find and launch the launcher activity of the installed app. If there are
    multiple launcher activities, only one will be opened. If the installed APK has
    no launcher activity, this parameter will have no effect.
    """


class InstallAndroidPkgByURL(TypedDict, total=False):
    apk: Required[str]
    """HTTP URL to download APK file or ZIP archive (max file size: 512MB).

    **Single APK mode (installMultiple: false):**

    - Provide URL to a single APK file
    - Example: https://example.com/app.apk

    **Install-Multiple mode (installMultiple: true):**

    - Provide URL to a ZIP archive containing multiple APK files
    - ZIP filename example: com.reddit.frontpage-gplay.zip
    - ZIP contents example:

    com.reddit.frontpage-gplay.zip └── com.reddit.frontpage-gplay/ (folder) ├──
    reddit-base.apk (base APK) ├── reddit-arm64.apk (architecture-specific) ├──
    reddit-en.apk (language pack) └── reddit-mdpi.apk (density-specific resources)

    - Example URL: https://example.com/com.reddit.frontpage-gplay.zip

    This is commonly used for split APKs where different components are separated by
    architecture, language, or screen density.
    """

    install_multiple: Annotated[bool, PropertyInfo(alias="installMultiple")]
    """Whether to use 'adb install-multiple' command for installation.

    When true, uses install-multiple which is useful for split APKs or when
    installing multiple related packages. When false, uses standard 'adb install'
    command. Split APKs are commonly used for apps with different architecture
    variants, language packs, or modular components.
    """

    open: bool
    """Whether to open the app after installation.

    Will find and launch the launcher activity of the installed app. If there are
    multiple launcher activities, only one will be opened. If the installed APK has
    no launcher activity, this parameter will have no effect.
    """


AndroidInstallParams: TypeAlias = Union[InstallAndroidPkgByFile, InstallAndroidPkgByURL]
