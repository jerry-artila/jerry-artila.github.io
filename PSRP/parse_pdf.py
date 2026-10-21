import sys, re, os, json, html

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_NAME = "亞伯拉罕以撒雅各的神"
PDF_PATH = os.path.join(BASE_DIR, THEME_NAME, f"{THEME_NAME}.pdf")
THEME_DIR = os.path.join(BASE_DIR, THEME_NAME)

if sys.platform == "darwin":
    # 1a. Setup native PDFKit on macOS (zero third-party dependencies)
    import ctypes
    from ctypes import c_void_p, c_char_p, c_ulong, cast, CFUNCTYPE

    pdfkit = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/PDFKit.framework/PDFKit")
    objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")
    objc.objc_getClass.restype = c_void_p
    objc.objc_getClass.argtypes = [c_char_p]
    objc.sel_registerName.restype = c_void_p
    objc.sel_registerName.argtypes = [c_char_p]
    msgSend = objc.objc_msgSend

    def send(target, sel_name, restype, argtypes=None, *args):
        sel = objc.sel_registerName(sel_name.encode("utf-8"))
        types = [restype, c_void_p, c_void_p]
        if argtypes:
            types.extend(argtypes)
        func = cast(msgSend, CFUNCTYPE(*types))
        return func(target, sel, *args)

    NSString = objc.objc_getClass(b"NSString")
    NSURL = objc.objc_getClass(b"NSURL")
    PDFDocument = objc.objc_getClass(b"PDFDocument")

    ns_path = send(NSString, "stringWithUTF8String:", c_void_p, [c_char_p], PDF_PATH.encode("utf-8"))
    url = send(NSURL, "fileURLWithPath:", c_void_p, [c_void_p], ns_path)
    doc_alloc = send(PDFDocument, "alloc", c_void_p)
    doc = send(doc_alloc, "initWithURL:", c_void_p, [c_void_p], url)
    count = send(doc, "pageCount", c_ulong)

    def get_page_text(i):
        page = send(doc, "pageAtIndex:", c_void_p, [c_ulong], i)
        ns_str = send(page, "string", c_void_p)
        if ns_str:
            utf8 = send(ns_str, "UTF8String", c_char_p)
            return utf8.decode("utf-8", "ignore") if utf8 else ""
        return ""
else:
    # 1b. Setup PyMuPDF on Windows / Linux
    import pymupdf

    doc = pymupdf.open(PDF_PATH)
    count = len(doc)

    def get_page_text(i):
        """擷取單頁文字，並將同一水平列（如左側懸掛編號與右側內文）合併為同一行，確保與 macOS PDFKit 輸出一致。"""
        d = doc[i].get_text("dict")
        raw_lines = []
        for b in d.get("blocks", []):
            for l in b.get("lines", []):
                txt = "".join(s["text"] for s in l.get("spans", []))
                bbox = l["bbox"]
                y_mid = (bbox[1] + bbox[3]) / 2.0
                x0 = bbox[0]
                raw_lines.append((y_mid, x0, txt))

        merged = []
        for y_mid, x0, txt in raw_lines:
            if merged and abs(merged[-1][0] - y_mid) < 3.0 and x0 > merged[-1][1]:
                merged[-1] = (merged[-1][0], x0, merged[-1][2] + txt)
            else:
                merged.append((y_mid, x0, txt))
        return "\n".join(m[2] for m in merged)

REPLACEMENTS = {
    "尌": "就",
    "貣": "起",
    "爱": "物",
    "爰": "牧",
    "仉": "今",
    "孚": "守",
    "孙": "宇",
    "畧": "略",
}

def clean_text(text):
    for k, v in REPLACEMENTS.items():
        text = text.replace(k, v)
    return text

bible_books = "創|出|利|民|申|書|士|得|撒上|撒下|王上|王下|代上|代下|拉|尼|斯|伯|詩|箴|傳|歌|賽|耶|哀|結|但|何|珥|摩|俄|拿|彌|鴻|哈|番|該|亞|瑪|太|可|路|約|徒|羅|林前|林後|加|弗|腓|西|帖前|帖後|提前|提後|多|門|來|雅|彼前|彼後|約一|約二|約三|猶|啓|啟"

re_l1 = re.compile(r"^(壹|貳|參|肆|伍|陸|柒|捌|玖|拾)([\s　、]|$)(.*)$")
re_l2 = re.compile(r"^([一二三四五六七八九十]+)([\s　、]|$)(.*)$")
re_l3 = re.compile(r"^(\d+)([\s　、\.]|$)(.*)$")
re_l4 = re.compile(r"^([a-z])([\s　、\.]|$)(.*)$")
re_l5 = re.compile(r"^(㈠|㈡|㈢|㈣|㈤|㈥|㈦|㈧|㈨|㈩|\([一二三四五六七八九十]+\)|\([0-9]+\))([\s　、]|$)(.*)$")
re_scripture = re.compile(rf"^({bible_books})\s*([0-9]+[0-9:～~\-—,\.a-zA-Z\s上下]*?)(\s+)(.*)$")

LESSONS_CONFIG = [
    {
        "num": 1,
        "code": "01",
        "title": "第一篇 認識並經歷亞伯拉罕的神、以撒的神、和雅各的神，而成爲神的以色列",
        "short_title": "認識並經歷亞伯拉罕的神、以撒的神、和雅各的神，而成爲神的以色列",
        "s_page": 3,
        "e_page": 13
    },
    {
        "num": 2,
        "code": "02",
        "title": "第二篇 亞伯拉罕的神見於祂對待亞伯拉罕的事",
        "short_title": "亞伯拉罕的神見於祂對待亞伯拉罕的事",
        "s_page": 16,
        "e_page": 26
    },
    {
        "num": 3,
        "code": "03",
        "title": "第三篇 兩個婦人的寓意",
        "short_title": "兩個婦人的寓意",
        "s_page": 31,
        "e_page": 40
    },
    {
        "num": 4,
        "code": "04",
        "title": "第四篇 獻上以撒並經歷神是叫死人復活的神",
        "short_title": "獻上以撒並經歷神是叫死人復活的神",
        "s_page": 46,
        "e_page": 54
    },
    {
        "num": 5,
        "code": "05",
        "title": "第五篇 過享受恩典的生活，使神喜悅",
        "short_title": "過享受恩典的生活，使神喜悅",
        "s_page": 57,
        "e_page": 68
    },
    {
        "num": 6,
        "code": "06",
        "title": "第六篇 伯特利的夢",
        "short_title": "伯特利的夢",
        "s_page": 74,
        "e_page": 81
    },
    {
        "num": 7,
        "code": "07",
        "title": "第七篇 蒙揀選、受對付、被破碎",
        "short_title": "蒙揀選、受對付、被破碎",
        "s_page": 86,
        "e_page": 95
    },
    {
        "num": 8,
        "code": "08",
        "title": "第八篇 成熟的過程",
        "short_title": "成熟的過程",
        "s_page": 97,
        "e_page": 104
    },
    {
        "num": 9,
        "code": "09",
        "title": "第九篇 祝福",
        "short_title": "祝福",
        "s_page": 107,
        "e_page": 114
    }
]

def parse_lesson(cfg):
    raw_lines = []
    for p in range(cfg["s_page"] - 1, cfg["e_page"]):
        txt = clean_text(get_page_text(p))
        for l in txt.split("\n"):
            l_str = l.strip()
            if "職事信息摘錄：" in l_str:
                break
            if re.match(r"^\d+$", l_str):
                continue
            raw_lines.append(l_str)
        else:
            continue
        break
    
    # find first "壹"
    start_idx = 0
    for idx, l in enumerate(raw_lines):
        if re_l1.match(l):
            start_idx = idx
            break
            
    outline_lines = [l for l in raw_lines[start_idx:] if l]
    
    items = []
    curr = None
    for line in outline_lines:
        m1 = re_l1.match(line)
        m2 = re_l2.match(line)
        m3 = re_l3.match(line)
        m4 = re_l4.match(line)
        m5 = re_l5.match(line)
        ms = re_scripture.match(line)
        
        if m1:
            curr = {"level": 1, "num": m1.group(1), "text": m1.group(3).strip(), "scriptures": []}
            items.append(curr)
        elif m5:
            curr = {"level": 5, "num": m5.group(1), "text": m5.group(3).strip(), "scriptures": []}
            items.append(curr)
        elif m2:
            curr = {"level": 2, "num": m2.group(1), "text": m2.group(3).strip(), "scriptures": []}
            items.append(curr)
        elif m3:
            curr = {"level": 3, "num": m3.group(1), "text": m3.group(3).strip(), "scriptures": []}
            items.append(curr)
        elif m4:
            curr = {"level": 4, "num": m4.group(1), "text": m4.group(3).strip(), "scriptures": []}
            items.append(curr)
        elif ms:
            ref = ms.group(1) + ms.group(2)
            stext = ms.group(4).strip()
            s_obj = {"ref": ref, "text": stext}
            if curr:
                curr["scriptures"].append(s_obj)
            else:
                items.append({"level": 1, "num": "", "text": "", "scriptures": [s_obj]})
        else:
            if curr:
                if curr["scriptures"]:
                    curr["scriptures"][-1]["text"] += line
                else:
                    curr["text"] += line
    return items

print("Parser module ready.")
