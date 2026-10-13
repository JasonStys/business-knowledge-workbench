# @index-begin
# @index-end
"""Jason Stys: frozen private website service and fixed-format conversion child dispatch."""

import sys
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    if len(sys.argv) > 1 and sys.argv[1] == "--convert":
        sys.argv.pop(1)
        from server.worker import main
    else:
        from server.private_cli import main
    main()
