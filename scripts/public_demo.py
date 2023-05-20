import os
import sys
import os.path as osp

import qrcode

import modules.scripts as scripts
import gradio as gr
import logging
from gradio.context import Context

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

    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return "Public Demo Extension"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def postprocess(self, p, processed, *args):
        # this hides negative front
        if shared.opts.hide_negative_prompt:
            negative_prompt = p.negative_prompt
            for i, text in enumerate(processed.infotexts):
                processed.infotexts[i] = text.replace(f'Negative prompt: {negative_prompt}', '')
            processed.info = processed.info.replace(f'Negative prompt: {negative_prompt}', '')
            processed.negative_prompt = ''
            processed.all_negative_prompts = ['' for _ in processed.all_negative_prompts]

        if shared.opts.add_qr_code:
            # I'm adding images to array I iterate to, better to create new one and replace
            new_processed_images = processed.images[:processed.index_of_first_image]
            for i, img in enumerate(processed.images[processed.index_of_first_image:]):
                image_path = img.already_saved_as.replace(p.outpath_samples, '')
                qr_link = f'{shared.opts.static_server_uri}{image_path.replace(os.path.sep, "/")}'
                qr_img = qrcode.make(qr_link).get_image()
                new_processed_images.append(img)
                new_processed_images.append(qr_img)
            processed.images = new_processed_images


shared.options_templates.update(shared.options_section(('ui', "User interface"), {
    "hide_negative_prompt": shared.OptionInfo(True,
                                              "if true, will hide negative prompt from the text info under images in UI"),
    "add_qr_code": shared.OptionInfo(True,
                                     "If true, a qr code will be generated, pointing to the image on static web server"),
    "static_server_uri": shared.OptionInfo("http://localhost:7860/file=outputs/txt2img-images",
                                           "URL of the prefix of the URI, directory with current date and image name will be appended after this."),
    "hide_footer_links": shared.OptionInfo(True,
                                           "if true, will replace the footer with one without links"),
    "wide_gallery": shared.OptionInfo(True,
                                      "if true, will put gallery to new row, making it wide"),
    "add_homepage_button": shared.OptionInfo(True,
                                             "if true, will add the return to homepage after the generate button"),

}))


# copied from
# https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/39ec4f06ffb2c26e1298b2c5d80874dc3fd693ac/modules/ui.py#L1861-L1887
# but all external links replaced by plaintext
def versions_html():
    import torch
    import launch

    python_version = ".".join([str(x) for x in sys.version_info[0:3]])
    commit = launch.commit_hash()

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
torch: {getattr(torch, '__long_version__', torch.__version__)}
&#x2000;•&#x2000;
xformers: {xformers_version}
&#x2000;•&#x2000;
gradio: {gr.__version__}
&#x2000;•&#x2000;
checkpoint: <span id="sd_checkpoint_hash">N/A</span>
"""


# because of https://github.com/gradio-app/gradio/issues/3667 I avoid using a tag at all
# and even when it gets fixed, having it as span is better, because even the js adding some link does not make it
# clickable


def on_before_component(component, **kwargs):
    # insert custom footer and hide the original one
    is_footer_html = isinstance(component, gr.components.HTML) and kwargs['elem_id'] == 'footer'
    is_output_gallery = isinstance(component, gr.components.Gallery) and kwargs['elem_id'] == 'txt2img_gallery'
    if not any((is_footer_html, is_output_gallery)):
        return
    # adding my own footer
    elif is_footer_html and shared.opts.hide_footer_links:
        footer = shared.html(osp.relpath(os.path.join(pth, "footer.html"), osp.join(script_path, "html")))
        footer = footer.format(versions=versions_html())
        gr.HTML(footer, elem_id="no_link_footer")
        # I can't do this, because I can't mutate the kwargs like this
        # kwargs['visible'] = False
        # kwargs['value'] = ''
        # we have the original footer component here, but it seems there is no way to change the value
    elif is_output_gallery and shared.opts.wide_gallery:
        the_row = Context.block.parent.parent
        if not isinstance(the_row, gr.Row):
            raise Exception("Something is wrong with the layout, Row expected")
        cur_block = Context.block
        the_row.__exit__()
        column_idx, gallery_column = [(i, c) for i, c in enumerate(the_row.children) if c.elem_id == 'txt2img_results'][
            0]
        del the_row.children[column_idx]
        with gr.Row().style(
            equal_height=False):  # adding new row so all the hidden stuff would be in the same hidden row
            Context.block.add(gallery_column)
        Context.block = cur_block


def on_after_component(component, **kwargs):
    # insert custom footer and hide the original one
    is_txt2img_generate_button = isinstance(component, gr.components.Button) and kwargs['elem_id'] == 'txt2img_generate'
    is_footer_html = isinstance(component, gr.components.HTML) and kwargs['elem_id'] == 'footer'
    if not any((is_txt2img_generate_button, is_footer_html)):
        return
    # adding my own button
    # manually closing the row and creating new one, and adding the button there
    elif is_txt2img_generate_button and shared.opts.add_homepage_button:
        component.parent.__exit__()
        id_part = 'txt2img'
        with gr.Row(elem_id=f"{id_part}_generate_box", elem_classes="reload-box"):
            # copied from this line in the settings
            # restart_gradio = gr.Button(value='Reload UI', variant='primary', elem_id="settings_restart_gradio")
            reload_page = gr.Button('Return to homepage', elem_id=f"{id_part}_reload", variant='secondary')
            reload_page.click(
                fn=lambda: None,
                _js='reload_page',
                inputs=[],
                outputs=[],
            )
    elif is_footer_html and shared.opts.hide_footer_links:
        component.visible = False
        component.value = ''


script_callbacks.on_before_component(on_before_component)
script_callbacks.on_after_component(on_after_component)

# todo: remaining to migrate
#   the output panel to new row
#   trying it out, installing to new dir after everything
