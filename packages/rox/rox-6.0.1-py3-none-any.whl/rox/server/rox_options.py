from rox.core.logging.logging import Logging
from rox.server.logging.server_logger import ServerLogger
from rox.core.analytics.utils import remove_trailing_slash

class SelfManagedOptions:
    def __init__(self, server_url, analytics_url):
        self.server_url = remove_trailing_slash(server_url)
        self.analytics_url = remove_trailing_slash(analytics_url)

class NetworkConfigurationsOptions:
    def __init__(self, get_config_api_endpoint, get_config_cloud_endpoint,
                 send_state_api_endpoint, send_state_cloud_endpoint,
                 analytics_endpoint, push_notification_endpoint):
        self.get_config_api_endpoint = remove_trailing_slash(get_config_api_endpoint)
        self.get_config_cloud_endpoint = remove_trailing_slash(get_config_cloud_endpoint)
        self.send_state_api_endpoint = remove_trailing_slash(send_state_api_endpoint)
        self.send_state_cloud_endpoint = remove_trailing_slash(send_state_cloud_endpoint)
        self.analytics_endpoint = remove_trailing_slash(analytics_endpoint)
        self.push_notification_endpoint = remove_trailing_slash(push_notification_endpoint)

class RoxOptions:
    def __init__(self, dev_mode_key=None, version=None, fetch_interval=None, logger=None, 
                impression_handler=None, configuration_fetched_handler=None, roxy_url=None,
                self_managed_options=None, network_configuration_options=None, 
                dynamic_property_rule_handler=None, disable_signature_verification=False):
        self.dev_mode_key = dev_mode_key or 'stam'
        self.version = version or '0.0'

        if fetch_interval is not None:
            self.fetch_interval = 30 if fetch_interval < 30 else fetch_interval
        else:
            self.fetch_interval = 60

        Logging.set_logger(logger or ServerLogger())

        self.impression_handler = impression_handler
        self.configuration_fetched_handler = configuration_fetched_handler
        self.roxy_url = roxy_url
        self.self_managed_options = self_managed_options
        self.network_configuration_options = network_configuration_options
        self.disable_signature_verification = disable_signature_verification
        self.dynamic_property_rule_handler = dynamic_property_rule_handler if dynamic_property_rule_handler is not None else self.__default_dynamic_handler

    def is_self_managed(self):
        return self.self_managed_options is not None

    def __default_dynamic_handler(self, prop_name, context):
        if context:
            return context[prop_name]
        return None
