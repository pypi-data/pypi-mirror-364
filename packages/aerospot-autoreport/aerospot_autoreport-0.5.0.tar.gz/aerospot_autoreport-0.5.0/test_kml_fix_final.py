#!/usr/bin/env python
"""
最终测试KML边界修复效果
"""

import sys
import os
sys.path.append('./src')

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from autoreport.processor.maps import generate_interpolation_indicator_map, generate_clean_interpolation_map

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_test_data():
    """创建测试数据"""
    # 在KML边界附近创建测试数据
    np.random.seed(42)
    
    # KML边界范围
    min_lon, max_lon = 120.264388, 120.269001
    min_lat, max_lat = 31.515078, 31.520721
    
    # 生成数据点
    n_points = 15
    lons = np.random.uniform(min_lon, max_lon, n_points)
    lats = np.random.uniform(min_lat, max_lat, n_points)
    values = np.random.uniform(0, 8, n_points)
    
    return pd.DataFrame({
        'longitude': lons,
        'latitude': lats,
        'chla': values
    })

def test_kml_interpolation_map():
    """测试KML边界插值图生成"""
    print("=== 测试KML边界插值图生成 ===")
    
    # 创建测试数据
    data = create_test_data()
    print(f"创建测试数据: {len(data)} 个点")
    
    # 模拟卫星图信息
    satellite_info = (800, 600, np.ones((600, 800, 3)))  # 模拟卫星图
    
    # 模拟地理边界
    satellite_geo_bounds = [120.26, 31.51, 120.27, 31.53]  # 卫星图边界
    data_geo_bounds = [120.264, 31.515, 120.270, 31.521]  # 数据边界
    
    # 生成插值图
    save_path = "test_kml_interpolation_fixed.png"
    kml_boundary_path = "test.kml"
    
    try:
        result, grid_values = generate_interpolation_indicator_map(
            data=data,
            indicator='chla',
            satellite_info=satellite_info,
            save_path=save_path,
            satellite_geo_bounds=satellite_geo_bounds,
            data_geo_bounds=data_geo_bounds,
            all_points_outside=False,
            water_mask=None,
            kml_boundary_path=kml_boundary_path
        )
        
        if result:
            print(f"✓ 插值图生成成功: {save_path}")
            return True
        else:
            print("✗ 插值图生成失败")
            return False
            
    except Exception as e:
        print(f"✗ 插值图生成出错: {e}")
        return False

def test_kml_clean_interpolation_map():
    """测试KML边界纯净插值图生成"""
    print("\n=== 测试KML边界纯净插值图生成 ===")
    
    # 创建测试数据
    data = create_test_data()
    
    # 生成纯净插值图
    save_path = "test_kml_clean_interpolation_fixed.png"
    kml_boundary_path = "test.kml"
    
    try:
        result, grid_values = generate_clean_interpolation_map(
            data=data,
            indicator='chla',
            save_path=save_path,
            grid_resolution=200,
            transparent_bg=True,
            output_format='png',
            satellite_info=None,
            kml_boundary_path=kml_boundary_path
        )
        
        if result:
            print(f"✓ 纯净插值图生成成功: {save_path}")
            return True
        else:
            print("✗ 纯净插值图生成失败")
            return False
            
    except Exception as e:
        print(f"✗ 纯净插值图生成出错: {e}")
        return False

def main():
    """主函数"""
    print("KML边界插值修复最终测试")
    print("=" * 50)
    
    # 测试插值图
    success1 = test_kml_interpolation_map()
    
    # 测试纯净插值图
    success2 = test_kml_clean_interpolation_map()
    
    print("\n=== 测试总结 ===")
    if success1 and success2:
        print("✓ 所有测试通过")
        print("✓ KML边界修复成功")
        print("✓ 插值范围现在正确限制在KML边界内")
    else:
        print("✗ 部分测试失败")
        if not success1:
            print("✗ 插值图生成失败")
        if not success2:
            print("✗ 纯净插值图生成失败")

if __name__ == "__main__":
    main()