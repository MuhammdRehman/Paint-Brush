from tkinter import *
from tkinter import colorchooser
from tkinter import Button, PhotoImage
import math
from tkinter import simpledialog
from PIL import ImageGrab
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw
from queue import Queue
from tkinter.colorchooser import askcolor
class ZoomTool:
    def __init__(self, canvas, width, height):
        self.zoom_factor = 1.0  # Initial zoom factor
        self.canvas = canvas
        self.canvas_width = width
        self.canvas_height = height

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.apply_zoom()

    def zoom_out(self):
        if self.zoom_factor > 0.1:
            self.zoom_factor -= 0.1
            self.apply_zoom()

    def apply_zoom(self):
        canvas_width_scaled = int(self.canvas_width * self.zoom_factor)
        canvas_height_scaled = int(self.canvas_height * self.zoom_factor)
        canvas_x_offset = (self.canvas_width - canvas_width_scaled) // 2
        canvas_y_offset = (self.canvas_height - canvas_height_scaled) // 2

        self.canvas.config(width=canvas_width_scaled, height=canvas_height_scaled)
        self.canvas.scale("all", 0, 0, self.zoom_factor, self.zoom_factor)
        self.canvas.move("all", canvas_x_offset, canvas_y_offset)
class PaintApp:
    def __init__(self,width,height,title):
        self.screen = Tk()
        self.screen.title(title)
        self.screen.geometry(f'{str(width)}x{str(height)}')
        self.zoom_factor = 1.0  # Initial zoom factor
        self.canvas_width = width
        self.canvas_height=height
        
        #area for buttons
        self.button_Area = Frame(self.screen,width = width,height = 100,bg = "grey86")
        self.button_Area.pack()
        #   canvas
        self.canvas = Canvas(self.screen,width=width,height = height , bg = "white")
        self.canvas.pack()
        
        # Initialize selected objects and last position variables
        self.selected_objects = []
        self.last_x = None
        self.last_y = None
        self.selected_area_start_x = None
        self.selected_area_start_y = None
        
        #==============================================================
        #                 default attributes
        #==============================================================
        
        self.brush_color = 'black'
        self.shape_id = None
        self.last_x,self.last_y = None,None
        self.textValue = StringVar()
        self.stroke_size = IntVar()
        self.text_size = IntVar()
        self.num_points=7
        self.stroke_size.set(2)
        self.text_size.set(20)
        # stroke size options 
        self.options = [1,2,3,4,5,10,30,40,50,100,200]
        self.text_font=[10,20,50,72,100]
        
        # Initialize other parts of your code
        self.magnify_window = None
        self.magnify_label = None
        self.magnify_active = False
        # Bind button 2 (right mouse button) press event
        self.screen.bind("<Button-2>", self.toggle_magnify)
        
        # Bind the drag and release events
        self.screen.bind("<B1-Motion>", self.on_canvas_drag)
        self.screen.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.screen.bind("<Button-1>", self.on_canvas_click)

        #==============================================================
        #                 basics
        #==============================================================
        
        
        #   open button
        self.open_button = Button(self.button_Area,text = "Open",bg='grey68',height=2, width=8,command=self.open_press)
        self.open_button.place(x=3,y=5)
        #   save button
        self.save_button = Button(self.button_Area,text = "Save",bg='grey68',height=2, width=8,command=self.saveImage)
        self.save_button.place(x=3,y=55)
        #   help button
        self.help_button = Button(self.button_Area,text = "Help",bg='grey68',height=2, width=8,command=self.help)
        self.help_button.place(x=75,y=5)
        #   clear button
        self.clear_button = Button(self.button_Area,text = "Clear",bg='grey68',height=2, width=8,command=self.clear_button)
        self.clear_button.place(x=75,y=55)
        
        #==============================================================
        #                 brushes
        #==============================================================
        
        #   brush button
        self.image_B=PhotoImage(file="pictures/brush.png")
        self.brush_button = Button(self.button_Area,image=self.image_B,borderwidth=2 ,command=self.on_brush_press)
        self.brush_button.place(x=200,y=5)
        #   bind
        self.canvas.bind("<B1-Motion>",self.brush_draw)
        self.canvas.bind("<ButtonRelease-1>",self.brush_draw_ending)
        
        #   eraser button
        self.image_er=PhotoImage(file="pictures/eraser.png")
        self.eraser_button = Button(self.button_Area,image=self.image_er,borderwidth=2 ,command=self.on_eraser_press)
        self.eraser_button.place(x=200,y=50)
        
        #   selection button
        self.image_sel=PhotoImage(file="pictures/selection.png")
        self.sel_button = Button(self.button_Area,image=self.image_sel,borderwidth=2 ,command=self.on_selection_press)
        self.sel_button.place(x=250,y=50)
        
        #mag picker
        self.image_mag=PhotoImage(file="pictures/mag.png")
        self.picker_active=False
        self.mag_button = Button(self.button_Area,image=self.image_mag,borderwidth=2 ,command=self.on_color_picker_press)
        self.mag_button.place(x=250,y=5)
        
        #color picker
        self.image_picker=PhotoImage(file="pictures/color_picker.png")
        self.picker_active=False
        self.picker_button = Button(self.button_Area,image=self.image_picker,borderwidth=2 ,command=self.on_color_picker_press)
        self.picker_button.place(x=300,y=50)
        
        #bucket button
        self.bucket_active=False
        self.image_bucket=PhotoImage(file="pictures/bucket.png")
        self.bucket_button = Button(self.button_Area,image=self.image_bucket,borderwidth=2 ,command=self.on_bucket_press)
        self.bucket_button.place(x=300,y=5)
        
        
        
        #   font size
        self.sizeLabel = Label(self.button_Area , text="Brush Size",height=1, width=9,font=("Arial",10,"bold"),bg="Lightgrey")
        self.sizeLabel.place(x=350,y=22)
        self.sizeList = OptionMenu(self.button_Area , self.stroke_size , *self.options)
        self.sizeList.place(x=363,y=55)
        
        #==============================================================
        #                 shapes
        #==============================================================
        #   circle button
        self.image_C=PhotoImage(file="pictures/circle.png")
        self.circle_button = Button(self.button_Area,image=self.image_C,borderwidth=1 ,command=self.on_circle_press)
        self.circle_button.place(x=750,y=22)
        #   diamond button
        self.image_D=PhotoImage(file="pictures/diamond.png")
        self.diamond_button = Button(self.button_Area,image=self.image_D,borderwidth=1 ,command=self.on_diamond_press)
        self.diamond_button.place(x=750,y=55)
        #   arrow button
        self.image_arrow=PhotoImage(file="pictures/arrow.png")
        self.arrow_button = Button(self.button_Area,image=self.image_arrow,borderwidth=1  ,command=self.on_arrow_press)
        self.arrow_button.place(x=715,y=22)
        #   oval button
        self.image_o=PhotoImage(file="pictures/oval.png")
        self.oval_button = Button(self.button_Area,image=self.image_o, borderwidth=1 ,command=self.on_oval_press)
        self.oval_button.place(x=715,y=55)
        #   triangle button
        self.image_t=PhotoImage(file="pictures/triangle.png")
        self.triangle_button = Button(self.button_Area,image=self.image_t,borderwidth=1 ,command=self.on_triangle_press)
        self.triangle_button.place(x=680,y=22)
        #   hexagon button
        self.image_h=PhotoImage(file="pictures/hexagon.png")
        self.hexagon_button = Button(self.button_Area,image=self.image_h,borderwidth=1 ,command=self.on_hexagon_press)
        self.hexagon_button.place(x=680,y=55)
        #   star button 
        self.image_S=PhotoImage(file="pictures/star.png")
        self.star_button = Button(self.button_Area,image=self.image_S,borderwidth=1 ,command=self.on_star_press)
        self.star_button.place(x=645,y=22)
        #   square button
        self.image_s=PhotoImage(file="pictures/square.png")
        self.Square_button = Button(self.button_Area,image=self.image_s,borderwidth=1 ,command=self.on_square_press)
        self.Square_button.place(x=645,y=55)
        #   rectangle button
        self.image_R=PhotoImage(file="pictures/rectangle.png")
        self.Rectangle_button = Button(self.button_Area,image=self.image_R,borderwidth=1 ,command=self.on_rectangle_press)
        self.Rectangle_button.place(x=610,y=22)
        #   pentagon button
        self.image_P=PhotoImage(file="pictures/pentagon.png")
        self.pentagon_button = Button(self.button_Area,image=self.image_P,borderwidth=1 ,command=self.on_pentagon_press)
        self.pentagon_button.place(x=610,y=55)
        #   polygon button
        self.image_polygon=PhotoImage(file="pictures/polygon_n.png")
        self.polygon_button = Button(self.button_Area,image=self.image_polygon,borderwidth=1 ,command=self.on_N_polygon_press)
        self.polygon_button.place(x=800,y=15)
        #                                                   label of polygon
        self.entry_polygon = Entry(self.button_Area , bg="white" , width=8 )
        self.entry_polygon.place(x=800,y=75)
        self.entry_polygon.bind("<KeyRelease>", self.update_num_points)
        
        #==============================================================
        #                 text tool
        #==============================================================
        
        #text button
        self.image_txt=PhotoImage(file="pictures/texttool.png")
        self.textTitle_Button = Button(self.button_Area ,image=self.image_txt,borderwidth=1 ,command=self.on_text_press )
        self.textTitle_Button.place(x=457,y=22)
        self.entryButton = Entry(self.button_Area, textvariable=self.textValue , bg="white" , width=12 )
        self.entryButton.place(x=455,y=57)
        #text size
        self.txtLabel = Label(self.button_Area , text="Text Size",bg="grey86", width=7,font=("Times New Roman",10,"bold"))
        self.txtLabel.place(x=540,y=26)
        self.txtList = OptionMenu(self.button_Area , self.text_size , *self.text_font)
        self.txtList.configure(width=1, height=1)
        self.txtList.place(x=540,y=54)
        
        #==============================================================
        #                 color buttons all or color pallete
        #==============================================================
         # magnify
        #===========================================  
        
        # zoom in
        self.zoom_tool = ZoomTool(self.canvas, width, height)
       # self.zoom_in11=PhotoImage(file="pics/zoom_in.png")
        self.mag_button1 = Button(self.button_Area,text="Zoom++",borderwidth=1,command=self.zoom_tool.zoom_in)
        self.mag_button1.place(x=142,y=15)
        # zoom out
        #self.zoom_out22=PhotoImage(file="pics/zoom_out.png")
        self.mag_button2 = Button(self.button_Area,text="Zoom--",borderwidth=1,command=self.zoom_tool.zoom_out)
        self.mag_button2.place(x=142,y=65)
        # Create the color label
        self.label_back = Label(self.button_Area,text="Color 1",height=1 ,width=6 , bg="LightGrey")
        self.label_back.place(x=870, y=74)
        self.color_label = Label(self.button_Area,height=3, width=6 , bg=self.brush_color)
        self.color_label.place(x=870, y=17)
        
        #1
        self.redButton = Button(self.button_Area, bg="red", width=2, command=lambda: (setattr(self, 'brush_color', 'red'), self.update_color_label()))
        self.redButton.place(x=936, y=15)
        self.tomatoButton = Button(self.button_Area, text="", bg="red3", width=2, command=lambda: (setattr(self, 'brush_color', 'red3'), self.update_color_label()))
        self.tomatoButton.place(x=936, y=45)
        #2
        self.yellowButton = Button(self.button_Area, text="", bg="yellow", width=2, command=lambda: (setattr(self, 'brush_color', 'yellow'), self.update_color_label()))
        self.yellowButton.place(x=966, y=15)
        self.orangeButton = Button(self.button_Area, text="", bg="orange", width=2, command=lambda: (setattr(self, 'brush_color', 'orange'), self.update_color_label()))
        self.orangeButton.place(x=966, y=45)
        #3
        self.orangeredButton = Button(self.button_Area, text="", bg="orange red", width=2, command=lambda: (setattr(self, 'brush_color', 'orange red'), self.update_color_label()))
        self.orangeredButton.place(x=996, y=15)
        self.orange3Button = Button(self.button_Area, text="", bg="orange3", width=2, command=lambda: (setattr(self, 'brush_color', 'orange3'), self.update_color_label()))
        self.orange3Button.place(x=996, y=45)
        #4
        self.greenyellowButton = Button(self.button_Area, text="", bg="green yellow", width=2, command=lambda: (setattr(self, 'brush_color', 'green yellow'), self.update_color_label()))
        self.greenyellowButton.place(x=1026, y=15)
        self.greenButton = Button(self.button_Area, text="", bg="green", width=2, command=lambda: (setattr(self, 'brush_color', 'green'), self.update_color_label()))
        self.greenButton.place(x=1026, y=45)
        #5
        self.blue1Button = Button(self.button_Area, text="", bg="blue", width=2, command=lambda: (setattr(self, 'brush_color', 'blue1'), self.update_color_label()))
        self.blue1Button.place(x=1056, y=15)
        self.blue3Button = Button(self.button_Area, text="", bg="Lightblue3", width=2, command=lambda: (setattr(self, 'brush_color', 'blue3'), self.update_color_label()))
        self.blue3Button.place(x=1056, y=45)
        #6
        self.pink1Button = Button(self.button_Area, text="", bg="pink", width=2, command=lambda: (setattr(self, 'brush_color', 'pink'), self.update_color_label()))
        self.pink1Button.place(x=1086, y=15)
        self.plum2Button = Button(self.button_Area, text="", bg="plum2", width=2, command=lambda: (setattr(self, 'brush_color', 'plum2'), self.update_color_label()))
        self.plum2Button.place(x=1086, y=45)
        #7
        self.darksalmonButton = Button(self.button_Area, text="", bg="black", width=2, command=lambda: (setattr(self, 'brush_color', 'black'), self.update_color_label()))
        self.darksalmonButton.place(x=1116, y=15)
        self.gray12Button = Button(self.button_Area, text="", bg="gray", width=2, command=lambda: (setattr(self, 'brush_color', 'gray'), self.update_color_label()))
        self.gray12Button.place(x=1116, y=45)
        #                                                   Select Color button
        self.color_pallete=PhotoImage(file="pictures/color.png")
        self.select_color_button = Button(self.button_Area,image=self.color_pallete,borderwidth=2 ,command=self.select_color)
        self.select_color_button.place(x=1156,y=15)
        self.color_lab=Label(self.button_Area,text="Select Color",bg="Lightgrey",width=10)
        self.color_lab.place(x=1160,y=75)

    #==============================================================
    #                 magnify
    #==============================================================
    def toggle_magnify(self, event):
        self.magnify_active = not self.magnify_active

        if self.magnify_active:
            # Bind mouse move event to enable magnifying
            self.canvas.bind("<Motion>", self.on_mouse_move)
            self.canvas.bind("<Leave>", self.on_mouse_leave)
        else:
            # Unbind mouse move event to disable magnifying
            self.canvas.unbind("<Motion>")
            self.canvas.unbind("<Leave>")
            self.on_mouse_leave(None)
    def on_mouse_move(self, event):
        x, y = event.x, event.y

        # Calculate the region to magnify
        magnify_size = 150  # Adjust the size as desired
        region = (x - magnify_size, y - magnify_size, x + magnify_size, y + magnify_size)

        # Capture a screenshot of the region
        screenshot = ImageGrab.grab(region)

        # Create or update the magnifying window
        self.update_magnify_window(screenshot)

    def update_magnify_window(self, image):
        if not self.magnify_window:
            # Create a new magnifying window
            self.magnify_window = Toplevel()
            self.magnify_window.overrideredirect(True)
            self.magnify_window.geometry("200x200")  # Set the desired fixed size

            # Create a label to display the magnified image
            self.magnify_label = Label(self.magnify_window)
            self.magnify_label.pack()

        # Resize the image to fit the window
        width, height = self.magnify_window.winfo_width(), self.magnify_window.winfo_height()
        resized_image = image.resize((width, height), Image.ANTIALIAS)

        # Convert the image to Tkinter-compatible format
        photo = ImageTk.PhotoImage(resized_image)

        # Update the magnify label with the new image
        self.magnify_label.configure(image=photo)
        self.magnify_label.image = photo

    def on_mouse_leave(self, event):
        # Destroy the magnifying window when the mouse leaves the canvas
        if self.magnify_window:
            self.magnify_window.destroy()
            self.magnify_window = None
            self.magnify_label = None

    #==============================================================
    #                 shapes and brushes
    #==============================================================
    
    #                               color of brush update 
    def update_color_label(self):
            self.color_label.config(bg=self.brush_color)
    
    #                               brush code 
    def on_brush_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ReleaseButton-1>")

        self.canvas.bind("<B1-Motion>",self.brush_draw)
        self.canvas.bind("<ButtonRelease-1>",self.brush_draw_ending)
    def brush_draw(self,event):
        if self.last_x is None:
            self.last_x,self.last_y = event.x,event.y
            return
        self.canvas.create_line(self.last_x,self.last_y,event.x,event.y,width = self.stroke_size.get(),capstyle = ROUND,fill= self.brush_color)
        self.last_x , self.last_y = event.x,event.y
        self.canvas["cursor"] = 'tcross'
    def brush_draw_ending(self,event):
        self.last_x , self.last_y = None,None
    #                                               eraser function code
    def on_eraser_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ReleaseButton-1>")

        self.canvas.bind("<B1-Motion>",self.eraser_draw)
        self.canvas.bind("<ButtonRelease-1>",self.eraser_draw_ending)
    def eraser_draw(self,event):
        if self.last_x is None:
            self.last_x,self.last_y = event.x,event.y
            return
        self.canvas.create_line(self.last_x,self.last_y,event.x,event.y,width = self.stroke_size.get(), capstyle = ROUND,fill= "white")
        self.last_x , self.last_y = event.x,event.y
        self.canvas["cursor"] = "dot"#DOTBOX
    def eraser_draw_ending(self,event):
        self.last_x , self.last_y = None,None
    #                                               circle code
    def on_circle_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ReleaseButton-1>")
        self.canvas.bind("<B1-Motion>",self.draw_circle)
        self.canvas.bind("<ButtonRelease-1>",self.draw_generic_end)
    def draw_circle(self,event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x,self.last_y = event.x,event.y
            return
        radius = abs(self.last_x - event.x) + abs(self.last_y - event.y)

        x1,y1 = (self.last_x - radius),(self.last_y - radius)
        x2,y2 = (self.last_x + radius),(self.last_y + radius)

        self.shape_id = self.canvas.create_oval(x1,y1,x2,y2,outline = self.brush_color,width = self.stroke_size.get())  
    #                                               diamond button 
    def on_diamond_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_diamond)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_diamond(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        width = abs(event.x - self.last_x)
        height = abs(event.y - self.last_y)
        x1, y1 = (self.last_x - width), self.last_y
        x2, y2 = self.last_x, (self.last_y - height)
        x3, y3 = (self.last_x + width), self.last_y
        x4, y4 = self.last_x, (self.last_y + height)
        self.shape_id = self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, outline=self.brush_color, fill='', width=self.stroke_size.get())
    #                                               arrow press code
    def on_arrow_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ReleaseButton-1>")
        self.canvas.bind("<B1-Motion>", self.draw_arrow)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_arrow(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        x1, y1 = self.last_x, self.last_y
        x2, y2 = event.x, event.y
        dx, dy = x2 - x1, y2 - y1
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return
        arrowhead_size = 10
        arrowhead_angle = 0.4
        arrowhead_length = arrowhead_size * arrowhead_angle
        if dx == 0:
            if dy > 0:
                arrowhead_angle = -arrowhead_angle
            x3, y3 = x2 - arrowhead_size / 2, y2 - dy / length * arrowhead_size
            x4, y4 = x2 + arrowhead_size / 2, y2 - dy / length * arrowhead_size
            x5, y5 = x2, y2 - dy / length * arrowhead_length
        else:
            angle = math.atan(dy / dx)
            if dx < 0:
                angle += math.pi
            x3, y3 = x2 - dx / length * arrowhead_size * math.cos(angle - arrowhead_angle), y2 - dy / length * arrowhead_size * math.sin(angle - arrowhead_angle)
            x4, y4 = x2 - dx / length * arrowhead_size * math.cos(angle + arrowhead_angle), y2 - dy / length * arrowhead_size * math.sin(angle + arrowhead_angle)
            x5, y5 = x2 - dx / length * arrowhead_length * math.cos(angle), y2 - dy / length * arrowhead_length * math.sin(angle)
        self.shape_id = self.canvas.create_line(x1, y1, x2, y2, arrowshape=(arrowhead_size, arrowhead_size, arrowhead_length), fill=self.brush_color, width=self.stroke_size.get()) 
    #                                               triangle code
    def on_triangle_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ReleaseButton-1>")
        self.canvas.bind("<B1-Motion>",self.draw_triangle)
        self.canvas.bind("<ButtonRelease-1>",self.draw_generic_end)
    def draw_triangle(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        side = abs(event.x - self.last_x)
        height = abs(event.y - self.last_y)
        x1, y1 = self.last_x, self.last_y
        x2, y2 = self.last_x + side, self.last_y + height
        x3, y3 = self.last_x - side, self.last_y + height
        self.shape_id = self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline=self.brush_color, fill='', width=self.stroke_size.get())
    #                                               oval code
    def draw_oval(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        x1, y1 = self.last_x, self.last_y
        x2, y2 = event.x, event.y
        self.shape_id = self.canvas.create_oval(x1, y1, x2, y2, outline=self.brush_color, width=self.stroke_size.get())
    def on_oval_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_oval)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    #                                               Hexagon code
    def on_hexagon_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_hexagon)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_hexagon(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        side = abs(event.x - self.last_x)
        height = int(side * math.sqrt(3) / 2)
        x1, y1 = self.last_x + side, self.last_y
        x2, y2 = self.last_x + side // 2, self.last_y + height
        x3, y3 = self.last_x - side // 2, self.last_y + height
        x4, y4 = self.last_x - side, self.last_y
        x5, y5 = self.last_x - side // 2, self.last_y - height
        x6, y6 = self.last_x + side // 2, self.last_y - height
        self.shape_id = self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, outline=self.brush_color, fill='', width=self.stroke_size.get())
    #                                               Star code
    def draw_star(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        distance = ((self.last_x - event.x)**2 + (self.last_y - event.y)**2)**0.5
        x1, y1 = self.last_x, self.last_y
        x2, y2 = event.x, event.y
        angle = 2 * math.pi / 5
        points = []
        for i in range(5):
            x = (distance / 2) * math.cos(i * angle + math.pi / 2) + (x1 + x2) / 2
            y = (distance / 2) * math.sin(i * angle + math.pi / 2) + (y1 + y2) / 2
            points.extend((x, y))
            x = (distance / 4) * math.cos(i * angle + math.pi / 2 + angle / 2) + (x1 + x2) / 2
            y = (distance / 4) * math.sin(i * angle + math.pi / 2 + angle / 2) + (y1 + y2) / 2
            points.extend((x, y))
        self.shape_id = self.canvas.create_polygon(points, outline=self.brush_color, fill='', width=self.stroke_size.get())
    def on_star_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_star)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    #                                               square code
    def on_square_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_square)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_square(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        side = max(abs(self.last_x - event.x), abs(self.last_y - event.y))
        if self.last_x < event.x:
            if self.last_y < event.y:
                x1, y1 = self.last_x, self.last_y
                x2, y2 = self.last_x + side, self.last_y + side
            else:
                x1, y1 = self.last_x, self.last_y - side
                x2, y2 = self.last_x + side, self.last_y
        elif self.last_y < event.y:
            x1, y1 = self.last_x - side, self.last_y
            x2, y2 = self.last_x, self.last_y + side
        else:
            x1, y1 = self.last_x - side, self.last_y - side
            x2, y2 = self.last_x, self.last_y
        self.shape_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.brush_color, width=self.stroke_size.get())
    #                                               rectangle code
    def on_rectangle_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_rectangle(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return

        x1, y1 = self.last_x, self.last_y
        x2, y2 = event.x, event.y

        self.shape_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.brush_color, width=self.stroke_size.get())
    #                                               text button code
    def on_text_press(self):
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<ButtonRelease-3>")
        self.canvas.bind("<Button-3>", self.draw_text)
        self.canvas.bind("<ButtonRelease-3>", self.draw_generic_end)
    def draw_text(self, event):
        self.canvas.create_text(event.x , event.y , text=self.textValue.get(),font=("Arial", self.text_size.get(), "bold"), fill=self.brush_color)
    #                                               pentagon button code
    def on_pentagon_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_pentagon)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_pentagon(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return
        side = abs(event.x - self.last_x)
        radius = side / (2 * math.sin(math.radians(36))) 
        angle = math.radians(-54)
        points = []
        for _ in range(5):
            x = self.last_x + radius * math.cos(angle)
            y = self.last_y - radius * math.sin(angle)
            points.append((x, y))
            angle += math.radians(72)
        self.shape_id = self.canvas.create_polygon(*points, outline=self.brush_color, fill='', width=self.stroke_size.get())
    #                                               n polygon
    def on_N_polygon_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_N_polygon)
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def draw_N_polygon(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return

        center_x, center_y = self.last_x, self.last_y
        side = abs(event.x - self.last_x)
        radius = side / (2 * math.sin(math.radians(360 / self.num_points)))  
        angle = math.radians(-90)
        points = []
        for _ in range(self.num_points):
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
            angle += math.radians(360 / self.num_points)

        self.shape_id = self.canvas.create_polygon(*points, outline=self.brush_color, fill='', width=self.stroke_size.get())
    def update_num_points(self, event):
        try:
            self.num_points = int(self.entry_polygon.get())
        except ValueError:
            self.num_points = 7
    
    #==============================================================
    #                 selection tool
    #==============================================================
    
    def on_selection_press(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<B1-Motion>", self.draw_selection)
        self.canvas.bind("<ButtonRelease-1>", self.select_area)

    def draw_selection(self, event):
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        if self.last_x is None:
            self.last_x, self.last_y = event.x, event.y
            return

        x1, y1 = self.last_x, self.last_y
        x2, y2 = event.x, event.y

        self.shape_id = self.canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1, outline="black", width=3)

    def select_area(self, event):
        if self.last_x is None or self.last_y is None:
            return
        
        # Delete the previously placed image, if any
        self.canvas.delete("placed_image")
        
        selected_items = []
        objects = self.canvas.find_all()
        for obj_id in objects:
            bbox = self.canvas.bbox(obj_id)
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                if self.last_x <= x1 and self.last_y <= y1 and event.x >= x2 and event.y >= y2:
                    selected_items.append(obj_id)
        self.selected_objects = selected_items
        self.selected_area_start_x = self.last_x
        self.selected_area_start_y = self.last_y
        self.capture_and_place_image(event.x, event.y)

    def capture_and_place_image(self, x, y):
        if self.selected_area_start_x is not None and self.selected_area_start_y is not None:
            x1, y1 = self.selected_area_start_x, self.selected_area_start_y
            x2, y2 = x, y
            # Capture the selected area as an image
            captured_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            # Store the captured image for later use
            self.captured_image = captured_image
            # Draw a rectangle with white background where the selection was made
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white")

    def on_canvas_drag(self, event):
        if self.selected_objects:
            self.draw_selected_area()  # Draw the selection rectangle

    def on_canvas_release(self, event):
        if self.selected_objects:
            pass

    def on_canvas_click(self, event):
        if self.selected_objects:
            if self.last_x is not None and self.last_y is not None and self.selected_area_start_x is not None and self.selected_area_start_y is not None:
                dx = event.x - self.selected_area_start_x
                dy = event.y - self.selected_area_start_y
                for obj_id in self.selected_objects:
                    self.canvas.move(obj_id, dx, dy)
            self.selected_objects = []
            self.last_x = None
            self.last_y = None
            self.selected_area_start_x = None
            self.selected_area_start_y = None
            self.canvas.delete("selected_area")

    def draw_selected_area(self):
        if self.last_x is not None and self.last_y is not None:
            self.canvas.delete("selected_area")
            self.canvas.create_rectangle(self.last_x, self.last_y, self.last_x + 1, self.last_y + 1, tags="selected_area", outline="red", width=2)

    def draw_generic_end(self, event):
        self.last_x, self.last_y = None, None
        self.shape_id = None
    
    #==============================================================
    #                 color picker
    #==============================================================
    def on_color_picker_press(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.pick_color)  # Bind pick_color directly
        self.canvas.bind("<ButtonRelease-1>", self.draw_generic_end)
    def pick_color(self, event):
        
        if not self.picker_active:
            return
        x, y = event.x, event.y
        image = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
        pixel_rgb = image.getpixel((0, 0))
        # Convert the RGB values to hexadecimal color code
        hex_color = '#%02x%02x%02x' % pixel_rgb
        # Set the brush color to the picked color
        self.brush_color = hex_color
        self.update_color_label()
        self.picker_active = False
        self.canvas["cursor"] = DOTBOX
    
    #==============================================================
    #                 fill bucket
    #==============================================================
    
    def on_bucket_press(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.toggle_bucket)

    def toggle_bucket(self, event):
        if self.bucket_active:
            self.bucket_active = False
        else:
            self.bucket_active = True
            self.bucket(event)

    def bucket(self, event):
        if not self.bucket_active:
            return
        # Get the coordinates of the clicked point
        x, y = event.x, event.y
        # Get the item ID of the clicked point
        item_id = self.canvas.find_closest(x, y)[0]
        # Get the color of the clicked point
        clicked_color = self.canvas.itemcget(item_id, "fill")
        # Call the fill function to fill the connected area with the clicked color
        self.fill(x, y, clicked_color, self.brush_color)
        self.bucket_active = False

    def fill(self, x, y, target_color, fill_color):
        # Create a mask to track visited pixels
        mask = [[False] * self.canvas.winfo_height() for _ in range(self.canvas.winfo_width())]
        # Create a queue for traversal
        queue = Queue()
        # Enqueue the starting point
        queue.put((x, y))
        # Get the item ID of the starting point
        start_item_id = self.canvas.find_closest(x, y)[0]
        # Get the color of the starting point
        start_color = self.canvas.itemcget(start_item_id, "fill")
        # Check if the starting point already has the fill color
        if start_color == fill_color:
            return
        # Perform flood-fill traversal
        while not queue.empty():
            x, y = queue.get()
            # Check if the current pixel is within the canvas bounds and has the target color
            if  (x >= 0 and y >= 0 and x < self.canvas.winfo_width() and y < self.canvas.winfo_height() and not mask[x][y]
                and self.canvas.itemcget(self.canvas.find_closest(x, y)[0], "fill") == target_color 
                ):
                
                # Change the color of the current pixel
                self.canvas.itemconfig(self.canvas.find_closest(x, y), fill=fill_color)
                mask[x][y] = True

                # Enqueue neighboring pixels
                queue.put((x + 1, y))
                queue.put((x - 1, y))
                queue.put((x, y + 1))
                queue.put((x, y - 1))

    #==============================================================
    #                 SAVE IMAGE
    #==============================================================
    
    def saveImage(self):
        try:
            fileLocation = filedialog.asksaveasfilename(defaultextension="png")
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            canvasWidth = self.canvas.winfo_width()
            canvasHeight = self.canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x+canvasWidth, y+canvasHeight-22))
            img.save(fileLocation)
            if showImage := messagebox.askyesno("Paint App", "Would you to Preview the image (-_')"):
                img.show()
        except Exception as e:
            messagebox.showinfo("Paint app: " , "Error occurred    !!!\nWhile Saving...  ('_')")

    #==============================================================
    #                 open image
    #==============================================================
    
    def open_press(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            image = Image.open(file_path)

            # Resize the image to fit the canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image = image.resize((canvas_width, canvas_height), Image.ANTIALIAS)

            self.background_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

    #==============================================================
    #                 choose color
    #==============================================================
    def select_color(self):
        selected_color = colorchooser.askcolor()
        self.brush_color = selected_color[1]
        self.update_color_label()

    #==============================================================
    #                 clear canvas
    #==============================================================
    def clear_button(self):
        self.canvas.delete('all')
            
    #==============================================================
    #                 help information
    #==============================================================
    def help(self):
        self.helpText = "1. Draw by holding right button of mouse to create dotted lines.\n2.Click scroll well to put text on Canvas.\n3. Click on Select Color Option select specific color\n4. Click on Clear to clear entire Canvas\n5.Click Scroll Button to Magnify"
        messagebox.showinfo("Help" , self.helpText)
    #==============================================================
    #                 mainloop
    #==============================================================
    def run(self):
        self.screen.resizable(False , False)
        self.screen.mainloop()

    #                                   ==============================================================
    #                                                        end of the class
    #                                   ==============================================================
    
#                main body

PaintApp(1250, 720, "PAINT").run()
