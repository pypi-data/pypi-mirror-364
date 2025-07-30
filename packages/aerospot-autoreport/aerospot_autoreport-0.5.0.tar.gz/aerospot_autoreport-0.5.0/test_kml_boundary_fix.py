#!/usr/bin/env python
"""
测试修复后的KML边界点处理
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from autoreport.utils.kml import get_kml_boundary_points, get_kml_boundary_bounds
from autoreport.processor.maps import enhanced_interpolation_with_neighborhood

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def test_kml_boundary_points():
    """测试KML边界点获取"""
    kml_file = "test.kml"
    
    print("=== 测试KML边界点获取 ===")
    
    # 获取边界点
    boundary_points = get_kml_boundary_points(kml_file)
    
    if boundary_points:
        print(f"✓ 成功获取 {len(boundary_points)} 个边界点")
        
        # 显示前几个点
        print("前5个边界点:")
        for i, (lon, lat) in enumerate(boundary_points[:5]):
            print(f"  {i+1}: ({lon:.6f}, {lat:.6f})")
            
        # 计算边界范围
        lons = [p[0] for p in boundary_points]
        lats = [p[1] for p in boundary_points]
        
        print(f"边界范围: 经度 {min(lons):.6f} - {max(lons):.6f}")
        print(f"          纬度 {min(lats):.6f} - {max(lats):.6f}")
        
        return boundary_points
    else:
        print("✗ 获取边界点失败")
        return None

def test_kml_interpolation():
    """测试使用KML边界的插值"""
    kml_file = "test.kml"
    
    print("\n=== 测试KML边界插值 ===")
    
    # 创建模拟数据
    boundary_points = get_kml_boundary_points(kml_file)
    if not boundary_points:
        print("无法获取边界点，跳过测试")
        return
    
    # 在边界范围内生成随机数据点
    lons = [p[0] for p in boundary_points]
    lats = [p[1] for p in boundary_points]
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    # 生成随机数据
    np.random.seed(42)
    n_points = 20
    data_lons = np.random.uniform(min_lon, max_lon, n_points)
    data_lats = np.random.uniform(min_lat, max_lat, n_points)
    data_values = np.random.uniform(0, 10, n_points)
    
    # 创建DataFrame
    test_data = pd.DataFrame({
        'longitude': data_lons,
        'latitude': data_lats,
        'test_indicator': data_values
    })
    
    print(f"生成 {len(test_data)} 个测试数据点")
    
    # 使用KML边界进行插值
    try:
        grid_values, grid_lon, grid_lat, boundary_mask, boundary_points_result = enhanced_interpolation_with_neighborhood(
            test_data,
            grid_resolution=100,
            method='linear',
            boundary_method='kml',
            indicator_col='test_indicator',
            kml_boundary_path=kml_file
        )
        
        print(f"✓ 插值成功")
        print(f"  网格大小: {grid_values.shape}")
        print(f"  有效插值点: {np.sum(~np.isnan(grid_values))}")
        print(f"  边界掩码有效点: {np.sum(boundary_mask)}")
        print(f"  边界点数量: {len(boundary_points_result) if boundary_points_result is not None else 0}")
        
        # 可视化结果
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # 原始数据散点图
        ax1 = axes[0]
        scatter = ax1.scatter(data_lons, data_lats, c=data_values, cmap='viridis', s=100, edgecolor='black')
        
        # 绘制KML边界
        kml_coords = np.array(boundary_points)
        ax1.plot(kml_coords[:, 0], kml_coords[:, 1], 'r-', linewidth=2, label='KML边界')
        
        ax1.set_title('原始数据点和KML边界')
        ax1.set_xlabel('经度')
        ax1.set_ylabel('纬度')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1)
        
        # 插值结果
        ax2 = axes[1]
        im = ax2.imshow(grid_values, extent=[grid_lon.min(), grid_lon.max(), grid_lat.min(), grid_lat.max()],
                       origin='lower', cmap='viridis', interpolation='bilinear')
        ax2.scatter(data_lons, data_lats, c='red', s=50, alpha=0.7)
        ax2.plot(kml_coords[:, 0], kml_coords[:, 1], 'r-', linewidth=2)
        ax2.set_title('KML边界插值结果')
        ax2.set_xlabel('经度')
        ax2.set_ylabel('纬度')
        plt.colorbar(im, ax=ax2)
        
        # 边界掩码
        ax3 = axes[2]
        mask_im = ax3.imshow(boundary_mask, extent=[grid_lon.min(), grid_lon.max(), grid_lat.min(), grid_lat.max()],
                           origin='lower', cmap='RdYlBu', alpha=0.7)
        ax3.plot(kml_coords[:, 0], kml_coords[:, 1], 'r-', linewidth=2)
        ax3.set_title('边界掩码')
        ax3.set_xlabel('经度')
        ax3.set_ylabel('纬度')
        plt.colorbar(mask_im, ax=ax3)
        
        plt.tight_layout()
        plt.savefig('kml_boundary_interpolation_test.png', dpi=200, bbox_inches='tight')
        plt.close()
        
        print("✓ 可视化图片已保存: kml_boundary_interpolation_test.png")
        
        return True
        
    except Exception as e:
        print(f"✗ 插值失败: {e}")
        return False

def main():
    """主函数"""
    print("KML边界点处理修复测试")
    print("=" * 50)
    
    # 测试边界点获取
    boundary_points = test_kml_boundary_points()
    
    # 测试插值
    if boundary_points:
        success = test_kml_interpolation()
        
        if success:
            print("\n=== 测试总结 ===")
            print("✓ KML边界点获取正常")
            print("✓ KML边界插值正常")
            print("✓ 边界掩码创建正常")
            print("✓ 修复验证成功")
        else:
            print("\n=== 测试总结 ===")
            print("✓ KML边界点获取正常")
            print("✗ KML边界插值失败")
    else:
        print("\n=== 测试总结 ===")
        print("✗ KML边界点获取失败")

if __name__ == "__main__":
    main()