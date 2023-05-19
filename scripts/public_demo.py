import os
import sys
import os.path as osp

import modules.scripts as scripts
import gradio as gr
import logging

from modules import shared, script_callbacks
from modules.paths_internal import script_path

pth = scripts.basedir()
logfile = os.path.join(pth, 'public_demo.log')

# Setup Logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(logfile)
file_handler.setFormatter(log_format)
log.addHandler(file_handler)


class Script(scripts.Script):
    def title(self):
        return "Public Demo Extension"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def postprocess(self, p, processed, *args):
        # this hides negative front
        negative_prompt = p.negative_prompt
        for i, text in enumerate(processed.infotexts):
            processed.infotexts[i] = text.replace(f'Negative prompt: {negative_prompt}', '')
        processed.info = processed.info.replace(f'Negative prompt: {negative_prompt}', '')
        processed.negative_prompt = ''
        processed.all_negative_prompts = ['' for _ in processed.all_negative_prompts]


shared.options_templates.update(shared.options_section(('ui', "User interface"), {
    "hide_negative_prompt": shared.OptionInfo(False,
                                              "if true, will hide negative prompt from the text info under images in UI"),
}))


def versions_html():
    import torch
    import launch

    python_version = ".".join([str(x) for x in sys.version_info[0:3]])
    commit = launch.commit_hash()
    tag = launch.git_tag()

    if shared.xformers_available:
        import xformers
        xformers_version = xformers.__version__
    else:
        xformers_version = "N/A"

    return f"""
version: https://github.com/AUTOMATIC1111/stable-diffusion-webui/commit/{commit}
&#x2000;•&#x2000;
python: <span title="{sys.version}">{python_version}</span>
&#x2000;•&#x2000;
torch: {getattr(torch, '__long_version__',torch.__version__)}
&#x2000;•&#x2000;
xformers: {xformers_version}
&#x2000;•&#x2000;
gradio: {gr.__version__}
&#x2000;•&#x2000;
checkpoint: <a id="sd_checkpoint_hash">N/A</a>
"""


def on_before_component(component, **kwargs):
    # insert custom footer and hide the original one
    if (not isinstance(component, gr.components.HTML)) or (kwargs['elem_id'] != 'footer'):
        return
    # just creating my component
    footer = shared.html(osp.relpath(os.path.join(pth, "footer.html"), osp.join(script_path, "html")))
    footer = footer.format(versions=versions_html())
    gr.HTML(footer, elem_id="no_link_footer")


script_callbacks.on_before_component(on_before_component)
