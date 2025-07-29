from setuptools import setup, find_packages

setup(
    name='netdecom',
    version='0.0.5.2',
    description='Dimensionality Reduction and Decomposition of Undirected Graph Models and Bayesian Networks',
    author='Hugh',
    packages=find_packages(),
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    package_data={
        'netdecom.examples': ['*.txt'],  # 明确说明子模块 netdecom.examples
    },
    zip_safe=False,  # 推荐设置为 False，以便 importlib.resources 能访问文件内容
)
