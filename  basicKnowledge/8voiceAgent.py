import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
import json
import tempfile

import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf
import torch
from transformers import pipeline
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torchaudio
import edge_tts
import asyncio

device = "cuda" if torch.cuda.is_available() else "cpu"
# init TTS model
tts_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)
tts_vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(device)

torch.manual_seed(42)
speaker_embeddings = torch.randn((1, 512)).to(device)


os.environ["PATH"] = r"C:\ffmpeg-8.1\bin;" + os.environ.get("PATH", "")

stt_pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny",
    device=device,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    language="english",        # 显式指定语言
    generate_kwargs={
        "suppress_tokens": [],   # 避免重复 logits processor 警告
    },
)


def stt_from_wav_file(path: str) -> str:
    result = stt_pipe(path)
    # result is usually {"text": "...", "chunks": [...]}
    return result["text"]


def calculator(expression: str) -> str:
    """a simple calculator tool demo"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {e}"})


class ReActAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.model = "gemma4:e2b"
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. You can use the calculator tool to answer math questions. When you want to use the tool, respond with a message like this: {\"tool\": \"calculator\", \"input\": \"2 + 2\"}. If you do not know how to answer a question, just answer I don't know."
            }
        ]
        self.available_tools = {"calculator": calculator}
        self.tool = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "A simple calculator tool that evaluates basic math expressions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The math expression to evaluate, e.g., '2 + 2'."
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]

    def process_query(self, query: str) -> str:
        self.messages.append({"role": "user", "content": query})
        print("Assistant is thinking...",  end="", flush=True)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tool,
            stream=False
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        self.messages.append(response_message.model_dump())

        if tool_calls:
            for tool_call in tool_calls:
                print("tool call", tool_call.function.name)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                function_to_call = self.available_tools[tool_name]

                result = function_to_call(**tool_args)
                print(f"tool [{tool_name}] result: {result}")
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result
                })

            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tool,
                stream=False
            )
            second_response_message = second_response.choices[0].message
            self.messages.append(second_response_message.model_dump())
            return "Assistant: " +  second_response_message.content
        else:
            return "Assistant: " + response_message.content

    def chat_loop(self):
        while True:
            try:
                query = self.speech_to_text().strip()
                print("You said:", query)
                if query.lower() in ["exit", "quit"]:
                    break
                answer = self.process_query(query)
                print(answer)
                #self.text_to_speech(answer)
                self.text_to_speech_edge_version(answer)
            except Exception as e:
                print(f"Error: {e}")


    @classmethod
    def speech_to_text_model(cls) -> str:
        samplerrate = 16000
        channels = 1
        recording = []
        is_recording = False

        print("Press the space  to speak, second press to stop...")

        def callback(indata, frames, time, status):
            if is_recording:
                recording.append(indata.copy())

        stream = sd.InputStream(samplerate=samplerrate, channels=channels, callback=callback)
        stream.start()

        keyboard.wait("space")
        is_recording = True
        print("Recording, press space to stop...")

        keyboard.wait("space")
        is_recording = False
        stream.stop()
        stream.close()
        print("Recording stopped.")

        if not recording:
            print("No audio recorded.")
            return ""

        audio_data = np.concatenate(recording, axis=0)


        with tempfile.NamedTemporaryFile(suffix=".wav", delete = False) as temp_audio_file:
            sf.write(temp_audio_file.name, audio_data, samplerrate)
            temp_audio_file.flush()
            temp_audio_file.seek(0)
            audio_path = temp_audio_file.name

        with open (audio_path, "rb") as f:
            client = OpenAI(
            base_url="http://localhost:11434/v1", api_key="ollama"
            )
            response = client.audio.transcriptions.create(
            file=f, # model="dimavz/whisper-tiny:latest", model= "gemma4:e2b"

            )
            print("Transcription:", response.text)
            return response.text


    @classmethod
    def speech_to_text(cls) -> str:

        samplerrate = 16000
        channels = 1
        recording = []
        is_recording = False

        print("Press the space  to speak, second press to stop...")

        """
        
        参数	含义
        indata	当前采集到的音频数据块，形状 (frames, channels)
        frames	这一块包含多少个采样点（默认约 1024 个）
        time	时间戳信息
        status	是否有溢出/下溢等状态警告
        时间轴 ────────────────────────────────>

        callback 被调用:  [块1]     [块2]     [块3]     [块4] ...
                          │        │        │        │
        is_recording? ──→ No      Yes      Yes      Yes
                          │        ↓        ↓        ↓
                          忽略    录入!    录入!    录入!
        
        recording 列表:  [] → [...] → [...,...] → [...,...,...]
        """
        def callback(indata, frames, time, status):
            if is_recording:
                recording.append(indata.copy())

        """"
        麦克风 ──→ InputStream ──→ callback() ──→ recording 列表 (16kHz, 单声道) (每秒调用 ~15次)
        `stream.start()` 后，sounddevice 会在**后台线程**持续采集音频并调用 callback。此时还没开始录音（`is_recording=False`），所以 callback 虽然在跑，但数据被忽略。
        """
        stream = sd.InputStream(samplerate=samplerrate, channels=channels, callback=callback)
        stream.start()

        """
                时间线:
        ─────────────────────────────────────────────────────>
          [程序启动]          [用户按空格]           [用户再按空格]
             │                    │                       │
             ▼                    ▼                       ▼
         等待中...          is_recording=True        is_recording=False
         (callback忽略数据)   (callback开始录音)       (callback停止录音)
        """
        keyboard.wait("space")
        is_recording = True
        print("Recording, press space to stop...")

        keyboard.wait("space")
        is_recording = False
        stream.stop()
        stream.close()
        print("Recording stopped.")

        if  not recording:
            print("No audio recorded.")
            return ""

        audio_data = np.concatenate(recording, axis=0)

        if audio_data.ndim > 1:
            if audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)
            audio_data = audio_data.flatten()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete = False) as temp_audio_file:
            sf.write(temp_audio_file.name, audio_data, samplerrate)
            temp_audio_file.flush()
            temp_audio_file.seek(0)
            audio_path = temp_audio_file.name
        transcription = stt_from_wav_file(audio_path)


        print("Transcription:", transcription)
        return transcription


    @classmethod
    def text_to_speech_model_doesnot_support(cls, text: str) -> None:
        # ollama does not support streaming audio response yet
        client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        response = client.audio.speech.create(
            #  model="tts-1",  # text to video
            model="legraphista/Orpheus:3b-ft-q2_k",
            input=text,
            voice="alloy"  # specify the voice you want to use
        )

        audio_data = response.audio.data
        audio_bytes = bytes(audio_data)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file.flush()
            temp_audio_file.seek(0)
            audio_path = temp_audio_file.name

        data, samplerate = sf.read(audio_path)
        sd.play(data, samplerate)
        sd.wait()

    @classmethod
    def text_to_speech(cls, text: str) -> None:
        """use Microsoft SpeechT5 text to speech model to generate audio and play it"""
        # 清理文本
        clean_text = text.replace("Assistant:", "").replace("$", "").strip()
        print(f"[TTS DEBUG] Input text: '{clean_text}'")

        # use processor to convert text to input ids
        inputs = tts_processor(text=clean_text, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # generate speech with the TTS model
        with torch.no_grad():
            speech = tts_model.generate_speech(
                inputs["input_ids"],
                speaker_embeddings,
                vocoder=tts_vocoder
            )

        # debug
        print(f"[TTS DEBUG] speech shape: {speech.shape}, dtype: {speech.dtype}")
        print(f"[TTS DEBUG] min={speech.min():.4f}, max={speech.max():.4f}, mean={speech.mean():.4f}")

        # convert to numpy and play
        audio_np = speech.cpu().numpy()
        if audio_np.ndim > 1:
            audio_np = audio_np.squeeze()

        print(f"[TTS DEBUG] final shape: {audio_np.shape}, length: {len(audio_np)} samples")
        print("[TTS DEBUG] Playing audio...")

        # play（SpeechT5 output 16000）
        sd.play(audio_np, samplerate=16000)
        sd.wait()
        print("[TTS DEBUG] Playback finished.")

    @classmethod
    def text_to_speech_edge_version(cls, text: str) -> None:
        clean_text = text.replace("Assistant:", "").replace("$", "").strip()
        voice = "en-US-AriaNeural"  # specify the voice you want to use, you can find more voices in edge-tts documentation


        communicate = edge_tts.Communicate(text=clean_text, voice=voice)
        asyncio.get_event_loop().run_until_complete(
            communicate.save("temp_output.mp3")
        )

        data, samplerate = sf.read("temp_output.mp3")
        sd.play(data, samplerate)
        sd.wait()

if __name__ == "__main__":
    agent = ReActAgent()
    agent.chat_loop()
