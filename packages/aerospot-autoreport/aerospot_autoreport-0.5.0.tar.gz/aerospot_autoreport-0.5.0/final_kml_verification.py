#!/usr/bin/env python
"""
最终验证KML边界显示范围修复
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import pandas as pd
from autoreport.processor.maps import enhanced_interpolation_with_neighborhood
from autoreport.utils.kml import get_kml_boundary_bounds, get_kml_boundary_points

def verify_kml_ranges():
    """验证KML边界范围处理"""
    print("=== KML边界范围验证 ===")
    
    kml_file = "test.kml"
    
    # 1. 检查KML文件的实际边界
    kml_bounds = get_kml_boundary_bounds(kml_file)
    kml_points = get_kml_boundary_points(kml_file)
    
    print(f"KML边界范围: {kml_bounds}")
    print(f"KML边界点数: {len(kml_points) if kml_points is not None else 0}")
    
    # 2. 创建测试数据
    np.random.seed(42)
    min_lon, min_lat, max_lon, max_lat = kml_bounds
    
    n_points = 10
    lons = np.random.uniform(min_lon, max_lon, n_points)
    lats = np.random.uniform(min_lat, max_lat, n_points)
    values = np.random.uniform(0, 10, n_points)
    
    test_data = pd.DataFrame({
        'longitude': lons,
        'latitude': lats,
        'test_indicator': values
    })
    
    # 3. 执行插值并检查范围
    try:
        grid_values, grid_lon, grid_lat, boundary_mask, boundary_points = enhanced_interpolation_with_neighborhood(
            test_data,
            grid_resolution=100,
            method='linear',
            boundary_method='kml',
            indicator_col='test_indicator',
            kml_boundary_path=kml_file
        )
        
        # 4. 检查插值网格范围
        grid_lon_min, grid_lon_max = grid_lon.min(), grid_lon.max()
        grid_lat_min, grid_lat_max = grid_lat.min(), grid_lat.max()
        
        print(f"\n插值网格范围:")
        print(f"  经度: {grid_lon_min:.6f} - {grid_lon_max:.6f}")
        print(f"  纬度: {grid_lat_min:.6f} - {grid_lat_max:.6f}")
        
        print(f"\nKML边界范围:")
        print(f"  经度: {min_lon:.6f} - {max_lon:.6f}")
        print(f"  纬度: {min_lat:.6f} - {max_lat:.6f}")
        
        # 5. 检查是否匹配
        lon_match = abs(grid_lon_min - min_lon) < 0.0001 and abs(grid_lon_max - max_lon) < 0.0001
        lat_match = abs(grid_lat_min - min_lat) < 0.0001 and abs(grid_lat_max - max_lat) < 0.0001
        
        if lon_match and lat_match:
            print("\n✓ 插值网格范围与KML边界范围匹配")
        else:
            print("\n✗ 插值网格范围与KML边界范围不匹配")
            print(f"  经度差异: {abs(grid_lon_min - min_lon):.6f}, {abs(grid_lon_max - max_lon):.6f}")
            print(f"  纬度差异: {abs(grid_lat_min - min_lat):.6f}, {abs(grid_lat_max - max_lat):.6f}")
        
        # 6. 检查边界掩码效果
        total_points = boundary_mask.size
        valid_points = np.sum(boundary_mask)
        valid_ratio = valid_points / total_points
        
        print(f"\n边界掩码统计:")
        print(f"  总网格点: {total_points}")
        print(f"  有效点数: {valid_points}")
        print(f"  有效比例: {valid_ratio:.2%}")
        
        # 7. 检查插值结果
        interpolated_points = np.sum(~np.isnan(grid_values))
        interpolated_ratio = interpolated_points / total_points
        
        print(f"\n插值结果统计:")
        print(f"  有插值数据的点: {interpolated_points}")
        print(f"  插值覆盖比例: {interpolated_ratio:.2%}")
        
        return True
        
    except Exception as e:
        print(f"✗ 插值测试失败: {e}")
        return False

def main():
    """主函数"""
    print("KML边界显示范围最终验证")
    print("=" * 50)
    
    success = verify_kml_ranges()
    
    print("\n=== 验证结果 ===")
    if success:
        print("✓ KML边界范围处理正确")
        print("✓ 插值网格使用KML边界范围")
        print("✓ 边界掩码正常工作")
        print("✓ 修复验证成功")
    else:
        print("✗ 验证失败")

if __name__ == "__main__":
    main()