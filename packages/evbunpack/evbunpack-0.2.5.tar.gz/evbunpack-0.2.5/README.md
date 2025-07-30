# evbunpack
[![Windows Build](https://github.com/mos9527/evbunpack/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/mos9527/evbunpack/blob/main/.github/workflows/build-and-publish.yml) [![Releases](https://img.shields.io/github/downloads/mos9527/evbunpack/total.svg)](https://GitHub.com/mos9527/evbunpack/releases/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 

[Enigma Virtual Box](https://enigmaprotector.com/en/downloads/changelogenigmavb.html) unpacker

## Features
- Executable unpacking
  - TLS, Exceptions, Import Tables and Relocs are recovered
  - Executables with [Overlays](https://davidghughes.com/2023/08/06/overlays/) can be restored as well
  - Enigma loader DLLs and extra data added by the packer is stripped
- Virtual Box Files unpacking
  - Supports both built-in files and external packages
  - Supports compressed mode

## Tested Versions
- This applies to PE unpacking. If the chosen PE unpack variant does not work, please try out the other ones with `-pe [variant]`

| Packer Version | Notes | Unpack with Flags |
| - | - | - |
| 11.00 | Automatically tested in CI for x86/x64 binaries.  | `-pe 10_70` |
| 10.70 | Automatically tested in CI for x86/x64 binaries.  | `-pe 10_70` |
| 9.70 | Automatically tested in CI for x86/x64 binaries. |  `-pe 9_70` |
| 7.80 | Automatically tested in CI for x86/x64 binaries | `-pe 7_80 --legacy-fs ` |

## Installation
  **For Windows Users** : Builds are available [here](https://github.com/mos9527/evbunpack/releases)

  Or get the latest version from PyPi:
  ```bash
      pip install evbunpack
  ```

## Usage

    usage: evbunpack [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-l] [--ignore-fs] [--ignore-pe] [--legacy-fs] [-pe {10_70,9_70,7_80}] [--out-pe OUT_PE] file output

    Enigma Virtual Box Unpacker

    options:
      -h, --help            show this help message and exit
      --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Set log level

    Flags:
      -l, --list            Don't extract the files and print the table of content to stderr only
      --ignore-fs           Don't extract virtual filesystem
      --ignore-pe           Don't restore the executable
      --legacy-fs           Use legacy mode for filesystem extraction
      -pe {10_70,9_70,7_80}, --pe-variant {10_70,9_70,7_80}
                            Unpacker variant to use when unpacking EXEs. default=9_70

    Overrides:
      --out-pe OUT_PE       (If the executable is to be recovered) Where the unpacked EXE is saved. Leave as-is to save it in the output folder.

    Input:
      file                  File to be unpacked
      output                Output folder

### Example Usage ([test file available here](https://github.com/mos9527/evbunpack/blob/main/tests/x64_PackerTestApp_packed_20240522.exe))
Input:
```bash
evbunpack x64_PackerTestApp_packed_20240522.exe output
```
Output:
```bash
INFO: Enigma Virtual Box Unpacker v0.2.1
INFO: Extracting virtual filesystem
Filesystem:
   └─── output
       └─── output/README.txt
Writing File [size=0x11, offset=0x3465]: total=      11h read=       0h
INFO: Extraction complete
INFO: Restoring executable
INFO: Using default executable save path: output\x64_PackerTestApp_packed_20240522.exe
Saving PE: total=    3211h read=       0h
INFO: Unpacked PE saved: output\x64_PackerTestApp_packed_20240522.exe
```
## TODO
- Automatically detect packer version

## Credits
- [evb-extractor](https://github.com/EVBExtractor/evb-extractor)
- [aplib](https://github.com/snemes/aplib)

## License
Apache 2.0 License
