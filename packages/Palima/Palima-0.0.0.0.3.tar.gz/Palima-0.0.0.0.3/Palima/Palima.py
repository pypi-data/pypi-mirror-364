#EYPA is tkinter, time, os based game engine!
import tkinter as tk #For window functions!
import time #For Wait functions!
import os #For SetIconICO function and other working with PATH functions!

VVV = "Pre-P 0.3"
VV = 32

class EditWindow():
    def SetIconICO(ID:str, path:str):
        try:
            path = path
        except Exception as e:
            print(f"Palima Function Runner Detected A Error: ({e})")
        
        globals()[ID].withdraw()
        globals()[ID].iconbitmap(path)
        globals()[ID].deiconify()

    def Title(ID:str, Title:str):
        globals()[ID].title(Title)

    def Size(ID:str, X:int, Y:int):
        globals()[ID].geometry(f"{X}x{Y}")

    def ScreenResizable(ID:str, X:bool, Y:bool):
        globals()[ID].resizable(X, Y)

def AddScreen(ID:str):
    root = tk.Tk()
    root.title("Palima Screen")
    root.geometry("350x350")
    globals()[ID] = root
    ico_path = os.path.abspath("Palima/Palima.ico")
    if os.path.exists(ico_path):
        globals()[ID].iconbitmap(ico_path)
    else:
        print(f"Palima.ico not found at {ico_path}")
    return ID

class Screen():
    def LoopScreen(ID:str):
        try:
            globals()[ID].mainloop()
        except (TypeError, KeyError, ValueError):
            print("Palima Function Runner Detected A Error: No screen object for loop!")

    def UpdateScreen(ID:str):
        try:
            globals()[ID].update()
        except (TypeError, KeyError, ValueError):
            print("Palima Function Runner Detected A Error: No screen object for update!")

    def SetSize(ID:str, x:int, y:int):
        globals()[ID].geometry(f"{x}x{y}")

class Wait():
    def Second(Value):
        time.sleep(Value) #time.sleep() function is already working with second type.

    #When we want use time.sleep() function with not second type then, we must do math.

    def SplitSecond(Value):
        time.sleep(Value/60)

    def Minute(Value):
        time.sleep(Value*60)

    def Hour(Value):
        time.sleep((Value*60)*60)

class TextLabel():
    def Add(ID:str, Text:str):
        TextLabel = tk.Label(text=Text, font="Helvetica 10")
        globals()[ID] = TextLabel
        return ID

    def FontSize(ID:str, FS:int):
        globals()[ID].config(font=f"Helvetica {FS}")

    def Position(ID:str, X:int, Y:int):
        globals()[ID].place(x=X, y=Y)

    def Text(ID:str, Text:str):
        globals()[ID].config(text=Text)

def ListenInputs(ID:str, Key:str, Function):
    Key_KEY = {
        "MouseButton-Left":"<Button-1>",
        "MouseButton-Middle":"<Button-2>",
        "MouseButton-Right":"<Button-3>",
        "MouseRelease-Left":"<ButtonRelease-1>",
        "MouseRelease-Middle":"<ButtonRelease-2>",
        "MouseRelease-Right":"<ButtonRelease-3>",
        "MouseDouble-Left":"<Double-Button-1>",
        "MouseDouble-Middle":"<Double-Button-2>",
        "MouseDouble-Right":"<Double-Button-3>",
        "MouseTriple-Left":"<Triple-Button-1>",
        "MouseTriple-Middle":"<Triple-Button-2>",
        "MouseTriple-Right":"<Triple-Button-3>",
        "MouseButtonMotion-Left":"<B1-Motion>",
        "MouseButtonMotion-Middle":"<B2-Motion>",
        "MouseButtonMotion-Right":"<B3-Motion>",
        "MouseMotion":"<Motion>",
        "MouseEnter":"<Enter>",
        "MouseLeave":"<Leave>",
        "WidgetSize":"<Configure>",
        "WidgetFocusIn":"<FocusIn>",
        "WidgetFocusOut":"<FocusOut>",
        "AnyKey":"<Key>",
        "AnyMouseRelease":"<KeyRelease>",
        "EnterKey":"<Return>",
        "BackSpaceKey":"<BackSpace>",
        "TabKey":"<Tab>",
        "EscapeKey":"<Escape>",
        "UpKey":"<Up>",
        "DownKey":"<Down>",
        "LeftKey":"<Left>",
        "RightKey":"<Right>",
        "PageUpKey":"<PageUp>",
        "PageDownKey":"<PageDown>",
        "HomeKey":"<Home>",
        "EndKey":"<End>",
        "DeleteKey":"<Delete>",
        "LeftShiftKey":"<Shift_L>",
        "RightShiftKey":"<Shift-R>",
        "LeftControlKey":"<Control_L>",
        "RightControlKey":"<Control_R>",
        "LeftAltKey":"<Alt_L>",
        "RightAltKey":"<Alt-R>",
        "AnyButton":"<ButtonPress>",
        "AnyButtonRelease":"<ButtonRelease>",
        "MouseWheelScroll":"<MouseWheel>",
        "ShowWidget":"<Map>",
        "UnShowWidget":"<Unmap>",
        "WriteAgain":"<Expose>",
        "ActiveWindow":"<Active>",
        "DeactiveWindow":"<Deactive>",
        "DestroyWidget":"<Destroy>",
        "Reparent":"<Reparent>",
        "Visibility":"<Visibility>",
        "Key-a":"<Key-a>",
        "Key-b":"<Key-b>",
        "Key-c":"<Key-c>",
        "Key-d":"<Key-d>",
        "Key-e":"<Key-e>",
        "Key-f":"<Key-f>",
        "Key-g":"<Key-g>",
        "Key-h":"<Key-h>",
        "Key-i":"<Key-i>",
        "Key-j":"<Key-j>",
        "Key-k":"<Key-k>",
        "Key-l":"<Key-l>",
        "Key-m":"<Key-m>",
        "Key-n":"<Key-n>",
        "Key-o":"<Key-o>",
        "Key-p":"<Key-p>",
        "Key-q":"<Key-q>",
        "Key-r":"<Key-r>",
        "Key-s":"<Key-s>",
        "Key-t":"<Key-t>",
        "Key-u":"<Key-u>",
        "Key-v":"<Key-v>",
        "Key-w":"<Key-w>",
        "Key-x":"<Key-x>",
        "Key-y":"<Key-y>",
        "Key-z":"<Key-z>",
        "Key-A":"<Key-A>",
        "Key-B":"<Key-B>",
        "Key-C":"<Key-C>",
        "Key-D":"<Key-D>",
        "Key-E":"<Key-E>",
        "Key-F":"<Key-F>",
        "Key-G":"<Key-G>",
        "Key-H":"<Key-H>",
        "Key-I":"<Key-I>",
        "Key-J":"<Key-J>",
        "Key-K":"<Key-K>",
        "Key-L":"<Key-L>",
        "Key-M":"<Key-M>",
        "Key-N":"<Key-N>",
        "Key-O":"<Key-O>",
        "Key-P":"<Key-P>",
        "Key-Q":"<Key-Q>",
        "Key-R":"<Key-R>",
        "Key-S":"<Key-S>",
        "Key-T":"<Key-T>",
        "Key-U":"<Key-U>",
        "Key-V":"<Key-V>",
        "Key-W":"<Key-W>",
        "Key-X":"<Key-X>",
        "Key-Y":"<Key-Y>",
        "Key-Z":"<Key-Z>",
        "Key-0":"<Key-0>",
        "Key-1":"<Key-1>",
        "Key-2":"<Key-2>",
        "Key-3":"<Key-3>",
        "Key-4":"<Key-4>",
        "Key-5":"<Key-5>",
        "Key-6":"<Key-6>",
        "Key-7":"<Key-7>",
        "Key-8":"<Key-8>",
        "Key-9":"<Key-9>",
        "Key-'":"<Key-'>",
        "Key-~":"<Key-~>",
        "Key-!":"<Key-!>",
        "Key-@":"<Key-@>",
        "Key-#":"<Key-#>",
        "Key-$":"<Key-$>",
        "Key-%":"<Key-%>",
        "Key-^":"<Key-^>",
        "Key-&":"<Key-&>",
        "Key-*":"<Key-*>",
        "Key-(":"<Key-(>",
        "Key-)":"<Key-)>",
        "Key--":"<Key-->",
        "Key-_":"<Key-_>",
        "Key-_":"<Key-_>",
        "Key-=":"<Key-=>",
        "Key-[":"<Key-[>",
        "Key-]":"<Key-]>",
        "Key-{":"<Key-{>",
        "Key-}":"<Key-}>",
        "Key-/":"<Key-/>",
        "Key-|":"<Key-|>",
        "Key-;":"<Key-;>",
        "Key-:":"<Key-:>",
        'Key-"':'<Key-">',
        'Key-,':'<Key-,>',
        'Key-.':'<Key-.>',
        'Key->':'<Key->>',
        'Key-?':'<Key-?>',
        'Key-/':'<Key-/>',
        'Key-space':'<Key-space>',
        'Key-F1':'<Key-F1>',
        'Key-F2':'<Key-F2>',
        'Key-F3':'<Key-F3>',
        'Key-F4':'<Key-F4>',
        'Key-F5':'<Key-F5>',
        'Key-F6':'<Key-F6>',
        'Key-F7':'<Key-F7>',
        'Key-F8':'<Key-F8>',
        'Key-F9':'<Key-F9>',
        'Key-F10':'<Key-F10>',
        'Key-F11':'<Key-F11>',
        'Key-Print':'<Key-Print>',
        'Key-Scroll_Lock':'<Key-Scroll_Lock>',
        'Key-Pause':'<Key-Pause>',
        'Key-Num_Lock':'<Key-Num_Lock>'
        }

    try:
        KEY = Key_KEY[Key]
        globals()[ID].bind(KEY, Function)
    except Exception as e:
        print(f"Palima Error During ListenInputs function: {Key}, {e}")

    globals()[ID].bind(KEY)

class Cursor():
    def ShowCursor(ID:str):
        globals()[ID].config(cursor='')
    def HideCursor(ID:str):
        globals()[ID].config(cursor='none')


class Box():
    def Add(ID:str):
        Box_label = tk.Label(bg="black", width=50, height=50)
        globals()[ID] = Box_label
        return ID
    
    def Position(ID:str, X:int, Y:int):
        globals()[ID].place(x=X, y=Y)

    def Text(ID:str, Text:str):
        globals()[ID].config(text=Text)

    def FillColor(ID:str, Color:str):
        globals()[ID].config(bg=Color.lower())

    def Size(ID:str, WidthV:int, HeightV:int):
        globals()[ID].config(width=WidthV, height=HeightV)

class GetInfo():
    def Version():
        return VVV, VV
