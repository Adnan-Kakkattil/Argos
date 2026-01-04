"""
Agent Update Checker and Auto-Updater
Handles automatic version checking and updating
"""
import requests
import zipfile
import shutil
import sys
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict
import subprocess

class UpdateChecker:
    """Handles agent version checking and automatic updates"""
    
    def __init__(self, api_base: str, agent_token: str, current_version: Optional[str] = None):
        self.api_base = api_base
        self.agent_token = agent_token
        self.current_version = current_version or "1.0.0"  # Default version
        self.headers = {
            'X-Agent-Token': agent_token,
            'Content-Type': 'application/json'
        }
    
    def check_for_updates(self) -> Optional[Dict]:
        """
        Check if a new version is available
        
        Returns:
            Dict with update info if available, None otherwise
        """
        url = f"{self.api_base}/version/agent/check-update"
        
        params = {
            "current_version": self.current_version
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('update_available'):
                return data
            return None
            
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None
    
    def download_update(self, download_url: str, file_hash: Optional[str] = None) -> Optional[Path]:
        """
        Download the update zip file
        
        Args:
            download_url: URL to download the update
            file_hash: Expected SHA-256 hash of the file
            
        Returns:
            Path to downloaded file, or None if failed
        """
        # Make download_url absolute if relative
        if download_url.startswith('/'):
            # Relative URL - prepend API base
            base_url = self.api_base.rsplit('/api/v1', 1)[0]
            download_url = f"{base_url}{download_url}"
        
        try:
            print(f"Downloading update from {download_url}...")
            response = requests.get(
                download_url,
                headers=self.headers,
                timeout=300,  # 5 minutes for large files
                stream=True
            )
            response.raise_for_status()
            
            # Save to temp directory
            temp_dir = Path(__file__).parent / "temp_updates"
            temp_dir.mkdir(exist_ok=True)
            
            zip_path = temp_dir / "update.zip"
            
            # Download file
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file hash if provided
            if file_hash:
                calculated_hash = self._calculate_file_hash(zip_path)
                if calculated_hash != file_hash:
                    print(f"ERROR: File hash mismatch. Expected {file_hash}, got {calculated_hash}")
                    zip_path.unlink()
                    return None
                print("File hash verified successfully")
            
            print(f"Update downloaded successfully: {zip_path}")
            return zip_path
            
        except Exception as e:
            print(f"Error downloading update: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def apply_update(self, zip_path: Path) -> bool:
        """
        Extract and apply the update
        
        Args:
            zip_path: Path to the update zip file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            agent_dir = Path(__file__).parent
            backup_dir = agent_dir / "backup"
            extract_dir = agent_dir / "temp_extract"
            
            # Create backup of current version
            print("Creating backup of current version...")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            backup_dir.mkdir()
            
            # Backup important files
            files_to_backup = ['config.json', 'PrismTrackAgent.exe']
            for file_name in files_to_backup:
                file_path = agent_dir / file_name
                if file_path.exists():
                    shutil.copy2(file_path, backup_dir / file_name)
            
            # Extract update
            print("Extracting update...")
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Copy new files (preserve config.json)
            print("Applying update...")
            config_backup = None
            if (agent_dir / "config.json").exists():
                config_backup = (agent_dir / "config.json").read_text()
            
            # Copy all files from extract_dir to agent_dir
            for item in extract_dir.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(extract_dir)
                    target_path = agent_dir / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
            
            # Restore config.json
            if config_backup:
                (agent_dir / "config.json").write_text(config_backup)
            
            # Clean up
            print("Cleaning up...")
            shutil.rmtree(extract_dir)
            zip_path.unlink()
            
            print("Update applied successfully!")
            return True
            
        except Exception as e:
            print(f"Error applying update: {e}")
            # Try to restore from backup
            self._restore_backup(agent_dir, backup_dir)
            return False
    
    def _restore_backup(self, agent_dir: Path, backup_dir: Path):
        """Restore files from backup"""
        try:
            if backup_dir.exists():
                print("Restoring from backup...")
                for file_name in backup_dir.iterdir():
                    if file_name.is_file():
                        shutil.copy2(file_name, agent_dir / file_name.name)
                print("Backup restored")
        except Exception as e:
            print(f"Error restoring backup: {e}")
    
    def restart_agent(self):
        """Restart the agent after update"""
        try:
            print("Restarting agent...")
            # Get current executable path
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = sys.executable
                script_path = Path(__file__).parent / "main.py"
                exe_path = f'"{sys.executable}" "{script_path}"'
            
            # Start new process
            agent_dir = Path(__file__).parent
            if getattr(sys, 'frozen', False):
                # Running as executable
                subprocess.Popen([exe_path], cwd=agent_dir, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # Running as script
                subprocess.Popen(exe_path, cwd=agent_dir, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            # Exit current process
            sys.exit(0)
            
        except Exception as e:
            print(f"Error restarting agent: {e}")

