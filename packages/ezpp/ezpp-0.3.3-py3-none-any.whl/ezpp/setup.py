
#!/usr/bin/env python3

from setuptools import setup, find_packages
import re
from pathlib import Path


def get_pkg_info(package_name, key):
    """更健壮的版本获取函数"""
    # 1. 确定文件路径
    package_path = Path(__file__).resolve().parent / package_name
    init_file = package_path / "__init__.py"

    # 2. 检查文件是否存在
    if not init_file.exists():
        raise FileNotFoundError(f"无法找到 {init_file}")

    # 3. 读取文件内容
    content = init_file.read_text(encoding="utf-8")

    # 4. 使用正则表达式匹配版本号
    version_match = re.search(
        rf"^{key}\s*=\s*['\"]([^'\"]*)['\"]",
        content,
        re.MULTILINE
    )

    # 5. 处理匹配结果
    if version_match:
        return version_match.group(1)

    # 6. 尝试替代匹配模式
    version_match = re.search(
        r"^VERSION\s*=\s*\(([^)]*)\)",
        content,
        re.MULTILINE
    )

    if version_match:
        # 转换元组格式 (1, 2, 3) -> "1.2.3"
        version_tuple = eval(version_match.group(1))
        return ".".join(map(str, version_tuple))

    # 7. 所有尝试失败
    raise RuntimeError(f"无法在 {init_file} 中提取版本号")


def get_title(package_name):
    """从包的 __init__.py 文件中获取标题"""
    return get_pkg_info(package_name, "__title__")


def get_version(package_name):
    """从包的 __init__.py 文件中获取版本号"""
    return get_pkg_info(package_name, "__version__")


setup(
    name=get_title("ezpp"),          # 项目名称
    version=get_version("ezpp"),                  # 初始版本
    description="Your project description",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/your-project",

    # 包发现与包含
    packages=find_packages(),         # 自动发现所有包
    # 或者手动指定包:
    # packages=["your_package", "your_package.submodule"],

    # 依赖管理
    install_requires=[
        "requests>=2.25.1",
        "Pillow>=9.0.0",
    ],

    # 可选依赖
    extras_require={
        "dev": ["pytest>=6.0", "flake8", "black"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },

    # 入口点（命令行工具）
    entry_points={
        "console_scripts": [
            "your-command = your_package.cli:main",
        ],
    },

    # 分类信息（PyPI 分类）
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],

    # 许可证
    license="MIT",

    # Python 版本要求
    python_requires=">=3.8",
)
