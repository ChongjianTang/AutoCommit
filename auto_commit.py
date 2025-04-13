#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoCommit
"""

import os
import random
import datetime
import subprocess
import json


def main():
    print("Auto Commit Start...")
    config = load_config()
    valid_repos = check_repositories(config)

    if not valid_repos:
        print("No valid repo, check config.json")
        return

    for repo_path in valid_repos:
        has_uncommitted_changes(repo_path)


def load_config(config_path="config.json"):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print("Config loaded")
            return config


    except FileNotFoundError:
        print(f"Config not found: {config_path}")

        default_config = {
            "repositories": [],
            "work_hours": {
                "start": "09:00",
                "end": "18:00"
            },
            "commits_per_day": {
                "min": 3,
                "max": 8
            }
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
            print(f"Create default config: {config_path}")
            return config


def is_valid_git_repo(repo_path):
    git_dir = os.path.join(repo_path, ".git")
    return os.path.exists(git_dir) and os.path.isdir(git_dir)


def check_repositories(config):
    valid_repos = []
    for repo_path in config["repositories"]:
        if is_valid_git_repo(repo_path):
            print(f"Valid git repo: {repo_path}")
            valid_repos.append(repo_path)
        else:
            print(f"Invalid git repo: {repo_path}")

    return valid_repos


def has_uncommitted_changes(repo_path):
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result)
    except subprocess.SubprocessError as e:
        print(f"Error in has_uncommitted_changes: {e}")
        return False


if __name__ == "__main__":
    main()
