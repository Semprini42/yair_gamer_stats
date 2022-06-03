from win32gui import GetWindowText, GetForegroundWindow
print (GetWindowText(GetForegroundWindow()))