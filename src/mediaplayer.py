import cv2
import tkinter as tk
import file
from PIL import Image, ImageTk
from model import Model

class MediaPlayer:

    pic_extensions = ['jpg', 'png', 'jpeg', 'bmp']
    media_scale_factor = 1

    def __init__(self, app, media_canvas, video_menu):
        self.app = app
        self.media_canvas = media_canvas
        self.video_menu = video_menu
        self.cap = None
        self.photo = None
        self.media_extension = None
        self.video_runtime = False
        self.current_frame_no = 0
        self.current_frame = None
        self.current_media_path = None
        self.loaded_frames = None
        self.last_object_drawn = None
        self.scale_factor = 1
        self.constant_analysis = False
        self.detected_object_labels = []

    def display_from_path(self, media_path):

        if self.cap is not None:
            self.cap.release()

        self.media_canvas.delete("all")

        self.current_media_path = media_path
        self.media_extension = file.get_file_extension(media_path)

        if self.media_extension not in MediaPlayer.pic_extensions:
            self.display_video_media(media_path)
            self.video_menu.enable_video_buttons()
            self.video_menu.start_stop_button.config(text="PLAY")
            self.video_runtime = False
        else:
            self.display_image_media(media_path)
            self.video_menu.disable_video_buttons()

    def display_video_media(self, media_path):
        self.cap = cv2.VideoCapture(media_path)
        self.loaded_frames = self.get_video_frames(media_path)
        width, height = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.scale_factor = self.get_scale_factor(width, height)
        self.rebuild_video_menu(self.loaded_frames)
        self.current_frame_no = 0
        self.display_video_frame()

    def display_image_media(self, media_path):
        image = cv2.imread(media_path)
        self.scale_factor = self.get_scale_factor(image.shape[1], image.shape[0])
        image = self.scale_frame(image)
        self.current_frame = image
        self.photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        self.last_object_drawn = self.media_canvas.create_image(self.media_canvas.width/2, self.media_canvas.height/2, image=self.photo)

    def toggle_video_display(self):

        if self.video_runtime:
            self.video_runtime = False
        else:
            self.video_runtime = True
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_no)
            self.update_from_cap()

    def display_video_frame(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_no)
        ret, frame = self.cap.read()
        if ret:
            frame = self.scale_frame(frame)
            self.current_frame = frame
            self.media_canvas.delete(self.photo) if self.photo is not None else ...
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            if self.last_object_drawn is not None:
                self.media_canvas.delete(self.last_object_drawn)
            self.last_object_drawn = self.media_canvas.create_image(self.media_canvas.width/2, self.media_canvas.height/2, image=self.photo)

    def analyse_current_frame(self):
        result = Model.predict(self.current_frame)
        objects_coords = Model.get_detected_elements()
        annotated = result[0].plot()
        #annotated = self.scale_frame(annotated)
        self.current_frame = annotated
        self.display_analysed_frame(annotated, objects_coords)

    def toggle_play_and_analyse(self):
        self.constant_analysis = True if self.constant_analysis == False else False

    def display_analysed_frame(self, frame, objects_coords):
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.last_object_drawn = self.media_canvas.create_image(self.media_canvas.width/2, self.media_canvas.height/2, image=self.photo)
        self.detected_object_labels.clear()
        for id in objects_coords:
            label_object = self.draw_object_label(id, objects_coords[id])
            self.detected_object_labels.append(label_object)

    def delete_object_labels(self):
        for label_object in self.detected_object_labels:
            for text, bg in label_object:
                self.media_canvas.delete(text)
                self.media_canvas.delete(bg)
        
    def draw_object_label(self, id, coords):
        label_x_pos =  coords[0] + self.media_canvas.bbox(self.last_object_drawn)[0]
        label_y_pos =  coords[1] + self.media_canvas.bbox(self.last_object_drawn)[1]
        label = self.media_canvas.create_text(label_x_pos, label_y_pos, text=f"{id}: {coords[0]}x{coords[1]}", font=("Helvetica", 12), fill="white")
        bbox = self.media_canvas.bbox(label)
        label_bg_rect = self.media_canvas.create_rectangle(bbox, fill="black")
        self.media_canvas.tag_raise(label, label_bg_rect)
        return (label, label_bg_rect)
        

    def update_from_cap(self):
        if self.video_runtime:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame_no += 1
                self.media_canvas.delete(self.photo) if self.photo is not None else ...
                if self.constant_analysis:
                    frame = self.scale_frame(frame)
                    result = Model.predict(frame)
                    frame = result[0].plot()
                    self.draw_photo(frame)
                    self.current_frame = frame
                    self.detected_object_labels.clear()
                    objects_coords = Model.get_detected_elements()
                    for id in objects_coords:
                        label_object = self.draw_object_label(id, objects_coords[id])
                        self.detected_object_labels.append(label_object)
                else:
                    self.current_frame = frame
                    frame = self.scale_frame(frame)
                    self.draw_photo(frame)
                self.video_menu.set_scale_value(self.current_frame_no)
            self.app.after(10, self.update_from_cap)


    def draw_photo(self, frame):
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        if self.last_object_drawn is not None:
            self.media_canvas.delete(self.last_object_drawn)
        self.last_object_drawn = self.media_canvas.create_image(self.media_canvas.width/2, self.media_canvas.height/2, image=self.photo)
                

    def rebuild_video_menu(self, frames):
        if len(frames) > 1:
            self.video_menu.rebuild(frames, visible=True)
        else:
            self.video_menu.rebuild(frames)

    def get_video_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return []

        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()
        return frames
    
    def save_current_frame(self, file_path):
        if file_path:
            cv2.imwrite(file_path, self.current_frame)

    def scale_frame(self, frame):
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        new_dimensions = (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor))
        resized_image = cv2.resize(frame, new_dimensions, interpolation=cv2.INTER_LINEAR)
        return resized_image
    
    def get_scale_factor(self, frame_width, frame_height):
        scale = 1
        horizontal_scale = self.media_canvas.width/frame_width
        vertical_scale = self.media_canvas.height/frame_height
        if horizontal_scale < vertical_scale:
            scale = horizontal_scale
        else:
            scale = vertical_scale
        return scale