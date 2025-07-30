#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SVG Water Quality Generator 统一接口

这是水质数据处理和SVG生成的统一入口点，提供命令行和编程接口。
"""

import argparse
import json
import logging
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# 尝试相对导入，失败则使用绝对导入
try:
    from .config.indicators import WATER_QUALITY_INDICATORS, get_indicator_info
    from .core.downloader import ResourceDownloader
    from .core.extractor import ZipExtractor
    from .data.parser import DataParser
    from .data.standardizer import DataStandardizer
    from .data.validator import DataValidator
    from .interpolation.enhanced_interpolation import (
        enhanced_interpolation_with_boundary,
    )
    from .utils.logger import setup_logging
    from .visualization.svg_generator import create_clean_interpolation_svg
except ImportError:
    # 开发模式下的绝对导入
    from config.indicators import get_indicator_info
    from core.downloader import ResourceDownloader
    from core.extractor import ZipExtractor
    from data.parser import DataParser
    from data.standardizer import DataStandardizer
    from data.validator import DataValidator
    from interpolation.enhanced_interpolation import (
        enhanced_interpolation_with_boundary,
    )
    from utils.logger import setup_logging
    from visualization.svg_generator import create_clean_interpolation_svg

logger = logging.getLogger(__name__)


class WaterQualityProcessor:
    """水质数据处理器"""

    def __init__(
        self,
        output_dir: str = "./outputs",
        temp_dir: Optional[str] = None,
        grid_resolution: int = 300,
        log_level: str = "INFO",
    ):
        """
        初始化水质数据处理器

        Args:
            output_dir: 输出目录
            temp_dir: 临时目录
            grid_resolution: 网格分辨率
            log_level: 日志级别
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if temp_dir is None:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="water_quality_"))
        else:
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.grid_resolution = grid_resolution

        # 初始化组件
        self.downloader = ResourceDownloader(str(self.temp_dir))
        self.extractor = ZipExtractor(str(self.temp_dir))
        self.parser = DataParser()
        self.standardizer = DataStandardizer()
        self.validator = DataValidator()

        # 设置日志
        setup_logging(log_level)
        logger.info(f"水质数据处理器已初始化，输出目录: {self.output_dir}")

    def process_from_oss_zip(
        self,
        zip_url: str,
        colormap: str = "jet",
        boundary_method: str = "alpha_shape",
        interpolation_method: str = "universal_kriging",
        transparent_bg: bool = True,
        figsize: Tuple[float, float] = (10, 8),
    ) -> Dict[str, Any]:
        """
        从OSS ZIP文件处理水质数据并生成SVG

        Args:
            zip_url: OSS ZIP文件URL
            colormap: 颜色映射方案
            boundary_method: 边界检测方法
            interpolation_method: 插值方法
            transparent_bg: 是否使用透明背景
            figsize: 图形尺寸

        Returns:
            处理结果字典，包含SVG文件路径和经纬度边界信息
        """
        try:
            logger.info(f"开始处理OSS ZIP文件: {zip_url}")

            # 1. 下载ZIP文件
            zip_path = self.downloader.download(zip_url)
            if not zip_path:
                raise ValueError("ZIP文件下载失败")

            # 2. 解压文件
            extract_dir = self.extractor.extract(zip_path)
            if not extract_dir:
                raise ValueError("ZIP文件解压失败")

            # 3. 解析数据
            df = self.parser.parse_uav_data(extract_dir)
            if df is None:
                raise ValueError("数据解析失败")

            # 4. 标准化数据
            df, mapping_info = self.standardizer.standardize_dataframe(df)

            # 5. 验证数据
            validation_result = self.validator.validate_dataframe(df)
            if not validation_result["is_valid"]:
                logger.warning(f"数据验证警告: {validation_result['warnings']}")

            # 6. 获取所有可用指标
            available_indicators = self._get_available_indicators(df)
            logger.info(f"可用指标: {available_indicators}")

            # 7. 为每个指标生成SVG
            results = {}
            for indicator in available_indicators:
                svg_result = self._generate_svg_for_indicator(
                    df,
                    indicator,
                    colormap,
                    boundary_method,
                    interpolation_method,
                    transparent_bg,
                    figsize,
                )
                results[indicator] = svg_result

            logger.info(f"完成处理，共生成{len(results)}个SVG文件")
            return results

        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
            raise
        finally:
            # 清理临时文件
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

    def _get_available_indicators(self, df: pd.DataFrame) -> List[str]:
        """获取数据中可用的水质指标"""
        available = []

        # 排除坐标列
        coord_columns = ["index", "longitude", "latitude"]
        indicator_columns = [col for col in df.columns if col not in coord_columns]

        # 检查每个指标列是否有有效数据
        for indicator in indicator_columns:
            # 检查是否有有效数据
            has_valid_data = not df[indicator].isna().all()
            if has_valid_data:
                # 检查数据类型是否为数值型
                try:
                    # 尝试转换为数值型以验证数据有效性
                    numeric_data = pd.to_numeric(df[indicator], errors="coerce")
                    if not numeric_data.isna().all():
                        available.append(indicator)
                        logger.info(f"发现可用指标: {indicator}")
                    else:
                        logger.warning(f"指标 {indicator} 无法转换为数值型，跳过")
                except Exception as e:
                    logger.warning(f"指标 {indicator} 数据验证失败: {str(e)}")

        logger.info(f"总共发现 {len(available)} 个可用指标: {available}")
        return available

    def _generate_svg_for_indicator(
        self,
        df: pd.DataFrame,
        indicator: str,
        colormap: str,
        boundary_method: str,
        interpolation_method: str,
        transparent_bg: bool,
        figsize: Tuple[float, float],
    ) -> Dict[str, Any]:
        """为单个指标生成SVG"""
        try:
            logger.info(f"开始为指标 {indicator} 生成SVG")

            # 过滤有效数据
            valid_data = df[["longitude", "latitude", indicator]].dropna()
            if len(valid_data) < 3:
                logger.warning(f"指标 {indicator} 的有效数据点不足3个，跳过")
                return None

            # 增强插值
            interpolated_data, grid_x, grid_y, mask, boundary_points = (
                enhanced_interpolation_with_boundary(
                    data=valid_data,
                    indicator_col=indicator,
                    grid_resolution=self.grid_resolution,
                    method=interpolation_method,
                    boundary_method=boundary_method,
                )
            )

            # 计算经纬度边界信息
            bounds_info = self._calculate_bounds_info(grid_x, grid_y, mask)

            # 🎯 计算原始数据范围，确保与AutoReportV3一致
            original_min = float(valid_data[indicator].min())
            original_max = float(valid_data[indicator].max())
            value_range = (original_min, original_max)
            
            # 🔍 对比插值数据与原始数据范围差异
            valid_interpolated = interpolated_data[~np.isnan(interpolated_data)]
            if len(valid_interpolated) > 0:
                interp_min = float(valid_interpolated.min())
                interp_max = float(valid_interpolated.max())
                logger.info(f"原始数据范围: [{original_min:.3f}, {original_max:.3f}]")
                logger.info(f"插值数据范围: [{interp_min:.3f}, {interp_max:.3f}]")
                if abs(interp_min - original_min) > 0.1 or abs(interp_max - original_max) > 0.1:
                    logger.warning(f"插值扩展了数据范围！原始vs插值: [{original_min:.3f}, {original_max:.3f}] vs [{interp_min:.3f}, {interp_max:.3f}]")
            else:
                logger.warning("插值数据全为NaN")
            
            logger.info(f"✅ 使用原始数据范围作为SVG colorbar（与AutoReportV3一致）")

            # 生成SVG文件
            svg_filename = f"{indicator}_heatmap.svg"
            svg_path = self.output_dir / svg_filename

            success = create_clean_interpolation_svg(
                grid_values=interpolated_data,
                grid_x=grid_x,
                grid_y=grid_y,
                save_path=str(svg_path),
                title=None,  # 纯净SVG不包含标题
                colormap=colormap,
                figsize=figsize,
                transparent_bg=transparent_bg,
                value_range=value_range,  # 🎯 传递原始数据范围
            )

            if not success:
                logger.error(f"SVG生成失败: {indicator}")
                return None

            # 生成边界信息文件
            bounds_filename = f"{indicator}_bounds.json"
            bounds_path = self.output_dir / bounds_filename
            with open(bounds_path, "w", encoding="utf-8") as f:
                json.dump(bounds_info, f, indent=2, ensure_ascii=False)

            # 获取指标信息（支持未知指标）
            indicator_info = get_indicator_info(indicator)

            result = {
                "svg_path": str(svg_path),
                "bounds_path": str(bounds_path),
                "bounds_info": bounds_info,
                "indicator_name": indicator_info["name"],
                "unit": indicator_info["unit"],
                "data_points": len(valid_data),
                "min_value": float(valid_data[indicator].min()),
                "max_value": float(valid_data[indicator].max()),
                "mean_value": float(valid_data[indicator].mean()),
            }

            logger.info(f"指标 {indicator} 的SVG生成完成: {svg_path}")
            return result

        except Exception as e:
            logger.error(f"生成指标 {indicator} 的SVG时发生错误: {str(e)}")
            return None

    def _calculate_bounds_info(
        self, grid_x: np.ndarray, grid_y: np.ndarray, mask: np.ndarray
    ) -> Dict[str, Any]:
        """计算经纬度边界信息用于地图叠加"""
        # 找到有效区域的边界
        valid_indices = np.where(mask)

        if len(valid_indices[0]) == 0:
            # 如果没有有效区域，使用整个网格
            min_lat, max_lat = grid_y.min(), grid_y.max()
            min_lon, max_lon = grid_x.min(), grid_x.max()
        else:
            # 使用有效区域计算边界
            valid_y_coords = grid_y[valid_indices]
            valid_x_coords = grid_x[valid_indices]

            min_lat = float(valid_y_coords.min())
            max_lat = float(valid_y_coords.max())
            min_lon = float(valid_x_coords.min())
            max_lon = float(valid_x_coords.max())

        # 计算中心点
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2

        # 计算范围
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon

        bounds_info = {
            "geographic_bounds": {
                "min_longitude": min_lon,
                "max_longitude": max_lon,
                "min_latitude": min_lat,
                "max_latitude": max_lat,
                "center_longitude": center_lon,
                "center_latitude": center_lat,
                "longitude_range": lon_range,
                "latitude_range": lat_range,
            },
            "grid_info": {
                "grid_resolution": self.grid_resolution,
                "grid_width": grid_x.shape[1],
                "grid_height": grid_y.shape[0],
                "valid_pixels": int(np.sum(mask)),
            },
            "projection_info": {
                "coordinate_system": "WGS84",
                "units": "degrees",
                "note": "经纬度坐标，适用于Web地图叠加",
            },
        }

        return bounds_info

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，清理临时文件"""
        if hasattr(self, "temp_dir") and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="SVG Water Quality Generator - 水质数据SVG热力图生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
                使用示例:
                python interface.py --zip-url "https://example.com/data.zip" --output-dir "./outputs"
                python interface.py --zip-url "/path/to/config.json" --colormap "water_quality" --resolution 600
                echo "https://example.com/data.zip" | python interface.py --output-dir "./outputs"
                echo "/path/to/config.json" | python interface.py --output-dir "./outputs"
                
                JSON配置文件格式:
                {
                    "file_url": "https://example.com/data.zip",
                    "description": "数据描述信息（可选）"
                }
                
                Windows用户注意：
                如果URL包含&符号，请使用标准输入方式，或用双引号包围URL：
                echo https://example.com/data.zip?param1=value1^&param2=value2 | python interface.py
                python interface.py --zip-url "https://example.com/data.zip?param1=value1&param2=value2"
        """,
    )

    # ZIP URL参数（可选，如果不提供则从标准输入读取）
    parser.add_argument(
        "--zip-url",
        required=False,
        help="OSS ZIP文件下载URL或JSON配置文件路径（如果不提供则从标准输入读取）",
    )

    # 可选参数
    parser.add_argument(
        "--output-dir", default="./outputs", help="输出目录 (默认: ./outputs)"
    )

    parser.add_argument(
        "--resolution", type=int, default=300, help="网格分辨率 (默认: 300, 与AutoReportV3一致)"
    )

    parser.add_argument(
        "--colormap",
        default="jet",
        choices=["jet", "water_quality", "viridis", "RdYlBu_r"],
        help="颜色映射方案 (默认: jet)",
    )

    parser.add_argument(
        "--boundary-method",
        default="alpha_shape",
        choices=["alpha_shape", "convex_hull", "density_based"],
        help="边界检测方法 (默认: alpha_shape)",
    )

    parser.add_argument(
        "--interpolation-method",
        default="universal_kriging",
        choices=["universal_kriging", "ordinary_kriging_spherical", "ordinary_kriging_exponential"],
        help="插值方法 (默认: universal_kriging高精度泛克里金插值)",
    )

    parser.add_argument(
        "--figsize",
        nargs=2,
        type=float,
        default=[12, 10],
        help="图形尺寸 width height (默认: 12 10)",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别 (默认: INFO)",
    )

    parser.add_argument("--no-transparent", action="store_true", help="禁用透明背景")

    return parser.parse_args()


def read_zip_url_from_stdin():
    """从标准输入读取ZIP文件URL或JSON文件路径"""
    try:
        # 检查是否有标准输入数据
        if sys.stdin.isatty():
            return None

        # 读取第一行作为URL或文件路径
        input_data = sys.stdin.readline().strip()
        if not input_data:
            return None
        return resolve_zip_url(input_data)
    except Exception as e:
        logger.error(f"从标准输入读取ZIP URL失败: {str(e)}")
        return None


def resolve_zip_url(input_data: str) -> Optional[str]:
    """解析输入数据，获取ZIP文件下载URL

    Args:
        input_data: 输入数据，可能是URL或JSON文件路径

    Returns:
        解析后的ZIP文件下载URL
    """
    try:
        # 检查是否为HTTP/HTTPS URL
        if input_data.startswith(("http://", "https://")):
            logger.info(f"检测到直接下载链接: {input_data}")
            return input_data

        # 检查是否为文件路径
        input_path = Path(input_data)

        if input_path.exists() and input_path.is_file():
            logger.info(f"检测到文件路径: {input_data}")

            # 尝试读取JSON文件
            try:
                with open(input_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                # 检查是否包含 file_url 键
                if "file_url" in json_data:
                    file_url = json_data["file_url"]
                    logger.info(f"从JSON文件读取到下载链接: {file_url}")
                    return file_url
                else:
                    logger.error(
                        f"JSON文件中缺少 'file_url' 键: {list(json_data.keys())}"
                    )
                    return None

            except json.JSONDecodeError as e:
                logger.error(f"JSON文件格式错误: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"读取JSON文件失败: {str(e)}")
                return None

        # 如果不是URL也不是有效文件路径，尝试当作URL处理
        logger.warning(f"输入数据格式不明确，尝试当作URL处理: {input_data}")
        return input_data

    except Exception as e:
        logger.error(f"解析输入数据失败: {str(e)}")
        return None


def log_results(results: Dict[str, Any]):
    """记录处理结果到日志"""
    logger.info("=== 处理结果 ===")

    if not results:
        logger.warning("没有生成任何结果")
        return

    for indicator, result in results.items():
        if result:
            logger.info(f"指标: {result['indicator_name']} ({indicator})")
            logger.info(f"   SVG文件: {result['svg_path']}")
            logger.info(f"   边界文件: {result['bounds_path']}")
            logger.info(f"   数据点数: {result['data_points']}")
            logger.info(
                f"   数值范围: {result['min_value']:.2f} - {result['max_value']:.2f} {result['unit']}"
            )
            logger.info(f"   平均值: {result['mean_value']:.2f} {result['unit']}")

            bounds = result["bounds_info"]["geographic_bounds"]
            logger.info(
                f"   经度范围: {bounds['min_longitude']:.6f} - {bounds['max_longitude']:.6f}"
            )
            logger.info(
                f"   纬度范围: {bounds['min_latitude']:.6f} - {bounds['max_latitude']:.6f}"
            )
            logger.info(
                f"   中心点: ({bounds['center_longitude']:.6f}, {bounds['center_latitude']:.6f})"
            )
        else:
            logger.error(f"指标 {indicator} 处理失败")


def format_output_dict(results: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """格式化输出字典"""
    output = {}
    for indicator, result in results.items():
        if result and result.get("svg_path") and result.get("bounds_path"):
            # 转换为绝对路径
            svg_abs_path = str(Path(result["svg_path"]).resolve())
            coords = result.get("bounds_info")['geographic_bounds']
            min_long = coords["min_longitude"]
            max_long = coords["max_longitude"]
            min_lat = coords["min_latitude"]
            max_lat = coords["max_latitude"]

            # 修正：西北(w_n)、东北(e_n)、西南(w_s)、东南(e_s)的经纬度顺序
            w_n = f"{min_long},{max_lat}"  # 西北角
            e_n = f"{max_long},{max_lat}"  # 东北角
            w_s = f"{min_long},{min_lat}"  # 西南角
            e_s = f"{max_long},{min_lat}"  # 东南角
            output[indicator] = [svg_abs_path, w_n, e_n, w_s, e_s]
    return output


def main():
    """主入口函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()

        # 创建时间戳文件夹（提前创建以便保存日志）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_output_dir = Path(args.output_dir) / timestamp
        timestamped_output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建输出目录: {timestamped_output_dir}")

        # 配置日志文件保存到时间戳文件夹
        log_file_path = timestamped_output_dir / "processing.log"

        # 添加文件日志处理器
        try:
            from .utils.logger import add_file_handler
        except ImportError:
            from utils.logger import add_file_handler
        add_file_handler(log_file_path, level=args.log_level)
        logger.info(f"日志文件保存至: {log_file_path}")

        # 获取ZIP URL：优先使用命令行参数，否则从标准输入读取
        zip_url = None
        if args.zip_url:
            zip_url = resolve_zip_url(args.zip_url)
        else:
            zip_url = read_zip_url_from_stdin()

        if not zip_url:
            logger.error(
                "必须提供ZIP文件URL或JSON文件路径，可以通过--zip-url参数或标准输入提供"
            )
            logger.error("使用示例:")
            logger.error(
                "  python interface.py --zip-url 'https://example.com/data.zip'"
            )
            logger.error("  python interface.py --zip-url '/path/to/config.json'")
            logger.error("  echo 'https://example.com/data.zip' | python interface.py")
            logger.error("  echo '/path/to/config.json' | python interface.py")
            return 1

        # 验证URL格式
        if not zip_url.startswith(("http://", "https://")):
            logger.error(f"无效的URL格式: {zip_url}")
            return 1

        logger.info(f"正在处理ZIP文件: {zip_url}")

        # 使用水质数据处理器（不要重复设置日志）
        # 临时保存当前日志处理器
        current_handlers = logging.getLogger().handlers[:]

        with WaterQualityProcessor(
            output_dir=str(timestamped_output_dir),
            grid_resolution=args.resolution,
            log_level=args.log_level,
        ) as processor:
            # 恢复文件日志处理器
            for handler in current_handlers:
                if handler not in logging.getLogger().handlers:
                    logging.getLogger().addHandler(handler)

            # 处理数据
            results = processor.process_from_oss_zip(
                zip_url=zip_url,
                colormap=args.colormap,
                boundary_method=args.boundary_method,
                interpolation_method=args.interpolation_method,
                transparent_bg=not args.no_transparent,
                figsize=tuple(args.figsize),
            )

            # 记录详细结果到日志
            log_results(results)

            # 输出Python字典格式结果
            output_dict = format_output_dict(results)
            import json

            print(json.dumps(output_dict, indent=2, ensure_ascii=False))

            # 返回成功状态
            return 0

    except KeyboardInterrupt:
        error_msg = "用户中断处理"
        logger.error(error_msg)
        if "log_file_path" in locals():
            print(f"程序被用户中断。详细日志请查看: {log_file_path}")
        return 1
    except Exception as e:
        import traceback

        error_msg = f"程序崩溃: {str(e)}"
        traceback_str = traceback.format_exc()

        # 记录详细的崩溃信息到日志
        logger.error("=" * 50)
        logger.error("程序发生致命错误，即将退出")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("完整错误堆栈:")
        logger.error(traceback_str)
        logger.error("=" * 50)

        # 确保日志写入文件
        for handler in logging.getLogger().handlers:
            if hasattr(handler, "flush"):
                handler.flush()

        # 向用户提供日志查看指引
        if "log_file_path" in locals():
            print(f"程序运行失败: {str(e)}")
            print(f"详细错误信息和堆栈跟踪已保存到日志文件: {log_file_path}")
            print("请检查日志文件以获取完整的错误诊断信息。")
        else:
            print(f"程序运行失败: {str(e)}")
            print("无法访问日志文件，请检查输出目录权限。")

        return 1


if __name__ == "__main__":
    sys.exit(main())
