```
     /\\  \\         /\\  \\         /\\__\\         /\\__\\         /\\  \\
    /::\\  \\       /::\\  \\       /:/  /        /:/  /        /::\\  \\
   /:/\\:\\  \\     /:/\\:\\  \\     /:/__/        /:/__/        /:/\\:\\  \\
  /:/  \\:\\  \\   /::\\~\\:\\  \\   /::\\__\\____   /::\\__\\____   /:/  \\:\\  \\
 /:/__/_\\:\\__\\ /:/\\:\\ \\:\\__\\ /:/\\:::::\\__\\ /:/\\:::::\\__\\ /:/__/ \\:\\__\\
 \\:\\  /\\ \\/__/ \\:\\~\\:\\ \\/__/ \\/_|:|~~|~    \\/_|:|~~|~    \\:\\  \\ /:/  /
  \\:\\ \\:\\__\\    \\:\\ \\:\\__\\      |:|  |        |:|  |      \\:\\  /:/  /
   \\:\\/:/  /     \\:\\ \\/__/      |:|  |        |:|  |       \\:\\/:/  /
    \\::/  /       \\:\\__\\        |:|  |        |:|  |        \\::/  /
     \\/__/         \\/__/         \\|__|         \\|__|         \\/__/
```

## Overview
TODO

## Firmware
Classe 300 supports firmware update through the mini USB port on the back of the device. You can download the firmware file from [BTicino's website](https://www.homesystems-legrandgroup.com/) and flash it using the [MyHOME Suite](https://www.homesystems-legrandgroup.com/home?p_p_id=it_smc_bticino_homesystems_search_AutocompletesearchPortlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_it_smc_bticino_homesystems_search_AutocompletesearchPortlet_journalArticleId=2493426&_it_smc_bticino_homesystems_search_AutocompletesearchPortlet_mvcPath=%2Fview_journal_article_content.jsp) software (Windows-only).

The firmware file (.fwz) is actually just a password-protected zip archive (the password is `C300`). You can unpack it using:

```sh
unzip -P C300 C300_020012.fwz -d out
```

It contains 4 files:
- `fwz.xml`: firmware metadata XML with file list and version info
- `uImage`: u-boot image
- `btweb_only.ubifs`: main UBIfs image
- `btweb_only_recovery.ubifs`: recovery UBIfs image, same as above, but no GUI?

The device is running a custom-built version of (now defunct) [Ångström](https://web.archive.org/web/20200815133137/http://angstrom-distribution.org/) OpenEmbedded-based Linux distribution with a layer of BTicino's own tools. Busybox is available.

If you wish to quickly preview contents of UBIfs image files, you can use the [UBI Reader](https://github.com/onekey-sec/ubi_reader) tool to extract them:

```sh
ubireader_extract_files btweb_only.ubifs -o btweb_only
ubireader_extract_files btweb_only_recovery.ubifs -o btweb_only_recovery
```

## Flashing
TODO

## OpenWebNet
TODO

## Gateway
TODO

## Integrations
TODO
