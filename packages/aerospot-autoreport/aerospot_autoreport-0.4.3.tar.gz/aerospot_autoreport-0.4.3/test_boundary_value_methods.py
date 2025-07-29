#!/usr/bin/env python
"""
对比边界虚拟点的不同赋值方法
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.spatial.distance import cdist
from autoreport.utils.kml import get_kml_boundary_points, create_kml_boundary_mask

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def compare_boundary_value_methods():
    """对比边界虚拟点的不同赋值方法"""
    print("=== 对比边界虚拟点赋值方法 ===")
    
    # 1. 设置参数
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ 无法获取KML边界点")
        return
    
    # 2. 设置网格
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    margin = 0.0005
    lon_min = kml_lon_min - margin
    lon_max = kml_lon_max + margin
    lat_min = kml_lat_min - margin
    lat_max = kml_lat_max + margin
    
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min
    
    desired_resolution = 0.00002
    lat_pixels = int(np.ceil(lat_range / desired_resolution))
    lon_pixels = int(np.ceil(lon_range / desired_resolution))
    lat_pixels = min(max(lat_pixels, 50), 200)
    lon_pixels = min(max(lon_pixels, 50), 200)
    
    grid_lat, grid_lon = np.mgrid[lat_min:lat_max:lat_pixels*1j, 
                                 lon_min:lon_max:lon_pixels*1j]
    
    # 3. 创建测试数据 - 有明显的空间梯度
    np.random.seed(42)
    n_points = 12
    
    # 创建有梯度的数据：左高右低
    lons = np.random.uniform(kml_lon_min + 0.0005, kml_lon_max - 0.0005, n_points)
    lats = np.random.uniform(kml_lat_min + 0.0005, kml_lat_max - 0.0005, n_points)
    
    # 基于位置创建有梯度的值：西边高，东边低
    normalized_lons = (lons - kml_lon_min) / (kml_lon_max - kml_lon_min)
    base_values = 8 - 6 * normalized_lons  # 从8降到2
    noise = np.random.normal(0, 0.5, n_points)
    values = base_values + noise
    values = np.clip(values, 0, 10)  # 限制范围
    
    points = np.column_stack((lons, lats))
    
    print(f"数据点值范围: {values.min():.2f} - {values.max():.2f}")
    
    # 4. 准备边界点
    n_boundary_points = min(30, len(kml_points))
    if len(kml_points) > n_boundary_points:
        indices = np.linspace(0, len(kml_points)-1, n_boundary_points, dtype=int)
        sampled_boundary_points = kml_points[indices]
    else:
        sampled_boundary_points = kml_points
    
    # 5. 方法1：使用平均值
    boundary_value_avg = np.mean(values)
    boundary_values_avg = np.full(len(sampled_boundary_points), boundary_value_avg)
    
    extended_points_avg = np.vstack([points, sampled_boundary_points])
    extended_values_avg = np.concatenate([values, boundary_values_avg])
    
    grid_values_avg = griddata(extended_points_avg, extended_values_avg, (grid_lon, grid_lat), method='linear')
    
    # 6. 方法2：使用最近真实值
    distances = cdist(sampled_boundary_points, points)
    nearest_indices = np.argmin(distances, axis=1)
    boundary_values_nearest = values[nearest_indices]
    
    extended_points_nearest = np.vstack([points, sampled_boundary_points])
    extended_values_nearest = np.concatenate([values, boundary_values_nearest])
    
    grid_values_nearest = griddata(extended_points_nearest, extended_values_nearest, (grid_lon, grid_lat), method='linear')
    
    # 7. 应用KML掩码
    kml_mask = create_kml_boundary_mask(grid_lon, grid_lat, kml_path)
    
    grid_values_avg[~kml_mask] = np.nan
    grid_values_nearest[~kml_mask] = np.nan
    
    # 8. 可视化对比
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 第一行：数据分布和边界点值
    # 原始数据
    ax1 = axes[0, 0]
    ax1.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, alpha=0.7, label='KML边界')
    scatter = ax1.scatter(lons, lats, c=values, s=80, cmap='viridis', 
                         edgecolors='black', linewidth=1, label='真实数据')
    ax1.set_xlim(lon_min, lon_max)
    ax1.set_ylim(lat_min, lat_max)
    ax1.set_title('原始数据分布')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1)
    
    # 平均值方法的边界点
    ax2 = axes[0, 1]
    ax2.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, alpha=0.7, label='KML边界')
    ax2.scatter(lons, lats, c=values, s=60, cmap='viridis', 
               edgecolors='black', linewidth=1, label='真实数据')
    boundary_scatter_avg = ax2.scatter(sampled_boundary_points[:, 0], sampled_boundary_points[:, 1], 
                                      c=boundary_values_avg, s=40, cmap='viridis', 
                                      marker='s', edgecolors='red', linewidth=1, label=f'边界虚拟点(均值={boundary_value_avg:.2f})')
    ax2.set_xlim(lon_min, lon_max)
    ax2.set_ylim(lat_min, lat_max)
    ax2.set_title('方法1：边界点使用平均值')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.colorbar(boundary_scatter_avg, ax=ax2)
    
    # 最近值方法的边界点
    ax3 = axes[0, 2]
    ax3.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, alpha=0.7, label='KML边界')
    ax3.scatter(lons, lats, c=values, s=60, cmap='viridis', 
               edgecolors='black', linewidth=1, label='真实数据')
    boundary_scatter_nearest = ax3.scatter(sampled_boundary_points[:, 0], sampled_boundary_points[:, 1], 
                                          c=boundary_values_nearest, s=40, cmap='viridis', 
                                          marker='s', edgecolors='red', linewidth=1, label='边界虚拟点(最近值)')
    ax3.set_xlim(lon_min, lon_max)
    ax3.set_ylim(lat_min, lat_max)
    ax3.set_title('方法2：边界点使用最近真实值')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    plt.colorbar(boundary_scatter_nearest, ax=ax3)
    
    # 第二行：插值结果对比
    # 平均值方法结果
    ax4 = axes[1, 0]
    im4 = ax4.imshow(grid_values_avg, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax4.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax4.scatter(lons, lats, c='white', s=30, edgecolors='black', linewidth=1)
    ax4.set_title('平均值方法插值结果')
    plt.colorbar(im4, ax=ax4)
    
    # 最近值方法结果
    ax5 = axes[1, 1]
    im5 = ax5.imshow(grid_values_nearest, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax5.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax5.scatter(lons, lats, c='white', s=30, edgecolors='black', linewidth=1)
    ax5.set_title('最近值方法插值结果')
    plt.colorbar(im5, ax=ax5)
    
    # 差异图
    ax6 = axes[1, 2]
    diff = grid_values_nearest - grid_values_avg
    im6 = ax6.imshow(diff, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='RdBu', interpolation='bilinear')
    ax6.plot(kml_points[:, 0], kml_points[:, 1], 'k-', linewidth=1, alpha=0.8)
    ax6.set_title('差异 (最近值 - 平均值)')
    plt.colorbar(im6, ax=ax6)
    
    plt.suptitle('边界虚拟点赋值方法对比', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('boundary_value_methods_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\n✅ 对比图已保存: boundary_value_methods_comparison.png")
    
    # 9. 统计分析
    print("\n=== 方法对比分析 ===")
    print(f"真实数据值范围: {values.min():.2f} - {values.max():.2f}")
    print(f"平均值方法边界值: {boundary_value_avg:.2f} (固定)")
    print(f"最近值方法边界值范围: {boundary_values_nearest.min():.2f} - {boundary_values_nearest.max():.2f}")
    
    # 计算边界区域的值分布
    edge_mask = kml_mask & ~np.isnan(grid_values_avg)
    edge_values_avg = grid_values_avg[edge_mask]
    edge_values_nearest = grid_values_nearest[edge_mask]
    
    print(f"\\n插值结果边界区域值分布:")
    print(f"平均值方法: {edge_values_avg.min():.2f} - {edge_values_avg.max():.2f}")
    print(f"最近值方法: {edge_values_nearest.min():.2f} - {edge_values_nearest.max():.2f}")
    
    print(f"\\n最近值方法的优势:")
    print("1. 保持空间梯度的连续性")
    print("2. 边界值更接近附近的真实观测")
    print("3. 插值结果更符合物理现象")

def main():
    """主函数"""
    print("边界虚拟点赋值方法对比测试")
    print("=" * 50)
    
    compare_boundary_value_methods()

if __name__ == "__main__":
    main()