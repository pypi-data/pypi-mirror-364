#!/usr/bin/env python
"""
展示KML修复前后的对比效果
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import matplotlib.pyplot as plt
from autoreport.utils.kml import get_kml_boundary_points

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_comparison():
    """创建修复前后的对比图"""
    print("=== 创建KML修复前后对比图 ===")
    
    # 1. 获取KML边界点
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ 无法获取KML边界点")
        return
    
    # 2. 设置参数
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    margin = 0.0005
    lon_min = kml_lon_min - margin
    lon_max = kml_lon_max + margin
    lat_min = kml_lat_min - margin
    lat_max = kml_lat_max + margin
    
    # 3. 创建示例数据
    np.random.seed(42)
    n_points = 20
    lons = np.random.uniform(kml_lon_min, kml_lon_max, n_points)
    lats = np.random.uniform(kml_lat_min, kml_lat_max, n_points)
    values = np.random.uniform(0, 10, n_points)
    
    # 4. 创建网格
    resolution = 100
    
    # 修复前：强制正方形网格
    grid_lat_before, grid_lon_before = np.mgrid[lat_min:lat_max:resolution*1j, 
                                               lon_min:lon_max:resolution*1j]
    
    # 修复后：按比例网格
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min
    aspect_ratio = lon_range / lat_range
    
    total_pixels = resolution * resolution
    lat_pixels = int(np.sqrt(total_pixels / aspect_ratio))
    lon_pixels = int(lat_pixels * aspect_ratio)
    
    grid_lat_after, grid_lon_after = np.mgrid[lat_min:lat_max:lat_pixels*1j, 
                                             lon_min:lon_max:lon_pixels*1j]
    
    # 5. 创建示例插值热力图（简化版）
    from scipy.interpolate import griddata
    
    points = np.column_stack((lons, lats))
    
    # 修复前
    grid_values_before = griddata(points, values, (grid_lon_before, grid_lat_before), method='linear')
    
    # 修复后  
    grid_values_after = griddata(points, values, (grid_lon_after, grid_lat_after), method='linear')
    
    # 应用KML掩码
    from autoreport.utils.kml import create_kml_boundary_mask
    
    mask_before = create_kml_boundary_mask(grid_lon_before, grid_lat_before, kml_path)
    mask_after = create_kml_boundary_mask(grid_lon_after, grid_lat_after, kml_path)
    
    grid_values_before[~mask_before] = np.nan
    grid_values_after[~mask_after] = np.nan
    
    # 6. 创建对比图
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 第一行：修复前
    # 原始KML边界
    ax1 = axes[0, 0]
    ax1.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax1.fill(kml_points[:, 0], kml_points[:, 1], alpha=0.3, color='red')
    ax1.scatter(lons, lats, c=values, s=50, cmap='viridis', edgecolors='black', label='数据点')
    ax1.set_xlim(lon_min, lon_max)
    ax1.set_ylim(lat_min, lat_max)
    ax1.set_title('KML边界定义 + 数据点')
    ax1.set_xlabel('经度')
    ax1.set_ylabel('纬度')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 修复前：强制正方形
    ax2 = axes[0, 1]
    im2 = ax2.imshow(grid_values_before, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax2.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax2.scatter(lons, lats, c='white', s=20, edgecolors='black', linewidth=0.5)
    ax2.set_title(f'修复前：强制正方形网格\\n{grid_lat_before.shape[0]}×{grid_lat_before.shape[1]}')
    ax2.set_xlabel('经度')
    ax2.set_ylabel('纬度')
    plt.colorbar(im2, ax=ax2)
    
    # 修复前的问题说明
    ax3 = axes[0, 2]
    ax3.text(0.5, 0.7, '修复前的问题:', ha='center', va='center', 
             transform=ax3.transAxes, fontsize=14, fontweight='bold', color='red')
    ax3.text(0.5, 0.5, f'• 强制正方形网格 ({resolution}×{resolution})\\n'
                      f'• 不考虑实际地理比例\\n'
                      f'• 长宽比被扭曲: {aspect_ratio:.3f} → 1.0\\n'
                      f'• 形状看起来被拉伸', 
             ha='center', va='center', transform=ax3.transAxes, fontsize=12)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_title('问题分析')
    
    # 第二行：修复后
    # 修复后：按比例网格
    ax4 = axes[1, 0]
    im4 = ax4.imshow(grid_values_after, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax4.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=1, alpha=0.8)
    ax4.scatter(lons, lats, c='white', s=20, edgecolors='black', linewidth=0.5)
    ax4.set_title(f'修复后：按比例网格\\n{grid_lat_after.shape[0]}×{grid_lat_after.shape[1]}')
    ax4.set_xlabel('经度')
    ax4.set_ylabel('纬度')
    plt.colorbar(im4, ax=ax4)
    
    # 网格对比
    ax5 = axes[1, 1]
    # 显示网格像素的实际形状
    pixel_before = (lon_max - lon_min) / grid_lat_before.shape[1], (lat_max - lat_min) / grid_lat_before.shape[0]
    pixel_after = (lon_max - lon_min) / grid_lat_after.shape[1], (lat_max - lat_min) / grid_lat_after.shape[0]
    
    ax5.text(0.5, 0.8, '网格像素形状对比:', ha='center', va='center', 
             transform=ax5.transAxes, fontsize=14, fontweight='bold')
    ax5.text(0.5, 0.6, f'修复前像素: {pixel_before[0]:.6f} × {pixel_before[1]:.6f}\\n'
                      f'像素长宽比: {pixel_before[0]/pixel_before[1]:.3f}\\n\\n'
                      f'修复后像素: {pixel_after[0]:.6f} × {pixel_after[1]:.6f}\\n'
                      f'像素长宽比: {pixel_after[0]/pixel_after[1]:.3f}', 
             ha='center', va='center', transform=ax5.transAxes, fontsize=12)
    ax5.set_xlim(0, 1)
    ax5.set_ylim(0, 1)
    ax5.set_xticks([])
    ax5.set_yticks([])
    ax5.set_title('像素形状对比')
    
    # 修复效果说明
    ax6 = axes[1, 2]
    ax6.text(0.5, 0.7, '修复后的改进:', ha='center', va='center', 
             transform=ax6.transAxes, fontsize=14, fontweight='bold', color='green')
    ax6.text(0.5, 0.5, f'• 按实际比例创建网格\\n'
                      f'• 保持地理长宽比: {aspect_ratio:.3f}\\n'
                      f'• 网格尺寸: {lat_pixels}×{lon_pixels}\\n'
                      f'• 形状完全符合KML边界\\n'
                      f'• 插值效果更准确', 
             ha='center', va='center', transform=ax6.transAxes, fontsize=12)
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    ax6.set_xticks([])
    ax6.set_yticks([])
    ax6.set_title('修复效果')
    
    plt.suptitle('KML边界插值修复前后对比', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('kml_before_after_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("✅ 对比图已保存: kml_before_after_comparison.png")
    
    # 7. 输出统计信息
    print("\\n=== 修复效果统计 ===")
    print(f"KML边界长宽比: {aspect_ratio:.3f}")
    print(f"修复前网格: {grid_lat_before.shape[0]}×{grid_lat_before.shape[1]} (比例: 1.0)")
    print(f"修复后网格: {grid_lat_after.shape[0]}×{grid_lat_after.shape[1]} (比例: {grid_lat_after.shape[1]/grid_lat_after.shape[0]:.3f})")
    
    coverage_before = np.sum(~np.isnan(grid_values_before)) / grid_values_before.size
    coverage_after = np.sum(~np.isnan(grid_values_after)) / grid_values_after.size
    
    print(f"修复前有效覆盖率: {coverage_before:.2%}")
    print(f"修复后有效覆盖率: {coverage_after:.2%}")

def main():
    """主函数"""
    print("KML边界插值修复前后对比")
    print("=" * 50)
    
    create_comparison()

if __name__ == "__main__":
    main()