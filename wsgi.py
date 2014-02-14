import sys, os

import newrelic.agent
newrelic.agent.iniitalize('/home/web/MyJobs-pixel/newrelic.ini')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pixel import app as application

application = newrelic.agent.wsgi_application()(application)
