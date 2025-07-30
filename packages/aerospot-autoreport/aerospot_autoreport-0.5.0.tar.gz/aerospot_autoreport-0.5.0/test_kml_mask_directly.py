#!/usr/bin/env python
"""
直接测试KML边界掩码是否正确工作
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import matplotlib.pyplot as plt
from autoreport.utils.kml import create_kml_boundary_mask, get_kml_boundary_points

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def test_kml_mask_directly():
    """直接测试KML边界掩码"""
    print("=== 直接测试KML边界掩码 ===")
    
    # 1. 获取KML边界点
    kml_path = "test.kml"
    kml_points = get_kml_boundary_points(kml_path)
    
    if kml_points is None:
        print("❌ 无法获取KML边界点")
        return
    
    print(f"✅ KML边界点: {len(kml_points)} 个")
    
    # 2. 创建测试网格
    kml_lon_min, kml_lon_max = kml_points[:, 0].min(), kml_points[:, 0].max()
    kml_lat_min, kml_lat_max = kml_points[:, 1].min(), kml_points[:, 1].max()
    
    print(f"KML范围: 经度 {kml_lon_min:.6f} - {kml_lon_max:.6f}")
    print(f"KML范围: 纬度 {kml_lat_min:.6f} - {kml_lat_max:.6f}")
    
    # 创建网格，稍微扩展一点以包含边界外区域
    margin = 0.001
    lon_min = kml_lon_min - margin
    lon_max = kml_lon_max + margin
    lat_min = kml_lat_min - margin
    lat_max = kml_lat_max + margin
    
    resolution = 100
    grid_lat, grid_lon = np.mgrid[lat_min:lat_max:resolution*1j, 
                                 lon_min:lon_max:resolution*1j]
    
    print(f"网格范围: 经度 {lon_min:.6f} - {lon_max:.6f}")
    print(f"网格范围: 纬度 {lat_min:.6f} - {lat_max:.6f}")
    print(f"网格大小: {grid_lon.shape}")
    
    # 3. 创建KML边界掩码
    kml_mask = create_kml_boundary_mask(grid_lon, grid_lat, kml_path)
    
    # 4. 统计掩码信息
    total_points = kml_mask.size
    valid_points = np.sum(kml_mask)
    valid_ratio = valid_points / total_points
    
    print(f"总网格点: {total_points}")
    print(f"KML内有效点: {valid_points}")
    print(f"KML覆盖率: {valid_ratio:.2%}")
    
    # 5. 可视化结果
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 显示KML边界
    ax1 = axes[0]
    ax1.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax1.fill(kml_points[:, 0], kml_points[:, 1], alpha=0.3, color='red', label='KML区域')
    ax1.set_xlim(lon_min, lon_max)
    ax1.set_ylim(lat_min, lat_max)
    ax1.set_title('KML边界定义')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('经度')
    ax1.set_ylabel('纬度')
    
    # 显示边界掩码
    ax2 = axes[1]
    im2 = ax2.imshow(kml_mask, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='RdYlBu', interpolation='nearest')
    ax2.plot(kml_points[:, 0], kml_points[:, 1], 'k-', linewidth=2, label='KML边界')
    ax2.set_title('KML边界掩码')
    ax2.set_xlabel('经度')
    ax2.set_ylabel('纬度')
    ax2.legend()
    plt.colorbar(im2, ax=ax2)
    
    # 显示掩码边界
    ax3 = axes[2]
    # 创建一个带有边界的示例插值数据
    test_values = np.ones_like(grid_lon) * 5.0  # 基础值
    test_values[~kml_mask] = np.nan  # 边界外设为NaN
    
    im3 = ax3.imshow(test_values, extent=[lon_min, lon_max, lat_min, lat_max],
                    origin='lower', cmap='viridis', interpolation='bilinear')
    ax3.plot(kml_points[:, 0], kml_points[:, 1], 'r-', linewidth=2, label='KML边界')
    ax3.set_title('应用KML掩码后的效果')
    ax3.set_xlabel('经度')
    ax3.set_ylabel('纬度')
    ax3.legend()
    plt.colorbar(im3, ax=ax3)
    
    plt.tight_layout()
    plt.savefig('kml_mask_direct_test.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\n✅ 测试图片已保存: kml_mask_direct_test.png")
    
    # 6. 验证掩码是否正确
    print("\n=== 验证掩码正确性 ===")
    
    # 检查边界点是否在掩码内
    from matplotlib.path import Path
    kml_path_obj = Path(kml_points)
    
    # 随机选择一些网格点进行验证
    test_indices = np.random.choice(total_points, min(1000, total_points), replace=False)
    grid_points = np.column_stack((grid_lon.ravel(), grid_lat.ravel()))
    test_points = grid_points[test_indices]
    
    # 使用matplotlib Path检查
    path_results = kml_path_obj.contains_points(test_points)
    mask_results = kml_mask.ravel()[test_indices]
    
    # 比较结果
    matches = np.sum(path_results == mask_results)
    accuracy = matches / len(test_indices)
    
    print(f"掩码准确率: {accuracy:.2%} ({matches}/{len(test_indices)})")
    
    if accuracy > 0.95:
        print("✅ KML边界掩码工作正常")
        return True
    else:
        print("❌ KML边界掩码有问题")
        return False

def main():
    """主函数"""
    print("KML边界掩码直接测试")
    print("=" * 50)
    
    success = test_kml_mask_directly()
    
    print("\n=== 最终结论 ===")
    if success:
        print("✅ KML边界掩码功能正常")
        print("✅ 能够正确限制插值范围")
    else:
        print("❌ KML边界掩码有问题")
        print("❌ 需要修复实现")

if __name__ == "__main__":
    main()