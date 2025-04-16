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
import tempfile


def main():
    print("Auto Commit Start...")
    config = load_config()
    valid_repos = check_repositories(config)

    if not valid_repos:
        print("No valid repo, check config.json")
        return

    for repo_path in valid_repos:
        git_status_results = git_status(repo_path)
        for result in git_status_results:
            if result[0] == "M ":
                # File is modified and staged (changes added to the index)
                if result[1].endswith('.py'):
                    process_python_files(repo_path, result[1])
                pass
            elif result[0] == " M":
                # File is modified but not staged (changes in working directory only)
                pass
            elif result[0] == "MM":
                # File is modified, some changes are staged and others are not staged
                if result[1].endswith('.py'):
                    process_python_files(repo_path, result[1])
                pass
            elif result[0] == "A ":
                # New file added to staging area
                pass
            elif result[0] == "R ":
                # File has been renamed in the staging area
                pass
            elif result[0] == "D ":
                # File is deleted in staging area
                pass
            elif result[0] == "C ":
                # File has been copied in staging area
                pass
            elif result[0] == "??":
                # Untracked file (not under version control yet)
                pass
            elif result[0] == "UU":
                # File has merge conflicts (both modified during merge)
                pass



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


def git_status(repo_path):
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        result = result.stdout.strip().split('\n')
        result = [[r[:2], r[3:]] for r in result]
        return result
    except subprocess.SubprocessError as e:
        print(f"Error in has_uncommitted_changes: {e}")
        return None


def git_add(repo_path, file_path):
    try:
        subprocess.run(
            ["git", "-C", repo_path, "add", file_path],
            check=True
        )
        print(f"Added to staging: {file_path}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_add: {e}")
        return False


def git_commit(repo_path, file_path, message):
    try:
        if file_path:
            subprocess.run(
                ["git", "-C", repo_path, "commit", "--only", file_path, "-m", message],
                check=True
            )
        else:
            subprocess.run(
                ["git", "-C", repo_path, "commit", "-m", message],
                check=True
            )
            print(f"Committed with message: {message}")
            return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_commit: {e}")
        return False


def git_diff_staged(repo_path, file_path):
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--staged", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.SubprocessError as e:
        print(f"Error in git_diff_cached: {e}")
        return None


def git_add_patch(repo_path, patch_content):
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(patch_content)
            temp_path = temp_file.name

        subprocess.run(
            ["git", "-C", repo_path, "apply", "--staged", temp_path],
            check=True
        )

        os.unlink(temp_path)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_add_patch: {e}")
        return False


def process_python_files(repo_path, python_files):
    full_diff = git_diff_staged(repo_path, python_files)
    for t in full_diff.split("@@"):
        print(t)



if __name__ == "__main__":
    main()