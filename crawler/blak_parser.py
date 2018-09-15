import re


def get_filename(html):
    content = html
    pat = re.compile(r'<span.*p_tatime.*">(.*)</span>')
    date = pat.search(content).group(1)
    pat = re.compile(r'<b id="b_subject">(.*)</b>')
    title = pat.search(content).group(1)
    date = date.replace(' ', '_')
    date = date.replace(':', '')
    return title + '_' + date


def get_title(html):
    content = html
    pat = re.compile(r'<b id="b_subject">(.*)</b>')
    title = pat.search(content).group(1)
    return title


def get_body(html):
    content = html
    pattern = re.compile(r'<!-- 主贴内容开始 -->(.*)<!-- 投票选项开始 -->', re.DOTALL)
    body = pattern.search(content).group(1)
    return body


def clean_body(body_str):
    inter_str = body_str
    # remove redundant html code
    pat = re.compile(r'<div.*?style="">')
    inter_str = pat.sub(r'', inter_str)
    # remove hyper link
    pat = re.compile(r'<a.*?>(.*?)</a>')
    inter_str = pat.sub(r'\1', inter_str)
    # remove hidden tag
    pat = re.compile(r'<span style="display:none;">.*?</span>')
    inter_str = pat.sub(r'', inter_str)
    # remove useless picture
    pat = re.compile(r'<div.*?<IMG SRC="(.*?)".*?"按此在新窗口浏览图片".*?</div>')
    inter_str = pat.sub(r'图片损坏: \1', inter_str)
    # remove <span> and </span>
    pat = re.compile(r'<span>(.*?)</span>')
    inter_str = pat.sub(r'\1', inter_str)
    # remove <font>
    pat = re.compile(r'<font.*?">(.*?)</font>', re.DOTALL)
    inter_str = pat.sub(r'\1', inter_str)
    # remove spaces
    pat = re.compile(r'\s+')
    inter_str = pat.sub(r'', inter_str)
    # remove multiple &nbsp;'
    pat = re.compile(r'(?:&nbsp;){3,}')
    inter_str = pat.sub(r'', inter_str)
    # convert &nbsp; to space
    pat = re.compile(r'&nbsp;')
    inter_str = pat.sub(r' ', inter_str)
    # convert &gt; to >
    pat = re.compile(r'&gt;')
    inter_str = pat.sub(r'>', inter_str)
    # convert <br> to \n
    pat = re.compile(r'<br>|<br/>|</br>')
    inter_str = pat.sub(r'\n', inter_str)
    # remove redundant line breaks
    pat = re.compile(r'\n{2,}')
    inter_str = pat.sub(r'\n', inter_str)
    return inter_str


def parse_format(body_str):
    inter_str = body_str
    pat = re.compile(r'<b>(.*?)</b>', re.DOTALL)
    split_list = list(filter(lambda x: x != '', pat.split(inter_str)))
    bold_list = pat.findall(inter_str)
    # 1. find all bold parts
    if len(split_list) == 1:
        return split_list
    else:
        for i in range(len(split_list)):
            for bold in bold_list:
                if split_list[i] == bold:
                    # pat = re.compile(r'\n')
                    # bold = pat.sub(r'', bold)
                    split_list[i] = [bold, 'bold']

    # 3. find color parts
    for i in range(1024):
        if i >= len(split_list):
            break
        if isinstance(split_list[i], str):
            tmp = split_list[i]
        else:
            tmp = split_list[i][0]
        pat = re.compile(r'<div.*?<img.*?data-original="(.*?)@.*?</div>')
        pic_link = pat.search(tmp)
        if pic_link != None:
            pic_link = pic_link.group(1)
            if isinstance(split_list[i], str):
                split_list[i] = pat.sub(r'', split_list[i])
                tmp = split_list[i]
            else:
                split_list[i][0] = pat.sub(r'', split_list[i][0])
                tmp = split_list[i][0]
            split_list.insert(i + 1, '\n')
            split_list.insert(i + 1, [pic_link, 'picture'])
            split_list.insert(i + 1, '\n')
        pat = re.compile(r'<spanstyle="color:(.*?)">(.*?)</span>', re.DOTALL)
        color_list = pat.findall(tmp)
        if len(color_list) == 0:
            continue
        else:
            pat = re.compile(r'<spanstyle="color:.*?">(.*?)</span>', re.DOTALL)
            clean_body_list = list(filter(lambda x: x != '', pat.split(tmp)))
            for j in range(len(clean_body_list)):
                for color in color_list:
                    if clean_body_list[j] == color[1]:
                        clean_body_list[j] = [color[1], color[0]]
            if isinstance(split_list[i], str):
                split_list[i] = clean_body_list
            else:
                if split_list[i][1] != 'bold':
                    split_list[i][0] = clean_body_list
                else:
                    for item in clean_body_list:
                        if isinstance(item, str):
                            split_list[i][0] = item
                        else:
                            split_list.insert(i + 1, item)

    # 4. split by line break
    for i in range(1024):
        if i >= len(split_list):
            break
        if isinstance(split_list[i], list):
            for j in range(len(split_list[i])):
                if isinstance(split_list[i][j], list):
                    for k in range(len(split_list[i][j])):
                        if not isinstance(split_list[i][j][k], str):
                            break
                        pat = re.compile(r'(\n)')
                        tmp = list(filter(lambda x: x != '', pat.split(split_list[i][j][k])))
                        if len(tmp) > 1:
                            split_list[i][j][k] = tmp
                else:
                    if split_list[i][j] != '\n':
                        pat = re.compile(r'(\n)')
                        tmp = list(filter(lambda x: x != '', pat.split(split_list[i][j])))
                    else:
                        if isinstance(split_list[i][j - 1], str):
                            if j > 1 and split_list[i][j - 1][-1] == '\n':
                                split_list[i][j - 1] = split_list[i][j - 1][:-1]
                        else:
                            if j > 1 and len(split_list[i][j - 1][-1]) > 0 and \
                                    split_list[i][j - 1][-1][-1] == '\n':
                                split_list[i][j - 1][-1] = split_list[i][j - 1][-1][:-1]
                        tmp = []
                    if len(tmp) > 1:
                        split_list[i][j] = tmp
        else:
            if split_list[i] != '\n':
                pat = re.compile(r'(\n)')
                tmp = list(filter(lambda x: x != '', pat.split(split_list[i])))
                for ii in range(1024):
                    if ii >= len(tmp):
                        break
                    if ii > 0 and tmp[ii] == '\n' and tmp[ii - 1] == '\n':
                        tmp.pop(ii)
            else:
                if isinstance(split_list[i - 1], str):
                    if i > 1 and split_list[i - 1][-1] == '\n':
                        split_list[i - 1] = split_list[i - 1][:-1]
                else:
                    if i > 1 and len(split_list[i - 1][-1]) > 0 and split_list[i - 1][-1][
                        -1] == '\n':
                        split_list[i - 1][-1] = split_list[i - 1][-1][:-1]
                tmp = []
            if len(tmp) > 1:
                split_list[i] = tmp

    return split_list


def parser(html=None):
    if html == None:
        print('Need HTML file to parse!')
        exit(0)
    else:
        print('Start to parse html...')
    filename = get_filename(html)
    title = get_title(html)
    body = get_body(html)
    body = clean_body(body)
    format_content = parse_format(body)
    format_content.insert(0, title)
    format_content.insert(0, filename)
    return format_content


if __name__ == '__main__':
    parser()
