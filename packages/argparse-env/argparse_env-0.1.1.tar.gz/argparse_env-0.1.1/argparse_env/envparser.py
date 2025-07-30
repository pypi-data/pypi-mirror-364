import argparse
import os
import sys

def boolean_type(value):
    """
    Converts a string to a boolean. Accepts true, on, 1, false, off, 0
    """
    if isinstance(value, bool):
        return value

    val = str(value).lower()
    if val in {"true", "on", "1"}:
        return True
    elif val in {"false", "off", "0"}:
        return False
    else:
        raise argparse.ArgumentTypeError(
            f"Invalid boolean value: {value}. Expected one of true/on/1 or false/off/0."
        )

def comma_separated_list(value, conv=None):
    """
    Splits a string on commas and converts each element using
    type conversation conv if provided.
    If value is already a list/tuple, returns it as is.
    """
    if isinstance(value, (list, tuple)):
        # If already a list (e.g., if coming from the command line that already parsed multiple args)
        return value
    items = value.split(',')
    if conv:
        try:
            items = [conv(item.strip()) for item in items]
        except Exception as e:
            raise argparse.ArgumentTypeError(f"Failed to convert list item: {e}")
    else:
        items = [item.strip() for item in items]
    return items

class EnvArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, env_prefix=None, **kwargs):
        """
        Args:
            env_prefix: A prefix to prepend to the variable name,
                        effectively a namespace for for args.
        """
        self.env_prefix = env_prefix
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        # Determine a candidate dest name
        dest = kwargs.get('dest')
        if not dest:
            for arg in args:
                if arg.startswith('--'):
                    dest = arg.lstrip('-').replace('-', '_')
                    break
            else:
                dest = args[0].lstrip('-').replace('-', '_')
            kwargs['dest'] = dest

        # See if we already have a type set
        orig_type = kwargs.get('type')

        # Handle booleans if action is 'store_true' or 'store_false'.
        if not kwargs.get('action') in ('store_true', 'store_false'):
            # If nargs > 1 (or an iterable type is expected) and no custom type is provided,
            # wrap the type conversion to allow for comma-separated environment values.
            nargs = kwargs.get('nargs')
            if nargs and nargs != '?' and not isinstance(nargs, int) or (isinstance(nargs, int) and nargs > 1):
                # Wrap the existing type in our comma-separated function.
                # This way, if the environment supplies a string, we split it,
                # but if the command line already provided multiple arguments, argparse will work as usual.
                # Note: We only need to wrap if a type was provided otherwise our default is str.
                use_conv = orig_type if orig_type is not None else str

                # Create a lambda that accepts a value and performs splitting.
                orig_func = kwargs.get('type', str)  # existing conversion function
                kwargs['type'] = lambda v: comma_separated_list(v, conv=use_conv)

        # Check if an environment variable exists and provide it as default if so.
        if self.env_prefix:
            env_var = f"{self.env_prefix}_{dest.upper()}"
            if env_var in os.environ:
                # If the environment provides a value, set it as the default.
                # The value from the env variable is processed through our type conversion.
                env_value = os.environ[env_var]

                # Process the env_value for booleans or list-like arguments if needed.
                try:
                    if kwargs.get('action') in ('store_true', 'store_false'):
                        # Here the type is boolean_type.
                        processed_value = boolean_type(env_value)
                    elif 'nargs' in kwargs and kwargs['nargs'] != '?' and (kwargs['nargs'] != 1):
                        # Wrap value for multiple items.
                        # Note: if the env variable includes spaces,
                        # they will be considered part of the item unless stripped.
                        processed_value = comma_separated_list(env_value, conv=orig_type if orig_type else str)
                    else:
                        # Use the provided type conversion if any.
                        processed_value = (orig_type or (lambda x: x))(env_value)
                except Exception as e:
                    self.error(f"Error processing environment variable {env_var}: {e}")

                kwargs['default'] = processed_value

        return super().add_argument(*args, **kwargs)
