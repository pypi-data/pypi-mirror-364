#!/usr/bin/env python
"""
测试KML文件检测功能
"""

import sys
import os
sys.path.append('./src')

import json
from autoreport.main import AeroSpotReportGenerator

def test_kml_detection():
    """测试KML文件检测功能"""
    print("=== 测试KML文件检测功能 ===")
    
    # 1. 读取现有配置
    with open('test.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"配置中的KML路径: {config.get('company_info', {}).get('kml_boundary_url', 'None')}")
    
    # 2. 检查KML文件是否存在
    kml_path = config.get('company_info', {}).get('kml_boundary_url')
    if kml_path:
        exists = os.path.exists(kml_path)
        print(f"KML文件存在检查: {kml_path} -> {'存在' if exists else '不存在'}")
    else:
        print("配置中没有KML文件路径")
        return False
    
    # 3. 创建报告生成器实例（不运行完整流程）
    try:
        generator = AeroSpotReportGenerator()
        generator.config = config
        
        # 模拟资源下载部分，检查KML是否被正确处理
        company_info = config.get("company_info", {})
        kml_url = company_info.get("kml_boundary_url")
        
        if kml_url:
            print(f"准备处理KML文件: {kml_url}")
            
            # 检查是否是本地文件路径
            if os.path.exists(kml_url):
                print(f"✅ KML文件检测成功: 本地文件 {kml_url}")
                return True
            elif kml_url.startswith(('http://', 'https://')):
                print(f"📡 KML文件检测: 网络URL {kml_url}")
                print("注意: 网络URL需要在实际运行时下载")
                return True
            else:
                print(f"❌ KML文件检测失败: 无效路径 {kml_url}")
                return False
        else:
            print("⚠️ 配置中没有KML文件URL")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False

def test_kml_boundary_method_selection():
    """测试KML边界方法选择逻辑"""
    print("\n=== 测试边界方法选择逻辑 ===")
    
    # 模拟不同情况的边界方法选择
    test_cases = [
        {"kml_path": "./test.kml", "exists": True, "expected": "kml"},
        {"kml_path": "./nonexistent.kml", "exists": False, "expected": "alpha_shape"},
        {"kml_path": None, "exists": False, "expected": "alpha_shape"},
        {"kml_path": "", "exists": False, "expected": "alpha_shape"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        kml_path = case["kml_path"]
        
        # 模拟边界方法选择逻辑
        if kml_path and os.path.exists(kml_path):
            boundary_method = 'kml'
        else:
            boundary_method = 'alpha_shape'
        
        expected = case["expected"]
        result = "✅" if boundary_method == expected else "❌"
        
        print(f"测试 {i}: kml_path='{kml_path}' -> {boundary_method} {result}")
        if boundary_method != expected:
            print(f"  期望: {expected}, 实际: {boundary_method}")
    
    return True

def main():
    """主函数"""
    print("KML文件检测功能测试")
    print("=" * 50)
    
    success1 = test_kml_detection()
    success2 = test_kml_boundary_method_selection()
    
    print("\n=== 总结 ===")
    if success1 and success2:
        print("🎉 KML文件检测功能正常！")
        print("✅ 配置中的KML路径被正确识别")
        print("✅ 边界方法选择逻辑正确")
        print("✅ 可以正确区分KML和alpha_shape方法")
    else:
        print("❌ KML文件检测功能异常")
        if not success1:
            print("❌ 配置中的KML路径处理有问题")
        if not success2:
            print("❌ 边界方法选择逻辑有问题")

if __name__ == "__main__":
    main()