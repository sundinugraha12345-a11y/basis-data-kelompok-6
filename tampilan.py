import streamlit as st
import pandas as pd
import mysql.connector
import datetime

# ==========================================
# 1. FUNGSI KONEKSI DATABASE (CLEVER CLOUD)
# ==========================================
def get_db_connection():
    return mysql.connector.connect(
        host="beyszfa0jr2llg848xpr-mysql.services.clever-cloud.com",
        database="beyszfa0jr2llg848xpr", 
        user="u4mvn9ck4uwhf5kt",               
        password="AOrccIxnxjcSl5v7u3YG", 
        port=3306
    )

def fetch_data_barang():
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                b.id_produk, 
                k.nama_kategori AS kategori, 
                b.nama_produk, 
                b.harga_jual, 
                b.stok_awal 
            FROM barang b
            LEFT JOIN kategori_barang k ON b.id_kategori = k.id_kategori
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id_produk", "kategori", "nama_produk", "harga_jual", "stok_awal"])

def fetch_daftar_kategori():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_kategori, nama_kategori FROM kategori_barang")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception:
        return []

def fetch_data_kategori_tabel():
    try:
        conn = get_db_connection()
        query = "SELECT id_kategori AS `ID Kategori`, nama_kategori AS `Nama Kategori` FROM kategori_barang"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["ID Kategori", "Nama Kategori"])

def fetch_data_supplier():
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                id_supplier AS `ID Supplier`, 
                nama_supplier AS `Nama Supplier`, 
                no_telp AS `No. Telp / WA`, 
                alamat AS `Alamat` 
            FROM supplier
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["ID Supplier", "Nama Supplier", "No. Telp / WA", "Alamat"])


# ==========================================
# 2. KONFIGURASI HALAMAN & STYLING UI/UX
# ==========================================
st.set_page_config(page_title="test ui/ux kelompok 5", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1e1e26; 
    }
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        border: none;
        background-color: transparent;
        color: #ffffff;
        text-align: left;
        padding: 15px 20px;
        font-size: 16px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3d3d4d;
        border-left: 5px solid #ff4b4b;
    }
    h1, h2, h3, p { color: white; }
    </style>
    """, unsafe_allow_html=True)

if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'nama_lengkap' not in st.session_state:
    st.session_state.nama_lengkap = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'page' not in st.session_state:
    st.session_state.page = ""
if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []


# ==========================================
# 3. LOGIC HALAMAN LOGIN
# ==========================================
if not st.session_state.is_logged_in:
    st.write("#")
    st.markdown("<h2 style='text-align: center;'>🔐 Login Sistem Minimarket</h2>", unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        with st.form("form_login"):
            input_username = st.text_input("Username")
            input_password = st.text_input("Password", type="password")
            tombol_login = st.form_submit_button("Masuk")
            
            if tombol_login:
                if input_username == "" or input_password == "":
                    st.error("Username dan Password wajib diisi bro!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor(dictionary=True)
                        query = "SELECT * FROM users WHERE username = %s AND password = %s"
                        cursor.execute(query, (input_username, input_password))
                        user_data = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if user_data:
                            st.session_state.is_logged_in = True
                            st.session_state.username = user_data['username']
                            st.session_state.nama_lengkap = user_data['nama_lengkap']
                            st.session_state.role = user_data['role']
                            st.session_state.page = user_data['role']
                            st.rerun()
                        else:
                            st.error("Username atau Password salah, bro!")
                    except mysql.connector.Error as err:
                        st.error(f"Gagal koneksi sistem login. Error: {err}")


# ==========================================
# 4. SIDEBAR NAVIGASI (HANYA MUNCUL JIKA SUDAH LOGIN)
# ==========================================
if st.session_state.is_logged_in:
    role = st.session_state.role
    nama_user = st.session_state.nama_lengkap

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown(f"<h3 style='color: white; text-align: center;'>{nama_user}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ff4b4b; text-align: center; font-weight: bold;'>Akses: {role}</p>", unsafe_allow_html=True)
        st.write("---")
        
        if role == "Admin Gudang" or role == "Manager/Owner":
            if st.button("📦 Admin Gudang"):
                st.session_state.page = "Admin Gudang"
                st.rerun()
        if role == "Kasir" or role == "Manager/Owner":
            if st.button("🛒 Kasir"):
                st.session_state.page = "Kasir"
                st.rerun()
        if role == "Manager/Owner":
            if st.button("📊 Manager/Owner"):
                st.session_state.page = "Manager/Owner"
                st.rerun()
                
        st.write("---")
        if st.button("🔴 Logout"):
            st.session_state.is_logged_in = False
            st.session_state.clear()
            st.rerun()


    # ==========================================
    # 5. LOGIC HALAMAN UTAMA
    # ==========================================
    page = st.session_state.page

    # --- HALAMAN: ADMIN GUDANG ---
    if page == "Admin Gudang":
        st.title("📦 Manajemen Inventory")
        tab1, tab2, tab3 = st.tabs(["Tambah Produk / Update Stok", "Tambah Kategori Baru", "Data Supplier"])
        
        with tab1:
            st.subheader("Input Produk Baru / Tambah Stok")
            kategori_db = fetch_daftar_kategori()
            opsi_kategori = {f"{row['id_kategori']} - {row['nama_kategori']}": row['id_kategori'] for row in kategori_db}
            
            col1, col2 = st.columns(2)
            id_p = col1.text_input("ID Produk Baru (Dipakai jika barang belum ada)", value="P006")
            
            if opsi_kategori:
                kat_terpilih = col2.selectbox("Kategori", list(opsi_kategori.keys()))
                id_kat_fix = opsi_kategori[kat_terpilih]
            else:
                col2.warning("Kategori belum ada! Silakan tambah kategori di Tab sebelah dulu, bro.")
                id_kat_fix = None
                
            nama_p = col1.text_input("Nama Produk", placeholder="Contoh: Coca Cola")
            harga = col2.number_input("Harga Jual (DECIMAL)", min_value=0, value=0)
            stok = st.number_input("Stok Tambahan / Stok Awal (INT)", min_value=0, value=0)
            
            if st.button("Simpan ke Database", type="primary"):
                nama_p_bersih = nama_p.strip()
                
                if nama_p_bersih == "":
                    st.error("Nama produk wajib diisi!")
                elif id_kat_fix is None:
                    st.error("Pilih kategori yang valid dulu, brok!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor(buffered=True)
                        
                        check_query = "SELECT id_produk, stok_awal FROM barang WHERE LOWER(nama_produk) = LOWER(%s)"
                        cursor.execute(check_query, (nama_p_bersih,))
                        existing_product = cursor.fetchone()
                        
                        while cursor.nextset():
                            pass
                        
                        if existing_product:
                            id_lama, stok_lama = existing_product
                            stok_baru = stok_lama + stok
                            
                            update_query = "UPDATE barang SET stok_awal = %s WHERE id_produk = %s"
                            cursor.execute(update_query, (stok_baru, id_lama))
                            conn.commit()
                            st.success(f"Produk '{nama_p_bersih}' terdeteksi sudah ada. Stok digabungkan ke ID: {id_lama}. Total Stok: {stok_baru}")
                        else:
                            insert_query = """
                                INSERT INTO barang (id_produk, id_kategori, nama_produk, harga_jual, stok_awal, id_supplier) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_query, (id_p, id_kat_fix, nama_p_bersih, harga, stok, None))
                            conn.commit()
                            st.success(f"Produk baru '{nama_p_bersih}' berhasil ditambahkan dengan ID: {id_p}")
                            
                        cursor.close()
                        conn.close()
                        st.rerun()
                    except mysql.connector.Error as err:
                        st.error(f"Gagal memproses data ke database. Error: {err}")

        with tab2:
            st.subheader("➕ Tambah Kategori Produk Baru")
            kat_col1, kat_col2 = st.columns(2)
            df_kat_cek = fetch_data_kategori_tabel()
            next_id_kat = len(df_kat_cek) + 1
            
            id_kategori_input = kat_col1.number_input("ID Kategori (Sesuai Struktur DB)", min_value=1, value=next_id_kat)
            nama_kategori_input = kat_col2.text_input("Nama Kategori Baru", placeholder="Contoh: Alat Tulis, Kosmetik")
            
            if st.button("Simpan Kategori Baru"):
                nama_kat_clean = nama_kategori_input.strip()
                if nama_kat_clean == "":
                    st.error("Nama kategori gak boleh kosong, brok!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        query_kat = "INSERT INTO kategori_barang (id_kategori, nama_kategori) VALUES (%s, %s)"
                        cursor.execute(query_kat, (id_kategori_input, nama_kat_clean))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Kategori baru '{nama_kat_clean}' berhasil disimpan!")
                        st.rerun()
                    except mysql.connector.Error as err:
                        st.error(f"Gagal simpan kategori. Kemungkinan ID '{id_kategori_input}' sudah terpakai. Error: {err}")
            
            st.write("---")
            st.subheader("📋 Kategori Saat Ini")
            if df_kat_cek.empty:
                st.info("Belum ada kategori yang tercatat.")
            else:
                st.dataframe(df_kat_cek, use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("Input Supplier Baru")
            s_col1, s_col2 = st.columns(2)
            id_sup = s_col1.text_input("ID Supplier (PK)", value="SUP003")
            nama_sup = s_col2.text_input("Nama Supplier", placeholder="Contoh: PT Sinar Sosro")
            telp_sup = s_col1.text_input("No Telepon / WhatsApp")
            alamat_sup = s_col2.text_area("Alamat Perusahaan")
            
            if st.button("Simpan Supplier"):
                if nama_sup == "":
                    st.error("Nama Supplier wajib diisi!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        query_sup = "INSERT INTO supplier (id_supplier, nama_supplier, no_telp, alamat) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query_sup, (id_sup, nama_sup, telp_sup, alamat_sup))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Supplier '{nama_sup}' berhasil didaftarkan!")
                        st.rerun()
                    except mysql.connector.Error as err:
                        st.error(f"Gagal simpan supplier. Error: {err}")
            
            st.write("---")
            st.subheader("📋 Daftar Supplier Terdaftar")
            df_supplier = fetch_data_supplier()
            if df_supplier.empty:
                st.info("Belum ada data supplier yang tercatat di database.")
            else:
                st.dataframe(df_supplier, use_container_width=True, hide_index=True)


    # --- HALAMAN: KASIR ---
    elif page == "Kasir":
        st.title("🛒 Menu Transaksi Kasir")
        df_barang = fetch_data_barang()

        if df_barang.empty:
            st.warning("Belum ada data produk di database.")
        else:
            st.subheader("📋 Daftar Stok Produk")
            st.dataframe(df_barang, use_container_width=True, hide_index=True)
            st.write("---")
            
            ruang_kiri, ruang_kanan = st.columns([1.1, 1])
            
            with ruang_kiri:
                st.subheader("🛍️ Pilih & Tambah Barang")
                pilihan_produk = [f"{row['id_produk']} - {row['nama_produk']} (Stok: {row['stok_awal']})" for index, row in df_barang.iterrows()]
                
                produk_terpilih = st.selectbox("Pilih Produk", pilihan_produk)
                jumlah_beli = st.number_input("Jumlah Beli", min_value=1, value=1)
                
                idx = pilihan_produk.index(produk_terpilih) if produk_terpilih in pilihan_produk else 0
                id_p = df_barang.iloc[idx]['id_produk']
                nama_p = df_barang.iloc[idx]['nama_produk']
                harga_p = float(df_barang.iloc[idx]['harga_jual'])
                stok_p = int(df_barang.iloc[idx]['stok_awal'])
                
                if st.button("➕ Tambah ke Keranjang"):
                    if stok_p <= 0:
                        st.error(f"Stok '{nama_p}' habis!")
                    elif jumlah_beli > stok_p:
                        st.error(f"Stok tidak cukup! Sisa: {stok_p} pcs.")
                    else:
                        sudah_ada = False
                        for item in st.session_state.keranjang:
                            if item['id_produk'] == id_p:
                                if item['jumlah'] + jumlah_beli > stok_p:
                                    st.error("Total di keranjang melebihi stok gudang!")
                                    sudah_ada = True
                                    break
                                item['jumlah'] += jumlah_beli
                                item['subtotal'] = item['jumlah'] * item['harga']
                                sudah_ada = True
                                break
                        
                        if not sudah_ada:
                            st.session_state.keranjang.append({
                                'id_produk': id_p, 'nama_produk': nama_p, 'harga': harga_p, 'jumlah': jumlah_beli, 'subtotal': harga_p * jumlah_beli
                            })
                        st.toast(f"{nama_p} ditambah!", icon="🛒")
                        st.rerun()

                if st.button("🗑️ Kosongkan Keranjang"):
                    st.session_state.keranjang = []
                    st.rerun()

            with ruang_kanan:
                st.subheader("📝 Keranjang Kasir")
                if not st.session_state.keranjang:
                    st.info("Keranjang kosong.")
                else:
                    df_keranjang = pd.DataFrame(st.session_state.keranjang)
                    st.dataframe(df_keranjang[['nama_produk', 'harga', 'jumlah', 'subtotal']], use_container_width=True, hide_index=True)
                    
                    total_semua = df_keranjang['subtotal'].sum()
                    st.markdown(f"## Total Tagihan: <span style='color: #ff4b4b;'>Rp {total_semua:,.0f}</span>", unsafe_allow_html=True)
                    
                    if st.button("🚀 PROSES TRANSAKSI", type="primary"):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            waktu_sekarang = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            for item in st.session_state.keranjang:
                                cursor.execute(
                                    "INSERT INTO transaksi (id_produk, jumlah, total_bayar, tanggal_transaksi) VALUES (%s, %s, %s, %s)", 
                                    (item['id_produk'], item['jumlah'], item['subtotal'], waktu_sekarang)
                                )
                                cursor.execute("UPDATE barang SET stok_awal = stok_awal - %s WHERE id_produk = %s", (item['jumlah'], item['id_produk']))
                            
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            st.balloons()
                            st.session_state.keranjang = []
                            st.rerun()
                        except mysql.connector.Error as err:
                            st.error(f"Transaksi Gagal: {err}")


    # --- HALAMAN: MANAGER / OWNER ---
    elif page == "Manager/Owner":
        st.title("📊 Laporan Penjualan")
        
        # =========================================================================
        # FITUR AUTO-REFRESH LIVE CLOCK (MENGGUNAKAN ST.FRAGMENT)
        # =========================================================================
        @st.fragment(run_every=1.0)
        def live_clock():
            waktu_utc = datetime.datetime.utcnow()
            waktu_wib = waktu_utc + datetime.timedelta(hours=7)
            
            jam_sekarang = waktu_wib.strftime("%H:%M:%S")
            tanggal_sekarang = waktu_wib.strftime("%d %B %Y")
            
            st.markdown(f"""
                <div style='background-color: #1e1e26; padding: 12px 20px; border-radius: 6px; margin-bottom: 25px; border-left: 5px solid #ff4b4b; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>
                    <span style='color: #888899; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;'>⏰ Real-Time Tracker (WIB):</span>
                    <span style='color: #ff4b4b; font-size: 18px; font-weight: bold; margin-left: 10px;'>{jam_sekarang}</span>
                    <span style='color: #ffffff; font-size: 14px; margin-left: 15px;'>| {tanggal_sekarang}</span>
                </div>
            """, unsafe_allow_html=True)

        live_clock()
        # =========================================================================

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(total_bayar) FROM transaksi")
            total_income_raw = cursor.fetchone()[0]
            total_income = float(total_income_raw) if total_income_raw is not None else 0.0
            
            cursor.execute("SELECT SUM(jumlah) FROM transaksi")
            total_terjual_raw = cursor.fetchone()[0]
            total_terjual = int(total_terjual_raw) if total_terjual_raw is not None else 0
            
            cursor.execute("SELECT COUNT(*) FROM barang WHERE stok_awal < 5")
            stok_kritis = cursor.fetchone()[0]
            
            query_laporan = """
                SELECT 
                    t.id_transaksi AS `ID Transaksi`, 
                    b.nama_produk AS `Nama Produk`, 
                    t.jumlah AS `Jumlah Terjual (Pcs)`, 
                    t.total_bayar AS `Total Bayar (Rp)`, 
                    t.tanggal_transaksi AS `Tanggal Transaksi` 
                FROM transaksi t 
                JOIN barang b ON t.id_produk = b.id_produk 
                ORDER BY t.id_transaksi DESC
            """
            df_laporan = pd.read_sql(query_laporan, conn)
            
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Gagal memuat laporan: {e}")
            total_income, total_terjual, stok_kritis = 0.0, 0, 0
            df_laporan = pd.DataFrame()

        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Omset", f"Rp {total_income:,.0f}")
        m2.metric("📦 Total Produk Terjual", f"{total_terjual} Pcs")
        m3.metric("⚠️ Stok Kritis (< 5 pcs)", f"{stok_kritis} Item")
        
        st.write("---")
        st.subheader("📋 Detail Riwayat Transaksi")
        
        if df_laporan.empty:
            st.info("Belum ada riwayat transaksi yang tercatat.")
        else:
            st.dataframe(df_laporan, use_container_width=True, hide_index=True)