import sys
from . import cli


try:
    cli.main()
except KeyboardInterrupt:
    print("Received SIGINT. Quit...")
    sys.exit(-1)
