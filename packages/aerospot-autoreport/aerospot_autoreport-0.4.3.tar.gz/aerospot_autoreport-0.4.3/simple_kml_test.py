#!/usr/bin/env python
"""
简单的KML文件测试脚本
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import matplotlib.pyplot as plt
from autoreport.utils.kml import KMLParser, get_kml_boundary_bounds

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def test_kml_parsing():
    """测试KML文件解析"""
    kml_file = "test.kml"
    
    print("=== KML文件解析测试 ===")
    print(f"测试文件: {kml_file}")
    
    # 使用KMLParser解析
    try:
        parser = KMLParser(kml_file)
        boundaries = parser.extract_coordinates()
        
        print(f"找到 {len(boundaries)} 个边界区域")
        
        for i, boundary in enumerate(boundaries):
            print(f"\n边界 {i+1}:")
            print(f"  坐标点数: {len(boundary)}")
            
            # 计算边界范围
            lons = [coord[0] for coord in boundary]
            lats = [coord[1] for coord in boundary]
            
            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)
            
            print(f"  经度范围: {min_lon:.6f} - {max_lon:.6f}")
            print(f"  纬度范围: {min_lat:.6f} - {max_lat:.6f}")
            
            # 显示前几个坐标点
            print("  前5个坐标点:")
            for j, coord in enumerate(boundary[:5]):
                print(f"    {j+1}: 经度 {coord[0]:.6f}, 纬度 {coord[1]:.6f}")
            
            # 绘制边界
            coords = np.array(boundary)
            plt.figure(figsize=(10, 8))
            plt.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2, label='KML边界')
            plt.scatter(coords[:, 0], coords[:, 1], c='red', s=30, alpha=0.6, label='坐标点')
            
            # 标记起点和终点
            plt.scatter(coords[0, 0], coords[0, 1], c='green', s=100, marker='o', label='起点')
            plt.scatter(coords[-1, 0], coords[-1, 1], c='blue', s=100, marker='s', label='终点')
            
            plt.xlabel('经度')
            plt.ylabel('纬度')
            plt.title(f'KML边界 {i+1} 可视化')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.axis('equal')
            
            # 保存图片
            plt.savefig(f'kml_boundary_{i+1}.png', dpi=200, bbox_inches='tight')
            plt.close()
            
            print(f"  边界图片已保存: kml_boundary_{i+1}.png")
        
        return boundaries
        
    except Exception as e:
        print(f"解析KML文件时出错: {e}")
        return []

def test_boundary_bounds():
    """测试边界范围获取"""
    kml_file = "test.kml"
    
    print("\n=== 边界范围获取测试 ===")
    
    try:
        bounds = get_kml_boundary_bounds(kml_file)
        if bounds:
            min_lon, min_lat, max_lon, max_lat = bounds
            print(f"边界范围: 经度 {min_lon:.6f} - {max_lon:.6f}, 纬度 {min_lat:.6f} - {max_lat:.6f}")
            print(f"区域大小: 经度跨度 {max_lon - min_lon:.6f}°, 纬度跨度 {max_lat - min_lat:.6f}°")
        else:
            print("无法获取边界范围")
        
        return bounds
        
    except Exception as e:
        print(f"获取边界范围时出错: {e}")
        return None

def main():
    """主函数"""
    print("KML文件简单测试")
    print("=" * 40)
    
    # 测试KML解析
    boundaries = test_kml_parsing()
    
    # 测试边界范围
    bounds = test_boundary_bounds()
    
    print("\n=== 测试总结 ===")
    if boundaries:
        print(f"✓ 成功解析 {len(boundaries)} 个边界区域")
        total_points = sum(len(b) for b in boundaries)
        print(f"✓ 总共包含 {total_points} 个坐标点")
        
        if bounds:
            print(f"✓ 边界范围获取成功")
        else:
            print("✗ 边界范围获取失败")
    else:
        print("✗ KML文件解析失败")

if __name__ == "__main__":
    main()