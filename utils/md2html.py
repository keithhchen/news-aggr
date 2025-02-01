import markdown
from bs4 import BeautifulSoup

follow_pic = """<section style="text-align: center;margin-left: 16px;margin-right: 16px;"><img class="rich_pages wxw-img" data-type="jpeg" src="https://mmbiz.qpic.cn/mmbiz_jpg/ddoFEEahZice8askrD1Oe0v74LO9QiaiaDaaiabQdYgXicD7oP0jyia370MgjQhicJcHuVSNOtNiaHWTNkFiaIQrlNhFmMA/640?wx_fmt=jpeg&amp;from=appmsg&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1&amp;wx_co=1" style="width: 100%; height: auto;" crossorigin="anonymous" alt="图片" data-fail="0"></section>
<section style="text-align: center;background-color: rgb(255, 255, 255);line-height: 1.75em;margin-top: 24px;margin-bottom: 24px;margin-left: 16px;margin-right: 16px;"><span style="color: rgb(0, 0, 0);font-family: Optima-Regular, PingFangTC-light;font-size: 36px;">💬</span></section><section style="text-align: center;background-color: rgb(255, 255, 255);line-height: 1.75em;margin-bottom: 24px;margin-left: 16px;margin-right: 16px;"><span style="color: rgb(0, 0, 0);font-family: Optima-Regular, PingFangTC-light;letter-spacing: 1px;font-size: 14px;">如果你也是未来领域的关注者，请留言你的回声</span></section>"""

def style_html(md_text):
    # Convert Markdown to HTML
    html = markdown.markdown(md_text)
    
    
    html += follow_pic

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    first_h1 = soup.find("h1")
    if first_h1:
        first_h1.decompose()
    
    # Apply styles
    for h2 in soup.find_all("h2"):
        h2["style"] = "font-size: 20px; color: rgb(21, 101, 192); font-weight: bold; margin: 16px 16px 8px;"
        if (h2.string == "亮点"):
            continue
        hr = soup.new_tag("hr")
        hr["style"] = "border-style: solid; border-width: 1px 0 0; border-color: rgba(0, 0, 0, 0.1); -webkit-transform-origin: 0 0; -webkit-transform: scale(1, 0.5); transform-origin: 0 0; transform: scale(1, 0.5);"
        h2.insert_after(hr)

    for p in soup.find_all("p", recursive=False):
        p["style"] = "font-size: 16px; margin: 16px 16px 24px; line-height: 1.75em;"


    for h2 in soup.find_all(["h2", "h3"], string="详细对话"):
        h2["style"] += "font-size: 14px; color: rgb(0, 0, 0);"
        for p in h2.find_all_next("p"):
            if "style" not in p.attrs:
                p["style"] = ""
            p["style"] += "font-size: 14px; margin-top: 8px; margin-bottom: 8px;"
        
    for h2 in soup.find_all(["h2", "h3"], string="亮点"):
        h2["style"] += "font-size: 14px; color: rgb(0, 0, 0);"
        ul = h2.find_next_sibling("ul")
        ul["style"] = "margin-top: 16px; margin-bottom: 16px;"
        if ul:
            for li in ul.find_all("li"):
                li["style"] = "margin: 16px 0; font-size: 14px; line-height: 1.6;"

    highlights = soup.find(["h2", "h3"], string="亮点")

    if highlights:
        section = soup.new_tag("section", id="highlights")
        elements_to_move = []
        section["style"] = "border-radius: 20px; background: #fafafa; margin: 16px 8px; padding: 16px;"
        sibling = highlights

        while sibling and (sibling.name != "h2" or sibling == highlights):
            elements_to_move.append(sibling)
            sibling = sibling.find_next_sibling()
        highlights.insert_before(section)

        for element in elements_to_move:
            section.append(element.extract())

    
    for blockquote in soup.find_all("blockquote"):
        blockquote["style"] = "font-size: 14px; color: rgb(136, 136, 136);"

    for em in soup.find_all("em"):
        if "链接：" in em.text:
            em["style"] = "font-size: 12px; color: rgb(136, 136, 136);"

    for elem in soup.find_all(True):
        if "style" in elem.attrs:
            elem["style"] +=  "font-family: Optima-Regular, PingFangTC-light;"

    return soup