
from pptx import Presentation

class PPTParser:
    def __init__(self, file_path):
        self.prs = Presentation(file_path)

    def extract_text_from_slides(self):
        text_runs = []
        for slide in self.prs.slides:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        text_runs.append(run.text)
        return text_runs

if __name__ == "__main__":
    parser = PPTParser("test.pptx")
    text = parser.extract_text_from_slides()
    for t in text:
        print(t)
    # print("parser: ")
    # print(parser.__eq__(parser.prs))
    # print("Parsing completed.")
    # print(str(parser.prs))