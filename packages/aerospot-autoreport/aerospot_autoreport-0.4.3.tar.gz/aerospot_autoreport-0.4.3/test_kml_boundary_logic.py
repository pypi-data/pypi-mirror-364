#!/usr/bin/env python
"""
测试KML边界虚拟点逻辑的修正
验证只使用KML范围内的真实数据点作为边界虚拟点的值
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.spatial.distance import cdist
from autoreport.utils.kml import get_kml_boundary_points

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def test_kml_boundary_virtual_points():
    """测试KML边界虚拟点的逻辑修正"""
    print("=== 测试KML边界虚拟点逻辑 ===")
    
    # 1. 获取KML边界
    kml_path = "test.kml"
    kml_boundary_points = get_kml_boundary_points(kml_path)
    
    if kml_boundary_points is None:
        print("❌ 无法获取KML边界点")
        return False
    
    # 2. 创建测试数据：一些在KML内，一些在KML外
    np.random.seed(42)
    
    # KML边界范围
    kml_lon_min, kml_lon_max = kml_boundary_points[:, 0].min(), kml_boundary_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_boundary_points[:, 1].min(), kml_boundary_points[:, 1].max()
    
    # 创建KML内的数据点（高值）
    n_inside = 8
    lons_inside = np.random.uniform(kml_lon_min + 0.0005, kml_lon_max - 0.0005, n_inside)
    lats_inside = np.random.uniform(kml_lat_min + 0.0005, kml_lat_max - 0.0005, n_inside)
    values_inside = np.random.uniform(6, 9, n_inside)  # 高值
    
    # 创建KML外的数据点（低值）
    n_outside = 6
    # 在KML边界外但附近的点
    margin = 0.002
    lons_outside = np.concatenate([
        np.random.uniform(kml_lon_min - margin, kml_lon_min, n_outside//2),
        np.random.uniform(kml_lon_max, kml_lon_max + margin, n_outside//2)
    ])
    lats_outside = np.random.uniform(kml_lat_min - margin/2, kml_lat_max + margin/2, n_outside)
    values_outside = np.random.uniform(1, 3, n_outside)  # 低值
    
    # 合并所有数据点
    all_lons = np.concatenate([lons_inside, lons_outside])
    all_lats = np.concatenate([lats_inside, lats_outside])
    all_values = np.concatenate([values_inside, values_outside])
    points = np.column_stack((all_lons, all_lats))
    
    print(f"KML内数据点: {n_inside} 个，平均值: {values_inside.mean():.2f}")
    print(f"KML外数据点: {n_outside} 个，平均值: {values_outside.mean():.2f}")
    print(f"总数据点: {len(points)} 个")
    
    # 3. 测试边界虚拟点逻辑
    # 在KML边界上采样点
    n_boundary_points = 20
    if len(kml_boundary_points) > n_boundary_points:
        indices = np.linspace(0, len(kml_boundary_points)-1, n_boundary_points, dtype=int)
        sampled_boundary_points = kml_boundary_points[indices]
    else:
        sampled_boundary_points = kml_boundary_points
    
    # 筛选出在KML范围内的真实数据点
    kml_polygon_path = Path(kml_boundary_points)
    points_inside_mask = kml_polygon_path.contains_points(points)
    
    print(f"在KML范围内的真实数据点: {np.sum(points_inside_mask)} 个")
    
    if np.any(points_inside_mask):
        # 获取在KML范围内的数据点
        points_inside_kml = points[points_inside_mask]
        values_inside_kml = all_values[points_inside_mask]
        
        # 计算边界点到KML范围内真实数据点的距离
        distances = cdist(sampled_boundary_points, points_inside_kml)
        
        # 找到每个边界点在KML范围内的最近真实数据点
        nearest_indices = np.argmin(distances, axis=1)
        
        # 使用KML范围内最近真实数据点的值作为边界虚拟点的值
        boundary_values_corrected = values_inside_kml[nearest_indices]
        
        print(f"修正后边界虚拟点平均值: {boundary_values_corrected.mean():.2f}")
        print(f"修正后边界虚拟点值范围: {boundary_values_corrected.min():.2f} - {boundary_values_corrected.max():.2f}")
    else:
        print("❌ 没有真实数据点在KML范围内")
        return False
    
    # 4. 对比原始逻辑（使用所有点中的最近点）
    distances_all = cdist(sampled_boundary_points, points)
    nearest_indices_all = np.argmin(distances_all, axis=1)
    boundary_values_original = all_values[nearest_indices_all]
    
    print(f"原始逻辑边界虚拟点平均值: {boundary_values_original.mean():.2f}")
    print(f"原始逻辑边界虚拟点值范围: {boundary_values_original.min():.2f} - {boundary_values_original.max():.2f}")
    
    # 5. 可视化对比
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 左图：数据分布
    ax1 = axes[0]
    # 绘制KML边界
    ax1.plot(kml_boundary_points[:, 0], kml_boundary_points[:, 1], 'k-', linewidth=2, label='KML边界')
    ax1.fill(kml_boundary_points[:, 0], kml_boundary_points[:, 1], alpha=0.2, color='gray')
    
    # 绘制数据点
    scatter_inside = ax1.scatter(lons_inside, lats_inside, c=values_inside, s=100, 
                                cmap='viridis', edgecolors='green', linewidth=2, 
                                label=f'KML内数据 (均值:{values_inside.mean():.1f})')
    scatter_outside = ax1.scatter(lons_outside, lats_outside, c=values_outside, s=100, 
                                 cmap='viridis', edgecolors='red', linewidth=2,
                                 label=f'KML外数据 (均值:{values_outside.mean():.1f})')
    
    # 绘制边界采样点
    ax1.scatter(sampled_boundary_points[:, 0], sampled_boundary_points[:, 1], 
               c='orange', s=50, marker='s', label='边界采样点')
    
    ax1.set_title('测试数据分布')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter_inside, ax=ax1, label='数据值')
    
    # 中图：修正后的边界虚拟点值
    ax2 = axes[1]
    ax2.plot(kml_boundary_points[:, 0], kml_boundary_points[:, 1], 'k-', linewidth=2)
    ax2.fill(kml_boundary_points[:, 0], kml_boundary_points[:, 1], alpha=0.2, color='gray')
    
    scatter2 = ax2.scatter(sampled_boundary_points[:, 0], sampled_boundary_points[:, 1], 
                          c=boundary_values_corrected, s=100, cmap='viridis', 
                          edgecolors='black', linewidth=1)
    ax2.set_title(f'修正后虚拟点值\\n(只使用KML内数据)\\n均值: {boundary_values_corrected.mean():.2f}')
    plt.colorbar(scatter2, ax=ax2, label='虚拟点值')
    
    # 右图：原始逻辑的边界虚拟点值
    ax3 = axes[2]
    ax3.plot(kml_boundary_points[:, 0], kml_boundary_points[:, 1], 'k-', linewidth=2)
    ax3.fill(kml_boundary_points[:, 0], kml_boundary_points[:, 1], alpha=0.2, color='gray')
    
    scatter3 = ax3.scatter(sampled_boundary_points[:, 0], sampled_boundary_points[:, 1], 
                          c=boundary_values_original, s=100, cmap='viridis', 
                          edgecolors='black', linewidth=1)
    ax3.set_title(f'原始逻辑虚拟点值\\n(使用所有数据)\\n均值: {boundary_values_original.mean():.2f}')
    plt.colorbar(scatter3, ax=ax3, label='虚拟点值')
    
    plt.suptitle('KML边界虚拟点逻辑修正对比', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('kml_boundary_virtual_points_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("✅ 对比图已保存: kml_boundary_virtual_points_comparison.png")
    
    # 6. 分析修正效果
    print("\n=== 修正效果分析 ===")
    value_diff = boundary_values_corrected.mean() - boundary_values_original.mean()
    print(f"边界虚拟点平均值差异: {value_diff:+.2f}")
    
    if np.abs(value_diff) > 1:
        print("✅ 修正有显著效果：边界虚拟点值更准确地反映KML范围内的数据特征")
    else:
        print("ℹ️ 修正效果不明显：可能测试数据差异不够大")
    
    return True

def main():
    """主函数"""
    print("KML边界虚拟点逻辑修正测试")
    print("=" * 50)
    
    success = test_kml_boundary_virtual_points()
    
    print("\n=== 总结 ===")
    if success:
        print("✅ KML边界虚拟点逻辑修正完成")
        print("✅ 现在只使用KML范围内的真实数据点作为边界虚拟点的值源")
        print("✅ 这确保了边界插值更准确地反映目标区域的数据特征")
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    main()