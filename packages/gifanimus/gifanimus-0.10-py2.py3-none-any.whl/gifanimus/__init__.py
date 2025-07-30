"""A Simple Gif Animation Window, By: Fibo Metavinci"""

__version__ = "0.10"

import threading
import tkinter
from PIL import Image, ImageTk
import sys
import time
import platform

class GifAnimation:
    def __init__(self, gifDir, frameDelay=1000, loop=True, consoleMsg="", quiet=False):
        '''
        Initialization of attributes.
        
        gifDir:  is a string that represents the directory path of the gif file.
        
        frameDelay:  is an optional parameter representing the delay between
        frames in milliseconds. Default value is 1000ms (1 second).
        
        loop:  defines whether the animation should repeat after reaching the
        last frame. It's set to True by default, but can be changed to False
        if you want the animation to stop at the last frame.
        
        consoleMsg:  is an optional string that will be displayed in the console while the animation is running.
        '''
        self.gif = gifDir
        self.delay = frameDelay
        self.loop = loop
        self.msg = consoleMsg
        self.quiet = quiet
        self.window = AnimationWindow(self.gif, self.delay, self.loop, self.msg, self.quiet)
        self.thread = threading.Thread(target=self.window.Activate)
        self.thread.setDaemon(True)

    def Play(self):
        self.thread.start()
        
    def Stop(self):
        self.window.Stop()


class AnimationWindow:
    def __init__(self, gifDir, frameDelay, loop, consoleMsg, quiet):
        self.gif = gifDir
        self.delay = frameDelay
        self.loop = loop
        self.msg = consoleMsg
        self.quiet = quiet
        self.root = None
        self.file = None
        self.frames = None
        self.speed = None
        self.window = None
        self.img = None
        self.active = False
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"

    def Activate(self):
        self.root = tkinter.Tk()
        # Handle different platforms appropriately
        if self.is_windows:
            # On Windows, use a minimal root window
            self.root.geometry("1x1+0+0")
            self.root.overrideredirect(True)
            self.root.attributes('-alpha', 0.0)
        elif self.is_macos:
            # On macOS, use a minimal root window (avoid fullscreen issues)
            self.root.geometry("1x1+0+0")
            self.root.overrideredirect(True)
            self.root.attributes('-alpha', 0.0)
        else:
            # On Linux, use fullscreen
            self.root.attributes('-fullscreen', True)
            
        self.file = Image.open(self.gif) 
        self.frames = [tkinter.PhotoImage(file=self.gif, format='gif -index %i'%(i)) for i in range(self.file.n_frames)]
        self.speed = self.delay // len(self.frames) # make one cycle of animation around 4 secs

        self.active = True
        self.Play()
        if not self.quiet:
            thread = threading.Thread(target=self.consoleAnimation)
            thread.setDaemon(True)
            thread.start()

        self.root.mainloop()
        
    def _center_window(self, win):
        # Force the window to update its geometry
        win.update_idletasks()
        
        # Get screen dimensions
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        
        # Get window dimensions
        window_width = win.winfo_width()
        window_height = win.winfo_height()
        
        # If window dimensions are still 0, use the image dimensions directly
        if window_width <= 1 or window_height <= 1:
            try:
                # Get dimensions from the first frame
                window_width = self.frames[0].width()
                window_height = self.frames[0].height()
            except:
                # Fallback to reasonable defaults
                window_width = 200
                window_height = 200
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Ensure window is positioned on screen
        x = max(0, x)
        y = max(0, y)
        
        # Apply the geometry
        win.geometry(f'+{x}+{y}')
        
        # Force the window to update and show at the new position
        win.update_idletasks()
        win.update()

    def consoleAnimation(self):
        animation = ['  -  ', '  /  ', '  |  ', '  \\  ']
        i = 0
        while self.active:
            sys.stdout.write( animation[i % len(animation)] + f"\r{self.msg}" )
            sys.stdout.flush()
            time.sleep(0.25)
            i += 1
            
    def Stop(self):
        self.active = False
      
    def Play(self, n=0, top=None, lbl=None):
        if not self.active:
            if self.window:
                self.window.destroy()
            if self.root:
                self.root.destroy()
            sys.stdout.flush()
            return
        
        if n == 0:
            if self.img == None:
                if self.is_windows or self.is_macos:
                    # On Windows and macOS, create the window directly without withdrawing root
                    self.window = tkinter.Toplevel()
                else:
                    self.root.withdraw()
                    self.window = tkinter.Toplevel(width=self.root.winfo_width(), height=self.root.winfo_height())
                
                self.window.overrideredirect(True)
                # Remove the problematic alpha setting that makes window invisible
                # self.window.wm_attributes("-alpha", 0.0)
                
                self.img = tkinter.Label(self.window, text="", image=self.frames[0])
                self.img.pack()
                
                # Schedule centering after the window has properly sized itself
                self.window.after(10, self._center_window, self.window)
                
                # Ensure window is visible and on top
                self.window.lift()
                self.window.focus_force()
                
        if n < len(self.frames)-1:
            self.img.config(image=self.frames[n])
            self.img.after(self.speed, self.Play, n+1, top, lbl)
        else:
            if self.loop:
                self.img.config(image=self.frames[0])
                self.img.after(self.speed, self.Play, 0, top, lbl)
            else:
                self.active = False
            


