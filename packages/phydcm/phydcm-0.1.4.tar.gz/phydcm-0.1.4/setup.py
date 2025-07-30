from setuptools import setup, find_packages

setup(
    # كل المعلومات الأساسية تم نقلها إلى pyproject.toml
    name="phydcm",
    version="0.1.4",
    description="A Python package for medical image analysis",
    author="PhyDCM Team",
    author_email="phydcm.team@outlook.com",
    packages=find_packages(),
    include_package_data=True,  # ضروري لتضمين ملفات json أو configs إن وجدت
    zip_safe=False,  # لأنك قد تحتاج تحميل ملفات خارجية
)
