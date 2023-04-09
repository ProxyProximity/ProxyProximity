"""Constants for the ProxyProximity integration."""

# Base component constants
DOMAIN = "proximity"

# Attributes
ATTR_DISTANCE = "distance"

# Services
SERVICE_CALIBRATE = "calibrate"

# Configuration
CONF_DEVICE_TRACKER = "device_tracker"
CONF_ENTITY_SUFFIX = "entity_suffix"
CONF_SHOW_AS_STATE = "show_as_state"
CONF_SHOW_LAST_CHANGED = "show_last_changed"
CONF_ROUND_DIGITS = "round_digits"
CONF_DEFAULT_TX_POWER = "default_tx_power"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_DEVICE_TRACKER = "device_tracker"
DEFAULT_ENTITY_SUFFIX = "prox"
DEFAULT_SHOW_AS_STATE = False
DEFAULT_SHOW_LAST_CHANGED = False
DEFAULT_ROUND_DIGITS = 2
DEFAULT_DEFAULT_TX_POWER = -59

# Platforms
PLATFORMS = [DEVICE_TRACKER_DOMAIN]

# Messages
MESSAGE_DEVICE_CONNECTED = "{} connected to {} network."
MESSAGE_DEVICE_DISCONNECTED = "{} disconnected from {} network."
