
class PencilArtPrompt():
    def __init__(self, gender: int):
        self.gender = gender
        if gender == 1:
            self.key1 = "boy"
            self.key2 = "male"
        else:
            self.key1 = "girl"
            self.key2 = "female"

        self.prompt = f"pencil draw, 1{self.key1}, solo, looking at viewer, realistic, sketch, portrait from photo reference, real face, monochrome, grayscale, best quality"
        self.negative_prompt = f"worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

    def get_prompt(self):
        return self.prompt, self.negative_prompt