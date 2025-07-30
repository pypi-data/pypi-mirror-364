# gifanimus
A very simple package for playing looped gifs

Install the package with pip:

```
pip install gifanimus
```

&nbsp;

Simple Example:

```python
from gifanimus import GifAnimation
import time

##Create a new loading animation
loading = GifAnimation('./loading.gif', 1000, True, 'LOADING...')

time.sleep(3)
##Start the animation
loading.Play()

time.sleep(10)

##Stop the animation
loading.Stop()
```

&nbsp;

**GifAnimation class parameters**:

**gifDir**: is a string that represents the directory path of the gif file.

**frameDelay**: is an optional parameter representing the delay between  
frames in milliseconds. Default value is 1000ms (1 second). This delay is
divided by the total number of frames in the gif, so it effectively controls 
the play speed of the gif.

**loop**: defines whether the animation should repeat after reaching the  
last frame. It's set to True by default, but can be changed to False  
if you want the animation to stop at the last frame.

**consoleMsg**: is an optional string that will be displayed in the console while the animation is running.

**quiet**: is an optional boolean, if true nothing will be output to the termnal when gif animation is playing.
