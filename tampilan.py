import streamlit as st
import pandas as pd
import mysql.connector

# ==========================================
# 1. FUNGSI KONEKSI DATABASE (CLEVER CLOUD ONLINE)
# ==========================================
def get_db_connection():
    return mysql.connector.connect(
        host="beyszfa0jr2llg848xpr-mysql.services.clever-cloud.com",
        database="beyszfa0jr2llg848xpr",
        user="u4mvn9ck4uwhf5kt",              
        password="AOrccIxnxjcSl5v7u3YG", 
        port=3306
    )

# --- TRIK CACHING: Biar aplikasi gak lelet bolak-balik nembak cloud ---
@st.cache_data(ttl=5)  
def fetch_data_barang():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT id_produk, nama_produk, harga_jual, stok_awal FROM barang", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id_produk", "nama_produk", "harga_jual", "stok_awal"])


# ==========================================
# 2. KONFIGURASI HALAMAN & STYLING UI/UX
# ==========================================
st.set_page_config(page_title="test ui/ux kelompok 5", layout="wide")

st.markdown("""
    <style>
    /* Styling Sidebar */
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

# Session State Awal untuk Login dan Navigasi Halaman
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

# --- Session State untuk menampung data Keranjang Belanja ---
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
                            
                            if user_data['role'] == "Admin Gudang":
                                st.session_state.page = "Admin Gudang"
                            elif user_data['role'] == "Kasir":
                                st.session_state.page = "Kasir"
                            elif user_data['role'] == "Manager/Owner":
                                st.session_state.page = "Manager/Owner"
                                
                            st.cache_data.clear() # Cache dibersihkan dengan bener tanpa typo
                            st.rerun()
                        else:
                            st.error("Username atau Password salah, bro!")
                            
                    except mysql.connector.Error as err:
                        st.error(f"Gagal koneksi sistem login. Error: {err}")


# ==========================================
# 4. SIDEBAR NAVIGASI (Hanya Muncul Jika Sudah Login)
# ==========================================
if st.session_state.is_logged_in:
    role = st.session_state.role
    nama_user = st.session_state.nama_lengkap

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        
        st.markdown(f"<h3 style='color: white; text-align: center;'>{nama_user}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ff4b4b; text-align: center; font-weight: bold;'>Akses: {role}</p>", unsafe_allow_html=True)
        st.write("---")
        
        st.markdown("<p style='color: #888; font-size: 12px; padding-left: 20px;'>MENU NAVIGASI</p>", unsafe_allow_html=True)
        
        if role == "Admin Gudang":
            if st.button("📦 Admin Gudang"):
                st.session_state.page = "Admin Gudang"
                st.rerun()
                
        elif role == "Kasir":
            if st.button("🛒 Kasir"):
                st.session_state.page = "Kasir"
                st.rerun()
                
        elif role == "Manager/Owner":
            if st.button("📦 Admin Gudang"):
                st.session_state.page = "Admin Gudang"
                st.rerun()
            if st.button("🛒 Kasir"):
                st.session_state.page = "Kasir"
                st.rerun()
            if st.button("📊 Manager/Owner"):
                st.session_state.page = "Manager/Owner"
                st.rerun()
                
        st.write("---")
        if st.button("🔴 Logout"):
            st.session_state.is_logged_in = False
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()
            
        st.write("---")
        st.caption("kelompok 5")


    # ==========================================
    # 5. LOGIC HALAMAN UTAMA
    # ==========================================
    page = st.session_state.page

    # --- HALAMAN: ADMIN GUDANG ---
    if page == "Admin Gudang":
        st.title("📦 Manajemen Inventory")
        tab1, tab2 = st.tabs(["Tambah Produk", "Data Supplier"])
        
        with tab1:
            st.subheader("Input Produk Baru")
            col1, col2 = st.columns(2)
            id_p = col1.text_input("ID Produk (PK)", value="P001") 
            kat = col2.selectbox("Kategori", ["K001 - Minuman", "K002 - Makanan", "K003 - ATK"]) 
            nama_p = col1.text_input("Nama Produk", placeholder="Contoh: Coca Cola") 
            harga = col2.number_input("Harga Jual (DECIMAL)", min_value=0) 
            stok = st.number_input("Stok Awal (INT)", min_value=0) 
            
            if st.button("Simpan ke Database"):
                if nama_p == "":
                    st.error("Waduh bro, Nama Produk gak boleh kosong!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        query = "INSERT INTO barang (id_produk, kategori, nama_produk, harga_jual, stok_awal) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(query, (id_p, kat, nama_p, harga, stok))
                        conn.commit()  
                        cursor.close()
                        conn.close()
                        st.cache_data.clear() 
                        st.success(f"Mantap! Data produk '{nama_p}' berhasil disimpan!")
                    except mysql.connector.Error as err:
                        st.error(f"Gagal simpan database. Error: {err}")

        with tab2:
            st.subheader("Input Supplier Baru")
            s_col1, s_col2 = st.columns(2)
            id_sup = s_col1.text_input("ID Supplier (PK)", value="SUP001")
            nama_sup = s_col2.text_input("Nama Supplier", placeholder="Contoh: PT Sinar Sosro")
            telp_sup = s_col1.text_input("No Telepon / WhatsApp", placeholder="Contoh: 08123456xxx")
            alamat_sup = s_col2.text_area("Alamat Perusahaan", placeholder="Contoh: Jl. Sudirman No. 45")
            
            if st.button("Simpan Supplier"):
                if nama_sup == "":
                    st.error("Nama Supplier wajib diisi, bro!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        query_sup = "INSERT INTO supplier (id_supplier, nama_supplier, no_telp, alamat) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query_sup, (id_sup, nama_sup, telp_sup, alamat_sup))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Gokil! Supplier '{nama_sup}' berhasil didaftarkan!")
                    except mysql.connector.Error as err:
                        st.error(f"Gagal simpan supplier. Error: {err}")
            
            st.write("---")
            st.subheader("📋 Daftar Supplier Terdaftar")
            try:
                conn = get_db_connection()
                df_supplier = pd.read_sql("SELECT * FROM supplier", conn)
                conn.close()
                if df_supplier.empty:
                    st.info("Belum ada data supplier di database.")
                else:
                    st.dataframe(df_supplier, use_container_width=True)
            except Exception as e:
                st.error(f"Gagal memuat data supplier: {e}")


    # --- HALAMAN: KASIR (VERSI MULTI-ITEM / KERANJANG CEPAT) ---
    elif page == "Kasir":
        st.title("🛒 Menu Transaksi Kasir")
        
        df_barang = fetch_data_barang()

        if df_barang.empty:
            st.warning("Belum ada data produk di database. Silakan isi dulu di menu Admin Gudang!")
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
                
                st.write("#")
                if st.button("➕ Tambah ke Keranjang"):
                    if jumlah_beli > stok_p:
                        st.error(f"Stok tidak cukup! Sisa stok '{nama_p}' cuma {stok_p}")
                    else:
                        sudah_ada = False
                        for item in st.session_state.keranjang:
                            if item['id_produk'] == id_p:
                                if item['jumlah'] + jumlah_beli > stok_p:
                                    st.error(f"Total jumlah di keranjang melebihi stok yang ada!")
                                    sudah_ada = True
                                    break
                                item['jumlah'] += jumlah_beli
                                item['subtotal'] = item['jumlah'] * item['harga']
                                sudah_ada = True
                                break
                        
                        if not sudah_ada:
                            st.session_state.keranjang.append({
                                'id_produk': id_p,
                                'nama_produk': nama_p,
                                'harga': harga_p,
                                'jumlah': jumlah_beli,
                                'subtotal': harga_p * jumlah_beli
                            })
                        st.toast(f"{nama_p} berhasil ditambah!", icon="🛒")
                        st.rerun()

                if st.button("🗑️ Kosongkan Keranjang", type="secondary"):
                    st.session_state.keranjang = []
                    st.rerun()

            with ruang_kanan:
                st.subheader("📝 Keranjang Kasir Saat Ini")
                
                if not st.session_state.keranjang:
                    st.info("Keranjang kosong. Silakan tambah barang di kiri.")
                    total_semua = 0
                else:
                    df_keranjang = pd.DataFrame(st.session_state.keranjang)
                    
                    st.dataframe(df_keranjang[['nama_produk', 'harga', 'jumlah', 'subtotal']], 
                                 use_container_width=True, hide_index=True)
                    
                    total_semua = df_keranjang['subtotal'].sum()
                    st.markdown(f"## Total Tagihan: <span style='color: #ff4b4b;'>Rp {total_semua:,.0f}</span>", unsafe_allow_html=True)
                    st.write("---")
                    
                    if st.button("🚀 PROSES TRANSAKSI & CETAK STRUK", type="primary"):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            for item in st.session_state.keranjang:
                                cursor.execute(
                                    "INSERT INTO transaksi (id_produk, jumlah, total_bayar) VALUES (%s, %s, %s)",
                                    (item['id_produk'], item['jumlah'], item['subtotal'])
                                )
                                cursor.execute(
                                    "UPDATE barang SET stok_awal = stok_awal - %s WHERE id_produk = %s",
                                    (item['jumlah'], item['id_produk'])
                                )
                            
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            st.balloons()
                            st.success("🔥 Transaksi Berhasil Disimpan ke Server Online!")
                            
                            struk_teks = "====================================\n"
                            struk_teks += "          STRUK MINIMARKET\n"
                            struk_teks += "       KELOMPOK 5 - MULTI ITEM\n"
                            struk_teks += "====================================\n"
                            for item in st.session_state.keranjang:
                                struk_teks += f"{item['nama_produk']} x{item['jumlah']}\n"
                                struk_teks += f"  @{item['harga']:,.0f} -> Rp {item['subtotal']:,.0f}\n"
                            struk_teks += "------------------------------------\n"
                            struk_teks += f"TOTAL BELANJA : Rp {total_semua:,.0f}\n"
                            struk_teks += "====================================\n"
                            struk_teks += "    TERIMA KASIH ATAS KUNJUNGANNYA\n"
                            struk_teks += "====================================\n"
                            
                            st.text(struk_teks)
                            
                            st.session_state.keranjang = []
                            st.cache_data.clear()
                            
                        except mysql.connector.Error as err:
                            st.error(f"Gagal memproses seluruh transaksi. Error: {err}")


    # --- HALAMAN: MANAGER / OWNER ---
    elif page == "Manager/Owner":
        st.title("📊 Laporan Penjualan & Dashboard Keuangan")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(total_bayar) FROM transaksi")
            total_income_raw = cursor.fetchone()[0]
            total_income = float(total_income_raw) if total_income_raw is not None else 0.0
            
            keuntungan_bersih = total_income * 0.20
            
            cursor.execute("SELECT COUNT(*) FROM barang WHERE stok_awal < 5")
            stok_kritis = cursor.fetchone()[0]
            cursor.close()
            
            query_laporan = """
                SELECT t.id_transaksi, b.nama_produk, t.jumlah, t.total_bayar, t.tanggal_transaksi 
                FROM transaksi t
                JOIN barang b ON t.id_produk = b.id_produk
                ORDER BY t.id_transaksi DESC
            """
            df_laporan = pd.read_sql(query_laporan, conn)
            conn.close()
        except Exception as e:
            total_income = 0.0
            keuntungan_bersih = 0.0
            stok_kritis = 0
            df_laporan = pd.DataFrame(columns=["id_transaksi", "nama_produk", "jumlah", "total_bayar", "tanggal_transaksi"])

        # Layout Dashboard Keuangan
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Omset (Kotor)", f"Rp {total_income:,.0f}") 
        m2.metric("📈 Estimasi Profit (Bersih 20%)", f"Rp {keuntungan_bersih:,.0f}", delta="Untung")
        m3.metric("⚠️ Stok Menipis (< 5 pcs)", f"{stok_kritis} Item", delta="- Kritis", delta_color="inverse") 
        
        st.write("---")
        st.subheader("📋 Catatan Riwayat Transaksi Real-Time")
        if df_laporan.empty:
            st.info("Belum ada riwayat transaksi yang tercatat.")
        else:
            st.dataframe(df_laporan, use_container_width=True, hide_index=True)