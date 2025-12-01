
import win32com.client

class PPTController:
    def __init__(self):
        self.app = win32com.client.Dispatch("PowerPoint.Application")
        self.app.Visible = 1

    def open_presentation(self, file_path):
        self.presentation = self.app.Presentations.Open(file_path)

    def start_show(self):
        self.presentation.SlideShowSettings.Run()

    def next_slide(self):
        self.presentation.SlideShowWindow.View.Next()

    def previous_slide(self):
        self.presentation.SlideShowWindow.View.Previous()

    def goto_slide(self, slide_index):
        self.presentation.SlideShowWindow.View.GotoSlide(slide_index)

    def end_show(self):
        window = self.presentation.SlideShowWindow
        if window is not None:
            window.View.Exit()  


    def close(self):
        self.app.Quit()
