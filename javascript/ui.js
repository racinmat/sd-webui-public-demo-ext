function reload_page(){
    location.reload()
    return []
}

// copied from https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/39ec4f06ffb2c26e1298b2c5d80874dc3fd693ac/javascript/ui.js#L344-L354
// but commented out the link, because I want to disable links
onOptionsChanged(function() {
    var elem = gradioApp().getElementById('sd_checkpoint_hash');
    var sd_checkpoint_hash = opts.sd_checkpoint_hash || "";
    var shorthash = sd_checkpoint_hash.substring(0, 10);

    if (elem && elem.textContent != shorthash) {
        elem.textContent = shorthash;
        elem.title = sd_checkpoint_hash;
        //elem.href = "https://google.com/search?q=" + sd_checkpoint_hash;
    }
});
