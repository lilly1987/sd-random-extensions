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
from modules.shared import opts,state
from modules.sd_samplers import samplers,samplers_for_img2img
import logging
from my import *

logger = logging.getLogger(__name__)
logger.handlers.clear()
#logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.WARNING)

# 일반 핸들러. 할 필요 업음. 이미 메인에서 출력해줌
streamFormatter = logging.Formatter("Random %(asctime)s %(levelname)s %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
#streamHandler.setLevel(logging.INFO)
#streamHandler.setLevel(logging.WARNING)
streamHandler.setFormatter(streamFormatter)
logger.addHandler(streamHandler)

# 파일 핸들러
fileFormatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
fileHandler = logging.FileHandler("Random.%(asctime)s.log")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(fileFormatter)
logger.addHandler(fileHandler)

if logger.getEffectiveLevel() == logging.DEBUG :
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

logger.debug('==== DEBUG ====')
logger.info(' Load ')

class Script(scripts.Script):
    fix_whs=['none','width long','height long','random']
    fix_whs_d={0 : wh_chg_n, 1: wh_chg_w, 2 : wh_chg_h, 3 : wh_chg_r}
    is_img2img=True
    
    def title(self):
        return "Random"
        
    def show(self, is_img2img):
        self.is_img2img=is_img2img
        return True
        
    def ui(self,is_img2img):
        with gr.Group():
            with gr.Accordion(self.title(), open=False):
                is_enabled = gr.Checkbox(label=f"{self.title()} enabled", value=True)
                
                with gr.Group():
                    if is_img2img:
                        loops = gr.Slider(minimum=1,maximum=10000,step=1,label='Loops',value=1, elem_id="rnd-loops")
                    else:
                        loops = gr.Slider(minimum=1,maximum=10000,step=1,label='Loops',value=10000, elem_id="rnd-loops")
        return [is_enabled,loops]
        
    def process_batch(self, p,
        is_enabled,
        loops,
        *args,
        **kwargs
    ):
        if not is_enabled:
            logger.debug(f"{self.title()} disabled - exiting")
            return p

    def process(self,p,
        is_enabled,
        loops,
    ):
        if not is_enabled:
            logger.debug(f"{self.title()} disabled - exiting")
            return p