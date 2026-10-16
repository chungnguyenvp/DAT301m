"""Rà soát độ sạch dữ liệu đã xử lý: py -3.13 -X utf8 scripts/audit_processed.py (chạy từ gốc repo).

In số trường hợp và vài ví dụ cho từng kiểm tra; không sửa gì. Cách đọc kết quả: mục 1d PROCESSING_REPORT.md.
"""
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from lawproc import config  # noqa: E402
from lawproc.validity import in_force_at  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

units = [json.loads(l) for l in open(ROOT / 'data/processed/legal_units.jsonl', encoding='utf-8')]
vers = [json.loads(l) for l in open(ROOT / 'data/processed/legal_units_versioned.jsonl', encoding='utf-8')]
live = [r for r in vers if in_force_at(r, config.CUTOFF)[0]]
annex_kind = {r['unit_id']: r['loai_phu_luc'] for r in vers if r['level'] == 'phu_luc'}
AMENDING = config.AMENDING_DOCS
results = []


def report(code, name, items, show=3):
    results.append((code, name, len(items)))
    print(f'\n[{code}] {name}: {len(items)}')
    for it in items[:show]:
        print('    -', str(it)[:230])


body = [u for u in units if u['level'] in ('dieu', 'khoan', 'diem')]
body_live = [r for r in live if r['level'] in ('dieu', 'khoan', 'diem')]
content_live = body_live + [r for r in live if r['level'] == 'phu_luc' and annex_kind.get(r['unit_id']) == 'noi_dung']

# ---------- Cấu trúc (bản gốc legal_units) ----------
VN = 'a b c d đ e g h i k l m n o p q r s t u v x y'.split()
kids = collections.defaultdict(list)
for u in units:
    if u['level'] == 'khoan':
        kids[(u['doc_id'], u['dieu'])].append(u['khoan'])
gap_k = []
for (doc, dieu), ks in kids.items():
    nums = [int(re.match(r'\d+', k).group()) for k in ks if re.fullmatch(r'\d+', k)]
    if doc == 'qcvn_41_2024':
        continue  # khoản dạng 3.1. đánh số riêng
    if nums and (sorted(nums) != list(range(1, max(nums) + 1)) or len(set(nums)) != len(nums)):
        gap_k.append((doc, f'Điều {dieu}', sorted(nums)))
report('S1', 'Điều có số khoản không liên tục từ 1 hoặc trùng', gap_k, 8)

pts = collections.defaultdict(list)
for u in units:
    if u['level'] == 'diem' and u['khoan'] is not None:
        pts[(u['doc_id'], u['dieu'], u['khoan'])].append(u['diem'])
gap_p = []
for key, ds in pts.items():
    base = [d for d in ds if d in VN]
    if not base:
        continue
    idx = [VN.index(d) for d in base]
    if idx != list(range(len(idx))):
        gap_p.append((*key, ds))
report('S2', 'Khoản có điểm không theo thứ tự a, b, c, d, đ, e…', gap_p, 8)

has_child = {(u['doc_id'], u['dieu']) for u in units if u['level'] in ('khoan', 'diem')}
empty_dieu = [u['unit_id'] for u in units if u['level'] == 'dieu' and not u['text'].strip()
              and (u['doc_id'], u['dieu']) not in has_child]
report('S3', 'Điều rỗng (không chữ, không khoản)', empty_dieu)
empty_kd = [u['unit_id'] for u in units if u['level'] in ('khoan', 'diem') and not u['text'].strip()]
report('S4', 'Khoản/điểm rỗng', empty_kd)

LABEL_LINE = re.compile(r'\n(?:\d{1,2}\.\s|[a-zđ]\)\s)')
missed = [(u['unit_id'], u['text'][:150].replace('\n', ' / ')) for u in body
          if u['doc_id'] not in AMENDING and LABEL_LINE.search(u['text'])
          and not re.search(r'[“"]', u['text'])]
report('S5', 'Đơn vị còn dòng bắt đầu bằng nhãn "1." / "a)" mà chưa tách (ngoài văn bản sửa đổi, ngoài trích dẫn)',
       missed, 6)
inline = [(u['unit_id'], u['text'][:160]) for u in body if u['level'] in ('khoan', 'diem')
          and u['doc_id'] not in AMENDING and re.search(r';\s+[b-hk-y]\)\s+[A-ZĐÂĂÊÔƠƯa-zđ]', u['text'])]
report('S6', 'Đơn vị có dạng "…; b) …" liền dòng (nghi gộp điểm)', inline, 6)
long_title = [(u['unit_id'], len(u['title']), u['title'][:120]) for u in units
              if u['level'] == 'dieu' and len(u['title']) > 250]
report('S7', 'Tiêu đề Điều dài > 250 ký tự (nghi lẫn nội dung)', long_title)
no_title = [u['unit_id'] for u in units if u['level'] == 'dieu' and not u['title'].strip()]
report('S8', 'Điều không có tiêu đề', no_title, 6)

# ---------- Ký tự (bản đang hiệu lực, nội dung luật) ----------
def txt(r):
    return (r['title'] or '') + '\n' + (r['text'] or '')


not_nfc = [r['unit_id'] for r in live if unicodedata.normalize('NFC', txt(r)) != txt(r)]
report('C1', 'Chữ chưa chuẩn hóa NFC', not_nfc)
weird_script = [(r['unit_id'], c) for r in live for c in set(txt(r))
                if unicodedata.name(c, '').split(' ')[0] in ('CYRILLIC', 'GREEK') or c == '�'
                or (unicodedata.category(c) == 'Cc' and c != '\n')]
report('C2', 'Ký tự Kirin/Hy Lạp/ký tự điều khiển/�', weird_script, 6)
# chuỗi đặc trưng của UTF-8 bị đọc sai ("Ã©", "á»…"); chữ hoa hợp lệ như "NGÃ" không tính
moji = [(r['unit_id'], m.group()) for r in live for m in
        [re.search(r'Ã[ -¿]|Æ°|á»[-¿]|Ä‘|â€', txt(r))] if m]
report('C3', 'Lỗi mã hóa kiểu "Ã©", "á»"', moji)
ok_chars = set('abcdefghijklmnopqrstuvwxyzđáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ'
               '0123456789 \n.,;:!?()[]{}"\'“”‘’-–—/%+*=<>&_@#°§…|×≥≤±·•~^')
odd = collections.Counter(c for r in content_live for c in txt(r).lower() if c not in ok_chars)
print('\n[C4] Ký tự ngoài tập thường gặp (nội dung luật đang hiệu lực, không tính mẫu biểu):',
      [(c, hex(ord(c)), n) for c, n in odd.most_common(20)])
results.append(('C4', 'Ký tự lạ (lượt)', sum(odd.values())))

# ---------- Rác còn sót ----------
ART = {
    'header Công báo': r'CÔNG BÁO\s*/\s*Số|Công báo số \d+\s*\+',
    'chuyển trang Công báo': r'\((?:Xem tiếp|Tiếp theo) Công báo',
    'dấu chữ ký số': r'Ký bởi:|Người ký:|Thời gian ký:|Cơ quan:.*Chính phủ\b.*\d{2}:\d{2}',
    'quảng cáo/watermark trang web': r'thuvienphapluat|luatvietnam|LawNet|Văn bản này được|Tải về|www\.',
    'nơi nhận/chữ ký trong thân': r'Nơi nhận\s*:|\bTM\. (?:CHÍNH PHỦ|QUỐC HỘI)|\bKT\. (?:BỘ TRƯỞNG|THỦ TƯỚNG)',
    'số trang lẻ giữa câu': r'\n\d{1,3}\n',
}
for name, pat in ART.items():
    hits = [(r['unit_id'], re.search(pat, txt(r)).group()) for r in content_live if re.search(pat, txt(r))]
    report('R', name, hits, 4)

hyph = [(r['unit_id'], m.group()) for r in content_live for m in [re.search(r'\b\w+- \w+', r['text'])] if m
        and not re.search(r'\d- |[A-ZĐ]- ', m.group())]
report('R6', 'Từ bị ngắt dòng có gạch nối "xx- yy"', hyph, 6)
spaces = [r['unit_id'] for r in content_live if re.search(r'  |\s[,.;:](?!\.)', r['text'])]
report('R7', 'Khoảng trắng thừa hoặc trước dấu câu', spaces, 4)

# ---------- Sửa đổi ----------
amended = [r for r in vers if r['source_doc_id'] != r['doc_id']]
quotes = [(r['version_id'], r['text'][:80], r['text'][-40:]) for r in amended
          if re.match(r'\s*[“"]', r['text']) or re.search(r'[”"]\s*\.?$', r['text'])]
report('A1', 'Bản sửa đổi còn dấu ngoặc kép trích dẫn ở đầu/cuối', quotes, 4)
instr = [(r['version_id'], r['text'][:120]) for r in amended
         if re.search(r'(?:sửa đổi|bổ sung|thay thế)[^.]{0,40}như sau\s*:', r['text'])]
report('A2', 'Bản sửa đổi còn câu chỉ dẫn "… như sau:"', instr, 4)
bad_dates = [r['version_id'] for r in vers if r['valid_to'] and r['valid_from'] >= r['valid_to']]
report('A3', 'Phiên bản có valid_from ≥ valid_to', bad_dates)

# ---------- Trùng ----------
seen = collections.defaultdict(list)
for r in body_live:
    if len(r['text']) > 120:
        seen[(r['doc_id'], r['text'])].append(r['unit_id'])
dups = [v for v in seen.values() if len(v) > 1]
report('D1', 'Đơn vị cùng văn bản có nội dung giống hệt (dài > 120 ký tự)', dups, 6)

# ---------- Bộ 600 câu ----------
qs = [json.loads(l) for l in open(ROOT / 'data/processed/gplx_600.jsonl', encoding='utf-8')]
report('G1', 'Câu GPLX có lựa chọn rỗng hoặc còn nhãn dính', [q['so_cau'] for q in qs
       if any(not o.strip() or re.search(r'\s[1-4]\.\s', o) for o in q['lua_chon'])])
qdup = collections.Counter(q['cau_hoi'] for q in qs)
report('G2', 'Câu hỏi GPLX trùng nội dung câu hỏi', [(t[:80], n) for t, n in qdup.items() if n > 1], 6)
report('G3', 'Câu GPLX có ký tự lạ/điều khiển', [q['so_cau'] for q in qs
       if any(unicodedata.category(c) == 'Cc' for c in q['cau_hoi'] + ''.join(q['lua_chon']))])
print('\nTÓM TẮT:', [(c, n, k) for c, n, k in results])
