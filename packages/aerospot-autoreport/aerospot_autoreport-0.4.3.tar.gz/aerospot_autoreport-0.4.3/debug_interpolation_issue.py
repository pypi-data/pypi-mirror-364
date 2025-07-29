#!/usr/bin/env python
"""
调试插值和掩码不匹配的问题
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from autoreport.utils.kml import get_kml_boundary_points, create_kml_boundary_mask

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def debug_interpolation_issue():
    """调试插值和掩码不匹配的问题"""
    print("=== 调试插值和掩码不匹配问题 ===")
    
    # 1. 获取KML边界
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ 无法获取KML边界点")
        return
    
    # 2. 设置网格范围
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    margin = 0.0005
    lon_min = kml_lon_min - margin
    lon_max = kml_lon_max + margin
    lat_min = kml_lat_min - margin
    lat_max = kml_lat_max + margin
    
    print(f"网格范围: 经度 {lon_min:.6f} - {lon_max:.6f}")
    print(f"网格范围: 纬度 {lat_min:.6f} - {lat_max:.6f}")
    
    # 3. 创建网格
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min
    aspect_ratio = lon_range / lat_range
    
    desired_resolution = 0.00002
    lat_pixels = int(np.ceil(lat_range / desired_resolution))
    lon_pixels = int(np.ceil(lon_range / desired_resolution))
    lat_pixels = min(max(lat_pixels, 50), 300)  # 限制大小以便观察
    lon_pixels = min(max(lon_pixels, 50), 300)
    
    grid_lat, grid_lon = np.mgrid[lat_min:lat_max:lat_pixels*1j, 
                                 lon_min:lon_max:lon_pixels*1j]
    
    print(f"网格大小: {lat_pixels} x {lon_pixels}")
    
    # 4. 创建测试数据 - 问题可能在这里！
    np.random.seed(42)
    
    # 情况1：数据点只在KML边界的一小部分区域
    print("\n--- 情况1：数据点分布局限 ---")
    n_points = 15
    # 故意让数据点只分布在KML边界的一部分
    partial_lon_min = kml_lon_min + (kml_lon_max - kml_lon_min) * 0.2
    partial_lon_max = kml_lon_min + (kml_lon_max - kml_lon_min) * 0.8
    partial_lat_min = kml_lat_min + (kml_lat_max - kml_lat_min) * 0.1
    partial_lat_max = kml_lat_min + (kml_lat_max - kml_lat_min) * 0.7
    
    limited_lons = np.random.uniform(partial_lon_min, partial_lon_max, n_points)
    limited_lats = np.random.uniform(partial_lat_min, partial_lat_max, n_points)
    limited_values = np.random.uniform(2, 8, n_points)
    
    # 情况2：数据点覆盖整个KML边界
    print("--- 情况2：数据点覆盖整个边界 ---")
    full_lons = np.random.uniform(kml_lon_min, kml_lon_max, n_points)
    full_lats = np.random.uniform(kml_lat_min, kml_lat_max, n_points)
    full_values = np.random.uniform(2, 8, n_points)
    
    # 5. 执行插值对比
    points_limited = np.column_stack((limited_lons, limited_lats))
    points_full = np.column_stack((full_lons, full_lats))
    
    grid_values_limited = griddata(points_limited, limited_values, (grid_lon, grid_lat), method='linear')
    grid_values_full = griddata(points_full, full_values, (grid_lon, grid_lat), method='linear')
    
    # 6. 创建KML掩码
    kml_mask = create_kml_boundary_mask(grid_lon, grid_lat, kml_path)
    
    # 7. 统计信息
    print(f"\n=== 插值结果统计 ===")
    limited_valid = np.sum(~np.isnan(grid_values_limited))
    full_valid = np.sum(~np.isnan(grid_values_full))
    mask_valid = np.sum(kml_mask)
    total_pixels = grid_lat.size
    
    print(f"总网格点数: {total_pixels}")
    print(f"KML掩码有效点: {mask_valid} ({mask_valid/total_pixels:.1%})")
    print(f"局限分布插值有效点: {limited_valid} ({limited_valid/total_pixels:.1%})")
    print(f"完整分布插值有效点: {full_valid} ({full_valid/total_pixels:.1%})")
    
    # 8. 可视化对比
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    
    # 第一行：局限分布情况
    # 数据点分布
    ax1 = axes[0, 0]
    ax1.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax1.scatter(limited_lons, limited_lats, c=limited_values, s=50, cmap='viridis', 
               edgecolors='black', label='数据点')
    ax1.set_xlim(lon_min, lon_max)
    ax1.set_ylim(lat_min, lat_max)
    ax1.set_title('局限分布：数据点')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 插值结果
    ax2 = axes[0, 1]
    im2 = ax2.imshow(grid_values_limited, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax2.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax2.set_title('局限分布：插值结果')
    plt.colorbar(im2, ax=ax2)
    
    # KML掩码
    ax3 = axes[0, 2]
    im3 = ax3.imshow(kml_mask, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='RdYlBu', interpolation='nearest')
    ax3.plot(kml_points[:, 0], kml_points[:, 1], 'k-', linewidth=1)
    ax3.set_title('KML边界掩码')
    plt.colorbar(im3, ax=ax3)
    
    # 应用掩码后
    masked_limited = grid_values_limited.copy()
    masked_limited[~kml_mask] = np.nan
    ax4 = axes[0, 3]
    im4 = ax4.imshow(masked_limited, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax4.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax4.set_title('应用掩码后')
    plt.colorbar(im4, ax=ax4)
    
    # 第二行：完整分布情况
    # 数据点分布
    ax5 = axes[1, 0]
    ax5.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax5.scatter(full_lons, full_lats, c=full_values, s=50, cmap='viridis', 
               edgecolors='black', label='数据点')
    ax5.set_xlim(lon_min, lon_max)
    ax5.set_ylim(lat_min, lat_max)
    ax5.set_title('完整分布：数据点')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 插值结果
    ax6 = axes[1, 1]
    im6 = ax6.imshow(grid_values_full, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax6.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax6.set_title('完整分布：插值结果')
    plt.colorbar(im6, ax=ax6)
    
    # 重复显示KML掩码
    ax7 = axes[1, 2]
    im7 = ax7.imshow(kml_mask, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='RdYlBu', interpolation='nearest')
    ax7.plot(kml_points[:, 0], kml_points[:, 1], 'k-', linewidth=1)
    ax7.set_title('KML边界掩码（同上）')
    plt.colorbar(im7, ax=ax7)
    
    # 应用掩码后
    masked_full = grid_values_full.copy()
    masked_full[~kml_mask] = np.nan
    ax8 = axes[1, 3]
    im8 = ax8.imshow(masked_full, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax8.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax8.set_title('应用掩码后')
    plt.colorbar(im8, ax=ax8)
    
    plt.suptitle('插值和掩码问题调试', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('interpolation_mask_debug.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\n✅ 调试图已保存: interpolation_mask_debug.png")
    
    # 9. 分析问题原因
    print("\n=== 问题分析 ===")
    print("问题原因：")
    print("1. griddata()只在数据点分布的区域附近进行插值")
    print("2. 如果数据点没有覆盖整个KML边界，插值结果就不会覆盖整个边界")
    print("3. 这是插值算法的正常行为，不是bug")
    
    print("\n解决方案：")
    print("1. 确保数据点分布覆盖整个KML边界区域")
    print("2. 在KML边界上添加虚拟数据点")
    print("3. 使用fill_value参数进行外推")
    print("4. 调整插值参数以增强外推能力")

def main():
    """主函数"""
    print("插值和掩码不匹配问题调试")
    print("=" * 50)
    
    debug_interpolation_issue()

if __name__ == "__main__":
    main()