from channels import route_class, route
from webterminallte.consumers import Webterminal, SshTerminalMonitor

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. In this example, we route
# all WebSocket connections to the class-based BindingConsumer (the consumer
# class itself specifies what channels it wants to consume)
channel_routing = [
    route_class(Webterminal, path=r'^/ws/(?P<ip>(?:(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?)\.){3}(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?))/(?P<id>[0-9]+)/$'),
    route_class(SshTerminalMonitor, path=r'^/monitor/(?P<channel>[\w-]+)'),
]
