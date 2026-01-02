"""
Create MSI Installer for PrismTrack Agent
Uses Python msilib to create a basic MSI installer
"""
import os
import sys
import shutil
import zipfile
from pathlib import Path
import msilib
from msilib import schema, sequence, text

def create_msi():
    """Create MSI installer for PrismTrack Agent"""
    
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    agent_dir = project_root / "PrismTrackAgent"
    dist_dir = agent_dir / "dist"
    exe_path = dist_dir / "PrismTrackAgent.exe"
    
    # Check if executable exists
    if not exe_path.exists():
        print(f"ERROR: PrismTrackAgent.exe not found at: {exe_path}")
        print("Please build the executable first using: python build_exe.py")
        return False
    
    print("Creating MSI installer for PrismTrack Agent...")
    print(f"  Source: {exe_path}")
    
    # Create output directory
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)
    msi_path = output_dir / "PrismTrackAgent.msi"
    
    # Database name
    db_name = str(msi_path)
    
    # Create MSI database
    print("  Creating MSI database...")
    db = msilib.init_database(
        db_name,
        schema,
        "PrismTrack Agent",
        "{8B8B8B8B-8B8B-8B8B-8B8B-8B8B8B8B8B8B}",  # Product GUID
        "1.0.0"
    )
    
    # Add properties
    msilib.add_tables(db, [
        ("Property", [
            ("ProductName", "PrismTrack Agent"),
            ("ProductVersion", "1.0.0"),
            ("Manufacturer", "PrismTrack"),
            ("ProductCode", "{8B8B8B8B-8B8B-8B8B-8B8B-8B8B8B8B8B8B}"),
            ("UpgradeCode", "{9C9C9C9C-9C9C-9C9C-9C9C-9C9C9C9C9C9C}"),
        ]),
        ("Directory", [
            ("TARGETDIR", "SourceDir"),
            ("ProgramFilesFolder", "TARGETDIR"),
            ("INSTALLDIR", "ProgramFilesFolder", "PrismTrack"),
            ("AGENTDIR", "INSTALLDIR", "Agent"),
        ]),
        ("Component", [
            ("AgentExe", "AGENTDIR", "PrismTrackAgent.exe"),
        ]),
        ("File", [
            ("PrismTrackAgent.exe", "AgentExe", "PrismTrackAgent.exe", 512, exe_path.stat().st_size, "#PrismTrackAgent.exe"),
        ]),
        ("Feature", [
            ("DefaultFeature", "PrismTrack Agent", "Complete installation", 1, None, ["AgentExe"]),
        ]),
    ])
    
    # Copy executable to MSI
    print("  Adding files to MSI...")
    cab_name = msilib.cab_name()
    msilib.make_cab(cab_name, [str(exe_path)], "PrismTrackAgent.exe")
    
    # Add cab to database
    msilib.add_file(db, "PrismTrackAgent.exe", cab_name, "AgentExe")
    
    # Generate sequences
    print("  Generating installation sequences...")
    msilib.generate_sequences(db)
    
    # Commit database
    db.Commit()
    db.Close()
    
    print(f"\nMSI installer created successfully!")
    print(f"  Location: {msi_path}")
    print(f"  Size: {msi_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return True

if __name__ == "__main__":
    try:
        success = create_msi()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error creating MSI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

