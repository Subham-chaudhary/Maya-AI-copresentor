from murf import Murf, MurfRegion
from dotenv import load_dotenv, dotenv_values
load_dotenv()

class MurfTTSClient:
    def __init__(self):
        self.client = Murf(api_key=dotenv_values()['MURF_API_KEY'],
        region=MurfRegion.IN)

    def generate_speech(self, voice_id: str, style: str, text: str, rate: int, multi_native_locale: str, **kwargs):
        response = self.client.text_to_speech.generate(
            voice_id=voice_id,
            style=style,
            text=text,
            rate=rate,
            multi_native_locale=multi_native_locale,
            **kwargs
        )
        # print(f"Generated speech response: {response.status_code}")
        # print(response.content)
        print(response)
        return response.content

# Example of how to use the MurfTTSClient
if __name__ == "__main__":
    murf_generator = MurfTTSClient()
    
    audio_data = murf_generator.generate_speech(
        voice_id="en-US-natalie",
        style="Terrified",
        text="so how are you",
        rate=-38,
        multi_native_locale="en-IN"
    )
    print(audio_data)

    # if audio_data:
    #     try:
    #         with open("generated_speech.mp3", "wb") as audio_file:
    #             audio_file.write(audio_data)
    #         print("Speech generated and saved to generated_speech.mp3")
    #     except Exception as e:
    #         print(f"Error saving speech: {e}")
    # else:
    #     print("Failed to generate speech.")
