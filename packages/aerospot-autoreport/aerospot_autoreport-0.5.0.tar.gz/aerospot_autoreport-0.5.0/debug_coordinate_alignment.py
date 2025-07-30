#!/usr/bin/env python
"""
调试坐标对齐问题
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from autoreport.processor.maps import enhanced_interpolation_with_neighborhood
from autoreport.utils.kml import get_kml_boundary_points

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def debug_coordinate_alignment():
    """调试坐标对齐问题"""
    print("=== 调试坐标对齐问题 ===")
    
    # 1. 模拟实际使用场景
    # 假设的卫星图边界（通常比KML边界大）
    satellite_geo_bounds = [120.260, 31.510, 120.275, 31.525]  # [min_lon, min_lat, max_lon, max_lat]
    
    # KML边界（实际的测量区域）
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ 无法获取KML边界点")
        return
    
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    print(f"卫星图边界: {satellite_geo_bounds}")
    print(f"KML边界: [{kml_lon_min:.6f}, {kml_lat_min:.6f}, {kml_lon_max:.6f}, {kml_lat_max:.6f}]")
    
    # 2. 创建测试数据
    np.random.seed(42)
    n_points = 15
    lons = np.random.uniform(kml_lon_min, kml_lon_max, n_points)
    lats = np.random.uniform(kml_lat_min, kml_lat_max, n_points)
    values = np.random.uniform(2, 8, n_points)
    
    test_data = pd.DataFrame({
        'longitude': lons,
        'latitude': lats,
        'chla': values
    })
    
    # 3. 执行插值（模拟KML方法）
    grid_values, grid_lon, grid_lat, boundary_mask, boundary_points = enhanced_interpolation_with_neighborhood(
        test_data,
        grid_resolution=200,
        method='linear',
        boundary_method='kml',
        indicator_col='chla',
        kml_boundary_path=kml_path
    )
    
    # 4. 获取插值网格的实际范围
    grid_lon_min, grid_lon_max = grid_lon.min(), grid_lon.max()
    grid_lat_min, grid_lat_max = grid_lat.min(), grid_lat.max()
    
    print(f"\\n插值网格实际范围: [{grid_lon_min:.6f}, {grid_lat_min:.6f}, {grid_lon_max:.6f}, {grid_lat_max:.6f}]")
    print(f"插值网格形状: {grid_values.shape}")
    
    # 5. 可视化问题
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 显示边界对比
    ax1 = axes[0]
    # 绘制卫星图边界
    sat_rect = plt.Rectangle((satellite_geo_bounds[0], satellite_geo_bounds[1]), 
                            satellite_geo_bounds[2] - satellite_geo_bounds[0],
                            satellite_geo_bounds[3] - satellite_geo_bounds[1],
                            fill=False, edgecolor='blue', linewidth=2, label='卫星图边界')
    ax1.add_patch(sat_rect)
    
    # 绘制KML边界
    ax1.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax1.fill(kml_points[:, 0], kml_points[:, 1], alpha=0.3, color='red')
    
    # 绘制插值网格范围
    grid_rect = plt.Rectangle((grid_lon_min, grid_lat_min), 
                             grid_lon_max - grid_lon_min,
                             grid_lat_max - grid_lat_min,
                             fill=False, edgecolor='green', linewidth=2, 
                             linestyle='--', label='插值网格范围')
    ax1.add_patch(grid_rect)
    
    # 绘制数据点
    ax1.scatter(lons, lats, c=values, s=50, cmap='viridis', 
               edgecolors='black', linewidth=1, label='数据点')
    
    ax1.set_xlim(satellite_geo_bounds[0] - 0.002, satellite_geo_bounds[2] + 0.002)
    ax1.set_ylim(satellite_geo_bounds[1] - 0.002, satellite_geo_bounds[3] + 0.002)
    ax1.set_title('边界范围对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('经度')
    ax1.set_ylabel('纬度')
    
    # 错误的显示方式：使用卫星图边界
    ax2 = axes[1]
    # 模拟卫星图背景
    ax2.imshow(np.ones((100, 100, 3)) * 0.8, 
              extent=[satellite_geo_bounds[0], satellite_geo_bounds[2], 
                     satellite_geo_bounds[1], satellite_geo_bounds[3]], 
              alpha=0.5)
    
    # 错误：使用卫星图边界显示插值结果
    im2 = ax2.imshow(grid_values, 
                    extent=[satellite_geo_bounds[0], satellite_geo_bounds[2], 
                           satellite_geo_bounds[1], satellite_geo_bounds[3]],
                    origin='lower', cmap='jet', interpolation='bilinear',
                    alpha=0.8)
    ax2.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, alpha=0.8)
    ax2.scatter(lons, lats, c='white', s=30, edgecolors='black', linewidth=1)
    ax2.set_title('错误：使用卫星图边界显示\\n插值结果被拉伸')
    ax2.set_xlim(satellite_geo_bounds[0], satellite_geo_bounds[2])
    ax2.set_ylim(satellite_geo_bounds[1], satellite_geo_bounds[3])
    plt.colorbar(im2, ax=ax2)
    
    # 正确的显示方式：使用插值网格边界
    ax3 = axes[2]
    # 模拟卫星图背景
    ax3.imshow(np.ones((100, 100, 3)) * 0.8, 
              extent=[satellite_geo_bounds[0], satellite_geo_bounds[2], 
                     satellite_geo_bounds[1], satellite_geo_bounds[3]], 
              alpha=0.5)
    
    # 正确：使用插值网格的实际边界
    im3 = ax3.imshow(grid_values, 
                    extent=[grid_lon_min, grid_lon_max, grid_lat_min, grid_lat_max],
                    origin='lower', cmap='jet', interpolation='bilinear',
                    alpha=0.8)
    ax3.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, alpha=0.8)
    ax3.scatter(lons, lats, c='white', s=30, edgecolors='black', linewidth=1)
    ax3.set_title('正确：使用插值网格边界\\n坐标对齐准确')
    ax3.set_xlim(satellite_geo_bounds[0], satellite_geo_bounds[2])
    ax3.set_ylim(satellite_geo_bounds[1], satellite_geo_bounds[3])
    plt.colorbar(im3, ax=ax3)
    
    plt.suptitle('坐标对齐问题调试', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('coordinate_alignment_debug.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\\n✅ 调试图已保存: coordinate_alignment_debug.png")
    
    # 6. 问题分析
    print("\\n=== 问题分析 ===")
    print("错误原因：")
    print("1. 插值结果使用了卫星图边界作为extent")
    print("2. 但插值网格的实际范围是KML边界+margin")
    print("3. 导致插值图被拉伸到错误的地理位置")
    
    print("\\n解决方案：")
    print("1. 使用插值网格的实际边界作为extent")
    print("2. extent应该是[grid_lon_min, grid_lon_max, grid_lat_min, grid_lat_max]")
    print("3. 不要使用geo_bounds作为插值图的extent")
    
    # 7. 计算偏移量
    lon_offset = (satellite_geo_bounds[0] + satellite_geo_bounds[2]) / 2 - (grid_lon_min + grid_lon_max) / 2
    lat_offset = (satellite_geo_bounds[1] + satellite_geo_bounds[3]) / 2 - (grid_lat_min + grid_lat_max) / 2
    
    print(f"\\n坐标偏移量:")
    print(f"经度偏移: {lon_offset:.6f} 度")
    print(f"纬度偏移: {lat_offset:.6f} 度")

def main():
    """主函数"""
    print("坐标对齐问题调试")
    print("=" * 50)
    
    debug_coordinate_alignment()

if __name__ == "__main__":
    main()