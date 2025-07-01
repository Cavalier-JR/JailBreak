#!/usr/bin/env python3
"""
Tempest Framework - Environment Test
环境测试脚本

这个脚本用于测试所有API的连接情况，确保环境配置正确。
"""

import os
import sys
import time
from dotenv import load_dotenv
from tempest_framework import DeepSeekAPI, GeminiAPI, GLMAPI, OpenRouterAPI, PPIOAPI, KimiAPI

# 加载环境变量
load_dotenv()


def test_api_connection(api_instance, api_name):
    """
    测试单个API的连接
    """
    print(f"\n🔧 测试 {api_name} API连接...")
    print("-" * 40)
    
    try:
        # 检查API密钥
        if not api_instance.api_key:
            print(f"❌ {api_name} API密钥未配置")
            return False
        
        print(f"✅ API密钥已配置")
        print(f"📋 模型名称: {api_instance.get_model_name()}")
        print(f"🌐 API地址: {api_instance.base_url}")
        
        # 发送测试请求
        print(f"📡 发送测试请求...")
        test_prompt = "你好，请简单介绍一下你自己。"
        
        start_time = time.time()
        response = api_instance.query(test_prompt)
        # 添加API调用后的等待时间
        time.sleep(20.0)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response and not response.startswith("[错误:"):
            print(f"✅ 连接成功!")
            print(f"⏱️  响应时间: {response_time:.2f} 秒")
            print(f"📝 响应内容: {response[:100]}{'...' if len(response) > 100 else ''}")
            return True
        else:
            print(f"❌ 连接失败")
            print(f"📝 错误信息: {response}")
            return False
            
    except Exception as e:
        print(f"❌ 连接异常: {str(e)}")
        return False


def check_environment_variables():
    """
    检查环境变量配置
    """
    print("🔍 检查环境变量配置...")
    print("=" * 50)
    
    required_keys = {
        'DEEPSEEK_API_KEY': 'DeepSeek API密钥',
        'GEMINI_API_KEY': 'Gemini API密钥', 
        'GLM_API_KEY': 'GLM API密钥',
        'PPIO_API_KEY': 'PPIO API密钥',
        'KIMI_API_KEY': 'Kimi API密钥'
    }
    
    # OpenRouter使用环境变量配置
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if openrouter_key:
        print(f"✅ OpenRouter API密钥: 已配置 ({openrouter_key[:10]}...)")
    else:
        print("❌ OpenRouter API密钥: 未配置")
    
    missing_keys = []
    configured_keys = []
    
    for key, description in required_keys.items():
        value = os.getenv(key)
        if value:
            configured_keys.append(f"✅ {description}: 已配置 ({value[:10]}...)")
        else:
            missing_keys.append(f"❌ {description}: 未配置")
    
    # 检查OpenRouter密钥
    if not openrouter_key:
        missing_keys.append(f"❌ OpenRouter API密钥: 未配置")
    
    # 显示结果
    for item in configured_keys:
        print(item)
    
    for item in missing_keys:
        print(item)
    
    if missing_keys:
        print("\n⚠️  警告: 部分API密钥未配置，相关功能可能无法正常使用")
        print("\n📝 请在.env文件中配置缺失的API密钥:")
        for key in [k.split(':')[0].replace('❌ ', '').replace(' API密钥', '') for k in missing_keys]:
            if 'DeepSeek' in key:
                print(f"DEEPSEEK_API_KEY=your_deepseek_api_key_here")
            elif 'Gemini' in key:
                print(f"GEMINI_API_KEY=your_gemini_api_key_here")
            elif 'GLM' in key:
                print(f"GLM_API_KEY=your_glm_api_key_here")
            elif 'PPIO' in key:
                print(f"PPIO_API_KEY=your_ppio_api_key_here")
            elif 'Kimi' in key:
                print(f"KIMI_API_KEY=your_kimi_api_key_here")
        
        # 检查OpenRouter密钥
        if not openrouter_key:
            print(f"OPENROUTER_API_KEY=your_openrouter_api_key_here")
        
        return False
    else:
        print("\n✅ 所有API密钥均已配置")
        return True


def test_all_apis():
    """
    测试所有API连接
    """
    print("\n🚀 开始API连接测试...")
    print("=" * 50)
    
    # 初始化API实例
    apis = [
        (DeepSeekAPI(), "DeepSeek"),
        (GeminiAPI(), "Gemini"),
        (GLMAPI(), "GLM"),
        (OpenRouterAPI(), "OpenRouter"),
        (PPIOAPI(), "PPIO"),
        (KimiAPI(), "Kimi")
    ]
    
    results = []
    
    for api_instance, api_name in apis:
        success = test_api_connection(api_instance, api_name)
        results.append((api_name, success))
        
        # 在测试之间添加延迟，避免频率限制
        if api_instance != apis[-1][0]:  # 不是最后一个
            print("⏳ 等待3秒避免频率限制...")
            time.sleep(3)
    
    return results


def display_summary(results):
    """
    显示测试结果摘要
    """
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print("=" * 50)
    
    successful_apis = []
    failed_apis = []
    
    for api_name, success in results:
        if success:
            successful_apis.append(api_name)
            print(f"✅ {api_name}: 连接正常")
        else:
            failed_apis.append(api_name)
            print(f"❌ {api_name}: 连接失败")
    
    print(f"\n📈 成功率: {len(successful_apis)}/{len(results)} ({len(successful_apis)/len(results)*100:.1f}%)")
    
    if successful_apis:
        print(f"\n✅ 可用的API: {', '.join(successful_apis)}")
    
    if failed_apis:
        print(f"\n❌ 不可用的API: {', '.join(failed_apis)}")
        print("\n🔧 建议检查:")
        print("   1. API密钥是否正确配置")
        print("   2. 网络连接是否正常")
        print("   3. API服务是否可用")
        print("   4. 是否存在频率限制")
    
    if len(successful_apis) == len(results):
        print("\n🎉 所有API连接正常，环境配置完成!")
        return True
    else:
        print("\n⚠️  部分API连接失败，请检查配置")
        return False


def main():
    """
    主函数
    """
    print("🧪 Tempest Framework - 环境测试")
    print("=" * 60)
    print("这个脚本将测试所有API的连接情况")
    
    try:
        # 检查环境变量
        env_ok = check_environment_variables()
        
        if not env_ok:
            print("\n❌ 环境变量检查失败，请配置API密钥后重试")
            return
        
        # 询问是否继续测试
        confirm = input("\n🚀 是否开始API连接测试? (y/n, 默认y): ").strip().lower()
        if confirm in ['n', 'no']:
            print("👋 测试已取消")
            return
        
        # 测试所有API
        results = test_all_apis()
        
        # 显示摘要
        all_success = display_summary(results)
        
        if all_success:
            print("\n🎯 环境测试完成，可以开始使用Tempest框架!")
        else:
            print("\n🔧 请修复失败的API连接后再使用框架")
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()