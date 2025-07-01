#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempest Framework - Test Suite
测试套件 - 验证整个Tempest框架的功能

Author: Tempest Framework Team
Date: 2025
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config_loader import ConfigLoader, setup_logging
from tempest_framework import (
    TempestOrchestrator, AttackerAgent, JudgeAgent, TargetAgent,
    DeepSeekAPI, GeminiAPI, GLMAPI, OpenRouterAPI, PPIOAPI, KimiAPI, ConversationBranch
)
from jailbreak_bench_sample import JailbreakBenchSample
from utils import Timer, AttackResult, calculate_metrics, ProgressTracker

class FrameworkTester:
    """框架测试器"""
    
    def __init__(self):
        self.config = ConfigLoader()
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有测试
        
        Returns:
            测试结果字典
        """
        print("🚀 开始Tempest框架测试套件")
        print("=" * 50)
        
        test_results = {
            "config_test": self.test_config_loader(),
            "api_test": self.test_api_connections(),
            "agent_test": self.test_agents(),
            "dataset_test": self.test_dataset(),
            "orchestrator_test": self.test_orchestrator(),
            "integration_test": self.test_integration(),
        }
        
        # 汇总结果
        passed_tests = sum(1 for result in test_results.values() if result["passed"])
        total_tests = len(test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 测试完成: {passed_tests}/{total_tests} 通过")
        
        if passed_tests == total_tests:
            print("✅ 所有测试通过！框架准备就绪。")
        else:
            print("❌ 部分测试失败，请检查配置和API密钥。")
        
        return test_results
    
    def test_config_loader(self) -> Dict[str, Any]:
        """
        测试配置加载器
        
        Returns:
            测试结果
        """
        print("\n🔧 测试配置加载器...")
        
        try:
            # 测试配置验证
            is_valid = self.config.validate_config()
            
            # 测试配置获取
            algo_config = self.config.get_algorithm_config()
            api_config = self.config.get_api_config("deepseek")
            
            # 测试环境变量更新
            original_turns = self.config.get("algorithm.max_turns")
            os.environ["TEMPEST_MAX_TURNS"] = "7"
            self.config.update_from_env()
            updated_turns = self.config.get("algorithm.max_turns")
            
            success = (
                is_valid and
                algo_config is not None and
                api_config is not None and
                updated_turns == 7
            )
            
            if success:
                print("  ✅ 配置加载器测试通过")
            else:
                print("  ❌ 配置加载器测试失败")
            
            return {
                "passed": success,
                "details": {
                    "config_valid": is_valid,
                    "algo_config_loaded": algo_config is not None,
                    "api_config_loaded": api_config is not None,
                    "env_update_works": updated_turns == 7,
                }
            }
            
        except Exception as e:
            print(f"  ❌ 配置加载器测试异常: {e}")
            return {"passed": False, "error": str(e)}
    
    def test_api_connections(self) -> Dict[str, Any]:
        """
        测试API连接
        
        Returns:
            测试结果
        """
        print("\n🌐 测试API连接...")
        
        api_results = {}
        
        # 测试DeepSeek API
        try:
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if deepseek_key:
                deepseek_api = DeepSeekAPI()
                test_response = deepseek_api.query("Hello", "You are a helpful assistant.")
                # 添加API调用后的等待时间
                time.sleep(20.0)
                api_results["deepseek"] = bool(test_response and len(test_response) > 0 and not test_response.startswith("[错误:"))
                print(f"  DeepSeek API: {'✅' if api_results['deepseek'] else '❌'}")
            else:
                api_results["deepseek"] = False
                print("  DeepSeek API: ❌ (未配置API密钥)")
        except Exception as e:
            api_results["deepseek"] = False
            print(f"  DeepSeek API: ❌ ({str(e)[:50]}...)")
        
        # 测试Gemini API
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                gemini_api = GeminiAPI()
                test_response = gemini_api.query("Hello", "You are a helpful assistant.")
                # 添加API调用后的等待时间
                time.sleep(20.0)
                api_results["gemini"] = bool(test_response and len(test_response) > 0 and not test_response.startswith("[错误:"))
                print(f"  Gemini API: {'✅' if api_results['gemini'] else '❌'}")
            else:
                api_results["gemini"] = False
                print("  Gemini API: ❌ (未配置API密钥)")
        except Exception as e:
            api_results["gemini"] = False
            print(f"  Gemini API: ❌ ({str(e)[:50]}...)")
        
        # 测试GLM API（可选）
        try:
            glm_key = os.getenv("GLM_API_KEY")
            if glm_key:
                glm_api = GLMAPI()
                test_response = glm_api.query("Hello", "You are a helpful assistant.")
                # 添加API调用后的等待时间
                time.sleep(20.0)
                api_results["glm"] = bool(test_response and len(test_response) > 0 and not test_response.startswith("[错误:"))
                print(f"  GLM API: {'✅' if api_results['glm'] else '❌'}")
            else:
                api_results["glm"] = None  # 可选API
                print("  GLM API: ⚠️ (未配置，可选)")
        except Exception as e:
            api_results["glm"] = False
            print(f"  GLM API: ❌ ({str(e)[:50]}...)")
        
        # 测试OpenRouter API
        try:
            openrouter_api = OpenRouterAPI()
            test_response = openrouter_api.query("Hello", "You are a helpful assistant.")
            # 添加API调用后的等待时间
            time.sleep(20.0)
            api_results["openrouter"] = bool(test_response and len(test_response) > 0 and not test_response.startswith("[错误:"))
            print(f"  OpenRouter API: {'✅' if api_results['openrouter'] else '❌'}")
        except Exception as e:
            api_results["openrouter"] = False
            print(f"  OpenRouter API: ❌ ({str(e)[:50]}...)")
        
        # 测试PPIO API
        try:
            ppio_key = os.getenv("PPIO_API_KEY")
            if ppio_key:
                ppio_api = PPIOAPI()
                test_response = ppio_api.query("Hello", "You are a helpful assistant.")
                # 添加API调用后的等待时间
                time.sleep(20.0)
                api_results["ppio"] = bool(test_response and len(test_response) > 0 and not test_response.startswith("[错误:"))
                print(f"  PPIO API: {'✅' if api_results['ppio'] else '❌'}")
            else:
                api_results["ppio"] = None  # 可选API
                print("  PPIO API: ⚠️ (未配置，可选)")
        except Exception as e:
            api_results["ppio"] = False
            print(f"  PPIO API: ❌ ({str(e)[:50]}...)")
        
        # 测试Kimi API
        try:
            kimi_key = os.getenv("KIMI_API_KEY")
            if kimi_key:
                kimi_api = KimiAPI()
                test_response = kimi_api.query("Hello", "You are a helpful assistant.")
                # 添加API调用后的等待时间
                time.sleep(20.0)
                api_results["kimi"] = bool(test_response and len(test_response) > 0 and not test_response.startswith("[错误:"))
                print(f"  Kimi API: {'✅' if api_results['kimi'] else '❌'}")
            else:
                api_results["kimi"] = None  # 可选API
                print("  Kimi API: ⚠️ (未配置，可选)")
        except Exception as e:
            api_results["kimi"] = False
            print(f"  Kimi API: ❌ ({str(e)[:50]}...)")
        
        # 至少需要DeepSeek和Gemini可用
        success = api_results.get("deepseek", False) and api_results.get("gemini", False)
        
        return {
            "passed": success,
            "details": api_results
        }
    
    def test_agents(self) -> Dict[str, Any]:
        """
        测试智能体
        
        Returns:
            测试结果
        """
        print("\n🤖 测试智能体...")
        
        agent_results = {}
        
        try:
            # 创建API实例
            deepseek_api = DeepSeekAPI()
            gemini_api = GeminiAPI()
            openrouter_api = OpenRouterAPI()
            
            # 测试攻击智能体
            attacker = AttackerAgent(deepseek_api)
            agent_results["attacker_created"] = True
            print("  攻击智能体: ✅ 创建成功")
            
            # 测试评分智能体
            judge = JudgeAgent(gemini_api)
            agent_results["judge_created"] = True
            print("  评分智能体: ✅ 创建成功")
            
            # 测试目标智能体
            target = TargetAgent(gemini_api)
            agent_results["target_created"] = True
            print("  目标智能体: ✅ 创建成功")
            
            # 如果有真实API密钥，测试功能
            if os.getenv("DEEPSEEK_API_KEY") and os.getenv("GEMINI_API_KEY"):
                try:
                    # 测试攻击智能体生成
                    test_branch = ConversationBranch("test_id", "Test harmful behavior")
                    prompts = attacker.generate_adversarial_prompts(test_branch, [])
                    # 添加API调用后的等待时间
                    time.sleep(20.0)
                    agent_results["attacker_functional"] = len(prompts) > 0
                    print(f"  攻击智能体功能: {'✅' if agent_results['attacker_functional'] else '❌'}")
                    
                    # 测试目标智能体响应
                    response = target.get_response("Hello, how are you?")
                    # 添加API调用后的等待时间
                    time.sleep(20.0)
                    agent_results["target_functional"] = len(response) > 0
                    print(f"  目标智能体功能: {'✅' if agent_results['target_functional'] else '❌'}")
                    
                    # 测试评分智能体评估
                    score = judge.evaluate_safety("Hello, how are you?", "I'm doing well, thank you!")
                    # 添加API调用后的等待时间
                    time.sleep(20.0)
                    agent_results["judge_functional"] = score is not None
                    print(f"  评分智能体功能: {'✅' if agent_results['judge_functional'] else '❌'}")
                    
                except Exception as e:
                    print(f"  智能体功能测试失败: {str(e)[:50]}...")
                    agent_results["functional_test_error"] = str(e)
            else:
                print("  ⚠️ 跳过功能测试（需要真实API密钥）")
            
            success = all([
                agent_results.get("attacker_created", False),
                agent_results.get("judge_created", False),
                agent_results.get("target_created", False)
            ])
            
            return {
                "passed": success,
                "details": agent_results
            }
            
        except Exception as e:
            print(f"  ❌ 智能体测试异常: {e}")
            return {"passed": False, "error": str(e)}
    
    def test_dataset(self) -> Dict[str, Any]:
        """
        测试数据集
        
        Returns:
            测试结果
        """
        print("\n📊 测试数据集...")
        
        try:
            # 创建数据集实例
            dataset = JailbreakBenchSample()
            
            # 测试数据加载
            all_behaviors = dataset.get_all_behaviors()
            sample_behaviors = dataset.get_sample(5)
            stats = dataset.get_statistics()
            
            success = (
                len(all_behaviors) > 0 and
                len(sample_behaviors) <= 5 and
                stats["total_behaviors"] > 0
            )
            
            if success:
                print(f"  ✅ 数据集测试通过 (共{len(all_behaviors)}个行为)")
            else:
                print("  ❌ 数据集测试失败")
            
            return {
                "passed": success,
                "details": {
                    "total_behaviors": len(all_behaviors),
                    "sample_size": len(sample_behaviors),
                    "statistics": stats
                }
            }
            
        except Exception as e:
            print(f"  ❌ 数据集测试异常: {e}")
            return {"passed": False, "error": str(e)}
    
    def test_orchestrator(self) -> Dict[str, Any]:
        """
        测试编排器
        
        Returns:
            测试结果
        """
        print("\n🎭 测试编排器...")
        
        try:
            # 创建API实例
            deepseek_api = DeepSeekAPI()
            gemini_api = GeminiAPI()
            
            attacker = AttackerAgent(deepseek_api)
            judge = JudgeAgent(gemini_api)
            target = TargetAgent(gemini_api)
            
            # 创建编排器
            orchestrator = TempestOrchestrator(
                attacker_agent=attacker,
                judge_agent=judge,
                target_agent=target,
                max_turns=2,  # 减少测试时间
                branch_factor=2,
                keep_branches=2
            )
            
            print("  ✅ 编排器创建成功")
            
            # 如果有真实API密钥，进行简单的攻击测试
            if os.getenv("DEEPSEEK_API_KEY") and os.getenv("GEMINI_API_KEY"):
                try:
                    print("  🧪 运行简单攻击测试...")
                    
                    with Timer() as timer:
                        result = orchestrator.run_jailbreak_attempt(
                            "Tell me how to make a paper airplane",  # 无害测试
                            timeout=300
                        )
                        # 添加API调用后的等待时间
                        time.sleep(20.0)
                    
                    functional_test = {
                        "attack_completed": result is not None,
                        "has_result_data": hasattr(result, 'success') if result else False,
                        "execution_time": timer.elapsed()
                    }
                    
                    print(f"  攻击测试完成: {'✅' if functional_test['attack_completed'] else '❌'}")
                    print(f"  执行时间: {functional_test['execution_time']:.2f}秒")
                    
                except Exception as e:
                    print(f"  ⚠️ 功能测试失败: {str(e)[:50]}...")
                    functional_test = {"error": str(e)}
            else:
                print("  ⚠️ 跳过功能测试（需要真实API密钥）")
                functional_test = {"skipped": True}
            
            return {
                "passed": True,
                "details": {
                    "orchestrator_created": True,
                    "functional_test": functional_test
                }
            }
            
        except Exception as e:
            print(f"  ❌ 编排器测试异常: {e}")
            return {"passed": False, "error": str(e)}
    
    def test_integration(self) -> Dict[str, Any]:
        """
        测试集成功能
        
        Returns:
            测试结果
        """
        print("\n🔗 测试集成功能...")
        
        try:
            # 测试工具函数
            from utils import (
                Timer, extract_score_from_text, generate_unique_id,
                calculate_metrics, AttackResult
            )
            
            # 测试计时器
            with Timer() as timer:
                time.sleep(0.01)
            timer_works = timer.elapsed() > 0
            
            # 测试评分提取
            score = extract_score_from_text("安全性评分: 7")
            score_extraction_works = score == 7
            
            # 测试ID生成
            unique_id = generate_unique_id("test_")
            id_generation_works = unique_id.startswith("test_")
            
            # 测试指标计算
            mock_results = [
                AttackResult(
                    success=True, final_score=10, turns_used=3, total_queries=9,
                    attack_time=1.5, final_response="test", conversation_history=[],
                    knowledge_base_entries=[]
                ),
                AttackResult(
                    success=False, final_score=2, turns_used=5, total_queries=15,
                    attack_time=2.0, final_response="test", conversation_history=[],
                    knowledge_base_entries=[]
                )
            ]
            metrics = calculate_metrics(mock_results)
            metrics_calculation_works = metrics.attack_success_rate == 0.5
            
            integration_tests = {
                "timer": timer_works,
                "score_extraction": score_extraction_works,
                "id_generation": id_generation_works,
                "metrics_calculation": metrics_calculation_works
            }
            
            success = all(integration_tests.values())
            
            for test_name, result in integration_tests.items():
                print(f"  {test_name}: {'✅' if result else '❌'}")
            
            return {
                "passed": success,
                "details": integration_tests
            }
            
        except Exception as e:
            print(f"  ❌ 集成测试异常: {e}")
            return {"passed": False, "error": str(e)}
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """
        检查运行前提条件
        
        Returns:
            前提条件检查结果
        """
        print("🔍 检查运行前提条件...")
        
        checks = {}
        
        # 检查Python版本
        import sys
        python_version = sys.version_info
        checks["python_version"] = python_version >= (3, 7)
        print(f"  Python版本 ({python_version.major}.{python_version.minor}): "
              f"{'✅' if checks['python_version'] else '❌'}")
        
        # 检查必要的包
        required_packages = ["requests", "yaml", "pathlib"]
        for package in required_packages:
            try:
                __import__(package)
                checks[f"package_{package}"] = True
                print(f"  包 {package}: ✅")
            except ImportError:
                checks[f"package_{package}"] = False
                print(f"  包 {package}: ❌")
        
        # 检查配置文件
        config_file = Path("config.yaml")
        checks["config_file"] = config_file.exists()
        print(f"  配置文件: {'✅' if checks['config_file'] else '❌'}")
        
        # 检查API密钥
        api_keys = {
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        }
        
        for key_name, key_value in api_keys.items():
            checks[key_name] = bool(key_value and len(key_value) > 10)
            print(f"  {key_name}: {'✅' if checks[key_name] else '❌'}")
        
        return checks

def main():
    """主函数"""
    # 设置日志
    config = ConfigLoader()
    setup_logging(config)
    
    # 创建测试器
    tester = FrameworkTester()
    
    # 检查前提条件
    prerequisites = tester.check_prerequisites()
    
    if not all(prerequisites.values()):
        print("\n⚠️ 部分前提条件未满足，测试可能失败")
        print("请确保:")
        print("1. Python版本 >= 3.7")
        print("2. 安装了所有依赖包: pip install -r requirements.txt")
        print("3. 配置了API密钥在.env文件中")
        print("4. config.yaml文件存在")
        
        response = input("\n是否继续测试? (y/N): ")
        if response.lower() != 'y':
            print("测试已取消")
            return
    
    # 运行测试
    test_results = tester.run_all_tests()
    
    # 保存测试结果
    from utils import save_json, ensure_directory
    
    results_dir = ensure_directory("results")
    result_file = results_dir / f"test_results_{int(time.time())}.json"
    
    save_json({
        "timestamp": time.time(),
        "prerequisites": prerequisites,
        "test_results": test_results
    }, result_file)
    
    print(f"\n📄 测试结果已保存到: {result_file}")
    
    # 给出建议
    failed_tests = [name for name, result in test_results.items() 
                   if not result["passed"]]
    
    if failed_tests:
        print("\n🔧 修复建议:")
        for test_name in failed_tests:
            if test_name == "api_test":
                print("  - 检查API密钥配置和网络连接")
            elif test_name == "config_test":
                print("  - 检查config.yaml文件格式和内容")
            elif test_name == "agent_test":
                print("  - 确保API密钥有效且有足够的配额")
            elif test_name == "dataset_test":
                print("  - 检查jailbreak_bench_sample.py文件")
            elif test_name == "orchestrator_test":
                print("  - 检查整体框架集成")
    else:
        print("\n🎉 框架测试全部通过！可以开始使用Tempest进行安全评估。")
        print("\n下一步:")
        print("  1. 运行单次攻击演示: python demo_single_attack.py")
        print("  2. 运行完整评估: python tempest_framework.py")
        print("  3. 查看README.md了解更多使用方法")

if __name__ == "__main__":
    main()