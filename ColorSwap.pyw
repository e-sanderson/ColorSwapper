import tkinter as tk
from PIL import Image, ImageTk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfilename, asksaveasfilename

class ColorSwapper:

    FONT = "Consolas"
    SIZE =  "13"
    STYLE = "bold"
    MAIN_FONT = FONT + " " + SIZE + " " + STYLE

    ARROW_FACTOR = 2
    ARROW_FONT = (FONT, str(int(ARROW_FACTOR*int(SIZE))), STYLE)

    COLOR = "#DBECEE"

    def __init__(self, root):

        '''
        GUI Initialization
        '''

        self.root = root

        self.root.title("Color Swapper")
        self.root.option_add("*Font", ColorSwapper.MAIN_FONT)
        self.root.option_add("*Background", ColorSwapper.COLOR)
        self.root.config(bg=ColorSwapper.COLOR)

        self.currentImage = None
        self.previewImage = None

        self.imageDisplay = tk.Label(self.root, borderwidth=10)
        self.imageDisplay.grid(row=0, column=0, columnspan=5)
        self.imageDisplay.bind("<Button 1>", self.extractPixel)

        self.directionButton = tk.Button(text='\u2193', borderwidth=1, relief='solid', font=ColorSwapper.ARROW_FONT, width=1, height=1, command=lambda:self.cycle(self.directionButton))
        self.directionButton.grid(row=1, column=0, rowspan=2, sticky='nswe')
        self.directionButton.state = 0
        self.cycle(self.directionButton)

        self.color1 = ColorSwapper.ColorInputBar(self.root)
        self.color1.grid(row=1, column=1, sticky='nswe')

        self.color2 = ColorSwapper.ColorInputBar(self.root, RGBA=('255', '255', '255', '0'))
        self.color2.grid(row=2, column=1, sticky='nswe')

        self.extractButton1 = tk.Button(self.root, text="\u2020", borderwidth=1, relief='solid', command=lambda:self.toggle(self.extractButton1, self.extractButton2))
        self.extractButton1.state = False
        self.extractButton1.grid(row=1, column=2, sticky='nswe')
        
        self.extractButton2 = tk.Button(self.root, text="\u2020", borderwidth=1, relief='solid', command=lambda:self.toggle(self.extractButton2, self.extractButton1))
        self.extractButton2.state = False
        self.extractButton2.grid(row=2, column=2, sticky='nswe')
        
        self.browseButton = tk.Button(self.root, text="Select Image", borderwidth=1, relief='solid', command=self.changeImage)
        self.browseButton.grid(row=1, column=3, sticky='nswe')

        self.updateButton = tk.Button(self.root, text="Update Color", borderwidth=1, relief='solid', command=self.updateColors)
        self.updateButton.grid(row=2, column=3, sticky='nswe')

        self.saveButton = tk.Button(self.root, text="Save", borderwidth=1, relief='solid', command=self.saveImage)
        self.saveButton.grid(row=1, column=4, rowspan=2, sticky='nswe')

        self.centerWindow()

    # Centers the gui window on the screen
    def centerWindow(self):
        self.root.update()
        screenW = self.root.winfo_screenwidth()
        screenH = self.root.winfo_screenheight()
        windowW = self.root.winfo_reqwidth()
        windowH = self.root.winfo_reqheight()
		
        positionR = int((screenW - windowW) / 2)
        positionD = int((screenH - windowH) / 2)
        self.root.geometry("+{}+{}".format(positionR, positionD))

    # Changes the curernt image being processed
    def changeImage(self):
        file = askopenfilename()
        if file == "":
            return
        if self.currentImage is not None:
            self.currentImage.close()
        self.currentImage = Image.open(file)
        self.currentImage = self.currentImage.convert("RGBA")
        self.updatePreview()
        self.centerWindow()

    # Saves the current state of the image
    def saveImage(self):
        path = asksaveasfilename()
        if path != "":
            if path[-4:] != ".png":
                path += ".png"
            if self.currentImage is not None:
                self.currentImage.save(path)

    # Updates the preview of the image
    def updatePreview(self):
        preview = self.currentImage
        w, h = preview.size
        screenw, screenh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        while (w > 0.8 * screenh) or (h > 0.8 * screenh):
            w, h = int(w*0.99), int(h*0.99)
        preview = preview.resize((w, h), Image.ANTIALIAS)
        background = self.createBackground(w, h)
        background.paste(preview, mask=preview)
        self.previewImage = ImageTk.PhotoImage(background)
        self.imageDisplay.config(image=self.previewImage)

    # Extracts the pixel color at the clicked point in the image
    def extractPixel(self, event):
        if self.currentImage is not None:
            RGBA = self.currentImage.getpixel((event.x, event.y))
            if self.extractButton1.state:
                self.color1.setColor(RGBA)
                self.toggle(self.extractButton1, self.extractButton2)
            if self.extractButton2.state:
                self.color2.setColor(RGBA)
                self.toggle(self.extractButton2, self.extractButton1)

    # Changes the pixels of one color within the image to another
    def updateColors(self):
        data = list(self.currentImage.getdata())
        direction = self.directionButton.state
        c1, c2 = self.color1.getIntRGBA(), self.color2.getIntRGBA()
        for i in range(len(data)):
            pixel = data[i]
            if direction == 0 and pixel == c2:
                # Up Arrow
                data[i] = c1
            elif direction == 1 and pixel == c1:
               # Down Arrow
               data[i] = c2
            elif direction == 2:
                # Double Arrow
                if pixel == c1:
                    data[i] = c2
                elif pixel == c2:
                    data[i] = c1
            
        self.currentImage.putdata(data)
        self.updatePreview()

    # A function for creating a simple checkerboard background so alpha levels can be observed
    def createBackground(self, width, height, NUM_RECTS=32):
        rwidth, rheight = width // NUM_RECTS, height // NUM_RECTS
        base = Image.new("RGBA", (width, height))
        c1, c2 = (0, 0, 0, 255), (255, 255, 255, 255)
        rowtype1 = [None for i in range(width)]
        rowtype2 = rowtype1[::]
        data = [None for j in range(height)]

        count = 0
        for i in range(width):
            rowtype1[i] = c1
            rowtype2[i] = c2
            count += 1
            if count % rwidth == 0:
                c1, c2 = c2, c1

        count = 0
        for j in range(height):
            data[j] = rowtype1
            count += 1
            if count % rheight == 0:
                rowtype1, rowtype2 = rowtype2, rowtype1

        data = sum(data, [])

        base.putdata(data)
        return base

    # Toggles two toggle buttons
    def toggle(self, button, other):
        if not other.state:
            button.state = not button.state
            b, f = button.config('bg')[-1], button.config('fg')[-1]
            button.config(bg=f, fg=b)

    # Cycles between various button states
    def cycle(self, button):
        states=["\u2191", "\u2193", "\u2195"]
        button.state = (button.state + 1) % 3
        button.config(text=states[button.state])

    

    class ColorInputBar(tk.Frame):
        '''
        ColorInputBar is a container for various color input objects.
        '''

        def __init__(self, parent, RGBA=('255', '255', '255', '100'), HEX="FFFFFF"):

            '''
            GUI Initialization
            '''

            tk.Frame.__init__(self, parent)

            self.preview = ColorSwapper.ColorInputBar.ColorPreview(self)
            self.preview.pack(side='left', fill='both')
            self.preview.bind("<Button 1>", self.colorPallet)

            self.red = tk.StringVar()
            self.red.set(RGBA[0])
            self.redEntry = ColorSwapper.ColorInputBar.ColorEntry(self, label="R", value=self.red, validationFunc=self.validateRGB)
            self.redEntry.pack(side='left')
            self.red.trace_add('write', lambda *args: self.trace(self.red))


            self.green = tk.StringVar()
            self.green.set(RGBA[1])
            self.greenEntry = ColorSwapper.ColorInputBar.ColorEntry(self, label="G", value=self.green, validationFunc=self.validateRGB)
            self.greenEntry.pack(side='left')
            self.green.trace_add('write', lambda *args: self.trace(self.green))

            self.blue = tk.StringVar()
            self.blue.set(RGBA[2])
            self.blueEntry = ColorSwapper.ColorInputBar.ColorEntry(self, label="B", value=self.blue, validationFunc=self.validateRGB)
            self.blueEntry.pack(side='left')
            self.blue.trace_add('write', lambda *args: self.trace(self.blue))

            self.alpha = tk.StringVar()
            self.alpha.set(RGBA[3])
            self.alphaEntry = ColorSwapper.ColorInputBar.ColorEntry(self, scalemax=100, label="A", value=self.alpha, validationFunc=self.validateAlpha)
            self.alphaEntry.pack(side='left')
            self.alpha.trace_add('write', lambda *args: self.trace(self.alpha))

            self.hex = tk.StringVar()
            self.hex.set(HEX)
            self.hexEntry = ColorSwapper.ColorInputBar.ColorEntry(self, label="Hex", value=self.hex, validationFunc=self.validateHex, textLimit=6, scalemax=None)
            self.hexEntry.pack(expand=True, fill='both')
            self.hex.trace_add('write', lambda *args: self.trace(self.hex, RGBA=False))

            self.updateRGBA()

        # Sets the corrosponding RGBA values into the appropriate fields for a given color
        def setColor(self, RGBA):
            RGBA = [' '*(3 - len(str(c))) + str(c) for c in RGBA]
            self.red.set(RGBA[0])
            self.green.set(RGBA[1])
            self.blue.set(RGBA[2])
            self.alpha.set(str(int(RGBA[3]) * 100 // 255))

        # Returns an array containing the current RGBA values as strings
        def getRGBA(self):
            return [self.red.get(), self.green.get(), self.blue.get(), self.alpha.get()]

        # Returns an array containing the current RGBA values as ints
        def getIntRGBA(self):
            r, g, b, a = map(int, self.getRGBA())
            a = a * 255 // 100
            return (r, g, b, a)

        # Returns the hex string of the current color
        def getHex(self):
            return self.hex.get()

        # Updates the current RGBA values
        def updateRGBA(self):
            hx = self.getHex()
            r, g, b = self.hex2rgb(hx)
            a = self.alpha.get()
            self.red.set(r)
            self.green.set(g)
            self.blue.set(b)
            color = (int(r), int(g), int(b), int(a) * 255 // 100)
            self.preview.updateColor(color)

        # Updates the current hex vale
        def updateHex(self):
            newHex = self.rgb2hex(self.getRGBA()[:-1])
            self.hex.set(str(hex(int(newHex, 16)))[2:].upper())


        # Ensure the current RGB value is a valid RGB value
        def validateRGB(self, new):
            if not (new == "" or (new.isdigit() and int(new) <= 255)):
                return False
            return True

        # Ensures the current alpha value is a valid alpha value
        def validateAlpha(self, new):
            if not (new == "" or (new.isdigit() and int(new) <= 100)):
                return False
            return True

        # Ensures the current hex value is a valid hex value
        def validateHex(self, new):
            validHex = all([c in "0123456789abcdefABCDEF" for c in new]) and len(new) <= 6
            if not (new == "" or validHex):
                return False
            return True

        # Function for making hex and RGB update together
        def trace(self, channel, RGBA=True):
            new = channel.get()
            if new == "":
                new = "0"
            if RGBA:
                channel.set(str(int(new)))
                self.updateHex()
            else:
                channel.set(str(hex(int(new, 16)))[2:].upper())
                self.updateRGBA()
                

        # Opens a color pallet for the user to select a color from
        def colorPallet(self, event):
            color = askcolor()[1]
            if color is not None:
                self.hex.set(color[1:])

        # RGB to hex conversion
        def rgb2hex(self, RGB):
            hx = ""
            for c in RGB:
                h = hex(int(c))[2:]
                if len(h) != 2:
                   h = (2 - len(h))*"0" + h
                hx += h
            if not hx:
                hx = "0"
            return hx

        # Hex to RGB values conversion
        def hex2rgb(self, hx):
            hx = (6 - len(hx))*" " + hx
            rgbx = [hx[i:i+2].strip() for i in range(0, len(hx), 2)]
            return [str(int(h, 16)) if h != "" else "0" for h in rgbx]

        class ColorEntry(tk.Frame):
            '''
            ColorEntry objects are Frames that group an entry object with a text object, for spacing and simplicity
            '''

            def __init__(self, parent, label=None, value=None, scaleVal=None, validationFunc=None, textLimit=3, scalemax=255):

                '''
                GUI Initialization
                '''

                tk.Frame.__init__(self, parent, highlightbackground='black', highlightcolor='black', highlightthickness=1)
                self.parent = parent
                self.label = tk.Label(self, text=label)
                self.entry = tk.Entry(self, relief='solid', width=textLimit, textvariable=value, validate='key', validatecommand=(self.register(validationFunc), '%P'))
                if scalemax is not None:
                    self.label.grid(row=0, column=0)
                    self.entry.grid(row=0, column=1)
                    templabel = tk.Label(text="   ")
                    w, h = templabel.winfo_reqwidth(), templabel.winfo_reqheight()
                    templabel.destroy()
                    self.scale = tk.Scale(self, relief='solid', sliderrelief='solid', highlightcolor='black', borderwidth=1, orient='horizontal', width=h//5, length=w, sliderlength=w//4, showvalue=0, to=scalemax, variable=value, bigincrement=5)
                    self.scale.grid(row=1, column=0, columnspan=2, sticky='nswe')
                else:
                    self.label.pack(side='left')
                    self.entry.pack(side='left')

        class ColorPreview(tk.Label):
            '''
            ColorPreview objects are Labels that simply draw a rectangle to display a color
            '''

            def __init__(self, parent, color=(255, 255, 255, 100)):


                '''
                GUI Initialization
                '''

                NUM_CHAR_WIDTH = 3

                tk.Label.__init__(self, parent, text=" "*NUM_CHAR_WIDTH, borderwidth=1, relief='solid')
                self.size = (self.winfo_reqwidth(), self.winfo_reqheight())
                self.color = color
                self.updatePreview()
                self.bind("<Configure>", self.resize)

            # Updates the color of the color preview
            def updateColor(self, color):
                self.color = color
                self.updatePreview()

            # Resizes the color preview
            def resize(self, event):
                newsize = (event.width - 2, event.height - 2)
                if newsize != self.size:
                    self.size = newsize
                    self.updatePreview()

            # Updates the current color preview
            def updatePreview(self):
                w, h = self.size
                NUM_RECTS = 8
                background = ColorSwapper.createBackground(None, w, h, NUM_RECTS)
                preview = Image.new("RGBA", self.size, color=self.color)
                background.paste(preview, mask=preview)
                self.colorPreview = ImageTk.PhotoImage(background)
                self.config(image=self.colorPreview)
              
if __name__ == '__main__':

    root = tk.Tk()
    ColorSwap = ColorSwapper(root)
    root.mainloop()