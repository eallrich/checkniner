"""Provides a single source for getting the statsd client configuration."""
import platform

from django.conf import settings
from statsd import StatsClient

host = platform.node().replace('.', '_')
prefix = "%s.checkniner" % (host,)
server = settings.STATSD_CONFIG['host']
port   = settings.STATSD_CONFIG['port']

statsd = StatsClient(server, port, prefix=prefix)
