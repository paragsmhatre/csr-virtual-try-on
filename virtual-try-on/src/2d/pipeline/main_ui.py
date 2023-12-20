import gradio as gr
from PIL import Image
from main import main
import os
import glob

def process(body,pallu,blouse,background_prompt,steps,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom):
    # clean inputs and outputs folder.
    
    files = glob.glob("./data/raw_images/temp/input/pattern/image_gen/*")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
            
    files = glob.glob("./data/raw_images/temp/input/pattern/*")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
    
    files = glob.glob("./data/raw_images/temp/output/pattern/*")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        
    # Download images to local folders
    if body:
        body = body.save("./data/raw_images/temp/input/pattern/body.png") 
    if pallu:
        pallu = pallu.save("./data/raw_images/temp/input/pattern/pallu.png") 
    if blouse:
        blouse = blouse.save("./data/raw_images/temp/input/pattern/blouse.png")
        
    # call the pipline
    input_image_path="./data/white-saree/enlarge_image__4_.png"
    pattern_image_base_path="./data/raw_images/temp/input"
    segment_dir_path="./data/white-saree/segmentations_v3"
    output_dir="./data/raw_images/temp/output"
    masking_json_path="./config/warping_points.json"
    background_image_prompt=background_prompt
    #background_image_prompt="Create a soft focus 4k HDR beautiful taken by a professional photographer background. Create a background image that showcases a minimalist and modern living room, with our bookshelf subtly complementing the aesthetic. Use warm and natural lighting to emphasize the shelf's practicality and versatility. The camera angle should be a close shot to capture the bookshelf in its entirety."
    contrast=1
    
    main(input_image_path,pattern_image_base_path,segment_dir_path,output_dir,contrast,background_image_prompt,masking_json_path,steps,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom)
    
    # Read output files
    output_list=[]
    if "enhance_image" in steps:
        output_dir="./data/raw_images/temp/output/pattern/upscale"
        dir_list = os.listdir(output_dir)
        output_list=[]
        for output_image in dir_list:
            output=Image.open(f"{output_dir}/{output_image}")
            output_list.append(output)  
    elif "background_update" in steps:
        output_dir="./data/raw_images/temp/output/pattern/image_gen"
        dir_list = os.listdir(output_dir)
        output_list=[]
        for output_image in dir_list:
            output=Image.open(f"{output_dir}/{output_image}")
            output_list.append(output)    
    elif "reconstruct" in steps:
        output=Image.open("./data/raw_images/temp/output/pattern/pattern_clean.png")
        output_list.append(output) 
    return output_list


def reconstruct(body,pallu,blouse,background_prompt,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom):
    return process(body,pallu,blouse,background_prompt,["reconstruct"],body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom)

def background_update(body,pallu,blouse,background_prompt,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom):
    return process(body,pallu,blouse,background_prompt,["reconstruct","background_update"],body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom)
    
def enhance_image(body,pallu,blouse,background_prompt,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom):
    return process(body,pallu,blouse,background_prompt,["reconstruct","background_update","enhance_image"],body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom)

with gr.Blocks() as demo:
    gr.HTML(value="""<a style="color:#5f6368;text-decoration:none;font-size:30px;" href="/">Virtual Try On : Saree V1.0</a>""")
    with gr.Row():
        with gr.Column(scale=1.5):
            body = gr.Image(type="pil",show_label=True,label="Saree Body",sources=["upload"])
            body_zoom=gr.Slider(0, 100, value=20, label="Bottom Saree Zoom level", info="Zoom level from 20 and 100%")
            top_half_body_zoom=gr.Slider(0, 100, value=25, label="Top Saree Zoom level", info="Zoom level from 30 and 100%")
            pallu = gr.Image(type="pil",show_label=True,label="Pallu",sources=["upload"])
            pallu_zoom=gr.Slider(0, 100, value=60, label="Pallu Zoom level", info="Zoom level from 60 and 100%")
            blouse = gr.Image(type="pil",show_label=True,label="blouse",sources=["upload"])
            blouse_zoom=gr.Slider(0, 100, value=30, label="Blouse Zoom level", info="Zoom level from 30 and 100%")
            background_prompt = gr.Textbox(lines=5,label="Prompt for background image",value="""Create a soft focus 4k HDR beautiful taken by a professional photographer background. Create a background image that showcases a minimalist and modern living room, with our bookshelf subtly complementing the aesthetic. Use warm and natural lighting to emphasize the shelf's practicality and versatility. The camera angle should be a close shot to capture the bookshelf in its entirety.""")
        with gr.Column(scale=4):
            output = gr.Gallery(label="Generated Images",preview=True,allow_preview=True,object_fit="contain",columns=3,height=1000)
    gr.Examples(examples=[["./data/raw_images/temp/example/body.png","./data/raw_images/temp/example/pallu.png","./data/raw_images/temp/example/blouse.png","Create a soft focus 4k HDR beautiful taken by a professional photographer background. Create a background image that showcases a minimalist and modern living room, with our bookshelf subtly complementing the aesthetic. Use warm and natural lighting to emphasize the shelf's practicality and versatility. The camera angle should be a close shot to capture the bookshelf in its entirety."]],inputs=[body,pallu,blouse,background_prompt], outputs=[output])
    with gr.Row():
        with gr.Column(scale=1.5):
            btn = gr.Button("Step 1 - Reconstruct")
            btn.click(reconstruct, inputs=[body,pallu,blouse,background_prompt,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom], outputs=[output])
        with gr.Column(scale=1.5):
            btn1 = gr.Button("Step 2 - Background Update")
            btn1.click(background_update, inputs=[body,pallu,blouse,background_prompt,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom], outputs=[output])
        with gr.Column(scale=1.5):
            btn2 = gr.Button("Step 3 - Enhance Image")
            btn2.click(enhance_image, inputs=[body,pallu,blouse,background_prompt,body_zoom,pallu_zoom,blouse_zoom,top_half_body_zoom], outputs=[output])
    
    
if __name__ == "__main__":
    demo.launch(show_api=False) 