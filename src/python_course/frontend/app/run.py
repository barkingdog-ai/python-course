"""用一個腳本來啟動 streamlit server，以減少 makefile 的指令

因為 streamlit 沒有提供類似 `uvicorn.run()` 這種執行方式，所以就只能直接透過內建的 CLI 來執行
參考：https://stackoverflow.com/a/62775219
"""

import sys

from streamlit.web import cli as stcli

from python_course.core import settings
from python_course.frontend.app import main

# The address where the server will listen for client and browser connections.
address = settings.STREAMLIT_HOST
# The port where the server will listen for browser connections.
port = settings.STREAMLIT_PORT
# If false, will attempt to open a browser window on start.
headless = "true"
# Automatically rerun script when the file is modified on disk.
run_on_save = "true"

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        main.__file__,
        "--server.address",
        address,
        "--server.port",
        str(port),
        "--server.headless",
        headless,
        "--server.runOnSave",
        run_on_save,
    ]
    sys.exit(stcli.main())
