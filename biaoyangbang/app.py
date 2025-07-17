from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import glob

app = Flask(__name__)
UPLOAD_FOLDER = "static/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FONT_PATH = "static/SourceHanSansCN-Normal.otf"

# 自动匹配背景图文件（支持png或jpg）
bg_paths = glob.glob("static/表扬榜背景图.*")
if bg_paths:
    BACKGROUND_PATH = bg_paths[0]
else:
    raise FileNotFoundError("找不到背景图文件（static/表扬榜背景图.png或.jpg）")

@app.route('/', methods=['GET', 'POST'])
def index():
    default_font_size = 50  # 约等于PPT 22号字
    default_rows = 9
    default_cols = 6
    default_color = "black"
    default_names = ""

    if request.method == 'POST':
        names_text = request.form.get('names', default_names)
        font_size = int(request.form.get('font_size', default_font_size))
        rows = int(request.form.get('rows', default_rows))
        cols = int(request.form.get('cols', default_cols))
        color = request.form.get('font_color', default_color)

        names = [name.strip() for name in names_text.split('\n') if name.strip()]
        names_per_page = rows * cols
        total_pages = (len(names) + names_per_page - 1) // names_per_page

        font = ImageFont.truetype(FONT_PATH, font_size)
        image_urls = []
        download_urls = []

        for page in range(total_pages):
            img = Image.open(BACKGROUND_PATH).convert("RGBA")
            draw = ImageDraw.Draw(img)

            top_margin = 210  # 4.43cm ≈ 167px
            left_margin = img.width * 0.1
            text_box_width = img.width * 0.8
            cell_width = text_box_width / cols
            cell_height = font_size * 1.8  # 行距1.5倍

            page_names = names[page * names_per_page : (page + 1) * names_per_page]

            for index, name in enumerate(page_names):
                row = index // cols
                col = index % cols
                x = int(left_margin + col * cell_width)
                y = int(top_margin + row * cell_height)
                draw.text((x, y), name, font=font, fill=color)

            filename = f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}_{page+1}.png"
            path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(path)

            image_urls.append(f"/{path}")
            download_urls.append(f"/download/{filename}")

        images = list(zip(image_urls, download_urls))

        return render_template('index.html',
                               images=images,
                               names=names_text,
                               font_size=font_size,
                               rows=rows,
                               cols=cols,
                               font_color=color)

    return render_template('index.html',
                           images=None,
                           names=default_names,
                           font_size=default_font_size,
                           rows=default_rows,
                           cols=default_cols,
                           font_color=default_color)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)