import tkinter as tk
from tkinter import filedialog
from mediaplayer import MediaPlayer

class MainWindow:

    app = None
    resolution = None
    app_name = "PPO app"
    bg_color = "#212121"      #   DARK MODE APP

    def __init__(self):
        MainWindow.app = self
        self.root = tk.Tk()
        MainWindow.resolution = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.root.config(bg=MainWindow.bg_color)
        self.root.geometry(f"{MainWindow.resolution[0]}x{MainWindow.resolution[1]}+0+0")
        self.root.title(MainWindow.app_name)
        
        self.right_frame = AppBuilder.build_right_frame(self.root)
        self.left_frame = AppBuilder.build_left_frame(self.root)
        self.menu = None
        self.root.config(menu=self.menu)
        self.media_canvas = self.left_frame.get_media_canvas()
        self.video_menu = self.left_frame.get_video_menu()
        self.media_player = MediaPlayer(self.root, self.media_canvas, self.video_menu)
        
        select_media_button = tk.Button(
                                        self.right_frame, text="SELECT MEDIA",
                                        command=self.select_media_file,
                                        fg=VideoMenu.fg_color,
                                        bg=VideoMenu.through_color,
                                        )
        select_media_button.pack()

        analyse_save_button = tk.Button(
                                        self.right_frame,
                                        text="ANALYSE AND SAVE MEDIA",
                                        command=self.analyse_and_save,
                                        fg=VideoMenu.fg_color,
                                        bg=VideoMenu.through_color,
                                        )
        analyse_save_button.pack()

        save_frame_button = tk.Button(
                                        self.right_frame,
                                        text="SAVE FRAME",
                                        command=self.open_save_frame_dialog,
                                        fg=VideoMenu.fg_color,
                                        bg=VideoMenu.through_color,
                                        )
        save_frame_button.pack()

        objects_info_label = tk.Frame(
                                        self.right_frame,
                                        width=150,
                                        height=MainWindow.app.root.winfo_screenheight()/2,
                                        bg=VideoMenu.through_color,
                                      )
        objects_info_label.pack(side="bottom")



    def open_load_file_dialog(self):
        filename = filedialog.askopenfilename()
        if filename:
            return filename
        else:
            return None
        


    def open_save_frame_dialog(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPG files", "*.jpg"), ("All files", "*.*")],
            title="Save As"
        )
        self.media_player.save_current_frame(file_path)
    



    def set_screen_resolution(self):
        ...


    def select_media_file(self):
        media_file_path = self.open_load_file_dialog()
        if media_file_path is not None:
            self.media_player.display_from_path(media_file_path)


    def analyse_and_save(self):
        ...




class AppBuilder:

    @staticmethod
    def build_right_frame(master):
        right_frame = tk.Frame(master,
                               width=MainWindow.app.root.winfo_screenwidth() - MediaFrame.widget_width,
                               height=MainWindow.app.root.winfo_screenheight(),
                               background=MainWindow.bg_color)
        right_frame.pack(side="right")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        return right_frame

    @staticmethod
    def build_left_frame(master):
        left_frame = LeftFrame(master)
        left_frame.pack(side="left")
        return left_frame




class LeftFrame(tk.Frame):

    def __init__(self, master, width=1080, height=720, background="black"):
        super().__init__(master, width=width, height=height, background=background)
        self.media_frame = MediaFrame(self)

    def get_media_canvas(self):
        return self.media_frame.canvas
    
    def get_video_menu(self):
        return self.media_frame.video_menu



class MediaFrame(tk.Frame):

    bg_color = "#171717"
    widget_width = 1080

    def __init__(self, master):
        super().__init__(master, width=1080, height=MainWindow.app.root.winfo_screenheight(), background=MediaFrame.bg_color)
        self.pack(side="top")
        self.canvas = MediaCanvas(self)
        self.video_menu = VideoMenu(self)




class MediaCanvas(tk.Canvas):

    resolution = (1200, 675)    #   1:1,6 x 1920x1080 display
    scale = 1

    def __init__(self, master):
        super().__init__(master,
                         width=MediaCanvas.resolution[0]*MediaCanvas.scale,
                         height=MediaCanvas.resolution[1]*MediaCanvas.scale,
                         background="black", highlightthickness=0
                         )
        self.pack(side="top")
        self.width = MediaCanvas.resolution[0]*MediaCanvas.scale
        self.height = MediaCanvas.resolution[1]*MediaCanvas.scale




class VideoMenu(tk.Frame):

    fg_color = "#969696"
    bg_color = "#171717"
    through_color = "#3c3c3c"

    def __init__(self, master, frames=None, fps=30):
        super().__init__(master, width=MediaFrame.widget_width, height=100, bg=VideoMenu.bg_color)
        self.fps = fps
        self.video_scale = None
        self.start_stop_button = None
        self.analyse_button = None
        self.constant_analysis_button = None
        self.build(frames)

    def build(self, frames, visible=False):
        self.build_video_buttons()
        self.video_scale = self.build_video_scale(frames, visible)
        self.pack(side="top")

    def build_video_scale(self, frames, visible):
        if visible:
            video_scale = tk.Scale(self, from_=0, to=len(frames), length=600, tickinterval=300,
                                   orient=tk.HORIZONTAL, fg=VideoMenu.fg_color, bg=VideoMenu.bg_color,
                                   troughcolor=VideoMenu.through_color, command=self.update_video_frame)
        else:
            video_scale = tk.Label(self, width=MediaFrame.widget_width, background=VideoMenu.bg_color)
        video_scale.pack(side="top")
        return video_scale
    
    def disable_video_buttons(self):
        self.constant_analysis_button.config(state=tk.DISABLED)
        self.start_stop_button.config(state=tk.DISABLED)

    def enable_video_buttons(self):
        self.constant_analysis_button.config(state=tk.NORMAL)
        self.start_stop_button.config(state=tk.NORMAL)
    
    def build_video_buttons(self):
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(side="top")
        self.start_stop_button = self.build_start_stop_button()
        self.analyse_button = self.build_analyse_button()
        self.constant_analysis_button = self.build_constant_analysis_button()

    def build_start_stop_button(self):
        start_stop_button = tk.Button(self.buttons_frame, text="PLAY", fg=VideoMenu.fg_color,
                                      bg=VideoMenu.through_color, command=self.toggle_display)
        start_stop_button.pack(side="left")
        return start_stop_button
    
    def build_analyse_button(self):
        analyse_button = tk.Button(self.buttons_frame, text="ANALYSE", fg=VideoMenu.fg_color,
                                      bg=VideoMenu.through_color, command=self.analyse_current_frame)
        analyse_button.pack(side="left")
        return analyse_button

    def build_constant_analysis_button(self):
        analyse_button = tk.Button(self.buttons_frame, text="ANALYSE CONSTANTLY", fg=VideoMenu.fg_color,
                                      bg=VideoMenu.through_color, command=self.toggle_play_and_analyse)
        analyse_button.pack(side="left")
        return analyse_button

    def toggle_display(self):
        if self.start_stop_button.cget("text") == "STOP":
            self.start_stop_button.config(text="PLAY")
        else:
            self.start_stop_button.config(text="STOP")
        MainWindow.app.media_player.toggle_video_display()

    def toggle_play_and_analyse(self):
        if self.constant_analysis_button.cget("relief")==tk.RAISED:
            self.constant_analysis_button.config(relief=tk.SUNKEN)
        else:
            self.constant_analysis_button.config(relief=tk.RAISED)
        MainWindow.app.media_player.toggle_play_and_analyse()
    
    def analyse_current_frame(self):
        MainWindow.app.media_player.analyse_current_frame()

    def rebuild(self, frames=None, visible=False):
        self.video_scale.destroy()
        self.buttons_frame.destroy()
        self.build(frames, visible)

    def update_video_frame(self, value):
        if not MainWindow.app.media_player.video_runtime:
            MainWindow.app.media_player.current_frame_no = int(value)
            MainWindow.app.media_player.display_video_frame()

    def set_scale_value(self, frame_no):
        self.video_scale.set(frame_no)