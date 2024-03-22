# StockShark
All you need to start using the engine is to run the file StockShark.exe .

In some cases, if the file does not start correctly, you may need to rebuild the file StockShark.py . You can do this via the command line using pyinstaller. You can also install an icon on the exe file using the --icon flag. The icon can be found in the Images folder.

If this does not help, you can rebuild the file main.cpp .

In general, the entire engine is located in main.cpp so if you're wondering how it works and you're not afraid of my terribly written code, feel free to figure it out. The engine accepts multiple requests: "go infinity" - endlessly calculates the lines, from time to time giving the result; "go depth <depth>" - calculates to a given depth; "go time <min time> <max time>" - calculates a certain time. After each request, enter the FEN of the position for which you want to perform the calculation, and then enter -1, which means that the input is completed. If necessary, I will answer any question about the engine, just write to me in Discord akula538.

StockShark.py is just a GUI, but I'm also ready to answer questions about it.
