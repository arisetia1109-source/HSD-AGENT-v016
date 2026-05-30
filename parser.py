import re, pdfplumber

def clean(s): return ' '.join(str(s).split()) if s else ''

SKU_FIX = {
    'BG-220GR-1-BOTOL-BG': 'BG-220GR-1-BOTOL-BG-SKU',
    'BG-220GR-1-BOTOL-BH': 'BG-220GR-1-BOTOL-BH-SKU',
    'BG-100GR-1-BOTOL-BG': 'BG-100GR-1-BOTOL-BG-SKU',
    'BG-100GR-1-BOTOL-BH': 'BG-100GR-1-BOTOL-BH-SKU',
    'BG-DRINK-PROMO-1-BTL': 'BG-DRINK-PROMO-1-BTL-ORI',
    'BG-DRINK-PROMO-2-BTL': 'BG-DRINK-PROMO-2-BTL-ORI',
}
def normalize_product(sku, nama_produk):
    """Normalisasi nama produk berdasarkan pola SKU"""
    s = sku.upper()
    if any(x in s for x in ['100GR','100 GR']): return 'Black Garlic 100gr'
    if any(x in s for x in ['220GR','220 GR']): return 'Black Garlic 220gr'
    if any(x in s for x in ['500GR','500 GR']): return 'Black Garlic 500gr'
    if 'DRINK' in s and any(x in s for x in ['PEACH','PCH']): return 'Drink BG Peach'
    if 'DRINK' in s: return 'Drink BG Original'
    if any(x in s for x in ['FLORA','MF-','MULTIFLORA']): return 'Madu Multi Flora 260gr'
    if any(x in s for x in ['KURMA','MK-','BUNGA']): return 'Madu Bunga Kurma 260gr'
    n = nama_produk.upper() if nama_produk else ''
    if 'PEACH' in n and 'DRINK' in n: return 'Drink BG Peach'
    if 'DRINK' in n: return 'Drink BG Original'
    if '100' in n and ('GR' in n or 'GRAM' in n): return 'Black Garlic 100gr'
    if '220' in n and ('GR' in n or 'GRAM' in n): return 'Black Garlic 220gr'
    if '500' in n and ('GR' in n or 'GRAM' in n): return 'Black Garlic 500gr'
    if any(x in n for x in ['FLORA','MULTI FLORA']): return 'Madu Multi Flora 260gr'
    if any(x in n for x in ['KURMA','BUNGA KURMA']): return 'Madu Bunga Kurma 260gr'
    return nama_produk or sku

SKU_FIX = {
    'BG-220GR-1-BOTOL-BG': 'BG-220GR-1-BOTOL-BG-SKU',
    'BG-220GR-1-BOTOL-BH': 'BG-220GR-1-BOTOL-BH-SKU',
    'BG-100GR-1-BOTOL-BG': 'BG-100GR-1-BOTOL-BG-SKU',
    'BG-100GR-1-BOTOL-BH': 'BG-100GR-1-BOTOL-BH-SKU',
    'BG-DRINK-PROMO-1-BTL': 'BG-DRINK-PROMO-1-BTL-ORI',
    'BG-DRINK-PROMO-2-BTL': 'BG-DRINK-PROMO-2-BTL-ORI',
}
def fix_sku(s):
    s=s.strip('-').strip()
    for k,v in SKU_FIX.items():
        if s.startswith(k): return v
    return s
    s=s.strip('-').strip()
    for k,v in SKU_FIX.items():
        if s.startswith(k): return v
    return s

def detect(text):
    t=text.upper()
    if re.search(r'SPXID\d+',text): return 'Shopee','Shopee Express','ECO'
    if 'JET.CO.ID' in t or re.search(r'\bJX\d{10}\b',text):
        pl='TikTok Shop' if 'TIKTOK' in t else 'Tokopedia/TikTok'
        sv='EZ'
        for s in ['EZ','NDD','ECO','REG']:
            if re.search(r'\b'+s+r'\b',text[:300].upper()): sv=s; break
        return pl,'J&T Express',sv
    if re.search(r'\bGTL\d{8,12}\b',text):
        pl='TikTok Shop' if 'TIKTOK' in t else 'Tokopedia/TikTok'
        return pl,'GTL','REG'
    if re.search(r'No\.\s*Resi:\s*0046\d+|No\.\s*Resi:\s*00296',text) or re.search(r'\b0046\d{8,10}\b',text):
        pl='TikTok Shop' if 'TIKTOK' in t else 'Tokopedia/TikTok'
        return pl,'SiCepat','REG'
    if re.search(r'No\.\s*Resi:\s*CM\d+',text) or re.search(r'\bBDO\d+\b',text):
        return 'Shopee','Wahana','Reguler'
    if re.search(r'\bAAJ\w+\b',text) or 'ANTERAJA' in t: return 'Shopee','Anteraja','REG'
    if re.search(r'\bLEX\w+\b',text) or 'LAZADA' in t: return 'Lazada','LEX','REG'
    return 'Unknown','Unknown','-'

def get_resi(text):
    for p in [r'\b(JX\d{10})\b',r'\b(GTL\d{8,12})\b',
              r'No\.\s*Resi:\s*(0046\d+)',r'No\.\s*Resi:\s*(00296\d+)',
              r'\b(SPXID\d{10,15})\b',r'No\.\s*Resi:\s*(CM\d+)',
              r'\b(AAJ\w{8,})\b',r'\b(LEX\w{8,})\b']:
        m=re.search(p,text)
        if m: return m.group(1)
    return ''

def get_pesanan(text):
    for p in [r'No\.?\s*Pesanan[:\s]+([\w]+)',r'Order\s*I[Dd][:\s]+([\d]+)',
              r'Pesan:\s*\(([\w]+)\)']:
        m=re.search(p,text)
        if m: return m.group(1)
    return ''

def get_penerima(text):
    m=re.search(r'Penerima\s*:\s*([^\n(]+)',text)
    if m:
        n=clean(m.group(1).split('(')[0])
        if 1<len(n)<60: return n
    m2=re.search(r'Receiver\s+([^\n(]+)',text)
    if m2:
        n=clean(m2.group(1).split('(')[0])
        if 1<len(n)<60: return n
    return ''

def get_alamat_tiktok(text):
    lines=text.split('\n'); capture=False; addr=[]
    for line in lines:
        l=clean(line)
        # Support: "Penerima :" (TikTok/Shopee) DAN "Receiver" (GTL)
        if re.search(r'Penerima\s*:|Receiver\s+',line): capture=True; continue
        if capture:
            if re.search(r'Weight\s*:|Ship\s*:|Order\s*Id|Estimated|Shipping Date|Sender\s|TT Order|In transit',line,re.I): break
            if l and not re.search(r'^\(?\+?62|^Pengirim|^Sender|DKI JAKARTA',l) and len(l)>4:
                addr.append(l)
            if len(addr)>=5: break
    return ' '.join(addr)

def get_alamat_shopee(text):
    lines=text.split('\n')
    # Cara 1: cari baris KAB/KOTA
    for i,line in enumerate(lines):
        l=clean(line)
        if re.search(r'KAB\.|KOTA JAKARTA|JAWA|SUMATERA|KALIMANTAN|SULAWESI|BALI|BANTEN|NTB|RIAU|PAPUA|ACEH|KOTA\s+\w+',l.upper()):
            addr=[]
            for j in range(max(0,i-3),min(i+3,len(lines))):
                lj=clean(lines[j])
                if lj and len(lj)>4 and not re.search(r'Penerima|Pengirim|HSD|6281|COD|Berat|Batas|No\.|Reguler|CASHLESS|SPXID|BDO|Resi:|SKU|Variasi',lj,re.I):
                    addr.append(lj)
            if addr: return ' '.join(addr[:4])
    # Cara 2: ambil teks setelah penerima sampai sebelum tabel produk
    m=re.search(r'Penerima\s*:\s*[^\n]+\n(.*?)(?:Berat:|No\.Pesanan:|#\s+Nama)',text,re.DOTALL)
    if m:
        raw=m.group(1)
        lns=[clean(l) for l in raw.split('\n') if len(clean(l))>5]
        lns=[l for l in lns if not re.search(r'^\d{10,}|^Pengirim|^HSD|CASHLESS|COD|Resi:|SKU',l,re.I)]
        if lns: return ' '.join(lns[:3])
    return ''

def parse_tiktok_products(text):
    """TikTok/J&T/GTL: Product Name | SKU | Seller SKU | Qty"""
    items=[]
    m=re.search(r'Product Name\s+SKU\s+Seller SKU\s+Qty\s*\n([\s\S]+?)(?:Qty Total:|Order ID:|$)',text)
    if not m: return items
    raw=[l.strip() for l in m.group(1).split('\n') if l.strip()]
    main_re=re.compile(r'^(.*?)\s+(Default|220\s*GR|\b1\b|[A-Z0-9]{2,10})\s+([A-Z][A-Z0-9]*-[A-Z0-9\-]+)\s+(\d{1,2})\s*$')
    sku_suf=re.compile(r'([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)\s*$')
    i=0
    while i<len(raw):
        mm=main_re.match(raw[i])
        if mm:
            prod_part=mm.group(1).strip()
            sys_sku=mm.group(2).strip()
            seller_sku=mm.group(3).strip()
            qty=int(mm.group(4))
            j=i+1
            while j<len(raw):
                if main_re.match(raw[j]): break
                sf=sku_suf.search(raw[j])
                if sf: seller_sku+=sf.group(1); j+=1; continue
                j+=1; break
            seller_sku=re.sub(r'\s+','',seller_sku)
            seller_sku=fix_sku(seller_sku)
            nama=re.sub(r'^\d+\s*','',prod_part).strip()
            nama=re.sub(r'\b(Default|220\s*GR)\s*$','',nama).strip().rstrip(',')
            variasi='' if sys_sku.upper()=='DEFAULT' else sys_sku
            # Fallback variasi dari field "Barang : 220 GR" di J&T
            if not variasi:
                bm=re.search(r'Barang\s*:\s*([^\n,]+)',text)
                if bm: variasi=bm.group(1).strip()
            items.append({'nama_produk':nama,'sku':seller_sku,'variasi':variasi,'qty':qty})
            i=j
        else: i+=1
    return items

def parse_shopee_products(text):
    """Shopee/Wahana/SiCepat: # | Nama Produk | SKU | Variasi | Qty"""
    items=[]
    m=re.search(r'#\s+Nama Produk\s+SKU\s+Variasi\s+Qty([\s\S]+?)(?:Pesan:|$)',text)
    if not m: return items
    lines=[l.strip() for l in m.group(1).split('\n') if l.strip()]
    main_re=re.compile(r'^(\d+)\s+.+?(BG-[A-Z0-9\-]+)\s+(220 GR|ORIGINAL \d+\s*BOTOL|DEFAULT|[\w\s]{2,25}?)\s+(\d{1,2})\s*$')
    i=0
    while i<len(lines):
        mm=main_re.match(lines[i])
        if mm:
            sku_p=mm.group(2).rstrip('-')
            variasi=mm.group(3).strip()
            qty=int(mm.group(4))
            # Nama produk: teks antara nomor dan BG-
            rest=lines[i]
            nm=re.match(r'^\d+\s+',rest)
            if nm:
                after=rest[nm.end():]
                bg=after.find(sku_p[:6])
                nama=after[:bg].strip().rstrip(',') if bg>0 else ''
            else: nama=''
            # Scan lanjutan untuk complete SKU
            j=i+1; last_cap=''
            while j<len(lines) and not main_re.match(lines[j]):
                ce=re.search(r'\b([A-Z][A-Z0-9]*)\s*$',lines[j])
                if ce: last_cap=ce.group(1)
                if not nama:
                    rn=re.sub(r'[A-Z0-9\-]+\s*$','',lines[j]).strip()
                    if rn and len(rn)>3: nama=rn.rstrip(',')
                j+=1
            if last_cap and last_cap not in sku_p and last_cap not in ('GR','BOTOL','SKU'):
                full_sku=sku_p+('-' if not sku_p.endswith('-') else '')+last_cap
            elif last_cap=='SKU':
                full_sku=sku_p+'-SKU'
            else:
                full_sku=sku_p
            full_sku=fix_sku(full_sku)
            variasi_c='' if variasi.upper()=='DEFAULT' else variasi
            items.append({'nama_produk':nama,'sku':full_sku,'variasi':variasi_c,'qty':qty})
            i=j
        else: i+=1
    return items

def parse_page(text):
    platform,courier,layanan=detect(text)
    resi=get_resi(text)
    if not resi: return []
    penerima=get_penerima(text)
    pesanan=get_pesanan(text)

    # SiCepat bisa pakai format Shopee (# Nama Produk) ATAU TikTok (Product Name)
    has_shopee_table='# Nama Produk' in text and 'Variasi' in text
    has_tiktok_table='Product Name' in text and 'Seller SKU' in text

    if has_shopee_table:
        alamat=get_alamat_shopee(text)
        products=parse_shopee_products(text)
    elif has_tiktok_table:
        alamat=get_alamat_tiktok(text)
        products=parse_tiktok_products(text)
    else:
        alamat=get_alamat_shopee(text) if courier in ['Wahana','Shopee Express'] else get_alamat_tiktok(text)
        products=[]

    if not products:
        products=[{'nama_produk':'(cek manual)','sku':'(cek manual)','variasi':'','qty':1}]

    return [{'platform':platform,'courier':courier,'layanan':layanan,
             'no_resi':resi,
             'nama_produk': normalize_product(p['sku'], p['nama_produk']),
             'nama_produk_asli': p['nama_produk'],
             'sku':p['sku'],'variasi':p['variasi'],
             'qty':p['qty'],'no_pesanan':pesanan,
             'nama_penerima':penerima,'alamat':alamat} for p in products]

def process_pdf(pdf_path, progress_callback=None):
    all_rows,errors,seen=[],[],{}
    with pdfplumber.open(pdf_path) as pdf:
        total=len(pdf.pages)
        for i,page in enumerate(pdf.pages):
            try:
                text=page.extract_text() or ''
                for r in parse_page(text):
                    k=r['no_resi']+'_'+(r['sku'] or str(r['qty']))
                    if k not in seen: seen[k]=True; all_rows.append(r)
            except Exception as e: errors.append(f"Hal {i+1}: {e}")
            if progress_callback: progress_callback(i+1,total)
    return all_rows,errors
