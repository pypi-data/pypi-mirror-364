#!/usr/bin/env python
"""
诊断KML掩码的形状和方向问题
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import matplotlib.pyplot as plt
from autoreport.utils.kml import get_kml_boundary_points, create_kml_boundary_mask

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def diagnose_kml_mask():
    """诊断KML掩码问题"""
    print("=== 诊断KML掩码形状和方向问题 ===")
    
    # 1. 获取KML边界点
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ 无法获取KML边界点")
        return
    
    # 2. 分析KML边界范围
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    lon_range = kml_lon_max - kml_lon_min
    lat_range = kml_lat_max - kml_lat_min
    aspect_ratio = lon_range / lat_range
    
    print(f"KML边界范围:")
    print(f"  经度: {kml_lon_min:.6f} - {kml_lon_max:.6f} (范围: {lon_range:.6f})")
    print(f"  纬度: {kml_lat_min:.6f} - {kml_lat_max:.6f} (范围: {lat_range:.6f})")
    print(f"  长宽比: {aspect_ratio:.3f}")
    
    # 3. 创建测试网格 - 使用正方形网格（问题所在）
    print("\n--- 当前的正方形网格方式 ---")
    margin = 0.0005
    lon_min = kml_lon_min - margin
    lon_max = kml_lon_max + margin
    lat_min = kml_lat_min - margin
    lat_max = kml_lat_max + margin
    
    resolution = 100
    grid_lat_square, grid_lon_square = np.mgrid[lat_min:lat_max:resolution*1j, 
                                               lon_min:lon_max:resolution*1j]
    
    print(f"正方形网格形状: {grid_lat_square.shape}")
    print(f"网格长宽比: {grid_lat_square.shape[1] / grid_lat_square.shape[0]:.3f}")
    
    # 4. 创建按比例的网格 - 修复方案
    print("\n--- 修复：按实际比例创建网格 ---")
    # 计算合适的网格分辨率，保持长宽比
    total_pixels = resolution * resolution
    lat_pixels = int(np.sqrt(total_pixels / aspect_ratio))
    lon_pixels = int(lat_pixels * aspect_ratio)
    
    print(f"修正后网格尺寸: {lat_pixels} x {lon_pixels}")
    print(f"修正后长宽比: {lon_pixels / lat_pixels:.3f}")
    
    grid_lat_proper, grid_lon_proper = np.mgrid[lat_min:lat_max:lat_pixels*1j, 
                                               lon_min:lon_max:lon_pixels*1j]
    
    # 5. 创建KML掩码对比
    mask_square = create_kml_boundary_mask(grid_lon_square, grid_lat_square, kml_path)
    mask_proper = create_kml_boundary_mask(grid_lon_proper, grid_lat_proper, kml_path)
    
    # 6. 可视化对比
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 第一行：原始KML边界和正方形网格结果
    ax1 = axes[0, 0]
    ax1.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax1.fill(kml_points[:, 0], kml_points[:, 1], alpha=0.3, color='red')
    ax1.set_xlim(lon_min, lon_max)
    ax1.set_ylim(lat_min, lat_max)
    ax1.set_title('原始KML边界')
    ax1.set_xlabel('经度')
    ax1.set_ylabel('纬度')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')  # 等比例显示
    
    ax2 = axes[0, 1]
    im2 = ax2.imshow(mask_square, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='RdYlBu', interpolation='nearest')
    ax2.plot(kml_points[:, 0], kml_points[:, 1], 'k-', linewidth=1, alpha=0.7)
    ax2.set_title(f'正方形网格掩码 ({grid_lat_square.shape[0]}x{grid_lat_square.shape[1]})')
    ax2.set_xlabel('经度')
    ax2.set_ylabel('纬度')
    plt.colorbar(im2, ax=ax2)
    
    ax3 = axes[0, 2]
    im3 = ax3.imshow(mask_proper, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='RdYlBu', interpolation='nearest')
    ax3.plot(kml_points[:, 0], kml_points[:, 1], 'k-', linewidth=1, alpha=0.7)
    ax3.set_title(f'按比例网格掩码 ({grid_lat_proper.shape[0]}x{grid_lat_proper.shape[1]})')
    ax3.set_xlabel('经度')
    ax3.set_ylabel('纬度')
    plt.colorbar(im3, ax=ax3)
    
    # 第二行：检查坐标轴方向
    ax4 = axes[1, 0]
    # 在网格的四个角落标记点，检查坐标轴方向
    corner_lons = [lon_min, lon_max, lon_max, lon_min]
    corner_lats = [lat_min, lat_min, lat_max, lat_max]
    corner_labels = ['西南', '东南', '东北', '西北']
    
    ax4.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2)
    for i, (lon, lat, label) in enumerate(zip(corner_lons, corner_lats, corner_labels)):
        ax4.plot(lon, lat, 'bo', markersize=8)
        ax4.annotate(label, (lon, lat), xytext=(5, 5), textcoords='offset points')
    ax4.set_xlim(lon_min, lon_max)
    ax4.set_ylim(lat_min, lat_max)
    ax4.set_title('坐标轴方向检查')
    ax4.set_xlabel('经度')
    ax4.set_ylabel('纬度')
    ax4.grid(True, alpha=0.3)
    ax4.set_aspect('equal')
    
    # 显示网格坐标的实际排列
    ax5 = axes[1, 1]
    # 显示网格的前几行和列
    sample_size = min(10, grid_lat_square.shape[0])
    sample_lat = grid_lat_square[:sample_size, :sample_size]
    sample_lon = grid_lon_square[:sample_size, :sample_size]
    
    for i in range(sample_size):
        for j in range(sample_size):
            ax5.plot(sample_lon[i, j], sample_lat[i, j], 'b.', markersize=2)
            if i == 0 or j == 0:  # 标记边界
                ax5.annotate(f'({i},{j})', (sample_lon[i, j], sample_lat[i, j]), 
                           xytext=(2, 2), textcoords='offset points', fontsize=6)
    
    ax5.set_title('网格点分布 (前10x10)')
    ax5.set_xlabel('经度')
    ax5.set_ylabel('纬度')
    ax5.grid(True, alpha=0.3)
    
    # 掩码差异分析
    ax6 = axes[1, 2]
    if mask_square.shape == mask_proper.shape:
        mask_diff = mask_proper.astype(int) - mask_square.astype(int)
        im6 = ax6.imshow(mask_diff, extent=[lon_min, lon_max, lat_min, lat_max],
                        origin='lower', cmap='RdBu', interpolation='nearest')
        ax6.set_title('掩码差异 (按比例 - 正方形)')
        plt.colorbar(im6, ax=ax6)
    else:
        ax6.text(0.5, 0.5, f'网格尺寸不同\\n正方形: {mask_square.shape}\\n按比例: {mask_proper.shape}',
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('网格尺寸对比')
    
    plt.tight_layout()
    plt.savefig('kml_mask_diagnosis.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\n✅ 诊断图片已保存: kml_mask_diagnosis.png")
    
    # 7. 分析结果
    print("\n=== 问题分析 ===")
    print(f"1. 强制正方形问题: 当前网格强制为 {resolution}x{resolution}")
    print(f"   实际应该是按比例: 约 {lat_pixels}x{lon_pixels}")
    print(f"2. 长宽比问题: 实际比例 {aspect_ratio:.3f}, 被强制为 1.0")
    
    # 检查掩码覆盖率
    square_coverage = np.sum(mask_square) / mask_square.size
    proper_coverage = np.sum(mask_proper) / mask_proper.size
    
    print(f"3. 掩码覆盖率:")
    print(f"   正方形网格: {square_coverage:.2%}")
    print(f"   按比例网格: {proper_coverage:.2%}")

def main():
    """主函数"""
    print("KML掩码形状和方向问题诊断")
    print("=" * 50)
    
    diagnose_kml_mask()

if __name__ == "__main__":
    main()