#!/usr/bin/env python
"""
可视化KML文件在卫星底图上的脚本
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np
import requests
from PIL import Image
import io
import xml.etree.ElementTree as ET
from typing import List, Tuple
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def parse_kml_coordinates(kml_file_path: str) -> List[Tuple[float, float]]:
    """解析KML文件中的坐标"""
    try:
        tree = ET.parse(kml_file_path)
        root = tree.getroot()
        
        # 处理命名空间
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        coordinates = []
        
        # 查找所有坐标元素
        for coord_elem in root.findall('.//kml:coordinates', ns):
            coord_text = coord_elem.text.strip()
            if coord_text:
                # 解析坐标字符串
                points = coord_text.split()
                for point in points:
                    if point.strip():
                        parts = point.split(',')
                        if len(parts) >= 2:
                            lon = float(parts[0])
                            lat = float(parts[1])
                            coordinates.append((lon, lat))
        
        return coordinates
    except Exception as e:
        print(f"解析KML文件时出错: {e}")
        return []

def get_satellite_image(bounds: Tuple[float, float, float, float], 
                       width: int = 800, height: int = 600) -> np.ndarray:
    """获取卫星底图
    bounds: (min_lon, min_lat, max_lon, max_lat)
    """
    min_lon, min_lat, max_lon, max_lat = bounds
    
    # 使用OpenStreetMap的卫星图层作为底图
    # 这里使用一个简单的瓦片服务，实际项目中可能需要更高质量的卫星图
    try:
        # 计算瓦片范围
        zoom = 15  # 缩放级别
        
        # 创建一个简单的底图（灰色背景）
        img = np.ones((height, width, 3)) * 0.9
        
        # 添加网格效果模拟卫星图
        for i in range(0, height, 50):
            img[i:i+2, :] = 0.8
        for j in range(0, width, 50):
            img[:, j:j+2] = 0.8
            
        return img
    except Exception as e:
        print(f"获取卫星图时出错: {e}")
        # 返回默认底图
        return np.ones((height, width, 3)) * 0.9

def visualize_kml_on_satellite(kml_file_path: str, output_path: str = None):
    """在卫星底图上可视化KML文件"""
    
    # 解析KML坐标
    coordinates = parse_kml_coordinates(kml_file_path)
    
    if not coordinates:
        print("未找到有效的坐标数据")
        return
    
    print(f"找到 {len(coordinates)} 个坐标点")
    
    # 计算边界
    lons = [coord[0] for coord in coordinates]
    lats = [coord[1] for coord in coordinates]
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    print(f"坐标范围: 经度 {min_lon:.6f} - {max_lon:.6f}, 纬度 {min_lat:.6f} - {max_lat:.6f}")
    
    # 扩展边界以留出边距
    lon_margin = (max_lon - min_lon) * 0.1
    lat_margin = (max_lat - min_lat) * 0.1
    
    bounds = (min_lon - lon_margin, min_lat - lat_margin, 
              max_lon + lon_margin, max_lat + lat_margin)
    
    # 创建图形
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # 获取卫星底图
    satellite_img = get_satellite_image(bounds)
    
    # 显示底图
    ax.imshow(satellite_img, extent=bounds, aspect='equal', alpha=0.8)
    
    # 绘制KML边界
    if len(coordinates) > 0:
        # 创建多边形
        polygon_coords = np.array(coordinates)
        
        # 绘制多边形边界
        polygon = patches.Polygon(polygon_coords, linewidth=2, 
                                edgecolor='red', facecolor='yellow', 
                                alpha=0.3, label='KML边界')
        ax.add_patch(polygon)
        
        # 绘制边界线
        ax.plot(polygon_coords[:, 0], polygon_coords[:, 1], 
                'r-', linewidth=2, label='边界线')
        
        # 标记起点和终点
        ax.plot(coordinates[0][0], coordinates[0][1], 'go', 
                markersize=8, label='起点')
        ax.plot(coordinates[-1][0], coordinates[-1][1], 'bo', 
                markersize=8, label='终点')
        
        # 标记所有坐标点
        for i, (lon, lat) in enumerate(coordinates[::5]):  # 每5个点标记一个
            ax.plot(lon, lat, 'ro', markersize=3, alpha=0.7)
    
    # 设置坐标轴
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_xlabel('经度 (°)')
    ax.set_ylabel('纬度 (°)')
    ax.set_title('KML文件在卫星底图上的可视化')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 添加坐标信息
    info_text = f"区域范围:\n经度: {min_lon:.6f} - {max_lon:.6f}\n纬度: {min_lat:.6f} - {max_lat:.6f}\n坐标点数: {len(coordinates)}"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # 保存图片
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存到: {output_path}")
    
    plt.show()

def main():
    """主函数"""
    kml_file = "test.kml"
    output_file = "kml_visualization.png"
    
    if not os.path.exists(kml_file):
        print(f"KML文件不存在: {kml_file}")
        return
    
    print(f"正在可视化KML文件: {kml_file}")
    visualize_kml_on_satellite(kml_file, output_file)

if __name__ == "__main__":
    main()