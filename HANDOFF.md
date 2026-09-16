# CourseCarry handoff

## Current objective and constraints

- Fix the user-confirmed startup failure in the portable Windows release: `ImportError: DLL load failed while importing QtGui: 找不到指定的程序。`
- The affected laptop still reports the same failure with `CourseCarry-v0.6.2-alpha-windows-x64.zip`.
- The final release must be extract-and-run. End users must not have to install Python, Qt, the Visual C++ redistributable, or any other runtime.
- Preserve existing user changes and private LMS data. Do not claim affected-laptop compatibility until that laptop actually opens the release.
- Update `README.md` alongside any CourseCarry behavior or release change.

## Current verified state

- The existing release ZIP is `D:\CourseCarry\release\CourseCarry-v0.6.2-alpha-windows-x64.zip` (73,085,018 bytes; SHA-256 previously recorded as `d3a3692bbf265fb9590a395274ebdd7e6c84155ae07255b32c229f81f29c6034`).
- It was built with Python 3.13.15, PySide6/Qt 6.11.2, and Nuitka 4.1.1.
- Local source tests and packaged self-tests passed on the development laptop, but that evidence did not reproduce or resolve the affected-laptop failure.
- Static inspection confirms `qt6gui.dll` imports Windows graphics APIs including `D3D12SerializeVersionedRootSignature` and two D3D12 ordinals, plus the bundled Microsoft C++ runtime DLLs.
- Only Python 3.13 is installed globally on the development laptop. No older PySide6 wheel is currently cached.
- Neither `D:\CourseCarry\HANDOFF.md` nor `D:\Politeload\HANDOFF.md` existed before this checkpoint.
- Static comparison found the failed Qt 6.11.2 `Qt6Gui.dll` directly imports `d3d12.dll` procedures/ordinals that Qt 6.5.3 does not import.
- An isolated Python 3.11.9 + PySide6 6.5.3 build environment was created under `D:\Politeload`; it is a build tool only and is not required on release laptops.
- All 39 existing offline tests passed under Python 3.11/Qt 6.5.3. Three new pre-Qt startup diagnostic tests passed, and an offscreen Qt 6.5.3 smoke test constructed the real main window at 1220x790.
- The reviewed v0.6.3-alpha source, build gates, startup diagnostics, tests, README, changelog, and release documentation have been copied into `D:\CourseCarry`.
- Nuitka successfully built `dist\CourseCarry\CourseCarry.exe` with Python 3.11 and Qt 6.5.3. The bundle verifier passed the runtime, system-DLL exclusion, Qt version, and direct-D3D12 checks.
- The exact freshly extracted v0.6.3 ZIP passed `--bundle-self-test` with exit code 0, and a normal launch created a native window titled `CourseCarry 0.6.3-alpha`.
- Release artifact: `D:\CourseCarry\release\CourseCarry-v0.6.3-alpha-windows-x64.zip`; final SHA-256 `ddb443f6d455681434cf110292fce1e07c7ba261b16ecccf2a6705b674675817`.
- The ZIP includes `CourseCarry-Diagnostic.cmd` and `.ps1`. Windows PowerShell 5.1 tested the exact extracted diagnostic successfully: every listed native component loaded, QtGui 6.5.3 was reported without a direct D3D12 reference, and the report contained no username or filesystem paths.
- Temporary smoke-test extraction/profile folders were removed after testing.
- The complete v0.6.3-alpha source update was committed as `0cee297` and pushed to `master` at `https://github.com/Jinghua2128/CourseCarry` on 2026-09-16. GitHub reported that the repository had already moved from the old `Politeload` URL, so the local `origin` was updated to the CourseCarry URL.
- No Git tag or GitHub Release was created. The verified release ZIP and checksum remain local for the user to publish separately.

## Work in progress

- Obtain the affected-laptop result for the exact v0.6.3-alpha ZIP.

## Blockers and required external verification

- The affected laptop's Windows version/build and architecture have not been captured yet.
- A successful build on the development laptop is not final verification. The next candidate ZIP must be extracted into a fresh folder and opened on the affected laptop.

## Concrete next step

Transfer only the v0.6.3-alpha ZIP and `.sha256` file to the affected laptop, delete the old extracted CourseCarry folder, extract the new ZIP into a fresh folder, and run `CourseCarry.exe`. If it still fails, collect `%LOCALAPPDATA%\CourseCarry\startup-diagnostic.txt` instead of installing anything.
