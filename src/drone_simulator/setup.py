from setuptools import find_packages, setup

package_name = 'drone_simulator'

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
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sathwik',
    maintainer_email='sathwik@todo.todo',
    description='Drone movement simulator for Aerocue',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'drone_simulator = drone_simulator.drone_simulator_node:main',
        ],
    },
)
