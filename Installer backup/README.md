# PrismTrack Agent MSI Installer (Rust + cargo-wix)

Rust-based MSI installer builder using `cargo-wix` for PrismTrack Agent.

## Requirements

- Rust 1.70+ (install from https://rustup.rs/)
- WiX Toolset 3.11+ (install from https://wixtoolset.org/)
- cargo-wix (install with: `cargo install cargo-wix`)
- PrismTrackAgent.exe built (run `python build_exe.py` in PrismTrackAgent directory)

## Building the MSI Installer

### Step 1: Install cargo-wix (if not already installed)

```bash
cargo install cargo-wix
```

### Step 2: Build the MSI

```bash
cd installer
cargo wix
```

The MSI installer will be created as:
- `installer/PrismTrackAgent.msi` (or `target/wix/PrismTrackAgent.msi`)

## How It Works

The `cargo-wix` tool:
1. Compiles the Rust project (dummy binary for cargo-wix)
2. Uses WiX Toolset to compile `wix/main.wxs`
3. Links the MSI installer with all files
4. Creates `PrismTrackAgent.msi`

## MSI Installer Features

- Installs to: `C:\Program Files\PrismTrack\Agent\`
- Includes:
  - `PrismTrackAgent.exe` (Python executable)
  - `config.json` (configuration file)
  - `installer_script.ps1` (PowerShell installation script)
- Custom action: Runs PowerShell script after installation
- PowerShell script:
  - Collects system information (Hardware UUID, username, hostname, UPN)
  - Registers agent with backend API
  - Saves agent_token to config.json
  - Starts PrismTrackAgent.exe

## Files

- `Cargo.toml` - Rust project configuration with cargo-wix metadata
- `src/main.rs` - Dummy Rust binary (not included in MSI)
- `wix/main.wxs` - WiX source file defining MSI structure
- `installer_script.ps1` - PowerShell installation script

## Customization

Edit `wix/main.wxs` to customize:
- Installation directory
- Files to include
- Custom actions
- UI appearance

## Troubleshooting

### cargo-wix not found
```bash
cargo install cargo-wix
```

### WiX Toolset not found
- Install from: https://wixtoolset.org/
- Add to PATH or restart terminal

### PrismTrackAgent.exe not found
- Build the executable first:
  ```bash
  cd ../PrismTrackAgent
  python build_exe.py
  ```

### Build errors
- Ensure all source files exist
- Check file paths in `wix/main.wxs`
- Verify WiX Toolset is properly installed
