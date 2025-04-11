#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""

import os
import random
import time
import datetime
import subprocess
import json
import logging
from pathlib import Path
import schedule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("auto_commit.log"), logging.StreamHandler()]
)
logger = logging.getLogger("auto_commit")


class AutoCommitSystem:
    def __init__(self, config_path="config.json"):
        """初始化自动提交系统"""
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        """从配置文件加载设置"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                logger.info(f"配置文件已加载: {self.config_path}")
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_path}")
            # 创建默认配置
            self.config = {
                "repositories": [],
                "work_hours": {
                    "start": "09:00",
                    "end": "18:00"
                },
                "commit_frequency": {
                    "min_per_day": 3,
                    "max_per_day": 8
                },
                "line_changes": {
                    "min_lines": 5,
                    "max_lines": 50
                },
                "file_extensions": [".py", ".js", ".html", ".css", ".md"]
            }
            self.save_config()

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
            logger.info(f"配置已保存到: {self.config_path}")

    def add_repository(self, repo_path):
        """添加要监控的仓库"""
        repo_path = os.path.abspath(repo_path)
        if not os.path.exists(os.path.join(repo_path, ".git")):
            logger.error(f"无效的Git仓库: {repo_path}")
            return False

        if repo_path not in self.config["repositories"]:
            self.config["repositories"].append(repo_path)
            self.save_config()
            logger.info(f"已添加仓库: {repo_path}")
            return True
        return False

    def remove_repository(self, repo_path):
        """移除监控的仓库"""
        repo_path = os.path.abspath(repo_path)
        if repo_path in self.config["repositories"]:
            self.config["repositories"].remove(repo_path)
            self.save_config()
            logger.info(f"已移除仓库: {repo_path}")
            return True
        return False

    def is_work_hour(self):
        """检查当前是否在工作时间内"""
        now = datetime.datetime.now().time()
        start_time = datetime.datetime.strptime(self.config["work_hours"]["start"], "%H:%M").time()
        end_time = datetime.datetime.strptime(self.config["work_hours"]["end"], "%H:%M").time()

        return start_time <= now <= end_time

    def get_random_files(self, repo_path, num_files=1):
        """从仓库中随机选择几个文件"""
        valid_files = []
        for ext in self.config["file_extensions"]:
            # 使用git ls-files确保只选择已被git跟踪的文件
            cmd = ["git", "-C", repo_path, "ls-files", f"*{ext}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            files = result.stdout.strip().split("\n")
            valid_files.extend([os.path.join(repo_path, f) for f in files if f])

        if not valid_files:
            logger.warning(f"仓库中没有找到符合条件的文件: {repo_path}")
            return []

        # 随机选择文件
        num_files = min(num_files, len(valid_files))
        return random.sample(valid_files, num_files)

    def generate_commit_message(self):
        """生成随机的commit消息"""
        prefixes = [
            "Fix", "Update", "Refactor", "Improve", "Optimize",
            "Add", "Remove", "Modify", "Enhance", "Clean up"
        ]

        components = [
            "documentation", "code style", "performance", "UI", "functionality",
            "tests", "comments", "error handling", "dependencies", "configuration"
        ]

        details = [
            "for better readability", "to follow best practices",
            "to address feedback", "based on code review",
            "to fix edge cases", "for maintainability",
            "to reduce complexity", "to improve efficiency",
            "to meet new requirements", "for consistency"
        ]

        prefix = random.choice(prefixes)
        component = random.choice(components)
        detail = random.choice(details)

        return f"{prefix} {component} {detail}"

    def modify_file_content(self, file_path):
        """修改文件内容，增加或减少行数"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 备份原始内容，以防出错
            with open(f"{file_path}.bak", 'w', encoding='utf-8') as f:
                f.writelines(lines)

            # 决定是增加还是减少行数
            action = random.choice(['add', 'remove', 'modify'])
            min_lines = self.config["line_changes"]["min_lines"]
            max_lines = self.config["line_changes"]["max_lines"]
            num_changes = random.randint(min_lines, max_lines)

            if action == 'add':
                # 在随机位置添加注释或空行
                for _ in range(num_changes):
                    pos = random.randint(0, len(lines))
                    comment = f"# Auto-generated comment: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    lines.insert(pos, comment)

            elif action == 'remove' and len(lines) > num_changes * 2:
                # 随机删除一些行，但不要删除太多
                for _ in range(min(num_changes, len(lines) // 3)):
                    pos = random.randint(0, len(lines) - 1)
                    del lines[pos]

            else:  # modify
                # 修改一些行的内容
                for _ in range(min(num_changes, len(lines))):
                    pos = random.randint(0, len(lines) - 1)
                    lines[
                        pos] = f"# Modified: {lines[pos].strip()} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            logger.info(f"已修改文件: {file_path} ({action} {num_changes} lines)")
            return True

        except Exception as e:
            logger.error(f"修改文件失败: {file_path}, 错误: {str(e)}")
            # 恢复备份
            try:
                if os.path.exists(f"{file_path}.bak"):
                    os.replace(f"{file_path}.bak", file_path)
            except Exception:
                pass
            return False

    def commit_changes(self, repo_path):
        """提交更改到Git仓库"""
        try:
            # 获取随机文件
            num_files = random.randint(1, 3)
            files = self.get_random_files(repo_path, num_files)

            if not files:
                logger.warning(f"没有找到可修改的文件: {repo_path}")
                return False

            # 修改文件
            modified_files = []
            for file_path in files:
                if self.modify_file_content(file_path):
                    modified_files.append(file_path)

            if not modified_files:
                logger.warning("没有成功修改任何文件")
                return False

            # 生成commit消息
            commit_message = self.generate_commit_message()

            # 添加修改的文件
            for file_path in modified_files:
                subprocess.run(["git", "-C", repo_path, "add", file_path])

            # 提交更改
            subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_message])

            # 清理备份文件
            for file_path in modified_files:
                backup = f"{file_path}.bak"
                if os.path.exists(backup):
                    os.remove(backup)

            logger.info(f"成功提交更改: {repo_path}, 消息: '{commit_message}', 修改了 {len(modified_files)} 个文件")
            return True

        except Exception as e:
            logger.error(f"提交更改失败: {repo_path}, 错误: {str(e)}")
            return False

    def schedule_commits(self):
        """为今天安排随机时间的提交"""
        if not self.config["repositories"]:
            logger.warning("没有配置任何仓库，无法安排提交")
            return

        # 清除之前的计划
        schedule.clear()

        # 获取今天的工作时间范围
        now = datetime.datetime.now()
        start_time = datetime.datetime.strptime(self.config["work_hours"]["start"], "%H:%M").time()
        end_time = datetime.datetime.strptime(self.config["work_hours"]["end"], "%H:%M").time()

        start_datetime = datetime.datetime.combine(now.date(), start_time)
        end_datetime = datetime.datetime.combine(now.date(), end_time)

        # 如果当前时间已经超过今天的结束时间，则不安排任何提交
        if now.time() > end_time:
            logger.info("今天的工作时间已结束，不安排新的提交")
            return

        # 如果当前时间早于开始时间，则从开始时间开始安排
        start_from = max(now, start_datetime)

        # 决定今天要进行多少次提交
        min_commits = self.config["commit_frequency"]["min_per_day"]
        max_commits = self.config["commit_frequency"]["max_per_day"]
        num_commits = random.randint(min_commits, max_commits)

        # 计算可用的时间范围（秒）
        available_seconds = (end_datetime - start_from).total_seconds()

        if available_seconds <= 0:
            logger.warning("今天没有足够的工作时间来安排提交")
            return

        # 随机选择提交时间点
        for _ in range(num_commits):
            # 随机选择一个仓库
            repo_path = random.choice(self.config["repositories"])

            # 随机选择一个时间点
            offset_seconds = random.randint(0, int(available_seconds))
            commit_time = start_from + datetime.timedelta(seconds=offset_seconds)

            # 安排任务
            logger.info(f"计划在 {commit_time.strftime('%H:%M:%S')} 对仓库 {repo_path} 进行提交")

            # 使用schedule库在指定时间执行提交
            schedule.every().day.at(commit_time.strftime("%H:%M:%S")).do(self.commit_changes, repo_path=repo_path)

    def run(self):
        """运行自动提交系统"""
        logger.info("启动自动提交系统")

        # 每天早上安排当天的提交
        schedule.every().day.at(self.config["work_hours"]["start"]).do(self.schedule_commits)

        # 如果是当天启动，立即安排今天的提交
        if self.is_work_hour():
            self.schedule_commits()

        # 主循环
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("用户中断，停止自动提交系统")
                break
            except Exception as e:
                logger.error(f"运行出错: {str(e)}")
                time.sleep(60)  # 出错后等待一分钟再继续


def main():
    """主函数"""
    auto_commit = AutoCommitSystem()

    # 命令行参数处理可以在这里添加

    auto_commit.run()


if __name__ == "__main__":
    main()