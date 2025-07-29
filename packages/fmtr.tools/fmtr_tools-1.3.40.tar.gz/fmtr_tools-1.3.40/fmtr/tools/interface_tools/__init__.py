from fmtr.tools.import_tools import MissingExtraMockModule

try:
    from fmtr.tools.interface_tools.interface_tools import Interface, update, progress
    from fmtr.tools.interface_tools import controls
    from fmtr.tools.interface_tools.context import Context
except ImportError as exception:
    Interface = update = progress = controls = MissingExtraMockModule('interface', exception)
