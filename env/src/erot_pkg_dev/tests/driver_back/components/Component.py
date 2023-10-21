import argparse
from RoPy import PystLink


class Singleton (type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ComponentFactory(metaclass=Singleton):
    link = None

    def __init__(self, *args, **kwargs):
        super(ComponentFactory, self).__init__()
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", help="socket Port", type=int, default="1234")
        parser.add_argument("--ip", help="socket ip", type=str, default="127.0.0.1")
        opts, unknown = parser.parse_known_args(args)
        ComponentFactory.set_link(ip=opts.ip, port=opts.port)

    @classmethod
    def generate_component(cls, component_type, *args, **kwargs):
        if not issubclass(component_type, Component):
            raise TypeError(f"{component_type.__name__} is not subclass of {Component.__name__}")
        return component_type(ComponentFactory.link, *args, **kwargs)

    @classmethod
    def set_link(cls, ip, port):
        if ComponentFactory.link:
            print("Detect existing link in factory, drop link creation and use existing link")
        else:
            ComponentFactory.link = PystLink(host=ip, port=port)


class Component:
    def __init__(self, link, *args, **kwargs):
        super(Component, self).__init__()
        self.link = link
