
import gradio as gr
import openai, subprocess
from pathlib import Path
import os
import azure.cognitiveservices.speech as speechsdk
import uuid

# Azure tts 设定
SPEECH_REGION='eastus'
SPEECH_KEY= 'af2d4aa2348b4b73b60487c73e0eb431'

speech_config = speechsdk.SpeechConfig(subscription='af2d4aa2348b4b73b60487c73e0eb431', region='eastus')
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name='	zh-CN-XiaoxiaoNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)



# 初始变量设定
openai.api_key = None
debatetype = '你是一名逻辑性很强的资深辩手，你擅长通过数据论据和学理论据来反驳，你的反驳总是一阵见血，而且很有逻辑性。接下来我会提出我的观点，你需要做的就是针锋相对地反驳我'
username=' '
messages = [{"role": "system", "content": debatetype}]
chat_transcript = ""
sessions={}
uuid_count=0


# stt和tts函数
def transcribe(audio,session_id):
    global messages
    global chat_transcript 
    global speech_synthesizer
    global sessions
    global api_key
    global debate_prompt
    global username
    # 获取当前会话的信息
    session = sessions[session_id]
    api_key = session["api_key"]
    debate_prompt = session["debate_prompt"]
    username = session["username"]
    messages = session["messages"]

    #对话处理
    myfile=Path(audio)
    myfile=myfile.rename(myfile.with_suffix('.wav'))
    audio_file = open(myfile,"rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]

    messages.append(system_message)

    #更新会话上下文
    session["messages"] = messages
    sessions[session_id] = session

    speech_synthesis_result = speech_synthesizer.speak_text_async(system_message['content']).get()
    stream = stream = speechsdk.AudioDataStream(speech_synthesis_result)
    stream.save_to_wav_file("outputs.wav")
    # 原windows tts 解决方案  subprocess.call(["wsay", system_message['content']])

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript,'outputs.wav'

# 记录消除函数
def eraser(session_id):
    global sessions
    global messages
    session = sessions[session_id]
    messages = session["messages"]
    messages = [{"role": "system", "content": debatetype}]
     #更新会话上下文
    session["messages"] = messages
    sessions[session_id] = session
    print('擦除成功✏️🧽')

# 初始化函数
def initway(api_key,debateprompt,name):
    global sessions
    global uuid_count
    openai.api_key =api_key
    debatetype=debateprompt
    username=name 
    messages = [{"role": "system", "content": debatetype}]

    uuid_count+=1
    session_id=str(uuid.uuid4())     # 生成UUID
    sessions[session_id]={
        "api_key": api_key,
        "debate_prompt": debateprompt,
        "username": username,
        "messages": [{"role": "system", "content": debatetype}]
    }
    print("初始化成功！🎉")
    print("当前使用者："+ username)
    print("当前uuid:"+ session_id)
    print("当前辩风:" + debatetype)
    print('当前已服务:'+str(uuid_count)+'(人次)')
    return session_id

title = "<h1 style='font-size: 40px;'><center>Xidian-Debater</center></h1>"
author="<p align='center' style='font-size: 20px;'> 人工智能学院辩论队Kashiwa出品</p>"
css1 = """
.h1 {
  text-align: center ;
}
   """

with gr.Blocks(css="#chatbot{height:300px} .overflow-y-auto{height:500px}") as init:
    gr.Markdown(title)
    gr.Markdown(author)
    with gr.Row():
        api_key = gr.Textbox(
            lines=2, placeholder="api_key Here...", label="api_key",value="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")
        debateprompt = gr.Textbox(
            lines=5, placeholder="style Here...", label="辩风" ,value="你是一名逻辑性很强的资深辩手，你擅长通过数据论据和学理论据来反驳，你的反驳总是一阵见血，而且很有逻辑性。接下来我会提出我的观点，你需要做的就是针锋相对地反驳我，每次回答不超过100个字")
       
    with gr.Row():
        session_id_get=gr.Textbox(label="当前uuid")
        name = gr.Textbox(label="当前使用者姓名")
    btn = gr.Button(value="初始化")
    btn.click(initway, [api_key, debateprompt,name],[session_id_get])


Debate= gr.Blocks(css=css1)
with Debate:
    gr.Markdown(title)
    gr.Markdown(author)
    session_idin=gr.Textbox(label="请输入uuid")
    with gr.Row():
        trans = gr.Button("🎭 转录")
        output_button = gr.Button("重置🧽")
    with gr.Row():
        audio_in=gr.Audio(source="microphone", type="filepath",label="语音输入")
        audio_out=gr.Audio(source="microphone", type="filepath",label="语音输出")
    
    output_transcript = gr.Textbox(label="对话区")
    trans.click(transcribe, [audio_in,session_idin],[output_transcript,audio_out])
    output_button.click(eraser,[session_idin])
   
# test=gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="text")

ui = gr.TabbedInterface([init,Debate],["初始化","辩论",])
ui.launch(share=True)