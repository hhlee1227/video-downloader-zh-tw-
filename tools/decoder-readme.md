# iOS Shortcut Decoder

A lightweight command-line tool written in Python to decode and extract logic from iOS 15+ signed `.shortcut` files. 

Since iOS 15, Apple `.shortcut` files are packed inside an Apple Encrypted Archive (AEA) and code-signed to prevent unauthorized modifications. This tool extracts the embedded public key from the shortcut's unencrypted metadata, uses it to verify and decompress the AEA payload, and parses the internal binary property list (bplist) into a human-readable JSON format.

## Requirements

The tool requires Python 3 and the following dependencies:
- `python-aea` (for parsing Apple Encrypted Archives)
- `cryptography` (for extracting ECDSA certificates)

Install the requirements via pip:

```bash
pip install python-aea cryptography
```

## Usage

**Option 1: Drag and Drop (Windows)**
Simply drag and drop your `.shortcut` file onto `iOSShortcutDecoder.exe`. The tool will automatically create a `.json` and `.txt` file in the same folder.

**Option 2: Command Line**
Run the script from your terminal:

```bash
iOSShortcutDecoder.exe "PathToShortcut.shortcut"
```

The tool will output:
1. `PathToShortcut.json`: The full decoded bplist as JSON.
2. `PathToShortcut.txt`: A simplified, highly readable summary of the shortcut's core logic (omitting noisy metadata and UUIDs).

## Example

```bash
iOSShortcutDecoder.exe "XoaAnhDaUpload.shortcut"
```

Output:
```
[*] Reading shortcut file: XoaAnhDaUpload.shortcut
[*] Extracting certificate and public key from metadata...
[*] Decrypting and decompressing AEA payload...
[*] Inner payload is an Apple Archive (AA01). Extracting bplist...
[*] Parsing shortcut logic...
[+] Successfully decoded shortcut to XoaAnhDaUpload.json
```

## Why JSON output?

Modifying signed iOS 15+ shortcuts and importing them back into an iOS device is very difficult without an Apple Developer certificate, as iOS will reject modified unsigned files. 

This tool provides a read-only translation of the shortcut's logic. You can use the generated JSON as a "blueprint" to understand exactly what the shortcut does (e.g. actions, variables, API calls) and then manually recreate or edit those steps directly in the Shortcuts app on your iPhone or iPad.
