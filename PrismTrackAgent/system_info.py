"""
System Information Collection for PrismTrack Agent
"""
import winreg
import os
import subprocess
import socket
import sys
from typing import Optional

class SystemInfo:
    """Collects system information from Windows machine"""
    
    def __init__(self, hardware_uuid: str, machine_name: str, 
                 username: str, hostname: str, upn_email: Optional[str]):
        self.hardware_uuid = hardware_uuid
        self.machine_name = machine_name
        self.username = username
        self.hostname = hostname
        self.upn_email = upn_email
    
    @staticmethod
    def collect():
        """Collect all system information"""
        print("Collecting system information...")
        
        # Get Hardware UUID from registry
        hardware_uuid = SystemInfo.get_hardware_uuid()
        print(f"  Hardware UUID: {hardware_uuid}")
        
        # Get machine name
        machine_name = os.environ.get('COMPUTERNAME', socket.gethostname())
        print(f"  Machine Name: {machine_name}")
        
        # Get username (whoami)
        username = SystemInfo.get_username()
        print(f"  Username: {username}")
        
        # Get hostname
        hostname = socket.getfqdn()
        print(f"  Hostname: {hostname}")
        
        # Get UPN email (try AD first, then local)
        upn_email = SystemInfo.get_upn_email(username, hostname)
        print(f"  UPN Email: {upn_email}")
        
        return SystemInfo(hardware_uuid, machine_name, username, hostname, upn_email)
    
    @staticmethod
    def get_hardware_uuid():
        """Get Machine GUID from Windows registry"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography"
            )
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return guid
        except Exception as e:
            print(f"Error getting hardware UUID: {e}")
            # Fallback: generate a UUID based on machine name
            import hashlib
            machine_name = os.environ.get('COMPUTERNAME', 'unknown')
            return hashlib.md5(machine_name.encode()).hexdigest()
    
    @staticmethod
    def get_username():
        """Get current username (whoami)"""
        try:
            # Try whoami command first
            result = subprocess.run(
                ['whoami'], 
                capture_output=True, 
                text=True, 
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"Error running whoami: {e}")
        
        # Fallback to environment variable
        username = os.environ.get('USERNAME', 'unknown')
        domain = os.environ.get('USERDOMAIN', '')
        
        if domain:
            return f"{domain}\\{username}"
        return username
    
    @staticmethod
    def get_upn_email(username: str, hostname: str):
        """Get UPN email (try AD, fallback to local)"""
        # Extract username without domain
        clean_username = username.split('\\')[-1] if '\\' in username else username
        
        # Try to get from Active Directory
        try:
            ps_command = f'''
            try {{
                $user = Get-ADUser -Identity "{clean_username}" -Properties UserPrincipalName -ErrorAction SilentlyContinue
                if ($user -and $user.UserPrincipalName) {{
                    Write-Output $user.UserPrincipalName
                }}
            }} catch {{
                Write-Output ""
            }}
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0 and result.stdout.strip():
                email = result.stdout.strip()
                if email and '@' in email:
                    return email
        except Exception as e:
            print(f"Error getting UPN from AD: {e}")
        
        # Fallback: construct email from username and hostname
        return f"{clean_username}@{hostname}"

