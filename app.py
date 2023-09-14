
import gradio as gr
import openai, subprocess
from pathlib import Path
import os
import azure.cognitiveservices.speech as speechsdk


# Azure tts
# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
SPEECH_REGION='eastus'
SPEECH_KEY= 'af2d4aa2348b4b73b60487c73e0eb431'

speech_config = speechsdk.SpeechConfig(subscription='af2d4aa2348b4b73b60487c73e0eb431', region='eastus')
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name='	zh-CN-XiaoxiaoNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


# 换成你自己的api_key
openai.api_key = "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"
debatestyle = " "
messages = [{"role": "system", "content": '你是一名逻辑性很强的资深辩手，你擅长通过数据论据和学理论据来反驳，你的反驳总是一阵见血，而且很有逻辑性。接下来我会提出我的观点，你需要做的就是针锋相对地反驳我'}]
chat_transcript = ""
def transcribe(audio):
    global messages
    global chat_transcript
    global speech_synthesizer
    myfile=Path(audio)
    myfile=myfile.rename(myfile.with_suffix('.wav'))
    audio_file = open(myfile,"rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    # print(response)
    messages.append(system_message)

    speech_synthesis_result = speech_synthesizer.speak_text_async(system_message['content']).get()
    
    # 原windows tts 解决方案  subprocess.call(["wsay", system_message['content']])

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript

def eraser():
    global messages
    messages = [{"role": "system", "content": '你是一名逻辑性很强的资深辩手，你擅长通过数据论据和学理论据来反驳，你的反驳总是一阵见血，而且很有逻辑性。接下来我会提出我的观点，你需要做的就是针锋相对地反驳我，每次回答不超过100个字'}]
    print('擦除成功✏️🧽')

def initway(api_key,style):
    openai.api_key =api_key

    debatestyle = style
    print("初始化成功！🎉")



with gr.Blocks(css="#chatbot{height:300px} .overflow-y-auto{height:500px}") as init:
    with gr.Row():
        api_key = gr.Textbox(
            lines=1, placeholder="api_key Here...", label="api_key",value="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")
        style = gr.Textbox(
            lines=1, placeholder="style Here...", label="辩风" ,value="你是一名逻辑性很强的资深辩手，你擅长通过数据论据和学理论据来反驳，你的反驳总是一阵见血，而且很有逻辑性。接下来我会提出我的观点，你需要做的就是针锋相对地反驳我，每次回答不超过100个字")
        btn = gr.Button(value="初始化")
        btn.click(initway, [api_key, style])

with gr.Blocks(css="#chatbot{height:300px} .overflow-y-auto{height:500px}") as Debate:
    with gr.Row():
        audio=gr.Audio(source="microphone", type="filepath",label="语音输入")
        trans = gr.Button("🎭 转录")
        output_button = gr.Button("重置🧽")
    with gr.Row():
        output_transcript = gr.Textbox(label="语音转录输出")
    trans.click(transcribe, [audio],[output_transcript])
    output_button.click(eraser)
   
test=gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="text")

ui = gr.TabbedInterface([init,Debate,test],["初始化","辩论","测试"])
ui.launch()