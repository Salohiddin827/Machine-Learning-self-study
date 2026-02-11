import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import glob
import json

class LabelAnnotationTool:
    def __init__(self, root):
        self.root = root
        # Paths - use consistent path naming without trailing slashes
        self.images_dir = "sample"
        self.labels_dir = "labels"
        self.labels2_dir = ""
        self.output_dir = "new_labels"
        self.skipped_images_dir = "skipped_labels/images"
        self.skipped_labels_dir = "skipped_labels/labels"
        self.state_file = "review_state.json"
        
        # Create output directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.skipped_images_dir, exist_ok=True)
        os.makedirs(self.skipped_labels_dir, exist_ok=True)
        
        # Review state tracking
        self.reviewed_images = set()
        self.load_review_state()
        
        # Get all image files (supports png/jpg/jpeg, lower & upper-case)
        self.image_files = []
        exts = ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]
        for ext in exts:
            self.image_files += glob.glob(os.path.join(self.images_dir, ext))
        self.image_files = sorted(list(set(self.image_files)))  # Remove duplicates and sort
        self.current_index = 0
        
        # Current image data
        self.current_image = None
        self.current_photo = None
        self.labels = []  # List of [class_id, x_center, y_center, width, height]
        
        # Drawing state
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.current_class = 0
        self.selected_box = None
        self.temp_rect_id = None
        
        # Copy/paste state
        self.clipboard = []  # Store copied labels
        self.selected_boxes = []  # List of selected box indices for multi-select
        self.copy_mode = False  # Toggle for copy mode
        
        # Reference line state
        self.ref_line_y = 0.5  # normalized position (0-1) relative to image height
        self.dragging_line = False
        self.show_ref_line = True  # toggle visibility
        
        # Crosshair state
        self.show_crosshair = True  # toggle crosshair visibility
        self.mouse_x = 0
        self.mouse_y = 0
        self.crosshair_h_id = None  # horizontal line ID
        self.crosshair_v_id = None  # vertical line ID
        
        # Colors for each class (0-9)
        self.colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'orange', 'purple', 'brown', 'pink']
        
        # Setup UI
        self.setup_ui()
        
        # Load first image or continue from last position
        if self.image_files:
            start_index = self.get_starting_index()
            self.load_image(start_index)
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Top frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Navigation buttons
        tk.Button(control_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Save", command=self.save_labels).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Skip (/)", command=self.skip_image, bg="#ffddaa").pack(side=tk.LEFT, padx=2)
        
        # Reference line toggle
        tk.Button(control_frame, text="Toggle Line (l)", command=self.toggle_ref_line, bg="#ccddff").pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Toggle Crosshair (h)", command=self.toggle_crosshair, bg="#ccffcc").pack(side=tk.LEFT, padx=2)
        
        # Image counter and review status
        self.counter_label = tk.Label(control_frame, text="0/0")
        self.counter_label.pack(side=tk.LEFT, padx=10)
        
        self.review_status_label = tk.Label(control_frame, text="Not Reviewed", fg="red")
        self.review_status_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Next Unreviewed (n)", command=self.next_unreviewed).pack(side=tk.LEFT, padx=5)
        
        # Class selection
        tk.Label(control_frame, text="Current Class:").pack(side=tk.LEFT, padx=5)
        self.class_var = tk.IntVar(value=0)
        for i in range(10):
            tk.Radiobutton(control_frame, text=str(i), variable=self.class_var, 
                          value=i, bg=self.colors[i]).pack(side=tk.LEFT)
        
        # Delete button
        tk.Button(control_frame, text="Delete Selected (Del)", command=self.delete_selected).pack(side=tk.LEFT, padx=10)
        
        # Copy/Paste buttons
        tk.Button(control_frame, text="Copy Mode (x)", command=self.toggle_copy_mode).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Copy Selected (c)", command=self.copy_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Clear Selection", command=self.clear_selection).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Paste (v)", command=self.paste_labels).pack(side=tk.LEFT, padx=2)
        
        # Copy mode and clipboard status labels
        self.copy_mode_label = tk.Label(control_frame, text="Copy Mode: OFF", fg="gray")
        self.copy_mode_label.pack(side=tk.LEFT, padx=10)
        
        self.clipboard_label = tk.Label(control_frame, text="Clipboard: Empty", fg="gray")
        self.clipboard_label.pack(side=tk.LEFT, padx=10)
        
        # Instructions
        instructions = tk.Label(control_frame, text="Draw: Click & Drag | Force Draw: Shift+Drag | Copy Mode: x | Select: Click | Copy: c | Clear: Esc | Paste: v | Delete: Del/d | Class: 0-4 | Skip: /")
        instructions.pack(side=tk.LEFT, padx=10)
        
        # Canvas for image display
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)  # Track mouse for crosshair
        
        # Bind keyboard events
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("d", lambda e: self.delete_selected())
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Button-4>", lambda e: self.prev_image())
        self.root.bind("<Button-5>", lambda e: self.next_image())
        self.root.bind("<s>", lambda e: self.save_labels())
        self.root.bind("n", lambda e: self.next_unreviewed())
        self.root.bind("x", lambda e: self.toggle_copy_mode())
        self.root.bind("c", lambda e: self.copy_selected())
        self.root.bind("v", lambda e: self.paste_labels())
        self.root.bind("<Escape>", lambda e: self.clear_selection())
        
        # Bind class change with 0-9 keys
        for i in range(10):
            self.root.bind(str(i), lambda e, c=i: self.change_class(c))
        
        # Bind skip key
        self.root.bind("/", lambda e: self.skip_image())
        
        # Bind line toggle key
        self.root.bind("l", lambda e: self.toggle_ref_line())
        
        # Bind crosshair toggle key
        self.root.bind("h", lambda e: self.toggle_crosshair())
    
    def load_image(self, index):
        if index < 0 or index >= len(self.image_files):
            return
        
        self.current_index = index
        image_path = self.image_files[index]
        base_name = os.path.basename(image_path)
        
        # Update counter
        self.counter_label.config(text=f"{index + 1}/{len(self.image_files)}")
        
        # Update review status
        if base_name in self.reviewed_images:
            self.review_status_label.config(text="✓ Reviewed", fg="green")
        else:
            self.review_status_label.config(text="Not Reviewed", fg="red")
        
        # Load image
        self.current_image = Image.open(image_path)
        self.img_width, self.img_height = self.current_image.size
        
        # Load labels - prioritize new_labels if it exists
        self.labels = []
        # Get label filename by replacing image extension with .txt
        label_base_name = os.path.splitext(base_name)[0] + '.txt'
        
        # Check if edited version exists in new_labels
        label_path_new = os.path.join(self.output_dir, label_base_name)
        
        if os.path.exists(label_path_new):
            # Load only from new_labels (this is the edited version)
            print(f"Loading from new_labels: {label_path_new}")
            with open(label_path_new, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        # Ensure class_id is valid (0-9)
                        if 0 <= class_id <= 9:
                            self.labels.append([class_id, float(parts[1]), float(parts[2]), 
                                              float(parts[3]), float(parts[4])])
        else:
            # Load from original folders and merge
            # Load from labels folder (only if labels_dir is not empty)
            if self.labels_dir:
                label_path1 = os.path.join(self.labels_dir, label_base_name)
                if os.path.exists(label_path1):
                    print(f"Loading from labels_dir: {label_path1}")
                    with open(label_path1, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) == 5:
                                class_id = int(parts[0])
                                # Ensure class_id is valid (0-9)
                                if 0 <= class_id <= 9:
                                    self.labels.append([class_id, float(parts[1]), float(parts[2]), 
                                                      float(parts[3]), float(parts[4])])
            
            # Load from labels2 folder
            label_path2 = os.path.join(self.labels2_dir, label_base_name)
            if os.path.exists(label_path2):
                print(f"Loading from labels2_dir: {label_path2}")
                with open(label_path2, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            # Ensure class_id is valid (0-9)
                            if 0 <= class_id <= 9:
                                self.labels.append([class_id, float(parts[1]), float(parts[2]), 
                                                  float(parts[3]), float(parts[4])])
        
        print(f"Loaded {len(self.labels)} labels for {base_name}")
        
        self.selected_box = None
        self.selected_boxes = []
        self.display_image()
    
    def display_image(self):
        # Create a copy of the image to draw on
        img_copy = self.current_image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Draw all bounding boxes
        for i, label in enumerate(self.labels):
            class_id, x_center, y_center, width, height = label
            
            # Convert normalized coordinates to pixel coordinates
            x1 = int((x_center - width / 2) * self.img_width)
            y1 = int((y_center - height / 2) * self.img_height)
            x2 = int((x_center + width / 2) * self.img_width)
            y2 = int((y_center + height / 2) * self.img_height)
            
            # Draw rectangle - thicker for selected boxes
            color = self.colors[class_id]
            if i in self.selected_boxes:
                line_width = 6  # Selected boxes are thicker
            elif i == self.selected_box:
                line_width = 5
            else:
                line_width = 4
            draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)
            
            # Draw class label
            draw.text((x1, y1 - 15), f"Class {class_id}", fill=color)
        
        # Draw reference line if enabled
        if self.show_ref_line:
            line_y = int(self.ref_line_y * self.img_height)
            draw.line([(0, line_y), (self.img_width, line_y)], fill='cyan', width=3)
            # Draw small text showing line position
            draw.text((10, line_y + 5), f"Y: {self.ref_line_y:.2f}", fill='cyan')
        
        # Draw image filename at the bottom center
        if self.current_index < len(self.image_files):
            image_name = os.path.basename(self.image_files[self.current_index])
            # Draw filename with white background
            text_width = len(image_name) * 8  # Approximate
            text_x = (self.img_width - text_width) // 2
            text_y = self.img_height - 30
            
            # Draw semi-transparent background
            draw.rectangle([text_x - 5, text_y - 5, text_x + text_width + 5, text_y + 20], 
                          fill=(0, 0, 0, 180), outline='white', width=2)
            draw.text((text_x, text_y), image_name, fill='white')
        
        # Resize image to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate scaling to fit canvas
            scale = min(canvas_width / self.img_width, canvas_height / self.img_height, 1.0)
            new_width = int(self.img_width * scale)
            new_height = int(self.img_height * scale)
            
            img_copy = img_copy.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage and display
        self.current_photo = ImageTk.PhotoImage(img_copy)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def on_mouse_down(self, event):
        # Get click position in image coordinates
        x, y = self.canvas_to_image_coords(event.x, event.y)
        
        # Check if clicking near the reference line (within 10 pixels)
        if self.show_ref_line:
            line_y = self.ref_line_y * self.img_height
            if abs(y - line_y) < 10:
                self.dragging_line = True
                return
        
        # Check if Shift is pressed to force drawing mode (draw inside boxes)
        shift_pressed = event.state & 0x1
        
        # Check if clicking on existing box (only if Shift is not pressed)
        clicked_box = None if shift_pressed else self.find_box_at_position(x, y)
        
        if clicked_box is not None and not shift_pressed:
            if self.copy_mode:
                # In copy mode, toggle selection on the clicked box
                if clicked_box in self.selected_boxes:
                    self.selected_boxes.remove(clicked_box)
                else:
                    self.selected_boxes.append(clicked_box)
            else:
                # Normal mode: check if Ctrl is pressed for multi-select
                if event.state & 0x4:  # Ctrl only (Shift is used for drawing now)
                    if clicked_box in self.selected_boxes:
                        self.selected_boxes.remove(clicked_box)
                    else:
                        self.selected_boxes.append(clicked_box)
                else:
                    self.selected_boxes = [clicked_box]
            
            self.selected_box = clicked_box
            self.display_image()
        else:
            # Start drawing new box (only if not in copy mode)
            # When Shift is pressed, force drawing even if clicking inside a box
            if not self.copy_mode:
                self.drawing = True
                self.start_x = x
                self.start_y = y
                self.selected_box = None
                self.selected_boxes = []
    
    def on_mouse_drag(self, event):
        if self.dragging_line:
            # Update line position
            _, y = self.canvas_to_image_coords(event.x, event.y)
            self.ref_line_y = max(0.0, min(1.0, y / self.img_height))
            self.display_image()
            return
        
        if self.drawing:
            # Delete previous temporary rectangle
            if self.temp_rect_id:
                self.canvas.delete(self.temp_rect_id)
            
            # Get current position in canvas coordinates
            end_x, end_y = event.x, event.y
            
            # Get scale factor for drawing on canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                scale = min(canvas_width / self.img_width, canvas_height / self.img_height, 1.0)
                # Convert image coordinates to canvas coordinates
                canvas_start_x = self.start_x * scale
                canvas_start_y = self.start_y * scale
                
                # Get current class color
                color = self.colors[self.class_var.get()]
                
                # Draw temporary rectangle on canvas
                self.temp_rect_id = self.canvas.create_rectangle(
                    canvas_start_x, canvas_start_y, end_x, end_y,
                    outline=color, width=2, dash=(5, 5)
                )
    
    def on_mouse_up(self, event):
        if self.dragging_line:
            self.dragging_line = False
            return
        
        if self.drawing:
            # Delete temporary rectangle
            if self.temp_rect_id:
                self.canvas.delete(self.temp_rect_id)
                self.temp_rect_id = None
            
            end_x, end_y = self.canvas_to_image_coords(event.x, event.y)
            
            # Create new box
            x1, x2 = min(self.start_x, end_x), max(self.start_x, end_x)
            y1, y2 = min(self.start_y, end_y), max(self.start_y, end_y)
            
            # Convert to normalized YOLO format
            x_center = ((x1 + x2) / 2) / self.img_width
            y_center = ((y1 + y2) / 2) / self.img_height
            width = (x2 - x1) / self.img_width
            height = (y2 - y1) / self.img_height
            
            # Only add if box has valid size
            if width > 0.01 and height > 0.01:
                class_id = self.class_var.get()
                self.labels.append([class_id, x_center, y_center, width, height])
                self.display_image()
            
            self.drawing = False
            self.start_x = None
            self.start_y = None
    
    def on_mouse_move(self, event):
        """Track mouse position for crosshair"""
        if not self.show_crosshair:
            return
        
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.draw_crosshair()
    
    def draw_crosshair(self):
        """Draw crosshair lines on canvas"""
        if not self.show_crosshair or not self.current_photo:
            return
        
        # Delete old crosshair lines
        if self.crosshair_h_id:
            self.canvas.delete(self.crosshair_h_id)
        if self.crosshair_v_id:
            self.canvas.delete(self.crosshair_v_id)
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Draw horizontal line (full width)
        self.crosshair_h_id = self.canvas.create_line(
            0, self.mouse_y, canvas_width, self.mouse_y,
            fill='yellow', width=1, dash=(3, 3)
        )
        
        # Draw vertical line (full height)
        self.crosshair_v_id = self.canvas.create_line(
            self.mouse_x, 0, self.mouse_x, canvas_height,
            fill='yellow', width=1, dash=(3, 3)
        )
    
    def on_right_click(self, event):
        # Delete box on right-click
        x, y = self.canvas_to_image_coords(event.x, event.y)
        clicked_box = self.find_box_at_position(x, y)
        
        if clicked_box is not None:
            self.selected_boxes = [clicked_box]
            self.selected_box = clicked_box
            self.delete_selected()
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        # Convert canvas coordinates to image coordinates
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            scale = min(canvas_width / self.img_width, canvas_height / self.img_height, 1.0)
            img_x = canvas_x / scale
            img_y = canvas_y / scale
        else:
            img_x = canvas_x
            img_y = canvas_y
        
        return img_x, img_y
    
    def find_box_at_position(self, x, y):
        # Find which box (if any) contains the given position
        for i, label in enumerate(self.labels):
            class_id, x_center, y_center, width, height = label
            
            # Convert to pixel coordinates
            x1 = (x_center - width / 2) * self.img_width
            y1 = (y_center - height / 2) * self.img_height
            x2 = (x_center + width / 2) * self.img_width
            y2 = (y_center + height / 2) * self.img_height
            
            if x1 <= x <= x2 and y1 <= y <= y2:
                return i
        
        return None
    
    def delete_selected(self):
        # Delete all selected boxes, removing in reverse order to maintain indices
        if self.selected_boxes:
            for idx in sorted(self.selected_boxes, reverse=True):
                if idx < len(self.labels):
                    del self.labels[idx]
            self.selected_boxes = []
            self.selected_box = None
            self.display_image()
        elif self.selected_box is not None and self.selected_box < len(self.labels):
            del self.labels[self.selected_box]
            self.selected_box = None
            self.display_image()
    
    def change_class(self, new_class):
        self.class_var.set(new_class)
        if self.selected_box is not None and self.selected_box < len(self.labels):
            self.labels[self.selected_box][0] = new_class
            self.display_image()
    
    def toggle_copy_mode(self):
        """Toggle copy mode on/off"""
        self.copy_mode = not self.copy_mode
        if self.copy_mode:
            self.copy_mode_label.config(text="Copy Mode: ON", fg="orange")
            messagebox.showinfo("Copy Mode", "Copy mode enabled!\nClick on labels to select them.\nPress C to copy or Esc to exit.")
        else:
            self.copy_mode_label.config(text="Copy Mode: OFF", fg="gray")
            self.selected_boxes = []
            self.selected_box = None
            self.display_image()
    
    def clear_selection(self):
        """Clear all selected labels"""
        self.selected_boxes = []
        self.selected_box = None
        if self.copy_mode:
            self.copy_mode_label.config(text="Copy Mode: ON", fg="orange")
        self.display_image()
    
    def copy_selected(self):
        """Copy selected labels to clipboard"""
        if self.selected_boxes:
            # Copy all selected boxes
            self.clipboard = []
            for idx in self.selected_boxes:
                if idx < len(self.labels):
                    # Deep copy the label
                    self.clipboard.append(self.labels[idx][:])
            
            # Update clipboard status
            self.clipboard_label.config(
                text=f"Clipboard: {len(self.clipboard)} label(s) copied",
                fg="green"
            )
            messagebox.showinfo("Copied", f"{len(self.clipboard)} label(s) copied to clipboard")
        elif self.selected_box is not None and self.selected_box < len(self.labels):
            # Copy single selected box
            self.clipboard = [self.labels[self.selected_box][:]]
            self.clipboard_label.config(
                text=f"Clipboard: 1 label copied",
                fg="green"
            )
            messagebox.showinfo("Copied", "1 label copied to clipboard")
        else:
            messagebox.showwarning("No Selection", "Please select a label to copy")
    
    def paste_labels(self):
        """Paste labels from clipboard"""
        if not self.clipboard:
            messagebox.showwarning("Empty Clipboard", "No labels in clipboard. Copy some labels first.")
            return
        
        # Add all clipboard labels to current image
        for label in self.clipboard:
            self.labels.append(label[:])  # Deep copy each label
        
        # Update display
        self.display_image()
        self.clipboard_label.config(
            text=f"Clipboard: {len(self.clipboard)} label(s)",
            fg="blue"
        )
    
    def toggle_ref_line(self):
        """Toggle the visibility of the reference line"""
        self.show_ref_line = not self.show_ref_line
        self.display_image()
    
    def toggle_crosshair(self):
        """Toggle the visibility of the crosshair"""
        self.show_crosshair = not self.show_crosshair
        if not self.show_crosshair:
            # Clear crosshair when disabled
            if self.crosshair_h_id:
                self.canvas.delete(self.crosshair_h_id)
                self.crosshair_h_id = None
            if self.crosshair_v_id:
                self.canvas.delete(self.crosshair_v_id)
                self.crosshair_v_id = None
    
    def skip_image(self):
        """Skip current image and its label to skipped folders"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        import shutil
        image_path = self.image_files[self.current_index]
        base_name = os.path.basename(image_path)
        # Get label filename by replacing image extension with .txt
        label_base_name = os.path.splitext(base_name)[0] + '.txt'
        
        # Move image to skipped folder
        skipped_image_path = os.path.join(self.skipped_images_dir, base_name)
        try:
            shutil.move(image_path, skipped_image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move image: {str(e)}")
            return
        
        # Move label if it exists - check all possible locations
        label_sources = [
            os.path.join(self.output_dir, label_base_name),
            os.path.join(self.labels_dir, label_base_name),
            os.path.join(self.labels2_dir, label_base_name)
        ]
        
        for label_path in label_sources:
            if os.path.exists(label_path):
                skipped_label_path = os.path.join(self.skipped_labels_dir, label_base_name)
                try:
                    shutil.move(label_path, skipped_label_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to move label: {str(e)}")
                break
        
        # Remove from reviewed images if it was there
        if base_name in self.reviewed_images:
            self.reviewed_images.remove(base_name)
        
        # Reload image files list
        self.image_files = []
        exts = ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]
        for ext in exts:
            self.image_files += glob.glob(os.path.join(self.images_dir, ext))
        self.image_files = sorted(list(set(self.image_files)))
        
        # Save state
        self.save_review_state()
        
        # Load next image
        if self.current_index >= len(self.image_files) and len(self.image_files) > 0:
            self.current_index = len(self.image_files) - 1
        
        if self.image_files:
            self.load_image(self.current_index)
            messagebox.showinfo("Skipped", "Image and label moved to skipped_labels folder")
        else:
            messagebox.showinfo("Completed", "All images have been reviewed or skipped!")
    
    def save_labels(self, show_message=True):
        if not self.image_files:
            return
        
        # Get current image base name
        image_path = self.image_files[self.current_index]
        base_name = os.path.basename(image_path)
        # Get label filename by replacing image extension with .txt
        label_base_name = os.path.splitext(base_name)[0] + '.txt'
        output_path = os.path.join(self.output_dir, label_base_name)
        
        # Save labels in YOLO format
        with open(output_path, 'w') as f:
            for label in self.labels:
                class_id, x_center, y_center, width, height = label
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        # Mark as reviewed
        image_name = os.path.basename(image_path)
        self.reviewed_images.add(image_name)
        self.save_review_state()
        
        # Update review status
        self.review_status_label.config(text="✓ Reviewed", fg="green")
        
        if show_message:
            messagebox.showinfo("Saved", f"Labels saved to {output_path}")
    
    def prev_image(self):
        if self.current_index > 0:
            self.save_labels(show_message=False)
            self.load_image(self.current_index - 1)
    
    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.save_labels(show_message=False)
            self.load_image(self.current_index + 1)
    
    def next_unreviewed(self):
        """Jump to the next unreviewed image"""
        for i in range(self.current_index + 1, len(self.image_files)):
            image_name = os.path.basename(self.image_files[i])
            if image_name not in self.reviewed_images:
                self.save_labels(show_message=False)
                self.load_image(i)
                return
        
        # If no unreviewed images found after current, search from beginning
        for i in range(0, self.current_index):
            image_name = os.path.basename(self.image_files[i])
            if image_name not in self.reviewed_images:
                self.save_labels(show_message=False)
                self.load_image(i)
                return
        
        messagebox.showinfo("Complete", "All images have been reviewed!")
    
    def load_review_state(self):
        """Load the review state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.reviewed_images = set(data.get('reviewed_images', []))
                    return data.get('last_index', 0)
            except:
                pass
        return 0
    
    def save_review_state(self):
        """Save the review state to file"""
        data = {
            'reviewed_images': list(self.reviewed_images),
            'last_index': self.current_index
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_starting_index(self):
        """Get the starting index based on review state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_index', 0)
            except:
                pass
        return 0
    
    def on_closing(self):
        """Handle window close event"""
        # Save current labels before closing
        if self.image_files and self.current_index < len(self.image_files):
            self.save_labels(show_message=False)
        
        # Save review state
        self.save_review_state()
        
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = LabelAnnotationTool(root)
    root.mainloop()