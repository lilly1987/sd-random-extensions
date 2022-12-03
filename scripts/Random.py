import math
import os
import sys
import traceback
import random
import modules.scripts as scripts
import gradio as gr
from modules.processing import Processed,process_images

# 개조용 추가 로드
import re,random
from modules.images import FilenameGenerator
from PIL import Image
from modules import processing,shared,generation_parameters_copypaste
from modules.shared import opts,state,hypernetworks
from modules.sd_samplers import samplers,samplers_for_img2img ,set_samplers
import logging
from my import *
from modules.hypernetworks import hypernetwork
from modules.ui import create_refresh_button

is_debug = getattr(opts, f"is_debug", False)
#setattr(opts, f"{__name__}_debug", is_debug)

logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.WARNING)
#logger.setLevel(logging.ERROR)
#logger.setLevel(logging.CRITICAL)

# 일반 핸들러. 할 필요 업음. 이미 메인에서 출력해줌
streamFormatter = logging.Formatter("Random %(asctime)s %(levelname)s\t: %(message)s")
streamHandler = logging.StreamHandler()
if is_debug :
    streamHandler.setLevel(logging.DEBUG)
else:
    streamHandler.setLevel(logging.INFO)
#streamHandler.setLevel(logging.WARNING)
streamHandler.setFormatter(streamFormatter)
logger.addHandler(streamHandler)

# 파일 핸들러
fileFormatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
fileHandler = logging.FileHandler("Random.py.log")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(fileFormatter)
logger.addHandler(fileHandler)

if is_debug :
    logger.debug('==== DEBUG ====')
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

logger.info(' Load ')

def apply_hypernetwork(x):
    if x.lower() in ["", "none"]:
        name = None
    else:
        name = hypernetwork.find_closest_hypernetwork_name(x)
        if not name:
            raise RuntimeError(f"Unknown hypernetwork: {x}")
    hypernetwork.load_hypernetwork(name)

def apply_samplers():
    #global samplers, samplers_for_img2img
    #
    #hidden = set(opts.hide_samplers)
    #hidden_img2img = set(opts.hide_samplers + ['PLMS'])
    #
    #samplers = [x for x in all_samplers if x.name not in hidden]
    #samplers_for_img2img = [x for x in all_samplers if x.name not in hidden_img2img]
    #
    #samplers_map.clear()
    #for sampler in all_samplers:
    #    samplers_map[sampler.name.lower()] = sampler.name
    #    for alias in sampler.aliases:
    #        samplers_map[alias.lower()] = sampler.name
    
    set_samplers()
    logger.debug(f"{[x.name for x in samplers]}")
    logger.debug(f"{[x.name for x in samplers_for_img2img]}")
            
            
class Script(scripts.Script):
    fix_whs=['none','width long','height long','random']
    fix_whs_d={0 : wh_chg_n, 1: wh_chg_w, 2 : wh_chg_h, 3 : wh_chg_r}
    is_img2img=True
    
    def title(self):
        return "Random"
        
    def show(self, is_img2img):
        self.is_img2img=is_img2img
        return scripts.AlwaysVisible
        
    def ui(self,is_img2img):
        with gr.Group():
            with gr.Accordion(self.title(), open=False):
                is_enabled = gr.Checkbox(label=f"{self.title()} enabled", value=True)
                
                with gr.Group():
                    sd_hypernetwork_strength1 = gr.Slider(minimum=0.0,maximum=1.0,step=0.001,label='sd_hypernetwork_strength1 min/max',value=0.0 , elem_id="rnd-sd_hypernetwork_strength1")
                    sd_hypernetwork_strength2 = gr.Slider(minimum=0.0,maximum=1.0,step=0.001,label='sd_hypernetwork_strength2 min/max',value=1.0 , elem_id="rnd-sd_hypernetwork_strength2")
                    with gr.Accordion("Hypernetwork", open=False):
                        noHypernetwork = gr.Checkbox(label=f"No Hypernetwork Random choices", value=False)
                        rHypernetworks = gr.CheckboxGroup(label='Hypernetwork', choices=["None"] + [x for x in hypernetworks.keys()], value=["None"] + [x for x in hypernetworks.keys()], elem_id="rnd-Hypernetwork")
                    create_refresh_button(rHypernetworks, shared.reload_hypernetworks, lambda: {"choices": (["None"] + [x for x in shared.hypernetworks.keys()]) , "value": ["None"] + [x for x in hypernetworks.keys()] } , "refresh_rHypernetworks")
                
                with gr.Group():
                    step1 = gr.Slider(minimum=1,maximum=150,step=1,label='step1 min/max',value=10, elem_id="rnd-step1")
                    step2 = gr.Slider(minimum=1,maximum=150,step=1,label='step2 min/max',value=15, elem_id="rnd-step2")
                
                with gr.Group():
                    cfg1 = gr.Slider(minimum=1,maximum=30,step=0.5,label='cfg1 min/max',value=6 , elem_id="rnd-cfg1")
                    cfg2 = gr.Slider(minimum=1,maximum=30,step=0.5,label='cfg2 min/max',value=15, elem_id="rnd-cfg2")
                
                with gr.Group():
                    gr.Markdown("only i2i option", elem_id="rnd-denoising",css=".gradio-container {min-height: 6rem;}")
                    denoising1 = gr.Slider(minimum=0,maximum=1,step=0.01,label='denoising1 min/max',value=0.5, elem_id="rnd-denoising1")
                    denoising2 = gr.Slider(minimum=0,maximum=1,step=0.01,label='denoising2 min/max',value=1.0, elem_id="rnd-denoising2")
                
                with gr.Group():
                    if is_img2img:
                        no_resize = gr.Checkbox(label='no resize',value=True , elem_id="rnd-no-resize")
                    else:
                        no_resize = gr.Checkbox(label='no resize',value=False, elem_id="rnd-no-resize")
                    w1 = gr.Slider(minimum=64,maximum=2048,step=64,label='width 1 min/max' ,value=512 , elem_id="rnd-w1")
                    w2 = gr.Slider(minimum=64,maximum=2048,step=64,label='width 2 min/max' ,value=768 , elem_id="rnd-w2")
                    h1 = gr.Slider(minimum=64,maximum=2048,step=64,label='height 1 min/max',value=512 , elem_id="rnd-h1")
                    h2 = gr.Slider(minimum=64,maximum=2048,step=64,label='height 2 min/max',value=768 , elem_id="rnd-h2")
                    
                    fix_wh = gr.Radio(label='fix width height direction', choices=[x for x in self.fix_whs], value=self.fix_whs[0], type="index", elem_id="rnd-fix_wh")

                with gr.Group():
                    if is_img2img:
                        rnd_sampler = gr.CheckboxGroup(label='Sampling Random', elem_id="rnd_sampler", choices=[x.name for x in samplers],value=[x.name for x in samplers_for_img2img])#, type="index"
                        create_refresh_button(rnd_sampler, apply_samplers, lambda: {"choices": [x.name for x in samplers_for_img2img],"value": [x.name for x in samplers_for_img2img]}, "refresh_rnd_sampler")
                    else :
                        rnd_sampler = gr.CheckboxGroup(label='Sampling Random', elem_id="rnd_sampler", choices=[x.name for x in samplers],value=[x.name for x in samplers])#, type="index"
                        create_refresh_button(rnd_sampler, apply_samplers, lambda: {"choices": [x.name for x in samplers],"value": [x.name for x in samplers]}, "refresh_rnd_sampler")
                
                with gr.Group():
                    fixed_seeds = gr.Checkbox(label='Keep -1 for seeds',value=True)
            
        return [
            is_enabled,
            noHypernetwork,rHypernetworks,sd_hypernetwork_strength1,sd_hypernetwork_strength2,
            step1,step2,cfg1,cfg2,denoising1,denoising2,
            no_resize,w1,w2,h1,h2,fix_wh,
            rnd_sampler,
            fixed_seeds
        ]
        
    def process_batch(self, p,
        is_enabled,
        noHypernetwork,rHypernetworks,sd_hypernetwork_strength1,sd_hypernetwork_strength2,
        step1,step2,cfg1,cfg2,denoising1,denoising2,
        no_resize,w1,w2,h1,h2,fix_wh,
        rnd_sampler,
        fixed_seeds,
        *args,
        **kwargs
    ):
        if not is_enabled:
            logger.debug(f"{self.title()} disabled - exiting")
            return p

    def process(self,p,
        is_enabled,
        noHypernetwork,rHypernetworks,sd_hypernetwork_strength1,sd_hypernetwork_strength2,
        step1,step2,cfg1,cfg2,denoising1,denoising2,
        no_resize,w1,w2,h1,h2,fix_wh,
        rnd_sampler,
        fixed_seeds
    ):
        if not is_enabled:
            logger.debug(f"{self.title()} disabled - exiting")
            return p
        logger.debug(f"{rHypernetworks};{sd_hypernetwork_strength1};{sd_hypernetwork_strength2};")
        logger.debug(f"{step1};{step2};{cfg1};{cfg2};{denoising1};{denoising2};")
        logger.debug(f"{no_resize};{w1};{w2};{h1};{h2};{fix_wh};")
        logger.debug(f"{rnd_sampler};{fixed_seeds};")
        
        # Random
        
        #shared.opts.onchange("sd_hypernetwork", wrap_queued_call(lambda: modules.hypernetworks.hypernetwork.load_hypernetwork(shared.opts.sd_hypernetwork)))
        
        rHypernetwork=opts.sd_hypernetwork
        if not noHypernetwork:
            if len(rHypernetworks) == 1:
                rHypernetwork=rHypernetworks[0]
                apply_hypernetwork(rHypernetworks[0])
            elif len(rHypernetworks) > 1:
                rHypernetwork=random.choice(rHypernetworks)
                apply_hypernetwork(rHypernetwork)
        
        (hpmin,hpmax)=(min(sd_hypernetwork_strength1,sd_hypernetwork_strength2),max(sd_hypernetwork_strength1,sd_hypernetwork_strength2))
        sd_hypernetwork_strength=random.randint(0, int((hpmax - hpmin) / 0.001)) * 0.001 + hpmin
        hypernetwork.apply_strength(sd_hypernetwork_strength)
        
        p.steps=random.randint(min(step1,step2),max(step1,step2))
        
        (cfgmin,cfgmax)= (min(cfg1,cfg2),max(cfg1,cfg2))
        p.cfg_scale=random.randint(0, int((cfgmax - cfgmin) / 0.5)) * 0.5 + cfgmin


        if not no_resize:
            h1=h1/64
            h2=h2/64
            w1=w1/64
            w2=w2/64
            p.width=random.randint(min(w1,w2),max(w1,w2))*64
            p.height=random.randint(min(h1,h2),max(h1,h2))*64
            wh_chg = self.fix_whs_d.get(fix_wh, wh_chg_n)
            wh_chg(p)
            
        if len(rnd_sampler) == 1:
            p.sampler_name=rnd_sampler[0]
        elif len(rnd_sampler) > 1:
            p.sampler_name=random.choice(rnd_sampler)
            
        if self.is_img2img:
            p.denoising_strength=random.uniform(min(denoising1,denoising2),max(denoising1,denoising2))
            logger.info(f"hypernetwork:{rHypernetwork} ; hypernetwork strength:{sd_hypernetwork_strength} ; steps:{p.steps} ; cfg:{p.cfg_scale} ; width:{p.width} ; height:{p.height} ; denoising_strength:{p.denoising_strength} ; ")
        else :
            logger.info(f"hypernetwork:{rHypernetwork} ; hypernetwork strength:{sd_hypernetwork_strength} ; steps:{p.steps} ; cfg:{p.cfg_scale} ; width:{p.width} ; height:{p.height} ;")
        
        if fixed_seeds:
            p.seed=-1;
            processing.fix_seed(p)