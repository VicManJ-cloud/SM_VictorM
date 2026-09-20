from setuptools import find_packages, setup

package_name = 'basics'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vick',
    maintainer_email='victor.itam.mx@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'velocity_publisher.py = basics.velocity_publisher:main',
            'velocity_subscriber.py = basics.velocity_subscriber:main',
            'velocity_turtle_pub.py = basics.velocity_turtle_pub:main',
            'velocity_turtle_subs.py = basics.velocity_turtle_subs:main',
            'led_blink.py = basics.led_blink:main',
            'serial_bridge.py = basics.serial_bridge:main',
            'analog_serial_pub.py = basics.analog_serial_pub:main',
            'analog_subs.py = basics.analog_subs:main',
            'joystick_serial_pub.py = basics.joystick_serial_pub:main',
            'turtle_controller.py = basics.turtle_controller:main',
        ],
    },
)
