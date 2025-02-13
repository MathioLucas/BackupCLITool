#!/usr/bin/env python3
import os
import shutil
from datetime import datetime
import argparse
from pathlib import Path
import json

class BackupTool:
    def __init__(self):
        self.config_file = "backup_config.json"
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"dirs": [], "destination": "", "keep_days": 7}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def add(self, path):
        path = os.path.abspath(path)
        if os.path.exists(path) and path not in self.config["dirs"]:
            self.config["dirs"].append(path)
            self.save_config()
            print(f"Added {path} to backup list")
    
    def set_dest(self, path):
        self.config["destination"] = os.path.abspath(path)
        os.makedirs(self.config["destination"], exist_ok=True)
        self.save_config()
        print(f"Backup destination set to {path}")
    
    def backup(self):
        if not self.config["dirs"] or not self.config["destination"]:
            print("Please configure backup directories and destination first")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        backup_dir = Path(self.config["destination"]) / f"backup_{timestamp}"
        
        for source in self.config["dirs"]:
            if os.path.exists(source):
                dest = backup_dir / os.path.basename(source)
                shutil.copytree(source, dest)
                print(f"Backed up {source}")
        
        self._cleanup()
    
    def _cleanup(self):
        cutoff = (datetime.now() - pd.Timedelta(days=self.config["keep_days"]))
        for item in Path(self.config["destination"]).glob("backup_*"):
            try:
                date = datetime.strptime(item.name[7:], "%Y%m%d_%H%M")
                if date < cutoff:
                    shutil.rmtree(item)
                    print(f"Removed old backup: {item.name}")
            except ValueError:
                continue

def main():
    parser = argparse.ArgumentParser(description="Simple Backup Tool")
    parser.add_argument("command", choices=["add", "dest", "backup", "list"])
    parser.add_argument("path", nargs="?", help="Path for add/dest commands")
    args = parser.parse_args()
    
    tool = BackupTool()
    
    if args.command == "add" and args.path:
        tool.add(args.path)
    elif args.command == "dest" and args.path:
        tool.set_dest(args.path)
    elif args.command == "backup":
        tool.backup()
    elif args.command == "list":
        print("\nBackup dirs:", *tool.config["dirs"], sep="\n- ")
        print(f"\nDestination: {tool.config['destination']}")

if __name__ == "__main__":
    main()
