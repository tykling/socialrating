def svgthumbnail(mimetype):
    svg = """<svg class="bd-placeholder-img card-img-top" width="100%" height="225" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" focusable="false" role="img" aria-label="Placeholder: Thumbnail">
    <title>Thumbnail</title>
    <rect width="100%" height="100%" fill="#55595c"></rect>
    <text x="50%" y="50%" fill="#eceeef" dy=".3em" dominant-baseline="middle" text-anchor="middle">"""
    return svg + mimetype + "</text></svg>"
