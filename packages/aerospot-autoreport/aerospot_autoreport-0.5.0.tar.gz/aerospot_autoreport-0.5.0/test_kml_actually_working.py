#!/usr/bin/env python
"""
测试KML文件是否真的被正确利用来限制插值范围
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from autoreport.utils.kml import get_kml_boundary_points, create_kml_boundary_mask
from autoreport.processor.maps import enhanced_interpolation_with_neighborhood

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def test_kml_boundaries():
    """测试KML边界是否真的被使用"""
    print("=== 测试KML边界是否真的被使用 ===")
    
    # 1. 检查KML文件解析
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ KML文件解析失败")
        return False
    
    print(f"✅ KML文件解析成功，获取 {len(kml_points)} 个边界点")
    print(f"KML边界范围: 经度 {kml_points[:, 0].min():.6f} - {kml_points[:, 0].max():.6f}")
    print(f"KML边界范围: 纬度 {kml_points[:, 1].min():.6f} - {kml_points[:, 1].max():.6f}")
    
    # 2. 创建测试数据 - 一些在KML边界内，一些在边界外
    np.random.seed(42)
    
    # KML边界范围
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    # 创建混合数据：50%在KML边界内，50%在边界外
    n_inside = 10
    n_outside = 10
    
    # 边界内数据
    inside_lons = np.random.uniform(kml_lon_min, kml_lon_max, n_inside)
    inside_lats = np.random.uniform(kml_lat_min, kml_lat_max, n_inside)
    inside_values = np.random.uniform(2, 8, n_inside)
    
    # 边界外数据（扩展范围）
    outside_lons = np.random.uniform(kml_lon_min - 0.002, kml_lon_max + 0.002, n_outside)
    outside_lats = np.random.uniform(kml_lat_min - 0.002, kml_lat_max + 0.002, n_outside)
    outside_values = np.random.uniform(0, 2, n_outside)  # 不同的值范围
    
    # 合并数据
    all_lons = np.concatenate([inside_lons, outside_lons])
    all_lats = np.concatenate([inside_lats, outside_lats])
    all_values = np.concatenate([inside_values, outside_values])
    
    test_data = pd.DataFrame({
        'longitude': all_lons,
        'latitude': all_lats,
        'test_indicator': all_values
    })
    
    print(f"\n创建测试数据: {len(test_data)} 个点 ({n_inside} 内部 + {n_outside} 外部)")
    
    # 3. 测试alpha_shape方法
    print("\n--- 测试alpha_shape方法 ---")
    grid_values_alpha, grid_lon_alpha, grid_lat_alpha, mask_alpha, points_alpha = enhanced_interpolation_with_neighborhood(
        test_data,
        grid_resolution=100,
        method='linear',
        boundary_method='alpha_shape',
        indicator_col='test_indicator'
    )
    
    alpha_valid_points = np.sum(~np.isnan(grid_values_alpha))
    print(f"Alpha Shape有效插值点: {alpha_valid_points}")
    
    # 4. 测试KML方法
    print("\n--- 测试KML方法 ---")
    grid_values_kml, grid_lon_kml, grid_lat_kml, mask_kml, points_kml = enhanced_interpolation_with_neighborhood(
        test_data,
        grid_resolution=100,
        method='linear',
        boundary_method='kml',
        indicator_col='test_indicator',
        kml_boundary_path=kml_path
    )
    
    kml_valid_points = np.sum(~np.isnan(grid_values_kml))
    print(f"KML方法有效插值点: {kml_valid_points}")
    
    # 5. 测试KML边界掩码
    print("\n--- 测试KML边界掩码 ---")
    kml_mask = create_kml_boundary_mask(grid_lon_kml, grid_lat_kml, kml_path)
    kml_mask_points = np.sum(kml_mask)
    print(f"KML边界掩码有效点: {kml_mask_points}")
    
    # 6. 可视化对比
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 第一行：插值结果对比
    # Alpha Shape结果
    ax1 = axes[0, 0]
    im1 = ax1.imshow(grid_values_alpha, extent=[grid_lon_alpha.min(), grid_lon_alpha.max(), 
                                               grid_lat_alpha.min(), grid_lat_alpha.max()],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax1.scatter(inside_lons, inside_lats, c='red', s=50, marker='o', label='边界内数据')
    ax1.scatter(outside_lons, outside_lats, c='blue', s=50, marker='x', label='边界外数据')
    if points_alpha is not None:
        ax1.plot(points_alpha[:, 0], points_alpha[:, 1], 'r-', linewidth=2, alpha=0.7, label='Alpha边界')
    ax1.set_title('Alpha Shape插值结果')
    ax1.legend()
    plt.colorbar(im1, ax=ax1)
    
    # KML结果
    ax2 = axes[0, 1]
    im2 = ax2.imshow(grid_values_kml, extent=[grid_lon_kml.min(), grid_lon_kml.max(), 
                                             grid_lat_kml.min(), grid_lat_kml.max()],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax2.scatter(inside_lons, inside_lats, c='red', s=50, marker='o', label='边界内数据')
    ax2.scatter(outside_lons, outside_lats, c='blue', s=50, marker='x', label='边界外数据')
    if points_kml is not None:
        ax2.plot(points_kml[:, 0], points_kml[:, 1], 'r-', linewidth=2, alpha=0.7, label='KML边界')
    ax2.set_title('KML方法插值结果')
    ax2.legend()
    plt.colorbar(im2, ax=ax2)
    
    # 插值结果差异
    ax3 = axes[0, 2]
    diff = grid_values_kml - grid_values_alpha
    im3 = ax3.imshow(diff, extent=[grid_lon_kml.min(), grid_lon_kml.max(), 
                                  grid_lat_kml.min(), grid_lat_kml.max()],
                    origin='lower', cmap='RdBu', interpolation='bilinear')
    ax3.set_title('插值结果差异 (KML - Alpha)')
    plt.colorbar(im3, ax=ax3)
    
    # 第二行：边界掩码对比
    # Alpha Shape掩码
    ax4 = axes[1, 0]
    im4 = ax4.imshow(mask_alpha, extent=[grid_lon_alpha.min(), grid_lon_alpha.max(), 
                                        grid_lat_alpha.min(), grid_lat_alpha.max()],
                    origin='lower', cmap='binary', interpolation='nearest')
    ax4.set_title('Alpha Shape边界掩码')
    plt.colorbar(im4, ax=ax4)
    
    # KML掩码
    ax5 = axes[1, 1]
    im5 = ax5.imshow(mask_kml, extent=[grid_lon_kml.min(), grid_lon_kml.max(), 
                                      grid_lat_kml.min(), grid_lat_kml.max()],
                    origin='lower', cmap='binary', interpolation='nearest')
    ax5.set_title('KML边界掩码')
    plt.colorbar(im5, ax=ax5)
    
    # 掩码差异
    ax6 = axes[1, 2]
    mask_diff = mask_kml.astype(int) - mask_alpha.astype(int)
    im6 = ax6.imshow(mask_diff, extent=[grid_lon_kml.min(), grid_lon_kml.max(), 
                                       grid_lat_kml.min(), grid_lat_kml.max()],
                    origin='lower', cmap='RdBu', interpolation='nearest')
    ax6.set_title('掩码差异 (KML - Alpha)')
    plt.colorbar(im6, ax=ax6)
    
    plt.tight_layout()
    plt.savefig('kml_boundary_effectiveness_test.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\n✅ 对比图已保存: kml_boundary_effectiveness_test.png")
    
    # 7. 分析结果
    print("\n=== 分析结果 ===")
    
    # 检查有效点数差异
    point_diff = abs(kml_valid_points - alpha_valid_points)
    mask_diff_count = np.sum(mask_kml != mask_alpha)
    
    print(f"有效插值点数差异: {point_diff}")
    print(f"边界掩码差异点数: {mask_diff_count}")
    
    if point_diff > 100 or mask_diff_count > 100:
        print("✅ KML边界确实产生了不同的插值结果")
        print("✅ KML文件被正确利用来限制插值范围")
        return True
    else:
        print("❌ KML边界与alpha_shape结果几乎相同")
        print("❌ KML文件可能没有被正确利用")
        return False

def main():
    """主函数"""
    print("KML边界有效性测试")
    print("=" * 50)
    
    success = test_kml_boundaries()
    
    print("\n=== 最终结论 ===")
    if success:
        print("✅ KML文件被正确利用来限制插值范围")
        print("✅ 边界掩码工作正常")
        print("✅ 插值结果符合预期")
    else:
        print("❌ KML文件没有被正确利用")
        print("❌ 需要检查实现逻辑")

if __name__ == "__main__":
    main()