from setuptools import find_packages, setup

package_name = 'aerocue_ai'

setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],

    install_requires=[
        'setuptools',
    ],

    zip_safe=True,

    maintainer='sathwik',
    maintainer_email='sathwik@todo.todo',

    description='AeroCue AI YOLO survivor detection node',

    license='Apache-2.0',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'yolo_node = aerocue_ai.yolo_node:main',
        ],
    },
)
