# Fix for yt-dlp Issue #15712 (android_sdkless 403)

## Summary
The yt-dlp issue "unable to download video data: HTTP 403" when using
`android_sdkless` formats was fixed upstream in the latest yt-dlp release.
Updating yt-dlp resolves the problem.

## What This Build Does
- Requires yt-dlp 2026.1.31 or newer in `requirements.txt`.
- Automatically disables the `android_sdkless` client for older yt-dlp
  versions (workaround), but allows it again when the fix is present.

## How to Fix for Users
1. Update yt-dlp to the latest stable release.
   - Pip install:
     - `python3 -m pip install --upgrade yt-dlp`
   - System package manager:
     - Use the app's "Update Dependencies" action or your OS package manager.
2. Confirm yt-dlp version is 2026.1.31 or newer.
3. Re-try the download.

## Notes
- If you must stay on an older yt-dlp version, the app keeps the
  `android_sdkless` workaround enabled to avoid 403 errors.
- As of Feb 3, 2026, the latest stable release on PyPI is 2026.1.31.
