# Luraph v15.2 Deobfuscator

A standalone, single-engine CLI build extracted from [Tweety0ff/LuauGhidra](https://github.com/Tweety0ff/LuauGhidra). This branch contains only the Luraph v15.2 deobfuscator and the runtime, parser, and helper tools it uses. The desktop UI and other deobfuscators are not included.

## Requirements

- Node.js 18 or newer
- Python 3.10 or newer
- Git, CMake, and a C++17 compiler to build the patched Luau tools

The deobfuscator has no npm or pip packages to install.

## Build the Luau tools

From the repository root:

```bash
python build_luau.py
```

This fetches the Luau source, applies the compatibility patches required by the sandbox, and builds `bin/luau` and `bin/luau-ast` (on Windows, the executables have `.exe` extensions).

## Run

```bash
node deob.js protected.lua -o deobfuscated.lua
```

Useful options:

- `--no-devirt` — produce a fast behaviour trace without VM lifting
- `--debug` — keep intermediate trace and analysis files
- `--detect` — detect the obfuscator and print the result without deobfuscating
- `--cfg-json '{"key": value}'` — pass additional sandbox configuration

The input can be a `.lua` or `.luau` file. Without an explicit output path, the result is written to an `output/` directory beside the input.

## Optional post-clean

After deobfuscation, remove dead statements that the Luau AST pass can prove unreachable:

```powershell
python luaclean.py bin/luau-ast.exe deobfuscated.lua deobfuscated-clean.lua
```

On Linux/macOS, use `bin/luau-ast` instead of `bin/luau-ast.exe`.

## Included components

- `deob.js` and `src/` — CLI, detection, sandbox orchestration, and trace handling
- `core/` — Python devirtualizer, control-flow reconstruction, and code generation
- `runtime/` and `protocol.json` — offline Luau sandbox and shared runtime protocol
- `build_luau.py` — builds the patched Luau runtime and AST tool
- `tools/` — proto inspection helpers for advanced analysis

For setup details and troubleshooting, see [SETUP.md](SETUP.md). For implementation notes, see [TECHNICAL.md](TECHNICAL.md).

## Responsible use

Use this tool only to inspect scripts you own or are authorized to analyze. Treat deobfuscated output as untrusted code; do not execute it without reviewing it first.
