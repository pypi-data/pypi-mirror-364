# -*- coding: utf-8 -*-
"""Git Commit分析工具模块

该模块提供了一个GitCommitAnalyzer类，用于获取和分析指定Git commit的详细信息，
包括提交信息、修改内容以及详细的功能、原因和逻辑分析。
"""

import os
import re
import subprocess
from typing import Any, Dict

from jarvis.jarvis_agent import Agent
from jarvis.jarvis_platform.registry import PlatformRegistry
from jarvis.jarvis_tools.registry import ToolRegistry
from jarvis.jarvis_utils.output import OutputType, PrettyOutput
from jarvis.jarvis_utils.tag import ct, ot
from jarvis.jarvis_utils.utils import init_env


class GitCommitAnalyzer:
    """Git Commit分析器

    该类用于获取和分析指定Git commit的详细信息，包括：
    - 完整的提交信息
    - 修改的文件列表和状态
    - 修改的功能、原因和逻辑分析
    """

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行commit分析

        Args:
            args: 包含commit_sha/commit_range和root_dir的参数字典
                commit_sha: 单个commit的SHA
                commit_range: 两个commit的SHA范围，格式为"commit1..commit2"
                root_dir: 代码库根目录

        Returns:
            包含分析结果的字典
        """
        try:
            commit_sha = args.get("commit_sha")
            commit_range = args.get("commit_range")
            root_dir = args.get("root_dir", ".")

            if commit_range:
                return self.analyze_commit_range(commit_range, root_dir)
            elif commit_sha:
                return self.analyze_single_commit(commit_sha, root_dir)
            else:
                raise ValueError("Either commit_sha or commit_range must be provided")
        except Exception as e:
            return {
                "success": False,
                "stdout": {},
                "stderr": f"Failed to analyze commit: {str(e)}",
            }

    def analyze_single_commit(self, commit_sha: str, root_dir: str) -> Dict[str, Any]:
        """分析单个commit

        Args:
            commit_sha: commit的SHA
            root_dir: 代码库根目录

        Returns:
            包含分析结果的字典
        """
        original_dir = os.getcwd()
        try:
            os.chdir(root_dir)

            # 获取commit详细信息
            commit_info = subprocess.check_output(
                f"git show {commit_sha} --pretty=fuller", shell=True, text=True
            )

            # 获取commit修改内容
            diff_content = subprocess.check_output(
                f"git show {commit_sha} --patch", shell=True, text=True
            )

            # 分析commit的功能、原因和逻辑
            analysis_result = self._analyze_diff_content(diff_content)

            return {
                "success": True,
                "stdout": {
                    "commit_info": commit_info,
                    "diff_content": diff_content,
                    "analysis_result": analysis_result,
                },
                "stderr": "",
            }
        except subprocess.CalledProcessError as error:
            return {
                "success": False,
                "stdout": {},
                "stderr": f"Failed to analyze commit: {str(error)}",
            }
        finally:
            os.chdir(original_dir)

    def analyze_commit_range(self, commit_range: str, root_dir: str) -> Dict[str, Any]:
        """分析两个commit之间的代码变更

        Args:
            commit_range: 两个commit的SHA范围，格式为"commit1..commit2"
            root_dir: 代码库根目录

        Returns:
            包含分析结果的字典
        """
        original_dir = os.getcwd()
        try:
            os.chdir(root_dir)

            # 获取commit范围差异
            diff_content = subprocess.check_output(
                f"git diff {commit_range} --patch", shell=True, text=True
            )

            # 获取commit范围信息
            commit_info = subprocess.check_output(
                f"git log {commit_range} --pretty=fuller", shell=True, text=True
            )

            # 使用相同的分析方法处理差异内容
            analysis_result = self._analyze_diff_content(diff_content)

            return {
                "success": True,
                "stdout": {
                    "commit_info": commit_info,
                    "diff_content": diff_content,
                    "analysis_result": analysis_result,
                },
                "stderr": "",
            }
        except subprocess.CalledProcessError as error:
            return {
                "success": False,
                "stdout": {},
                "stderr": f"Failed to analyze commit range: {str(error)}",
            }
        finally:
            os.chdir(original_dir)

    def _analyze_diff_content(self, diff_content: str) -> str:
        """分析diff内容并生成报告

        Args:
            diff_content: git diff或git show的输出内容

        Returns:
            分析结果字符串
        """
        system_prompt = """你是一位资深代码分析专家，拥有多年代码审查和重构经验。你需要对Git commit进行深入分析，包括：
1. 修改的功能：明确说明本次commit实现或修改了哪些功能
2. 修改的原因：分析为什么要进行这些修改（如修复bug、优化性能、添加新功能等）
3. 修改的逻辑：详细说明代码修改的具体实现逻辑和思路
4. 影响范围：评估本次修改可能影响的其他模块或功能
5. 代码质量：分析代码风格、可读性和可维护性
6. 测试覆盖：评估是否需要添加或修改测试用例
7. 最佳实践：检查代码是否符合行业最佳实践和项目规范

请确保分析内容：
- 准确反映commit的实际修改
- 提供足够的技术细节
- 保持结构清晰，便于理解
- 重点关注关键修改和潜在风险"""

        tool_registry = ToolRegistry()
        agent = Agent(
            system_prompt=system_prompt,
            name="Commit Analysis Agent",
            summary_prompt=f"""请生成一份详细的commit分析报告，包含以下内容：
{ot("REPORT")}
# 功能分析
[说明本次commit实现或修改了哪些功能]

# 修改原因
[分析进行这些修改的原因，如修复bug、优化性能、添加新功能等]

# 实现逻辑
[详细说明代码修改的具体实现逻辑和思路]

# 影响范围
[评估本次修改可能影响的其他模块或功能]

# 代码质量
[分析代码风格、可读性和可维护性]

# 测试覆盖
[评估是否需要添加或修改测试用例]

# 最佳实践
[检查代码是否符合行业最佳实践和项目规范]
{ct("REPORT")}""",
            output_handler=[tool_registry],
            llm_type="normal",
            auto_complete=True,
        )

        return agent.run(diff_content)


def extract_analysis_report(result: str) -> str:
    """从分析结果中提取报告内容

    Args:
        result: 包含REPORT标签的完整分析结果字符串

    Returns:
        提取的报告内容，如果未找到REPORT标签则返回空字符串
    """
    search_match = re.search(
        ot("REPORT") + r"\n(.*?)\n" + ct("REPORT"), result, re.DOTALL
    )
    if search_match:
        return search_match.group(1)
    return result


def main():
    """主函数，用于命令行接口"""
    import argparse

    init_env("欢迎使用 Jarvis-GitCommitAnalyzer，您的Git Commit分析助手已准备就绪！")

    parser = argparse.ArgumentParser(description="Git Commit Analyzer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("commit", nargs="?", help="Commit SHA to analyze")
    group.add_argument(
        "--range", type=str, help="Commit range to analyze (commit1..commit2)"
    )
    parser.add_argument(
        "--root-dir", type=str, help="Root directory of the codebase", default="."
    )

    args = parser.parse_args()

    analyzer = GitCommitAnalyzer()
    if args.range:
        result = analyzer.execute(
            {"commit_range": args.range, "root_dir": args.root_dir}
        )
    else:
        result = analyzer.execute(
            {"commit_sha": args.commit, "root_dir": args.root_dir}
        )

    if result["success"]:
        PrettyOutput.section("Commit Information:", OutputType.SUCCESS)
        PrettyOutput.print(result["stdout"]["commit_info"], OutputType.CODE)
        PrettyOutput.section("Analysis Report:", OutputType.SUCCESS)
        report = extract_analysis_report(result["stdout"]["analysis_result"])
        PrettyOutput.print(report, OutputType.SUCCESS, lang="markdown")
    else:
        PrettyOutput.print(result["stderr"], OutputType.WARNING)


if __name__ == "__main__":
    main()
