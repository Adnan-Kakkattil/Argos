"""
PrismTrack Agent - Main Application
Tracks employee productivity and sends data to PrismTrack backend
"""
import asyncio
import sys
import os
from datetime import datetime
from config import Config
from system_info import SystemInfo
from registration import register_agent
from tracking import ProductivityTracker
from api_client import ApiClient
from update_checker import UpdateChecker

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("PrismTrack Agent")
    print("Employee Productivity Tracking")
    print("=" * 60)
    print()

async def main():
    """Main application entry point"""
    print_banner()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = Config.load()
        
        if not config.org_id:
            print("ERROR: org_id not found in config.json")
            print("Please ensure config.json contains a valid org_id")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print(f"  Org ID: {config.org_id}")
        print(f"  API Base: {config.api_base}")
        print()
        
        # Collect system information
        print("Collecting system information...")
        system_info = SystemInfo.collect()
        print()
        
        # Register agent if not already registered
        if not config.agent_token:
            print("Agent not registered. Registering with backend...")
            try:
                agent_token = register_agent(
                    api_base=config.api_base,
                    org_id=config.org_id,
                    system_info=system_info
                )
                config.agent_token = agent_token
                config.save()
                print("Agent registered successfully!")
                print()
            except Exception as e:
                print(f"ERROR: Failed to register agent: {e}")
                print("Please check your network connection and API endpoint")
                input("Press Enter to exit...")
                sys.exit(1)
        else:
            print("Using existing agent token")
            print()
        
        # Initialize API client
        api_client = ApiClient(config.api_base, config.agent_token)
        
        # Start productivity tracker
        print("Starting productivity tracking...")
        print(f"  Heartbeat interval: {config.heartbeat_interval} seconds")
        print(f"  Telemetry interval: {config.telemetry_interval} seconds")
        print(f"  Idle threshold: {config.idle_threshold_seconds} seconds")
        print()
        print("Agent is now running. Press Ctrl+C to stop.")
        print("-" * 60)
        print()
        
        tracker = ProductivityTracker(
            api_client, 
            system_info,
            idle_threshold_seconds=config.idle_threshold_seconds
        )
        
        # Initialize update checker
        update_checker = UpdateChecker(
            api_base=config.api_base,
            agent_token=config.agent_token,
            current_version=config.current_version
        )
        update_check_counter = 0
        
        # Main loop
        heartbeat_counter = 0
        telemetry_counter = 0
        
        while True:
            try:
                # Send heartbeat periodically
                heartbeat_counter += 1
                if heartbeat_counter >= (config.heartbeat_interval // 5):  # Check every 5 seconds
                    api_client.heartbeat()
                    heartbeat_counter = 0
                
                # Collect and send telemetry periodically
                telemetry_counter += 1
                if telemetry_counter >= (config.telemetry_interval // 5):  # Check every 5 seconds
                    tracker.collect_and_send()
                    telemetry_counter = 0
                
                # Check for updates periodically
                update_check_counter += 1
                if update_check_counter >= (config.update_check_interval // 5):  # Check every 5 seconds
                    try:
                        update_info = update_checker.check_for_updates()
                        if update_info:
                            print(f"\n{'='*60}")
                            print("UPDATE AVAILABLE!")
                            print(f"Current Version: {config.current_version}")
                            print(f"New Version: {update_info['latest_version']}")
                            print(f"Changelog: {update_info.get('changelog', 'N/A')}")
                            print(f"{'='*60}\n")
                            
                            # Download update
                            download_url = update_info['download_url']
                            file_hash = update_info.get('file_hash')
                            
                            zip_path = update_checker.download_update(download_url, file_hash)
                            if zip_path:
                                # Apply update
                                if update_checker.apply_update(zip_path):
                                    # Update config version
                                    config.current_version = update_info['latest_version']
                                    config.save()
                                    
                                    # Restart agent
                                    print("Restarting agent with new version...")
                                    await asyncio.sleep(2)  # Give time for message to display
                                    update_checker.restart_agent()
                    except Exception as e:
                        print(f"Error checking for updates: {e}")
                        # Continue running even if update check fails
                    
                    update_check_counter = 0
                
                # Wait 5 seconds before next iteration
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("\n\nShutting down agent...")
                print("Goodbye!")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                # Continue running despite errors
                await asyncio.sleep(5)
                
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    # Check if running on Windows
    if sys.platform != 'win32':
        print("ERROR: PrismTrack Agent requires Windows")
        sys.exit(1)
    
    # Run main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

