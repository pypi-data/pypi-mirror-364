"""
Directory setup CLI for HexaEight MCP Client
"""

import os
import shutil
from typing import List
from .utils import (
    find_license_directory, 
    create_hardlink, 
    print_section, 
    confirm_action,
    save_package_state,
    load_package_state
)

class DirectorySetupCLI:
    """CLI for setting up project directory with license hardlinks"""
    
    def run(self, directory_name: str) -> None:
        """Create directory with hardlinks to license files"""
        
        print_section(
            f"Create Directory: {directory_name}",
            "Setting up project directory with HexaEight license hardlinks..."
        )
        
        # Check if directory already exists
        if os.path.exists(directory_name):
            if not confirm_action(f"Directory '{directory_name}' already exists. Continue?"):
                print("👋 Directory setup cancelled")
                return
        
        # Find license directory
        license_dir = self._find_license_directory()
        if not license_dir:
            print("❌ Could not find hexaeight.mac license file")
            print("💡 Please run 'hexaeight-start license-activation' first")
            return
        
        print(f"📁 Found license directory: {license_dir}")
        
        try:
            # Create project directory
            os.makedirs(directory_name, exist_ok=True)
            print(f"✅ Created directory: {directory_name}")
            
            # Create hardlinks to license files
            self._create_license_links(license_dir, directory_name)
            
            # Save project info
            project_path = os.path.abspath(directory_name)
            self._save_project_info(project_path, license_dir)
            
            print_section("✅ Directory Setup Complete")
            print(f"📁 Project directory: {project_path}")
            print(f"🔗 License hardlinks created successfully")
            print(f"")
            print(f"🎯 Next Steps:")
            print(f"1. Change to your project directory:")
            print(f"   cd {directory_name}")
            print(f"")
            print(f"2. Generate agent configuration files:")
            print(f"   hexaeight-start generate-parent-or-child-agent-licenses")
            print(f"")
            print(f"3. Deploy sample multi-agent system:")
            print(f"   hexaeight-deploy multi-ai-agent-samples")
            
        except Exception as e:
            print(f"❌ Directory setup failed: {e}")
            # Cleanup on failure
            if os.path.exists(directory_name) and len(os.listdir(directory_name)) == 0:
                os.rmdir(directory_name)
            raise
    
    def _find_license_directory(self) -> str:
        """Find license directory using multiple strategies"""
        
        # Strategy 1: Check package state
        state = load_package_state()
        saved_license_dir = state.get("license_directory")
        if saved_license_dir and os.path.exists(os.path.join(saved_license_dir, "hexaeight.mac")):
            return saved_license_dir
        
        # Strategy 2: Use utility function
        license_dir = find_license_directory()
        if license_dir:
            return license_dir
        
        # Strategy 3: Ask user
        print("🔍 License directory not found automatically.")
        custom_path = input("Enter path to directory containing hexaeight.mac file (or press Enter to cancel): ").strip()
        
        if custom_path and os.path.exists(os.path.join(custom_path, "hexaeight.mac")):
            # Save for future use
            save_package_state("license_directory", custom_path)
            return custom_path
        
        return None
    
    def _create_license_links(self, license_dir: str, project_dir: str) -> None:
        """Create hardlinks to license files"""
        
        license_files = ["hexaeight.mac"]
        optional_files = ["env-file", "libe_sqlite3.so"]
        
        # Required files
        for filename in license_files:
            source = os.path.join(license_dir, filename)
            destination = os.path.join(project_dir, filename)
            
            if os.path.exists(source):
                if os.path.exists(destination):
                    os.remove(destination)
                
                success = create_hardlink(source, destination)
                if success:
                    print(f"🔗 Hardlinked: {filename}")
                else:
                    print(f"📄 Copied: {filename}")
            else:
                raise Exception(f"Required license file not found: {filename}")
        
        # Optional files
        for filename in optional_files:
            source = os.path.join(license_dir, filename)
            destination = os.path.join(project_dir, filename)
            
            if os.path.exists(source):
                if os.path.exists(destination):
                    os.remove(destination)
                
                try:
                    create_hardlink(source, destination)
                    print(f"🔗 Hardlinked: {filename}")
                except Exception as e:
                    print(f"⚠️  Could not link {filename}: {e}")
            else:
                print(f"ℹ️  Optional file not found: {filename}")
    
    def _save_project_info(self, project_path: str, license_dir: str) -> None:
        """Save project information"""
        
        # Save in package state
        state = load_package_state()
        if "projects" not in state:
            state["projects"] = []
        
        project_info = {
            "path": project_path,
            "license_directory": license_dir,
            "created": str(os.path.getctime(project_path))
        }
        
        # Remove existing entry for this path
        state["projects"] = [p for p in state["projects"] if p.get("path") != project_path]
        state["projects"].append(project_info)
        
        save_package_state("projects", state["projects"])
        
        # Create project-local info file
        project_info_file = os.path.join(project_path, ".hexaeight-project")
        with open(project_info_file, 'w') as f:
            f.write(f"# HexaEight MCP Client Project\n")
            f.write(f"LICENSE_DIRECTORY={license_dir}\n")
            f.write(f"PROJECT_PATH={project_path}\n")
        
        print(f"💾 Project info saved")
