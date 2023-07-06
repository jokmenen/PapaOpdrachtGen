function show_img(img_path) {
    const img = document.createElement("img");
    img.src = img_path;
    document.body.appendChild(img);
}


window.addEventListener('load', function() {
document.querySelector('input[type="file"]').addEventListener('change', function() {
    if (this.files && this.files[0]) {
        var img = document.querySelector('img');
        img.onload = () => {
            URL.revokeObjectURL(img.src);  // no longer needed, free memory
        }

        img.src = URL.createObjectURL(this.files[0]); // set src to blob url
        const button = document.createElement('button')
        document.body.appendChild(button);
    }
});
});